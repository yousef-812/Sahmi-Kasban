from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_calendar import EGXTradingCalendar
from app.market_data.types import CandleSeries, MarketDataProvider
from app.models import MarketReport, MarketReportItem

logger = logging.getLogger(__name__)

MAX_RANGE_DAYS = 45
TRACK_INTERVAL_MINUTES = 10
SOURCE_INTERVAL = "5m"
_FETCH_CONCURRENCY = 5
_EXIT_MODE_TARGET_TWO = "target_2"
_EXIT_MODE_HIGHEST = "highest"


class LabsBacktestError(RuntimeError):
    """Base error for the daily-report intraday backtest."""


class LabsBacktestRangeError(LabsBacktestError):
    """Raised when the requested date range is unsupported."""


@dataclass(frozen=True, slots=True)
class TrackedPoint:
    timestamp: datetime
    price: Decimal
    high: Decimal
    low: Decimal


@dataclass(frozen=True, slots=True)
class SessionTrade:
    report_id: UUID
    target_session_date: date
    rank: int
    ticker: str
    score: float
    price_at_analysis: Decimal | None
    targets: tuple[Decimal, ...]
    stop_loss: Decimal | None
    session_open: Decimal | None
    exit_price: Decimal | None
    exit_reason: str
    hit: bool
    minutes_to_exit: int | None
    return_pct: float | None
    tracked: tuple[TrackedPoint, ...]


@dataclass(frozen=True, slots=True)
class LabsDailyBacktestResult:
    params: dict[str, Any]
    summary: dict[str, Any]
    sessions: tuple[SessionTrade, ...]


def _decimal(value: object) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not result.is_finite() or result <= 0:
        return None
    return result


def _round(value: Decimal | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _fetch_period(start_date: date, end_date: date) -> str:
    span = (end_date - start_date).days
    if span <= 7:
        return "5d"
    if span <= 35:
        return "1mo"
    return "3mo"


def _parse_timestamp(raw: object) -> datetime | None:
    if isinstance(raw, datetime):
        parsed = raw
    elif isinstance(raw, str):
        normalized = raw.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _prediction_levels(
    payload: dict[str, Any],
) -> tuple[tuple[Decimal, ...], Decimal | None, Decimal | None]:
    analysis = payload.get("analysis")
    if not isinstance(analysis, dict):
        analysis = {}
    targets: list[Decimal] = []
    stop_loss: Decimal | None = None
    raw_targets = analysis.get("targets")
    if isinstance(raw_targets, list):
        for item in raw_targets:
            level = _decimal(item)
            if level is not None:
                targets.append(level)
        stop_loss = _decimal(analysis.get("stop_loss"))
    trade_plan = analysis.get("trade_plan")
    if isinstance(trade_plan, dict):
        for key in ("target_1", "target_2"):
            level = _decimal(trade_plan.get(key))
            if level is not None:
                targets.append(level)
        stop_loss = _decimal(trade_plan.get("stop_loss"))
    price_at_analysis = _decimal(payload.get("price_at_analysis"))
    if price_at_analysis is None and isinstance(trade_plan, dict):
        price_at_analysis = _decimal(trade_plan.get("entry"))
    return tuple(targets), stop_loss, price_at_analysis


def _session_bars(
    series: CandleSeries,
    *,
    target_session_date: date,
    calendar: EGXTradingCalendar,
) -> list[dict[str, object]]:
    filtered: list[tuple[datetime, dict[str, object]]] = []
    for raw in series.candles:
        timestamp = _parse_timestamp(raw.get("timestamp"))
        if timestamp is None:
            continue
        if timestamp.astimezone(calendar.timezone).date() == target_session_date:
            filtered.append((timestamp, raw))
    filtered.sort(key=lambda item: item[0])

    bars: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for timestamp, raw in filtered:
        open_price = _decimal(raw.get("open"))
        high = _decimal(raw.get("high"))
        low = _decimal(raw.get("low"))
        close = _decimal(raw.get("close"))
        if None in {open_price, high, low, close}:
            continue
        assert open_price is not None
        assert high is not None
        assert low is not None
        assert close is not None
        current_start = current["start"] if current is not None else None
        if current is None or (
            current_start is not None
            and (timestamp - current_start) >= timedelta(minutes=TRACK_INTERVAL_MINUTES)
        ):
            if current is not None:
                bars.append(current)
            current = {
                "start": timestamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
            }
        else:
            current_high = current["high"]
            current_low = current["low"]
            assert isinstance(current_high, Decimal)
            assert isinstance(current_low, Decimal)
            current["high"] = max(current_high, high)
            current["low"] = min(current_low, low)
            current["close"] = close
    if current is not None:
        bars.append(current)
    return bars


def _simulate_trade(
    bars: list[dict[str, object]],
    *,
    exit_price: Decimal,
    stop_loss: Decimal | None,
    calendar: EGXTradingCalendar,
) -> tuple[str, Decimal | None, int | None, bool, int | None]:
    if not bars:
        return "no_data", None, None, False, None
    session_start = bars[0]["start"]
    assert isinstance(session_start, datetime)
    for index, bar in enumerate(bars):
        start = bar["start"]
        assert isinstance(start, datetime)
        low = bar["low"]
        high = bar["high"]
        assert isinstance(low, Decimal)
        assert isinstance(high, Decimal)
        if stop_loss is not None and low <= stop_loss:
            minutes = int((start - session_start).total_seconds() // 60)
            return "stop", stop_loss, minutes, False, index
        if high >= exit_price:
            minutes = int((start - session_start).total_seconds() // 60)
            return "target", exit_price, minutes, True, index
    close = bars[-1]["close"]
    assert isinstance(close, Decimal)
    return "close", close, None, False, len(bars) - 1


def _tracked_points(
    bars: list[dict[str, object]],
    *,
    calendar: EGXTradingCalendar,
    exit_at: int | None,
) -> tuple[TrackedPoint, ...]:
    points: list[TrackedPoint] = []
    for index, bar in enumerate(bars):
        if exit_at is not None and index > exit_at:
            break
        start = bar["start"]
        assert isinstance(start, datetime)
        price = bar["close"]
        high = bar["high"]
        low = bar["low"]
        assert isinstance(price, Decimal)
        assert isinstance(high, Decimal)
        assert isinstance(low, Decimal)
        points.append(TrackedPoint(timestamp=start, price=price, high=high, low=low))
    return tuple(points)


def _exit_target(
    targets: tuple[Decimal, ...],
    *,
    exit_mode: str,
) -> Decimal | None:
    if not targets:
        return None
    if exit_mode == _EXIT_MODE_HIGHEST:
        return max(targets)
    if len(targets) >= 2:
        return targets[1]
    return targets[0]


def _summary_stats(trades: list[SessionTrade]) -> dict[str, Any]:
    evaluated = [trade for trade in trades if trade.exit_reason != "skipped"]
    traded = [trade for trade in evaluated if trade.return_pct is not None]
    hits = [trade for trade in traded if trade.hit]
    misses = [trade for trade in traded if not trade.hit]
    skipped = [trade for trade in trades if trade.exit_reason == "skipped"]

    def median(values: list[float]) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2 == 1:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2.0

    minutes = sorted(trade.minutes_to_exit for trade in hits if trade.minutes_to_exit is not None)
    returns = [trade.return_pct for trade in traded if trade.return_pct is not None]
    hit_returns = [trade.return_pct for trade in hits if trade.return_pct is not None]
    miss_returns = [trade.return_pct for trade in misses if trade.return_pct is not None]

    return {
        "reports_scanned": len({trade.report_id for trade in trades}),
        "trades": len(traded),
        "hits": len(hits),
        "misses": len(misses),
        "skipped": len(skipped),
        "hit_rate_pct": round(len(hits) / len(traded) * 100, 2) if traded else 0.0,
        "avg_return_pct": round(sum(returns) / len(returns), 2) if returns else 0.0,
        "median_return_pct": median(returns),
        "avg_hit_return_pct": (round(sum(hit_returns) / len(hit_returns), 2) if hit_returns else 0.0),
        "avg_miss_return_pct": (round(sum(miss_returns) / len(miss_returns), 2) if miss_returns else 0.0),
        "median_minutes_to_hit": median([float(m) for m in minutes]),
        "best_return_pct": max(returns) if returns else 0.0,
        "worst_return_pct": min(returns) if returns else 0.0,
        "cumulative_return_pct": round(sum(returns), 2),
    }


async def execute_daily_report_backtest(
    db: Session,
    provider: MarketDataProvider,
    *,
    start_date: date,
    end_date: date,
    rank: int | None,
    exit_mode: str,
    calendar: EGXTradingCalendar,
) -> LabsDailyBacktestResult:
    if start_date > end_date:
        raise LabsBacktestRangeError("start_date must be on or before end_date")
    if (end_date - start_date).days > MAX_RANGE_DAYS:
        raise LabsBacktestRangeError(f"The backtest range is limited to {MAX_RANGE_DAYS} calendar days")
    if exit_mode not in {_EXIT_MODE_TARGET_TWO, _EXIT_MODE_HIGHEST}:
        raise LabsBacktestRangeError(f"Unsupported exit_mode: {exit_mode}")

    reports = list(
        db.scalars(
            select(MarketReport)
            .where(
                MarketReport.status == "complete",
                MarketReport.target_session_date >= start_date,
                MarketReport.target_session_date <= end_date,
            )
            .order_by(MarketReport.target_session_date.asc())
        ).all()
    )

    pairs: list[tuple[MarketReport, MarketReportItem]] = []
    for report in reports:
        items = db.scalars(
            select(MarketReportItem)
            .where(MarketReportItem.report_id == report.id)
            .order_by(MarketReportItem.rank)
        ).all()
        for item in items:
            if rank is not None and item.rank != rank:
                continue
            pairs.append((report, item))

    tickers = sorted({item.ticker for _, item in pairs})
    period = _fetch_period(start_date, end_date)

    semaphore = asyncio.Semaphore(_FETCH_CONCURRENCY)
    series_by_ticker: dict[str, CandleSeries] = {}

    async def fetch_one(ticker: str) -> None:
        async with semaphore:
            try:
                series = await provider.get_history(
                    ticker,
                    period=period,
                    interval=SOURCE_INTERVAL,
                )
            except Exception as exc:
                logger.warning("Labs backtest fetch failed for %s: %s", ticker, exc)
                return
            series_by_ticker[ticker] = series

    await asyncio.gather(*(fetch_one(ticker) for ticker in tickers))

    trades: list[SessionTrade] = []
    for report, item in pairs:
        targets, stop_loss, price_at_analysis = _prediction_levels(item.payload)
        exit_price = _exit_target(targets, exit_mode=exit_mode)
        series = series_by_ticker.get(item.ticker)
        if series is None:
            trades.append(
                SessionTrade(
                    report_id=report.id,
                    target_session_date=report.target_session_date,
                    rank=item.rank,
                    ticker=item.ticker,
                    score=round(item.score_bp / 100.0, 2),
                    price_at_analysis=price_at_analysis,
                    targets=targets,
                    stop_loss=stop_loss,
                    session_open=None,
                    exit_price=exit_price,
                    exit_reason="skipped",
                    hit=False,
                    minutes_to_exit=None,
                    return_pct=None,
                    tracked=(),
                )
            )
            continue
        if exit_price is None:
            trades.append(
                SessionTrade(
                    report_id=report.id,
                    target_session_date=report.target_session_date,
                    rank=item.rank,
                    ticker=item.ticker,
                    score=round(item.score_bp / 100.0, 2),
                    price_at_analysis=price_at_analysis,
                    targets=targets,
                    stop_loss=stop_loss,
                    session_open=None,
                    exit_price=None,
                    exit_reason="skipped",
                    hit=False,
                    minutes_to_exit=None,
                    return_pct=None,
                    tracked=(),
                )
            )
            continue
        bars = _session_bars(series, target_session_date=report.target_session_date, calendar=calendar)
        exit_reason, exit_at_price, minutes, hit, exit_index = _simulate_trade(
            bars,
            exit_price=exit_price,
            stop_loss=stop_loss,
            calendar=calendar,
        )
        session_open = bars[0]["open"] if bars else None
        assert session_open is None or isinstance(session_open, Decimal)
        return_pct = None
        if session_open is not None and exit_at_price is not None:
            return_pct = _round((exit_at_price / session_open - Decimal("1")) * 100)
        trades.append(
            SessionTrade(
                report_id=report.id,
                target_session_date=report.target_session_date,
                rank=item.rank,
                ticker=item.ticker,
                score=round(item.score_bp / 100.0, 2),
                price_at_analysis=price_at_analysis,
                targets=targets,
                stop_loss=stop_loss,
                session_open=session_open,
                exit_price=exit_at_price,
                exit_reason=exit_reason,
                hit=hit,
                minutes_to_exit=minutes,
                return_pct=return_pct,
                tracked=_tracked_points(
                    bars,
                    calendar=calendar,
                    exit_at=exit_index,
                ),
            )
        )

    return LabsDailyBacktestResult(
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "rank": rank,
            "exit_mode": exit_mode,
            "track_interval_minutes": TRACK_INTERVAL_MINUTES,
            "source_interval": SOURCE_INTERVAL,
        },
        summary=_summary_stats(trades),
        sessions=tuple(trades),
    )

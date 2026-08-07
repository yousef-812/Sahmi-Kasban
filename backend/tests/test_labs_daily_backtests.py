from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.market_data.types import CandleSeries
from app.models import MarketReport, MarketReportItem
from app.services.labs_daily_backtests import (
    MAX_RANGE_DAYS,
    LabsBacktestRangeError,
    execute_daily_report_backtest,
)

_CALENDAR_TZ = ZoneInfo("Africa/Cairo")
_CALENDAR = None


def _calendar():
    global _CALENDAR
    if _CALENDAR is None:
        from app.market_calendar import EGXTradingCalendar

        _CALENDAR = EGXTradingCalendar(
            timezone_name="Africa/Cairo",
            holidays=frozenset(),
            scan_hour=15,
            scan_minute=30,
        )
    return _CALENDAR


class FakeIntradayProvider:
    name = "fake-intraday"

    def __init__(self, candles_by_ticker: dict[str, tuple[dict[str, object], ...]]) -> None:
        self.candles_by_ticker = candles_by_ticker
        self.calls: list[str] = []

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls.append((ticker, interval, period))
        candles = self.candles_by_ticker.get(ticker, ())
        data_as_of = datetime(2026, 7, 31, 15, 0, tzinfo=UTC)
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=data_as_of,
            data_as_of=data_as_of,
            fingerprint=f"labs-{ticker}-{len(candles)}",
            candles=candles,
        )


def _candle(
    day: int,
    hour: int,
    minute: int,
    *,
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> dict[str, object]:
    return {
        "timestamp": datetime(
            2026, 7, day, hour, minute, tzinfo=_CALENDAR_TZ
        ).astimezone(UTC).isoformat(),
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": 100_000,
    }


def _session_candles(
    day: int, prices: list[tuple[float, float, float, float]]
) -> tuple[dict[str, object], ...]:
    candles = []
    for index, (open_price, high, low, close) in enumerate(prices):
        candles.append(
            _candle(
                day,
                10 + index // 12,
                (index % 12) * 5,
                open_price=open_price,
                high=high,
                low=low,
                close=close,
            )
        )
    return tuple(candles)


def _create_report(
    db: Session,
    *,
    target_session_date: date,
    tickers: list[tuple[str, list[float]]],
) -> MarketReport:
    report = MarketReport(
        target_session_date=target_session_date,
        status="complete",
        generated_at=datetime(2026, 7, 30, 15, 5, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-30"},
        market_summary={"title": "Daily Top 10"},
    )
    db.add(report)
    db.flush()
    for rank, (ticker, targets) in enumerate(tickers, start=1):
        db.add(
            MarketReportItem(
                report_id=report.id,
                ticker=ticker,
                rank=rank,
                score_bp=9000 - rank,
                payload={
                    "ticker": ticker,
                    "rank": rank,
                    "price_at_analysis": 100.0,
                    "expected_direction": "up",
                    "analysis": {
                        "targets": targets,
                        "stop_loss": 95.0,
                    },
                },
            )
        )
    db.commit()
    return report


def test_target_two_hit_and_miss_are_aggregated(db_session: Session) -> None:
    _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        tickers=[
            ("HIT", [105.0, 110.0]),
            ("MISS", [120.0, 130.0]),
        ],
    )
    # HIT: price climbs to 111 within the session -> target two (110) reached.
    # MISS: price never reaches 130 -> exits at session close.
    hit_prices = [(100, 101, 99, 100.5), (100.5, 103, 100, 102), (102, 111, 101, 110.5)]
    miss_prices = [(100, 100.5, 99.5, 100), (100, 101, 99.5, 100.2), (100.2, 102, 100, 101)]
    provider = FakeIntradayProvider(
        {
            "HIT": _session_candles(27, hit_prices),
            "MISS": _session_candles(27, miss_prices),
        }
    )

    result = asyncio.run(
        execute_daily_report_backtest(
            db_session,
            provider,
            start_date=date(2026, 7, 27),
            end_date=date(2026, 7, 27),
            rank=None,
            exit_mode="target_2",
            calendar=_calendar(),
        )
    )

    assert len(result.sessions) == 2
    by_ticker = {trade.ticker: trade for trade in result.sessions}
    assert by_ticker["HIT"].hit is True
    assert by_ticker["HIT"].exit_reason == "target"
    assert by_ticker["HIT"].exit_price == Decimal("110")
    assert by_ticker["HIT"].return_pct is not None
    assert by_ticker["HIT"].return_pct > 9.0
    assert by_ticker["HIT"].minutes_to_exit is not None
    assert by_ticker["MISS"].hit is False
    assert by_ticker["MISS"].exit_reason == "close"

    summary = result.summary
    assert summary["trades"] == 2
    assert summary["hits"] == 1
    assert summary["misses"] == 1
    assert summary["hit_rate_pct"] == 50.0


def test_stop_loss_exits_before_target(db_session: Session) -> None:
    _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        tickers=[("STOP", [105.0, 110.0])],
    )
    # First bar drops below stop (95) before any target is reached.
    prices = [(100, 100.5, 94.0, 94.5), (94.5, 96, 94, 95.5)]
    provider = FakeIntradayProvider({"STOP": _session_candles(27, prices)})

    result = asyncio.run(
        execute_daily_report_backtest(
            db_session,
            provider,
            start_date=date(2026, 7, 27),
            end_date=date(2026, 7, 27),
            rank=None,
            exit_mode="target_2",
            calendar=_calendar(),
        )
    )

    trade = result.sessions[0]
    assert trade.exit_reason == "stop"
    assert trade.hit is False
    assert trade.exit_price == Decimal("95")


def test_highest_target_mode_uses_last_target(db_session: Session) -> None:
    _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        tickers=[("HIGH", [105.0, 110.0, 115.0])],
    )
    # Price reaches 112: hits target 2 (110) but not highest (115).
    prices = [(100, 101, 99, 100.5), (100.5, 112, 100, 111)]
    provider = FakeIntradayProvider({"HIGH": _session_candles(27, prices)})

    highest = asyncio.run(
        execute_daily_report_backtest(
            db_session,
            provider,
            start_date=date(2026, 7, 27),
            end_date=date(2026, 7, 27),
            rank=None,
            exit_mode="highest",
            calendar=_calendar(),
        )
    )
    assert highest.sessions[0].hit is False

    target_two = asyncio.run(
        execute_daily_report_backtest(
            db_session,
            provider,
            start_date=date(2026, 7, 27),
            end_date=date(2026, 7, 27),
            rank=None,
            exit_mode="target_2",
            calendar=_calendar(),
        )
    )
    assert target_two.sessions[0].hit is True
    assert target_two.sessions[0].exit_price == Decimal("110")


def test_rank_filter_selects_single_item(db_session: Session) -> None:
    _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        tickers=[
            ("R1", [105.0]),
            ("R2", [120.0]),
        ],
    )
    provider = FakeIntradayProvider(
        {
            "R1": _session_candles(27, [(100, 106, 99, 105)]),
            "R2": _session_candles(27, [(100, 101, 99, 100)]),
        }
    )

    result = asyncio.run(
        execute_daily_report_backtest(
            db_session,
            provider,
            start_date=date(2026, 7, 27),
            end_date=date(2026, 7, 27),
            rank=2,
            exit_mode="target_2",
            calendar=_calendar(),
        )
    )

    assert [trade.ticker for trade in result.sessions] == ["R2"]


def test_range_too_wide_is_rejected(db_session: Session) -> None:
    provider = FakeIntradayProvider({})
    try:
        asyncio.run(
            execute_daily_report_backtest(
                db_session,
                provider,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 3, 1),
                rank=None,
                exit_mode="target_2",
                calendar=_calendar(),
            )
        )
    except LabsBacktestRangeError as exc:
        assert str(MAX_RANGE_DAYS) in str(exc)
    else:
        raise AssertionError("expected LabsBacktestRangeError")


def _create_report_with_trade_plan(
    db: Session,
    *,
    target_session_date: date,
    tickers: list[tuple[str, dict[str, object]]],
) -> MarketReport:
    report = MarketReport(
        target_session_date=target_session_date,
        status="complete",
        generated_at=datetime(2026, 7, 30, 15, 5, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-30"},
        market_summary={"title": "Daily Top 10"},
    )
    db.add(report)
    db.flush()
    for rank, (ticker, plan) in enumerate(tickers, start=1):
        db.add(
            MarketReportItem(
                report_id=report.id,
                ticker=ticker,
                rank=rank,
                score_bp=9000 - rank,
                payload={
                    "ticker": ticker,
                    "rank": rank,
                    "expected_direction": "up",
                    "analysis": {
                        "trade_plan": {
                            "entry": 100.0,
                            "stop_loss": 95.0,
                            "target_1": 105.0,
                            "target_2": 110.0,
                            **plan,
                        },
                    },
                },
            )
        )
    db.commit()
    return report


def test_trade_plan_format_is_used_for_targets(db_session: Session) -> None:
    _create_report_with_trade_plan(
        db_session,
        target_session_date=date(2026, 7, 27),
        tickers=[("PLAN", {})],
    )
    # Price reaches 111 -> target two (110) from trade_plan should trigger.
    prices = [(100, 101, 99, 100.5), (100.5, 111, 100, 110.5)]
    provider = FakeIntradayProvider({"PLAN": _session_candles(27, prices)})

    result = asyncio.run(
        execute_daily_report_backtest(
            db_session,
            provider,
            start_date=date(2026, 7, 27),
            end_date=date(2026, 7, 27),
            rank=None,
            exit_mode="target_2",
            calendar=_calendar(),
        )
    )

    assert len(result.sessions) == 1
    trade = result.sessions[0]
    assert trade.exit_reason == "target"
    assert trade.exit_price == Decimal("110")
    assert trade.hit is True
    assert result.summary["trades"] == 1
    assert result.summary["skipped"] == 0

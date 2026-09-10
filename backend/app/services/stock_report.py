from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sahmi_kasban.engines.investment import (
    FundamentalInvestmentEngine,
    InvestmentMetrics,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_data.egx_symbols import EGX_ARABIC_NAMES
from app.market_data.fundamental import (
    FundamentalQuote,
    _fetch_fundamental_scanner_data,
)
from app.market_data.types import MarketDataProvider
from app.models import MarketDataSnapshot, MarketInstrumentCatalog

logger = logging.getLogger(__name__)


# ─── Bounce pattern config (surge → small-candle correction → bounce) ─────────
_BOUNCE_SURGE_WINDOW = 5          # sessions of the surge leg
_BOUNCE_SURGE_MIN_PCT = 12.0     # min gain of the surge leg
_BOUNCE_PULLBACK_MIN_PCT = 4.0   # min correction from the peak
_BOUNCE_PULLBACK_MAX_PCT = 15.0  # max correction from the peak
_BOUNCE_CONSOL_WINDOW = 5        # last N sessions must be small candles
_BOUNCE_MAX_AVG_BODY_PCT = 1.5  # max avg candle body of consolidation
_BOUNCE_MAX_RANGE_RATIO = 0.5   # consolidation avg range vs surge avg range
_BOUNCE_MIN_CANDLES = 12         # min history length for pattern detection


@dataclass
class BounceSignal:
    surge_gain_pct: float
    pullback_pct: float
    avg_body_pct: float
    range_ratio: float
    volume_confirmed: bool
    score: float


def _num(value: object, default: float = 0.0) -> float:
    try:
        result = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return result if result == result else default  # filter NaN


def detect_bounce_pattern(
    candles: list[dict],
    *,
    fair_upside_pct: float | None = None,
) -> BounceSignal | None:
    """Detect surge → small-candle correction pattern in daily candles.

    1. Latest 5-session window gaining >= 12% (surge leg).
    2. Correction of 4–15% from the post-surge peak, holding above the
       surge-start close.
    3. Last 5 candles are small: avg body <= 1.5% and avg range <= 50%
       of the surge-leg avg range.
    4. Volume contraction during consolidation (skipped as neutral when
       volume data is missing).
    """
    n = len(candles)
    if n < _BOUNCE_MIN_CANDLES:
        return None

    closes = [_num(c.get("close")) for c in candles]
    opens = [_num(c.get("open")) for c in candles]
    highs = [_num(c.get("high")) for c in candles]
    lows = [_num(c.get("low")) for c in candles]
    volumes = [_num(c.get("volume")) for c in candles]
    if any(v <= 0 for v in closes + opens + highs + lows):
        return None

    # 3. Consolidation: last 5 candles must be small-bodied.
    consol = range(n - _BOUNCE_CONSOL_WINDOW, n)
    avg_body = sum(abs(closes[i] - opens[i]) / closes[i] for i in consol) / _BOUNCE_CONSOL_WINDOW * 100.0
    if avg_body > _BOUNCE_MAX_AVG_BODY_PCT:
        return None
    consol_range = sum((highs[i] - lows[i]) / closes[i] for i in consol) / _BOUNCE_CONSOL_WINDOW

    # 1. Latest surge leg (5 moves) fully before the consolidation window.
    surge_start: int | None = None
    surge_gain = 0.0
    for i in range(0, n - _BOUNCE_CONSOL_WINDOW - _BOUNCE_SURGE_WINDOW):
        if closes[i] <= 0:
            continue
        gain = (closes[i + _BOUNCE_SURGE_WINDOW] - closes[i]) / closes[i] * 100.0
        if gain >= _BOUNCE_SURGE_MIN_PCT:
            surge_start, surge_gain = i, gain  # keep the latest
    if surge_start is None:
        return None

    surge_idx = range(surge_start, surge_start + _BOUNCE_SURGE_WINDOW + 1)
    surge_len = len(surge_idx)
    surge_range = sum((highs[i] - lows[i]) / closes[i] for i in surge_idx) / surge_len
    if surge_range <= 0:
        return None
    range_ratio = consol_range / surge_range
    if range_ratio > _BOUNCE_MAX_RANGE_RATIO:
        return None

    # 2. Healthy correction from the post-surge peak.
    peak = max(highs[surge_start:])
    last_close = closes[-1]
    if peak <= 0:
        return None
    pullback = (peak - last_close) / peak * 100.0
    if not (_BOUNCE_PULLBACK_MIN_PCT <= pullback <= _BOUNCE_PULLBACK_MAX_PCT):
        return None
    if last_close < closes[surge_start]:
        return None

    # 4. Volume contraction (neutral when data is missing).
    surge_vol = sum(volumes[i] for i in surge_idx) / surge_len
    consol_vol = sum(volumes[i] for i in consol) / _BOUNCE_CONSOL_WINDOW
    volume_confirmed = surge_vol > 0 and consol_vol > 0 and consol_vol < surge_vol
    if surge_vol > 0 and consol_vol > 0 and consol_vol > surge_vol:
        return None

    score = surge_gain + pullback * 0.5
    score += max(0.0, _BOUNCE_MAX_AVG_BODY_PCT - avg_body) * 4.0
    score += max(0.0, _BOUNCE_MAX_RANGE_RATIO - range_ratio) * 10.0
    if volume_confirmed:
        score += 3.0
    if fair_upside_pct is not None and fair_upside_pct > 0:
        score += min(fair_upside_pct, 50.0) * 0.1

    return BounceSignal(
        surge_gain_pct=round(surge_gain, 1),
        pullback_pct=round(pullback, 1),
        avg_body_pct=round(avg_body, 2),
        range_ratio=round(range_ratio, 2),
        volume_confirmed=volume_confirmed,
        score=round(score, 1),
    )


@dataclass
class StockReportItem:
    ticker: str
    company_name: str
    current_price: float
    fair_value: float | None = None
    margin_of_safety_pct: float | None = None
    investment_score: float | None = None
    price_change_pct: float | None = None
    expected_recovery_pct: float | None = None
    bounce_score: float | None = None
    pe_ratio: float | None = None
    sector: str = "عام"


@dataclass
class StockReportResult:
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    undervalued: list[StockReportItem] = field(default_factory=list)
    dropped: list[StockReportItem] = field(default_factory=list)
    bounce_candidates: list[StockReportItem] = field(default_factory=list)


async def generate_stock_report(
    db: Session,
    provider: MarketDataProvider,
) -> StockReportResult:
    """Generate the admin stock report with 3 sections:

    1. Stocks priced below fair value (margin_of_safety >= 15%)
    2. Stocks that dropped >=10% in the last month
    3. Bounce candidates (surge >= 12% in 5 sessions, then 4–15%
       correction with small consolidation candles + volume contraction)
    """
    result = StockReportResult()

    try:
        fundamental_data = await _fetch_fundamental_scanner_data()
    except Exception as exc:
        logger.warning("Failed to fetch fundamental data for stock report: %s", exc)
        fundamental_data = {}

    catalog_rows = (
        db.query(MarketInstrumentCatalog)
        .filter(MarketInstrumentCatalog.active.is_(True))
        .all()
    )
    catalog_map = {row.ticker: row for row in catalog_rows}

    valid_tickers: list[str] = []
    for ticker in fundamental_data:
        if len(ticker) > 6 or (ticker.startswith("EGS") and len(ticker) > 4):
            continue
        if ticker not in catalog_map:
            continue
        valid_tickers.append(ticker)

    # --- Compute fundamental metrics ---
    ticker_metrics: dict[str, tuple[FundamentalQuote, InvestmentMetrics]] = {}
    for ticker in valid_tickers:
        quote = fundamental_data[ticker]
        try:
            metrics = FundamentalInvestmentEngine.calculate_metrics(
                ticker=ticker,
                current_price=quote.close,
                pe_ratio=quote.pe_ratio,
                pb_ratio=quote.pb_ratio,
                dividend_yield_pct=quote.dividend_yield_pct,
                roe_pct=quote.roe_pct,
                total_debt=quote.total_debt,
                market_cap=quote.market_cap,
                net_income=quote.net_income,
                eps=quote.eps,
            )
            ticker_metrics[ticker] = (quote, metrics)
        except Exception as exc:
            logger.debug("Metrics calculation failed for %s: %s", ticker, exc)

    # --- Section 1: Undervalued stocks (fair value > current price by >= 15%) ---
    undervalued: list[StockReportItem] = []
    for ticker, (quote, metrics) in ticker_metrics.items():
        if (
            metrics.margin_of_safety_pct is not None
            and metrics.margin_of_safety_pct >= 15.0
            and metrics.fair_value is not None
            and metrics.fair_value > 0
        ):
            catalog_item = catalog_map.get(ticker)
            company_name = (
                catalog_item.description
                if catalog_item and catalog_item.description
                else EGX_ARABIC_NAMES.get(ticker, ticker)
            )
            undervalued.append(
                StockReportItem(
                    ticker=ticker,
                    company_name=company_name,
                    current_price=quote.close,
                    fair_value=metrics.fair_value,
                    margin_of_safety_pct=metrics.margin_of_safety_pct,
                    investment_score=metrics.investment_score,
                    pe_ratio=metrics.pe_ratio,
                )
            )
    undervalued.sort(key=lambda x: x.margin_of_safety_pct or 0, reverse=True)
    result.undervalued = undervalued[:30]

    # --- Section 2 & 3: Price-based analysis (last month data) ---
    tickers_for_price = [
        t for t in valid_tickers if t not in ticker_metrics
    ] + list(ticker_metrics.keys())
    tickers_for_price = list(dict.fromkeys(tickers_for_price))  # deduplicate preserving order

    dropped: list[StockReportItem] = []
    bounce_candidates: list[StockReportItem] = []

    semaphore = asyncio.Semaphore(15)

    async def _fetch_candles(ticker: str) -> tuple[str, list[dict]]:
        """Return (ticker, daily candles) or (ticker, []) on failure."""
        async with semaphore:
            try:
                series = await provider.get_history(
                    ticker, period="1mo", interval="1d"
                )
                candles = [dict(c) for c in series.candles]
                if len(candles) < 5:
                    return ticker, []
                return ticker, candles
            except Exception as exc:
                logger.debug("Price fetch failed for %s: %s", ticker, exc)
                return ticker, []

    candle_tasks = [_fetch_candles(t) for t in tickers_for_price[:100]]
    candle_results = await asyncio.gather(*candle_tasks)

    candle_map: dict[str, list[dict]] = {}
    price_map: dict[str, tuple[float, float]] = {}
    for ticker, candles in candle_results:
        if not candles:
            continue
        candle_map[ticker] = candles
        try:
            current_price = float(candles[-1]["close"])
            first_price = float(candles[0]["open"])
        except (TypeError, ValueError, KeyError):
            continue
        if first_price <= 0 or current_price <= 0:
            continue
        change_pct = ((current_price - first_price) / first_price) * 100.0
        price_map[ticker] = (current_price, change_pct)

    for ticker in tickers_for_price[:100]:
        if ticker not in price_map:
            continue
        current_price, change_pct = price_map[ticker]
        catalog_item = catalog_map.get(ticker)
        company_name = (
            catalog_item.description
            if catalog_item and catalog_item.description
            else EGX_ARABIC_NAMES.get(ticker, ticker)
        )

        # Section 2: Dropped >= 10%
        if change_pct <= -10.0:
            quote, metrics = ticker_metrics.get(ticker, (None, None))
            dropped.append(
                StockReportItem(
                    ticker=ticker,
                    company_name=company_name,
                    current_price=current_price,
                    price_change_pct=change_pct,
                    fair_value=metrics.fair_value if metrics else None,
                    margin_of_safety_pct=metrics.margin_of_safety_pct if metrics else None,
                    investment_score=metrics.investment_score if metrics else None,
                    pe_ratio=quote.pe_ratio if quote else None,
                )
            )

        # Section 3: Bounce candidates (surge → small-candle correction).
        # Fair-value upside is a ranking bonus only, not a filter.
        quote, metrics = ticker_metrics.get(ticker, (None, None))
        fair_upside: float | None = None
        if metrics and metrics.fair_value and metrics.fair_value > 0 and current_price > 0:
            fair_upside = ((metrics.fair_value - current_price) / current_price) * 100.0
        signal = detect_bounce_pattern(
            candle_map.get(ticker, []), fair_upside_pct=fair_upside
        )
        if signal is not None:
            bounce_candidates.append(
                StockReportItem(
                    ticker=ticker,
                    company_name=company_name,
                    current_price=current_price,
                    price_change_pct=change_pct,
                    fair_value=metrics.fair_value if metrics else None,
                    expected_recovery_pct=round(fair_upside, 1)
                    if fair_upside is not None and fair_upside > 0
                    else None,
                    bounce_score=signal.score,
                    margin_of_safety_pct=metrics.margin_of_safety_pct if metrics else None,
                    investment_score=metrics.investment_score if metrics else None,
                    pe_ratio=quote.pe_ratio if quote else None,
                )
            )

    dropped.sort(key=lambda x: x.price_change_pct or 0)
    result.dropped = dropped[:30]

    bounce_candidates.sort(key=lambda x: x.bounce_score or 0, reverse=True)
    result.bounce_candidates = bounce_candidates[:30]

    return result


def _item_to_dict(item: StockReportItem) -> dict:
    return {
        "ticker": item.ticker,
        "company_name": item.company_name,
        "current_price": item.current_price,
        "fair_value": item.fair_value,
        "margin_of_safety_pct": item.margin_of_safety_pct,
        "investment_score": item.investment_score,
        "price_change_pct": item.price_change_pct,
        "expected_recovery_pct": item.expected_recovery_pct,
        "bounce_score": item.bounce_score,
        "pe_ratio": item.pe_ratio,
        "sector": item.sector,
    }


def stock_report_to_dict(result: StockReportResult) -> dict:
    return {
        "generated_at": result.generated_at.isoformat(),
        "undervalued": [_item_to_dict(i) for i in result.undervalued],
        "dropped": [_item_to_dict(i) for i in result.dropped],
        "bounce_candidates": [_item_to_dict(i) for i in result.bounce_candidates],
        "summary": {
            "undervalued_count": len(result.undervalued),
            "dropped_count": len(result.dropped),
            "bounce_count": len(result.bounce_candidates),
        },
    }


def persist_stock_report_snapshot(
    db: Session,
    result: StockReportResult,
) -> MarketDataSnapshot:
    """Store the stock report as a MarketDataSnapshot for idempotent daily caching."""
    report_dict = stock_report_to_dict(result)

    snapshot = db.scalar(
        select(MarketDataSnapshot)
        .where(MarketDataSnapshot.ticker == "__STOCK_REPORT__")
        .order_by(MarketDataSnapshot.fetched_at.desc())
        .limit(1)
    )
    if snapshot is None:
        snapshot = MarketDataSnapshot(
            ticker="__STOCK_REPORT__",
            provider="admin",
            interval="1d",
            period="1M",
            data_as_of=result.generated_at,
            fetched_at=result.generated_at,
            expires_at=result.generated_at,
            fingerprint="stock_report_v1",
            candle_count=(
                len(result.undervalued) + len(result.dropped) + len(result.bounce_candidates)
            ),
            payload=report_dict,
        )
        db.add(snapshot)
    else:
        snapshot.data_as_of = result.generated_at
        snapshot.fetched_at = result.generated_at
        snapshot.payload = report_dict
        snapshot.candle_count = (
            len(result.undervalued) + len(result.dropped) + len(result.bounce_candidates)
        )
    db.commit()
    return snapshot

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
    3. Bounce candidates (sharp decline + high expected recovery)
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

    async def _fetch_price_change(ticker: str) -> tuple[str, float | None, float | None]:
        """Return (ticker, current_price, month_change_pct) or (ticker, None, None) on failure."""
        async with semaphore:
            try:
                series = await provider.get_history(
                    ticker, period="1mo", interval="1d"
                )
                if series.candle_count < 5:
                    return ticker, None, None
                candles = list(series.candles)
                current_price = float(candles[-1]["close"])
                first_price = float(candles[0]["open"])
                if first_price <= 0:
                    return ticker, None, None
                change_pct = ((current_price - first_price) / first_price) * 100.0
                return ticker, current_price, change_pct
            except Exception as exc:
                logger.debug("Price fetch failed for %s: %s", ticker, exc)
                return ticker, None, None

    price_tasks = [_fetch_price_change(t) for t in tickers_for_price[:100]]
    price_results = await asyncio.gather(*price_tasks)

    price_map: dict[str, tuple[float, float]] = {}
    for ticker, current_price, change_pct in price_results:
        if current_price is not None and change_pct is not None:
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

        # Section 3: Bounce candidates (dropped >= 15% AND fair value exists with upside >= 20%)
        quote, metrics = ticker_metrics.get(ticker, (None, None))
        if metrics and metrics.fair_value and metrics.fair_value > 0:
            expected_recovery = ((metrics.fair_value - current_price) / current_price) * 100.0
            if change_pct <= -15.0 and expected_recovery >= 20.0:
                bounce_candidates.append(
                    StockReportItem(
                        ticker=ticker,
                        company_name=company_name,
                        current_price=current_price,
                        price_change_pct=change_pct,
                        fair_value=metrics.fair_value,
                        expected_recovery_pct=round(expected_recovery, 1),
                        margin_of_safety_pct=metrics.margin_of_safety_pct,
                        investment_score=metrics.investment_score,
                        pe_ratio=metrics.pe_ratio,
                    )
                )

    dropped.sort(key=lambda x: x.price_change_pct or 0)
    result.dropped = dropped[:30]

    bounce_candidates.sort(key=lambda x: x.expected_recovery_pct or 0, reverse=True)
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

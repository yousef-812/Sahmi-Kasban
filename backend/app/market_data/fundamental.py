from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.egx_symbols import EGX_ARABIC_NAMES, normalize_egx_ticker
from app.models import MarketInstrumentCatalog
from sahmi_kasban.engines.investment import FundamentalInvestmentEngine, InvestmentMetrics

logger = logging.getLogger(__name__)

_FUNDAMENTAL_COLUMNS = [
    "name",
    "close",
    "price_earnings_ttm",
    "price_book_fq",
    "dividends_yield_current",
    "return_on_equity_fq",
    "total_debt_fq",
    "market_cap_basic",
    "earnings_per_share_basic_ttm",
    "net_income_ttm",
]

_fundamental_cache: list[dict[str, Any]] | None = None
_fundamental_cache_at: datetime | None = None
_fundamental_cache_lock = asyncio.Lock()


@dataclass(frozen=True, slots=True)
class FundamentalQuote:
    ticker: str
    close: float
    pe_ratio: float | None
    pb_ratio: float | None
    dividend_yield_pct: float | None
    roe_pct: float | None
    total_debt: float | None
    market_cap: float | None
    eps: float | None
    net_income: float | None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        val = float(value)
        return val if not (val != val or val == float("inf") or val == float("-inf")) else None
    except (ValueError, TypeError):
        return None


async def _fetch_fundamental_scanner_data() -> dict[str, FundamentalQuote]:
    settings = get_settings()
    payload = {
        "filter": [{"left": "type", "operation": "equal", "right": "stock"}],
        "options": {"lang": "ar"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": _FUNDAMENTAL_COLUMNS,
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "range": [0, settings.market_instrument_catalog_max_symbols],
    }
    headers = {
        "Origin": settings.tradingview_origin,
        "Referer": f"{settings.tradingview_origin}/",
        "User-Agent": settings.tradingview_user_agent,
    }
    timeout = httpx.Timeout(settings.market_instrument_catalog_timeout_seconds)

    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.post(settings.tradingview_scanner_url, json=payload)
        response.raise_for_status()
        raw_data = response.json().get("data", [])

    result: dict[str, FundamentalQuote] = {}
    for item in raw_data:
        d = item.get("d", [])
        if len(d) < len(_FUNDAMENTAL_COLUMNS):
            continue

        raw_name = str(d[0]).strip().upper()
        ticker = normalize_egx_ticker(raw_name)
        close = _parse_float(d[1])
        if not ticker or close is None or close <= 0:
            continue

        quote = FundamentalQuote(
            ticker=ticker,
            close=close,
            pe_ratio=_parse_float(d[2]),
            pb_ratio=_parse_float(d[3]),
            dividend_yield_pct=_parse_float(d[4]),
            roe_pct=_parse_float(d[5]),
            total_debt=_parse_float(d[6]),
            market_cap=_parse_float(d[7]),
            eps=_parse_float(d[8]),
            net_income=_parse_float(d[9]),
        )
        result[ticker] = quote

    return result


async def get_egx_investment_rankings(
    db: Session,
    *,
    limit: int = 10,
    force_refresh: bool = False,
) -> list[dict[str, Any]]:
    """Calculates fundamental investment rankings for EGX active stocks."""
    global _fundamental_cache, _fundamental_cache_at

    now = datetime.now(UTC)
    if (
        not force_refresh
        and _fundamental_cache is not None
        and _fundamental_cache_at is not None
        and now - _fundamental_cache_at < timedelta(hours=1)
    ):
        return _fundamental_cache[:limit]

    async with _fundamental_cache_lock:
        if (
            not force_refresh
            and _fundamental_cache is not None
            and _fundamental_cache_at is not None
            and now - _fundamental_cache_at < timedelta(hours=1)
        ):
            return _fundamental_cache[:limit]

        try:
            data = await _fetch_fundamental_scanner_data()
        except Exception as exc:
            logger.warning("Failed to fetch TradingView fundamental data: %s", exc)
            if _fundamental_cache is not None:
                return _fundamental_cache[:limit]
            return []

        # Get catalog items for company name and sector
        catalog_rows = db.query(MarketInstrumentCatalog).filter(
            MarketInstrumentCatalog.is_active.is_(True),
            MarketInstrumentCatalog.is_tradable.is_(True),
        ).all()
        catalog_map = {row.ticker: row for row in catalog_rows}

        ranked_items: list[dict[str, Any]] = []
        for ticker, quote in data.items():
            catalog_item = catalog_map.get(ticker)
            company_name = (
                catalog_item.name_arabic
                if catalog_item and catalog_item.name_arabic
                else EGX_ARABIC_NAMES.get(ticker, ticker)
            )
            sector = catalog_item.sector if catalog_item else "عام"

            metrics: InvestmentMetrics = FundamentalInvestmentEngine.calculate_metrics(
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

            # Filter out extreme penny stocks or zero volume anomalies if needed
            if metrics.investment_score >= 45.0:
                ranked_items.append({
                    "ticker": ticker,
                    "company_name": company_name,
                    "sector": sector,
                    "current_price": metrics.current_price,
                    "investment_score": metrics.investment_score,
                    "pe_ratio": metrics.pe_ratio,
                    "pb_ratio": metrics.pb_ratio,
                    "dividend_yield_pct": metrics.dividend_yield_pct,
                    "roe_pct": metrics.roe_pct,
                    "fair_value": metrics.fair_value,
                    "margin_of_safety_pct": metrics.margin_of_safety_pct,
                    "investment_category": metrics.investment_category,
                    "strengths": list(metrics.strengths),
                    "risks": list(metrics.risks),
                })

        # Sort by investment_score descending, then by margin of safety
        ranked_items.sort(
            key=lambda x: (
                x["investment_score"],
                x["margin_of_safety_pct"] or 0.0,
                x["dividend_yield_pct"] or 0.0,
            ),
            reverse=True,
        )

        _fundamental_cache = ranked_items
        _fundamental_cache_at = now
        logger.info("Generated %s EGX fundamental investment rankings", len(ranked_items))
        return ranked_items[:limit]


async def get_stock_investment_metric(db: Session, ticker: str) -> dict[str, Any] | None:
    normalized = normalize_egx_ticker(ticker)
    rankings = await get_egx_investment_rankings(db, limit=None)
    for item in rankings:
        if item["ticker"] == normalized:
            return item

    # If not in top rankings, compute directly from scanner data
    try:
        data = await _fetch_fundamental_scanner_data()
        quote = data.get(normalized)
        if quote is None:
            return None

        catalog_item = (
            db.query(MarketInstrumentCatalog)
            .filter(
                MarketInstrumentCatalog.ticker == normalized,
            )
            .first()
        )
        company_name = (
            catalog_item.name_arabic
            if catalog_item and catalog_item.name_arabic
            else EGX_ARABIC_NAMES.get(normalized, normalized)
        )
        sector = catalog_item.sector if catalog_item else "عام"

        metrics = FundamentalInvestmentEngine.calculate_metrics(
            ticker=normalized,
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

        return {
            "ticker": normalized,
            "company_name": company_name,
            "sector": sector,
            "current_price": metrics.current_price,
            "investment_score": metrics.investment_score,
            "pe_ratio": metrics.pe_ratio,
            "pb_ratio": metrics.pb_ratio,
            "dividend_yield_pct": metrics.dividend_yield_pct,
            "roe_pct": metrics.roe_pct,
            "fair_value": metrics.fair_value,
            "margin_of_safety_pct": metrics.margin_of_safety_pct,
            "investment_category": metrics.investment_category,
            "strengths": list(metrics.strengths),
            "risks": list(metrics.risks),
        }
    except Exception as exc:
        logger.warning("Failed to calculate single investment metric for %s: %s", normalized, exc)
        return None


async def compare_stocks_investment(db: Session, tickers: list[str]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for ticker in tickers:
        metric = await get_stock_investment_metric(db, ticker)
        if metric:
            items.append(metric)

    if not items:
        return {
            "items": [],
            "best_ticker": "",
            "summary": "تعذر العثور على بيانات استثمارية للأسهم المحددة.",
        }

    # Sort items by investment score descending
    items.sort(
        key=lambda x: (
            x["investment_score"],
            x["margin_of_safety_pct"] or 0.0,
            x["dividend_yield_pct"] or 0.0,
        ),
        reverse=True,
    )

    best = items[0]
    best_ticker = best["ticker"]
    best_name = best["company_name"]
    best_score = best["investment_score"]

    summary = (
        f"وفقاً للتحليل المالي الأساسي ومكررات الربحية وهامش الأمان، تتصدر شركة {best_name} ({best_ticker}) "
        f"المقارنة بتقييم استثماري {best_score:.1f}/100 "
    )
    if best.get("margin_of_safety_pct") and best["margin_of_safety_pct"] > 0:
        summary += f"مع هامش أمان يقدر بـ +{best['margin_of_safety_pct']:.1f}% عن القيمة العادلة."
    elif best.get("dividend_yield_pct") and best["dividend_yield_pct"] > 5:
        summary += f"وعائد توزيعات نقدية مغري يصل إلى {best['dividend_yield_pct']:.1f}%."
    else:
        summary += "مع استقرار في المؤشرات المالية والربحية."

    return {
        "items": items,
        "best_ticker": best_ticker,
        "summary": summary,
    }

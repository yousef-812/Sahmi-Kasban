"""Buy/sell pressure (CLV volume split) for one ticker — WP-29.

The split is computed from cached daily OHLCV candles via the core
``flow_summary`` (CLV-weighted volume): a documented pressure *estimate*,
not real order-flow — EGX exposes no free L2 feed (see ``order_flow.py``).
"""

from __future__ import annotations

import logging

import pandas as pd
from sahmi_kasban.indicators import flow_summary, prepare_candles
from sqlalchemy.orm import Session

from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataUnavailableError, UnknownTickerError

logger = logging.getLogger(__name__)


def _unavailable(ticker: str, *, reason: str) -> dict[str, object]:
    return {
        "available": False,
        "ticker": ticker,
        "buy_share_pct": None,
        "sell_share_pct": None,
        "buy_volume": None,
        "sell_volume": None,
        "net_volume": None,
        "ad_trend": 0,
        "mfi14": None,
        "obv_trend": 0,
        "verdict": "neutral",
        "window_days": 0,
        "as_of": None,
        "reason": reason,
    }


async def compute_stock_flow(db: Session, ticker: str, *, days: int = 90) -> dict[str, object]:
    """Return the buy/sell pressure summary of a ticker over the last ``days`` sessions."""
    normalized = normalize_egx_ticker(ticker)
    try:
        series, _cached = await get_cached_or_fresh_history(db, get_market_data_provider(), normalized)
    except UnknownTickerError as exc:
        return _unavailable(normalized, reason=str(exc))
    except MarketDataUnavailableError as exc:
        logger.warning("Stock flow could not load candles for %s: %s", normalized, exc)
        return _unavailable(normalized, reason=str(exc))

    try:
        frame = prepare_candles(pd.DataFrame(series.candles))
    except ValueError as exc:
        return _unavailable(normalized, reason=f"Unusable candle history: {exc}")

    window = max(1, min(days, len(frame)))
    summary = flow_summary(frame, window=window)
    return {
        "available": True,
        "ticker": normalized,
        "buy_share_pct": summary["buy_share_pct"],
        "sell_share_pct": summary["sell_share_pct"],
        "buy_volume": summary["buy_volume"],
        "sell_volume": summary["sell_volume"],
        "net_volume": summary["net_volume"],
        "ad_trend": summary["ad_trend"],
        "mfi14": summary["mfi14"],
        "obv_trend": summary["obv_trend"],
        "verdict": summary["verdict"],
        "window_days": window,
        "as_of": series.data_as_of,
        "reason": None,
    }

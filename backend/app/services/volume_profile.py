"""Volume profile (POC / value area) for one ticker — WP-30.

Built from cached daily OHLCV candles: each candle's volume is split across
the price bins its range touches, so bin volumes sum to candle volume
exactly. This is a daily-candle approximation — true volume-at-price needs
intrabar data EGX does not expose for free.
"""

from __future__ import annotations

import logging

import pandas as pd
from sahmi_kasban.indicators import prepare_candles
from sahmi_kasban.volume_profile import build_volume_profile
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
        "poc": None,
        "value_area_high": None,
        "value_area_low": None,
        "bins": [],
        "above_value_pct": None,
        "below_value_pct": None,
        "window_days": 0,
        "as_of": None,
        "reason": reason,
    }


async def compute_volume_profile(db: Session, ticker: str, *, days: int = 250) -> dict[str, object]:
    """Return the volume-at-price profile of a ticker over the last ``days`` sessions."""
    normalized = normalize_egx_ticker(ticker)
    try:
        series, _cached = await get_cached_or_fresh_history(db, get_market_data_provider(), normalized)
    except UnknownTickerError as exc:
        return _unavailable(normalized, reason=str(exc))
    except MarketDataUnavailableError as exc:
        logger.warning("Volume profile could not load candles for %s: %s", normalized, exc)
        return _unavailable(normalized, reason=str(exc))

    try:
        frame = prepare_candles(pd.DataFrame(series.candles))
    except ValueError as exc:
        return _unavailable(normalized, reason=f"Unusable candle history: {exc}")

    window = max(1, min(days, len(frame)))
    profile = build_volume_profile(frame.tail(window))
    if profile is None:
        return _unavailable(normalized, reason="No priced volume in the selected window.")

    return {
        "available": True,
        "ticker": normalized,
        "poc": profile["poc"],
        "value_area_high": profile["value_area_high"],
        "value_area_low": profile["value_area_low"],
        "bins": profile["bins"],
        "above_value_pct": profile["above_value_pct"],
        "below_value_pct": profile["below_value_pct"],
        "window_days": window,
        "as_of": series.data_as_of,
        "reason": None,
    }

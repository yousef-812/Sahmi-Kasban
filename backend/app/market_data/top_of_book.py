"""Top-of-book quote (bid/ask/spread) — WP-27.

The TradingView WS subscription already streams ``bid``/``ask`` fields (single
best prices without sizes) via ``StockDataFetcher.get_realtime_price``
(``reusable_data_fetcher.py``). This module exposes them as a tiny, honestly
degraded payload: when the feed omits either side (or the socket fails) the
response reports ``available: false`` + ``reason`` instead of zeros.

A short in-memory TTL cache (per ticker) avoids opening a WS quote for every
page refresh; only successful payloads are cached.
"""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from functools import lru_cache

from app.core.config import get_settings
from app.market_data.egx_symbols import normalize_egx_ticker
from reusable_data_fetcher import StockDataFetcher

logger = logging.getLogger(__name__)

_TOP_OF_BOOK_TTL_SECONDS = 7.0
_TOP_OF_BOOK_MAX_ENTRIES = 512

_CACHE: dict[str, tuple[float, dict[str, object]]] = {}

_UNAVAILABLE_REASON = "Top-of-book bid/ask is not available from the configured feed"


@lru_cache
def _get_fetcher() -> StockDataFetcher:
    settings = get_settings()
    return StockDataFetcher(
        tv_token=settings.tradingview_auth_token,
        timeout_seconds=settings.market_data_timeout_seconds,
    )


def _as_positive_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _cache_get(ticker: str) -> dict[str, object] | None:
    entry = _CACHE.get(ticker)
    if entry is None:
        return None
    cached_at, payload = entry
    if time.monotonic() - cached_at >= _TOP_OF_BOOK_TTL_SECONDS:
        _CACHE.pop(ticker, None)
        return None
    return payload


def _cache_put(ticker: str, payload: dict[str, object]) -> None:
    if len(_CACHE) >= _TOP_OF_BOOK_MAX_ENTRIES:
        _CACHE.clear()
    _CACHE[ticker] = (time.monotonic(), payload)


def _build_payload(ticker: str, quote: dict[str, object]) -> dict[str, object]:
    bid = _as_positive_float(quote.get("bid"))
    ask = _as_positive_float(quote.get("ask"))
    source = str(quote.get("source") or "") or None
    if bid is None or ask is None:
        return {
            "available": False,
            "ticker": ticker,
            "bid": None,
            "ask": None,
            "mid_price": None,
            "spread": None,
            "spread_bp": None,
            "as_of": None,
            "source": source,
            "reason": _UNAVAILABLE_REASON,
        }
    mid = round((bid + ask) / 2, 6)
    spread = round(ask - bid, 6)
    return {
        "available": True,
        "ticker": ticker,
        "bid": round(bid, 6),
        "ask": round(ask, 6),
        "mid_price": mid,
        "spread": spread,
        "spread_bp": round(spread / mid * 10_000, 4) if mid > 0 else None,
        "as_of": datetime.now(UTC),
        "source": source or "tradingview_realtime",
        "reason": None,
    }


async def get_top_of_book(ticker: str) -> dict[str, object]:
    """Return the best live bid/ask for a ticker (no sizes, no ladder)."""
    normalized = normalize_egx_ticker(ticker)
    cached = _cache_get(normalized)
    if cached is not None:
        return cached

    try:
        quote = await _get_fetcher().get_realtime_price(normalized)
    except Exception as exc:  # noqa: BLE001 — الـ facade يبتلع أخطاؤه، وهذه حاجز أمان
        logger.warning("Top-of-book fetch failed for %s: %s", normalized, exc)
        quote = {"source": "unavailable"}

    payload = _build_payload(normalized, quote if isinstance(quote, dict) else {})
    if payload["available"]:
        _cache_put(normalized, payload)
    return payload

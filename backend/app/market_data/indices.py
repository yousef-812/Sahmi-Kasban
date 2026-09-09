from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx

from app.core.config import get_settings
from app.market_data.quotes import MarketQuote

logger = logging.getLogger(__name__)

_INDEX_COLUMNS = [
    "name",
    "description",
    "close",
    "open",
    "high",
    "low",
    "change",
    "change_abs",
    "volume",
]

_IDX_NAME = 0
_IDX_DESCRIPTION = 1
_IDX_CLOSE = 2
_IDX_OPEN = 3
_IDX_HIGH = 4
_IDX_LOW = 5
_IDX_CHANGE = 6
_IDX_CHANGE_ABS = 7
_IDX_VOLUME = 8


@dataclass(frozen=True)
class MarketIndexInfo:
    """Static registry entry describing a supported Egyptian market index."""

    ticker: str
    tradingview_symbol: str
    arabic_name: str


# The three headline Egyptian market indices. TradingView ticker strings
# verified against their symbol pages (EGX:EGX30, EGX:EGX70EWI, EGX:EGX100EWI).
SUPPORTED_INDICES: tuple[MarketIndexInfo, ...] = (
    MarketIndexInfo("EGX30", "EGX:EGX30", "مؤشر EGX30"),
    MarketIndexInfo("EGX70", "EGX:EGX70EWI", "مؤشر EGX70 EWI"),
    MarketIndexInfo("EGX100", "EGX:EGX100EWI", "مؤشر EGX100 EWI"),
)

INDEX_BY_TICKER: dict[str, MarketIndexInfo] = {info.ticker: info for info in SUPPORTED_INDICES}
INDEX_BY_TV_SYMBOL: dict[str, MarketIndexInfo] = {info.tradingview_symbol: info for info in SUPPORTED_INDICES}


def list_index_info() -> list[MarketIndexInfo]:
    return list(SUPPORTED_INDICES)


def index_exists(ticker: str) -> bool:
    return ticker.strip().upper() in INDEX_BY_TICKER


def get_index_info(ticker: str) -> MarketIndexInfo | None:
    return INDEX_BY_TICKER.get(ticker.strip().upper())


def resolve_index_tradingview_symbol(ticker: str) -> str | None:
    """Return the canonical TradingView provider symbol for a supported index.

    ``EGX70``/``EGX100`` map to the EWI tickers (``EGX:EGX70EWI`` etc.);
    matches the symbol strings used by TradingView's quote/history feed.
    """
    normalized = ticker.strip().upper()
    info = INDEX_BY_TICKER.get(normalized)
    if info is None:
        return None
    return info.tradingview_symbol


_market_indices_cache_lock = asyncio.Lock()
_market_indices_cache_at: datetime | None = None
_market_indices_cache: tuple[MarketQuote, ...] | None = None


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_scanner_rows(payload: object) -> list[MarketQuote]:
    if not isinstance(payload, dict):
        return []
    raw_rows = payload.get("data")
    if not isinstance(raw_rows, list):
        return []
    quotes: list[MarketQuote] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            continue
        provider_symbol = raw_row.get("s")
        values = raw_row.get("d")
        if not isinstance(provider_symbol, str) or ":" not in provider_symbol:
            continue
        ticker = provider_symbol.split(":", 1)[1].strip().upper()
        info = INDEX_BY_TV_SYMBOL.get(provider_symbol) or INDEX_BY_TICKER.get(ticker)
        if info is None:
            continue
        values = values if isinstance(values, list) else []

        def column(index: int, _values: list = values) -> object:
            return _values[index] if index < len(_values) else None

        close = _as_float(column(_IDX_CLOSE))
        open_price = _as_float(column(_IDX_OPEN))
        high = _as_float(column(_IDX_HIGH))
        low = _as_float(column(_IDX_LOW))
        change_percent = _as_float(column(_IDX_CHANGE))
        change_abs = _as_float(column(_IDX_CHANGE_ABS))
        volume = _as_float(column(_IDX_VOLUME))
        description = column(_IDX_DESCRIPTION)
        if not isinstance(description, str) or not description.strip():
            description = column(_IDX_NAME)
        if not isinstance(description, str) or not description.strip():
            description = info.arabic_name

        previous_close = None
        if close is not None and change_abs is not None:
            previous_close = round(close - change_abs, 4)

        quotes.append(
            MarketQuote(
                ticker=info.ticker,
                description=str(description)[:255],
                exchange="EGX",
                sector=None,
                current_price=close,
                open_price=open_price,
                previous_close=previous_close,
                session_high=high,
                session_low=low,
                change=change_abs,
                change_percent=change_percent,
                volume=volume,
                week52_high=None,
                week52_low=None,
                market_open=False,
                session_change_percent=None,
                session_date=None,
                next_session_open=None,
            )
        )
    return quotes


async def _fetch_scanner_index_rows() -> list[MarketQuote]:
    settings = get_settings()
    tickers = [info.tradingview_symbol for info in SUPPORTED_INDICES]
    payload = {
        "symbols": {"tickers": tickers},
        "columns": _INDEX_COLUMNS,
    }
    headers = {
        "Origin": settings.tradingview_origin,
        "Referer": f"{settings.tradingview_origin}/",
        "User-Agent": settings.tradingview_user_agent,
    }
    timeout = httpx.Timeout(settings.market_data_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.post(settings.tradingview_scanner_url, json=payload)
        response.raise_for_status()
        rows = _parse_scanner_rows(response.json())
    return rows


async def fetch_market_indices(
    *,
    force_refresh: bool = False,
    cache_seconds: int = 30,
) -> tuple[MarketQuote, ...]:
    """Return live quotes for the supported Egyptian market indices.

    Cached in-memory for a short TTL to avoid hammering the TradingView scanner.
    Returns only indices that were successfully quoted from live trading data;
    empty when TradingView is unavailable.
    """
    global _market_indices_cache_at, _market_indices_cache

    now = datetime.now(UTC)
    if (
        not force_refresh
        and _market_indices_cache is not None
        and _market_indices_cache_at is not None
        and now - _market_indices_cache_at < timedelta(seconds=cache_seconds)
    ):
        return _market_indices_cache

    async with _market_indices_cache_lock:
        now = datetime.now(UTC)
        if (
            not force_refresh
            and _market_indices_cache is not None
            and _market_indices_cache_at is not None
            and now - _market_indices_cache_at < timedelta(seconds=cache_seconds)
        ):
            return _market_indices_cache

        try:
            rows = await _fetch_scanner_index_rows()
        except Exception as exc:
            logger.warning("TradingView index scanner failed: %s", exc)
            return tuple(_market_indices_cache or ())
        _market_indices_cache_at = now
        _market_indices_cache = tuple(rows)
        return _market_indices_cache


async def fetch_index_quote(ticker: str, *, force_refresh: bool = False) -> MarketQuote | None:
    info = get_index_info(ticker)
    if info is None:
        return None
    quotes = await fetch_market_indices(force_refresh=force_refresh)
    return next((quote for quote in quotes if quote.ticker == info.ticker), None)

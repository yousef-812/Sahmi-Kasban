"""Global/macro market context (world indices, FX, metals/energy) — WP-20.

Source reality check (per ``docs/MARKET_DATA_STRATEGY.md``):

- The unified ``MarketDataProvider`` protocol exposes only ``get_history``
  candles (``app/market_data/types.py``); it carries no macro/FX/commodity feed.
- The repo's live snapshot source is the TradingView **scanner** HTTP endpoint:
  ``app/market_data/quotes.py:640`` and ``app/market_data/indices.py:163`` POST to
  ``settings.tradingview_scanner_url`` (``app/core/config.py:74`` →
  ``https://scanner.tradingview.com/egypt/scan``) with ``symbols.tickers`` +
  ``columns`` and Origin/User-Agent headers, parsing ``{"data": [{"s", "d"}]}``.
- The identical contract serves non-EGX symbols when the market path segment of
  the configured URL is swapped: ``/global/scan`` (world indices), ``/forex/scan``
  (FX) and ``/futures/scan`` (metals/energy) were verified to return rows for the
  registry below; ``/egypt/scan`` returns ``{"totalCount": 0}`` for them. Only the
  URL's market segment changes — host, headers, payload and response shape are
  the ones this repo already uses.

Field mapping (scanner columns requested: ``close, change, currency``):

- ``s`` (provider symbol)  -> matched against ``GlobalSymbol.symbol``; unknown
  symbols in the response are dropped, so ``d`` index positions stay aligned.
- ``d[0]`` ``close``       -> ``value``
- ``d[1]`` ``change`` (%)  -> ``change_pct`` (percent, same as ``quotes.py:516``)
- ``d[2]`` ``currency``    -> ``currency`` (null for many indices)
``name``/``name_ar``/``kind`` come from the local registry — static labels, not
market data. MSCI has no true index symbol in the scanner (only the AMEX:URTH
MSCI World ETF), so it is deliberately absent from the registry.

Degradation rules: scanner failures become an explicit ``available: false``
response with empty lists and an ``error`` message — this module never raises to
the router, never writes to the database and never fabricates numbers.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse, urlunparse

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SOURCE = "tradingview_scanner"
GLOBAL_MARKET_CACHE_TTL = timedelta(minutes=60)
FAILURE_CACHE_TTL = timedelta(minutes=5)

_COLUMNS = ["close", "change", "currency"]
_IDX_VALUE = 0
_IDX_CHANGE_PCT = 1
_IDX_CURRENCY = 2


@dataclass(frozen=True, slots=True)
class GlobalSymbol:
    """Registry entry: a scanner market path plus display metadata for one symbol."""

    market: str
    symbol: str
    name: str
    name_ar: str
    kind: str


GLOBAL_SYMBOLS: tuple[GlobalSymbol, ...] = (
    GlobalSymbol("global", "SP:SPX", "S&P 500", "مؤشر S&P 500", "index"),
    GlobalSymbol("global", "NASDAQ:IXIC", "Nasdaq Composite", "مؤشر ناسداك المركب", "index"),
    GlobalSymbol("global", "DJ:DJI", "Dow Jones Industrial", "مؤشر داو جونز الصناعي", "index"),
    GlobalSymbol("global", "FTSE:UKX", "FTSE 100", "مؤشر فوتسِي 100", "index"),
    GlobalSymbol("global", "XETR:DAX", "DAX", "مؤشر داكس الألماني", "index"),
    GlobalSymbol("global", "TVC:NI225", "Nikkei 225", "مؤشر نيكاي 225", "index"),
    GlobalSymbol("global", "TADAWUL:TASI", "TASI", "مؤشر تداول العام", "index"),
    GlobalSymbol("forex", "FX_IDC:USDEGP", "USD/EGP", "دولار / جنيه مصري", "fx"),
    GlobalSymbol("forex", "FX:EURUSD", "EUR/USD", "يورو / دولار", "fx"),
    GlobalSymbol("forex", "FX:GBPUSD", "GBP/USD", "استرليني / دولار", "fx"),
    GlobalSymbol("forex", "FX:USDJPY", "USD/JPY", "دولار / ين ياباني", "fx"),
    GlobalSymbol("futures", "COMEX:GC1!", "Gold", "الذهب (عقد مستمر)", "metal"),
    GlobalSymbol("futures", "COMEX:SI1!", "Silver", "الفضة (عقد مستمر)", "metal"),
    GlobalSymbol("futures", "ICEEUR:BRN1!", "Brent Crude", "نفط برنت", "energy"),
    GlobalSymbol("futures", "NYMEX:CL1!", "WTI Crude", "نفط غرب تكساس", "energy"),
    GlobalSymbol("futures", "NYMEX:NG1!", "Natural Gas", "الغاز الطبيعي", "energy"),
)

_cache_lock = asyncio.Lock()
_cache: dict[str, object] | None = None
_cache_at: datetime | None = None
_cache_ttl: timedelta = GLOBAL_MARKET_CACHE_TTL


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def _scanner_url(market: str) -> str:
    parsed = urlparse(get_settings().tradingview_scanner_url)
    return urlunparse(parsed._replace(path=f"/{market}/scan"))


async def _fetch_scanner_payload(market: str, tickers: list[str]) -> object:
    settings = get_settings()
    payload = {"symbols": {"tickers": tickers}, "columns": _COLUMNS}
    headers = {
        "Origin": settings.tradingview_origin,
        "Referer": f"{settings.tradingview_origin}/",
        "User-Agent": settings.tradingview_user_agent,
    }
    timeout = httpx.Timeout(settings.market_data_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.post(_scanner_url(market), json=payload)
        response.raise_for_status()
        return response.json()


def _parse_payload(symbols: tuple[GlobalSymbol, ...], payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        return []
    raw_rows = payload.get("data")
    if not isinstance(raw_rows, list):
        return []
    by_symbol = {info.symbol: info for info in symbols}
    items: list[dict[str, object]] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            continue
        provider_symbol = raw_row.get("s")
        info = by_symbol.get(provider_symbol) if isinstance(provider_symbol, str) else None
        if info is None:
            continue
        values = raw_row.get("d")
        values = values if isinstance(values, list) else []
        value = _as_float(values[_IDX_VALUE]) if len(values) > _IDX_VALUE else None
        if value is None or value <= 0:
            continue
        change_pct = _as_float(values[_IDX_CHANGE_PCT]) if len(values) > _IDX_CHANGE_PCT else None
        raw_currency = values[_IDX_CURRENCY] if len(values) > _IDX_CURRENCY else None
        currency = raw_currency.strip() if isinstance(raw_currency, str) and raw_currency.strip() else None
        items.append(
            {
                "symbol": info.symbol,
                "name": info.name,
                "name_ar": info.name_ar,
                "value": value,
                "change_pct": change_pct,
                "currency": currency,
                "kind": info.kind,
            }
        )
    return items


async def _fetch_market(
    market: str, symbols: tuple[GlobalSymbol, ...]
) -> tuple[list[dict[str, object]], str | None]:
    try:
        payload = await _fetch_scanner_payload(market, [info.symbol for info in symbols])
    except Exception as exc:
        logger.warning("Global market scanner failed for %s: %s", market, exc)
        return [], f"{market}: {type(exc).__name__}"
    return _parse_payload(symbols, payload), None


async def _fetch_snapshot() -> dict[str, object]:
    groups: dict[str, tuple[GlobalSymbol, ...]] = {}
    for info in GLOBAL_SYMBOLS:
        groups.setdefault(info.market, []).append(info)
    results = await asyncio.gather(
        *(_fetch_market(market, tuple(symbol_group)) for market, symbol_group in groups.items())
    )
    errors = [error for _, error in results if error]
    items = [item for market_items, _ in results for item in market_items]
    indices = [item for item in items if item["kind"] == "index"]
    fx = [item for item in items if item["kind"] == "fx"]
    commodities = [item for item in items if item["kind"] in ("metal", "energy")]
    available = bool(indices or fx or commodities)
    error: str | None = None
    if not available:
        error = (
            f"{SOURCE} unavailable: {'; '.join(errors)}"
            if errors
            else f"{SOURCE} returned no rows for the configured global symbols"
        )
    elif errors:
        logger.warning("Global market snapshot is partial; failed markets: %s", "; ".join(errors))
    return {
        "available": available,
        "source": SOURCE,
        "as_of": datetime.now(UTC) if available else None,
        "indices": indices,
        "fx": fx,
        "commodities": commodities,
        "error": error,
    }


async def get_global_market(db: Session, *, force_refresh: bool = False) -> dict[str, object]:
    """Return the cached global/macro snapshot (indices, FX, metals/energy).

    ``db`` is accepted for service-layer symmetry with the other market-data
    functions but is never used: the snapshot lives in an in-module TTL cache
    (60 minutes for successful fetches, 5 minutes after a failed fetch) and no
    database row is written. ``force_refresh`` bypasses the cache.
    """
    del db
    global _cache, _cache_at, _cache_ttl

    now = datetime.now(UTC)
    if (
        not force_refresh
        and _cache is not None
        and _cache_at is not None
        and now - _cache_at < _cache_ttl
    ):
        return _cache

    async with _cache_lock:
        now = datetime.now(UTC)
        if (
            not force_refresh
            and _cache is not None
            and _cache_at is not None
            and now - _cache_at < _cache_ttl
        ):
            return _cache
        snapshot = await _fetch_snapshot()
        _cache = snapshot
        _cache_at = now
        _cache_ttl = GLOBAL_MARKET_CACHE_TTL if snapshot["available"] else FAILURE_CACHE_TTL
        return snapshot

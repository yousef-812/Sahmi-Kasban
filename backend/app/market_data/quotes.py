from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, time as datetime_time, timedelta
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.egx_symbols import EGX_ARABIC_NAMES, _TICKER_PATTERN, normalize_egx_ticker
from app.models import MarketDataSnapshot, MarketInstrumentCatalog

logger = logging.getLogger(__name__)

_CAIRO = ZoneInfo("Africa/Cairo")

_QUOTE_COLUMNS = [
    "name",
    "description",
    "close",
    "open",
    "high",
    "low",
    "change",
    "change_abs",
    "volume",
    "sector",
]

# Column indexes inside the TradingView scanner row payload (list in _QUOTE_COLUMNS order).
_IDX_NAME = 0
_IDX_DESCRIPTION = 1
_IDX_CLOSE = 2
_IDX_OPEN = 3
_IDX_HIGH = 4
_IDX_LOW = 5
_IDX_CHANGE = 6
_IDX_CHANGE_ABS = 7
_IDX_VOLUME = 8
_IDX_SECTOR = 9

_quotes_cache_lock = asyncio.Lock()
_quotes_cache_at: datetime | None = None
_quotes_cache: "MarketQuotesSnapshot | None" = None


@dataclass(frozen=True)
class MarketQuote:
    ticker: str
    description: str
    exchange: str
    sector: str | None
    current_price: float | None
    open_price: float | None
    previous_close: float | None
    session_high: float | None
    session_low: float | None
    change: float | None
    change_percent: float | None
    volume: float | None
    week52_high: float | None
    week52_low: float | None
    market_open: bool
    session_change_percent: float | None
    session_date: str | None
    next_session_open: datetime | None

    def to_dict(self) -> dict[str, object]:
        return {
            "ticker": self.ticker,
            "description": self.description,
            "exchange": self.exchange,
            "sector": self.sector,
            "current_price": self.current_price,
            "open_price": self.open_price,
            "previous_close": self.previous_close,
            "session_high": self.session_high,
            "session_low": self.session_low,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "week52_high": self.week52_high,
            "week52_low": self.week52_low,
            "market_open": self.market_open,
            "session_change_percent": self.session_change_percent,
            "session_date": self.session_date,
            "next_session_open": self.next_session_open,
        }


@dataclass(frozen=True)
class MarketQuotesSnapshot:
    source: str
    generated_at: datetime
    market_open: bool
    next_session_open: datetime | None
    items: tuple[MarketQuote, ...]


@dataclass(frozen=True)
class _SessionState:
    market_open: bool
    session_date: date | None
    next_session_open: datetime | None
    reset_change_percent: bool


def _session_state(now_utc: datetime) -> _SessionState:
    settings = get_settings()
    now = now_utc.astimezone(_CAIRO)
    open_time = datetime_time.fromisoformat(settings.egx_session_open_time)
    close_time = datetime_time.fromisoformat(settings.egx_session_close_time)
    reset_minutes = timedelta(minutes=settings.egx_session_reset_before_minutes)

    # Cairo weekday(): Sun=6, Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5.
    is_market_day = now.weekday() in {6, 0, 1, 2, 3}
    in_hours = open_time <= now.time() < close_time
    market_open = is_market_day and in_hours

    if is_market_day and now.time() < open_time:
        next_open = now.replace(
            hour=open_time.hour,
            minute=open_time.minute,
            second=0,
            microsecond=0,
        )
    else:
        days_ahead = 1
        while (now + timedelta(days=days_ahead)).weekday() not in {6, 0, 1, 2, 3}:
            days_ahead += 1
        next_day = now + timedelta(days=days_ahead)
        next_open = next_day.replace(
            hour=open_time.hour,
            minute=open_time.minute,
            second=0,
            microsecond=0,
        )

    reset_change_percent = market_open and next_open - now <= reset_minutes
    session_date = now.date() if is_market_day else None
    return _SessionState(
        market_open=market_open,
        session_date=session_date,
        next_session_open=next_open,
        reset_change_percent=reset_change_percent,
    )


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_scanner_quotes(payload: object) -> dict[str, MarketQuote]:
    if not isinstance(payload, dict):
        return {}
    raw_rows = payload.get("data")
    if not isinstance(raw_rows, list):
        return {}
    quotes: dict[str, MarketQuote] = {}
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            continue
        provider_symbol = raw_row.get("s")
        values = raw_row.get("d")
        if not isinstance(provider_symbol, str) or ":" not in provider_symbol:
            continue
        exchange, ticker = provider_symbol.split(":", 1)
        if exchange.strip().upper() != "EGX" or not _TICKER_PATTERN.fullmatch(
            ticker.strip().upper()
        ):
            continue
        ticker = ticker.strip().upper()
        values = values if isinstance(values, list) else []

        def column(index: int) -> object:
            return values[index] if index < len(values) else None

        name = column(_IDX_NAME)
        description = column(_IDX_DESCRIPTION)
        close = _as_float(column(_IDX_CLOSE))
        open_price = _as_float(column(_IDX_OPEN))
        high = _as_float(column(_IDX_HIGH))
        low = _as_float(column(_IDX_LOW))
        change_percent = _as_float(column(_IDX_CHANGE))
        change_abs = _as_float(column(_IDX_CHANGE_ABS))
        volume = _as_float(column(_IDX_VOLUME))
        sector = column(_IDX_SECTOR)
        sector_text = str(sector).strip() if sector not in (None, "") else None

        previous_close = None
        if close is not None and change_abs is not None:
            previous_close = round(close - change_abs, 4)

        fallback_description = ""
        if isinstance(description, str) and description.strip():
            fallback_description = description.strip()[:255]
        elif isinstance(name, str) and name.strip():
            fallback_description = name.strip()[:255]

        quotes[ticker] = MarketQuote(
            ticker=ticker,
            description=fallback_description,
            exchange="EGX",
            sector=sector_text,
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
    return quotes


def _cached_daily_bounds(db: Session) -> dict[str, tuple[float | None, float | None]]:
    cutoff = datetime.now(UTC) - timedelta(days=366)
    rows = db.scalars(
        select(MarketDataSnapshot).where(MarketDataSnapshot.interval == "1d")
    ).all()
    bounds: dict[str, tuple[float | None, float | None]] = {}
    for row in rows:
        candles = row.payload.get("candles", [])
        if not isinstance(candles, list):
            continue
        high = None
        low = None
        for candle in candles:
            if not isinstance(candle, dict):
                continue
            timestamp = candle.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    candle_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if _as_utc(candle_at) < cutoff:
                    continue
            candle_high = _as_float(candle.get("high"))
            candle_low = _as_float(candle.get("low"))
            if candle_high is not None:
                high = candle_high if high is None else max(high, candle_high)
            if candle_low is not None:
                low = candle_low if low is None else min(low, candle_low)
        if high is not None or low is not None:
            bounds[row.ticker] = (high, low)
    return bounds


def _merge_with_catalog(
    db: Session,
    quotes: dict[str, MarketQuote],
    *,
    market_open: bool,
    session_date: date | None,
    next_session_open: datetime | None,
    reset_change_percent: bool,
    daily_bounds: dict[str, tuple[float | None, float | None]],
) -> tuple[MarketQuote, ...]:
    catalog_rows = {
        row.ticker: row
        for row in db.scalars(
            select(MarketInstrumentCatalog).where(
                MarketInstrumentCatalog.active.is_(True)
            )
        ).all()
    }
    items: list[MarketQuote] = []
    for ticker, quote in quotes.items():
        row = catalog_rows.get(ticker)
        description = quote.description
        if row is not None and row.description.strip():
            description = row.description.strip()
        curated = EGX_ARABIC_NAMES.get(ticker)
        if curated:
            description = curated
        high52, low52 = daily_bounds.get(ticker, (None, None))
        session_change = None
        if not reset_change_percent:
            session_change = quote.change_percent
        items.append(
            MarketQuote(
                ticker=quote.ticker,
                description=description,
                exchange=quote.exchange,
                sector=quote.sector,
                current_price=quote.current_price,
                open_price=quote.open_price,
                previous_close=quote.previous_close,
                session_high=quote.session_high,
                session_low=quote.session_low,
                change=quote.change,
                change_percent=quote.change_percent,
                volume=quote.volume,
                week52_high=high52,
                week52_low=low52,
                market_open=market_open,
                session_change_percent=session_change,
                session_date=session_date.isoformat() if session_date else None,
                next_session_open=next_session_open,
            )
        )
    items.sort(key=lambda item: (item.ticker,))
    return tuple(items)


async def _fetch_scanner_rows() -> dict[str, MarketQuote]:
    settings = get_settings()
    payload = {
        "filter": [{"left": "type", "operation": "equal", "right": "stock"}],
        "options": {"lang": "ar"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": _QUOTE_COLUMNS,
        "sort": {"sortBy": "volume", "sortOrder": "desc"},
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
        return _parse_scanner_quotes(response.json())


async def fetch_market_quotes(db: Session, *, force_refresh: bool = False) -> MarketQuotesSnapshot:
    global _quotes_cache_at, _quotes_cache

    settings = get_settings()
    now = datetime.now(UTC)
    if not force_refresh and _quotes_cache is not None and _quotes_cache_at is not None:
        if now - _quotes_cache_at < timedelta(seconds=settings.market_quotes_refresh_seconds):
            return _quotes_cache

    async with _quotes_cache_lock:
        now = datetime.now(UTC)
        if (
            not force_refresh
            and _quotes_cache is not None
            and _quotes_cache_at is not None
            and now - _quotes_cache_at
            < timedelta(seconds=settings.market_quotes_refresh_seconds)
        ):
            return _quotes_cache

        quotes = await _fetch_scanner_rows()
        session = _session_state(now)
        daily_bounds = _cached_daily_bounds(db)
        items = _merge_with_catalog(
            db,
            quotes,
            market_open=session.market_open,
            session_date=session.session_date,
            next_session_open=session.next_session_open,
            reset_change_percent=session.reset_change_percent,
            daily_bounds=daily_bounds,
        )
        snapshot = MarketQuotesSnapshot(
            source="tradingview_scanner",
            generated_at=now,
            market_open=session.market_open,
            next_session_open=session.next_session_open,
            items=items,
        )
        _quotes_cache_at = now
        _quotes_cache = snapshot
        logger.info("Fetched %s EGX market quotes from TradingView", len(items))
        return snapshot


def _sorted_daily_candles(series: object) -> list[dict[str, object]]:
    candles: list[tuple[datetime, dict[str, object]]] = []
    for candle in getattr(series, "candles", ()):
        if not isinstance(candle, dict):
            continue
        timestamp = candle.get("timestamp")
        if isinstance(timestamp, str):
            try:
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                continue
        elif isinstance(timestamp, datetime):
            parsed = timestamp
        else:
            continue
        parsed = _as_utc(parsed)
        if all(
            _as_float(candle.get(key)) is not None
            for key in ("open", "high", "low", "close")
        ):
            candles.append((parsed, candle))
    candles.sort(key=lambda item: item[0])
    return [candle for _, candle in candles]


async def fetch_single_quote(db: Session, ticker: str, *, force_refresh: bool = False) -> MarketQuote | None:
    normalized = normalize_egx_ticker(ticker)
    snapshot = await fetch_market_quotes(db, force_refresh=False)
    quote = next(
        (item for item in snapshot.items if item.ticker == normalized),
        None,
    )
    if quote is None:
        return None
    if quote.week52_high is not None and quote.week52_low is not None and not force_refresh:
        return quote

    from app.market_data.cache import get_cached_or_fresh_history
    from app.market_data.provider import get_market_data_provider

    settings = get_settings()
    provider = get_market_data_provider()
    try:
        series, _cached = await get_cached_or_fresh_history(
            db,
            provider,
            normalized,
            period="1y",
            interval="1d",
            cache_minutes=settings.market_data_cache_minutes,
            min_candles=60,
        )
    except Exception:
        logger.warning("Could not load 1y history for %s while building its quote", normalized)
        return quote

    high = None
    low = None
    for candle in _sorted_daily_candles(series):
        candle_high = _as_float(candle.get("high"))
        candle_low = _as_float(candle.get("low"))
        if candle_high is not None:
            high = candle_high if high is None else max(high, candle_high)
        if candle_low is not None:
            low = candle_low if low is None else min(low, candle_low)

    open_price = quote.open_price
    previous_close = quote.previous_close
    session_high = quote.session_high
    session_low = quote.session_low
    change = quote.change
    change_percent = quote.change_percent

    daily = _sorted_daily_candles(series)
    if not quote.market_open and daily:
        last = daily[-1]
        candle_open = _as_float(last.get("open"))
        candle_high = _as_float(last.get("high"))
        candle_low = _as_float(last.get("low"))
        if candle_open is not None:
            open_price = candle_open
        if candle_high is not None:
            session_high = candle_high
        if candle_low is not None:
            session_low = candle_low
        if len(daily) >= 2:
            prev_close = _as_float(daily[-2].get("close"))
            if prev_close is not None:
                previous_close = prev_close
        if quote.current_price is not None and previous_close not in (None, 0):
            change = round(quote.current_price - previous_close, 4)
            change_percent = round(
                (quote.current_price / previous_close - 1) * 100,
                2,
            )

    return MarketQuote(
        ticker=quote.ticker,
        description=quote.description,
        exchange=quote.exchange,
        sector=quote.sector,
        current_price=quote.current_price,
        open_price=open_price,
        previous_close=previous_close,
        session_high=session_high,
        session_low=session_low,
        change=change,
        change_percent=change_percent,
        volume=quote.volume,
        week52_high=high,
        week52_low=low,
        market_open=quote.market_open,
        session_change_percent=quote.session_change_percent,
        session_date=quote.session_date,
        next_session_open=quote.next_session_open,
    )

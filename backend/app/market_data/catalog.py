from __future__ import annotations

import asyncio
import logging
import re
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.config import Environment, get_settings
from app.market_data.egx_symbols import (
    EGX_ARABIC_NAMES,
    EGX_SEED_SYMBOLS,
    EGX_SYMBOL_SET,
)
from app.market_data.types import MarketInstrument
from app.models import MarketInstrumentCatalog

logger = logging.getLogger(__name__)

_TICKER_PATTERN = re.compile(r"^[A-Z0-9]{1,24}$")
_SCANNER_MIN_AUTHORITATIVE_SYMBOLS = 100
_refresh_lock = asyncio.Lock()
_last_refresh_attempt_at: datetime | None = None


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def seed_market_instrument_catalog(db: Session) -> None:
    now = _utcnow()
    existing_map = {
        item.ticker: item
        for item in db.scalars(
            select(MarketInstrumentCatalog).where(MarketInstrumentCatalog.ticker.in_(EGX_SEED_SYMBOLS))
        ).all()
    }
    changed = False
    for ticker in EGX_SEED_SYMBOLS:
        existing = existing_map.get(ticker)
        if existing is None:
            db.add(
                MarketInstrumentCatalog(
                    ticker=ticker,
                    provider_symbol=f"EGX:{ticker}",
                    exchange="EGX",
                    description=EGX_ARABIC_NAMES.get(ticker, ""),
                    source="legacy_seed",
                    active=True,
                    last_seen_at=now,
                )
            )
            changed = True
        elif not existing.active:
            existing.active = True
            existing.last_seen_at = now
            changed = True
    if changed:
        db.commit()


def _parse_scanner_rows(payload: object) -> list[MarketInstrumentCatalog]:
    if not isinstance(payload, dict):
        return []
    raw_rows = payload.get("data")
    if not isinstance(raw_rows, list):
        return []

    now = _utcnow()
    parsed: dict[str, MarketInstrumentCatalog] = {}
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            continue
        provider_symbol = raw_row.get("s")
        values = raw_row.get("d")
        if not isinstance(provider_symbol, str) or ":" not in provider_symbol:
            continue
        exchange, ticker = provider_symbol.split(":", 1)
        exchange = exchange.strip().upper()
        ticker = ticker.strip().upper()
        if exchange != "EGX" or not _TICKER_PATTERN.fullmatch(ticker):
            continue
        values = values if isinstance(values, list) else []
        description = ""
        if len(values) > 1 and isinstance(values[1], str):
            description = values[1].strip()[:255]
        if not description and len(values) > 0 and isinstance(values[0], str):
            description = values[0].strip()[:255]
        parsed[ticker] = MarketInstrumentCatalog(
            ticker=ticker,
            provider_symbol=f"EGX:{ticker}",
            exchange="EGX",
            description=description,
            source="tradingview_scanner",
            active=True,
            last_seen_at=now,
        )
    return list(parsed.values())


def _preferred_description(
    existing: str,
    incoming: str,
    *,
    ticker: str,
) -> str:
    """Prefer Arabic descriptions, keeping curated blue-chip names authoritative."""
    curated = EGX_ARABIC_NAMES.get(ticker, "")
    if curated:
        return curated[:255]
    if incoming.strip():
        return incoming.strip()[:255]
    return existing[:255]


def _reconcile_scanner_rows(
    db: Session,
    rows: list[MarketInstrumentCatalog],
    *,
    authoritative: bool,
) -> tuple[int, int]:
    now = _utcnow()
    seen = {row.ticker for row in rows}
    existing_rows = {item.ticker: item for item in db.scalars(select(MarketInstrumentCatalog)).all()}
    for row in rows:
        existing = existing_rows.get(row.ticker)
        if existing is None:
            db.add(row)
            continue
        existing.provider_symbol = row.provider_symbol
        existing.exchange = row.exchange
        existing.description = _preferred_description(
            existing.description,
            row.description,
            ticker=row.ticker,
        )
        existing.source = row.source
        existing.active = True
        existing.last_seen_at = now

    deactivated = 0
    if authoritative:
        for existing in existing_rows.values():
            if (
                existing.exchange == "EGX"
                and existing.ticker not in seen
                and existing.ticker not in EGX_SYMBOL_SET
                and existing.active
            ):
                existing.active = False
                deactivated += 1
    return len(rows), deactivated


def _deactivate_unseen_legacy_seed_rows(db: Session) -> int:
    scanner_count = int(
        db.scalar(
            select(func.count())
            .select_from(MarketInstrumentCatalog)
            .where(
                MarketInstrumentCatalog.source == "tradingview_scanner",
                MarketInstrumentCatalog.active.is_(True),
            )
        )
        or 0
    )
    if scanner_count < _SCANNER_MIN_AUTHORITATIVE_SYMBOLS:
        return 0

    stale = list(
        db.scalars(
            select(MarketInstrumentCatalog).where(
                MarketInstrumentCatalog.source == "legacy_seed",
                MarketInstrumentCatalog.active.is_(True),
            )
        ).all()
    )
    stale = [row for row in stale if row.ticker not in EGX_SYMBOL_SET]
    for row in stale:
        row.active = False
    if stale:
        db.commit()
        logger.info(
            "Deactivated %s legacy seed symbols after authoritative scanner coverage",
            len(stale),
        )
    return len(stale)


async def refresh_market_instrument_catalog(db: Session) -> int:
    settings = get_settings()
    payload = {
        "filter": [{"left": "type", "operation": "equal", "right": "stock"}],
        "options": {"lang": "ar"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name", "description", "exchange", "type", "subtype"],
        "sort": {"sortBy": "name", "sortOrder": "asc"},
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
        rows = _parse_scanner_rows(response.json())

    if len(rows) < _SCANNER_MIN_AUTHORITATIVE_SYMBOLS:
        raise RuntimeError("TradingView scanner returned too few EGX stocks for authoritative reconciliation")

    count, deactivated = _reconcile_scanner_rows(db, rows, authoritative=True)
    db.commit()
    logger.info(
        "Refreshed %s EGX instruments from TradingView and deactivated %s stale symbols",
        count,
        deactivated,
    )
    return count


async def ensure_market_instrument_catalog(db: Session) -> str:
    global _last_refresh_attempt_at

    seed_market_instrument_catalog(db)
    settings = get_settings()
    if settings.app_env is Environment.TEST:
        return "legacy_seed_registry"

    _deactivate_unseen_legacy_seed_rows(db)
    latest_seen = _as_utc(
        db.scalar(
            select(func.max(MarketInstrumentCatalog.last_seen_at)).where(
                MarketInstrumentCatalog.source == "tradingview_scanner"
            )
        )
    )
    refresh_after = timedelta(hours=settings.market_instrument_catalog_refresh_hours)
    now = _utcnow()
    catalog_stale = latest_seen is None or latest_seen < now - refresh_after
    retry_after = timedelta(minutes=settings.market_instrument_catalog_retry_minutes)
    recently_attempted = _last_refresh_attempt_at is not None and _last_refresh_attempt_at > now - retry_after
    current_source = "tradingview_scanner" if latest_seen is not None else "legacy_seed_registry"
    if not catalog_stale or recently_attempted or _refresh_lock.locked():
        return current_source

    async with _refresh_lock:
        now = _utcnow()
        recently_attempted = (
            _last_refresh_attempt_at is not None and _last_refresh_attempt_at > now - retry_after
        )
        if recently_attempted:
            return current_source
        _last_refresh_attempt_at = now
        try:
            await refresh_market_instrument_catalog(db)
            return "tradingview_scanner"
        except Exception:
            db.rollback()
            logger.exception("Could not refresh the TradingView EGX instrument catalog")
            return current_source


async def search_market_instruments(
    db: Session,
    *,
    query: str,
    limit: int,
) -> tuple[str, int, list[MarketInstrument]]:
    source = await ensure_market_instrument_catalog(db)
    normalized_query = query.strip().upper()
    statement = select(MarketInstrumentCatalog).where(MarketInstrumentCatalog.active.is_(True))
    if normalized_query:
        pattern = f"%{normalized_query}%"
        statement = statement.where(
            or_(
                func.upper(MarketInstrumentCatalog.ticker).like(pattern),
                func.upper(MarketInstrumentCatalog.description).like(pattern),
            )
        ).order_by(
            case(
                (func.upper(MarketInstrumentCatalog.ticker) == normalized_query, 0),
                (
                    func.upper(MarketInstrumentCatalog.ticker).like(f"{normalized_query}%"),
                    1,
                ),
                else_=2,
            ),
            MarketInstrumentCatalog.ticker,
        )
    else:
        statement = statement.order_by(MarketInstrumentCatalog.ticker)

    rows = db.scalars(statement.limit(limit)).all()
    total = db.scalar(
        select(func.count())
        .select_from(MarketInstrumentCatalog)
        .where(MarketInstrumentCatalog.active.is_(True))
    )
    instruments = [
        MarketInstrument(
            ticker=row.ticker,
            provider_symbol=row.provider_symbol,
            exchange=row.exchange,
            description=row.description,
        )
        for row in rows
    ]
    return source, int(total or 0), instruments


async def market_instrument_exists(db: Session, ticker: str) -> bool:
    await ensure_market_instrument_catalog(db)
    normalized = ticker.strip().upper().removesuffix(".CA").removeprefix("EGX:")
    if not _TICKER_PATTERN.fullmatch(normalized):
        return False
    return (
        db.scalar(
            select(MarketInstrumentCatalog.ticker).where(
                MarketInstrumentCatalog.ticker == normalized,
                MarketInstrumentCatalog.active.is_(True),
            )
        )
        is not None
    )

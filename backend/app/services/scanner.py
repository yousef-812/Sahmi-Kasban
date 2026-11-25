"""Scanner snapshots: refresh them from cached candles and read the newest row.

The heavy lifting lives in the ``sahmi_kasban.scanner`` package; this service only
bridges it to the market-data cache and the ``scanner_snapshots`` table. Every
symbol keeps a single row per ``kind/timeframe`` so the API can read the newest
result without touching the provider.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pandas as pd
from sahmi_kasban import AnalysisConfig
from sahmi_kasban.engines.smc import SMCEngine
from sahmi_kasban.indicators import enrich_indicators, prepare_candles
from sahmi_kasban.scanner import (
    build_technical_snapshot,
    scan_fibonacci,
    scan_harmonic,
    technical_rating,
)
from sqlalchemy import and_, delete, func, select
from sqlalchemy.orm import Session

from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.catalog import ensure_market_instrument_catalog
from app.market_data.egx_symbols import EGX_ARABIC_NAMES, EGX_SEED_SYMBOLS, normalize_egx_ticker
from app.market_data.quotes import _resolve_canonical_sector
from app.market_data.types import MarketDataProvider, UnknownTickerError
from app.market_data.universe import apply_market_health_quarantine
from app.models import MarketInstrumentCatalog, ScannerSnapshot

logger = logging.getLogger(__name__)

SUPPORTED_KINDS: tuple[str, ...] = ("technical", "fibonacci", "harmonic")
DEFAULT_TIMEFRAME = "1D"
SCORE_BUY_THRESHOLD = 60.0
SCORE_SELL_THRESHOLD = 40.0


def _validate_kind(kind: str) -> str:
    if kind not in SUPPORTED_KINDS:
        raise ValueError(f"Unsupported scanner kind: {kind!r}; expected one of {SUPPORTED_KINDS}")
    return kind


def _normalize_symbol(symbol: str) -> str | None:
    try:
        return normalize_egx_ticker(symbol)
    except UnknownTickerError:
        return None


def _score_rating(score: float | None) -> str | None:
    """Map a 0..100 scanner score onto the buy/sell/neutral vocabulary."""
    if score is None:
        return None
    if score >= SCORE_BUY_THRESHOLD:
        return "buy"
    if score <= SCORE_SELL_THRESHOLD:
        return "sell"
    return "neutral"


def _as_utc_text(value: datetime) -> str:
    moment = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
    return moment.isoformat()


async def resolve_scanner_tickers(db: Session) -> list[str]:
    """Return the default symbol universe, mirroring the daily top-ten scan."""
    await ensure_market_instrument_catalog(db)
    universe = apply_market_health_quarantine(db)
    return list(universe.tickers) or list(EGX_SEED_SYMBOLS)


async def _resolve_tickers(db: Session, tickers: list[str] | None) -> list[str]:
    if tickers is None:
        return await resolve_scanner_tickers(db)
    resolved: list[str] = []
    for raw in tickers:
        symbol = _normalize_symbol(raw)
        if symbol is not None and symbol not in resolved:
            resolved.append(symbol)
    return resolved


def _symbol_meta(db: Session, tickers: list[str]) -> dict[str, dict[str, object]]:
    if not tickers:
        return {}
    rows = db.scalars(
        select(MarketInstrumentCatalog).where(MarketInstrumentCatalog.ticker.in_(tickers))
    ).all()
    descriptions = {row.ticker: row.description for row in rows}
    return {
        ticker: {
            "nameAr": descriptions.get(ticker) or EGX_ARABIC_NAMES.get(ticker),
            "sector": _resolve_canonical_sector(ticker, None),
        }
        for ticker in tickers
    }


def _score_and_rating(kind: str, payload: dict[str, object]) -> tuple[float | None, str | None]:
    if kind == "technical":
        score = payload.get("technicalScore")
        value = float(score) if isinstance(score, (int, float)) else None
        return value, technical_rating(value) if value is not None else None
    if kind == "fibonacci":
        score = payload.get("score")
        value = float(score) if isinstance(score, (int, float)) else None
        return value, _score_rating(value)
    patterns = payload.get("patterns")
    if not isinstance(patterns, list) or not patterns:
        return None, "neutral"
    best = max(patterns, key=lambda pattern: float(pattern.get("score") or 0.0))
    score = float(best.get("score") or 0.0)
    points = best.get("points") or {}
    origin = points.get("X") or {}
    return score, "buy" if origin.get("kind") == "low" else "sell"


async def _compute_payload(
    db: Session,
    provider: MarketDataProvider,
    *,
    kind: str,
    symbol: str,
    meta: dict[str, object],
    force: bool,
) -> dict[str, object] | None:
    series, _cached = await get_cached_or_fresh_history(db, provider, symbol, force_refresh=force)
    frame = pd.DataFrame(series.candles)
    if frame.empty:
        return None

    if kind == "technical":
        payload = build_technical_snapshot(frame, timeframe=DEFAULT_TIMEFRAME, symbol=symbol)
    elif kind == "fibonacci":
        payload = scan_fibonacci(frame, symbol=symbol, meta={**meta, "timeframe": DEFAULT_TIMEFRAME})
    else:
        payload = scan_harmonic(frame, symbol=symbol)
    if payload is None:
        return None

    payload.setdefault("timeframe", DEFAULT_TIMEFRAME)
    payload.setdefault("sector", meta.get("sector"))
    payload.setdefault("nameAr", meta.get("nameAr"))
    return payload


def _replace_snapshot(
    db: Session,
    *,
    kind: str,
    symbol: str,
    as_of: datetime,
    score: float | None,
    rating: str | None,
    payload: dict[str, object],
) -> None:
    db.execute(
        delete(ScannerSnapshot).where(
            ScannerSnapshot.kind == kind,
            ScannerSnapshot.symbol == symbol,
            ScannerSnapshot.timeframe == DEFAULT_TIMEFRAME,
        )
    )
    db.add(
        ScannerSnapshot(
            kind=kind,
            symbol=symbol,
            timeframe=DEFAULT_TIMEFRAME,
            as_of=as_of,
            score=score,
            rating=rating,
            payload=payload,
        )
    )
    db.flush()


def _build_item(
    *,
    kind: str,
    symbol: str,
    as_of: datetime,
    score: float | None,
    rating: str | None,
    payload: dict[str, object],
) -> dict[str, object]:
    item: dict[str, object] = dict(payload)
    item.update(
        {
            "kind": kind,
            "symbol": symbol,
            "timeframe": DEFAULT_TIMEFRAME,
            "as_of": _as_utc_text(as_of),
            "score": score,
            "rating": rating,
            "sector": payload.get("sector"),
        }
    )
    return item


def _item_from_row(row: ScannerSnapshot) -> dict[str, object]:
    payload = row.payload if isinstance(row.payload, dict) else {}
    score = float(row.score) if row.score is not None else None
    return _build_item(
        kind=row.kind,
        symbol=row.symbol,
        as_of=row.as_of,
        score=score,
        rating=row.rating,
        payload=payload,
    )


async def refresh_scanner_snapshot(
    db: Session,
    provider: MarketDataProvider,
    *,
    kind: str,
    tickers: list[str] | None = None,
    force: bool = False,
) -> dict[str, object]:
    """Recompute ``kind`` and replace the stored row of every scanned symbol.

    Symbols are processed one by one: a provider or computation failure is
    counted and logged, never allowed to abort the rest of the run.
    """
    _validate_kind(kind)
    symbols = await _resolve_tickers(db, tickers)
    meta = _symbol_meta(db, symbols)
    as_of = datetime.now(UTC)
    stored = skipped = failed = 0

    for symbol in symbols:
        try:
            payload = await _compute_payload(
                db,
                provider,
                kind=kind,
                symbol=symbol,
                meta=meta.get(symbol, {}),
                force=force,
            )
        except Exception:
            db.rollback()
            failed += 1
            logger.exception("Scanner %s refresh failed for %s", kind, symbol)
            continue
        if payload is None:
            skipped += 1
            continue

        score, rating = _score_and_rating(kind, payload)
        _replace_snapshot(
            db,
            kind=kind,
            symbol=symbol,
            as_of=as_of,
            score=score,
            rating=rating,
            payload=payload,
        )
        db.commit()
        stored += 1

    if failed or skipped:
        logger.info(
            "Scanner %s refresh finished: stored=%d skipped=%d failed=%d",
            kind,
            stored,
            skipped,
            failed,
        )
    return {"kind": kind, "count": stored, "as_of": as_of.isoformat()}


async def get_scanner_items(
    db: Session,
    *,
    kind: str,
    sector: str | None = None,
    rating: str | None = None,
    min_score: float | None = None,
    limit: int = 500,
) -> list[dict[str, object]]:
    """Return the newest snapshot per symbol for ``kind``, filtered and sorted."""
    _validate_kind(kind)
    newest = (
        select(ScannerSnapshot.symbol, func.max(ScannerSnapshot.as_of).label("latest_as_of"))
        .where(
            ScannerSnapshot.kind == kind,
            ScannerSnapshot.timeframe == DEFAULT_TIMEFRAME,
        )
        .group_by(ScannerSnapshot.symbol)
        .subquery()
    )
    rows = db.scalars(
        select(ScannerSnapshot)
        .join(
            newest,
            and_(
                ScannerSnapshot.symbol == newest.c.symbol,
                ScannerSnapshot.as_of == newest.c.latest_as_of,
            ),
        )
        .where(
            ScannerSnapshot.kind == kind,
            ScannerSnapshot.timeframe == DEFAULT_TIMEFRAME,
        )
    ).all()

    items = [_item_from_row(row) for row in rows]
    if sector is not None:
        wanted = sector.strip()
        items = [item for item in items if str(item.get("sector") or "").strip() == wanted]
    if rating is not None:
        wanted = rating.strip()
        items = [item for item in items if item.get("rating") == wanted]
    if min_score is not None:
        items = [
            item for item in items if item.get("score") is not None and float(item["score"]) >= min_score
        ]

    items.sort(
        key=lambda item: (
            -float(item["score"]) if item.get("score") is not None else float("inf"),
            str(item.get("symbol") or ""),
        )
    )
    return items[: max(limit, 0)]


async def get_scanner_item(
    db: Session,
    *,
    kind: str,
    symbol: str,
) -> dict[str, object] | None:
    """Return the stored snapshot of a single symbol, or ``None`` when absent."""
    _validate_kind(kind)
    normalized = _normalize_symbol(symbol)
    if normalized is None:
        return None
    row = db.scalar(
        select(ScannerSnapshot)
        .where(
            ScannerSnapshot.kind == kind,
            ScannerSnapshot.symbol == normalized,
            ScannerSnapshot.timeframe == DEFAULT_TIMEFRAME,
        )
        .order_by(ScannerSnapshot.as_of.desc())
        .limit(1)
    )
    return None if row is None else _item_from_row(row)


async def build_technical_item(
    db: Session,
    provider: MarketDataProvider,
    symbol: str,
) -> dict[str, object] | None:
    """Compute the technical snapshot on demand for symbols without a stored row."""
    normalized = _normalize_symbol(symbol)
    if normalized is None:
        return None
    meta = _symbol_meta(db, [normalized]).get(normalized, {})
    try:
        payload = await _compute_payload(
            db,
            provider,
            kind="technical",
            symbol=normalized,
            meta=meta,
            force=False,
        )
    except Exception:
        db.rollback()
        logger.warning("Technical scan failed for %s", normalized, exc_info=True)
        return None
    if payload is None:
        return None
    db.commit()

    score, rating = _score_and_rating("technical", payload)
    return _build_item(
        kind="technical",
        symbol=normalized,
        as_of=datetime.now(UTC),
        score=score,
        rating=rating,
        payload=payload,
    )


async def build_harmonic_item(
    db: Session,
    provider: MarketDataProvider,
    symbol: str,
) -> dict[str, object] | None:
    """Compute harmonic patterns on demand for symbols without a stored row."""
    normalized = _normalize_symbol(symbol)
    if normalized is None:
        return None
    meta = _symbol_meta(db, [normalized]).get(normalized, {})
    try:
        payload = await _compute_payload(
            db,
            provider,
            kind="harmonic",
            symbol=normalized,
            meta=meta,
            force=False,
        )
    except Exception:
        db.rollback()
        logger.warning("Harmonic scan failed for %s", normalized, exc_info=True)
        return None
    if payload is None:
        return None
    db.commit()

    score, rating = _score_and_rating("harmonic", payload)
    return _build_item(
        kind="harmonic",
        symbol=normalized,
        as_of=datetime.now(UTC),
        score=score,
        rating=rating,
        payload=payload,
    )


async def build_smc_item(
    db: Session,
    provider: MarketDataProvider,
    symbol: str,
) -> dict[str, object] | None:
    """Run the SMC engine on cached candles and return its flattened result."""
    normalized = _normalize_symbol(symbol)
    if normalized is None:
        return None
    try:
        series, _cached = await get_cached_or_fresh_history(db, provider, normalized)
    except Exception:
        db.rollback()
        logger.warning("SMC candles unavailable for %s", normalized, exc_info=True)
        return None
    db.commit()

    frame = enrich_indicators(prepare_candles(pd.DataFrame(series.candles)))
    if frame.empty:
        return None
    result = SMCEngine(AnalysisConfig()).analyze(frame, {})
    return {
        "symbol": normalized,
        "score": result.score,
        "details": result.details,
        "reasons": result.reasons,
    }

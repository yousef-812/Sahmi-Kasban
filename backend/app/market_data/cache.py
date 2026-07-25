from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.types import CandleSeries, MarketDataProvider, MarketDataUnavailableError
from app.models import MarketDataSnapshot


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _series_from_snapshot(snapshot: MarketDataSnapshot) -> CandleSeries:
    candles = snapshot.payload.get("candles", [])
    if not isinstance(candles, list):
        raise MarketDataUnavailableError("Cached market-data payload is invalid")
    return CandleSeries(
        ticker=snapshot.ticker,
        provider=snapshot.provider,
        interval=snapshot.interval,
        period=snapshot.period,
        fetched_at=_as_utc(snapshot.fetched_at),
        data_as_of=_as_utc(snapshot.data_as_of),
        fingerprint=snapshot.fingerprint,
        candles=tuple(candles),
    )


def _snapshot_identity_query(series: CandleSeries):
    return select(MarketDataSnapshot).where(
        MarketDataSnapshot.ticker == series.ticker,
        MarketDataSnapshot.provider == series.provider,
        MarketDataSnapshot.interval == series.interval,
        MarketDataSnapshot.period == series.period,
    )


async def get_cached_or_fresh_history(
    db: Session,
    provider: MarketDataProvider,
    ticker: str,
    *,
    force_refresh: bool = False,
    now: datetime | None = None,
) -> tuple[CandleSeries, bool]:
    settings = get_settings()
    current = now or datetime.now(UTC)
    normalized_ticker = normalize_egx_ticker(ticker)

    if not force_refresh:
        cached = db.scalar(
            select(MarketDataSnapshot)
            .where(
                MarketDataSnapshot.ticker == normalized_ticker,
                MarketDataSnapshot.interval == settings.market_data_interval,
                MarketDataSnapshot.period == settings.market_data_period,
                MarketDataSnapshot.expires_at > current,
            )
            .order_by(MarketDataSnapshot.fetched_at.desc())
            .limit(1)
        )
        if cached is not None:
            return _series_from_snapshot(cached), True

    series = await provider.get_history(
        normalized_ticker,
        period=settings.market_data_period,
        interval=settings.market_data_interval,
    )
    if series.candle_count < settings.market_data_min_candles:
        raise MarketDataUnavailableError(
            f"Only {series.candle_count} candles were returned; "
            f"at least {settings.market_data_min_candles} are required"
        )

    expires_at = current + timedelta(minutes=settings.market_data_cache_minutes)
    snapshot = db.scalar(_snapshot_identity_query(series))
    if snapshot is None:
        snapshot = MarketDataSnapshot(
            ticker=normalized_ticker,
            provider=series.provider,
            interval=series.interval,
            period=series.period,
            data_as_of=series.data_as_of,
            fetched_at=series.fetched_at,
            expires_at=expires_at,
            fingerprint=series.fingerprint,
            candle_count=series.candle_count,
            payload={"candles": list(series.candles)},
        )
        db.add(snapshot)
    else:
        snapshot.data_as_of = series.data_as_of
        snapshot.fetched_at = series.fetched_at
        snapshot.expires_at = expires_at
        snapshot.fingerprint = series.fingerprint
        snapshot.candle_count = series.candle_count
        snapshot.payload = {"candles": list(series.candles)}

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raced = db.scalar(_snapshot_identity_query(series))
        if raced is None:
            raise
        return _series_from_snapshot(raced), True
    return series, False
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.types import CandleSeries, MarketDataProvider
from sahmi_kasban.index_resolver import resolve_index_for_ticker

logger = logging.getLogger(__name__)

INDEX_HISTORY_PERIOD = "2y"
INDEX_HISTORY_INTERVAL = "1d"
INDEX_MIN_CANDLES = 200


def resolve_index_name(ticker: str) -> str:
    return resolve_index_for_ticker(ticker)


async def fetch_index_series(
    db: Session,
    provider: MarketDataProvider,
    index_name: str,
    *,
    force_refresh: bool = False,
    period: str = INDEX_HISTORY_PERIOD,
    cache_minutes: int | None = None,
) -> CandleSeries:
    """Fetch the daily history for an index name (EGX30/EGX70EWI).

    Index data is TradingView-only (yfinance has no usable index coverage for
    the EGX), so this may raise MarketDataUnavailableError when TradingView is
    down; callers decide whether to degrade to index-free analysis.
    """
    settings = get_settings()
    series, _cached = await get_cached_or_fresh_history(
        db,
        provider,
        index_name,
        force_refresh=force_refresh,
        period=period,
        interval=INDEX_HISTORY_INTERVAL,
        min_candles=INDEX_MIN_CANDLES,
        cache_minutes=(cache_minutes if cache_minutes is not None else settings.market_data_cache_minutes),
    )
    return series

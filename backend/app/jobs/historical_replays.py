from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.provider import get_market_data_provider
from app.services.historical_replays import (
    ReplayBatchPlan,
    ReplayTickerComputation,
    compute_replay_rows,
    failed_ticker_computation,
    persist_replay_batch,
    prepare_next_replay_batch,
)

logger = logging.getLogger(__name__)


def _with_evaluation_scope(
    computation: ReplayTickerComputation,
) -> ReplayTickerComputation:
    """Keep eligibility and unavailable rows out of directional accuracy."""

    scoped_rows: list[dict[str, Any]] = []
    for original in computation.rows:
        row = dict(original)
        quality = dict(row.get("analysis_quality") or {})
        qualified = row.get("qualified")
        if qualified is False:
            quality["evaluation_scope"] = "eligibility_exclusion"
            quality["directional_correct"] = None
            if row.get("status") == "evaluated":
                row["correct"] = None
        elif qualified is True:
            quality["evaluation_scope"] = "directional"
            quality["directional_correct"] = row.get("correct")
        else:
            quality["evaluation_scope"] = "not_evaluated"
            quality["directional_correct"] = None
            row["correct"] = None
        row["analysis_quality"] = quality
        scoped_rows.append(row)

    return ReplayTickerComputation(
        ticker_task_id=computation.ticker_task_id,
        ticker=computation.ticker,
        provider=computation.provider,
        data_fingerprint=computation.data_fingerprint,
        candle_count=computation.candle_count,
        rows=tuple(scoped_rows),
        error_code=computation.error_code,
        error_message=computation.error_message,
    )


async def _compute_one(
    plan: ReplayBatchPlan,
    *,
    ticker_task_id,
    ticker: str,
    provider_semaphore: asyncio.Semaphore,
    cpu_semaphore: asyncio.Semaphore,
) -> ReplayTickerComputation:
    provider = get_market_data_provider()
    settings = get_settings()
    try:
        # Network fetches can overlap, but CPU analysis is capped separately so a
        # worker with two CPUs never launches five indicator/engine loops at once.
        async with provider_semaphore:
            with SessionLocal() as db:
                series, _cached = await get_cached_or_fresh_history(
                    db,
                    provider,
                    ticker,
                    period="5y",
                    interval="1d",
                    cache_minutes=settings.historical_replay_cache_hours * 60,
                    min_candles=plan.min_train_size,
                )
                db.commit()

        async with cpu_semaphore:
            computation = await asyncio.to_thread(
                compute_replay_rows,
                ticker_task_id=ticker_task_id,
                ticker=ticker,
                series=series,
                engine_version=plan.engine_version,
                start_date=plan.start_date,
                end_date=plan.end_date,
                horizon_sessions=plan.horizon_sessions,
                min_train_size=plan.min_train_size,
                neutral_band_pct=plan.neutral_band_pct,
            )
        return _with_evaluation_scope(computation)
    except Exception as exc:
        logger.warning("Historical replay failed for %s: %s", ticker, exc)
        return failed_ticker_computation(
            ticker_task_id=ticker_task_id,
            ticker=ticker,
            exc=exc,
        )


async def process_next_historical_replay_batch() -> bool:
    with SessionLocal() as db:
        db.autoflush = True
        plan = await prepare_next_replay_batch(db)
    if plan is None:
        return False

    settings = get_settings()
    provider_semaphore = asyncio.Semaphore(
        settings.historical_replay_provider_concurrency
    )
    cpu_semaphore = asyncio.Semaphore(settings.historical_replay_cpu_concurrency)
    computations = await asyncio.gather(
        *(
            _compute_one(
                plan,
                ticker_task_id=task_id,
                ticker=ticker,
                provider_semaphore=provider_semaphore,
                cpu_semaphore=cpu_semaphore,
            )
            for task_id, ticker in plan.tasks
        )
    )
    with SessionLocal() as db:
        db.autoflush = True
        persist_replay_batch(
            db,
            job_id=plan.job_id,
            computations=tuple(computations),
        )
    return True


async def run_historical_replay_scheduler() -> None:
    """Resume account-bound replay jobs on the isolated worker process group."""

    settings = get_settings()
    logger.info(
        "Historical replay worker started provider_concurrency=%s cpu_concurrency=%s",
        settings.historical_replay_provider_concurrency,
        settings.historical_replay_cpu_concurrency,
    )
    while True:
        try:
            worked = await process_next_historical_replay_batch()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Historical replay worker batch failed")
            worked = False
        await asyncio.sleep(
            settings.historical_replay_active_poll_seconds
            if worked
            else settings.historical_replay_idle_poll_seconds
        )

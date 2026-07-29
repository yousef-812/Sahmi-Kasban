from __future__ import annotations

import asyncio
import logging

from app.db.session import SessionLocal
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


async def _compute_one(
    plan: ReplayBatchPlan,
    *,
    ticker_task_id,
    ticker: str,
) -> ReplayTickerComputation:
    provider = get_market_data_provider()
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            series = await provider.get_history(ticker, period="5y", interval="1d")
            return await asyncio.to_thread(
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
        except Exception as exc:
            last_error = exc
            if attempt == 0:
                await asyncio.sleep(1.0)
    assert last_error is not None
    logger.warning("Historical replay failed for %s: %s", ticker, last_error)
    return failed_ticker_computation(
        ticker_task_id=ticker_task_id,
        ticker=ticker,
        exc=last_error,
    )


async def process_next_historical_replay_batch() -> bool:
    with SessionLocal() as db:
        plan = await prepare_next_replay_batch(db)
    if plan is None:
        return False

    # The plan is capped at five ticker tasks. Provider requests and CPU analysis
    # run concurrently, while persistence remains serialized for safe counters.
    computations = await asyncio.gather(
        *(
            _compute_one(plan, ticker_task_id=task_id, ticker=ticker)
            for task_id, ticker in plan.tasks
        )
    )
    with SessionLocal() as db:
        persist_replay_batch(
            db,
            job_id=plan.job_id,
            computations=tuple(computations),
        )
    return True


async def run_historical_replay_scheduler() -> None:
    """Resume account-bound replay jobs until every ticker is persisted."""

    while True:
        try:
            worked = await process_next_historical_replay_batch()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Historical replay worker batch failed")
            worked = False
        await asyncio.sleep(1.5 if worked else 8.0)

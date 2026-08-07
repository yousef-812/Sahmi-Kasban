from __future__ import annotations

import asyncio
import logging

from app.core.config import get_settings
from app.core.observability import configure_observability
from app.db.session import SessionLocal
from app.jobs.historical_replays import run_historical_replay_scheduler
from app.jobs.labs_backtests import run_labs_backtest_scheduler
from app.market_data.catalog import ensure_market_instrument_catalog
from app.market_data.universe import apply_market_health_quarantine

logger = logging.getLogger(__name__)


async def _run_worker() -> None:
    with SessionLocal() as db:
        await ensure_market_instrument_catalog(db)
        universe = apply_market_health_quarantine(db)
        logger.info(
            "Replay universe health active=%s tradable=%s incompatible=%s quarantined=%s",
            universe.active_catalog_count,
            len(universe.tickers),
            universe.incompatible_symbol_count,
            universe.replay_failure_quarantine_count,
        )
    await asyncio.gather(
        run_historical_replay_scheduler(),
        run_labs_backtest_scheduler(),
    )


def main() -> None:
    settings = get_settings()
    configure_observability(settings)
    logger.info("Starting isolated historical replay process")
    asyncio.run(_run_worker())


if __name__ == "__main__":
    main()

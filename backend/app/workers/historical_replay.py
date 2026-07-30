from __future__ import annotations

import asyncio
import logging

from app.core.config import get_settings
from app.core.observability import configure_observability
from app.jobs.historical_replays import run_historical_replay_scheduler


def main() -> None:
    settings = get_settings()
    configure_observability(settings)
    logging.getLogger(__name__).info("Starting isolated historical replay process")
    asyncio.run(run_historical_replay_scheduler())


if __name__ == "__main__":
    main()

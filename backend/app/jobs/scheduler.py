from __future__ import annotations

import asyncio
import logging
import os

from app.jobs.generate_daily_top10 import run_daily_top10_scan

logger = logging.getLogger(__name__)


def _enabled() -> bool:
    return os.getenv("DAILY_SCAN_SCHEDULER_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _poll_seconds() -> int:
    raw = os.getenv("DAILY_SCAN_SCHEDULER_POLL_SECONDS", "60").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 60
    return min(max(value, 30), 3600)


async def run_daily_scan_scheduler() -> None:
    """Poll the idempotent daily scan so restarts do not miss the 17:00 run."""
    if not _enabled():
        logger.info("Daily EGX scan scheduler is disabled")
        return

    interval = _poll_seconds()
    logger.info("Daily EGX scan scheduler started with a %ss poll", interval)
    while True:
        try:
            result = await run_daily_top10_scan()
            if result.get("status") == "created":
                logger.info("Daily EGX report created by scheduler: %s", result)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled daily EGX scan failed")
        await asyncio.sleep(interval)

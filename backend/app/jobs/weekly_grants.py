from __future__ import annotations

import asyncio
import logging
import os

from app.db.session import SessionLocal
from app.services.wallet import grant_due_weekly_points

logger = logging.getLogger(__name__)


def _enabled() -> bool:
    return os.getenv("WEEKLY_GRANT_SCHEDULER_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _poll_seconds() -> int:
    raw = os.getenv("WEEKLY_GRANT_SCHEDULER_POLL_SECONDS", "3600").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 3600
    return min(max(value, 300), 86_400)


async def run_weekly_grant_scheduler() -> None:
    """Apply the idempotent Cairo-week grant after startup and on a safe interval."""

    if not _enabled():
        logger.info("Weekly wallet grant scheduler is disabled")
        return

    interval = _poll_seconds()
    logger.info("Weekly wallet grant scheduler started with a %ss poll", interval)
    while True:
        try:
            with SessionLocal() as db:
                granted = grant_due_weekly_points(db)
                db.commit()
            if granted:
                logger.info("Weekly wallet grants applied", extra={"granted_users": granted})
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled weekly wallet grants failed")
        await asyncio.sleep(interval)

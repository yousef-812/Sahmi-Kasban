from __future__ import annotations

import asyncio
import logging
import os

from app.jobs.generate_daily_top10 import run_daily_top10_scan
from app.jobs.generate_investment_report import run_investment_report_scan
from app.jobs.persona_scheduler import trigger_persona_discussions_job

logger = logging.getLogger(__name__)


def _enabled() -> bool:
    return os.getenv("DAILY_SCAN_SCHEDULER_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _poll_seconds() -> int:
    raw = os.getenv("DAILY_SCAN_SCHEDULER_POLL_SECONDS", "300").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 300
    return min(max(value, 30), 3600)


async def run_daily_scan_scheduler() -> None:
    """Poll the idempotent daily scans and AI persona discussions."""
    if not _enabled():
        logger.info("Daily EGX scan scheduler is disabled")
        return

    interval = _poll_seconds()
    logger.info("Daily EGX scan scheduler started with a %ss poll", interval)
    while True:
        try:
            inv_result = await run_investment_report_scan()
            if inv_result.get("status") == "created":
                logger.info("Investment report created by scheduler: %s", inv_result)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled investment report scan failed")

        try:
            result = await run_daily_top10_scan()
            if result.get("status") == "created":
                logger.info("Daily EGX report created by scheduler: %s", result)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled daily EGX scan failed")

        try:
            persona_res = await trigger_persona_discussions_job()
            if persona_res.get("created_count", 0) > 0:
                logger.info("AI personas discussions created by scheduler: %s", persona_res)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled AI persona discussions job failed")

        try:
            from app.db.session import SessionLocal
            from app.services.community import unpin_ended_discussions
            from app.services.prediction_evaluation import auto_evaluate_due_predictions
            with SessionLocal() as db:
                unpinned = unpin_ended_discussions(db)
                if unpinned > 0:
                    logger.info("Unpinned %s ended session discussions", unpinned)
                eval_res = await auto_evaluate_due_predictions(db)
                if eval_res.get("evaluated", 0) > 0:
                    logger.info("Automated prediction evaluation completed: %s", eval_res)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled automated prediction evaluation failed")

        await asyncio.sleep(interval)

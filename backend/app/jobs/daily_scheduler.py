from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime, timedelta

from app.core.config import get_settings
from app.jobs.generate_daily_top10 import run_daily_top10_scan
from app.market_calendar import EGXTradingCalendar

logger = logging.getLogger(__name__)
_RETRY_DELAY = timedelta(minutes=15)
_IDLE_POLL_SECONDS = 60


async def run_daily_report_scheduler() -> None:
    """Run the EGX Top 10 scan after 5:00 PM Cairo on trading days.

    Fly runs one warm API machine, so an in-process scheduler removes the missing
    external-cron dependency. Database uniqueness and the scan-run lock keep the
    operation idempotent if the app is restarted or later scaled to more machines.
    """

    settings = get_settings()
    calendar = EGXTradingCalendar.from_settings()
    completed_local_date: date | None = None
    last_attempt_at: datetime | None = None

    while True:
        try:
            now = datetime.now(UTC)
            local = now.astimezone(calendar.timezone)
            scheduled = local.replace(
                hour=settings.daily_scan_hour,
                minute=settings.daily_scan_minute,
                second=0,
                microsecond=0,
            )
            due = (
                calendar.is_trading_session(local.date())
                and local >= scheduled
                and completed_local_date != local.date()
            )
            retry_ready = (
                last_attempt_at is None or now - last_attempt_at >= _RETRY_DELAY
            )
            if due and retry_ready:
                last_attempt_at = now
                result = await run_daily_top10_scan(moment=now)
                status = str(result.get("status", ""))
                if status in {"created", "already_exists"}:
                    completed_local_date = local.date()
                    logger.info("Daily report scheduler completed: %s", result)
                else:
                    logger.info("Daily report scheduler skipped: %s", result)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled daily Top 10 scan failed; it will retry")

        await asyncio.sleep(_IDLE_POLL_SECONDS)

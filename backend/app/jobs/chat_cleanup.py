from __future__ import annotations

import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import DailyChatMessage, DailyChatSessionVote

logger = logging.getLogger(__name__)

_last_chat_notification_date: str | None = None


def get_cairo_now() -> datetime:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    return datetime.now(UTC).astimezone(tz)


def cleanup_weekly_chat_sessions(db: Session) -> dict[str, int]:
    """Delete all chat messages and votes older than 7 days."""
    cairo_now = get_cairo_now()
    cutoff_date = cairo_now.date()

    deleted_messages = db.execute(
        delete(DailyChatMessage).where(DailyChatMessage.session_date < cutoff_date)
    ).rowcount

    deleted_votes = db.execute(
        delete(DailyChatSessionVote).where(DailyChatSessionVote.session_date < cutoff_date)
    ).rowcount

    if deleted_messages > 0 or deleted_votes > 0:
        db.commit()
        logger.info(
            "Weekly chat cleanup: deleted %d messages and %d votes older than %s",
            deleted_messages,
            deleted_votes,
            cutoff_date.isoformat(),
        )

    return {
        "deleted_messages": deleted_messages,
        "deleted_votes": deleted_votes,
        "cutoff_date": cutoff_date.isoformat(),
    }


def should_send_chat_open_notification() -> bool:
    """Check if we should send chat open notification (once per day at chat start time)."""
    global _last_chat_notification_date
    cairo_now = get_cairo_now()
    today_str = cairo_now.date().isoformat()
    if _last_chat_notification_date == today_str:
        return False
    return True


def mark_chat_notification_sent() -> None:
    """Mark that chat open notification was sent for today."""
    global _last_chat_notification_date
    _last_chat_notification_date = get_cairo_now().date().isoformat()

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def get_cairo_today() -> date:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    return datetime.now(UTC).astimezone(tz).date()


def refund_failed_chat_votes_job(db: Session, target_date: date | None = None) -> dict[str, float | int]:
    """No-op: voting has been removed from the trading chat system."""
    return {
        "status": "no_voting_system",
        "total_votes": 0,
        "refunded_votes_count": 0,
        "total_coins_refunded": 0.0,
    }

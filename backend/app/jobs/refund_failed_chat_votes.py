from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import DailyChatSessionVote
from app.services.wallet import credit_points

VOTE_TARGET = 40
VOTE_COST_POINTS = 50  # 0.5 coins


def get_cairo_today() -> date:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    return datetime.now(UTC).astimezone(tz).date()


def refund_failed_chat_votes_job(db: Session, target_date: date | None = None) -> dict[str, float | int]:
    if target_date is None:
        target_date = get_cairo_today()

    votes = db.scalars(
        select(DailyChatSessionVote).where(
            DailyChatSessionVote.session_date == target_date,
            DailyChatSessionVote.refunded.is_(False),
        )
    ).all()

    total_votes = len(votes)

    if total_votes >= VOTE_TARGET:
        return {
            "status": "target_reached",
            "total_votes": total_votes,
            "refunded_votes_count": 0,
            "total_coins_refunded": 0.0,
        }

    refunded_count = 0
    for vote in votes:
        tx_id = f"chat_refund_{target_date.isoformat()}_{vote.user_id}"
        credit_points(
            db,
            user_id=vote.user_id,
            amount_points=VOTE_COST_POINTS,
            transaction_id=tx_id,
            entry_type="trading_chat_vote_refund",
            details={
                "session_date": target_date.isoformat(),
                "reason": "Vote threshold of 40 not reached by 3 PM",
                "coins": 0.5,
            },
        )
        vote.refunded = True
        refunded_count += 1

    db.commit()

    return {
        "status": "refunded",
        "total_votes": total_votes,
        "refunded_votes_count": refunded_count,
        "total_coins_refunded": refunded_count * 0.5,
    }

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import User, WalletEntry
from app.services.wallet import credit_points

WELCOME_BONUS_POINTS = 500
WELCOME_BONUS_START_AT = datetime(2026, 7, 29, tzinfo=UTC)


def grant_welcome_bonus_if_eligible(db: Session, user: User) -> WalletEntry | None:
    """Grant five welcome coins once after a newly created account is verified."""

    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    else:
        created_at = created_at.astimezone(UTC)

    if (
        user.status != "active"
        or not user.email_verified
        or created_at < WELCOME_BONUS_START_AT
    ):
        return None

    return credit_points(
        db,
        user_id=user.id,
        amount_points=WELCOME_BONUS_POINTS,
        transaction_id=f"welcome-bonus:{user.id}",
        entry_type="welcome_bonus",
        reference_type="user",
        reference_id=str(user.id),
        details={"reason": "verified_new_account"},
    )

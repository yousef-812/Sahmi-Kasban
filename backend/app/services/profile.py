from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.core.avatars import validate_avatar_key
from app.core.security import hash_password, verify_password
from app.models import (
    Discussion,
    PredictionVerification,
    PushDevice,
    Subscription,
    User,
    WalletAccount,
)
from app.services.auth import revoke_all_user_sessions


class CurrentPasswordInvalidError(RuntimeError):
    """Raised when a sensitive profile action receives a wrong password."""


def get_active_subscription(db: Session, user_id: UUID) -> Subscription:
    now = datetime.now(UTC)
    subscription = db.scalar(
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            (Subscription.expires_at.is_(None) | (Subscription.expires_at > now)),
        )
        .order_by(Subscription.started_at.desc())
    )
    if subscription is None:
        raise RuntimeError("Active subscription is missing")
    return subscription


def update_profile(
    db: Session,
    user: User,
    *,
    display_name: str | None = None,
    avatar_key: str | None = None,
) -> User:
    if display_name is not None:
        user.display_name = display_name
    if avatar_key is not None:
        user.avatar_key = validate_avatar_key(avatar_key)
    db.flush()
    return user


def change_password(
    db: Session,
    user: User,
    *,
    current_password: str,
    new_password: str,
) -> None:
    if not verify_password(current_password, user.password_hash):
        raise CurrentPasswordInvalidError("Current password is incorrect")
    user.password_hash = hash_password(new_password)
    user.auth_version += 1
    revoke_all_user_sessions(db, user.id)
    db.flush()


def soft_delete_account(db: Session, user: User, *, password: str) -> None:
    if not verify_password(password, user.password_hash):
        raise CurrentPasswordInvalidError("Password is incorrect")

    now = datetime.now(UTC)
    revoke_all_user_sessions(db, user.id)
    db.execute(delete(PushDevice).where(PushDevice.user_id == user.id))
    db.execute(
        update(Subscription)
        .where(
            Subscription.user_id == user.id,
            Subscription.status == "active",
        )
        .values(status="cancelled", expires_at=now)
    )
    user.email = f"deleted-{user.id}-{uuid4().hex[:8]}@deleted.invalid"
    user.display_name = "Deleted User"
    user.avatar_key = "avatar_01"
    user.password_hash = hash_password(uuid4().hex + "Aa1!")
    user.status = "deleted"
    user.deleted_at = now
    user.auth_version += 1
    db.flush()


def get_profile_stats(db: Session, user_id: UUID) -> dict[str, int]:
    discussions_count = db.scalar(select(func.count(Discussion.id)).where(Discussion.user_id == user_id)) or 0
    verified_predictions_count = (
        db.scalar(
            select(func.count(PredictionVerification.id))
            .join(Discussion, PredictionVerification.discussion_id == Discussion.id)
            .where(Discussion.user_id == user_id)
        )
        or 0
    )
    total_reward_points = (
        db.scalar(
            select(func.coalesce(func.sum(PredictionVerification.reward_points), 0))
            .join(Discussion, PredictionVerification.discussion_id == Discussion.id)
            .where(Discussion.user_id == user_id)
        )
        or 0
    )
    return {
        "discussions_count": int(discussions_count),
        "verified_predictions_count": int(verified_predictions_count),
        "total_reward_points": int(total_reward_points),
    }


def get_wallet_balance(db: Session, user_id: UUID) -> int:
    balance = db.scalar(select(WalletAccount.balance_points).where(WalletAccount.user_id == user_id))
    if balance is None:
        raise RuntimeError("Wallet account is missing")
    return int(balance)

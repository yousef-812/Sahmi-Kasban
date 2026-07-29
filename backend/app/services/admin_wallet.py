from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CommunityAdminEvent, User, WalletEntry
from app.services.wallet import POINTS_PER_COIN, credit_points, get_wallet_account, points_to_coins


class AdminWalletUserNotFoundError(RuntimeError):
    """Raised when an administrator targets an unavailable user account."""


def credit_user_coins(
    db: Session,
    *,
    admin_user_id: UUID,
    target_user_id: UUID,
    amount_coins: int,
    reason: str,
    request_id: str,
) -> dict:
    target = db.scalar(select(User).where(User.id == target_user_id))
    if target is None or target.status == "deleted":
        raise AdminWalletUserNotFoundError("Target user was not found")

    amount_points = amount_coins * POINTS_PER_COIN
    transaction_id = f"admin-credit:{request_id}"
    existing = db.scalar(
        select(WalletEntry).where(WalletEntry.transaction_id == transaction_id)
    )

    account = get_wallet_account(db, target_user_id, lock=True)
    balance_before = int(account.balance_points)
    entry = credit_points(
        db,
        user_id=target_user_id,
        amount_points=amount_points,
        transaction_id=transaction_id,
        entry_type="admin_wallet_credit",
        reference_type="admin_user",
        reference_id=str(admin_user_id),
        details={
            "reason": reason,
            "amount_coins": amount_coins,
            "admin_user_id": str(admin_user_id),
        },
    )
    idempotent = existing is not None

    if not idempotent:
        db.add(
            CommunityAdminEvent(
                actor_user_id=admin_user_id,
                target_user_id=target_user_id,
                action="wallet_credit",
                reason_code="manual_admin_credit",
                details={
                    "reason": reason,
                    "amount_coins": amount_coins,
                    "amount_points": amount_points,
                    "balance_before_points": balance_before,
                    "balance_after_points": int(account.balance_points),
                    "wallet_entry_id": str(entry.id),
                    "transaction_id": transaction_id,
                },
            )
        )

    db.flush()
    audit_count = int(
        db.scalar(
            select(func.count(CommunityAdminEvent.id)).where(
                CommunityAdminEvent.action == "wallet_credit",
                CommunityAdminEvent.target_user_id == target_user_id,
                CommunityAdminEvent.details["transaction_id"].as_string()
                == transaction_id,
            )
        )
        or 0
    )
    return {
        "user_id": target_user_id,
        "wallet_entry_id": entry.id,
        "transaction_id": transaction_id,
        "amount_coins": amount_coins,
        "amount_points": amount_points,
        "balance_points": int(account.balance_points),
        "balance_coins": points_to_coins(int(account.balance_points)),
        "idempotent": idempotent or audit_count > 1,
    }

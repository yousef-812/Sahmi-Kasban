from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CommunityAdminEvent, User, WalletAccount, WalletEntry
from app.services.admin_wallet import credit_user_coins
from app.services.wallet import WalletTransactionConflictError


def _user(db: Session, email: str) -> User:
    user = User(
        email=email,
        password_hash="test-password-hash",
        display_name=email.split("@", maxsplit=1)[0],
        status="active",
        email_verified=True,
    )
    db.add(user)
    db.flush()
    return user


def test_admin_wallet_credit_is_audited_and_idempotent(db_session: Session) -> None:
    admin = _user(db_session, "admin@example.com")
    target = _user(db_session, "user@example.com")
    db_session.add(WalletAccount(user_id=target.id, balance_points=1_000))
    db_session.flush()

    first = credit_user_coins(
        db_session,
        admin_user_id=admin.id,
        target_user_id=target.id,
        amount_coins=25,
        reason="تعويض عن مشكلة في التقرير",
        request_id="wallet-credit-test-1",
    )
    second = credit_user_coins(
        db_session,
        admin_user_id=admin.id,
        target_user_id=target.id,
        amount_coins=25,
        reason="تعويض عن مشكلة في التقرير",
        request_id="wallet-credit-test-1",
    )

    account = db_session.scalar(
        select(WalletAccount).where(WalletAccount.user_id == target.id)
    )
    assert account is not None
    assert account.balance_points == 3_500
    assert first["balance_points"] == 3_500
    assert first["idempotent"] is False
    assert second["balance_points"] == 3_500
    assert second["idempotent"] is True

    wallet_entries = db_session.scalar(
        select(func.count(WalletEntry.id)).where(
            WalletEntry.entry_type == "admin_wallet_credit"
        )
    )
    audit_events = db_session.scalar(
        select(func.count(CommunityAdminEvent.id)).where(
            CommunityAdminEvent.action == "wallet_credit"
        )
    )
    assert wallet_entries == 1
    assert audit_events == 1


def test_admin_wallet_credit_rejects_request_key_reuse_for_other_amount(
    db_session: Session,
) -> None:
    admin = _user(db_session, "admin-conflict@example.com")
    target = _user(db_session, "user-conflict@example.com")
    db_session.add(WalletAccount(user_id=target.id, balance_points=0))
    db_session.flush()

    credit_user_coins(
        db_session,
        admin_user_id=admin.id,
        target_user_id=target.id,
        amount_coins=10,
        reason="رصيد تجريبي",
        request_id="wallet-credit-conflict",
    )

    try:
        credit_user_coins(
            db_session,
            admin_user_id=admin.id,
            target_user_id=target.id,
            amount_coins=11,
            reason="رصيد تجريبي",
            request_id="wallet-credit-conflict",
        )
    except WalletTransactionConflictError:
        pass
    else:
        raise AssertionError("Expected request-key conflict")

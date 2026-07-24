from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import Subscription, WalletAccount
from app.services.auth import register_user
from app.services.wallet import (
    InsufficientBalanceError,
    debit_points,
    get_wallet_account,
    grant_due_weekly_points,
    grant_weekly_points_for_subscription,
)


PASSWORD = "StrongPass123"


def create_registered_user(db: Session, email: str = "wallet@example.com"):
    user, _token = register_user(
        db,
        email=email,
        password=PASSWORD,
        display_name="Wallet User",
    )
    db.commit()
    return user


def test_debit_is_idempotent_and_cannot_make_balance_negative(db_session: Session) -> None:
    user = create_registered_user(db_session)
    first = debit_points(
        db_session,
        user_id=user.id,
        amount_points=100,
        transaction_id="analysis:one",
        entry_type="stock_analysis_debit",
    )
    repeated = debit_points(
        db_session,
        user_id=user.id,
        amount_points=100,
        transaction_id="analysis:one",
        entry_type="stock_analysis_debit",
    )
    db_session.commit()

    assert first.id == repeated.id
    assert get_wallet_account(db_session, user.id).balance_points == 200

    with pytest.raises(InsufficientBalanceError):
        debit_points(
            db_session,
            user_id=user.id,
            amount_points=201,
            transaction_id="analysis:two",
            entry_type="stock_analysis_debit",
        )
    db_session.rollback()
    assert get_wallet_account(db_session, user.id).balance_points == 200


def test_weekly_grant_is_unique_for_user_and_week(db_session: Session) -> None:
    user = create_registered_user(db_session)
    subscription = db_session.query(Subscription).filter_by(user_id=user.id).one()
    account = db_session.query(WalletAccount).filter_by(user_id=user.id).one()
    assert account.balance_points == 300

    current = datetime(2026, 7, 25, 12, tzinfo=UTC)
    grant_weekly_points_for_subscription(db_session, subscription, moment=current)
    grant_weekly_points_for_subscription(db_session, subscription, moment=current)
    db_session.commit()
    assert account.balance_points == 300

    next_week = current + timedelta(days=7)
    grant_weekly_points_for_subscription(db_session, subscription, moment=next_week)
    db_session.commit()
    assert account.balance_points == 600


def test_bulk_weekly_job_does_not_duplicate_grants(db_session: Session) -> None:
    first_user = create_registered_user(db_session, "first@example.com")
    second_user = create_registered_user(db_session, "second@example.com")
    moment = datetime(2026, 8, 3, 9, tzinfo=UTC)

    first_run = grant_due_weekly_points(db_session, moment=moment)
    db_session.commit()
    second_run = grant_due_weekly_points(db_session, moment=moment)
    db_session.commit()

    assert first_run == 2
    assert second_run == 0
    assert get_wallet_account(db_session, first_user.id).balance_points == 600
    assert get_wallet_account(db_session, second_user.id).balance_points == 600

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription, User, WalletAccount, WeeklyGrant
from app.services.monetization_catalog import PLANS
from app.services.profile import get_wallet_balance
from app.services.wallet import grant_due_weekly_points


def _create_user(db: Session, *, index: int) -> User:
    user = User(
        email=f"weekly-plan-{index}@example.com",
        password_hash="test-password-hash",
        display_name=f"Weekly Plan {index}",
        email_verified=True,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=0))
    db.flush()
    return user


def _add_subscription(
    db: Session,
    *,
    user: User,
    plan_code: str,
    weekly_points: int,
    ads_enabled: bool,
    started_at: datetime,
    expires_at: datetime | None = None,
) -> Subscription:
    subscription = Subscription(
        user_id=user.id,
        plan_code=plan_code,
        status="active",
        weekly_points=weekly_points,
        ads_enabled=ads_enabled,
        started_at=started_at,
        expires_at=expires_at,
    )
    db.add(subscription)
    db.flush()
    return subscription


def test_weekly_job_grants_the_active_plan_amount_once_per_cairo_week(
    db_session: Session,
) -> None:
    moment = datetime(2026, 7, 27, 8, 0, tzinfo=UTC)
    users: dict[str, User] = {}

    for index, plan in enumerate(PLANS):
        user = _create_user(db_session, index=index)
        users[plan.code] = user

        if plan.code != "free":
            _add_subscription(
                db_session,
                user=user,
                plan_code="free",
                weekly_points=500,
                ads_enabled=True,
                started_at=moment - timedelta(days=120),
            )

        _add_subscription(
            db_session,
            user=user,
            plan_code=plan.code,
            weekly_points=plan.weekly_points,
            ads_enabled=plan.ads_enabled,
            started_at=moment - timedelta(days=index + 1),
            expires_at=None if plan.code == "free" else moment + timedelta(days=30),
        )

    first_count = grant_due_weekly_points(db_session, moment=moment)
    second_count = grant_due_weekly_points(db_session, moment=moment)

    assert first_count == len(PLANS)
    assert second_count == 0

    for plan in PLANS:
        user = users[plan.code]
        assert get_wallet_balance(db_session, user.id) == plan.weekly_points
        grant = db_session.scalar(select(WeeklyGrant).where(WeeklyGrant.user_id == user.id))
        assert grant is not None
        assert grant.plan_code == plan.code
        assert grant.amount_points == plan.weekly_points


def test_weekly_job_uses_free_fallback_after_paid_subscription_expires(
    db_session: Session,
) -> None:
    moment = datetime(2026, 8, 3, 8, 0, tzinfo=UTC)
    user = _create_user(db_session, index=99)
    _add_subscription(
        db_session,
        user=user,
        plan_code="free",
        weekly_points=500,
        ads_enabled=True,
        started_at=moment - timedelta(days=180),
    )
    _add_subscription(
        db_session,
        user=user,
        plan_code="pro",
        weekly_points=15_000,
        ads_enabled=False,
        started_at=moment - timedelta(days=31),
        expires_at=moment - timedelta(minutes=1),
    )

    granted = grant_due_weekly_points(db_session, moment=moment)

    assert granted == 1
    assert get_wallet_balance(db_session, user.id) == 500
    grant = db_session.scalar(select(WeeklyGrant).where(WeeklyGrant.user_id == user.id))
    assert grant is not None
    assert grant.plan_code == "free"
    assert grant.amount_points == 500

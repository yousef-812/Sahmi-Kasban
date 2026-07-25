from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Subscription, WalletAccount, WalletEntry, WeeklyGrant

POINTS_PER_COIN = 100


class WalletError(RuntimeError):
    """Base wallet operation error."""


class WalletAccountNotFoundError(WalletError):
    """Raised when a user wallet has not been provisioned."""


class InsufficientBalanceError(WalletError):
    """Raised when a debit would make the wallet balance negative."""


class WalletTransactionConflictError(WalletError):
    """Raised when an idempotency key is reused for different operation data."""


def points_to_coins(points: int) -> str:
    return f"{Decimal(points) / Decimal(POINTS_PER_COIN):.2f}"


def cairo_week_start(moment: datetime | None = None) -> date:
    settings = get_settings()
    zone = ZoneInfo(settings.market_timezone)
    current = moment or datetime.now(UTC)
    local_date = current.astimezone(zone).date()
    return date.fromordinal(local_date.toordinal() - local_date.weekday())


def _locked_wallet_query(user_id: UUID) -> Select[tuple[WalletAccount]]:
    return (
        select(WalletAccount)
        .where(WalletAccount.user_id == user_id)
        .with_for_update()
    )


def get_wallet_account(db: Session, user_id: UUID, *, lock: bool = False) -> WalletAccount:
    query = _locked_wallet_query(user_id) if lock else select(WalletAccount).where(
        WalletAccount.user_id == user_id
    )
    account = db.scalar(query)
    if account is None:
        raise WalletAccountNotFoundError("Wallet account is not provisioned")
    return account


def _validate_existing_entry(
    entry: WalletEntry,
    *,
    user_id: UUID,
    expected_amount: int,
    entry_type: str,
) -> None:
    if (
        entry.user_id != user_id
        or entry.amount_points != expected_amount
        or entry.entry_type != entry_type
    ):
        raise WalletTransactionConflictError(
            "Transaction ID was already used with different wallet operation data"
        )


def credit_points(
    db: Session,
    *,
    user_id: UUID,
    amount_points: int,
    transaction_id: str,
    entry_type: str,
    reference_type: str | None = None,
    reference_id: str | None = None,
    details: dict | None = None,
) -> WalletEntry:
    if amount_points <= 0:
        raise ValueError("Credit amount must be positive")

    account = get_wallet_account(db, user_id, lock=True)
    existing = db.scalar(
        select(WalletEntry).where(WalletEntry.transaction_id == transaction_id)
    )
    if existing is not None:
        _validate_existing_entry(
            existing,
            user_id=user_id,
            expected_amount=amount_points,
            entry_type=entry_type,
        )
        return existing

    account.balance_points += amount_points
    entry = WalletEntry(
        user_id=user_id,
        transaction_id=transaction_id,
        entry_type=entry_type,
        amount_points=amount_points,
        status="confirmed",
        reference_type=reference_type,
        reference_id=reference_id,
        details=details or {},
        confirmed_at=datetime.now(UTC),
    )
    db.add(entry)
    db.flush()
    return entry


def debit_points(
    db: Session,
    *,
    user_id: UUID,
    amount_points: int,
    transaction_id: str,
    entry_type: str,
    reference_type: str | None = None,
    reference_id: str | None = None,
    details: dict | None = None,
) -> WalletEntry:
    if amount_points <= 0:
        raise ValueError("Debit amount must be positive")

    account = get_wallet_account(db, user_id, lock=True)
    existing = db.scalar(
        select(WalletEntry).where(WalletEntry.transaction_id == transaction_id)
    )
    if existing is not None:
        _validate_existing_entry(
            existing,
            user_id=user_id,
            expected_amount=-amount_points,
            entry_type=entry_type,
        )
        return existing
    if account.balance_points < amount_points:
        raise InsufficientBalanceError("Insufficient wallet balance")

    account.balance_points -= amount_points
    entry = WalletEntry(
        user_id=user_id,
        transaction_id=transaction_id,
        entry_type=entry_type,
        amount_points=-amount_points,
        status="confirmed",
        reference_type=reference_type,
        reference_id=reference_id,
        details=details or {},
        confirmed_at=datetime.now(UTC),
    )
    db.add(entry)
    db.flush()
    return entry


def grant_weekly_points_for_subscription(
    db: Session,
    subscription: Subscription,
    *,
    moment: datetime | None = None,
) -> WeeklyGrant | None:
    if subscription.status != "active" or subscription.weekly_points <= 0:
        return None

    week_start = cairo_week_start(moment)
    get_wallet_account(db, subscription.user_id, lock=True)
    existing = db.scalar(
        select(WeeklyGrant).where(
            WeeklyGrant.user_id == subscription.user_id,
            WeeklyGrant.week_start == week_start,
        )
    )
    if existing is not None:
        return existing

    transaction_id = f"weekly:{subscription.user_id}:{week_start.isoformat()}"
    entry = credit_points(
        db,
        user_id=subscription.user_id,
        amount_points=subscription.weekly_points,
        transaction_id=transaction_id,
        entry_type="weekly_plan_grant",
        reference_type="subscription",
        reference_id=str(subscription.id),
        details={
            "plan_code": subscription.plan_code,
            "week_start": week_start.isoformat(),
        },
    )
    grant = WeeklyGrant(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        week_start=week_start,
        plan_code=subscription.plan_code,
        amount_points=subscription.weekly_points,
        wallet_transaction_id=entry.transaction_id,
    )
    db.add(grant)
    db.flush()
    return grant


def grant_due_weekly_points(
    db: Session,
    *,
    moment: datetime | None = None,
) -> int:
    current = moment or datetime.now(UTC)
    week_start = cairo_week_start(current)
    subscriptions = db.scalars(
        select(Subscription)
        .where(
            Subscription.status == "active",
            (Subscription.expires_at.is_(None) | (Subscription.expires_at > current)),
        )
        .order_by(Subscription.user_id, Subscription.started_at.desc())
    ).all()

    granted = 0
    processed_users: set[UUID] = set()
    for subscription in subscriptions:
        if subscription.user_id in processed_users:
            continue
        processed_users.add(subscription.user_id)
        before = db.scalar(
            select(WeeklyGrant.id).where(
                WeeklyGrant.user_id == subscription.user_id,
                WeeklyGrant.week_start == week_start,
            )
        )
        grant_weekly_points_for_subscription(db, subscription, moment=current)
        if before is None:
            granted += 1
    return granted

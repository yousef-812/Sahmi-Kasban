from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import WalletEntry
from app.schemas.accounts import (
    WalletEntryResponse,
    WalletHistoryResponse,
    WalletSummaryResponse,
)
from app.services.profile import get_active_subscription, get_wallet_balance
from app.services.wallet import points_to_coins

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletSummaryResponse)
def wallet_summary(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> WalletSummaryResponse:
    subscription = get_active_subscription(db, current_user.id)
    balance_points = get_wallet_balance(db, current_user.id)
    return WalletSummaryResponse(
        balance_points=balance_points,
        balance_coins=points_to_coins(balance_points),
        plan_code=subscription.plan_code,
        weekly_points=subscription.weekly_points,
        weekly_coins=points_to_coins(subscription.weekly_points),
        ads_enabled=subscription.ads_enabled,
    )


@router.get("/history", response_model=WalletHistoryResponse)
def wallet_history(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> WalletHistoryResponse:
    total = db.scalar(
        select(func.count(WalletEntry.id)).where(WalletEntry.user_id == current_user.id)
    ) or 0
    entries = db.scalars(
        select(WalletEntry)
        .where(WalletEntry.user_id == current_user.id)
        .order_by(WalletEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return WalletHistoryResponse(
        items=[
            WalletEntryResponse(
                transaction_id=entry.transaction_id,
                entry_type=entry.entry_type,
                amount_points=entry.amount_points,
                amount_coins=points_to_coins(entry.amount_points),
                status=entry.status,
                reference_type=entry.reference_type,
                reference_id=entry.reference_id,
                details=entry.details,
                created_at=entry.created_at,
                confirmed_at=entry.confirmed_at,
            )
            for entry in entries
        ],
        total=int(total),
        limit=limit,
        offset=offset,
    )

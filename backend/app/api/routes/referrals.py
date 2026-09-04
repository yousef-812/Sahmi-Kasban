from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.accounts import ReferralStatsResponse
from app.services.referral import get_user_referral_stats

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/me", response_model=ReferralStatsResponse)
def get_my_referral_stats(
    db: DatabaseSession,
    user: CurrentUser,
) -> ReferralStatsResponse:
    stats = get_user_referral_stats(db, user)
    return ReferralStatsResponse(**stats)

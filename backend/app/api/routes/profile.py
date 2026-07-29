from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.admin import is_admin_email
from app.core.avatars import AVATAR_KEYS
from app.schemas.accounts import (
    AvatarOption,
    AvatarOptionsResponse,
    ChangePasswordRequest,
    DeleteAccountRequest,
    MessageResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.profile import (
    CurrentPasswordInvalidError,
    change_password,
    get_active_subscription,
    get_profile_stats,
    get_wallet_balance,
    soft_delete_account,
    update_profile,
)
from app.services.wallet import points_to_coins

router = APIRouter(prefix="/profile", tags=["profile"])


def build_profile_response(db: DatabaseSession, user: CurrentUser) -> ProfileResponse:
    subscription = get_active_subscription(db, user.id)
    balance_points = get_wallet_balance(db, user.id)
    stats = get_profile_stats(db, user.id)
    return ProfileResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_key=user.avatar_key,
        email_verified=user.email_verified,
        status=user.status,
        is_admin=is_admin_email(user.email),
        plan_code=subscription.plan_code,
        subscription_status=subscription.status,
        weekly_points=subscription.weekly_points,
        weekly_coins=points_to_coins(subscription.weekly_points),
        ads_enabled=subscription.ads_enabled,
        subscription_expires_at=subscription.expires_at,
        balance_points=balance_points,
        balance_coins=points_to_coins(balance_points),
        **stats,
    )


@router.get("/avatars", response_model=AvatarOptionsResponse)
def avatar_options() -> AvatarOptionsResponse:
    return AvatarOptionsResponse(
        avatars=[
            AvatarOption(key=key, asset_path=f"assets/avatars/{key}.webp")
            for key in AVATAR_KEYS
        ]
    )


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(db: DatabaseSession, current_user: CurrentUser) -> ProfileResponse:
    return build_profile_response(db, current_user)


@router.patch("/me", response_model=ProfileResponse)
def update_my_profile(
    payload: ProfileUpdateRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ProfileResponse:
    update_profile(
        db,
        current_user,
        display_name=payload.display_name,
        avatar_key=payload.avatar_key,
    )
    db.commit()
    db.refresh(current_user)
    return build_profile_response(db, current_user)


@router.post("/change-password", response_model=MessageResponse)
def change_my_password(
    payload: ChangePasswordRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MessageResponse:
    try:
        change_password(
            db,
            current_user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
        db.commit()
    except CurrentPasswordInvalidError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return MessageResponse(message="Password changed; all sessions were revoked")


@router.delete("/me", response_model=MessageResponse)
def delete_my_account(
    payload: DeleteAccountRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MessageResponse:
    try:
        soft_delete_account(db, current_user, password=payload.password)
        db.commit()
    except CurrentPasswordInvalidError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        ) from exc
    return MessageResponse(message="Account deleted successfully")

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.avatars import DEFAULT_AVATAR_KEY, validate_avatar_key


class MessageResponse(BaseModel):
    message: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=2, max_length=80)
    avatar_key: str = DEFAULT_AVATAR_KEY
    referral_code: str | None = Field(default=None, max_length=32)

    @field_validator("display_name")
    @classmethod
    def clean_display_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Display name is too short")
        return cleaned

    @field_validator("avatar_key")
    @classmethod
    def supported_avatar(cls, value: str) -> str:
        return validate_avatar_key(value)


class RegisterResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    requires_email_verification: bool = True
    verification_code_expires_in_seconds: int = 600
    weekly_points_granted: int = 500


class VerifyEmailRequest(BaseModel):
    email: EmailStr | None = None
    code: str | None = Field(default=None, pattern=r"^\d{6}$")
    token: str | None = Field(default=None, min_length=20, max_length=500)

    @model_validator(mode="after")
    def require_code_or_legacy_token(self) -> VerifyEmailRequest:
        has_code = self.email is not None and self.code is not None
        has_token = self.token is not None
        if has_code == has_token:
            raise ValueError("Provide email and code, or provide a legacy token")
        return self


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=500)


class LogoutRequest(RefreshRequest):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=10, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1, max_length=128)


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=80)
    avatar_key: str | None = None

    @field_validator("display_name")
    @classmethod
    def clean_optional_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Display name is too short")
        return cleaned

    @field_validator("avatar_key")
    @classmethod
    def supported_optional_avatar(cls, value: str | None) -> str | None:
        return validate_avatar_key(value) if value is not None else None


class AvatarOption(BaseModel):
    key: str
    asset_path: str


class AvatarOptionsResponse(BaseModel):
    avatars: list[AvatarOption]


class ProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    avatar_key: str
    referral_code: str | None = None
    email_verified: bool
    status: str
    is_admin: bool
    plan_code: str
    subscription_status: str
    weekly_points: int
    weekly_coins: str
    ads_enabled: bool
    subscription_expires_at: datetime | None
    balance_points: int
    balance_coins: str
    discussions_count: int
    verified_predictions_count: int
    total_reward_points: int


class ReferredUserItem(BaseModel):
    display_name: str
    avatar_key: str
    joined_at: str = ""
    registered_at: str | None = None
    status: str
    earned_points: int = 0
    earned_coins: str = "0.00"


class ReferralStatsResponse(BaseModel):
    referral_code: str
    play_store_url: str
    share_text: str
    reward_coins_per_referral: float
    reward_points_per_referral: int
    total_referrals_count: int
    total_referred_count: int
    total_earned_points: int
    total_earned_coins: str
    recent_referrals: list[ReferredUserItem]
    referred_users: list[ReferredUserItem]



class WalletSummaryResponse(BaseModel):
    balance_points: int
    balance_coins: str
    plan_code: str
    weekly_points: int
    weekly_coins: str
    ads_enabled: bool


class WalletEntryResponse(BaseModel):
    transaction_id: str
    entry_type: str
    amount_points: int
    amount_coins: str
    status: str
    reference_type: str | None
    reference_id: str | None
    details: dict
    created_at: datetime
    confirmed_at: datetime | None


class WalletHistoryResponse(BaseModel):
    items: list[WalletEntryResponse]
    total: int
    limit: int
    offset: int

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class PlanCatalogItem(BaseModel):
    code: str
    display_name_ar: str
    weekly_points: int = Field(ge=0)
    weekly_coins: str
    ads_enabled: bool
    product_id: str | None
    history_limit: int = Field(ge=0)
    report_history_days: int = Field(ge=0)
    badge_code: str | None


class CoinPackCatalogItem(BaseModel):
    product_id: str
    display_name_ar: str
    points: int = Field(gt=0)
    coins: str


class MonetizationCatalogResponse(BaseModel):
    plans: list[PlanCatalogItem]
    coin_packs: list[CoinPackCatalogItem]
    ad_reward_points: int = Field(gt=0)
    ad_reward_coins: str
    ad_reward_daily_limit: int = Field(gt=0)
    ad_reward_cooldown_seconds: int = Field(ge=0)


class RewardedAdEligibilityResponse(BaseModel):
    eligible: bool
    reason: str | None
    rewards_used_today: int = Field(ge=0)
    rewards_remaining_today: int = Field(ge=0)
    next_available_at: datetime | None


class RewardedAdSessionRequest(BaseModel):
    platform: Literal["android", "ios"]


class RewardedAdSessionResponse(BaseModel):
    session_id: UUID
    ad_unit_id: str
    custom_data: str
    expires_at: datetime
    test_mode: bool


class RewardedAdSimulationRequest(BaseModel):
    custom_data: str = Field(min_length=20, max_length=256)


class RewardedAdSimulationResponse(BaseModel):
    idempotent: bool
    balance_points: int = Field(ge=0)
    balance_coins: str


class GooglePlayPurchaseRequest(BaseModel):
    product_id: str = Field(min_length=3, max_length=120)
    purchase_token: str = Field(min_length=8, max_length=4096)


class GooglePlayPurchaseResponse(BaseModel):
    purchase_id: UUID
    product_id: str
    product_type: Literal["subscription", "coins"]
    purchase_state: str
    acknowledgement_state: str
    entitlement_granted: bool
    idempotent: bool
    plan_code: str
    balance_points: int = Field(ge=0)
    balance_coins: str
    subscription_expires_at: datetime | None


class MonetizationStatusResponse(BaseModel):
    plan_code: str
    subscription_status: str
    subscription_expires_at: datetime | None
    weekly_points: int = Field(ge=0)
    weekly_coins: str
    ads_enabled: bool
    rewarded_ad: RewardedAdEligibilityResponse

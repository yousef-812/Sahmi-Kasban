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
    features: list[str] = Field(default_factory=list)
    comparison_monthly_allowance: int = Field(default=0, ge=0)
    max_comparison_stocks: int = Field(default=0, ge=0, le=5)
    priority_level: int = Field(default=0, ge=0, le=3)
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
    reward_points: int = Field(default=75, ge=0)
    reward_points_rewarded_interstitial: int = Field(default=30, ge=0)


class RewardedAdSessionRequest(BaseModel):
    platform: Literal["android", "ios"]
    ad_format: Literal["rewarded", "rewarded_interstitial"] = "rewarded"


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


class AdTelemetryEventRequest(BaseModel):
    ad_type: Literal["banner", "native", "interstitial", "rewarded", "app_open", "rewarded_interstitial"]
    event_type: Literal["loaded", "impression", "clicked", "failed_to_load", "failed_to_show", "reward_granted", "earned_reward"]
    ad_unit_id: str | None = None
    platform: str = "android"
    error_message: str | None = None


class AdEventLogItem(BaseModel):
    id: UUID
    user_id: UUID | None
    ad_type: str
    event_type: str
    ad_unit_id: str | None
    platform: str
    error_message: str | None
    created_at: datetime


class AdTelemetrySummaryResponse(BaseModel):
    total_events: int = Field(ge=0)
    impressions: int = Field(ge=0)
    load_failures: int = Field(ge=0)
    clicks: int = Field(ge=0)
    breakdown_by_type: dict[str, int] = Field(default_factory=dict)
    recent_logs: list[AdEventLogItem] = Field(default_factory=list)

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

SettingValue = int | float | bool | str
PushPlatform = Literal["android", "ios", "web"]
BroadcastAudience = Literal["all", "active", "plan", "user_ids"]


class OperationalSettingResponse(BaseModel):
    key: str
    category: str
    label: str
    description: str
    kind: str
    value: SettingValue
    default_value: SettingValue
    min_value: int | float | None
    max_value: int | float | None
    updated_at: datetime | None


class OperationalSettingsResponse(BaseModel):
    items: list[OperationalSettingResponse]


class OperationalSettingUpdateRequest(BaseModel):
    value: SettingValue


class AdminOverviewResponse(BaseModel):
    users_total: int = Field(ge=0)
    users_active: int = Field(ge=0)
    users_suspended: int = Field(ge=0)
    users_verified: int = Field(default=0, ge=0)
    users_unverified: int = Field(default=0, ge=0)
    users_active_now: int = Field(default=0, ge=0)
    discussions_pending: int = Field(ge=0)
    discussions_published: int = Field(ge=0)
    discussions_hidden: int = Field(ge=0)
    open_reports: int = Field(ge=0)
    open_appeals: int = Field(ge=0)
    verified_predictions: int = Field(ge=0)
    wallet_points_total: int
    notifications_today: int = Field(ge=0)
    unread_notifications: int = Field(ge=0)


class AdminUserListItem(BaseModel):
    id: UUID
    email: str
    display_name: str
    status: str
    plan_code: str
    balance_points: int
    discussions_count: int = Field(ge=0)
    created_at: datetime


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class AdminAuditEventResponse(BaseModel):
    id: UUID
    actor_user_id: UUID | None
    target_user_id: UUID | None
    discussion_id: UUID | None
    action: str
    reason_code: str | None
    details: dict
    created_at: datetime


class AdminAuditListResponse(BaseModel):
    items: list[AdminAuditEventResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class ServiceHealthResponse(BaseModel):
    id: UUID
    component: str
    provider: str
    status: str
    latency_ms: int | None
    details: dict
    observed_at: datetime


class ServiceHealthListResponse(BaseModel):
    items: list[ServiceHealthResponse]


class PushDeviceRegisterRequest(BaseModel):
    token: str = Field(min_length=20, max_length=4096)
    platform: PushPlatform

    @field_validator("token")
    @classmethod
    def normalize_token(cls, value: str) -> str:
        return value.strip()


class PushDeviceResponse(BaseModel):
    id: UUID
    platform: PushPlatform
    enabled: bool
    last_seen_at: datetime
    idempotent: bool


class PushDeviceUnregisterRequest(BaseModel):
    token: str = Field(min_length=20, max_length=4096)


class PushDeviceUnregisterResponse(BaseModel):
    enabled: bool
    idempotent: bool


class NotificationResponse(BaseModel):
    id: UUID
    title: str
    body: str
    category: str
    data: dict
    read_at: datetime | None
    sent_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int = Field(ge=0)
    unread_count: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class NotificationReadResponse(BaseModel):
    notification_id: UUID
    read: bool
    idempotent: bool


class NotificationReadAllResponse(BaseModel):
    updated: int = Field(ge=0)


class AdminBroadcastRequest(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    body: str = Field(min_length=3, max_length=1000)
    category: str = Field(default="announcement", min_length=2, max_length=40)
    data: dict[str, Any] = Field(default_factory=dict)
    audience: BroadcastAudience = "active"
    plan_code: str | None = Field(default=None, max_length=32)
    user_ids: list[UUID] = Field(default_factory=list, max_length=500)

    @field_validator("title", "body", "category")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_audience(self) -> AdminBroadcastRequest:
        if self.audience == "plan" and not self.plan_code:
            raise ValueError("Plan audience requires plan_code")
        if self.audience == "user_ids" and not self.user_ids:
            raise ValueError("user_ids audience requires at least one user")
        return self


class AdminBroadcastResponse(BaseModel):
    targeted_users: int = Field(ge=0)
    notifications_created: int = Field(ge=0)
    push_sent: int = Field(ge=0)
    push_failed: int = Field(ge=0)
    push_skipped: int = Field(ge=0)


class ReportEvaluationResponse(BaseModel):
    id: UUID
    report_id: UUID
    target_session_date: date
    status: str
    attempt_count: int = Field(ge=0)
    evaluated_count: int = Field(ge=0)
    pending_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    started_at: datetime | None
    completed_at: datetime | None
    last_attempt_at: datetime | None
    details: dict


class ReportEvaluationListResponse(BaseModel):
    items: list[ReportEvaluationResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class ReportEvaluationBackfillRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)


class ReportEvaluationBackfillResponse(BaseModel):
    scanned_reports: int = Field(ge=0)
    completed_reports: int = Field(ge=0)
    partial_reports: int = Field(ge=0)
    failed_reports: int = Field(ge=0)
    skipped_reports: int = Field(ge=0)
    evaluation_ids: list[UUID]


class AdminUpgradeUserPlanRequest(BaseModel):
    plan_code: Literal["free", "basic", "advanced", "pro"]
    duration_days: int | None = Field(default=None, ge=1, le=3650)
    bonus_points: int = Field(default=0, ge=0, le=1_000_000)


class AdminUpgradeUserPlanResponse(BaseModel):
    user_id: UUID
    display_name: str
    email: str
    plan_code: str
    status: str
    weekly_points: int
    ads_enabled: bool
    started_at: datetime
    expires_at: datetime | None = None
    balance_points: int
    message: str

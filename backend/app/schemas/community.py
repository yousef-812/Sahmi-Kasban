from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

DiscussionPeriod = Literal["next_session", "week", "month"]
DiscussionStatus = Literal["pending_review", "published", "rejected", "hidden"]
ReportReason = Literal[
    "spam",
    "abuse",
    "misleading",
    "contact_info",
    "off_topic",
    "other",
]
AdminDiscussionAction = Literal["approve", "reject", "hide", "restore"]
PredictionDirection = Literal["up", "down", "neutral"]


class DiscussionCreateRequest(BaseModel):
    submission_key: str = Field(min_length=8, max_length=64)
    ticker: str = Field(min_length=2, max_length=24, pattern=r"^[A-Za-z0-9._-]+$")
    title: str = Field(min_length=10, max_length=180)
    content: str = Field(min_length=20, max_length=5000)
    period_type: DiscussionPeriod

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("submission_key", "title", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class DiscussionAuthorResponse(BaseModel):
    user_id: UUID
    display_name: str
    avatar_key: str


class DiscussionResponse(BaseModel):
    id: UUID
    ticker: str
    title: str
    content: str
    period_type: DiscussionPeriod
    status: DiscussionStatus
    moderation_result: dict
    frozen_prediction: dict
    rejection_code: str | None
    created_at: datetime
    reviewed_at: datetime | None
    published_at: datetime | None
    author: DiscussionAuthorResponse


class DiscussionSubmissionResponse(BaseModel):
    discussion: DiscussionResponse
    held_points: int = Field(ge=0)
    held_coins: str
    balance_points: int = Field(ge=0)
    balance_coins: str
    idempotent: bool


class DiscussionListResponse(BaseModel):
    items: list[DiscussionResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class DiscussionReportRequest(BaseModel):
    reason_code: ReportReason
    details: str = Field(default="", max_length=1000)

    @field_validator("details")
    @classmethod
    def strip_details(cls, value: str) -> str:
        return value.strip()


class DiscussionReportResponse(BaseModel):
    report_id: UUID
    discussion_id: UUID
    status: str
    idempotent: bool


class UserMuteResponse(BaseModel):
    muted_user_id: UUID
    muted: bool
    idempotent: bool


class AdminPredictionInput(BaseModel):
    direction: PredictionDirection
    target_price: float | None = Field(default=None, gt=0)
    deadline: str | None = Field(default=None, max_length=120)
    claims: list[str] = Field(default_factory=list, max_length=10)
    specificity: float = Field(default=0.0, ge=0, le=1)

    @field_validator("deadline")
    @classmethod
    def strip_optional_deadline(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("claims")
    @classmethod
    def normalize_claims(cls, value: list[str]) -> list[str]:
        claims: list[str] = []
        for item in value:
            cleaned = item.strip()
            if cleaned and cleaned not in claims:
                claims.append(cleaned[:300])
        return claims


class AdminDiscussionActionRequest(BaseModel):
    action: AdminDiscussionAction
    reason_code: str | None = Field(default=None, min_length=2, max_length=64)
    details: str = Field(default="", max_length=1000)
    prediction: AdminPredictionInput | None = None

    @field_validator("reason_code")
    @classmethod
    def strip_optional_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned or None

    @field_validator("details")
    @classmethod
    def strip_admin_details(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_action_fields(self) -> AdminDiscussionActionRequest:
        if self.action == "approve" and self.prediction is None:
            raise ValueError("Manual approval requires a structured prediction")
        if self.action in {"reject", "hide"} and not self.reason_code:
            raise ValueError(f"{self.action} requires a reason code")
        return self


class AdminDiscussionResponse(BaseModel):
    discussion: DiscussionResponse
    hidden_at: datetime | None
    open_report_count: int = Field(ge=0)
    idempotent: bool = False


class AdminDiscussionListResponse(BaseModel):
    items: list[AdminDiscussionResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class AdminUserActionRequest(BaseModel):
    reason_code: str = Field(min_length=2, max_length=64)
    details: str = Field(default="", max_length=1000)

    @field_validator("reason_code", "details")
    @classmethod
    def normalize_admin_user_text(cls, value: str) -> str:
        return value.strip()


class AdminUserActionResponse(BaseModel):
    user_id: UUID
    status: str
    pending_rejected: int = Field(ge=0)
    published_hidden: int = Field(ge=0)
    idempotent: bool

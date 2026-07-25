from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

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

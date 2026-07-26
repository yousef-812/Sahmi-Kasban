from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

PredictionVerificationState = Literal[
    "unavailable",
    "waiting",
    "eligible",
    "verified",
]
PredictionStrength = Literal["rejected", "weak", "strong", "very_strong"]


class PredictionVerificationResponse(BaseModel):
    id: UUID
    discussion_id: UUID
    score_bp: int = Field(ge=0, le=10000)
    score_percent: float = Field(ge=0, le=100)
    strength: PredictionStrength
    reward_points: int = Field(ge=0)
    reward_coins: str
    evidence: dict
    verified_at: datetime


class PredictionVerificationStatusResponse(BaseModel):
    discussion_id: UUID
    state: PredictionVerificationState
    eligible_at: datetime | None
    verification: PredictionVerificationResponse | None


class PredictionVerificationSubmissionResponse(BaseModel):
    verification: PredictionVerificationResponse
    balance_points: int = Field(ge=0)
    balance_coins: str
    idempotent: bool


class PredictionStatsResponse(BaseModel):
    verified_predictions: int = Field(ge=0)
    accepted_predictions: int = Field(ge=0)
    accuracy_percent: float = Field(ge=0, le=100)
    average_score_percent: float = Field(ge=0, le=100)
    total_reward_points: int = Field(ge=0)
    total_reward_coins: str

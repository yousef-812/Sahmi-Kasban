from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

PerformanceWindow = Literal[7, 30]


class PerformanceOutcomeResponse(BaseModel):
    id: UUID
    ticker: str
    rank: int = Field(ge=1, le=10)
    status: str
    expected_direction: str
    price_at_analysis: float
    session_open: float | None
    session_high: float | None
    session_low: float | None
    session_close: float | None
    return_bp: int | None
    max_upside_bp: int | None
    max_drawdown_bp: int | None
    direction_correct: bool | None
    target_one: float | None
    target_two: float | None
    stop_loss: float | None
    target_one_hit: bool | None
    target_two_hit: bool | None
    stop_loss_hit: bool | None
    provider: str | None
    data_as_of: datetime | None
    evaluated_at: datetime | None
    evaluator_version: str
    evidence: dict
    correction_count: int = Field(ge=0)


class PerformanceBestWorstResponse(BaseModel):
    report_id: UUID
    target_session_date: date
    ticker: str
    rank: int = Field(ge=1, le=10)
    return_bp: int


class PerformanceSessionResponse(BaseModel):
    report_id: UUID
    target_session_date: date
    evaluation_status: str
    total_items: int = Field(ge=0)
    evaluated_items: int = Field(ge=0)
    pending_items: int = Field(ge=0)
    failed_items: int = Field(ge=0)
    data_completeness_pct: float = Field(ge=0, le=100)
    average_return_bp: int | None
    positive_count: int = Field(ge=0)
    negative_count: int = Field(ge=0)
    direction_accuracy_pct: float | None
    target_one_hit_rate_pct: float | None
    stop_loss_hit_rate_pct: float | None


class PerformanceRankResponse(BaseModel):
    rank: int = Field(ge=1, le=10)
    evaluated_items: int = Field(ge=0)
    average_return_bp: int | None
    median_return_bp: int | None
    positive_rate_pct: float | None
    direction_accuracy_pct: float | None
    target_one_hit_rate_pct: float | None
    stop_loss_hit_rate_pct: float | None


class PerformanceSummaryResponse(BaseModel):
    window_sessions: int
    sessions_found: int = Field(ge=0)
    complete_sessions: int = Field(ge=0)
    total_items: int = Field(ge=0)
    evaluated_items: int = Field(ge=0)
    pending_items: int = Field(ge=0)
    failed_items: int = Field(ge=0)
    data_completeness_pct: float = Field(ge=0, le=100)
    positive_count: int = Field(ge=0)
    negative_count: int = Field(ge=0)
    flat_count: int = Field(ge=0)
    average_return_bp: int | None
    median_return_bp: int | None
    positive_rate_pct: float | None
    direction_accuracy_pct: float | None
    target_one_hit_rate_pct: float | None
    target_two_hit_rate_pct: float | None
    stop_loss_hit_rate_pct: float | None
    best_outcome: PerformanceBestWorstResponse | None
    worst_outcome: PerformanceBestWorstResponse | None
    ranks: list[PerformanceRankResponse]
    sessions: list[PerformanceSessionResponse]
    benchmark: dict
    negative_results_retained: bool = True


class PerformanceReportListItem(BaseModel):
    report_id: UUID
    target_session_date: date
    generated_at: datetime
    evaluation_status: str
    total_items: int = Field(ge=0)
    evaluated_items: int = Field(ge=0)
    pending_items: int = Field(ge=0)
    failed_items: int = Field(ge=0)
    data_completeness_pct: float = Field(ge=0, le=100)
    average_return_bp: int | None
    positive_count: int = Field(ge=0)
    negative_count: int = Field(ge=0)


class PerformanceReportListResponse(BaseModel):
    items: list[PerformanceReportListItem]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class PerformanceRevisionResponse(BaseModel):
    id: UUID
    revision_number: int = Field(gt=0)
    reason: str
    before_payload: dict
    after_payload: dict
    created_at: datetime


class PerformanceReportDetailResponse(BaseModel):
    report_id: UUID
    target_session_date: date
    generated_at: datetime
    evaluation_status: str
    session: PerformanceSessionResponse
    outcomes: list[PerformanceOutcomeResponse]
    revisions: list[PerformanceRevisionResponse]
    negative_results_retained: bool = True


class PerformanceDelayedItemResponse(BaseModel):
    report_id: UUID
    target_session_date: date
    evaluation_id: UUID | None
    evaluation_status: str
    total_items: int = Field(ge=0)
    evaluated_items: int = Field(ge=0)
    pending_items: int = Field(ge=0)
    failed_items: int = Field(ge=0)
    last_attempt_at: datetime | None
    reasons: list[str]


class PerformanceDelayedListResponse(BaseModel):
    items: list[PerformanceDelayedItemResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class PerformanceCorrectionRequest(BaseModel):
    reason: str = Field(min_length=8, max_length=500)
    session_open: float = Field(gt=0)
    session_high: float = Field(gt=0)
    session_low: float = Field(gt=0)
    session_close: float = Field(gt=0)
    provider: str = Field(min_length=2, max_length=80)
    data_fingerprint: str = Field(min_length=4, max_length=128)
    data_as_of: datetime


class PerformanceCorrectionResponse(BaseModel):
    outcome: PerformanceOutcomeResponse
    revision: PerformanceRevisionResponse

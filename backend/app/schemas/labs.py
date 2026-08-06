from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class LabsBacktestParams(BaseModel):
    start_date: date
    end_date: date
    rank: int | None = Field(default=None, ge=1, le=10)
    exit_mode: str
    track_interval_minutes: int
    source_interval: str


class LabsBacktestSummary(BaseModel):
    reports_scanned: int
    trades: int
    hits: int
    misses: int
    skipped: int
    hit_rate_pct: float
    avg_return_pct: float
    median_return_pct: float | None
    avg_hit_return_pct: float
    avg_miss_return_pct: float
    median_minutes_to_hit: float | None
    best_return_pct: float
    worst_return_pct: float
    cumulative_return_pct: float


class LabsTrackedPoint(BaseModel):
    time: str
    price: float
    high: float
    low: float


class LabsBacktestSession(BaseModel):
    target_session_date: date
    report_id: UUID
    rank: int
    ticker: str
    score: float
    price_at_analysis: float | None
    targets: list[float]
    stop_loss: float | None
    session_open: float | None
    exit_price: float | None
    exit_reason: str
    hit: bool
    minutes_to_exit: int | None
    return_pct: float | None
    tracked: list[LabsTrackedPoint]


class LabsDailyBacktestResponse(BaseModel):
    params: LabsBacktestParams
    summary: LabsBacktestSummary
    sessions: list[LabsBacktestSession]
    meta: dict[str, Any] = Field(default_factory=dict)

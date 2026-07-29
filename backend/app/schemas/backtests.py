from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

BacktestPeriod = Literal["1y", "2y", "5y", "10y", "max"]


class AnalysisBacktestRunRequest(BaseModel):
    request_key: str = Field(min_length=12, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    tickers: list[str] = Field(min_length=1, max_length=3)
    period: BacktestPeriod = "5y"
    interval: Literal["1d"] = "1d"
    min_train_size: int = Field(default=200, ge=60, le=1000)
    horizon_sessions: int = Field(default=5, ge=1, le=20)
    step_sessions: int = Field(default=20, ge=1, le=60)
    neutral_band_pct: float = Field(default=1.0, ge=0, le=10)

    @field_validator("tickers")
    @classmethod
    def normalize_tickers(cls, value: list[str]) -> list[str]:
        normalized = [ticker.strip().upper() for ticker in value if ticker.strip()]
        if not normalized:
            raise ValueError("At least one ticker is required")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Choose different stock symbols")
        return normalized


class AnalysisBacktestResultResponse(BaseModel):
    id: UUID
    run_id: UUID
    ticker: str
    status: str
    provider: str | None
    data_fingerprint: str | None
    data_as_of: datetime | None
    candle_count: int = Field(ge=0)
    observations: int = Field(ge=0)
    buy_count: int = Field(ge=0)
    watch_count: int = Field(ge=0)
    avoid_count: int = Field(ge=0)
    directional_accuracy_pct: float
    buy_hit_rate_pct: float
    avoid_hit_rate_pct: float
    watch_hit_rate_pct: float
    average_forward_return_pct: float
    median_forward_return_pct: float
    average_buy_return_pct: float
    average_buy_max_drawdown_pct: float
    profit_factor: float | None
    error_code: str | None
    error_message: str | None
    summary: dict


class AnalysisBacktestRunResponse(BaseModel):
    id: UUID
    request_key: str
    engine_version: str
    status: str
    tickers: list[str]
    period: str
    interval: str
    min_train_size: int
    horizon_sessions: int
    step_sessions: int
    neutral_band_pct: float
    total_tickers: int = Field(gt=0)
    completed_tickers: int = Field(ge=0)
    failed_tickers: int = Field(ge=0)
    requested_by: UUID | None
    started_at: datetime
    completed_at: datetime | None
    details: dict
    idempotent: bool = False
    results: list[AnalysisBacktestResultResponse] = Field(default_factory=list)


class AnalysisBacktestRunListResponse(BaseModel):
    items: list[AnalysisBacktestRunResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


class AnalysisBacktestVersionSummaryResponse(BaseModel):
    engine_version: str
    runs: int = Field(ge=0)
    tickers: int = Field(ge=0)
    observations: int = Field(ge=0)
    buy_count: int = Field(ge=0)
    watch_count: int = Field(ge=0)
    avoid_count: int = Field(ge=0)
    directional_accuracy_pct: float
    buy_hit_rate_pct: float
    average_forward_return_pct: float
    average_buy_return_pct: float
    average_buy_max_drawdown_pct: float
    profit_factor: float | None


class AnalysisBacktestVersionListResponse(BaseModel):
    items: list[AnalysisBacktestVersionSummaryResponse]

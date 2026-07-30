from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class HistoricalReplayCreateRequest(BaseModel):
    request_key: str = Field(min_length=12, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    start_date: date
    end_date: date
    horizon_sessions: int = Field(default=5, ge=1, le=20)
    min_train_size: int = Field(default=200, ge=60, le=1000)
    neutral_band_pct: float = Field(default=1.0, ge=0, le=10)

    @model_validator(mode="after")
    def validate_range(self) -> HistoricalReplayCreateRequest:
        today = date.today()
        if self.end_date < self.start_date:
            raise ValueError("تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("الحد الأقصى لكل اختبار هو 31 يومًا")
        if self.end_date > today:
            raise ValueError("لا يمكن اختبار أيام مستقبلية")
        if self.start_date < today - timedelta(days=365 * 5 + 2):
            raise ValueError("الاختبار متاح لآخر خمس سنوات فقط")
        return self


class HistoricalReplayTickerResponse(BaseModel):
    ticker: str
    status: str
    provider: str | None
    candle_count: int = Field(ge=0)
    rows_written: int = Field(ge=0)
    evaluated_rows: int = Field(ge=0)
    pending_rows: int = Field(ge=0)
    failed_rows: int = Field(ge=0)
    error_code: str | None
    error_message: str | None


class HistoricalReplayJobResponse(BaseModel):
    id: UUID
    request_key: str
    engine_version: str
    status: str
    control_state: str
    worker_isolated: bool
    can_pause: bool
    can_resume: bool
    can_cancel: bool
    start_date: date
    end_date: date
    horizon_sessions: int
    min_train_size: int
    neutral_band_pct: float
    parallelism: int
    total_tickers: int = Field(ge=0)
    processed_tickers: int = Field(ge=0)
    successful_tickers: int = Field(ge=0)
    failed_tickers: int = Field(ge=0)
    total_rows: int = Field(ge=0)
    evaluated_rows: int = Field(ge=0)
    pending_rows: int = Field(ge=0)
    progress_pct: float = Field(ge=0, le=100)
    throughput_tickers_per_minute: float | None = Field(default=None, ge=0)
    estimated_seconds_remaining: int | None = Field(default=None, ge=0)
    started_at: datetime | None
    completed_at: datetime | None
    heartbeat_at: datetime | None
    error_message: str | None
    download_ready: bool
    created_at: datetime
    tickers: list[HistoricalReplayTickerResponse] = Field(default_factory=list)


class HistoricalReplayJobListResponse(BaseModel):
    items: list[HistoricalReplayJobResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)

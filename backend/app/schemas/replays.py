from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


def _validate_window(start_date: date, end_date: date) -> None:
    today = date.today()
    if end_date < start_date:
        raise ValueError("تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
    if (end_date - start_date).days > 30:
        raise ValueError("الحد الأقصى لكل اختبار هو 31 يومًا")
    if end_date > today:
        raise ValueError("لا يمكن اختبار أيام مستقبلية")
    if start_date < today - timedelta(days=365 * 5 + 2):
        raise ValueError("الاختبار متاح لآخر خمس سنوات فقط")


class HistoricalReplayCreateRequest(BaseModel):
    request_key: str = Field(min_length=12, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    start_date: date
    end_date: date
    horizon_sessions: int = Field(default=5, ge=1, le=20)
    min_train_size: int = Field(default=200, ge=60, le=1000)
    neutral_band_pct: float = Field(default=1.0, ge=0, le=10)

    @model_validator(mode="after")
    def validate_range(self) -> HistoricalReplayCreateRequest:
        _validate_window(self.start_date, self.end_date)
        return self


class HistoricalReplayWindowRequest(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_range(self) -> HistoricalReplayWindowRequest:
        _validate_window(self.start_date, self.end_date)
        return self


class HistoricalReplayBatchCreateRequest(BaseModel):
    request_key_prefix: str = Field(
        min_length=8,
        max_length=48,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    windows: list[HistoricalReplayWindowRequest] = Field(min_length=2, max_length=12)
    horizon_sessions: int = Field(default=5, ge=1, le=20)
    min_train_size: int = Field(default=200, ge=60, le=1000)
    neutral_band_pct: float = Field(default=1.0, ge=0, le=10)

    @model_validator(mode="after")
    def validate_unique_windows(self) -> HistoricalReplayBatchCreateRequest:
        identities = {
            (window.start_date, window.end_date)
            for window in self.windows
        }
        if len(identities) != len(self.windows):
            raise ValueError("لا يمكن تكرار نفس الفترة داخل الدفعة")
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


class HistoricalReplayBatchCreateResponse(BaseModel):
    items: list[HistoricalReplayJobResponse]
    total: int = Field(ge=0)
    shared_history_cache: bool = True
    execution_order: str = "sequential_windows_shared_ticker_cache"


class HistoricalReplayJobListResponse(BaseModel):
    items: list[HistoricalReplayJobResponse]
    total: int = Field(ge=0)
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)

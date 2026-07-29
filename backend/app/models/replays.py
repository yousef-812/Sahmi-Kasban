from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AnalysisReplayJob(TimestampMixin, Base):
    __tablename__ = "analysis_replay_jobs"
    __table_args__ = (
        UniqueConstraint("request_key", name="uq_analysis_replay_jobs_request_key"),
        CheckConstraint(
            "status IN ('pending','running','complete','partial','failed')",
            name="analysis_replay_job_status_allowed",
        ),
        CheckConstraint("end_date >= start_date", name="analysis_replay_job_date_order"),
        CheckConstraint(
            "horizon_sessions BETWEEN 1 AND 20",
            name="analysis_replay_job_horizon_range",
        ),
        CheckConstraint(
            "parallelism BETWEEN 1 AND 5",
            name="analysis_replay_job_parallelism_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    request_key: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    engine_version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    horizon_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    min_train_size: Mapped[int] = mapped_column(Integer, nullable=False)
    neutral_band_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    parallelism: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    total_tickers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_tickers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_tickers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_tickers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evaluated_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(String(1000))
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class AnalysisReplayTicker(TimestampMixin, Base):
    __tablename__ = "analysis_replay_tickers"
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "ticker",
            name="uq_analysis_replay_tickers_job_ticker",
        ),
        CheckConstraint(
            "status IN ('pending','running','complete','partial','failed')",
            name="analysis_replay_ticker_status_allowed",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_replay_jobs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    data_fingerprint: Mapped[str | None] = mapped_column(String(128))
    candle_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_written: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evaluated_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(String(500))


class AnalysisReplayRow(TimestampMixin, Base):
    __tablename__ = "analysis_replay_rows"
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "ticker",
            "analysis_date",
            name="uq_analysis_replay_rows_job_ticker_date",
        ),
        CheckConstraint(
            "status IN ('evaluated','pending_evaluation','skipped','failed')",
            name="analysis_replay_row_status_allowed",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_replay_jobs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ticker_task_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_replay_tickers.id", ondelete="CASCADE"),
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    analysis_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    engine_version: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    data_fingerprint: Mapped[str | None] = mapped_column(String(128))
    data_as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    candle_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    signal: Mapped[str | None] = mapped_column(String(8))
    score_bp: Mapped[int | None] = mapped_column(Integer)
    confidence_bp: Mapped[int | None] = mapped_column(Integer)
    qualified: Mapped[bool | None] = mapped_column(Boolean)
    engines: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    trade_plan: Mapped[dict | None] = mapped_column(JSON)
    warnings: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    analysis_quality: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    entry: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    evaluation_date: Mapped[date | None] = mapped_column(Date)
    exit: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    forward_return_bp: Mapped[int | None] = mapped_column(Integer)
    max_upside_bp: Mapped[int | None] = mapped_column(Integer)
    max_drawdown_bp: Mapped[int | None] = mapped_column(Integer)
    correct: Mapped[bool | None] = mapped_column(Boolean)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(String(500))

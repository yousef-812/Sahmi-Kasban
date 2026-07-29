from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
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


class AnalysisBacktestRun(TimestampMixin, Base):
    __tablename__ = "analysis_backtest_runs"
    __table_args__ = (
        UniqueConstraint("request_key", name="uq_analysis_backtest_runs_request_key"),
        CheckConstraint(
            "status IN ('running', 'partial', 'complete', 'failed')",
            name="analysis_backtest_run_status_allowed",
        ),
        CheckConstraint(
            "min_train_size >= 60",
            name="analysis_backtest_run_min_train_size",
        ),
        CheckConstraint(
            "horizon_sessions > 0",
            name="analysis_backtest_run_horizon_positive",
        ),
        CheckConstraint(
            "step_sessions > 0",
            name="analysis_backtest_run_step_positive",
        ),
        CheckConstraint(
            "neutral_band_bp >= 0",
            name="analysis_backtest_run_neutral_band_non_negative",
        ),
        CheckConstraint(
            "total_tickers > 0",
            name="analysis_backtest_run_total_tickers_positive",
        ),
        CheckConstraint(
            "completed_tickers >= 0",
            name="analysis_backtest_run_completed_non_negative",
        ),
        CheckConstraint(
            "failed_tickers >= 0",
            name="analysis_backtest_run_failed_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    request_key: Mapped[str] = mapped_column(String(64), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    tickers: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    interval: Mapped[str] = mapped_column(String(16), nullable=False)
    min_train_size: Mapped[int] = mapped_column(Integer, nullable=False)
    horizon_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    step_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    neutral_band_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tickers: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_tickers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_tickers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    requested_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AnalysisBacktestResult(TimestampMixin, Base):
    __tablename__ = "analysis_backtest_results"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "ticker",
            name="uq_analysis_backtest_results_run_ticker",
        ),
        CheckConstraint(
            "status IN ('complete', 'failed')",
            name="analysis_backtest_result_status_allowed",
        ),
        CheckConstraint(
            "candle_count >= 0 AND observations >= 0",
            name="analysis_backtest_result_counts_non_negative",
        ),
        CheckConstraint(
            "buy_count >= 0 AND watch_count >= 0 AND avoid_count >= 0",
            name="analysis_backtest_result_signal_counts_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_backtest_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    data_fingerprint: Mapped[str | None] = mapped_column(String(128))
    data_as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    candle_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    observations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    buy_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watch_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avoid_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    directional_accuracy_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    buy_hit_rate_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avoid_hit_rate_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watch_hit_rate_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_forward_return_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    median_forward_return_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_buy_return_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_buy_max_drawdown_bp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profit_factor_milli: Mapped[int | None] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AnalysisBacktestObservation(TimestampMixin, Base):
    __tablename__ = "analysis_backtest_observations"
    __table_args__ = (
        UniqueConstraint(
            "result_id",
            "cutoff_index",
            name="uq_analysis_backtest_observations_result_cutoff",
        ),
        CheckConstraint(
            "signal IN ('BUY', 'WATCH', 'AVOID')",
            name="analysis_backtest_observation_signal_allowed",
        ),
        CheckConstraint(
            "cutoff_index >= 60",
            name="analysis_backtest_observation_cutoff_minimum",
        ),
        CheckConstraint(
            "score_bp BETWEEN 0 AND 10000",
            name="analysis_backtest_observation_score_range",
        ),
        CheckConstraint(
            "confidence_bp BETWEEN 0 AND 10000",
            name="analysis_backtest_observation_confidence_range",
        ),
        CheckConstraint(
            "entry > 0 AND exit > 0",
            name="analysis_backtest_observation_prices_positive",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    result_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_backtest_results.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    cutoff_index: Mapped[int] = mapped_column(Integer, nullable=False)
    data_as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    signal: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    score_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    entry: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    exit: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    forward_return_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_upside_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_drawdown_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

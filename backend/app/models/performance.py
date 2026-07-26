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


class MarketReportEvaluation(TimestampMixin, Base):
    __tablename__ = "market_report_evaluations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'partial', 'complete', 'failed')",
            name="market_report_evaluation_status_allowed",
        ),
        CheckConstraint(
            "attempt_count >= 0",
            name="market_report_evaluation_attempts_non_negative",
        ),
        CheckConstraint(
            "evaluated_count >= 0",
            name="market_report_evaluation_evaluated_non_negative",
        ),
        CheckConstraint(
            "pending_count >= 0",
            name="market_report_evaluation_pending_non_negative",
        ),
        CheckConstraint(
            "failed_count >= 0",
            name="market_report_evaluation_failed_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("market_reports.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    target_session_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(24),
        default="pending",
        index=True,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evaluated_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pending_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class MarketReportItemOutcome(TimestampMixin, Base):
    __tablename__ = "market_report_item_outcomes"
    __table_args__ = (
        UniqueConstraint(
            "report_id",
            "ticker",
            name="uq_report_item_outcome_report_ticker",
        ),
        CheckConstraint(
            "status IN ('pending_data', 'complete', 'failed')",
            name="market_report_item_outcome_status_allowed",
        ),
        CheckConstraint(
            "expected_direction IN ('up', 'down', 'neutral')",
            name="market_report_item_outcome_direction_allowed",
        ),
        CheckConstraint(
            "price_at_analysis > 0",
            name="market_report_item_outcome_price_positive",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    evaluation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("market_report_evaluations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("market_reports.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    report_item_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("market_report_items.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    target_session_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(24),
        default="pending_data",
        index=True,
        nullable=False,
    )
    expected_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    price_at_analysis: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    session_open: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    session_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    session_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    session_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    return_bp: Mapped[int | None] = mapped_column(Integer)
    max_upside_bp: Mapped[int | None] = mapped_column(Integer)
    max_drawdown_bp: Mapped[int | None] = mapped_column(Integer)
    direction_correct: Mapped[bool | None] = mapped_column(Boolean)
    target_one: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    target_two: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    stop_loss: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    target_one_hit: Mapped[bool | None] = mapped_column(Boolean)
    target_two_hit: Mapped[bool | None] = mapped_column(Boolean)
    stop_loss_hit: Mapped[bool | None] = mapped_column(Boolean)
    provider: Mapped[str | None] = mapped_column(String(80))
    data_fingerprint: Mapped[str | None] = mapped_column(String(128))
    data_as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evaluator_version: Mapped[str] = mapped_column(
        String(32),
        default="report-performance-v1",
        nullable=False,
    )
    evidence: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

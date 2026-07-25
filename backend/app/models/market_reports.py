from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class MarketScanRun(TimestampMixin, Base):
    __tablename__ = "market_scan_runs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    source_session_date: Mapped[date] = mapped_column(
        Date,
        unique=True,
        index=True,
        nullable=False,
    )
    target_session_date: Mapped[date | None] = mapped_column(Date, index=True)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    total_symbols: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    analyzed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    eligible_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class MarketReportUnlock(TimestampMixin, Base):
    __tablename__ = "market_report_unlocks"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "report_id",
            name="uq_market_report_unlock_user_report",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("market_reports.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    wallet_transaction_id: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

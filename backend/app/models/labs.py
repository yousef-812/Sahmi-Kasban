from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class LabsBacktestJob(TimestampMixin, Base):
    """A queued daily-report intraday backtest executed by the isolated replay worker.

    The worker (test machine) claims queued jobs and runs them away from the API
    process group that serves end users.
    """

    __tablename__ = "labs_backtest_jobs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','running','complete','failed')",
            name="labs_backtest_job_status_allowed",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="labs_backtest_job_date_order",
        ),
        CheckConstraint(
            "rank IS NULL OR rank BETWEEN 1 AND 10",
            name="labs_backtest_job_rank_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    requested_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer)
    exit_mode: Mapped[str] = mapped_column(String(16), nullable=False)
    result_json: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(String(1000))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import JSON, Date, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class EarningsCalendar(TimestampMixin, Base):
    """Scheduled earnings release for an EGX instrument.

    Rows are only ever written from a real market-data source; the endpoint
    reports ``available: false`` instead of fabricating dates when none exist.
    """

    __tablename__ = "earnings_calendar"
    __table_args__ = (
        UniqueConstraint(
            "ticker",
            "event_date",
            "period",
            name="uq_earnings_ticker_date_period",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    ticker: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    period: Mapped[str | None] = mapped_column(String(16), nullable=True)
    estimate_eps: Mapped[Decimal | None] = mapped_column(Numeric(16, 6), nullable=True)
    actual_eps: Mapped[Decimal | None] = mapped_column(Numeric(16, 6), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    raw: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

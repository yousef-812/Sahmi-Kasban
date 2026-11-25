from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Signal(Base):
    """Trade signal with lifecycle state machine (new->buy->t1done->...->closed)."""

    __tablename__ = "signals"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    ticker: Mapped[str] = mapped_column(String(24), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    entry: Mapped[Decimal] = mapped_column(Numeric(16, 6), nullable=False)
    stop: Mapped[Decimal] = mapped_column(Numeric(16, 6), nullable=False)
    t1: Mapped[Decimal] = mapped_column(Numeric(16, 6), nullable=False)
    t2: Mapped[Decimal | None] = mapped_column(Numeric(16, 6), nullable=True)
    t3: Mapped[Decimal | None] = mapped_column(Numeric(16, 6), nullable=True)
    state: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pnl_pct: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    source: Mapped[str] = mapped_column(String(24), nullable=False)
    ref_report_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    events: Mapped[list[SignalEvent]] = relationship(
        "SignalEvent", back_populates="signal", cascade="all, delete-orphan"
    )


class SignalEvent(Base):
    """Audit event emitted on every signal state transition."""

    __tablename__ = "signal_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    signal_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("signals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event: Mapped[str] = mapped_column(String(32), nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(16, 6), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )

    signal: Mapped[Signal] = relationship("Signal", back_populates="events")


class Alert(Base):
    """Per-user in-app alert (signal transitions, unlocks, etc.)."""

    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    ref_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )

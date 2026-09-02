from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class MarketInstrumentCatalog(TimestampMixin, Base):
    __tablename__ = "market_instrument_catalog"

    ticker: Mapped[str] = mapped_column(String(24), primary_key=True)
    provider_symbol: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    exchange: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    source: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)


class MarketDataSnapshot(TimestampMixin, Base):
    __tablename__ = "market_data_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "ticker",
            "provider",
            "interval",
            "period",
            name="uq_market_data_snapshot_identity",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    interval: Mapped[str] = mapped_column(String(16), nullable=False)
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    data_as_of: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    fingerprint: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    candle_count: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

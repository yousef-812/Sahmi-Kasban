from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.entities import User


class WatchlistItem(TimestampMixin, Base):
    """Per-user watchlist entry with cached signal snapshot."""

    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_watchlist_user_ticker"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), nullable=False)
    last_signal: Mapped[str | None] = mapped_column(String(16), nullable=True)
    last_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    last_price: Mapped[Decimal | None] = mapped_column(Numeric(16, 6), nullable=True)
    last_change_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped[User] = relationship("User", back_populates="watchlist_items")

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StockComparison(TimestampMixin, Base):
    __tablename__ = "stock_comparisons"
    __table_args__ = (
        UniqueConstraint("user_id", "request_key", name="uq_stock_comparison_user_request"),
        CheckConstraint("charged_points >= 0", name="stock_comparison_charge_non_negative"),
        CheckConstraint(
            "analysis_charged_points >= 0",
            name="stock_comparison_analysis_charge_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    request_key: Mapped[str] = mapped_column(String(64), nullable=False)
    tickers: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    analysis_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    plan_code: Mapped[str] = mapped_column(String(32), nullable=False)
    included_allowance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    charged_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    analysis_charged_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wallet_transaction_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

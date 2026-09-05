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
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BillingPurchase(TimestampMixin, Base):
    __tablename__ = "billing_purchases"
    __table_args__ = (
        UniqueConstraint(
            "purchase_token_hash",
            name="uq_billing_purchases_purchase_token_hash",
        ),
        CheckConstraint("quantity > 0", name="billing_purchase_quantity_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    platform: Mapped[str] = mapped_column(String(24), default="google_play", nullable=False)
    product_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    product_type: Mapped[str] = mapped_column(String(24), nullable=False)
    purchase_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    purchase_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    order_id: Mapped[str | None] = mapped_column(String(160), index=True)
    state: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    acknowledgement_state: Mapped[str] = mapped_column(String(24), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    linked_purchase_token_hash: Mapped[str | None] = mapped_column(String(64))
    wallet_transaction_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    subscription_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
    )
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RewardedAdSession(TimestampMixin, Base):
    __tablename__ = "rewarded_ad_sessions"
    __table_args__ = (
        UniqueConstraint(
            "custom_data_hash",
            name="uq_rewarded_ad_sessions_custom_data_hash",
        ),
        CheckConstraint(
            "ad_format IN ('rewarded', 'rewarded_interstitial')",
            name="rewarded_ad_sessions_ad_format_valid",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    custom_data_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ad_unit_id: Mapped[str] = mapped_column(String(160), nullable=False)
    ad_format: Mapped[str] = mapped_column(String(32), default="rewarded", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RewardedAdClaim(TimestampMixin, Base):
    __tablename__ = "rewarded_ad_claims"
    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            name="uq_rewarded_ad_claims_transaction_id",
        ),
        UniqueConstraint(
            "session_id",
            name="uq_rewarded_ad_claims_session_id",
        ),
        CheckConstraint("reported_reward_amount >= 0", name="ad_reward_amount_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("rewarded_ad_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_id: Mapped[str] = mapped_column(String(160), nullable=False)
    ad_network: Mapped[str] = mapped_column(String(80), nullable=False)
    ad_unit_id: Mapped[str] = mapped_column(String(160), nullable=False)
    reported_reward_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_item: Mapped[str] = mapped_column(String(80), nullable=False)
    callback_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cairo_reward_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    wallet_transaction_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class AdEventLog(TimestampMixin, Base):
    __tablename__ = "ad_event_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    ad_type: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    ad_unit_id: Mapped[str | None] = mapped_column(String(160))
    platform: Mapped[str] = mapped_column(String(24), default="android", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)

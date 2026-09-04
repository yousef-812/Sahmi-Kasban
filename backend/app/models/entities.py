from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.models.watchlist import WatchlistItem

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    avatar_key: Mapped[str] = mapped_column(String(80), default="avatar_01", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    auth_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    referral_code: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    referred_by_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    watchlist_items: Mapped[list[WatchlistItem]] = relationship(
        "WatchlistItem", back_populates="user", cascade="all, delete-orphan"
    )


class WalletEntry(TimestampMixin, Base):
    __tablename__ = "wallet_entries"
    __table_args__ = (CheckConstraint("amount_points <> 0", name="wallet_amount_non_zero"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    transaction_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    entry_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    amount_points: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="confirmed", nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50))
    reference_id: Mapped[str | None] = mapped_column(String(120))
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Subscription(TimestampMixin, Base):
    __tablename__ = "subscriptions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    plan_code: Mapped[str] = mapped_column(String(32), default="free", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="active", nullable=False)
    weekly_points: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    ads_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    purchase_token_hash: Mapped[str | None] = mapped_column(String(128), unique=True)


class MarketReport(TimestampMixin, Base):
    __tablename__ = "market_reports"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    target_session_date: Mapped[date] = mapped_column(Date, unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_snapshot: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    market_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    extended_universe: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class MarketReportItem(TimestampMixin, Base):
    __tablename__ = "market_report_items"
    __table_args__ = (
        UniqueConstraint("report_id", "ticker", name="uq_market_report_item_ticker"),
        UniqueConstraint("report_id", "rank", name="uq_market_report_item_rank"),
        CheckConstraint("rank BETWEEN 1 AND 10", name="market_report_rank_range"),
        CheckConstraint("score_bp BETWEEN 0 AND 10000", name="market_report_score_range"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("market_reports.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class StockAnalysis(TimestampMixin, Base):
    __tablename__ = "stock_analyses"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    data_as_of: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    cache_key: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="complete", nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class Discussion(TimestampMixin, Base):
    __tablename__ = "discussions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "submission_key",
            name="uq_discussions_user_submission",
        ),
        UniqueConstraint(
            "user_id",
            "content_fingerprint",
            name="uq_discussions_user_content_fingerprint",
        ),
        CheckConstraint(
            "period_type IN ('next_session', 'week', 'month')",
            name="discussion_period_type_allowed",
        ),
        CheckConstraint(
            "status IN ('pending_review', 'published', 'rejected', 'hidden')",
            name="discussion_status_allowed",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(24), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    period_type: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(
        String(24),
        default="pending_review",
        index=True,
        nullable=False,
    )
    submission_key: Mapped[str | None] = mapped_column(String(64))
    content_fingerprint: Mapped[str | None] = mapped_column(String(64))
    wallet_hold_transaction_id: Mapped[str | None] = mapped_column(
        String(120),
        unique=True,
    )
    moderation_result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    frozen_prediction: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    rejection_code: Mapped[str | None] = mapped_column(String(64))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PredictionVerification(TimestampMixin, Base):
    __tablename__ = "prediction_verifications"
    __table_args__ = (
        CheckConstraint("score_bp BETWEEN 0 AND 10000", name="prediction_score_range"),
        CheckConstraint("reward_points >= 0", name="prediction_reward_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    discussion_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discussions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    score_bp: Mapped[int] = mapped_column(Integer, nullable=False)
    strength: Mapped[str] = mapped_column(String(24), nullable=False)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

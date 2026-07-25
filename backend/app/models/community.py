from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class DiscussionReport(TimestampMixin, Base):
    __tablename__ = "discussion_reports"
    __table_args__ = (
        UniqueConstraint(
            "discussion_id",
            "reporter_id",
            name="uq_discussion_reports_discussion_reporter",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    discussion_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discussions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reporter_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reason_code: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="open", index=True, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    resolution_details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class UserMute(TimestampMixin, Base):
    __tablename__ = "user_mutes"
    __table_args__ = (
        UniqueConstraint(
            "muter_user_id",
            "muted_user_id",
            name="uq_user_mutes_muter_muted",
        ),
        CheckConstraint(
            "muter_user_id <> muted_user_id",
            name="user_mute_different_users",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    muter_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    muted_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class DiscussionModerationEvent(TimestampMixin, Base):
    __tablename__ = "discussion_moderation_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    discussion_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discussions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    actor_type: Mapped[str] = mapped_column(String(24), nullable=False)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    action: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class CommunityAdminEvent(TimestampMixin, Base):
    __tablename__ = "community_admin_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    target_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    discussion_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discussions.id", ondelete="SET NULL"),
        index=True,
    )
    action: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

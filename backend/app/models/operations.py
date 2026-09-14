from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StockAlgorithmicSignatureModel(TimestampMixin, Base):
    __tablename__ = "stock_algorithmic_signatures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    overall_quality_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    signature_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    ai_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    category: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    value: Mapped[object] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    updated_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )


class ServiceHealthEvent(TimestampMixin, Base):
    __tablename__ = "service_health_events"
    __table_args__ = (
        CheckConstraint(
            "status IN ('healthy', 'degraded', 'failed')",
            name="service_health_status_allowed",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    component: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PushDevice(TimestampMixin, Base):
    __tablename__ = "push_devices"
    __table_args__ = (
        CheckConstraint(
            "platform IN ('android', 'ios', 'web')",
            name="push_device_platform_allowed",
        ),
    )

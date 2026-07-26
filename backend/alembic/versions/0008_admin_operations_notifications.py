"""Add administration operations, runtime settings, and notifications.

Revision ID: 0008_admin_operations_notifications
Revises: 0007_community_appeals
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_admin_operations_notifications"
down_revision: str | None = "0007_community_appeals"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=False),
        sa.Column("updated_by_user_id", sa.Uuid(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["updated_by_user_id"],
            ["users.id"],
            name="fk_app_settings_updated_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("key", name="pk_app_settings"),
    )
    op.create_index("ix_app_settings_category", "app_settings", ["category"], unique=False)

    op.create_table(
        "service_health_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("component", sa.String(length=40), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('healthy', 'degraded', 'failed')",
            name="service_health_status_allowed",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_service_health_events"),
    )
    op.create_index(
        "ix_service_health_events_component",
        "service_health_events",
        ["component"],
        unique=False,
    )
    op.create_index(
        "ix_service_health_events_observed_at",
        "service_health_events",
        ["observed_at"],
        unique=False,
    )

    op.create_table(
        "push_devices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("encrypted_token", sa.String(length=2500), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.String(length=300), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "platform IN ('android', 'ios', 'web')",
            name="push_device_platform_allowed",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_push_devices_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_push_devices"),
        sa.UniqueConstraint("token_hash", name="uq_push_devices_token_hash"),
    )
    op.create_index("ix_push_devices_user_id", "push_devices", ["user_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.String(length=1000), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_notifications_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_read_at", "notifications", ["read_at"], unique=False)
    op.create_index("ix_notifications_sent_at", "notifications", ["sent_at"], unique=False)

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("push_device_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("provider_message_id", sa.String(length=300), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('sent', 'failed', 'skipped')",
            name="notification_delivery_status_allowed",
        ),
        sa.ForeignKeyConstraint(
            ["notification_id"],
            ["notifications.id"],
            name="fk_notification_deliveries_notification_id_notifications",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["push_device_id"],
            ["push_devices.id"],
            name="fk_notification_deliveries_push_device_id_push_devices",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notification_deliveries"),
        sa.UniqueConstraint(
            "notification_id",
            "push_device_id",
            name="uq_notification_delivery_notification_device",
        ),
    )
    op.create_index(
        "ix_notification_deliveries_notification_id",
        "notification_deliveries",
        ["notification_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_deliveries_notification_id",
        table_name="notification_deliveries",
    )
    op.drop_table("notification_deliveries")
    op.drop_index("ix_notifications_sent_at", table_name="notifications")
    op.drop_index("ix_notifications_read_at", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_push_devices_user_id", table_name="push_devices")
    op.drop_table("push_devices")
    op.drop_index(
        "ix_service_health_events_observed_at",
        table_name="service_health_events",
    )
    op.drop_index(
        "ix_service_health_events_component",
        table_name="service_health_events",
    )
    op.drop_table("service_health_events")
    op.drop_index("ix_app_settings_category", table_name="app_settings")
    op.drop_table("app_settings")

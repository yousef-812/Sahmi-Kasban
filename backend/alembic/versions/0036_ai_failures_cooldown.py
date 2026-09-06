"""Add ai_cooldown_until to users and create ai_failure_logs table.

Revision ID: 0036_ai_failures_cooldown
Revises: 0035_discussion_is_pinned
Create Date: 2026-09-06
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0036_ai_failures_cooldown"
down_revision: str | None = "0035_discussion_is_pinned"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "ai_cooldown_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_table(
        "ai_failure_logs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("user_name", sa.String(100), nullable=False),
        sa.Column("user_email", sa.String(255), nullable=False),
        sa.Column("ticker", sa.String(24), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("error_traceback", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("ai_failure_logs")
    op.drop_column("users", "ai_cooldown_until")

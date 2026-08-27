"""Add persistent authentication rate limits.

Revision ID: 0018_auth_rate_limits
Revises: 0017_account_token_attempts
Create Date: 2026-07-31
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0018_auth_rate_limits"
down_revision: str | None = "0017_account_token_attempts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "auth_rate_limits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "attempts > 0",
            name="auth_rate_limit_attempts_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "action",
            "key_hash",
            name="uq_auth_rate_limits_action_key",
        ),
    )
    op.create_index(
        op.f("ix_auth_rate_limits_action"),
        "auth_rate_limits",
        ["action"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_rate_limits_action"), table_name="auth_rate_limits")
    op.drop_table("auth_rate_limits")

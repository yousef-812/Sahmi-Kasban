"""Add user_follows table and tipping columns to users table.

Revision ID: 0030_user_follows_and_tipping
Revises: 0029_rewarded_ad_format
Create Date: 2026-09-06
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0030_user_follows_and_tipping"
down_revision: str | None = "0029_rewarded_ad_format"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add tipping columns to users
    op.add_column(
        "users",
        sa.Column("tipping_unlocked", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("tipping_enabled", sa.Boolean(), nullable=False, server_default="true"),
    )

    # Create user_follows table
    op.create_table(
        "user_follows",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "follower_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "following_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("follower_id", "following_id", name="uq_user_follows_follower_following"),
    )


def downgrade() -> None:
    op.drop_table("user_follows")
    op.drop_column("users", "tipping_enabled")
    op.drop_column("users", "tipping_unlocked")

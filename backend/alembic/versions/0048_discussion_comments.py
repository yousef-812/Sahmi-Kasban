"""Add discussion_comments table.

Revision ID: 0048_discussion_comments
Revises: 0047_news_resolved_url
Create Date: 2026-11-27
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0048_discussion_comments"
down_revision: str | Sequence[str] | None = "0047_news_resolved_url"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discussion_comments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "discussion_id",
            sa.Uuid(),
            sa.ForeignKey("discussions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            sa.Uuid(),
            sa.ForeignKey("discussion_comments.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("content", sa.String(500), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="visible"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('visible', 'hidden')",
            name="discussion_comment_status_allowed",
        ),
    )
    op.create_index("ix_discussion_comments_discussion_id", "discussion_comments", ["discussion_id"])
    op.create_index("ix_discussion_comments_user_id", "discussion_comments", ["user_id"])
    op.create_index("ix_discussion_comments_parent_id", "discussion_comments", ["parent_id"])


def downgrade() -> None:
    op.drop_index("ix_discussion_comments_parent_id", table_name="discussion_comments")
    op.drop_index("ix_discussion_comments_user_id", table_name="discussion_comments")
    op.drop_index("ix_discussion_comments_discussion_id", table_name="discussion_comments")
    op.drop_table("discussion_comments")

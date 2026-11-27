"""Add post_type to discussions (prediction | general).

Revision ID: 0049_discussion_post_type
Revises: 0048_discussion_comments
Create Date: 2026-11-27
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0049_discussion_post_type"
down_revision: str | Sequence[str] | None = "0048_discussion_comments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "discussions",
        sa.Column("post_type", sa.String(16), nullable=False, server_default="prediction"),
    )


def downgrade() -> None:
    op.drop_column("discussions", "post_type")

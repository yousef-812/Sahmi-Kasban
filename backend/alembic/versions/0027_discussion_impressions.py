"""0027 — Add discussion_impressions table for deduplicated view tracking.

Adds discussion_impressions table to track unique views per user and prevent fake view counts.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0027_discussion_impressions"
down_revision: str | None = "0026_views_and_reactions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discussion_impressions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "discussion_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("discussions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "discussion_id",
            name="uq_discussion_impressions_user_discussion",
        ),
    )
    op.create_index("ix_discussion_impressions_user_id", "discussion_impressions", ["user_id"])
    op.create_index("ix_discussion_impressions_discussion_id", "discussion_impressions", ["discussion_id"])


def downgrade() -> None:
    op.drop_index("ix_discussion_impressions_discussion_id", table_name="discussion_impressions")
    op.drop_index("ix_discussion_impressions_user_id", table_name="discussion_impressions")
    op.drop_table("discussion_impressions")

"""0026 — Add views_count to discussions and discussion_reactions table.

Adds views_count column to discussions table and creates discussion_reactions table for community reactions.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0026_views_and_reactions"
down_revision: str | None = "0025_referral_system"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "discussions",
        sa.Column("views_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table(
        "discussion_reactions",
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
        sa.Column("reaction_type", sa.String(24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "discussion_id",
            name="uq_discussion_reactions_user_discussion",
        ),
        sa.CheckConstraint(
            "reaction_type IN ('agree', 'disagree')",
            name="discussion_reaction_type_allowed",
        ),
    )
    op.create_index("ix_discussion_reactions_user_id", "discussion_reactions", ["user_id"])
    op.create_index("ix_discussion_reactions_discussion_id", "discussion_reactions", ["discussion_id"])


def downgrade() -> None:
    op.drop_index("ix_discussion_reactions_discussion_id", table_name="discussion_reactions")
    op.drop_index("ix_discussion_reactions_user_id", table_name="discussion_reactions")
    op.drop_table("discussion_reactions")
    op.drop_column("discussions", "views_count")

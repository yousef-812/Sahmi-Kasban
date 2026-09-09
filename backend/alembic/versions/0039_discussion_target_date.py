"""Add target_date column to discussions table and relax period_type constraint.

Revision ID: 0039_discussion_target_date
Revises: 0038_news_urls_text
Create Date: 2026-09-09
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0039_discussion_target_date"
down_revision: str | None = "0038_news_urls_text"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add target_date column
    op.add_column("discussions", sa.Column("target_date", sa.Date(), nullable=True))
    op.create_index(op.f("ix_discussions_target_date"), "discussions", ["target_date"])

    # Drop old period_type check constraint — use IF EXISTS so this is safe on
    # databases where the constraint was never created or already removed.
    op.execute(
        "ALTER TABLE discussions DROP CONSTRAINT IF EXISTS ck_discussions_discussion_period_type_allowed"
    )
    op.execute(
        "ALTER TABLE discussions DROP CONSTRAINT IF EXISTS discussion_period_type_allowed"
    )


def downgrade() -> None:
    with op.batch_alter_table("discussions") as batch_op:
        batch_op.create_check_constraint(
            "discussion_period_type_allowed",
            "period_type IN ('next_session', 'week', 'month')",
        )
    op.drop_index(op.f("ix_discussions_target_date"), table_name="discussions")
    op.drop_column("discussions", "target_date")

"""Add is_pinned column to discussions table.

Revision ID: 0035_discussion_is_pinned
Revises: 0034_purge_ai_personas
Create Date: 2026-09-06
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0035_discussion_is_pinned"
down_revision: str | None = "0034_purge_ai_personas"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "discussions",
        sa.Column(
            "is_pinned",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("discussions", "is_pinned")

"""Add sector_reports table.

Revision ID: 0032_sector_reports
Revises: 0031_coin_tips_history
Create Date: 2026-09-06
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0032_sector_reports"
down_revision: str | None = "0031_coin_tips_history"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sector_reports",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("sector_code", sa.String(length=64), nullable=False, index=True),
        sa.Column("target_date", sa.Date(), nullable=False, index=True),
        sa.Column("leader_ticker", sa.String(length=24), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
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
        sa.UniqueConstraint("sector_code", "target_date", name="uq_sector_reports_code_date"),
    )


def downgrade() -> None:
    op.drop_table("sector_reports")

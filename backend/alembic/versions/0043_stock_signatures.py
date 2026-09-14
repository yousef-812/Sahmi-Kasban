"""Add stock_algorithmic_signatures table for persistent stock signatures.

Revision ID: 0043_stock_signatures
Revises: 0042_drop_period_check
Create Date: 2026-09-14
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0043_stock_signatures"
down_revision: str | Sequence[str] | None = "0042_drop_period_check"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stock_algorithmic_signatures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("overall_quality_score", sa.Float(), nullable=False, server_default="50.0"),
        sa.Column("signature_data", sa.JSON(), nullable=False),
        sa.Column("ai_approved", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker"),
    )
    op.create_index(
        "ix_stock_algorithmic_signatures_ticker",
        "stock_algorithmic_signatures",
        ["ticker"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stock_algorithmic_signatures_ticker",
        table_name="stock_algorithmic_signatures",
    )
    op.drop_table("stock_algorithmic_signatures")

"""0044 — Scanner snapshots for persisted scanner output.

Revision ID: 0044_scanner_snapshots
Revises: 0043_stock_signatures
Create Date: 2026-10-12
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0044_scanner_snapshots"
down_revision: str | Sequence[str] | None = "0043_stock_signatures"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scanner_snapshots",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("symbol", sa.String(24), nullable=False),
        sa.Column("timeframe", sa.String(8), nullable=False, server_default="1D"),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("score", sa.Numeric(6, 2), nullable=True),
        sa.Column("rating", sa.String(16), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_scanner_snapshots_kind_symbol", "scanner_snapshots", ["kind", "symbol"]
    )
    op.create_index(
        "ix_scanner_snapshots_kind_as_of",
        "scanner_snapshots",
        ["kind", sa.text("as_of DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_scanner_snapshots_kind_as_of", table_name="scanner_snapshots")
    op.drop_index("ix_scanner_snapshots_kind_symbol", table_name="scanner_snapshots")
    op.drop_table("scanner_snapshots")

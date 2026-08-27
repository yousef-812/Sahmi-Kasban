"""0022 — Watchlist items for tracked instruments.

Adds a per-user watchlist with server-side signal caching so the mobile
terminal can render live BUY/WATCH/AVOID badges without re-running the
full analysis engine on every pull.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0022_watchlist"
down_revision: str | None = "0021_extended_universe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "watchlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("ticker", sa.String(24), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_signal", sa.String(16), nullable=True),
        sa.Column("last_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("last_price", sa.Numeric(16, 6), nullable=True),
        sa.Column("last_change_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("last_checked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "notes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.UniqueConstraint("user_id", "ticker", name="uq_watchlist_user_ticker"),
    )
    op.create_index("ix_watchlist_user_added", "watchlist_items", ["user_id", sa.text("created_at DESC")])


def downgrade() -> None:
    op.drop_index("ix_watchlist_user_added", table_name="watchlist_items")
    op.drop_table("watchlist_items")

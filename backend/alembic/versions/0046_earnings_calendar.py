"""0046 — Earnings calendar for scheduled EGX earnings releases.

Revision ID: 0046_earnings_calendar
Revises: 0045_signals_alerts
Create Date: 2026-10-14
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0046_earnings_calendar"
down_revision: str | Sequence[str] | None = "0045_signals_alerts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "earnings_calendar",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ticker", sa.String(24), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("period", sa.String(16), nullable=True),
        sa.Column("estimate_eps", sa.Numeric(16, 6), nullable=True),
        sa.Column("actual_eps", sa.Numeric(16, 6), nullable=True),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column(
            "raw",
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
        sa.UniqueConstraint(
            "ticker",
            "event_date",
            "period",
            name="uq_earnings_ticker_date_period",
        ),
    )
    op.create_index("ix_earnings_calendar_ticker", "earnings_calendar", ["ticker"])


def downgrade() -> None:
    op.drop_index("ix_earnings_calendar_ticker", table_name="earnings_calendar")
    op.drop_table("earnings_calendar")

"""0047 — Add resolved_url to news_articles for the final publisher URL after redirect resolution.

Revision ID: 0047_news_resolved_url
Revises: 0046_earnings_calendar
Create Date: 2026-10-14
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0047_news_resolved_url"
down_revision: str | Sequence[str] | None = "0046_earnings_calendar"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("news_articles") as batch_op:
        batch_op.add_column(sa.Column("resolved_url", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("news_articles") as batch_op:
        batch_op.drop_column("resolved_url")

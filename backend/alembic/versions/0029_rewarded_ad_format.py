"""Add ad_format column to rewarded_ad_sessions to distinguish rewarded vs rewarded_interstitial.

Revision ID: 0029_rewarded_ad_format
Revises: 0028_developer_feedbacks
Create Date: 2026-09-05
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0029_rewarded_ad_format"
down_revision: str | None = "0028_developer_feedbacks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "rewarded_ad_sessions",
        sa.Column(
            "ad_format",
            sa.String(length=32),
            nullable=False,
            server_default="rewarded",
        ),
    )
    op.create_check_constraint(
        "rewarded_ad_sessions_ad_format_valid",
        "rewarded_ad_sessions",
        "ad_format IN ('rewarded', 'rewarded_interstitial')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "rewarded_ad_sessions_ad_format_valid",
        "rewarded_ad_sessions",
        type_="check",
    )
    op.drop_column("rewarded_ad_sessions", "ad_format")

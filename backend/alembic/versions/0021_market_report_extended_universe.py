"""Add extended_universe JSON column to market reports.

Revision ID: 0021_market_report_extended_universe
Revises: 0020_labs_backtest_jobs
Create Date: 2026-08-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0021_market_report_extended_universe"
down_revision: str | None = "0020_labs_backtest_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "market_reports",
        sa.Column("extended_universe", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("market_reports", "extended_universe")

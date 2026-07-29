"""Increase plan grants for the launch economy.

Revision ID: 0013_economy_v2
Revises: 0012_analysis_access
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013_economy_v2"
down_revision: str | None = "0012_analysis_access"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_WEEKLY_POINTS = {
    "free": 500,
    "basic": 2_500,
    "advanced": 6_000,
    "pro": 15_000,
}

OLD_WEEKLY_POINTS = {
    "free": 300,
    "basic": 1_000,
    "advanced": 1_500,
    "pro": 5_000,
}


def _apply(values: dict[str, int]) -> None:
    subscriptions = sa.table(
        "subscriptions",
        sa.column("plan_code", sa.String()),
        sa.column("weekly_points", sa.Integer()),
    )
    for plan_code, weekly_points in values.items():
        op.execute(
            subscriptions.update()
            .where(subscriptions.c.plan_code == plan_code)
            .values(weekly_points=weekly_points)
        )


def upgrade() -> None:
    _apply(NEW_WEEKLY_POINTS)


def downgrade() -> None:
    _apply(OLD_WEEKLY_POINTS)

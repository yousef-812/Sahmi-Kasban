"""Persist per-user access to stock analyses.

Revision ID: 0012_analysis_access
Revises: 0011_market_catalog
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_analysis_access"
down_revision: str | None = "0011_market_catalog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_stock_analysis_access",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("last_viewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["stock_analyses.id"],
            name="fk_user_stock_analysis_access_analysis_id_stock_analyses",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_stock_analysis_access_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_stock_analysis_access"),
        sa.UniqueConstraint(
            "user_id",
            "analysis_id",
            name="uq_user_stock_analysis_access_user_analysis",
        ),
    )
    op.create_index(
        "ix_user_stock_analysis_access_user_id",
        "user_stock_analysis_access",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_stock_analysis_access_analysis_id",
        "user_stock_analysis_access",
        ["analysis_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_stock_analysis_access_ticker",
        "user_stock_analysis_access",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        "ix_user_stock_analysis_access_user_ticker",
        "user_stock_analysis_access",
        ["user_id", "ticker"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_stock_analysis_access_user_ticker",
        table_name="user_stock_analysis_access",
    )
    op.drop_index(
        "ix_user_stock_analysis_access_ticker",
        table_name="user_stock_analysis_access",
    )
    op.drop_index(
        "ix_user_stock_analysis_access_analysis_id",
        table_name="user_stock_analysis_access",
    )
    op.drop_index(
        "ix_user_stock_analysis_access_user_id",
        table_name="user_stock_analysis_access",
    )
    op.drop_table("user_stock_analysis_access")

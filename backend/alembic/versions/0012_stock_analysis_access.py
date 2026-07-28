"""Persist per-user stock analysis access.

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
        "stock_analysis_accesses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
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
            name="fk_stock_analysis_accesses_analysis_id_stock_analyses",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_stock_analysis_accesses_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_stock_analysis_accesses"),
        sa.UniqueConstraint(
            "user_id",
            "analysis_id",
            name="uq_stock_analysis_access_user_analysis",
        ),
        sa.UniqueConstraint(
            "wallet_transaction_id",
            name="uq_stock_analysis_accesses_wallet_transaction_id",
        ),
    )
    op.create_index(
        "ix_stock_analysis_accesses_user_id",
        "stock_analysis_accesses",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_stock_analysis_accesses_analysis_id",
        "stock_analysis_accesses",
        ["analysis_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stock_analysis_accesses_analysis_id",
        table_name="stock_analysis_accesses",
    )
    op.drop_index(
        "ix_stock_analysis_accesses_user_id",
        table_name="stock_analysis_accesses",
    )
    op.drop_table("stock_analysis_accesses")

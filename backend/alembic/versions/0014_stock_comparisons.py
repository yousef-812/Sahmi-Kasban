"""Create stock comparison records.

Revision ID: 0014_stock_comparisons
Revises: 0013_economy_v2
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0014_stock_comparisons"
down_revision: str | None = "0013_economy_v2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stock_comparisons",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("request_key", sa.String(length=64), nullable=False),
        sa.Column("tickers", sa.JSON(), nullable=False),
        sa.Column("analysis_ids", sa.JSON(), nullable=False),
        sa.Column("plan_code", sa.String(length=32), nullable=False),
        sa.Column("included_allowance", sa.Boolean(), nullable=False),
        sa.Column("charged_points", sa.Integer(), nullable=False),
        sa.Column("analysis_charged_points", sa.Integer(), nullable=False),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "analysis_charged_points >= 0",
            name="stock_comparison_analysis_charge_non_negative",
        ),
        sa.CheckConstraint(
            "charged_points >= 0",
            name="stock_comparison_charge_non_negative",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "request_key",
            name="uq_stock_comparison_user_request",
        ),
        sa.UniqueConstraint("wallet_transaction_id"),
    )
    op.create_index(
        op.f("ix_stock_comparisons_user_id"),
        "stock_comparisons",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_comparisons_user_id"), table_name="stock_comparisons")
    op.drop_table("stock_comparisons")

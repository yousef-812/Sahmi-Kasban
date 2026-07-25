"""Add daily market scan runs and report unlocks.

Revision ID: 0004_daily_market_reports
Revises: 0003_market_data_snapshots
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_daily_market_reports"
down_revision: str | None = "0003_market_data_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
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
    ]


def upgrade() -> None:
    op.create_table(
        "market_scan_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_session_date", sa.Date(), nullable=False),
        sa.Column("target_session_date", sa.Date(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("total_symbols", sa.Integer(), nullable=False),
        sa.Column("analyzed_count", sa.Integer(), nullable=False),
        sa.Column("eligible_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_market_scan_runs"),
        sa.UniqueConstraint(
            "source_session_date",
            name="uq_market_scan_runs_source_session_date",
        ),
    )
    op.create_index(
        "ix_market_scan_runs_source_session_date",
        "market_scan_runs",
        ["source_session_date"],
    )
    op.create_index(
        "ix_market_scan_runs_target_session_date",
        "market_scan_runs",
        ["target_session_date"],
    )
    op.create_index(
        "ix_market_scan_runs_status",
        "market_scan_runs",
        ["status"],
    )

    op.create_table(
        "market_report_unlocks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_market_report_unlocks_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["market_reports.id"],
            name="fk_market_report_unlocks_report_id_market_reports",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_market_report_unlocks"),
        sa.UniqueConstraint(
            "user_id",
            "report_id",
            name="uq_market_report_unlock_user_report",
        ),
        sa.UniqueConstraint(
            "wallet_transaction_id",
            name="uq_market_report_unlocks_wallet_transaction_id",
        ),
    )
    op.create_index(
        "ix_market_report_unlocks_user_id",
        "market_report_unlocks",
        ["user_id"],
    )
    op.create_index(
        "ix_market_report_unlocks_report_id",
        "market_report_unlocks",
        ["report_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_market_report_unlocks_report_id",
        table_name="market_report_unlocks",
    )
    op.drop_index(
        "ix_market_report_unlocks_user_id",
        table_name="market_report_unlocks",
    )
    op.drop_table("market_report_unlocks")

    op.drop_index("ix_market_scan_runs_status", table_name="market_scan_runs")
    op.drop_index(
        "ix_market_scan_runs_target_session_date",
        table_name="market_scan_runs",
    )
    op.drop_index(
        "ix_market_scan_runs_source_session_date",
        table_name="market_scan_runs",
    )
    op.drop_table("market_scan_runs")

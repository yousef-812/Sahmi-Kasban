"""Add queued daily-report backtest jobs executed by the replay worker.

Revision ID: 0020_labs_backtest_jobs
Revises: 0019_auth_rate_limits_defaults
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0020_labs_backtest_jobs"
down_revision: str | None = "0019_auth_rate_limits_defaults"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "labs_backtest_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("exit_mode", sa.String(length=16), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('queued','running','complete','failed')", name="labs_backtest_job_status_allowed"),
        sa.CheckConstraint("end_date >= start_date", name="labs_backtest_job_date_order"),
        sa.CheckConstraint("rank IS NULL OR rank BETWEEN 1 AND 10", name="labs_backtest_job_rank_range"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], name="fk_labs_backtest_jobs_requested_by_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_labs_backtest_jobs"),
    )
    op.create_index("ix_labs_backtest_jobs_requested_by", "labs_backtest_jobs", ["requested_by"])
    op.create_index("ix_labs_backtest_jobs_status", "labs_backtest_jobs", ["status"])
    op.create_index("ix_labs_backtest_jobs_created_at", "labs_backtest_jobs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_labs_backtest_jobs_created_at", table_name="labs_backtest_jobs")
    op.drop_index("ix_labs_backtest_jobs_status", table_name="labs_backtest_jobs")
    op.drop_index("ix_labs_backtest_jobs_requested_by", table_name="labs_backtest_jobs")
    op.drop_table("labs_backtest_jobs")

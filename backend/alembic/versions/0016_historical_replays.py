"""Add resumable historical engine replays.

Revision ID: 0016_historical_replays
Revises: 0015_backtest_performance
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016_historical_replays"
down_revision: str | None = "0015_backtest_performance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "analysis_replay_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("request_key", sa.String(length=64), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("engine_version", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("horizon_sessions", sa.Integer(), nullable=False),
        sa.Column("min_train_size", sa.Integer(), nullable=False),
        sa.Column("neutral_band_bp", sa.Integer(), nullable=False),
        sa.Column("parallelism", sa.Integer(), nullable=False),
        sa.Column("total_tickers", sa.Integer(), nullable=False),
        sa.Column("processed_tickers", sa.Integer(), nullable=False),
        sa.Column("successful_tickers", sa.Integer(), nullable=False),
        sa.Column("failed_tickers", sa.Integer(), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("evaluated_rows", sa.Integer(), nullable=False),
        sa.Column("pending_rows", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("status IN ('pending','running','complete','partial','failed')", name="analysis_replay_job_status_allowed"),
        sa.CheckConstraint("end_date >= start_date", name="analysis_replay_job_date_order"),
        sa.CheckConstraint("horizon_sessions BETWEEN 1 AND 20", name="analysis_replay_job_horizon_range"),
        sa.CheckConstraint("min_train_size >= 60", name="analysis_replay_job_train_minimum"),
        sa.CheckConstraint("neutral_band_bp >= 0", name="analysis_replay_job_band_non_negative"),
        sa.CheckConstraint("parallelism BETWEEN 1 AND 5", name="analysis_replay_job_parallelism_range"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], name="fk_analysis_replay_jobs_requested_by_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_replay_jobs"),
        sa.UniqueConstraint("request_key", name="uq_analysis_replay_jobs_request_key"),
    )
    op.create_index("ix_analysis_replay_jobs_requested_by", "analysis_replay_jobs", ["requested_by"])
    op.create_index("ix_analysis_replay_jobs_status", "analysis_replay_jobs", ["status"])
    op.create_index("ix_analysis_replay_jobs_created_at", "analysis_replay_jobs", ["created_at"])

    op.create_table(
        "analysis_replay_tickers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("data_fingerprint", sa.String(length=128), nullable=True),
        sa.Column("candle_count", sa.Integer(), nullable=False),
        sa.Column("rows_written", sa.Integer(), nullable=False),
        sa.Column("evaluated_rows", sa.Integer(), nullable=False),
        sa.Column("pending_rows", sa.Integer(), nullable=False),
        sa.Column("failed_rows", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        *_timestamps(),
        sa.CheckConstraint("status IN ('pending','running','complete','partial','failed')", name="analysis_replay_ticker_status_allowed"),
        sa.ForeignKeyConstraint(["job_id"], ["analysis_replay_jobs.id"], name="fk_analysis_replay_tickers_job_id_jobs", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_replay_tickers"),
        sa.UniqueConstraint("job_id", "ticker", name="uq_analysis_replay_tickers_job_ticker"),
    )
    op.create_index("ix_analysis_replay_tickers_job_id", "analysis_replay_tickers", ["job_id"])
    op.create_index("ix_analysis_replay_tickers_status", "analysis_replay_tickers", ["status"])

    op.create_table(
        "analysis_replay_rows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("ticker_task_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("analysis_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("engine_version", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("data_fingerprint", sa.String(length=128), nullable=True),
        sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=True),
        sa.Column("candle_count", sa.Integer(), nullable=False),
        sa.Column("signal", sa.String(length=8), nullable=True),
        sa.Column("score_bp", sa.Integer(), nullable=True),
        sa.Column("confidence_bp", sa.Integer(), nullable=True),
        sa.Column("qualified", sa.Boolean(), nullable=True),
        sa.Column("engines", sa.JSON(), nullable=False),
        sa.Column("trade_plan", sa.JSON(), nullable=True),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("analysis_quality", sa.JSON(), nullable=False),
        sa.Column("entry", sa.Numeric(18, 6), nullable=True),
        sa.Column("evaluation_date", sa.Date(), nullable=True),
        sa.Column("exit", sa.Numeric(18, 6), nullable=True),
        sa.Column("forward_return_bp", sa.Integer(), nullable=True),
        sa.Column("max_upside_bp", sa.Integer(), nullable=True),
        sa.Column("max_drawdown_bp", sa.Integer(), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        *_timestamps(),
        sa.CheckConstraint("status IN ('evaluated','pending_evaluation','skipped','failed')", name="analysis_replay_row_status_allowed"),
        sa.CheckConstraint("score_bp IS NULL OR score_bp BETWEEN 0 AND 10000", name="analysis_replay_row_score_range"),
        sa.CheckConstraint("confidence_bp IS NULL OR confidence_bp BETWEEN 0 AND 10000", name="analysis_replay_row_confidence_range"),
        sa.ForeignKeyConstraint(["job_id"], ["analysis_replay_jobs.id"], name="fk_analysis_replay_rows_job_id_jobs", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ticker_task_id"], ["analysis_replay_tickers.id"], name="fk_analysis_replay_rows_ticker_task_id_tickers", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_replay_rows"),
        sa.UniqueConstraint("job_id", "ticker", "analysis_date", name="uq_analysis_replay_rows_job_ticker_date"),
    )
    op.create_index("ix_analysis_replay_rows_job_id", "analysis_replay_rows", ["job_id"])
    op.create_index("ix_analysis_replay_rows_ticker", "analysis_replay_rows", ["ticker"])
    op.create_index("ix_analysis_replay_rows_analysis_date", "analysis_replay_rows", ["analysis_date"])
    op.create_index("ix_analysis_replay_rows_status", "analysis_replay_rows", ["status"])


def downgrade() -> None:
    op.drop_index("ix_analysis_replay_rows_status", table_name="analysis_replay_rows")
    op.drop_index("ix_analysis_replay_rows_analysis_date", table_name="analysis_replay_rows")
    op.drop_index("ix_analysis_replay_rows_ticker", table_name="analysis_replay_rows")
    op.drop_index("ix_analysis_replay_rows_job_id", table_name="analysis_replay_rows")
    op.drop_table("analysis_replay_rows")
    op.drop_index("ix_analysis_replay_tickers_status", table_name="analysis_replay_tickers")
    op.drop_index("ix_analysis_replay_tickers_job_id", table_name="analysis_replay_tickers")
    op.drop_table("analysis_replay_tickers")
    op.drop_index("ix_analysis_replay_jobs_created_at", table_name="analysis_replay_jobs")
    op.drop_index("ix_analysis_replay_jobs_status", table_name="analysis_replay_jobs")
    op.drop_index("ix_analysis_replay_jobs_requested_by", table_name="analysis_replay_jobs")
    op.drop_table("analysis_replay_jobs")

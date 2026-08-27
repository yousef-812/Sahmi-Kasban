"""Add persistent analysis backtest performance.

Revision ID: 0015_backtest_performance
Revises: 0014_stock_comparisons
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0015_backtest_performance"
down_revision: str | None = "0014_stock_comparisons"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
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
        "analysis_backtest_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("request_key", sa.String(length=64), nullable=False),
        sa.Column("engine_version", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("tickers", sa.JSON(), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("interval", sa.String(length=16), nullable=False),
        sa.Column("min_train_size", sa.Integer(), nullable=False),
        sa.Column("horizon_sessions", sa.Integer(), nullable=False),
        sa.Column("step_sessions", sa.Integer(), nullable=False),
        sa.Column("neutral_band_bp", sa.Integer(), nullable=False),
        sa.Column("total_tickers", sa.Integer(), nullable=False),
        sa.Column("completed_tickers", sa.Integer(), nullable=False),
        sa.Column("failed_tickers", sa.Integer(), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('running', 'partial', 'complete', 'failed')",
            name="analysis_backtest_run_status_allowed",
        ),
        sa.CheckConstraint(
            "min_train_size >= 60",
            name="analysis_backtest_run_min_train_size",
        ),
        sa.CheckConstraint(
            "horizon_sessions > 0",
            name="analysis_backtest_run_horizon_positive",
        ),
        sa.CheckConstraint(
            "step_sessions > 0",
            name="analysis_backtest_run_step_positive",
        ),
        sa.CheckConstraint(
            "neutral_band_bp >= 0",
            name="analysis_backtest_run_neutral_band_non_negative",
        ),
        sa.CheckConstraint(
            "total_tickers > 0",
            name="analysis_backtest_run_total_tickers_positive",
        ),
        sa.CheckConstraint(
            "completed_tickers >= 0",
            name="analysis_backtest_run_completed_non_negative",
        ),
        sa.CheckConstraint(
            "failed_tickers >= 0",
            name="analysis_backtest_run_failed_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by"],
            ["users.id"],
            name="fk_analysis_backtest_runs_requested_by_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_backtest_runs"),
        sa.UniqueConstraint(
            "request_key",
            name="uq_analysis_backtest_runs_request_key",
        ),
    )
    op.create_index(
        "ix_analysis_backtest_runs_engine_version",
        "analysis_backtest_runs",
        ["engine_version"],
        unique=False,
    )
    op.create_index(
        "ix_analysis_backtest_runs_status",
        "analysis_backtest_runs",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_analysis_backtest_runs_requested_by",
        "analysis_backtest_runs",
        ["requested_by"],
        unique=False,
    )

    op.create_table(
        "analysis_backtest_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("data_fingerprint", sa.String(length=128), nullable=True),
        sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=True),
        sa.Column("candle_count", sa.Integer(), nullable=False),
        sa.Column("observations", sa.Integer(), nullable=False),
        sa.Column("buy_count", sa.Integer(), nullable=False),
        sa.Column("watch_count", sa.Integer(), nullable=False),
        sa.Column("avoid_count", sa.Integer(), nullable=False),
        sa.Column("directional_accuracy_bp", sa.Integer(), nullable=False),
        sa.Column("buy_hit_rate_bp", sa.Integer(), nullable=False),
        sa.Column("avoid_hit_rate_bp", sa.Integer(), nullable=False),
        sa.Column("watch_hit_rate_bp", sa.Integer(), nullable=False),
        sa.Column("average_forward_return_bp", sa.Integer(), nullable=False),
        sa.Column("median_forward_return_bp", sa.Integer(), nullable=False),
        sa.Column("average_buy_return_bp", sa.Integer(), nullable=False),
        sa.Column("average_buy_max_drawdown_bp", sa.Integer(), nullable=False),
        sa.Column("profit_factor_milli", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('complete', 'failed')",
            name="analysis_backtest_result_status_allowed",
        ),
        sa.CheckConstraint(
            "candle_count >= 0 AND observations >= 0",
            name="analysis_backtest_result_counts_non_negative",
        ),
        sa.CheckConstraint(
            "buy_count >= 0 AND watch_count >= 0 AND avoid_count >= 0",
            name="analysis_backtest_result_signal_counts_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["analysis_backtest_runs.id"],
            name="fk_analysis_backtest_results_run_id_runs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_backtest_results"),
        sa.UniqueConstraint(
            "run_id",
            "ticker",
            name="uq_analysis_backtest_results_run_ticker",
        ),
    )
    op.create_index(
        "ix_analysis_backtest_results_run_id",
        "analysis_backtest_results",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        "ix_analysis_backtest_results_ticker",
        "analysis_backtest_results",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        "ix_analysis_backtest_results_status",
        "analysis_backtest_results",
        ["status"],
        unique=False,
    )

    op.create_table(
        "analysis_backtest_observations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("result_id", sa.Uuid(), nullable=False),
        sa.Column("cutoff_index", sa.Integer(), nullable=False),
        sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signal", sa.String(length=8), nullable=False),
        sa.Column("score_bp", sa.Integer(), nullable=False),
        sa.Column("confidence_bp", sa.Integer(), nullable=False),
        sa.Column("entry", sa.Numeric(18, 6), nullable=False),
        sa.Column("exit", sa.Numeric(18, 6), nullable=False),
        sa.Column("forward_return_bp", sa.Integer(), nullable=False),
        sa.Column("max_upside_bp", sa.Integer(), nullable=False),
        sa.Column("max_drawdown_bp", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "signal IN ('BUY', 'WATCH', 'AVOID')",
            name="analysis_backtest_observation_signal_allowed",
        ),
        sa.CheckConstraint(
            "cutoff_index >= 60",
            name="analysis_backtest_observation_cutoff_minimum",
        ),
        sa.CheckConstraint(
            "score_bp BETWEEN 0 AND 10000",
            name="analysis_backtest_observation_score_range",
        ),
        sa.CheckConstraint(
            "confidence_bp BETWEEN 0 AND 10000",
            name="analysis_backtest_observation_confidence_range",
        ),
        sa.CheckConstraint(
            "entry > 0 AND exit > 0",
            name="analysis_backtest_observation_prices_positive",
        ),
        sa.ForeignKeyConstraint(
            ["result_id"],
            ["analysis_backtest_results.id"],
            name="fk_analysis_backtest_observations_result_id_results",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_backtest_observations"),
        sa.UniqueConstraint(
            "result_id",
            "cutoff_index",
            name="uq_analysis_backtest_observations_result_cutoff",
        ),
    )
    op.create_index(
        "ix_analysis_backtest_observations_result_id",
        "analysis_backtest_observations",
        ["result_id"],
        unique=False,
    )
    op.create_index(
        "ix_analysis_backtest_observations_data_as_of",
        "analysis_backtest_observations",
        ["data_as_of"],
        unique=False,
    )
    op.create_index(
        "ix_analysis_backtest_observations_signal",
        "analysis_backtest_observations",
        ["signal"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_analysis_backtest_observations_signal",
        table_name="analysis_backtest_observations",
    )
    op.drop_index(
        "ix_analysis_backtest_observations_data_as_of",
        table_name="analysis_backtest_observations",
    )
    op.drop_index(
        "ix_analysis_backtest_observations_result_id",
        table_name="analysis_backtest_observations",
    )
    op.drop_table("analysis_backtest_observations")

    op.drop_index(
        "ix_analysis_backtest_results_status",
        table_name="analysis_backtest_results",
    )
    op.drop_index(
        "ix_analysis_backtest_results_ticker",
        table_name="analysis_backtest_results",
    )
    op.drop_index(
        "ix_analysis_backtest_results_run_id",
        table_name="analysis_backtest_results",
    )
    op.drop_table("analysis_backtest_results")

    op.drop_index(
        "ix_analysis_backtest_runs_requested_by",
        table_name="analysis_backtest_runs",
    )
    op.drop_index(
        "ix_analysis_backtest_runs_status",
        table_name="analysis_backtest_runs",
    )
    op.drop_index(
        "ix_analysis_backtest_runs_engine_version",
        table_name="analysis_backtest_runs",
    )
    op.drop_table("analysis_backtest_runs")

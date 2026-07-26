"""Add the daily report performance ledger.

Revision ID: 0009_report_performance
Revises: 0008_admin_ops_notifications
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_report_performance"
down_revision: str | None = "0008_admin_ops_notifications"
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
        "market_report_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("target_session_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("evaluated_count", sa.Integer(), nullable=False),
        sa.Column("pending_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'partial', 'complete', 'failed')",
            name="market_report_evaluation_status_allowed",
        ),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name="market_report_evaluation_attempts_non_negative",
        ),
        sa.CheckConstraint(
            "evaluated_count >= 0",
            name="market_report_evaluation_evaluated_non_negative",
        ),
        sa.CheckConstraint(
            "pending_count >= 0",
            name="market_report_evaluation_pending_non_negative",
        ),
        sa.CheckConstraint(
            "failed_count >= 0",
            name="market_report_evaluation_failed_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["market_reports.id"],
            name="fk_market_report_evaluations_report_id_market_reports",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_market_report_evaluations"),
        sa.UniqueConstraint("report_id", name="uq_market_report_evaluations_report_id"),
    )
    op.create_index(
        "ix_market_report_evaluations_report_id",
        "market_report_evaluations",
        ["report_id"],
        unique=True,
    )
    op.create_index(
        "ix_market_report_evaluations_target_session_date",
        "market_report_evaluations",
        ["target_session_date"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_evaluations_status",
        "market_report_evaluations",
        ["status"],
        unique=False,
    )

    op.create_table(
        "market_report_item_outcomes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("report_item_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("target_session_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("expected_direction", sa.String(length=16), nullable=False),
        sa.Column("price_at_analysis", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("session_open", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("session_high", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("session_low", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("session_close", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("return_bp", sa.Integer(), nullable=True),
        sa.Column("max_upside_bp", sa.Integer(), nullable=True),
        sa.Column("max_drawdown_bp", sa.Integer(), nullable=True),
        sa.Column("direction_correct", sa.Boolean(), nullable=True),
        sa.Column("target_one", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("target_two", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("stop_loss", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("target_one_hit", sa.Boolean(), nullable=True),
        sa.Column("target_two_hit", sa.Boolean(), nullable=True),
        sa.Column("stop_loss_hit", sa.Boolean(), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("data_fingerprint", sa.String(length=128), nullable=True),
        sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evaluator_version", sa.String(length=32), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('pending_data', 'complete', 'failed')",
            name="market_report_item_outcome_status_allowed",
        ),
        sa.CheckConstraint(
            "expected_direction IN ('up', 'down', 'neutral')",
            name="market_report_item_outcome_direction_allowed",
        ),
        sa.CheckConstraint(
            "price_at_analysis > 0",
            name="market_report_item_outcome_price_positive",
        ),
        sa.ForeignKeyConstraint(
            ["evaluation_id"],
            ["market_report_evaluations.id"],
            name="fk_report_item_outcomes_evaluation_id_evaluations",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["market_reports.id"],
            name="fk_report_item_outcomes_report_id_market_reports",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["report_item_id"],
            ["market_report_items.id"],
            name="fk_report_item_outcomes_report_item_id_market_report_items",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_market_report_item_outcomes"),
        sa.UniqueConstraint("report_item_id", name="uq_market_report_item_outcomes_report_item_id"),
        sa.UniqueConstraint(
            "report_id",
            "ticker",
            name="uq_report_item_outcome_report_ticker",
        ),
    )
    op.create_index(
        "ix_market_report_item_outcomes_evaluation_id",
        "market_report_item_outcomes",
        ["evaluation_id"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_item_outcomes_report_id",
        "market_report_item_outcomes",
        ["report_id"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_item_outcomes_report_item_id",
        "market_report_item_outcomes",
        ["report_item_id"],
        unique=True,
    )
    op.create_index(
        "ix_market_report_item_outcomes_ticker",
        "market_report_item_outcomes",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_item_outcomes_target_session_date",
        "market_report_item_outcomes",
        ["target_session_date"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_item_outcomes_status",
        "market_report_item_outcomes",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_market_report_item_outcomes_status", table_name="market_report_item_outcomes")
    op.drop_index(
        "ix_market_report_item_outcomes_target_session_date",
        table_name="market_report_item_outcomes",
    )
    op.drop_index("ix_market_report_item_outcomes_ticker", table_name="market_report_item_outcomes")
    op.drop_index(
        "ix_market_report_item_outcomes_report_item_id",
        table_name="market_report_item_outcomes",
    )
    op.drop_index("ix_market_report_item_outcomes_report_id", table_name="market_report_item_outcomes")
    op.drop_index(
        "ix_market_report_item_outcomes_evaluation_id",
        table_name="market_report_item_outcomes",
    )
    op.drop_table("market_report_item_outcomes")
    op.drop_index("ix_market_report_evaluations_status", table_name="market_report_evaluations")
    op.drop_index(
        "ix_market_report_evaluations_target_session_date",
        table_name="market_report_evaluations",
    )
    op.drop_index("ix_market_report_evaluations_report_id", table_name="market_report_evaluations")
    op.drop_table("market_report_evaluations")

"""Create the foundational application schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
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
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        sa.Column("avatar_key", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "market_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("target_session_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_snapshot", sa.JSON(), nullable=False),
        sa.Column("market_summary", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_market_reports"),
    )
    op.create_index(
        "ix_market_reports_target_session_date",
        "market_reports",
        ["target_session_date"],
        unique=True,
    )

    op.create_table(
        "stock_analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cache_key", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name="pk_stock_analyses"),
        sa.UniqueConstraint("cache_key", name="uq_stock_analyses_cache_key"),
    )
    op.create_index("ix_stock_analyses_ticker", "stock_analyses", ["ticker"], unique=False)
    op.create_index(
        "ix_stock_analyses_data_as_of",
        "stock_analyses",
        ["data_as_of"],
        unique=False,
    )

    op.create_table(
        "wallet_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.String(length=120), nullable=False),
        sa.Column("entry_type", sa.String(length=50), nullable=False),
        sa.Column("amount_points", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.String(length=120), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("amount_points <> 0", name="ck_wallet_entries_wallet_amount_non_zero"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_wallet_entries_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_wallet_entries"),
        sa.UniqueConstraint("transaction_id", name="uq_wallet_entries_transaction_id"),
    )
    op.create_index("ix_wallet_entries_user_id", "wallet_entries", ["user_id"], unique=False)
    op.create_index(
        "ix_wallet_entries_entry_type",
        "wallet_entries",
        ["entry_type"],
        unique=False,
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plan_code", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("weekly_points", sa.Integer(), nullable=False),
        sa.Column("ads_enabled", sa.Boolean(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purchase_token_hash", sa.String(length=128), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_subscriptions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_subscriptions"),
        sa.UniqueConstraint(
            "purchase_token_hash",
            name="uq_subscriptions_purchase_token_hash",
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=False)

    op.create_table(
        "market_report_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score_bp", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "rank BETWEEN 1 AND 10",
            name="ck_market_report_items_market_report_rank_range",
        ),
        sa.CheckConstraint(
            "score_bp BETWEEN 0 AND 10000",
            name="ck_market_report_items_market_report_score_range",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["market_reports.id"],
            name="fk_market_report_items_report_id_market_reports",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_market_report_items"),
        sa.UniqueConstraint(
            "report_id",
            "ticker",
            name="uq_market_report_item_ticker",
        ),
        sa.UniqueConstraint(
            "report_id",
            "rank",
            name="uq_market_report_item_rank",
        ),
    )
    op.create_index(
        "ix_market_report_items_report_id",
        "market_report_items",
        ["report_id"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_items_ticker",
        "market_report_items",
        ["ticker"],
        unique=False,
    )

    op.create_table(
        "discussions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("content", sa.String(length=5000), nullable=False),
        sa.Column("period_type", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("moderation_result", sa.JSON(), nullable=False),
        sa.Column("frozen_prediction", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_discussions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_discussions"),
    )
    op.create_index("ix_discussions_user_id", "discussions", ["user_id"], unique=False)
    op.create_index("ix_discussions_ticker", "discussions", ["ticker"], unique=False)
    op.create_index("ix_discussions_status", "discussions", ["status"], unique=False)

    op.create_table(
        "prediction_verifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("discussion_id", sa.Uuid(), nullable=False),
        sa.Column("score_bp", sa.Integer(), nullable=False),
        sa.Column("strength", sa.String(length=24), nullable=False),
        sa.Column("reward_points", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "score_bp BETWEEN 0 AND 10000",
            name="ck_prediction_verifications_prediction_score_range",
        ),
        sa.CheckConstraint(
            "reward_points >= 0",
            name="ck_prediction_verifications_prediction_reward_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["discussion_id"],
            ["discussions.id"],
            name="fk_prediction_verifications_discussion_id_discussions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_prediction_verifications"),
        sa.UniqueConstraint(
            "discussion_id",
            name="uq_prediction_verifications_discussion_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("prediction_verifications")

    op.drop_index("ix_discussions_status", table_name="discussions")
    op.drop_index("ix_discussions_ticker", table_name="discussions")
    op.drop_index("ix_discussions_user_id", table_name="discussions")
    op.drop_table("discussions")

    op.drop_index("ix_market_report_items_ticker", table_name="market_report_items")
    op.drop_index("ix_market_report_items_report_id", table_name="market_report_items")
    op.drop_table("market_report_items")

    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_wallet_entries_entry_type", table_name="wallet_entries")
    op.drop_index("ix_wallet_entries_user_id", table_name="wallet_entries")
    op.drop_table("wallet_entries")

    op.drop_index("ix_stock_analyses_data_as_of", table_name="stock_analyses")
    op.drop_index("ix_stock_analyses_ticker", table_name="stock_analyses")
    op.drop_table("stock_analyses")

    op.drop_index("ix_market_reports_target_session_date", table_name="market_reports")
    op.drop_table("market_reports")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

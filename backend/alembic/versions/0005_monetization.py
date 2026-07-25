"""Add billing purchases and rewarded-ad verification records.

Revision ID: 0005_monetization
Revises: 0004_daily_market_reports
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_monetization"
down_revision: str | None = "0004_daily_market_reports"
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
        "billing_purchases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=24), nullable=False),
        sa.Column("product_id", sa.String(length=120), nullable=False),
        sa.Column("product_type", sa.String(length=24), nullable=False),
        sa.Column("purchase_token_hash", sa.String(length=64), nullable=False),
        sa.Column("purchase_token_encrypted", sa.Text(), nullable=False),
        sa.Column("order_id", sa.String(length=160), nullable=True),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("acknowledgement_state", sa.String(length=24), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("linked_purchase_token_hash", sa.String(length=64), nullable=True),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=True),
        sa.Column("subscription_id", sa.Uuid(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_billing_purchases_billing_purchase_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            name="fk_billing_purchases_subscription_id_subscriptions",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_billing_purchases_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_billing_purchases"),
        sa.UniqueConstraint(
            "purchase_token_hash",
            name="uq_billing_purchases_purchase_token_hash",
        ),
        sa.UniqueConstraint(
            "wallet_transaction_id",
            name="uq_billing_purchases_wallet_transaction_id",
        ),
    )
    op.create_index("ix_billing_purchases_user_id", "billing_purchases", ["user_id"])
    op.create_index("ix_billing_purchases_product_id", "billing_purchases", ["product_id"])
    op.create_index("ix_billing_purchases_order_id", "billing_purchases", ["order_id"])
    op.create_index("ix_billing_purchases_state", "billing_purchases", ["state"])
    op.create_index("ix_billing_purchases_expires_at", "billing_purchases", ["expires_at"])

    op.create_table(
        "rewarded_ad_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("custom_data_hash", sa.String(length=64), nullable=False),
        sa.Column("ad_unit_id", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_rewarded_ad_sessions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_rewarded_ad_sessions"),
        sa.UniqueConstraint(
            "custom_data_hash",
            name="uq_rewarded_ad_sessions_custom_data_hash",
        ),
    )
    op.create_index("ix_rewarded_ad_sessions_user_id", "rewarded_ad_sessions", ["user_id"])
    op.create_index("ix_rewarded_ad_sessions_status", "rewarded_ad_sessions", ["status"])
    op.create_index("ix_rewarded_ad_sessions_expires_at", "rewarded_ad_sessions", ["expires_at"])

    op.create_table(
        "rewarded_ad_claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("transaction_id", sa.String(length=160), nullable=False),
        sa.Column("ad_network", sa.String(length=80), nullable=False),
        sa.Column("ad_unit_id", sa.String(length=160), nullable=False),
        sa.Column("reported_reward_amount", sa.Integer(), nullable=False),
        sa.Column("reward_item", sa.String(length=80), nullable=False),
        sa.Column("callback_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cairo_reward_date", sa.Date(), nullable=False),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "reported_reward_amount >= 0",
            name="ck_rewarded_ad_claims_ad_reward_amount_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["rewarded_ad_sessions.id"],
            name="fk_rewarded_ad_claims_session_id_rewarded_ad_sessions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_rewarded_ad_claims_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_rewarded_ad_claims"),
        sa.UniqueConstraint("session_id", name="uq_rewarded_ad_claims_session_id"),
        sa.UniqueConstraint("transaction_id", name="uq_rewarded_ad_claims_transaction_id"),
        sa.UniqueConstraint(
            "wallet_transaction_id",
            name="uq_rewarded_ad_claims_wallet_transaction_id",
        ),
    )
    op.create_index("ix_rewarded_ad_claims_user_id", "rewarded_ad_claims", ["user_id"])
    op.create_index(
        "ix_rewarded_ad_claims_cairo_reward_date",
        "rewarded_ad_claims",
        ["cairo_reward_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_rewarded_ad_claims_cairo_reward_date",
        table_name="rewarded_ad_claims",
    )
    op.drop_index("ix_rewarded_ad_claims_user_id", table_name="rewarded_ad_claims")
    op.drop_table("rewarded_ad_claims")

    op.drop_index("ix_rewarded_ad_sessions_expires_at", table_name="rewarded_ad_sessions")
    op.drop_index("ix_rewarded_ad_sessions_status", table_name="rewarded_ad_sessions")
    op.drop_index("ix_rewarded_ad_sessions_user_id", table_name="rewarded_ad_sessions")
    op.drop_table("rewarded_ad_sessions")

    op.drop_index("ix_billing_purchases_expires_at", table_name="billing_purchases")
    op.drop_index("ix_billing_purchases_state", table_name="billing_purchases")
    op.drop_index("ix_billing_purchases_order_id", table_name="billing_purchases")
    op.drop_index("ix_billing_purchases_product_id", table_name="billing_purchases")
    op.drop_index("ix_billing_purchases_user_id", table_name="billing_purchases")
    op.drop_table("billing_purchases")

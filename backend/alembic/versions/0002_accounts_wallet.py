"""Add authentication sessions, account tokens, and wallet accounts.

Revision ID: 0002_accounts_wallet
Revises: 0001_initial_schema
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_accounts_wallet"
down_revision: str | None = "0001_initial_schema"
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
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True)))
    op.add_column(
        "users",
        sa.Column("auth_version", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True)))

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("user_agent", sa.String(length=500)),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_auth_sessions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_auth_sessions"),
        sa.UniqueConstraint(
            "refresh_token_hash",
            name="uq_auth_sessions_refresh_token_hash",
        ),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])

    op.create_table(
        "account_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_account_tokens_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_account_tokens"),
        sa.UniqueConstraint("token_hash", name="uq_account_tokens_token_hash"),
    )
    op.create_index("ix_account_tokens_user_id", "account_tokens", ["user_id"])
    op.create_index("ix_account_tokens_token_type", "account_tokens", ["token_type"])
    op.create_index("ix_account_tokens_expires_at", "account_tokens", ["expires_at"])

    op.create_table(
        "wallet_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("balance_points", sa.Integer(), server_default="0", nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "balance_points >= 0",
            name="ck_wallet_accounts_wallet_balance_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_wallet_accounts_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_wallet_accounts"),
        sa.UniqueConstraint("user_id", name="uq_wallet_accounts_user_id"),
    )
    op.create_index("ix_wallet_accounts_user_id", "wallet_accounts", ["user_id"])

    op.create_table(
        "weekly_grants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("subscription_id", sa.Uuid(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("plan_code", sa.String(length=32), nullable=False),
        sa.Column("amount_points", sa.Integer(), nullable=False),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint(
            "amount_points > 0",
            name="ck_weekly_grants_weekly_grant_amount_positive",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            name="fk_weekly_grants_subscription_id_subscriptions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_weekly_grants_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_weekly_grants"),
        sa.UniqueConstraint(
            "user_id",
            "week_start",
            name="uq_weekly_grants_user_week",
        ),
        sa.UniqueConstraint(
            "wallet_transaction_id",
            name="uq_weekly_grants_wallet_transaction_id",
        ),
    )
    op.create_index("ix_weekly_grants_user_id", "weekly_grants", ["user_id"])
    op.create_index("ix_weekly_grants_week_start", "weekly_grants", ["week_start"])


def downgrade() -> None:
    op.drop_index("ix_weekly_grants_week_start", table_name="weekly_grants")
    op.drop_index("ix_weekly_grants_user_id", table_name="weekly_grants")
    op.drop_table("weekly_grants")

    op.drop_index("ix_wallet_accounts_user_id", table_name="wallet_accounts")
    op.drop_table("wallet_accounts")

    op.drop_index("ix_account_tokens_expires_at", table_name="account_tokens")
    op.drop_index("ix_account_tokens_token_type", table_name="account_tokens")
    op.drop_index("ix_account_tokens_user_id", table_name="account_tokens")
    op.drop_table("account_tokens")

    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_column("users", "deleted_at")
    op.drop_column("users", "auth_version")
    op.drop_column("users", "email_verified_at")

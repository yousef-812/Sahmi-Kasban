"""Add normalized market-data snapshot cache.

Revision ID: 0003_market_data_snapshots
Revises: 0002_accounts_wallet
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_market_data_snapshots"
down_revision: str | None = "0002_accounts_wallet"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "market_data_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("interval", sa.String(length=16), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("candle_count", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_market_data_snapshots"),
        sa.UniqueConstraint(
            "ticker",
            "provider",
            "interval",
            "period",
            name="uq_market_data_snapshot_identity",
        ),
    )
    op.create_index(
        "ix_market_data_snapshots_ticker",
        "market_data_snapshots",
        ["ticker"],
    )
    op.create_index(
        "ix_market_data_snapshots_data_as_of",
        "market_data_snapshots",
        ["data_as_of"],
    )
    op.create_index(
        "ix_market_data_snapshots_expires_at",
        "market_data_snapshots",
        ["expires_at"],
    )
    op.create_index(
        "ix_market_data_snapshots_fingerprint",
        "market_data_snapshots",
        ["fingerprint"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_market_data_snapshots_fingerprint",
        table_name="market_data_snapshots",
    )
    op.drop_index(
        "ix_market_data_snapshots_expires_at",
        table_name="market_data_snapshots",
    )
    op.drop_index(
        "ix_market_data_snapshots_data_as_of",
        table_name="market_data_snapshots",
    )
    op.drop_index(
        "ix_market_data_snapshots_ticker",
        table_name="market_data_snapshots",
    )
    op.drop_table("market_data_snapshots")
"""Add the persistent EGX market instrument catalog.

Revision ID: 0011_market_catalog
Revises: 0010_perf_experience
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_market_catalog"
down_revision: str | None = "0010_perf_experience"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "market_instrument_catalog",
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("provider_symbol", sa.String(length=64), nullable=False),
        sa.Column("exchange", sa.String(length=24), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.PrimaryKeyConstraint("ticker", name="pk_market_instrument_catalog"),
        sa.UniqueConstraint(
            "provider_symbol",
            name="uq_market_instrument_catalog_provider_symbol",
        ),
    )
    op.create_index(
        "ix_market_instrument_catalog_provider_symbol",
        "market_instrument_catalog",
        ["provider_symbol"],
        unique=True,
    )
    op.create_index(
        "ix_market_instrument_catalog_exchange",
        "market_instrument_catalog",
        ["exchange"],
        unique=False,
    )
    op.create_index(
        "ix_market_instrument_catalog_source",
        "market_instrument_catalog",
        ["source"],
        unique=False,
    )
    op.create_index(
        "ix_market_instrument_catalog_active",
        "market_instrument_catalog",
        ["active"],
        unique=False,
    )
    op.create_index(
        "ix_market_instrument_catalog_last_seen_at",
        "market_instrument_catalog",
        ["last_seen_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_market_instrument_catalog_last_seen_at",
        table_name="market_instrument_catalog",
    )
    op.drop_index(
        "ix_market_instrument_catalog_active",
        table_name="market_instrument_catalog",
    )
    op.drop_index(
        "ix_market_instrument_catalog_source",
        table_name="market_instrument_catalog",
    )
    op.drop_index(
        "ix_market_instrument_catalog_exchange",
        table_name="market_instrument_catalog",
    )
    op.drop_index(
        "ix_market_instrument_catalog_provider_symbol",
        table_name="market_instrument_catalog",
    )
    op.drop_table("market_instrument_catalog")

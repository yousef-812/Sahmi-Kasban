"""Add per-user stock-analysis access records.

Revision ID: 0012_analysis_access
Revises: 0011_market_catalog
Create Date: 2026-07-28
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0012_analysis_access"
down_revision: str | None = "0011_market_catalog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    access_table = op.create_table(
        "stock_analysis_access",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=False),
        sa.Column("wallet_transaction_id", sa.String(length=120), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.ForeignKeyConstraint(["analysis_id"], ["stock_analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_stock_analysis_access"),
        sa.UniqueConstraint(
            "user_id",
            "analysis_id",
            name="uq_stock_analysis_access_user_analysis",
        ),
        sa.UniqueConstraint(
            "wallet_transaction_id",
            name="uq_stock_analysis_access_wallet_transaction_id",
        ),
    )
    op.create_index(
        "ix_stock_analysis_access_user_id",
        "stock_analysis_access",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_stock_analysis_access_analysis_id",
        "stock_analysis_access",
        ["analysis_id"],
        unique=False,
    )

    bind = op.get_bind()
    analysis_ids = {
        str(row[0])
        for row in bind.execute(sa.text("SELECT id FROM stock_analyses")).all()
    }
    legacy_debits = bind.execute(
        sa.text(
            """
            SELECT user_id, reference_id, transaction_id,
                   COALESCE(confirmed_at, created_at) AS unlocked_at
            FROM wallet_entries
            WHERE entry_type = 'stock_analysis_debit'
              AND reference_type = 'stock_analysis'
              AND reference_id IS NOT NULL
            """
        )
    ).mappings()
    now = datetime.now(UTC)
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for debit in legacy_debits:
        reference_id = str(debit["reference_id"])
        try:
            analysis_id = UUID(reference_id)
        except ValueError:
            continue
        if str(analysis_id) not in analysis_ids:
            continue
        key = (str(debit["user_id"]), str(analysis_id))
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "id": uuid4(),
                "user_id": debit["user_id"],
                "analysis_id": analysis_id,
                "wallet_transaction_id": str(debit["transaction_id"]),
                "unlocked_at": debit["unlocked_at"] or now,
                "created_at": debit["unlocked_at"] or now,
                "updated_at": debit["unlocked_at"] or now,
            }
        )
    if rows:
        op.bulk_insert(access_table, rows)


def downgrade() -> None:
    op.drop_index(
        "ix_stock_analysis_access_analysis_id",
        table_name="stock_analysis_access",
    )
    op.drop_index(
        "ix_stock_analysis_access_user_id",
        table_name="stock_analysis_access",
    )
    op.drop_table("stock_analysis_access")

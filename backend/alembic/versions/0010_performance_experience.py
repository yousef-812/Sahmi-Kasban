"""Add audited performance outcome revisions.

Revision ID: 0010_perf_experience
Revises: 0009_report_performance
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_perf_experience"
down_revision: str | None = "0009_report_performance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "market_report_outcome_revisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("outcome_id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("before_payload", sa.JSON(), nullable=False),
        sa.Column("after_payload", sa.JSON(), nullable=False),
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
        sa.CheckConstraint(
            "revision_number > 0",
            name="market_report_outcome_revision_positive",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_perf_revision_actor_user",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["outcome_id"],
            ["market_report_item_outcomes.id"],
            name="fk_perf_revision_outcome",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["market_reports.id"],
            name="fk_perf_revision_report",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_market_report_outcome_revisions"),
        sa.UniqueConstraint(
            "outcome_id",
            "revision_number",
            name="uq_market_report_outcome_revision_number",
        ),
    )
    op.create_index(
        "ix_market_report_outcome_revisions_outcome_id",
        "market_report_outcome_revisions",
        ["outcome_id"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_outcome_revisions_report_id",
        "market_report_outcome_revisions",
        ["report_id"],
        unique=False,
    )
    op.create_index(
        "ix_market_report_outcome_revisions_actor_user_id",
        "market_report_outcome_revisions",
        ["actor_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_market_report_outcome_revisions_actor_user_id",
        table_name="market_report_outcome_revisions",
    )
    op.drop_index(
        "ix_market_report_outcome_revisions_report_id",
        table_name="market_report_outcome_revisions",
    )
    op.drop_index(
        "ix_market_report_outcome_revisions_outcome_id",
        table_name="market_report_outcome_revisions",
    )
    op.drop_table("market_report_outcome_revisions")

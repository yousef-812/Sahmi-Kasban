"""Add developer feedbacks table.

Revision ID: 0028_developer_feedbacks
Revises: 0027_discussion_impressions
Create Date: 2026-09-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0028_developer_feedbacks"
down_revision: str | None = "0027_discussion_impressions"
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
        "developer_feedbacks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("message", sa.String(length=4000), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="new"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", sa.Uuid(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "status IN ('new', 'reviewed', 'resolved', 'archived')",
            name="developer_feedback_status_allowed",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_developer_feedbacks_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by_user_id"],
            ["users.id"],
            name="fk_developer_feedbacks_reviewed_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_developer_feedbacks"),
    )
    op.create_index(
        "ix_developer_feedbacks_user_id",
        "developer_feedbacks",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_developer_feedbacks_status",
        "developer_feedbacks",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_developer_feedbacks_status", table_name="developer_feedbacks")
    op.drop_index("ix_developer_feedbacks_user_id", table_name="developer_feedbacks")
    op.drop_table("developer_feedbacks")

"""Add one-time discussion appeals.

Revision ID: 0007_community_appeals
Revises: 0006_community_core
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_community_appeals"
down_revision: str | None = "0006_community_core"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "discussion_appeals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("discussion_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("source_status", sa.String(length=24), nullable=False),
        sa.Column("message", sa.String(length=2000), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("resolution_reason_code", sa.String(length=64), nullable=True),
        sa.Column("resolution_details", sa.JSON(), nullable=False),
        sa.Column("publish_transaction_id", sa.String(length=120), nullable=True),
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
            "status IN ('open', 'accepted', 'rejected')",
            name="ck_discussion_appeals_discussion_appeal_status_allowed",
        ),
        sa.CheckConstraint(
            "source_status IN ('rejected', 'hidden')",
            name="ck_discussion_appeals_discussion_appeal_source_status_allowed",
        ),
        sa.ForeignKeyConstraint(
            ["discussion_id"],
            ["discussions.id"],
            name="fk_discussion_appeals_discussion_id_discussions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_discussion_appeals_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by_user_id"],
            ["users.id"],
            name="fk_discussion_appeals_resolved_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_discussion_appeals"),
        sa.UniqueConstraint(
            "discussion_id",
            name="uq_discussion_appeals_discussion",
        ),
        sa.UniqueConstraint(
            "publish_transaction_id",
            name="uq_discussion_appeals_publish_transaction_id",
        ),
    )
    op.create_index(
        "ix_discussion_appeals_discussion_id",
        "discussion_appeals",
        ["discussion_id"],
    )
    op.create_index(
        "ix_discussion_appeals_user_id",
        "discussion_appeals",
        ["user_id"],
    )
    op.create_index(
        "ix_discussion_appeals_status",
        "discussion_appeals",
        ["status"],
    )
    op.create_index(
        "ix_discussion_appeals_resolved_by_user_id",
        "discussion_appeals",
        ["resolved_by_user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_discussion_appeals_resolved_by_user_id",
        table_name="discussion_appeals",
    )
    op.drop_index("ix_discussion_appeals_status", table_name="discussion_appeals")
    op.drop_index("ix_discussion_appeals_user_id", table_name="discussion_appeals")
    op.drop_index("ix_discussion_appeals_discussion_id", table_name="discussion_appeals")
    op.drop_table("discussion_appeals")

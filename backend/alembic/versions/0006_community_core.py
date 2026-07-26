"""Add community moderation, reports, and user mutes.

Revision ID: 0006_community_core
Revises: 0005_monetization
Create Date: 2026-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_community_core"
down_revision: str | None = "0005_monetization"
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
    with op.batch_alter_table("discussions") as batch:
        batch.add_column(sa.Column("submission_key", sa.String(length=64), nullable=True))
        batch.add_column(
            sa.Column("content_fingerprint", sa.String(length=64), nullable=True)
        )
        batch.add_column(
            sa.Column(
                "wallet_hold_transaction_id",
                sa.String(length=120),
                nullable=True,
            )
        )
        batch.add_column(sa.Column("rejection_code", sa.String(length=64), nullable=True))
        batch.add_column(
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch.add_column(sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_unique_constraint(
            "uq_discussions_user_submission",
            ["user_id", "submission_key"],
        )
        batch.create_unique_constraint(
            "uq_discussions_user_content_fingerprint",
            ["user_id", "content_fingerprint"],
        )
        batch.create_unique_constraint(
            "uq_discussions_wallet_hold_transaction_id",
            ["wallet_hold_transaction_id"],
        )
        batch.create_check_constraint(
            "ck_discussions_discussion_period_type_allowed",
            "period_type IN ('next_session', 'week', 'month')",
        )
        batch.create_check_constraint(
            "ck_discussions_discussion_status_allowed",
            "status IN ('pending_review', 'published', 'rejected', 'hidden')",
        )

    op.create_index(
        "ix_discussions_published_at",
        "discussions",
        ["published_at"],
        unique=False,
    )
    op.create_index(
        "ix_discussions_user_created_at",
        "discussions",
        ["user_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "discussion_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("discussion_id", sa.Uuid(), nullable=False),
        sa.Column("reporter_id", sa.Uuid(), nullable=False),
        sa.Column("reason_code", sa.String(length=50), nullable=False),
        sa.Column("details", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("resolution_details", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["discussion_id"],
            ["discussions.id"],
            name="fk_discussion_reports_discussion_id_discussions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reporter_id"],
            ["users.id"],
            name="fk_discussion_reports_reporter_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_by_user_id"],
            ["users.id"],
            name="fk_discussion_reports_resolved_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_discussion_reports"),
        sa.UniqueConstraint(
            "discussion_id",
            "reporter_id",
            name="uq_discussion_reports_discussion_reporter",
        ),
    )
    op.create_index(
        "ix_discussion_reports_discussion_id",
        "discussion_reports",
        ["discussion_id"],
    )
    op.create_index(
        "ix_discussion_reports_reporter_id",
        "discussion_reports",
        ["reporter_id"],
    )
    op.create_index(
        "ix_discussion_reports_status",
        "discussion_reports",
        ["status"],
    )

    op.create_table(
        "user_mutes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("muter_user_id", sa.Uuid(), nullable=False),
        sa.Column("muted_user_id", sa.Uuid(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "muter_user_id <> muted_user_id",
            name="ck_user_mutes_user_mute_different_users",
        ),
        sa.ForeignKeyConstraint(
            ["muter_user_id"],
            ["users.id"],
            name="fk_user_mutes_muter_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["muted_user_id"],
            ["users.id"],
            name="fk_user_mutes_muted_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_mutes"),
        sa.UniqueConstraint(
            "muter_user_id",
            "muted_user_id",
            name="uq_user_mutes_muter_muted",
        ),
    )
    op.create_index("ix_user_mutes_muter_user_id", "user_mutes", ["muter_user_id"])
    op.create_index("ix_user_mutes_muted_user_id", "user_mutes", ["muted_user_id"])

    op.create_table(
        "discussion_moderation_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("discussion_id", sa.Uuid(), nullable=False),
        sa.Column("actor_type", sa.String(length=24), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["discussion_id"],
            ["discussions.id"],
            name="fk_discussion_moderation_events_discussion_id_discussions",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_discussion_moderation_events_actor_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_discussion_moderation_events"),
    )
    op.create_index(
        "ix_discussion_moderation_events_discussion_id",
        "discussion_moderation_events",
        ["discussion_id"],
    )
    op.create_index(
        "ix_discussion_moderation_events_actor_user_id",
        "discussion_moderation_events",
        ["actor_user_id"],
    )
    op.create_index(
        "ix_discussion_moderation_events_action",
        "discussion_moderation_events",
        ["action"],
    )

    op.create_table(
        "community_admin_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("target_user_id", sa.Uuid(), nullable=True),
        sa.Column("discussion_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_community_admin_events_actor_user_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"],
            ["users.id"],
            name="fk_community_admin_events_target_user_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["discussion_id"],
            ["discussions.id"],
            name="fk_community_admin_events_discussion_id_discussions",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_community_admin_events"),
    )
    op.create_index(
        "ix_community_admin_events_actor_user_id",
        "community_admin_events",
        ["actor_user_id"],
    )
    op.create_index(
        "ix_community_admin_events_target_user_id",
        "community_admin_events",
        ["target_user_id"],
    )
    op.create_index(
        "ix_community_admin_events_discussion_id",
        "community_admin_events",
        ["discussion_id"],
    )
    op.create_index(
        "ix_community_admin_events_action",
        "community_admin_events",
        ["action"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_community_admin_events_action",
        table_name="community_admin_events",
    )
    op.drop_index(
        "ix_community_admin_events_discussion_id",
        table_name="community_admin_events",
    )
    op.drop_index(
        "ix_community_admin_events_target_user_id",
        table_name="community_admin_events",
    )
    op.drop_index(
        "ix_community_admin_events_actor_user_id",
        table_name="community_admin_events",
    )
    op.drop_table("community_admin_events")

    op.drop_index(
        "ix_discussion_moderation_events_action",
        table_name="discussion_moderation_events",
    )
    op.drop_index(
        "ix_discussion_moderation_events_actor_user_id",
        table_name="discussion_moderation_events",
    )
    op.drop_index(
        "ix_discussion_moderation_events_discussion_id",
        table_name="discussion_moderation_events",
    )
    op.drop_table("discussion_moderation_events")

    op.drop_index("ix_user_mutes_muted_user_id", table_name="user_mutes")
    op.drop_index("ix_user_mutes_muter_user_id", table_name="user_mutes")
    op.drop_table("user_mutes")

    op.drop_index("ix_discussion_reports_status", table_name="discussion_reports")
    op.drop_index("ix_discussion_reports_reporter_id", table_name="discussion_reports")
    op.drop_index("ix_discussion_reports_discussion_id", table_name="discussion_reports")
    op.drop_table("discussion_reports")

    op.drop_index("ix_discussions_user_created_at", table_name="discussions")
    op.drop_index("ix_discussions_published_at", table_name="discussions")
    with op.batch_alter_table("discussions") as batch:
        batch.drop_constraint(
            "ck_discussions_discussion_status_allowed",
            type_="check",
        )
        batch.drop_constraint(
            "ck_discussions_discussion_period_type_allowed",
            type_="check",
        )
        batch.drop_constraint(
            "uq_discussions_wallet_hold_transaction_id",
            type_="unique",
        )
        batch.drop_constraint(
            "uq_discussions_user_content_fingerprint",
            type_="unique",
        )
        batch.drop_constraint(
            "uq_discussions_user_submission",
            type_="unique",
        )
        batch.drop_column("hidden_at")
        batch.drop_column("reviewed_at")
        batch.drop_column("rejection_code")
        batch.drop_column("wallet_hold_transaction_id")
        batch.drop_column("content_fingerprint")
        batch.drop_column("submission_key")

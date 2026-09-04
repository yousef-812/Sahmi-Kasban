"""0025 — Add referral code and referred_by_id to users table.

Adds referral_code and referred_by_id columns to users table for referral reward system.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0025_referral_system"
down_revision: str | None = "0024_ai_community_personas"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("referral_code", sa.String(32), nullable=True))
    op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)
    op.add_column(
        "users",
        sa.Column(
            "referred_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "referred_by_id")
    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_column("users", "referral_code")

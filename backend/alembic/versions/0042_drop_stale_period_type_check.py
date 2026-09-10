"""Drop stale period_type check constraint missed by 0039.

Migration 0039 dropped `ck_discussions_discussion_period_type_allowed` and
`discussion_period_type_allowed`, but the constraint actually present in the
database carries a doubled prefix produced by the naming convention:
`ck_discussions_ck_discussions_discussion_period_type_allowed`.

As long as it exists, valid ISO-date period_type values (e.g. "2026-09-15",
sent by PredictionDateDropdown) fail with a 500 CheckViolation even though
the service layer accepts them. Drop every known variant defensively.

Revision ID: 0042_drop_stale_period_type_check
Revises: 0041_merge_heads
Create Date: 2026-09-10
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0042_drop_stale_period_type_check"
down_revision: str | None = "0041_merge_heads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE discussions DROP CONSTRAINT IF EXISTS "
        "ck_discussions_ck_discussions_discussion_period_type_allowed"
    )
    op.execute(
        "ALTER TABLE discussions DROP CONSTRAINT IF EXISTS "
        "ck_discussions_discussion_period_type_allowed"
    )
    op.execute(
        "ALTER TABLE discussions DROP CONSTRAINT IF EXISTS "
        "discussion_period_type_allowed"
    )


def downgrade() -> None:
    # Do not recreate: ISO-date period_type values are the supported format.
    pass

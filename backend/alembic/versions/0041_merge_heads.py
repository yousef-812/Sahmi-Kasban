"""merge heads after the unified profile migration

Revision ID: 0041_merge_heads
Revises: 0039_discussion_target_date, 0040_user_profile_bio
Create Date: 2026-09-09

"""
from __future__ import annotations

from collections.abc import Sequence

revision: str = "0041_merge_heads"
down_revision: str | Sequence[str] | None = (
    "0039_discussion_target_date",
    "0040_user_profile_bio",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
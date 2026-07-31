"""Track failed account-token attempts.

Revision ID: 0015_account_token_attempts
Revises: 0014_stock_comparisons
Create Date: 2026-07-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015_account_token_attempts"
down_revision: str | None = "0014_stock_comparisons"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "account_tokens",
        sa.Column(
            "failed_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "account_token_failed_attempts_non_negative",
        "account_tokens",
        "failed_attempts >= 0",
    )
    op.alter_column("account_tokens", "failed_attempts", server_default=None)


def downgrade() -> None:
    op.drop_constraint(
        "account_token_failed_attempts_non_negative",
        "account_tokens",
        type_="check",
    )
    op.drop_column("account_tokens", "failed_attempts")

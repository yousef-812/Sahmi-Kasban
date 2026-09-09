"""Add content column to news_articles for full article body.

Revision ID: 0039_news_article_content
Revises: 0038_news_urls_text
Create Date: 2026-09-09
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0039_news_article_content"
down_revision: str | None = "0038_news_urls_text"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("news_articles") as batch_op:
        batch_op.add_column(
            sa.Column("content", sa.Text(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("news_articles") as batch_op:
        batch_op.drop_column("content")
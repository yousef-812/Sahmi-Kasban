"""Alter news_articles url and image_url columns to Text.

Revision ID: 0038_news_urls_text
Revises: 0037_news_articles
Create Date: 2026-09-08
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0038_news_urls_text"
down_revision: str | None = "0037_news_articles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("news_articles") as batch_op:
        batch_op.alter_column(
            "url",
            type_=sa.Text(),
            existing_type=sa.String(length=1000),
            nullable=False,
        )
        batch_op.alter_column(
            "image_url",
            type_=sa.Text(),
            existing_type=sa.String(length=1000),
            nullable=True,
        )
        batch_op.alter_column(
            "title",
            type_=sa.String(length=1000),
            existing_type=sa.String(length=400),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("news_articles") as batch_op:
        batch_op.alter_column(
            "url",
            type_=sa.String(length=1000),
            existing_type=sa.Text(),
            nullable=False,
        )
        batch_op.alter_column(
            "image_url",
            type_=sa.String(length=1000),
            existing_type=sa.Text(),
            nullable=True,
        )
        batch_op.alter_column(
            "title",
            type_=sa.String(length=400),
            existing_type=sa.String(length=1000),
            nullable=False,
        )

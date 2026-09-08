"""Add news_articles and news_article_tickers tables.

Revision ID: 0037_news_articles
Revises: 0036_ai_failures_cooldown
Create Date: 2026-09-08
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0037_news_articles"
down_revision: str | None = "0036_ai_failures_cooldown"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "news_articles",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=400), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("source_name", sa.String(length=100), nullable=False),
        sa.Column("source_key", sa.String(length=40), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sentiment", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_articles")),
        sa.UniqueConstraint("url", name=op.f("uq_news_articles_url")),
    )
    op.create_index(op.f("ix_news_articles_is_active"), "news_articles", ["is_active"])
    op.create_index(op.f("ix_news_articles_published_at"), "news_articles", ["published_at"])
    op.create_index(op.f("ix_news_articles_sentiment"), "news_articles", ["sentiment"])
    op.create_index(op.f("ix_news_articles_source_key"), "news_articles", ["source_key"])

    op.create_table(
        "news_article_tickers",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("article_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("ticker", sa.String(length=24), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["article_id"],
            ["news_articles.id"],
            name=op.f("fk_news_article_tickers_article_id_news_articles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_article_tickers")),
        sa.UniqueConstraint(
            "article_id", "ticker", name="uq_news_article_tickers_article_id_ticker"
        ),
    )
    op.create_index(op.f("ix_news_article_tickers_article_id"), "news_article_tickers", ["article_id"])
    op.create_index(op.f("ix_news_article_tickers_ticker"), "news_article_tickers", ["ticker"])


def downgrade() -> None:
    op.drop_index(op.f("ix_news_article_tickers_ticker"), table_name="news_article_tickers")
    op.drop_index(op.f("ix_news_article_tickers_article_id"), table_name="news_article_tickers")
    op.drop_table("news_article_tickers")

    op.drop_index(op.f("ix_news_articles_source_key"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_sentiment"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_published_at"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_is_active"), table_name="news_articles")
    op.drop_table("news_articles")

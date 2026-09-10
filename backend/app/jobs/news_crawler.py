"""Scheduler لجلب الأخبار المالية من مصادر RSS كل 15 دقيقة تلقائياً."""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.market_data import MarketInstrumentCatalog
from app.models.news import NewsArticle
from app.services.news import (
    RSS_SOURCES,
    fetch_article_content_and_resolve,
    fetch_rss_source,
    save_articles_to_db,
)

logger = logging.getLogger(__name__)

_CRAWL_INTERVAL_SECONDS = 900  # 15 دقيقة
_CONTENT_FETCH_CONCURRENCY = 8


def _get_known_tickers(db) -> frozenset[str]:
    """جلب كل التيكرات النشطة من الـ DB."""
    rows = db.execute(
        select(MarketInstrumentCatalog.ticker).where(MarketInstrumentCatalog.active == True)  # noqa: E712
    ).scalars().all()
    return frozenset(rows)


async def _extract_contents(articles: list[dict]) -> None:
    """استخراج المحتوى الكامل للمقالات الجديدة بالتوازي مع حد أقصى للتوازي.

    كذلك يفك روابط Google News الوسيطة للوصول لرابط المقال الأصلي.
    """
    semaphore = asyncio.Semaphore(_CONTENT_FETCH_CONCURRENCY)

    async def _extract_one(article: dict) -> None:
        async with semaphore:
            content, resolved = await fetch_article_content_and_resolve(article["url"])
            article["content"] = content
            if resolved and resolved != article["url"]:
                article["url"] = resolved

    await asyncio.gather(*(_extract_one(a) for a in articles), return_exceptions=True)


async def run_news_crawl_once() -> int:
    """تشغيل دورة جلب أخبار واحدة من كل المصادر. يرجع عدد الأخبار الجديدة."""
    logger.info("News crawler: starting crawl cycle across %d sources", len(RSS_SOURCES))

    # جلب كل المصادر بالتوازي
    tasks = [fetch_rss_source(source) for source in RSS_SOURCES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_articles: list[dict] = []
    for source, result in zip(RSS_SOURCES, results, strict=False):
        if isinstance(result, Exception):
            logger.warning("News crawler: source %s failed: %s", source["key"], result)
        elif isinstance(result, list):
            all_articles.extend(result)

    if not all_articles:
        logger.info("News crawler: no articles fetched this cycle")
        return 0

    # حفظ في الـ DB
    try:
        with SessionLocal() as db:
            known_tickers = _get_known_tickers(db)

            # جلب المحتوى الكامل فقط للمقالات الجديدة (غير المخزنة)
            urls = [a["url"] for a in all_articles]
            existing_urls = set(
                db.execute(
                    select(NewsArticle.url).where(NewsArticle.url.in_(urls))
                ).scalars().all()
            )
            new_articles = [a for a in all_articles if a["url"] not in existing_urls]
            await _extract_contents(new_articles)
            logger.info(
                "News crawler: extracting full content for %d new articles",
                len(new_articles),
            )

            saved = save_articles_to_db(db, all_articles, known_tickers)
            logger.info(
                "News crawler: cycle complete — fetched=%d new=%d",
                len(all_articles),
                saved,
            )
            return saved
    except Exception:
        logger.exception("News crawler: DB save failed")
        return 0


async def run_news_crawler_scheduler() -> None:
    """Loop دائم يشغّل الـ crawler كل 15 دقيقة."""
    # انتظار قليل عند البداية حتى تنتهي warmup tasks الأخرى
    await asyncio.sleep(30)

    while True:
        try:
            await run_news_crawl_once()
        except Exception:
            logger.exception("News crawler: unexpected error in scheduler loop")
        await asyncio.sleep(_CRAWL_INTERVAL_SECONDS)

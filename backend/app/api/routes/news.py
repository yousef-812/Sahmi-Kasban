"""API endpoints للأخبار المالية."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentAdmin, get_db
from app.jobs.news_crawler import run_news_crawl_once
from app.schemas.news import NewsArticleResponse, NewsListResponse
from app.services.news import get_article_by_id, get_latest_news, get_stock_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=NewsListResponse, summary="آخر الأخبار المالية")
def list_news(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    source_key: str | None = Query(default=None),
    sentiment: str | None = Query(default=None),
    q: str | None = Query(default=None, description="البحث في الأخبار باسم الشركة، التيكر، أو الكلمات المفتاحية"),
    db: Session = Depends(get_db),
) -> NewsListResponse:
    """جلب آخر الأخبار المالية (عامة) مع فلترة اختيارية بالمصدر، الـ sentiment، أو بحث الكلمات المفتاحية."""
    return get_latest_news(
        db,
        limit=limit,
        offset=offset,
        source_key=source_key,
        sentiment=sentiment,
        q=q,
    )


@router.get("/{article_id}", response_model=NewsArticleResponse, summary="تفاصيل خبر")
def get_news_article(
    article_id: UUID,
    db: Session = Depends(get_db),
) -> NewsArticleResponse:
    """جلب تفاصيل خبر معين بالـ ID."""
    article = get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الخبر غير موجود")
    return article


# endpoint أخبار السهم — مُسجَّل في market router لكن خدمته هنا
stock_news_router = APIRouter(tags=["news"])


@stock_news_router.get(
    "/stocks/{ticker}/news",
    response_model=NewsListResponse,
    summary="أخبار سهم معين",
)
def get_stock_news_endpoint(
    ticker: str,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> NewsListResponse:
    """جلب أحدث الأخبار المرتبطة بسهم معين."""
    return get_stock_news(db, ticker=ticker, limit=limit, offset=offset)


# Admin endpoint لتشغيل الـ crawler يدوياً
admin_news_router = APIRouter(prefix="/admin/news", tags=["admin", "news"])


@admin_news_router.post("/crawl", summary="تشغيل جلب الأخبار يدوياً (Admin)")
async def trigger_news_crawl(
    _: CurrentAdmin,
) -> dict[str, int]:
    """تشغيل دورة جلب أخبار فورية (للمشرفين فقط)."""
    saved = await run_news_crawl_once()
    return {"new_articles_saved": saved}

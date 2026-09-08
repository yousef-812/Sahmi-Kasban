"""خدمة جلب وتخزين الأخبار المالية من مصادر RSS."""
from __future__ import annotations

import hashlib
import logging
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from uuid import UUID

import httpx
import feedparser
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.news import NewsArticle, NewsArticleTicker
from app.schemas.news import NewsArticleResponse, NewsListResponse

logger = logging.getLogger(__name__)

# ─── مصادر RSS ────────────────────────────────────────────────────────────────

RSS_SOURCES: list[dict[str, str]] = [
    {
        "key": "alborsanews",
        "name": "البورصة نيوز",
        "url": "https://alborsanews.com/feed/",
    },
    {
        "key": "almalnews",
        "name": "جريدة المال",
        "url": "https://almalnews.com/category/%d8%a3%d8%b3%d9%88%d8%a7%d9%82/%d8%a7%d9%84%d8%a8%d9%88%d8%b1%d8%b5%d8%a9/feed/",
    },
    {
        "key": "youm7",
        "name": "اليوم السابع",
        "url": "https://www.youm7.com/rss/SectionRss?SectionID=588",
    },
    {
        "key": "google_news_egx",
        "name": "Google News - البورصة",
        "url": "https://news.google.com/rss/search?q=%D8%A7%D9%84%D8%A8%D9%88%D8%B1%D8%B5%D8%A9+%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9&hl=ar&gl=EG&ceid=EG:ar",
    },
    {
        "key": "arabfinance",
        "name": "آراب فاينانس",
        "url": "https://www.arabfinance.com/RSS",
    },
]

_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ─── استخراج التيكرات من النص ─────────────────────────────────────────────────

# قاموس الأسماء العربية → تيكر (يتم تحديثه من الـ DB)
_ARABIC_NAME_TO_TICKER: dict[str, str] = {
    "البنك التجاري الدولي": "COMI",
    "التجاري الدولي": "COMI",
    "طلعت مصطفى": "TMGH",
    "الشرقية للدخان": "EAST",
    "النساجون الشرقيون": "ORWE",
    "جهينة": "JUFO",
    "المصرية للاتصالات": "ETEL",
    "بالم هيلز": "PHDC",
    "هيليوبوليس": "HELI",
    "سيدي كرير": "SIDM",
    "كيما": "KIMA",
    "بنك أبوظبي الإسلامي": "ADIB",
    "راية القابضة": "RAYA",
    "القلعة القابضة": "CCAP",
    "أوراسكوم": "ORAS",
    "أوراسكوم للإنشاء": "ORAS",
    "إعمار مصر": "EMFD",
    "سوديك": "SDKH",
    "بنك مصر": "BMCL",
    "البنك الأهلي": "NBKE",
    "كريدي أجريكول": "CIEB",
    "أبو قير للأسمدة": "ABUK",
    "موبكو": "MFPC",
    "سيناء للمنغنيز": "SMFR",
    "إيفيرتون": "EFCO",
    "رامي للغزل": "RAMI",
    "كابيتال مصر": "CAPD",
}

# نمط للتيكرات الإنجليزية المكتوبة في النص
_TICKER_INLINE_RE = re.compile(r"\b([A-Z]{3,6})\b")

# حروف التشكيل العربية لإزالتها قبل المطابقة
_HARAKAT_RE = re.compile(r"[\u064B-\u065F\u0670]")


def _normalize_arabic(text: str) -> str:
    """تطبيع النص العربي لتسهيل المطابقة."""
    text = _HARAKAT_RE.sub("", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    return text.strip()


def extract_tickers_from_text(text: str, known_tickers: frozenset[str]) -> list[tuple[str, float]]:
    """استخراج تيكرات الأسهم من نص الخبر. يرجع list[(ticker, relevance_score)]."""
    found: dict[str, float] = {}
    normalized_text = _normalize_arabic(text)

    # 1. بحث بالأسماء العربية (دقة عالية)
    for arabic_name, ticker in _ARABIC_NAME_TO_TICKER.items():
        if _normalize_arabic(arabic_name) in normalized_text:
            found[ticker] = max(found.get(ticker, 0.0), 0.9)

    # 2. بحث بالتيكر الإنجليزي مباشرة في النص
    for match in _TICKER_INLINE_RE.finditer(text):
        candidate = match.group(1)
        if candidate in known_tickers:
            found[candidate] = max(found.get(candidate, 0.0), 1.0)

    return list(found.items())


# ─── جلب RSS ──────────────────────────────────────────────────────────────────

def _parse_published_at(entry: feedparser.FeedParserDict) -> datetime:
    """تحويل تاريخ النشر من الـ RSS إلى datetime مع timezone."""
    # feedparser يضع published_parsed كـ time.struct_time
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=UTC)
        except Exception:
            pass
    # fallback: published string
    raw = getattr(entry, "published", None)
    if raw:
        try:
            return parsedate_to_datetime(raw).astimezone(UTC)
        except Exception:
            pass
    return datetime.now(UTC)


def _extract_image_from_entry(entry: feedparser.FeedParserDict) -> str | None:
    """استخراج رابط الصورة من الـ RSS entry."""
    # media:content أو media:thumbnail
    media_content = getattr(entry, "media_content", None)
    if media_content and isinstance(media_content, list):
        for media in media_content:
            url = media.get("url")
            if url:
                return url

    # enclosures
    enclosures = getattr(entry, "enclosures", None)
    if enclosures:
        for enc in enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href") or enc.get("url")

    return None


async def fetch_rss_source(source: dict[str, str]) -> list[dict]:
    """جلب وتحليل مصدر RSS واحد. يرجع list of raw article dicts."""
    articles = []
    try:
        async with httpx.AsyncClient(
            headers=_HTTP_HEADERS,
            timeout=15.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(source["url"])
            response.raise_for_status()
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", source["key"], exc)
        return articles

    parsed = feedparser.parse(response.text)
    for entry in parsed.entries:
        url = getattr(entry, "link", None) or getattr(entry, "id", None)
        if not url:
            continue

        title = getattr(entry, "title", "").strip()
        if not title:
            continue

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        # إزالة HTML tags من الـ summary
        summary = re.sub(r"<[^>]+>", " ", summary).strip()
        summary = re.sub(r"\s+", " ", summary)[:2000]

        articles.append({
            "url": url,
            "title": title,
            "summary": summary,
            "published_at": _parse_published_at(entry),
            "image_url": _extract_image_from_entry(entry),
            "source_name": source["name"],
            "source_key": source["key"],
        })

    logger.info("RSS %s: fetched %d entries", source["key"], len(articles))
    return articles


# ─── حفظ في الـ Database ──────────────────────────────────────────────────────

def save_articles_to_db(
    db: Session,
    raw_articles: list[dict],
    known_tickers: frozenset[str],
) -> int:
    """حفظ الأخبار في الـ DB مع ربطها بالتيكرات. يرجع عدد الأخبار الجديدة."""
    saved = 0

    for raw in raw_articles:
        url = raw["url"]

        # التحقق من عدم التكرار
        existing = db.execute(
            select(NewsArticle.id).where(NewsArticle.url == url)
        ).scalar_one_or_none()
        if existing is not None:
            continue

        article = NewsArticle(
            title=raw["title"],
            summary=raw["summary"],
            url=url,
            source_name=raw["source_name"],
            source_key=raw["source_key"],
            image_url=raw.get("image_url"),
            published_at=raw["published_at"],
            sentiment=None,
            is_active=True,
        )
        db.add(article)
        db.flush()  # نحتاج الـ id للـ tickers

        # استخراج التيكرات وحفظها
        combined_text = f"{raw['title']} {raw['summary']}"
        ticker_matches = extract_tickers_from_text(combined_text, known_tickers)
        for ticker, score in ticker_matches:
            db.add(NewsArticleTicker(
                article_id=article.id,
                ticker=ticker,
                relevance_score=score,
            ))

        saved += 1

    db.commit()
    return saved


# ─── استعلامات القراءة ────────────────────────────────────────────────────────

def _load_tickers_for_articles(
    db: Session, article_ids: list[UUID]
) -> dict[UUID, list[str]]:
    """تحميل التيكرات لمجموعة من المقالات دفعة واحدة."""
    if not article_ids:
        return {}
    rows = db.execute(
        select(NewsArticleTicker.article_id, NewsArticleTicker.ticker)
        .where(NewsArticleTicker.article_id.in_(article_ids))
        .order_by(NewsArticleTicker.relevance_score.desc())
    ).all()
    result: dict[UUID, list[str]] = {}
    for article_id, ticker in rows:
        result.setdefault(article_id, []).append(ticker)
    return result


def _to_response(article: NewsArticle, tickers: list[str]) -> NewsArticleResponse:
    return NewsArticleResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        url=article.url,
        source_name=article.source_name,
        source_key=article.source_key,
        image_url=article.image_url,
        published_at=article.published_at,
        sentiment=article.sentiment,
        tickers=tickers,
    )


def get_latest_news(
    db: Session,
    limit: int = 30,
    offset: int = 0,
    source_key: str | None = None,
    sentiment: str | None = None,
) -> NewsListResponse:
    """آخر الأخبار (عامة)."""
    query = select(NewsArticle).where(NewsArticle.is_active == True)  # noqa: E712
    if source_key:
        query = query.where(NewsArticle.source_key == source_key)
    if sentiment:
        query = query.where(NewsArticle.sentiment == sentiment)

    total = db.execute(
        select(NewsArticle.id).where(NewsArticle.is_active == True)  # noqa: E712
    ).all().__len__()

    articles = db.execute(
        query.order_by(desc(NewsArticle.published_at)).offset(offset).limit(limit)
    ).scalars().all()

    ids = [a.id for a in articles]
    tickers_map = _load_tickers_for_articles(db, ids)

    return NewsListResponse(
        items=[_to_response(a, tickers_map.get(a.id, [])) for a in articles],
        total=total,
        has_more=(offset + limit) < total,
    )


def get_stock_news(
    db: Session,
    ticker: str,
    limit: int = 20,
    offset: int = 0,
) -> NewsListResponse:
    """أخبار سهم معين."""
    ticker = ticker.strip().upper()

    # نجيب الـ article_ids المرتبطة بالتيكر ده
    linked_ids_q = (
        select(NewsArticleTicker.article_id)
        .where(NewsArticleTicker.ticker == ticker)
    )

    articles = db.execute(
        select(NewsArticle)
        .where(NewsArticle.id.in_(linked_ids_q))
        .where(NewsArticle.is_active == True)  # noqa: E712
        .order_by(desc(NewsArticle.published_at))
        .offset(offset)
        .limit(limit)
    ).scalars().all()

    total_count = db.execute(
        select(NewsArticle.id)
        .where(NewsArticle.id.in_(linked_ids_q))
        .where(NewsArticle.is_active == True)  # noqa: E712
    ).all().__len__()

    ids = [a.id for a in articles]
    tickers_map = _load_tickers_for_articles(db, ids)

    return NewsListResponse(
        items=[_to_response(a, tickers_map.get(a.id, [])) for a in articles],
        total=total_count,
        has_more=(offset + limit) < total_count,
    )


def get_article_by_id(db: Session, article_id: UUID) -> NewsArticleResponse | None:
    """تفاصيل خبر معين."""
    article = db.get(NewsArticle, article_id)
    if not article or not article.is_active:
        return None
    tickers_map = _load_tickers_for_articles(db, [article.id])
    return _to_response(article, tickers_map.get(article.id, []))

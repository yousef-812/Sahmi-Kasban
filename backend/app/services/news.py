"""خدمة جلب وتخزين الأخبار المالية من مصادر RSS."""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from uuid import UUID

import feedparser
import httpx
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from app.models.news import NewsArticle, NewsArticleTicker
from app.schemas.news import NewsArticleResponse, NewsListResponse

logger = logging.getLogger(__name__)

try:
    import trafilatura
except ImportError:  # pragma: no cover - fallback عند عدم التثبيت
    trafilatura = None  # type: ignore[assignment]

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - fallback عند عدم التثبيت
    BeautifulSoup = None  # type: ignore[assignment, misc]

_MAX_CONTENT_LENGTH = 100_000
_HTML_FETCH_TIMEOUT = 25.0
_HTML_FETCH_RETRIES = 3

# ─── مصادر RSS ────────────────────────────────────────────────────────────────

RSS_SOURCES: list[dict[str, str]] = [
    {
        "key": "google_news_egx",
        "name": "أخبار البورصة المصرية",
        "url": "https://news.google.com/rss/search?q=%D8%A7%D9%84%D8%A8%D9%88%D8%B1%D8%B5%D8%A9+%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9&hl=ar&gl=EG&ceid=EG:ar",
    },
    {
        "key": "google_news_stocks",
        "name": "أخبار أسهم مصر",
        "url": "https://news.google.com/rss/search?q=%D8%A3%D8%B3%D9%87%D9%85+%D8%A7%D9%84%D8%A8%D9%88%D8%B1%D8%B5%D8%A9+%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9&hl=ar&gl=EG&ceid=EG:ar",
    },
    {
        "key": "google_news_companies",
        "name": "أخبار شركات البورصة",
        "url": "https://news.google.com/rss/search?q=%D8%B4%D8%B1%D9%83%D8%A7%D8%AA+%D8%A7%D9%84%D8%A8%D9%88%D8%B1%D8%B5%D8%A9+%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9&hl=ar&gl=EG&ceid=EG:ar",
    },
    {
        "key": "alborsanews",
        "name": "البورصة نيوز",
        "url": "https://alborsanews.com/feed/",
    },
    {
        "key": "youm7",
        "name": "اليوم السابع الاقتصاد",
        "url": "https://www.youm7.com/rss/SectionRss?SectionID=588",
    },
    {
        "key": "almasryalyoum",
        "name": "المصري اليوم اقتصاد",
        "url": "https://www.almasryalyoum.com/rss/rssfeed",
    },
]

_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ─── استخراج التيكرات من النص ─────────────────────────────────────────────────

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
    "فوري": "FWRY",
    "حديد عز": "ESRS",
    "السويدي": "SWDY",
    "السويدي إلكتريك": "SWDY",
}

_TICKER_INLINE_RE = re.compile(r"\b([A-Z]{3,6})\b")
_HARAKAT_RE = re.compile(r"[\u064B-\u065F\u0670]")


def _normalize_arabic(text: str) -> str:
    """تطبيع النص العربي لتسهيل المطابقة."""
    text = _HARAKAT_RE.sub("", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    return text.strip()


def extract_tickers_from_text(text: str, known_tickers: frozenset[str]) -> list[tuple[str, float]]:
    """استخراج تيكرات الأسهم من نص الخبر."""
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
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=UTC)
        except Exception:
            pass
    raw = getattr(entry, "published", None)
    if raw:
        try:
            return parsedate_to_datetime(raw).astimezone(UTC)
        except Exception:
            pass
    return datetime.now(UTC)


def _extract_image_from_entry(entry: feedparser.FeedParserDict) -> str | None:
    """استخراج رابط الصورة من الـ RSS entry."""
    media_content = getattr(entry, "media_content", None)
    if media_content and isinstance(media_content, list):
        for media in media_content:
            url = media.get("url")
            if url:
                return str(url)[:3500]

    enclosures = getattr(entry, "enclosures", None)
    if enclosures:
        for enc in enclosures:
            if enc.get("type", "").startswith("image/"):
                href = enc.get("href") or enc.get("url")
                if href:
                    return str(href)[:3500]

    return None


async def fetch_rss_source(source: dict[str, str]) -> list[dict]:
    """جلب وتحليل مصدر RSS واحد."""
    articles = []
    try:
        async with httpx.AsyncClient(
            headers=_HTTP_HEADERS,
            timeout=15.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(source["url"])
            response.raise_for_status()
            content_text = response.text
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", source["key"], exc)
        return articles

    parsed = feedparser.parse(content_text)
    for entry in parsed.entries:
        raw_url = getattr(entry, "link", None) or getattr(entry, "id", None)
        if not raw_url:
            continue

        title = getattr(entry, "title", "").strip()
        if not title:
            continue

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        summary = re.sub(r"<[^>]+>", " ", summary).strip()
        summary = re.sub(r"\s+", " ", summary)[:4500]

        articles.append({
            "url": str(raw_url)[:3500],
            "title": title[:950],
            "summary": summary,
            "published_at": _parse_published_at(entry),
            "image_url": _extract_image_from_entry(entry),
            "source_name": source["name"],
            "source_key": source["key"],
        })

    logger.info("RSS %s: fetched %d entries", source["key"], len(articles))
    return articles


# ─── استخراج المحتوى الكامل للمقال ──────────────────────────────────────────

_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8",
    "Accept-Language": "ar,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Upgrade-Insecure-Requests": "1",
}


def _is_google_news_url(url: str) -> bool:
    """روابط Google News غالباً redirect لصفحة وسيطة وليست المقال المباشر."""
    lowered = url.lower()
    return "news.google.com" in lowered


def _extract_text_with_soup(html: str) -> str:
    """استخراج نص المقال من HTML عبر BeautifulSoup كحل بديل."""
    if BeautifulSoup is None or not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            tag.decompose()
        body = soup.body or soup
        paragraphs: list[str] = []
        for node in body.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
            text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
            if len(text) >= 40:
                paragraphs.append(text)
        if len(paragraphs) >= 3:
            return "\n\n".join(paragraphs)[:_MAX_CONTENT_LENGTH]
        # Fallback: كل نص الـ body
        raw = body.get_text("\n", strip=True)
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in raw.splitlines() if ln.strip()]
        merged = "\n\n".join(lines)
        return merged[: _MAX_CONTENT_LENGTH] if len(merged) >= 40 else ""
    except Exception:
        return ""


async def _fetch_html(url: str) -> tuple[str, str]:
    """جلب صفحة المقال عبر httpx بمحاكاة متصفح حقيقي مع إعادة محاولة.

    يعالج أيضاً روابط Google News الوسيطة بفك الـ redirect للوصول للمقال الأصلي.
    يرجع (html, final_url) حيث final_url هو الرابط النهائي بعد الـ redirects.
    """
    final_url = url
    last_error: Exception | None = None

    async with httpx.AsyncClient(
        headers=_FETCH_HEADERS,
        timeout=_HTML_FETCH_TIMEOUT,
        follow_redirects=True,
        max_redirects=6,
        http2=False,
    ) as client:
        for attempt in range(1, _HTML_FETCH_RETRIES + 1):
            try:
                response = await client.get(final_url)
                response.raise_for_status()
                final_url = str(response.url)
                # للمقالات العربية غالباً nافزة من Google بإصدارات ثابتة
                html = response.text
                if len(html) < 500 and "news.google.com" in str(response.url):
                    continue
                return html, final_url
            except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
                last_error = exc
                # لا نعيد المحاولة على أخطاء نهائية
                if isinstance(exc, httpx.HTTPStatusError):
                    status = exc.response.status_code
                    if status in (403, 404, 410) and attempt >= 2:
                        break
                if attempt < _HTML_FETCH_RETRIES:
                    await asyncio.sleep(1.5 * attempt)

    logger.warning("HTML fetch failed for %s: %s", url[:120], last_error)
    return "", final_url


async def resolve_article_url(url: str) -> str:
    """فك رابط Google News الوسيط وإرجاع رابط المقال الحقيقي.

    يرجع الرابط الأصلي لو فشل الفك حتى لا يضيع الرابط.
    """
    if not url or not _is_google_news_url(url):
        return url
    _, resolved = await _fetch_html(url)
    if not resolved or "news.google.com" in resolved:
        return url
    return resolved


async def fetch_article_content_and_resolve(url: str) -> tuple[str, str]:
    """جلب المحتوى الكامل مع فك رابط Google News الوسيط في جلب واحد.

    يرجع (content, final_url).
    """
    if not url:
        return "", url

    html, final_url = await _fetch_html(url)
    content = ""
    if html:
        # المحاولة الأولى: trafilatura لاستخراج الجوهر
        if trafilatura is not None:
            try:
                text = await asyncio.to_thread(trafilatura.extract, html)
                if text and len(text.strip()) >= 40:
                    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
                    content = "\n\n".join(paragraphs)[:_MAX_CONTENT_LENGTH]
            except Exception:
                logger.warning("trafilatura extraction failed for %s", url[:120])
        if not content:
            content = await asyncio.to_thread(_extract_text_with_soup, html)

    if _is_google_news_url(url) and final_url and "news.google.com" not in final_url:
        return content, final_url
    return content, url


async def fetch_article_content(url: str) -> str:
    """جلب المحتوى الكامل لصفحة الخبر (لتوقيع قديم متوافق).

    يرجع نص المقال مع فواصل أسطر بين الفقرات، أو سلسلة فارغة عند الفشل.
    """
    content, _ = await fetch_article_content_and_resolve(url)
    return content


# ─── حفظ في الـ Database ──────────────────────────────────────────────────────

def save_articles_to_db(
    db: Session,
    raw_articles: list[dict],
    known_tickers: frozenset[str],
) -> int:
    """حفظ الأخبار في الـ DB مع ربطها بالتيكرات مع حماية كاملة من الأخطاء التكرارية والمساحات."""
    saved = 0

    for raw in raw_articles:
        url = raw["url"][:3500]

        # التحقق من عدم التكرار
        existing = db.execute(
            select(NewsArticle.id).where(NewsArticle.url == url)
        ).scalar_one_or_none()
        if existing is not None:
            continue

        try:
            with db.begin_nested():
                raw_content = raw.get("content") or None
                article = NewsArticle(
                    title=raw["title"][:950],
                    summary=raw["summary"][:4500],
                    content=raw_content[:_MAX_CONTENT_LENGTH] if raw_content else None,
                    url=url,
                    source_name=raw["source_name"][:90],
                    source_key=raw["source_key"][:35],
                    image_url=raw.get("image_url")[:3500] if raw.get("image_url") else None,
                    published_at=raw["published_at"],
                    sentiment=None,
                    is_active=True,
                )
                db.add(article)
                db.flush()

                # استخراج التيكرات وحفظها
                combined_text = f"{raw['title']} {raw['summary']}"
                ticker_matches = extract_tickers_from_text(combined_text, known_tickers)
                for ticker, score in ticker_matches:
                    db.add(NewsArticleTicker(
                        article_id=article.id,
                        ticker=ticker[:20],
                        relevance_score=score,
                    ))
                saved += 1
        except Exception:
            logger.exception("Failed to save article %s", url[:100])

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


def _to_response(
    article: NewsArticle,
    tickers: list[str],
    *,
    include_content: bool = False,
) -> NewsArticleResponse:
    return NewsArticleResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        content=article.content if include_content else None,
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
    q: str | None = None,
) -> NewsListResponse:
    """آخر الأخبار (عامة) مع دعم البحث بالكلمات المفتاحية والرمز والاسم."""
    query = select(NewsArticle).where(NewsArticle.is_active == True)  # noqa: E712

    if source_key:
        query = query.where(NewsArticle.source_key == source_key)
    if sentiment:
        query = query.where(NewsArticle.sentiment == sentiment)

    if q and q.strip():
        search_term = f"%{q.strip()}%"
        # البحث في العنوان أو الملخص أو التيكرات المرتبطة
        matching_ticker_ids = select(NewsArticleTicker.article_id).where(
            NewsArticleTicker.ticker.ilike(search_term)
        )
        query = query.where(
            or_(
                NewsArticle.title.ilike(search_term),
                NewsArticle.summary.ilike(search_term),
                NewsArticle.source_name.ilike(search_term),
                NewsArticle.id.in_(matching_ticker_ids),
            )
        )

    # حساب العدد الكلي
    total_query = select(NewsArticle.id).where(NewsArticle.is_active == True)  # noqa: E712
    if source_key:
        total_query = total_query.where(NewsArticle.source_key == source_key)
    if sentiment:
        total_query = total_query.where(NewsArticle.sentiment == sentiment)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        matching_ticker_ids = select(NewsArticleTicker.article_id).where(
            NewsArticleTicker.ticker.ilike(search_term)
        )
        total_query = total_query.where(
            or_(
                NewsArticle.title.ilike(search_term),
                NewsArticle.summary.ilike(search_term),
                NewsArticle.source_name.ilike(search_term),
                NewsArticle.id.in_(matching_ticker_ids),
            )
        )

    total = len(db.execute(total_query).all())

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
    clean_ticker = ticker.strip().upper()

    # 1. الأخبار المرتبطة مباشرة بالتيكر
    linked_ids_q = (
        select(NewsArticleTicker.article_id)
        .where(NewsArticleTicker.ticker == clean_ticker)
    )

    # 2. أو الأخبار التي تحتوي رمز السهم في العنوان أو النص
    ticker_pattern = f"%{clean_ticker}%"

    articles = db.execute(
        select(NewsArticle)
        .where(
            or_(
                NewsArticle.id.in_(linked_ids_q),
                NewsArticle.title.ilike(ticker_pattern),
                NewsArticle.summary.ilike(ticker_pattern),
            )
        )
        .where(NewsArticle.is_active == True)  # noqa: E712
        .order_by(desc(NewsArticle.published_at))
        .offset(offset)
        .limit(limit)
    ).scalars().all()

    total_count = len(
        db.execute(
            select(NewsArticle.id)
            .where(
                or_(
                    NewsArticle.id.in_(linked_ids_q),
                    NewsArticle.title.ilike(ticker_pattern),
                    NewsArticle.summary.ilike(ticker_pattern),
                )
            )
            .where(NewsArticle.is_active == True)  # noqa: E712
        ).all()
    )

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
    return _to_response(article, tickers_map.get(article.id, []), include_content=True)


async def get_article_detail_content(db: Session, article_id: UUID) -> NewsArticleResponse | None:
    """تفاصيل خبر معين مع استخراج المحتوى الكامل عند الطلب إذا لم يكن مخزناً."""
    article = db.get(NewsArticle, article_id)
    if not article or not article.is_active:
        return None

    if not article.content:
        content = await fetch_article_content(article.url)
        if content:
            article.content = content[:_MAX_CONTENT_LENGTH]
            try:
                db.commit()
            except Exception:
                logger.exception("Failed to persist lazy article content %s", article_id)

    tickers_map = _load_tickers_for_articles(db, [article.id])
    return _to_response(article, tickers_map.get(article.id, []), include_content=True)

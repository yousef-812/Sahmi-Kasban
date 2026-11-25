"""خدمة حساب معنويات الأخبار لكل سهم (WP-16).

تعتمد على الأخبار المخزّنة محليًا عبر ``app.services.news`` (جدول ``news_articles``
المرتبط بـ ``news_article_tickers``). لا توجد نداءات شبكة ولا نماذج ML:

- إن كان عمود ``NewsArticle.sentiment`` مملوءًا (مدلول إيجابي/محايد/سلبي) تُستخدم قيمته مباشرة.
- وإلا يُطبَّق مُصنِّف لكسِكِون (heuristic) بالكلمات المفتاحية المالية العربية والإنجليزية
  على العنوان + الملخص — ليس نموذجًا، بل مطابقة كلمات ثابتة وقابلة للتكرار.

التلاشي الزمني: decay أسّي نصف عمره ``HALF_LIFE_DAYS`` (3.5 يوم افتراضيًا):
وزن المقال = 0.5 ** (عمر_المقال_بالأيام / HALF_LIFE_DAYS) * نسبة الصلة بالسهم.
النتيجة المجمّعة = متوسط مرجَّح لدرجات المقالات مقيَّد إلى [-1, 1].
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.news import NewsArticle, NewsArticleTicker

HALF_LIFE_DAYS = 3.5
DEFAULT_WINDOW_DAYS = 7
MAX_WINDOW_DAYS = 90
COVERAGE_NORMAL_MIN_SAMPLES = 10

_HARAKAT_RE = re.compile(r"[\u064B-\u065F\u0670]")
_EN_WORD_RE = re.compile(r"[A-Za-z]+")

_LABEL_TO_POLARITY: dict[str, float] = {
    "positive": 1.0,
    "pos": 1.0,
    "إيجابي": 1.0,
    "ايجابي": 1.0,
    "negative": -1.0,
    "neg": -1.0,
    "سلبي": -1.0,
    "neutral": 0.0,
    "محايد": 0.0,
    "محياد": 0.0,
}

# كلمات مالية مختارة (إنجليزية كاملة الكلمة)
_POSITIVE_EN = frozenset({
    "acquisition", "approved", "approval", "boost", "boosts", "breakthrough",
    "contract", "dividend", "dividends", "exceed", "exceeds", "expansion",
    "gain", "gains", "grow", "growth", "profit", "profitable", "profits",
    "bounce", "bullish", "high", "record", "recover", "recovery", "rise",
    "rises", "rose", "rising", "strong", "surge", "surges", "upgrade", "upgraded",
})
_NEGATIVE_EN = frozenset({
    "bankruptcy", "bearish", "complaint", "crash", "cut", "cuts", "debt",
    "decline", "declined", "declines", "default", "downgrade",
    "downgraded", "drop", "drops", "fell", "fine", "fraud", "investigation",
    "layoff", "layoffs", "lawsuit", "loss", "losses", "miss", "misses", "penalty",
    "plunge", "slump", "suspend", "suspended", "suspension", "warning", "weak",
})

# جذور/مقاطع عربية تُطابَق كـ substring بعد تطبيع النص (أ/إ/آ→ا، ة→ه، بدون تشكيل)
_POSITIVE_AR = (
    "ارباح", "استحواذ", "ازدهار", "ارتفع", "تعاف", "ترقيه", "توسع", "تجاوز",
    "قفز", "مكسب", "نمو", "صعد", "قوي", "توزيع",
)
_NEGATIVE_AR = (
    "افلاس", "ازمه", "انهيار", "تدنين", "تعثر", "تخفيض", "شكا", "غرام",
    "مديونيه", "ملاحقه", "هبوط", "تراجع", "خفض", "تسريح", "توقيف", "تعليق",
    "انخفاض", "فضيح", "خسار",
)


def _normalize_arabic(text: str) -> str:
    text = _HARAKAT_RE.sub("", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    return text.strip()


def _article_polarity(title: str, summary: str, stored_label: str | None) -> float:
    """درجة مقال واحد في [-1, 1] من الملصق المخزَّن أو من اللكسِكِون."""
    if stored_label:
        label = stored_label.strip().lower()
        if label in _LABEL_TO_POLARITY:
            return _LABEL_TO_POLARITY[label]

    combined = f"{title or ''} {summary or ''}".strip()
    if not combined:
        return 0.0

    lowered = combined.lower()
    positive_hits = 0
    negative_hits = 0

    for word in _EN_WORD_RE.findall(lowered):
        if word in _POSITIVE_EN:
            positive_hits += 1
        elif word in _NEGATIVE_EN:
            negative_hits += 1

    normalized = _normalize_arabic(combined)
    positive_hits += sum(1 for term in _POSITIVE_AR if term in normalized)
    negative_hits += sum(1 for term in _NEGATIVE_AR if term in normalized)

    total = positive_hits + negative_hits
    if total == 0:
        return 0.0
    return max(-1.0, min(1.0, (positive_hits - negative_hits) / total))


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def compute_symbol_sentiment(db: Session, ticker: str, *, days: int = 7) -> dict[str, object]:
    """يحسب معنويات الأخبار لنقطة زمنية محددة (بدون أي كتابة على القاعدة).

    يقرأ الأخبار النشطة المرتبطة بالـ ticker خلال آخر ``days`` يومًا، يمنح كل
    خبر وزنًا أسّيًا نصف عمره ``HALF_LIFE_DAYS`` (الأحدث يعلو على الأقدم) مضروبًا
    في ``relevance_score``، ثم يرجّع متوسطًا مرجّحًا في [-1, 1].
    """
    clean_ticker = ticker.strip().upper()
    window_days = max(1, min(int(days), MAX_WINDOW_DAYS))
    now = datetime.now(UTC)
    cutoff = now - timedelta(days=window_days)

    rows = db.execute(
        select(NewsArticle, NewsArticleTicker.relevance_score)
        .join(NewsArticleTicker, NewsArticleTicker.article_id == NewsArticle.id)
        .where(
            NewsArticleTicker.ticker == clean_ticker,
            NewsArticle.is_active == True,  # noqa: E712
            NewsArticle.published_at >= cutoff,
        )
        .order_by(NewsArticle.published_at.desc())
    ).all()

    sample_size = len(rows)
    result: dict[str, object] = {
        "ticker": clean_ticker,
        "score": 0.0,
        "sample_size": sample_size,
        "coverage": "insufficient",
        "as_of": now,
        "window_days": window_days,
    }
    if sample_size == 0:
        return result

    weighted_sum = 0.0
    weight_total = 0.0
    for article, relevance in rows:
        polarity = _article_polarity(article.title, article.summary, article.sentiment)
        published = _aware_utc(article.published_at)
        age_days = max(0.0, (now - published).total_seconds() / 86400.0)
        decay = 0.5 ** (age_days / HALF_LIFE_DAYS)
        relevance_score = float(relevance) if isinstance(relevance, (int, float)) else 1.0
        weight = decay * max(0.0, relevance_score)
        weighted_sum += weight * polarity
        weight_total += weight

    score = max(-1.0, min(1.0, weighted_sum / weight_total)) if weight_total > 0 else 0.0
    if sample_size < COVERAGE_NORMAL_MIN_SAMPLES:
        coverage = "low"
    else:
        coverage = "normal"

    result["score"] = round(score, 4)
    result["coverage"] = coverage
    return result

from __future__ import annotations

import asyncio
import json
import urllib.parse
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy.orm import Session

from app.jobs import news_crawler
from app.models.news import NewsArticle
from app.services import news as news_service
from app.services.news import get_article_detail_content, get_latest_news

GOOGLE_URL = "https://news.google.com/articles/CBMabc123"
PUBLISHER_URL = "https://publisher.example/article"
ARTICLE_TEXT = "نص المقال الكامل الذي يستخرج عند الطلب من صفحة الناشر."

# ─── أشكات حقيقية لمرحلتي فك رابط Google News ─────────────────────────────────

STAGE1_URL = "https://news.google.com/rss/articles/CBMabc123"
BATCHEXECUTE_URL = "https://news.google.com/_/DotsSplashUi/data/batchexecute"
PUBLISHER_ARTICLE_URL = "https://www.bankygate.com/78159/sample-article"

# هيكل JS المرتجع من المرحلة 1 (ليس صفحة الموافقة) بحقول data-n-a-sg/ts/id الحقيقية
STAGE1_SHELL_HTML = (
    '<!doctype html><html><head><meta charset="utf-8"><title>Google News</title></head><body>'
    '<c-wiz jscontroller="x1WM6d" data-n-a-id="CBMabc123_TRUNCATED" '
    'data-n-a-sg="SG_SIG_98765" data-n-a-ts="1730000000">'
    "<div>DotsSplashUi</div></c-wiz></body></html>"
)

# استجابة batchexecute بالشكل الحقيقي: بادئة )]}\' ثم wrb.fr/Fbv4je مع garturlres
STAGE2_RESPONSE = (
    ")]}'\n\n"
    '[["wrb.fr","Fbv4je","[\\"garturlres\\",\\"https://www.bankygate.com/78159/sample-article\\"]",'
    'null,null,null,"generic"]]'
)
STILL_GOOGLE_RESPONSE = (
    ")]}'\n\n"
    '[["wrb.fr","Fbv4je","[\\"garturlres\\",\\"https://news.google.com/rss/articles/STILL\\"]",'
    'null,null,null,"generic"]]'
)
UNPARSEABLE_RESPONSE = ")]}'\n\n[[not-json-at-all"

EXPECTED_GARTURLREQ = [
    ["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1, None, None, None, None, None, 0, 1],
    "X", "X", 1, [1, 1, 1], 1, 1, None, 0, 0, None, 0,
]

PUBLISHER_HTML = (
    "<!doctype html><html><head><title>ارتفاع تداولات البورصة</title></head><body><article>"
    "<h1>ارتفاع تداولات البورصة المصرية</h1>"
    "<p>ارتفع مؤشر البورصة المصرية بنسبة 1.2 في المئة خلال تعاملات اليوم مدعوماً بصفقات الشراء من المؤسسات الأجنبية.</p>"
    "<p>وانطلقت أسهم قطاع البنوك قيادة الصعود تفاعلآ مع توقعات خفض أسعار الفائدة في الاجتماعات القادمة.</p>"
    "<p>وأكد محللون ماليون أن الاستقرار الحالي يعكس ثقة المستثمرين في مستقبل الاقتصاد المصري على المدى المتوسط.</p>"
    "</article></body></html>"
)

# ─── نصوص صفحة الموافقة ───────────────────────────────────────────────────────

LANGUAGE_LIST_TEXT = "\n".join([
    "- العربية", "- Deutsch", "- English", "- Español",
    "- Français", "- Italiano", "- Português", "- Türkçe",
])
SLASH_LANGUAGE_LIST_TEXT = "- العربية / - Deutsch / - English / - Español / - Français / - Italiano"
CONSENT_TEXT = (
    "Before you continue to Google\n"
    "We use cookie files and Google technologies to improve your experience.\n"
    "قبل المتابعة إلى Google لاختيار لغتك المفضلة\n"
    + LANGUAGE_LIST_TEXT
)
CONSENT_HTML = (
    "<!doctype html><html><head><title>Consent</title></head><body>"
    + ("<p>padding paragraph keeping this fake consent html well above five hundred chars. </p>" * 8)
    + f"<main><p>{CONSENT_TEXT}</p></main>"
    + "</body></html>"
)

RSS_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<rss version="2.0"><channel><title>feed</title>'
    "<item>"
    "<title>خبر تجريبي</title>"
    "<link>https://example.com/article</link>"
    "<description>&amp;nbsp;&amp;nbsp;نص المالي&amp;nbsp;الأول</description>"
    "<pubDate>Tue, 14 Oct 2025 10:00:00 GMT</pubDate>"
    "</item></channel></rss>"
)
RSS_SOURCE = {"key": "test-rss", "name": "مصدر تجريبي", "url": "https://example.com/rss"}


# ─── أدوات محاكاة الشبكة (offline بالكامل) ────────────────────────────────────


class _FakeResponse:
    def __init__(self, text: str, url: str) -> None:
        self.text = text
        self.url = url

    def raise_for_status(self) -> None:
        return None


class _StaticExtractor:
    """بديل trafilatura يرجع نصاً ثابتاً (لاستخراج نص صفحة الموافقة بشكل حتمي)."""

    def __init__(self, text: str) -> None:
        self._text = text

    def extract(self, html: str) -> str:
        return self._text


# يسجّل kwargs الممرّرة إلى httpx.AsyncClient حتى نتحقق أن فكّ الرابط يضبط كوكي
# الموافقة. ضروري من عناوين IP الأوروبية: بدونها تعيد جوجل إلى consent.google.com.
_CLIENT_KWARGS: list[dict[str, object]] = []


def _install_fake_httpx(
    monkeypatch: pytest.MonkeyPatch,
    *,
    get_responses: dict[str, str] | None = None,
    default_get: str = "",
    post_response: str = "",
    fail_first_gets: int = 0,
    raise_on_get: type[BaseException] | None = None,
) -> tuple[list[tuple[str, str]], list[tuple[bytes | None, dict | None]]]:
    """استبدال httpx.AsyncClient بعميل وهمي يسجّل الطلبات ويعيد استجابات جاهزة."""
    record: list[tuple[str, str]] = []
    posts: list[tuple[bytes | None, dict | None]] = []
    failures_left = {"count": fail_first_gets}
    responses = dict(get_responses or {})
    _CLIENT_KWARGS.clear()

    class _FakeAsyncClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            _CLIENT_KWARGS.append(dict(kwargs))

        async def __aenter__(self) -> _FakeAsyncClient:
            return self

        async def __aexit__(self, *exc_info: object) -> bool:
            return False

        async def get(self, url: str, **kwargs: object) -> _FakeResponse:
            target = str(url)
            record.append(("GET", target))
            if raise_on_get is not None:
                raise raise_on_get()
            if failures_left["count"] > 0:
                failures_left["count"] -= 1
                raise httpx.ConnectError("simulated transient failure")
            for prefix, body in responses.items():
                if target.startswith(prefix):
                    return _FakeResponse(body, target)
            return _FakeResponse(default_get, target)

        async def post(
            self,
            url: str,
            *,
            content: bytes | None = None,
            headers: dict[str, str] | None = None,
            **kwargs: object,
        ) -> _FakeResponse:
            target = str(url)
            record.append(("POST", target))
            posts.append((content, headers))
            return _FakeResponse(post_response, target)

    monkeypatch.setattr(news_service.httpx, "AsyncClient", _FakeAsyncClient)
    return record, posts


def _seed_article(
    db: Session,
    *,
    url: str = GOOGLE_URL,
    content: str | None = None,
) -> NewsArticle:
    article = NewsArticle(
        title="خبر تجريبي",
        summary="ملخص الخبر التجريبي",
        content=content,
        url=url,
        source_name="test-source",
        source_key="test",
        published_at=datetime.now(UTC) - timedelta(hours=1),
    )
    db.add(article)
    db.commit()
    return article


def _patch_resolver(
    monkeypatch: pytest.MonkeyPatch,
    result: tuple[str, str],
) -> list[tuple[str, bool]]:
    calls: list[tuple[str, bool]] = []

    async def _fake_resolve(url: str, *, resolve_google_news: bool = False) -> tuple[str, str]:
        calls.append((url, resolve_google_news))
        return result

    monkeypatch.setattr(news_service, "fetch_article_content_and_resolve", _fake_resolve)
    return calls


# ─── resolved_url قبل وبعد قراءة التفاصيل ─────────────────────────────────────


def test_resolved_url_is_none_before_detail_read(db_session: Session) -> None:
    article = _seed_article(db_session)

    assert article.resolved_url is None

    listing = get_latest_news(db_session)
    assert listing.total == 1
    item = listing.items[0]
    assert item.resolved_url is None
    assert item.url == GOOGLE_URL
    dumped = item.model_dump()
    assert "resolved_url" in dumped
    assert dumped["resolved_url"] is None


def test_detail_read_persists_resolved_url(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session)
    calls = _patch_resolver(monkeypatch, (ARTICLE_TEXT, PUBLISHER_URL))

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.resolved_url == PUBLISHER_URL
    assert response.url == GOOGLE_URL
    assert response.content == ARTICLE_TEXT
    # مسار التفاصيل هو من يفعّل فك رابط Google News
    assert calls == [(GOOGLE_URL, True)]

    db_session.refresh(article)
    assert article.resolved_url == PUBLISHER_URL
    assert article.url == GOOGLE_URL
    assert article.content == ARTICLE_TEXT


def test_resolver_returning_google_news_url_keeps_resolved_url_none(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session)
    _patch_resolver(monkeypatch, (ARTICLE_TEXT, "https://news.google.com/articles/still_interstitial"))

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.resolved_url is None
    assert response.url == GOOGLE_URL

    db_session.refresh(article)
    assert article.resolved_url is None


def test_detail_read_resolves_even_when_content_already_cached(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session, content="محتوى محفوظ مسبقاً")
    _patch_resolver(monkeypatch, (ARTICLE_TEXT, PUBLISHER_URL))

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.resolved_url == PUBLISHER_URL
    assert response.url == GOOGLE_URL
    assert response.content == "محتوى محفوظ مسبقاً"


def test_direct_url_with_cached_content_does_not_fetch(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    direct_url = "https://publisher.example/direct-article"
    article = _seed_article(db_session, url=direct_url, content="محتوى محفوظ")

    async def _boom(url: str, *, resolve_google_news: bool = False) -> tuple[str, str]:
        raise AssertionError("no fetch expected for cached direct article")

    monkeypatch.setattr(news_service, "fetch_article_content_and_resolve", _boom)

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.resolved_url is None
    assert response.url == direct_url


# ─── فك رابط Google News بالمرحلتين (بدون شبكة) ───────────────────────────────


def test_resolve_google_news_url_follows_two_stage_recipe(monkeypatch: pytest.MonkeyPatch) -> None:
    record, posts = _install_fake_httpx(
        monkeypatch,
        get_responses={STAGE1_URL: STAGE1_SHELL_HTML},
        post_response=STAGE2_RESPONSE,
    )

    resolved = asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL))

    assert resolved == PUBLISHER_ARTICLE_URL
    assert record[0] == ("GET", STAGE1_URL)
    assert record[1] == ("POST", BATCHEXECUTE_URL)
    assert len(record) == 2

    content_type = posts[0][1]["Content-Type"]
    assert content_type == "application/x-www-form-urlencoded;charset=UTF-8"

    form = urllib.parse.parse_qs(posts[0][0].decode())
    freq = json.loads(form["f.req"][0])
    assert freq[0][0][0] == "Fbv4je"
    inner = json.loads(freq[0][0][1])
    assert inner[0] == "garturlreq"
    assert inner[1] == EXPECTED_GARTURLREQ
    assert inner[2] == "CBMabc123"
    assert inner[3] == 1730000000
    assert inner[4] == "SG_SIG_98765"


def test_resolve_google_news_url_sends_eu_consent_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """يجب إرسال كوكي الموافقة SOCS=CAI مع عميل فكّ الرابط.

    من عناوين IP داخل الاتحاد الأوروبي تعيد جوجل روابط /rss/articles/ إلى
    consent.google.com (GDPR) بدل صفحة الـ JS shell التي تحمل data-n-a-sg، فيفشل
    استخراج التوقيع. تحقّقنا عملياً من IP فرانكفورت: بدون الكوكي يرجع
    consent.google.com بلا توقيع، ومعه يرجع news.google.com بتوقيع سليم.
    الطريقة القديمة CONSENT=YES+ لم تعد تعمل.
    """
    _install_fake_httpx(
        monkeypatch,
        get_responses={STAGE1_URL: STAGE1_SHELL_HTML},
        post_response=STAGE2_RESPONSE,
    )

    assert asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL)) == PUBLISHER_ARTICLE_URL

    assert _CLIENT_KWARGS, "لم يُنشئ resolver أي AsyncClient"
    assert _CLIENT_KWARGS[0].get("cookies") == {"SOCS": "CAI"}


# ─── رفض القمامة الثنائية ─────────────────────────────────────────────────────
#
# بعض الناشرين يعيد استجابة مضغوطة بلا ترويسة Content-Encoding من عناوين IP غير
# مألوفة، فيفكّها httpx كنص خام يحوي بايتات NUL. حفظها في عمود text بـ
# PostgreSQL يرفع DataError ويكسر الجلسة (PendingRollbackError → HTTP 500).

CLEAN_ARABIC = (
    "ارتفع مؤشر البورصة المصرية بنسبة 1.2 في المئة خلال تعاملات اليوم "
    "مدعوماً بصفقات الشراء من المؤسسات الأجنبية وتفاعلآ مع توقعات خفض الفائدة."
)

# NUL ومحارف تحكم + بايتات عالية غير مألوفة (مثل ما ابتلعه httpx من استجابة مضغوطة)
GARBAGE_CONTENT = "\x00\x02\x7f\u4e00\u4e01\u9fff\u0000\u001f" * 12


def test_sanitize_extracted_text_strips_nul_and_control_chars() -> None:
    assert news_service._sanitize_extracted_text("أ\x00ب\x02ج\nد\x7f") == "أبج\nد"


def test_fetch_headers_do_not_request_brotli() -> None:
    """لا يجوز ضبط Accept-Encoding يدوياً مع br.

    httpx لا يفك brotli ما لم تكن مكتبة brotli مثبتة في الصورة. عند طلب br
    يعيد بعض الناشرين Content-Encoding: br فترجع بايتات خام تحوي NUL تُستخرج
    كقمامة. تحقّقنا عملياً من IP فرانكفورت على elbalad.news: مع br يرجع 72 بايت
    NUL و87 حرفاً عربياً فقط، وبدونه يرجع gzip يفكّه httpx سليماً (10046 حرفاً).
    """
    assert "Accept-Encoding" not in news_service._FETCH_HEADERS


def test_looks_like_prose_accepts_real_arabic_article() -> None:
    assert news_service._looks_like_prose(CLEAN_ARABIC) is True


def test_looks_like_prose_rejects_binary_garbage() -> None:
    assert news_service._looks_like_prose(GARBAGE_CONTENT) is False


def test_looks_like_prose_rejects_empty_or_whitespace() -> None:
    assert news_service._looks_like_prose("") is False
    assert news_service._looks_like_prose("   \n\t  ") is False


def test_fetch_discards_binary_garbage_content(monkeypatch: pytest.MonkeyPatch) -> None:
    """استجابة تنفك كنص خام يجب ألا تُحفظ كمحتوى مقال ولا تصل للمستخدم."""
    _install_fake_httpx(monkeypatch, default_get="<html><body></body></html>")
    monkeypatch.setattr(news_service, "trafilatura", _StaticExtractor(GARBAGE_CONTENT))

    content, _ = asyncio.run(
        news_service.fetch_article_content_and_resolve(PUBLISHER_URL)
    )

    assert content == ""
    assert "\x00" not in content


def test_detail_read_survives_failed_persist_without_breaking_session(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """فشل حفظ المحتوى يجب ألّا يحوّل الطلب إلى HTTP 500 (rollback ثم إعادة القراءة)."""
    article = NewsArticle(
        title="خبر",
        summary="ملخص",
        content=None,
        url=GOOGLE_URL,
        source_name="google",
        source_key="google",
        published_at=datetime.now(UTC) - timedelta(hours=1),
        is_active=True,
    )
    db_session.add(article)
    db_session.commit()
    article_id = article.id

    def _broken_commit() -> None:
        raise RuntimeError("simulated DataError")

    monkeypatch.setattr(db_session, "commit", _broken_commit)
    _patch_resolver(monkeypatch, (ARTICLE_TEXT, PUBLISHER_URL))

    result = asyncio.run(get_article_detail_content(db_session, article_id))

    assert result is not None
    db_session.rollback()


def test_resolve_google_news_url_rejects_result_still_on_google_news(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_httpx(
        monkeypatch,
        get_responses={STAGE1_URL: STAGE1_SHELL_HTML},
        post_response=STILL_GOOGLE_RESPONSE,
    )

    assert asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL)) is None


def test_resolve_google_news_url_returns_none_on_unparseable_batchexecute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_httpx(
        monkeypatch,
        get_responses={STAGE1_URL: STAGE1_SHELL_HTML},
        post_response=UNPARSEABLE_RESPONSE,
    )

    assert asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL)) is None


def test_resolve_google_news_url_returns_none_when_stage1_lacks_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record, posts = _install_fake_httpx(monkeypatch, default_get=CONSENT_HTML)

    assert asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL)) is None
    # مرحلة 1 وحدها (لا POST، ولا إعادة محاولة على شكل غير متوقع)
    assert record == [("GET", STAGE1_URL)]
    assert posts == []


def test_resolve_google_news_url_retries_stage1_once_on_transient_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record, _ = _install_fake_httpx(
        monkeypatch,
        get_responses={STAGE1_URL: STAGE1_SHELL_HTML},
        post_response=STAGE2_RESPONSE,
        fail_first_gets=1,
    )

    resolved = asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL))

    assert resolved == PUBLISHER_ARTICLE_URL
    gets = [entry for entry in record if entry[0] == "GET"]
    assert len(gets) == 2


def test_resolve_google_news_url_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_httpx(monkeypatch, raise_on_get=RuntimeError)

    assert asyncio.run(news_service.resolve_google_news_url(GOOGLE_URL)) is None


def test_resolver_ignores_non_google_news_url(monkeypatch: pytest.MonkeyPatch) -> None:
    record, posts = _install_fake_httpx(monkeypatch, default_get=CONSENT_HTML)

    assert asyncio.run(news_service.resolve_google_news_url(PUBLISHER_URL)) is None
    # لا يُرسل أي طلب شبكة على الأصلاً
    assert record == []
    assert posts == []


def test_resolver_returns_none_for_google_news_non_article_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record, _ = _install_fake_httpx(monkeypatch)

    search_url = "https://news.google.com/rss/search?q=stocks"
    assert asyncio.run(news_service.resolve_google_news_url(search_url)) is None
    assert record == []


# ─── دمج الفك مع جلب المحتوى ──────────────────────────────────────────────────


def test_fetch_with_resolution_uses_resolved_publisher_url(monkeypatch: pytest.MonkeyPatch) -> None:
    record, posts = _install_fake_httpx(
        monkeypatch,
        get_responses={
            STAGE1_URL: STAGE1_SHELL_HTML,
            PUBLISHER_ARTICLE_URL: PUBLISHER_HTML,
        },
        post_response=STAGE2_RESPONSE,
    )

    content, final_url = asyncio.run(
        news_service.fetch_article_content_and_resolve(GOOGLE_URL, resolve_google_news=True)
    )

    assert final_url == PUBLISHER_ARTICLE_URL
    assert "ارتفع مؤشر البورصة" in content
    assert not news_service.is_consent_page(content)
    assert posts != []
    # لا يُجلب أبداً صفحة news.google.com بعد نجاح الفك
    assert all(not url.startswith("https://news.google.com/articles/") for _, url in record)


def test_crawl_time_fetch_does_not_resolve_google_news(monkeypatch: pytest.MonkeyPatch) -> None:
    """استدعاء الزحف (بدون الخيار resolve_google_news) لا يفك الرابط إطلاقاً."""
    record, posts = _install_fake_httpx(monkeypatch, default_get=CONSENT_HTML)

    content, final_url = asyncio.run(news_service.fetch_article_content_and_resolve(GOOGLE_URL))

    assert content == ""
    assert final_url == GOOGLE_URL
    # طلب واحد مباشر فقط: لا طلب للمرحلة 1 ولا POST إلى batchexecute
    assert record == [("GET", GOOGLE_URL)]
    assert posts == []


def test_crawler_extract_contents_does_not_resolve_google_news(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record, posts = _install_fake_httpx(monkeypatch, default_get=CONSENT_HTML)
    monkeypatch.setattr(news_service, "trafilatura", _StaticExtractor(CONSENT_TEXT))
    articles = [{"url": GOOGLE_URL, "content": None}]

    asyncio.run(news_crawler._extract_contents(articles))

    assert posts == []
    assert articles[0]["url"] == GOOGLE_URL
    # صفحة الموافقة تُرفض ولا تُخزَّن كمحتوى
    assert articles[0]["content"] == ""
    assert record == [("GET", GOOGLE_URL)]


def test_detail_path_resolves_and_stores_publisher_content(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session)
    _install_fake_httpx(
        monkeypatch,
        get_responses={
            STAGE1_URL: STAGE1_SHELL_HTML,
            PUBLISHER_ARTICLE_URL: PUBLISHER_HTML,
        },
        post_response=STAGE2_RESPONSE,
    )

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.resolved_url == PUBLISHER_ARTICLE_URL
    assert response.url == GOOGLE_URL
    assert "ارتفع مؤشر البورصة" in (response.content or "")

    db_session.refresh(article)
    assert article.resolved_url == PUBLISHER_ARTICLE_URL
    assert article.url == GOOGLE_URL
    assert "ارتفع مؤشر البورصة" in (article.content or "")


# ─── حارس صفحة الموافقة (consent guard) ───────────────────────────────────────


def test_consent_guard_detects_arabic_before_continue_marker() -> None:
    assert news_service.is_consent_page("قبل المتابعة إلى Google لاختيار لغتك المفضلة") is True


def test_consent_guard_detects_cookie_and_google_marker() -> None:
    text = "We use cookie files and Google technologies to personalize your experience."
    assert news_service.is_consent_page(text) is True


def test_consent_guard_detects_multiline_language_list() -> None:
    assert news_service.is_consent_page(LANGUAGE_LIST_TEXT) is True


def test_consent_guard_detects_slash_separated_language_list() -> None:
    assert news_service.is_consent_page(SLASH_LANGUAGE_LIST_TEXT) is True


def test_consent_guard_accepts_normal_article_text() -> None:
    normal = (
        "ارتفع مؤشر البورصة المصرية بنسبة 1.2 في المئة خلال تعاملات اليوم "
        "مدعوماً بصفقات الشراء من المؤسسات الأجنبية الكبرى."
    )
    assert news_service.is_consent_page(normal) is False
    assert news_service.is_consent_page("") is False


def test_consent_page_content_is_never_stored_on_detail_read(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session)
    # مرحلة 1 ترجع صفحة موافقة (بدون توقيع) → فشل الفك → المسار القديم يرجع صفحة الموافقة
    record, posts = _install_fake_httpx(monkeypatch, default_get=CONSENT_HTML)
    monkeypatch.setattr(news_service, "trafilatura", _StaticExtractor(CONSENT_TEXT))

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.content is None
    assert posts == []
    assert record == [("GET", STAGE1_URL), ("GET", GOOGLE_URL)]

    db_session.refresh(article)
    assert article.content is None
    assert article.resolved_url is None


def test_detail_read_discards_previously_stored_consent_content(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session, content=CONSENT_TEXT)
    _patch_resolver(monkeypatch, (ARTICLE_TEXT, PUBLISHER_URL))

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.content == ARTICLE_TEXT

    db_session.refresh(article)
    assert article.content == ARTICLE_TEXT


def test_detail_read_clears_stored_consent_when_refetch_yields_nothing(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session, content=CONSENT_TEXT)
    _patch_resolver(monkeypatch, ("", GOOGLE_URL))

    response = asyncio.run(get_article_detail_content(db_session, article.id))

    assert response is not None
    assert response.content is None
    assert response.resolved_url is None

    db_session.refresh(article)
    assert article.content is None
    assert article.resolved_url is None


# ─── ترتيب فك الكيانات قبل إزالة الوسوم ───────────────────────────────────────


def test_rss_summary_unescapes_entities_before_stripping_tags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_httpx(monkeypatch, default_get=RSS_XML)

    articles = asyncio.run(news_service.fetch_rss_source(RSS_SOURCE))

    assert len(articles) == 1
    summary = articles[0]["summary"]
    assert summary == "نص المالي الأول"
    assert "nbsp;" not in summary
    assert "\xa0" not in summary


# ─── شكل الـ JSON عبر الـ API ─────────────────────────────────────────────────


def test_api_list_and_detail_expose_resolved_url(
    db_session: Session,
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    article = _seed_article(db_session)

    listing = client.get("/api/v1/news")
    assert listing.status_code == 200
    listed = listing.json()["items"][0]
    assert listed["resolved_url"] is None
    assert listed["url"] == GOOGLE_URL

    _patch_resolver(monkeypatch, (ARTICLE_TEXT, PUBLISHER_URL))

    detail = client.get(f"/api/v1/news/{article.id}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["resolved_url"] == PUBLISHER_URL
    assert payload["url"] == GOOGLE_URL

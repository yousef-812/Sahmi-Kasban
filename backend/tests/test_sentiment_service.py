from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, WalletAccount
from app.models.news import NewsArticle, NewsArticleTicker
from app.services.sentiment import compute_symbol_sentiment
from app.services.stock_analysis import execute_stock_analysis

TICKER = "COMI"


def _seed_article(
    db: Session,
    *,
    title: str,
    summary: str = "",
    hours_ago: float = 24.0,
    url: str,
    sentiment: str | None = None,
    ticker: str = TICKER,
    relevance: float = 1.0,
) -> NewsArticle:
    article = NewsArticle(
        title=title,
        summary=summary,
        url=url,
        source_name="test-source",
        source_key="test",
        published_at=datetime.now(UTC) - timedelta(hours=hours_ago),
        sentiment=sentiment,
    )
    db.add(article)
    db.flush()
    db.add(NewsArticleTicker(article_id=article.id, ticker=ticker, relevance_score=relevance))
    db.commit()
    return article


# ─── compute_symbol_sentiment ────────────────────────────────────────────────


def test_no_articles_returns_insufficient_neutral(db_session: Session) -> None:
    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["ticker"] == TICKER
    assert result["score"] == 0.0
    assert result["sample_size"] == 0
    assert result["coverage"] == "insufficient"
    assert isinstance(result["as_of"], datetime)


def test_lexicon_scores_positive_english_headline(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="Company reports record profits and rising dividends",
        url="https://example.com/positive-en",
        hours_ago=6,
    )

    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["sample_size"] == 1
    assert result["score"] > 0.0
    assert result["coverage"] == "low"


def test_lexicon_scores_positive_arabic_headline(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="ارتفعت أرباح الشركة وتتوقع نموا قويا",
        url="https://example.com/positive-ar",
        hours_ago=6,
    )

    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["sample_size"] == 1
    assert result["score"] > 0.0


def test_lexicon_scores_negative_headline(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="Shares crash as company posts heavy losses",
        url="https://example.com/negative-en",
        hours_ago=6,
    )

    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["score"] < 0.0


def test_stored_sentiment_label_overrides_lexicon(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="Company reports record profits and rising dividends",
        url="https://example.com/labeled-negative",
        hours_ago=6,
        sentiment="negative",
    )

    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["score"] < 0.0


def test_decay_recent_negative_outweighs_old_positive(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="Company reports record profits and rising dividends",
        url="https://example.com/old-positive",
        hours_ago=6.5 * 24,
    )
    _seed_article(
        db_session,
        title="Shares crash as company posts heavy losses",
        url="https://example.com/recent-negative",
        hours_ago=0.5 * 24,
    )

    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["sample_size"] == 2
    assert result["score"] < 0.0


def test_coverage_normal_requires_ten_samples(db_session: Session) -> None:
    for index in range(10):
        _seed_article(
            db_session,
            title="Company reports record profits",
            url=f"https://example.com/normal-{index}",
            hours_ago=index + 1,
        )

    result = compute_symbol_sentiment(db_session, TICKER)

    assert result["sample_size"] == 10
    assert result["coverage"] == "normal"


def test_window_days_filters_old_articles(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="Company reports record profits",
        url="https://example.com/old",
        hours_ago=20 * 24,
    )

    result = compute_symbol_sentiment(db_session, TICKER, days=7)

    assert result["sample_size"] == 0
    assert result["coverage"] == "insufficient"


def test_sentiment_is_deterministic_for_same_articles(db_session: Session) -> None:
    _seed_article(
        db_session,
        title="Company reports record profits and rising dividends",
        url="https://example.com/deterministic",
        hours_ago=12,
    )

    first = compute_symbol_sentiment(db_session, TICKER)
    second = compute_symbol_sentiment(db_session, TICKER)

    assert first["score"] == second["score"]
    assert first["sample_size"] == second["sample_size"]


# ─── GET /stocks/{ticker}/sentiment ─────────────────────────────────────────


def test_sentiment_endpoint_public_shape(client: TestClient, db_session: Session) -> None:
    response = client.get(f"/api/v1/stocks/{TICKER}/sentiment")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == TICKER
    assert payload["score"] == 0.0
    assert payload["sample_size"] == 0
    assert payload["coverage"] == "insufficient"
    assert payload["window_days"] == 7
    assert "as_of" in payload


def test_sentiment_endpoint_reflects_stored_articles(
    client: TestClient,
    db_session: Session,
) -> None:
    _seed_article(
        db_session,
        title="Company reports record profits and rising dividends",
        url="https://example.com/endpoint-positive",
        hours_ago=6,
    )

    response = client.get(f"/api/v1/stocks/{TICKER}/sentiment", params={"days": 7})

    assert response.status_code == 200
    payload = response.json()
    assert payload["sample_size"] == 1
    assert payload["score"] > 0.0
    assert payload["coverage"] == "low"


def test_sentiment_endpoint_rejects_invalid_ticker_and_days(client: TestClient) -> None:
    assert client.get("/api/v1/stocks/bad!!ticker/sentiment").status_code == 404
    assert client.get(f"/api/v1/stocks/{TICKER}/sentiment", params={"days": 0}).status_code == 422


# ─── stock_analysis wiring ──────────────────────────────────────────────────


class FakeMarketDataProvider:
    name = "fake"

    def __init__(self) -> None:
        self.calls = 0

    async def get_history(self, ticker: str, *, period: str, interval: str):
        from app.market_data.types import CandleSeries

        self.calls += 1
        start = datetime(2025, 9, 1, tzinfo=UTC)
        candles: list[dict[str, object]] = []
        for index in range(220):
            close = 100 + (index * 0.15) + ((index % 7) * 0.05)
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": round(close - 0.3, 6),
                    "high": round(close + 0.8, 6),
                    "low": round(close - 0.9, 6),
                    "close": round(close, 6),
                    "volume": 1_000_000 + (index * 1000),
                }
            )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 25, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="b" * 64,
            candles=tuple(candles),
        )


class FakeStockAIService:
    async def explain_stock_analysis(self, *, ticker: str, analysis_payload: dict, language: str = "ar") -> str:
        return f"AI explanation for {ticker} in {language}"


def _seed_user(db: Session, *, balance_points: int = 1000) -> User:
    user = User(
        email="sentiment-wiring@example.com",
        password_hash="hashed-password",
        display_name="Sentiment User",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
        auth_version=0,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=balance_points))
    db.commit()
    return user


def _news_engine_from_execution(execution) -> dict:
    payload = execution.analysis.payload
    engines = payload["analysis"]["engines"]
    assert "news_sentiment" in engines
    return engines["news_sentiment"]


def test_wiring_passes_news_sentiment_context_keys(
    db_session: Session,
    monkeypatch,
) -> None:
    user = _seed_user(db_session)
    fake_result: dict[str, object] = {
        "ticker": TICKER,
        "score": 0.8,
        "sample_size": 12,
        "coverage": "normal",
        "as_of": datetime.now(UTC),
        "window_days": 7,
    }
    monkeypatch.setattr(
        "app.services.stock_analysis.compute_symbol_sentiment",
        lambda db, ticker, *, days=7: fake_result,
    )

    execution = asyncio.run(
        execute_stock_analysis(
            db_session,
            user=user,
            ticker=TICKER,
            provider=FakeMarketDataProvider(),
            ai_service=FakeStockAIService(),
        )
    )

    news_engine = _news_engine_from_execution(execution)
    assert news_engine["details"]["sentiment"] == 0.8
    assert news_engine["details"]["sample_size"] == 12
    assert news_engine["details"]["coverage"] == "normal"
    assert news_engine["score"] == 90.0


def test_wiring_without_articles_stays_neutral(db_session: Session) -> None:
    user = _seed_user(db_session)

    execution = asyncio.run(
        execute_stock_analysis(
            db_session,
            user=user,
            ticker=TICKER,
            provider=FakeMarketDataProvider(),
            ai_service=FakeStockAIService(),
        )
    )

    news_engine = _news_engine_from_execution(execution)
    assert news_engine["details"]["sentiment"] == 0.0
    assert news_engine["details"]["sample_size"] == 0
    assert news_engine["details"]["coverage"] == "insufficient"
    assert news_engine["score"] == 50.0


def test_wiring_survives_sentiment_failure(db_session: Session, monkeypatch) -> None:
    user = _seed_user(db_session)

    def _boom(db, ticker, *, days=7):
        raise RuntimeError("sentiment backend exploded")

    monkeypatch.setattr("app.services.stock_analysis.compute_symbol_sentiment", _boom)

    execution = asyncio.run(
        execute_stock_analysis(
            db_session,
            user=user,
            ticker=TICKER,
            provider=FakeMarketDataProvider(),
            ai_service=FakeStockAIService(),
        )
    )

    news_engine = _news_engine_from_execution(execution)
    assert news_engine["details"]["coverage"] == "insufficient"
    assert news_engine["score"] == 50.0
    assert execution.cached is False

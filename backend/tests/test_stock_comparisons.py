from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.models import StockComparison, Subscription
from app.services.stock_analysis import get_stock_ai_service

PASSWORD = "StrongPass123"


class ComparisonMarketDataProvider:
    name = "comparison-fake"

    def __init__(self, *, fail_ticker: str | None = None) -> None:
        self.calls = 0
        self.fail_ticker = fail_ticker

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        if ticker.upper() == self.fail_ticker:
            raise MarketDataUnavailableError(f"temporary failure for {ticker}")
        start = datetime(2025, 9, 1, tzinfo=UTC)
        ticker_bias = 0.08 if ticker.upper() == "COMI" else 0.04
        candles = []
        for index in range(220):
            close = 40 + (index * ticker_bias) + ((index % 6) * 0.03)
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": close - 0.15,
                    "high": close + 0.55,
                    "low": close - 0.65,
                    "close": close,
                    "volume": 1_200_000 + (index * 1_100),
                }
            )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 28, 18, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(candles[-1]["timestamp"]),
            fingerprint=("a" if ticker.upper() == "COMI" else "b") * 64,
            candles=tuple(candles),
        )


class ComparisonAIService:
    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict,
        language: str = "ar",
    ) -> str:
        del analysis_payload
        return f"شرح {ticker} باللغة {language}"


def _register_login(client: TestClient, fake_email_service, email: str) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": "Comparison User",
        },
    )
    assert registered.status_code == 201
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verified.status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _install(provider: ComparisonMarketDataProvider) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_stock_ai_service] = lambda: ComparisonAIService()


def test_free_comparison_charges_once_and_reuses_owned_analyses(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = ComparisonMarketDataProvider()
    _install(provider)
    headers = _register_login(client, fake_email_service, "free-compare@example.com")
    payload = {
        "request_key": "comparison_free_001",
        "tickers": ["COMI", "DSCW"],
        "language": "ar",
    }

    first = client.post("/api/v1/market/comparisons", headers=headers, json=payload)
    repeated = client.post("/api/v1/market/comparisons", headers=headers, json=payload)

    assert first.status_code == 200
    result = first.json()
    assert result["idempotent"] is False
    assert result["included_allowance"] is False
    assert result["comparison_charged_points"] == 50
    assert result["analysis_charged_points"] == 100
    assert result["balance_points"] == 850
    assert len(result["items"]) == 2
    assert result["failed_items"] == []
    assert result["items"][0]["rank"] == 1
    assert result["best_ticker"] in {"COMI", "DSCW"}
    assert "{" not in result["summary"]

    assert repeated.status_code == 200
    assert repeated.json()["idempotent"] is True
    assert repeated.json()["balance_points"] == 850
    assert provider.calls == 4
    assert len(db_session.scalars(select(StockComparison)).all()) == 1


def test_comparison_keeps_two_results_when_one_ticker_temporarily_fails(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = ComparisonMarketDataProvider(fail_ticker="DSCW")
    _install(provider)
    headers = _register_login(client, fake_email_service, "partial-compare@example.com")

    response = client.post(
        "/api/v1/market/comparisons",
        headers=headers,
        json={
            "request_key": "comparison_partial_001",
            "tickers": ["COMI", "DSCW", "SWDY"],
            "language": "ar",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2
    assert payload["failed_items"] == [
        {
            "ticker": "DSCW",
            "code": "market_data_unavailable",
            "message": "بيانات السوق غير متاحة لهذا السهم حاليًا.",
            "retryable": True,
        }
    ]
    assert "DSCW" in payload["summary"]
    assert payload["analysis_charged_points"] == 100
    assert payload["comparison_charged_points"] == 50
    assert payload["balance_points"] == 850
    assert provider.calls == 5
    assert len(db_session.scalars(select(StockComparison)).all()) == 1


def test_basic_plan_uses_included_monthly_comparison(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = ComparisonMarketDataProvider()
    _install(provider)
    headers = _register_login(client, fake_email_service, "basic-compare@example.com")
    subscription = db_session.scalar(select(Subscription).where(Subscription.plan_code == "free"))
    assert subscription is not None
    subscription.plan_code = "basic"
    subscription.weekly_points = 2_500
    subscription.ads_enabled = False
    db_session.commit()

    response = client.post(
        "/api/v1/market/comparisons",
        headers=headers,
        json={
            "request_key": "comparison_basic_001",
            "tickers": ["COMI", "DSCW"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["included_allowance"] is True
    assert payload["comparison_charged_points"] == 0
    assert payload["analysis_charged_points"] == 100
    assert payload["allowance_used"] == 1
    assert payload["allowance_remaining"] == 3
    assert payload["balance_points"] == 900

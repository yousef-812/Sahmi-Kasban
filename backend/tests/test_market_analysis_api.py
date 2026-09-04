from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sahmi_kasban.ai import AIProviderError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.models import MarketDataSnapshot, StockAnalysis, WalletAccount, WalletEntry
from app.services.stock_analysis import get_stock_ai_service

PASSWORD = "StrongPass123"


class FakeMarketDataProvider:
    name = "fake"

    def __init__(self) -> None:
        self.calls = 0

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
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
            fingerprint="a" * 64,
            candles=tuple(candles),
        )


class FailingMarketDataProvider(FakeMarketDataProvider):
    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        raise MarketDataUnavailableError("provider unavailable")


class FakeStockAIService:
    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict,
        language: str = "ar",
    ) -> str:
        return f"AI explanation for {ticker} in {language}"


class FailingStockAIService(FakeStockAIService):
    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict,
        language: str = "ar",
    ) -> str:
        raise AIProviderError("AI unavailable")


def register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str = "analyst@example.com",
) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": "Market Analyst",
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


def install_market_dependencies(provider, ai_service) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_stock_ai_service] = lambda: ai_service


def test_market_instrument_registry_is_deduplicated(client: TestClient) -> None:
    response = client.get("/api/v1/market/instruments", params={"limit": 200})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] in ("legacy_seed_registry", "tradingview_scanner")
    assert payload["total_registry_size"] >= 155
    tickers = [item["ticker"] for item in payload["items"]]
    assert len(tickers) == len(set(tickers))
    assert "DSCW" in tickers
    assert all(item["provider_symbol"].startswith("EGX:") for item in payload["items"])


def test_analysis_charges_after_success_then_reuses_cache_for_free(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = FakeMarketDataProvider()
    install_market_dependencies(provider, FakeStockAIService())
    headers = register_and_login(client, fake_email_service)

    first = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["cached"] is False
    assert first_payload["market_snapshot_cached"] is False
    assert first_payload["charged_points"] == 50
    assert first_payload["charged_coins"] == "0.50"
    assert first_payload["balance_points"] == 950
    assert first_payload["payload"]["explanation_source"] == "ai"

    second = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["analysis_id"] == first_payload["analysis_id"]
    assert second_payload["cached"] is True
    assert second_payload["market_snapshot_cached"] is True
    assert second_payload["charged_points"] == 0
    assert second_payload["balance_points"] == 950
    assert provider.calls == 2

    analyses = db_session.scalars(select(StockAnalysis)).all()
    snapshots = db_session.scalars(select(MarketDataSnapshot)).all()
    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.entry_type == "stock_analysis_debit")
    ).all()
    assert len(analyses) == 1
    assert len(snapshots) == 2
    assert len(debits) == 1
    assert debits[0].amount_points == -50


def test_insufficient_balance_does_not_persist_analysis_or_debit(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = FakeMarketDataProvider()
    install_market_dependencies(provider, FakeStockAIService())
    headers = register_and_login(client, fake_email_service)
    wallet = db_session.scalar(select(WalletAccount))
    assert wallet is not None
    wallet.balance_points = 0
    db_session.commit()

    response = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert response.status_code == 402
    assert db_session.scalars(select(StockAnalysis)).all() == []
    assert db_session.scalars(select(MarketDataSnapshot)).all() == []
    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.entry_type == "stock_analysis_debit")
    ).all()
    assert debits == []


def test_provider_failure_does_not_charge_user(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = FailingMarketDataProvider()
    install_market_dependencies(provider, FakeStockAIService())
    headers = register_and_login(client, fake_email_service)

    response = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert response.status_code == 409
    assert "بيانات السهم غير متاحة مؤقتًا" in response.json()["detail"]
    wallet = db_session.scalar(select(WalletAccount))
    assert wallet is not None
    assert wallet.balance_points == 1_000
    assert db_session.scalars(select(StockAnalysis)).all() == []


def test_ai_failure_uses_deterministic_explanation_and_still_completes(
    client: TestClient,
    fake_email_service,
) -> None:
    provider = FakeMarketDataProvider()
    install_market_dependencies(provider, FailingStockAIService())
    headers = register_and_login(client, fake_email_service)

    response = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["charged_points"] == 50
    assert payload["payload"]["explanation_source"] == "deterministic"
    assert "نتيجة المحركات" in payload["payload"]["explanation"]


def test_unknown_ticker_is_rejected_before_provider_call(
    client: TestClient,
    fake_email_service,
) -> None:
    provider = FakeMarketDataProvider()
    install_market_dependencies(provider, FakeStockAIService())
    headers = register_and_login(client, fake_email_service)

    response = client.post(
        "/api/v1/stocks/UNKNOWN/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert response.status_code == 404
    assert provider.calls == 0

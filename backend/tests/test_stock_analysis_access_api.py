from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries
from app.models import UserStockAnalysisAccess, WalletEntry
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
            fingerprint="b" * 64,
            candles=tuple(candles),
        )


class FakeStockAIService:
    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict,
        language: str = "ar",
    ) -> str:
        return f"AI explanation for {ticker} in {language}"


def register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str,
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


def test_saved_analysis_is_server_persistent_and_account_scoped(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = FakeMarketDataProvider()
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_stock_ai_service] = lambda: FakeStockAIService()

    first_headers = register_and_login(
        client,
        fake_email_service,
        email="first@example.com",
    )
    first = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=first_headers,
        json={"language": "ar"},
    )
    assert first.status_code == 200
    assert first.json()["charged_points"] == 50

    # This GET uses only the authenticated account and the database. It models
    # opening the app after reinstalling it with no local analysis cache.
    restored = client.get(
        "/api/v1/stocks/COMI/analysis/latest",
        headers=first_headers,
    )
    assert restored.status_code == 200
    assert restored.json()["analysis_id"] == first.json()["analysis_id"]
    assert restored.json()["charged_points"] == 0

    second_headers = register_and_login(
        client,
        fake_email_service,
        email="second@example.com",
    )
    unavailable_to_other_account = client.get(
        "/api/v1/stocks/COMI/analysis/latest",
        headers=second_headers,
    )
    assert unavailable_to_other_account.status_code == 404

    second = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=second_headers,
        json={"language": "ar"},
    )
    assert second.status_code == 200
    assert second.json()["analysis_id"] == first.json()["analysis_id"]
    assert second.json()["charged_points"] == 50
    assert provider.calls == 1

    accesses = db_session.scalars(select(UserStockAnalysisAccess)).all()
    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.entry_type == "stock_analysis_debit")
    ).all()
    assert len(accesses) == 2
    assert len({access.user_id for access in accesses}) == 2
    assert len(debits) == 2

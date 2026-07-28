from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries
from app.models import MarketDataSnapshot, StockAnalysis, WalletAccount, WalletEntry
from app.services.stock_analysis import get_stock_ai_service

PASSWORD = "StrongPass123"


class StableMarketDataProvider:
    name = "stable-fake"

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
            close = 80 + (index * 0.12) + ((index % 5) * 0.04)
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": round(close - 0.2, 6),
                    "high": round(close + 0.7, 6),
                    "low": round(close - 0.8, 6),
                    "close": round(close, 6),
                    "volume": 900_000 + (index * 900),
                }
            )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 25, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="c" * 64,
            candles=tuple(candles),
        )


class BrokenCandleProvider(StableMarketDataProvider):
    name = "broken-fake"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        start = datetime(2025, 9, 1, tzinfo=UTC)
        candles = tuple(
            {
                "timestamp": (start + timedelta(days=index)).isoformat(),
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1_000_000,
            }
            for index in range(220)
        )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 25, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="d" * 64,
            candles=candles,
        )


class FakeStockAIService:
    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict,
        language: str = "ar",
    ) -> str:
        return f"Analysis for {ticker} in {language}"


def install_dependencies(provider) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_stock_ai_service] = lambda: FakeStockAIService()


def register_and_login(
    client: TestClient,
    fake_email_service,
    email: str,
) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": "Analysis User",
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


def test_shared_analysis_cache_charges_once_per_account(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = StableMarketDataProvider()
    install_dependencies(provider)
    first_headers = register_and_login(client, fake_email_service, "first-cache@example.com")
    second_headers = register_and_login(client, fake_email_service, "second-cache@example.com")

    first = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=first_headers,
        json={"language": "ar"},
    )
    second = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=second_headers,
        json={"language": "ar"},
    )

    assert first.status_code == 200
    assert first.json()["charged_points"] == 50
    assert first.json()["balance_points"] == 250
    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert second.json()["charged_points"] == 50
    assert second.json()["balance_points"] == 250
    assert provider.calls == 1

    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.entry_type == "stock_analysis_debit")
    ).all()
    wallets = db_session.scalars(
        select(WalletAccount).order_by(WalletAccount.balance_points)
    ).all()
    assert len(debits) == 2
    assert [wallet.balance_points for wallet in wallets] == [250, 250]


def test_core_engine_failure_rolls_back_snapshot_analysis_and_debit(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = BrokenCandleProvider()
    install_dependencies(provider)
    headers = register_and_login(client, fake_email_service, "broken-engine@example.com")

    response = client.post(
        "/api/v1/stocks/COMI/analysis",
        headers=headers,
        json={"language": "ar"},
    )

    assert response.status_code == 422
    wallet = db_session.scalar(select(WalletAccount))
    assert wallet is not None
    assert wallet.balance_points == 300
    assert db_session.scalars(select(MarketDataSnapshot)).all() == []
    assert db_session.scalars(select(StockAnalysis)).all() == []
    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.entry_type == "stock_analysis_debit")
    ).all()
    assert debits == []

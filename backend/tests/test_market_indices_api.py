from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.indices import (
    SUPPORTED_INDICES,
)
from app.market_data.provider import get_market_data_provider
from app.market_data.quotes import MarketQuote
from app.market_data.types import CandleSeries
from app.models import StockAnalysis, WalletEntry
from app.services.stock_analysis import get_stock_ai_service

PASSWORD = "StrongPass123"


class FakeIndexProvider:
    name = "fake"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        start = datetime(2025, 9, 1, tzinfo=UTC)
        candles: list[dict[str, object]] = []
        for index in range(220):
            close = 10_000 + (index * 2.0) + ((index % 7) * 0.5)
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": round(close - 2.0, 6),
                    "high": round(close + 4.0, 6),
                    "low": round(close - 4.0, 6),
                    "close": round(close, 6),
                    "volume": 20_000_000 + (index * 5_000),
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


def _install_dependencies(provider, ai_service) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_stock_ai_service] = lambda: ai_service


def _register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str = "index@example.com",
) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": "Index Watcher",
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


def test_supported_indices_cover_main_egx_indices() -> None:
    tickers = {info.ticker for info in SUPPORTED_INDICES}
    assert {"EGX30", "EGX70", "EGX100"} <= tickers
    for info in SUPPORTED_INDICES:
        assert info.tradingview_symbol.startswith("EGX:")


def test_index_quote_parser_skips_unknown_symbols() -> None:
    payload = {
        "data": [
            {"s": "EGX:EGX30", "d": ["EGX30", "مؤشر EGX30", 32000.0, 31900.0, 32100.0, 31850.0, 0.5, 160.0, 50_000_000]},
            {"s": "EGX:FAKE99", "d": ["FAKE99", "غريب", 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]},
        ]
    }
    from app.market_data.indices import _parse_scanner_rows

    parsed = _parse_scanner_rows(payload)
    assert len(parsed) == 1
    quote = parsed[0]
    assert isinstance(quote, MarketQuote)
    assert quote.ticker == "EGX30"
    assert quote.current_price == 32000.0
    assert quote.change_percent == 0.5


def test_index_analysis_charges_and_reuses(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = FakeIndexProvider()
    _install_dependencies(provider, FakeStockAIService())
    headers = _register_and_login(client, fake_email_service)

    first = client.post(
        "/api/v1/market/indices/EGX30/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["ticker"] == "EGX30"
    assert first_payload["cached"] is False
    assert first_payload["charged_points"] == 50
    assert first_payload["payload"].get("is_index") is True
    assert "analysis" in first_payload["payload"]

    second = client.post(
        "/api/v1/market/indices/EGX30/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["analysis_id"] == first_payload["analysis_id"]
    assert second_payload["cached"] is True
    assert second_payload["charged_points"] == 0

    latest = client.get(
        "/api/v1/market/indices/EGX30/analysis/latest",
        headers=headers,
    )
    assert latest.status_code == 200
    assert latest.json()["analysis_id"] == first_payload["analysis_id"]

    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.reference_type == "index_analysis")
    ).all()
    assert len(debits) == 1
    assert debits[0].amount_points == -50
    analyses = db_session.scalars(select(StockAnalysis)).all()
    assert len(analyses) == 1
    assert analyses[0].ticker == "EGX30"


def test_index_analysis_rejects_unknown_index(
    client: TestClient,
    fake_email_service,
) -> None:
    provider = FakeIndexProvider()
    _install_dependencies(provider, FakeStockAIService())
    headers = _register_and_login(client, fake_email_service)

    response = client.post(
        "/api/v1/market/indices/EGX999/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert response.status_code == 404


def test_index_analysis_insufficient_balance(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    provider = FakeIndexProvider()
    _install_dependencies(provider, FakeStockAIService())
    headers = _register_and_login(client, fake_email_service)
    from app.models import WalletAccount

    wallet = db_session.scalar(select(WalletAccount))
    assert wallet is not None
    wallet.balance_points = 0
    db_session.commit()

    response = client.post(
        "/api/v1/market/indices/EGX70/analysis",
        headers=headers,
        json={"language": "ar"},
    )
    assert response.status_code == 402
    assert db_session.scalars(select(StockAnalysis)).all() == []
    debits = db_session.scalars(
        select(WalletEntry).where(WalletEntry.reference_type == "index_analysis")
    ).all()
    assert debits == []
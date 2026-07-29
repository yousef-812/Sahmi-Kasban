from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries

PASSWORD = "StrongPass123"


class FakeAdminBacktestProvider:
    name = "fake-admin-backtest"

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
        start = datetime(2024, 1, 1, tzinfo=UTC)
        candles: list[dict[str, object]] = []
        for index in range(260):
            close = 75 + index * 0.09 + ((index % 7) - 3) * 0.06
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": round(close - 0.2, 6),
                    "high": round(close + 0.7, 6),
                    "low": round(close - 0.8, 6),
                    "close": round(close, 6),
                    "volume": 950_000 + index * 900,
                }
            )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 29, 12, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="b" * 64,
            candles=tuple(candles),
        )


def _register_and_login(
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
            "display_name": "Backtest Admin",
            "avatar_key": "avatar_03",
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


def test_backtest_admin_endpoints_are_protected_and_versioned(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    del db_session
    admin_email = "backtest-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers = _register_and_login(
        client,
        fake_email_service,
        email=admin_email,
    )
    user_headers = _register_and_login(
        client,
        fake_email_service,
        email="backtest-user@example.com",
    )
    provider = FakeAdminBacktestProvider()
    app.dependency_overrides[get_market_data_provider] = lambda: provider

    forbidden = client.get(
        "/api/v1/admin/operations/backtests/runs",
        headers=user_headers,
    )
    assert forbidden.status_code == 403

    created = client.post(
        "/api/v1/admin/operations/backtests/runs",
        headers=admin_headers,
        json={
            "request_key": "admin-corev2-history-001",
            "tickers": ["COMI"],
            "period": "5y",
            "min_train_size": 200,
            "horizon_sessions": 5,
            "step_sessions": 20,
        },
    )
    assert created.status_code == 200
    payload = created.json()
    assert payload["engine_version"] == "core-v2"
    assert payload["status"] == "complete"
    assert payload["completed_tickers"] == 1
    assert payload["results"][0]["observations"] == 3

    repeated = client.post(
        "/api/v1/admin/operations/backtests/runs",
        headers=admin_headers,
        json={
            "request_key": "admin-corev2-history-001",
            "tickers": ["COMI"],
            "period": "5y",
            "min_train_size": 200,
            "horizon_sessions": 5,
            "step_sessions": 20,
        },
    )
    assert repeated.status_code == 200
    assert repeated.json()["idempotent"] is True
    assert provider.calls == 1

    listed = client.get(
        "/api/v1/admin/operations/backtests/runs",
        headers=admin_headers,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    versions = client.get(
        "/api/v1/admin/operations/backtests/versions",
        headers=admin_headers,
    )
    assert versions.status_code == 200
    assert versions.json()["items"][0]["engine_version"] == "core-v2"
    assert versions.json()["items"][0]["observations"] == 3

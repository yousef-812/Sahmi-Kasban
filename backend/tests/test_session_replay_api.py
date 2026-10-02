from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries

PASSWORD = "StrongPass123"


class FakeIntradayProvider:
    name = "fake"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        assert period == "5d"
        assert interval in ("1m", "5m", "15m", "30m")
        base = datetime(2026, 9, 28, 8, 0, tzinfo=UTC)  # 10:00 Cairo
        candles: list[dict[str, object]] = []
        price = 100.0
        # Two sessions: older thin day + last full session (54 x 5m candles).
        for day_offset, count in ((0, 3), (1, 54)):
            for index in range(count):
                price += 0.05 if index % 3 else -0.02
                candles.append(
                    {
                        "timestamp": (
                            base + timedelta(days=day_offset, minutes=5 * index)
                        ).isoformat(),
                        "open": round(price - 0.05, 6),
                        "high": round(price + 0.08, 6),
                        "low": round(price - 0.09, 6),
                        "close": round(price, 6),
                        "volume": 10_000 + index * 100,
                    }
                )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 9, 30, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="c" * 64,
            candles=tuple(candles),
        )


def _register_and_login(client: TestClient, fake_email_service) -> dict[str, str]:
    email = "replay@example.com"
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": "Replay Watcher",
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


def test_session_replay_returns_last_full_session(
    client: TestClient, fake_email_service
) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: FakeIntradayProvider()
    try:
        headers = _register_and_login(client, fake_email_service)
        response = client.get(
            "/api/v1/market/session-replay",
            params={"ticker": "COMI", "interval": "5m"},
            headers=headers,
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["ticker"] == "COMI"
        assert payload["interval"] == "5m"
        assert payload["session_date"] == "2026-09-29"
        assert len(payload["candles"]) == 54
        first = payload["candles"][0]
        assert set(first) >= {"timestamp", "open", "high", "low", "close", "volume"}
    finally:
        app.dependency_overrides.pop(get_market_data_provider, None)


def test_session_replay_rejects_bad_interval(
    client: TestClient, fake_email_service
) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: FakeIntradayProvider()
    try:
        headers = _register_and_login(client, fake_email_service)
        response = client.get(
            "/api/v1/market/session-replay",
            params={"ticker": "COMI", "interval": "1d"},
            headers=headers,
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.pop(get_market_data_provider, None)


def test_session_replay_rejects_unknown_ticker(
    client: TestClient, fake_email_service
) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: FakeIntradayProvider()
    try:
        headers = _register_and_login(client, fake_email_service)
        response = client.get(
            "/api/v1/market/session-replay",
            params={"ticker": "ZZZZ", "interval": "5m"},
            headers=headers,
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_market_data_provider, None)

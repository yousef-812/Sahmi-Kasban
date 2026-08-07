from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.jobs import historical_replays as replay_worker
from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.types import CandleSeries

PASSWORD = "StrongPass123"


class CountingProvider:
    name = "counting-provider"

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
        start = datetime(2025, 1, 1, tzinfo=UTC)
        candles: list[dict[str, object]] = []
        for index in range(240):
            close = 25.0 + index * 0.03
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": close - 0.05,
                    "high": close + 0.2,
                    "low": close - 0.2,
                    "close": close,
                    "volume": 700_000 + index * 100,
                }
            )
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime.now(UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint="f" * 64,
            candles=tuple(candles),
        )


def _register_admin(
    client: TestClient,
    fake_email_service,
    monkeypatch,
    *,
    email: str,
) -> dict[str, str]:
    monkeypatch.setenv("ADMIN_EMAILS", email)
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": "Replay Admin",
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


def test_five_year_history_is_reused_from_persisted_snapshot(
    db_session: Session,
) -> None:
    provider = CountingProvider()
    current = datetime(2026, 7, 30, tzinfo=UTC)

    first, first_cached = asyncio.run(
        get_cached_or_fresh_history(
            db_session,
            provider,
            "COMI",
            period="5y",
            interval="1d",
            cache_minutes=24 * 60,
            min_candles=200,
            now=current,
        )
    )
    db_session.commit()
    second, second_cached = asyncio.run(
        get_cached_or_fresh_history(
            db_session,
            provider,
            "COMI",
            period="5y",
            interval="1d",
            cache_minutes=24 * 60,
            min_candles=200,
            now=current + timedelta(hours=1),
        )
    )

    assert first_cached is False
    assert second_cached is True
    assert provider.calls == 1
    assert second.fingerprint == first.fingerprint
    assert second.period == "5y"


def test_replay_can_pause_resume_and_cancel_without_running_on_api(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    headers = _register_admin(
        client,
        fake_email_service,
        monkeypatch,
        email="isolated-replay-admin@example.com",
    )
    today = date.today()
    created = client.post(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=headers,
        json={
            "request_key": "isolated-replay-control-0001",
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),
            "horizon_sessions": 5,
        },
    )
    assert created.status_code == 202
    payload = created.json()
    job_id = payload["id"]
    assert payload["worker_isolated"] is True
    assert payload["control_state"] == "pending"
    assert payload["can_pause"] is True

    paused = client.post(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}/pause",
        headers=headers,
    )
    assert paused.status_code == 200
    assert paused.json()["control_state"] == "paused"
    assert paused.json()["can_resume"] is True

    worker_sessions = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    monkeypatch.setattr(replay_worker, "SessionLocal", worker_sessions)
    assert asyncio.run(replay_worker.process_next_historical_replay_batch()) is False

    resumed = client.post(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}/resume",
        headers=headers,
    )
    assert resumed.status_code == 200
    assert resumed.json()["control_state"] == "pending"

    cancelled = client.post(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}/cancel",
        headers=headers,
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "failed"
    assert cancelled.json()["control_state"] == "cancelled"
    assert cancelled.json()["can_cancel"] is False


def test_replay_job_can_be_deleted_after_completion_and_blocks_while_active(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    headers = _register_admin(
        client,
        fake_email_service,
        monkeypatch,
        email="isolated-replay-delete-admin@example.com",
    )
    today = date.today()
    created = client.post(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=headers,
        json={
            "request_key": "isolated-replay-delete-0001",
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),
            "horizon_sessions": 5,
        },
    )
    assert created.status_code == 202
    job_id = created.json()["id"]

    active_delete = client.delete(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}",
        headers=headers,
    )
    assert active_delete.status_code == 409

    cancelled = client.post(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}/cancel",
        headers=headers,
    )
    assert cancelled.status_code == 200

    deleted = client.delete(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}",
        headers=headers,
    )
    assert deleted.status_code == 204

    missing = client.get(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}",
        headers=headers,
    )
    assert missing.status_code == 404


def test_multi_window_batch_queues_sequential_jobs_with_shared_cache(
    client: TestClient,
    fake_email_service,
    monkeypatch,
) -> None:
    headers = _register_admin(
        client,
        fake_email_service,
        monkeypatch,
        email="replay-batch-admin@example.com",
    )
    today = date.today()
    response = client.post(
        "/api/v1/admin/operations/historical-replays/batches",
        headers=headers,
        json={
            "request_key_prefix": "core-v22-validation",
            "windows": [
                {
                    "start_date": (today - timedelta(days=60)).isoformat(),
                    "end_date": (today - timedelta(days=40)).isoformat(),
                },
                {
                    "start_date": (today - timedelta(days=30)).isoformat(),
                    "end_date": (today - timedelta(days=10)).isoformat(),
                },
            ],
            "horizon_sessions": 5,
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["total"] == 2
    assert payload["shared_history_cache"] is True
    assert payload["execution_order"] == "sequential_windows_shared_ticker_cache"
    assert [item["request_key"] for item in payload["items"]] == [
        "core-v22-validation-01",
        "core-v22-validation-02",
    ]
    assert all(item["worker_isolated"] is True for item in payload["items"])

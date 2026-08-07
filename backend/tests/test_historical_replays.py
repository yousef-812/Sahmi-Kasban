from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.jobs import historical_replays as replay_worker
from app.market_data.types import CandleSeries
from app.models import AnalysisReplayJob, AnalysisReplayRow, User

PASSWORD = "StrongPass123"


class FakeReplayProvider:
    name = "fake-replay"

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
        start = datetime.now(UTC) - timedelta(days=420)
        candles: list[dict[str, object]] = []
        for index in range(420):
            close = 30 + index * 0.04 + ((index % 9) - 4) * 0.03
            timestamp = start + timedelta(days=index)
            candles.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "open": round(close - 0.08, 6),
                    "high": round(close + 0.25, 6),
                    "low": round(close - 0.28, 6),
                    "close": round(close, 6),
                    "volume": 500_000 + index * 700,
                }
            )
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime.now(UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint=(ticker.lower() + "x" * 64)[:64],
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


def test_historical_replay_is_account_bound_and_capped_at_31_days(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    first_email = "replay-first@example.com"
    second_email = "replay-second@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", f"{first_email},{second_email}")
    first_headers = _register_and_login(
        client,
        fake_email_service,
        email=first_email,
    )
    second_headers = _register_and_login(
        client,
        fake_email_service,
        email=second_email,
    )
    today = date.today()

    rejected = client.post(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=first_headers,
        json={
            "request_key": "replay-too-long-0001",
            "start_date": (today - timedelta(days=31)).isoformat(),
            "end_date": today.isoformat(),
            "horizon_sessions": 5,
        },
    )
    assert rejected.status_code == 422

    created = client.post(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=first_headers,
        json={
            "request_key": "replay-account-bound-0001",
            "start_date": (today - timedelta(days=30)).isoformat(),
            "end_date": today.isoformat(),
            "horizon_sessions": 5,
        },
    )
    assert created.status_code == 202
    payload = created.json()
    assert payload["parallelism"] == 5
    assert payload["status"] == "pending"
    assert payload["download_ready"] is False

    first_list = client.get(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=first_headers,
    )
    assert first_list.status_code == 200
    assert first_list.json()["total"] == 1

    second_list = client.get(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=second_headers,
    )
    assert second_list.status_code == 200
    assert second_list.json()["total"] == 0

    hidden = client.get(
        f"/api/v1/admin/operations/historical-replays/jobs/{payload['id']}",
        headers=second_headers,
    )
    assert hidden.status_code == 404
    assert db_session.scalar(select(AnalysisReplayJob)) is not None


def test_replay_worker_processes_five_tickers_and_exports_engine_details(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    admin_email = "replay-worker@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    headers = _register_and_login(
        client,
        fake_email_service,
        email=admin_email,
    )
    provider = FakeReplayProvider()
    monkeypatch.setattr(
        replay_worker,
        "get_market_data_provider",
        lambda: provider,
    )
    worker_sessions = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    monkeypatch.setattr(replay_worker, "SessionLocal", worker_sessions)
    today = date.today()
    created = client.post(
        "/api/v1/admin/operations/historical-replays/jobs",
        headers=headers,
        json={
            "request_key": "replay-worker-batch-0001",
            "start_date": (today - timedelta(days=8)).isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),
            "horizon_sessions": 3,
        },
    )
    assert created.status_code == 202
    job_id = created.json()["id"]

    worked = asyncio.run(replay_worker.process_next_historical_replay_batch())
    assert worked is True
    assert provider.calls == 7

    db_session.expire_all()
    job = db_session.get(AnalysisReplayJob, UUID(job_id))
    assert job is not None
    assert job.total_tickers >= 5
    assert job.processed_tickers == 5
    assert job.total_rows > 0
    rows = db_session.scalars(
        select(AnalysisReplayRow).where(AnalysisReplayRow.job_id == job.id)
    ).all()
    assert rows
    analyzed = [row for row in rows if row.signal is not None]
    assert analyzed
    assert all(
        row.data_as_of.date() < row.analysis_date
        for row in analyzed
        if row.data_as_of
    )
    assert "quantitative" in analyzed[0].engines
    assert analyzed[0].engine_version == "core-v2.5"

    exported = client.get(
        f"/api/v1/admin/operations/historical-replays/jobs/{job_id}/export.csv",
        headers=headers,
    )
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    text = exported.content.decode("utf-8-sig")
    assert "engines_json" in text
    assert "quantitative" in text
    assert "core-v2.5" in text

    owner = db_session.scalar(select(User).where(User.email == admin_email))
    assert owner is not None
    assert job.requested_by == owner.id

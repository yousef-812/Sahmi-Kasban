from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries
from app.models import MarketReport, MarketReportItem
from app.services.labs_backtest_jobs import (
    claim_next_labs_job,
    create_labs_backtest_job,
    get_labs_backtest_job,
    recover_stale_labs_jobs,
)

PASSWORD = "StrongPass123"
_CALENDAR_TZ = ZoneInfo("Africa/Cairo")


class FakeIntradayProvider:
    name = "fake-intraday-job"

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls.append(ticker)
        candles: list[dict[str, object]] = []
        for index in range(18):
            base = datetime(2026, 7, 27, 10 + index // 12, (index % 12) * 5, tzinfo=_CALENDAR_TZ)
            candles.append(
                {
                    "timestamp": base.astimezone(UTC).isoformat(),
                    "open": 100 + index * 0.5,
                    "high": 101 + index * 0.5,
                    "low": 99.5 + index * 0.5,
                    "close": 100.5 + index * 0.5,
                    "volume": 100_000,
                }
            )
        return CandleSeries(
            ticker=ticker.upper(),
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 31, 15, 0, tzinfo=UTC),
            data_as_of=datetime(2026, 7, 31, 15, 0, tzinfo=UTC),
            fingerprint=f"labs-job-{ticker}",
            candles=tuple(candles),
        )


def _seed_report(db: Session) -> None:
    report = MarketReport(
        target_session_date=date(2026, 7, 27),
        status="complete",
        generated_at=datetime(2026, 7, 26, 15, 5, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-26"},
        market_summary={"title": "Daily Top 10"},
    )
    db.add(report)
    db.flush()
    for rank in (1, 2):
        db.add(
            MarketReportItem(
                report_id=report.id,
                ticker="HIT" if rank == 1 else "COMI",
                rank=rank,
                score_bp=9000 - rank,
                payload={
                    "ticker": "x",
                    "price_at_analysis": 100.0,
                    "analysis": {"targets": [105.0, 110.0], "stop_loss": 95.0},
                },
            )
        )
    db.commit()


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
            "display_name": "Labs Admin",
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


def test_labs_job_service_claims_and_recovers(db_session: Session) -> None:
    job = create_labs_backtest_job(
        db_session,
        actor_user_id=job_owner_id(db_session),
        start_date=date(2026, 7, 27),
        end_date=date(2026, 7, 27),
        rank=None,
        exit_mode="target_2",
    )
    assert job.status == "queued"

    claimed = claim_next_labs_job(db_session)
    assert claimed is not None
    assert claimed.id == job.id
    assert claimed.status == "running"
    assert claimed.started_at is not None

    assert claim_next_labs_job(db_session) is None

    claimed.started_at = datetime(2020, 1, 1, tzinfo=UTC)
    db_session.commit()
    assert recover_stale_labs_jobs(db_session, stale_minutes=15) == 1
    refreshed = get_labs_backtest_job(
        db_session,
        job_id=job.id,
        actor_user_id=job.requested_by,
    )
    assert refreshed.status == "queued"


def job_owner_id(db: Session):
    from app.models import User

    user = User(
        email="labs-owner@example.com",
        password_hash="hashed-password",
        display_name="Labs Owner",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
        auth_version=0,
    )
    db.add(user)
    db.flush()
    db.commit()
    return user.id


def test_labs_backtest_job_api_roundtrip(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    admin_email = "labs-job-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers = _register_and_login(
        client,
        fake_email_service,
        email=admin_email,
    )
    user_headers = _register_and_login(
        client,
        fake_email_service,
        email="labs-job-user@example.com",
    )
    provider = FakeIntradayProvider()
    app.dependency_overrides[get_market_data_provider] = lambda: provider

    _seed_report(db_session)

    forbidden = client.get(
        "/api/v1/labs/backtest-jobs",
        headers=user_headers,
    )
    assert forbidden.status_code == 403

    created = client.post(
        "/api/v1/labs/backtest-jobs",
        headers=admin_headers,
        json={
            "start_date": "2026-07-27",
            "end_date": "2026-07-27",
            "exit_mode": "target_2",
        },
    )
    assert created.status_code == 202
    job = created.json()
    assert job["status"] == "queued"
    assert job["sessions"] == []

    listed = client.get(
        "/api/v1/labs/backtest-jobs",
        headers=admin_headers,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    fetched = client.get(
        f"/api/v1/labs/backtest-jobs/{job['id']}",
        headers=admin_headers,
    )
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "queued"

    invalid = client.post(
        "/api/v1/labs/backtest-jobs",
        headers=admin_headers,
        json={
            "start_date": "2026-07-27",
            "end_date": "2026-09-30",
            "exit_mode": "target_2",
        },
    )
    assert invalid.status_code == 422

    missing = client.get(
        "/api/v1/labs/backtest-jobs/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
    )
    assert missing.status_code == 404


def test_labs_backtest_job_delete(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    admin_email = "labs-delete-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers = _register_and_login(
        client,
        fake_email_service,
        email=admin_email,
    )

    created = client.post(
        "/api/v1/labs/backtest-jobs",
        headers=admin_headers,
        json={
            "start_date": "2026-07-27",
            "end_date": "2026-07-27",
            "exit_mode": "target_2",
        },
    )
    assert created.status_code == 202
    job_id = created.json()["id"]

    listed = client.get("/api/v1/labs/backtest-jobs", headers=admin_headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    deleted = client.delete(
        f"/api/v1/labs/backtest-jobs/{job_id}",
        headers=admin_headers,
    )
    assert deleted.status_code == 204

    missing = client.get(
        f"/api/v1/labs/backtest-jobs/{job_id}",
        headers=admin_headers,
    )
    assert missing.status_code == 404

    listed = client.get("/api/v1/labs/backtest-jobs", headers=admin_headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 0

    unknown = client.delete(
        "/api/v1/labs/backtest-jobs/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
    )
    assert unknown.status_code == 404

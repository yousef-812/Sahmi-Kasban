from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries
from app.models import MarketReport, MarketReportItem

PASSWORD = "StrongPass123"


class FakeAdminPerformanceProvider:
    name = "fake-admin-performance"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        target = datetime(2020, 1, 2, 12, 0, tzinfo=UTC)
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=target,
            data_as_of=target,
            fingerprint=f"admin-performance-{ticker}",
            candles=(
                {
                    "timestamp": target.isoformat(),
                    "open": 100.0,
                    "high": 106.0,
                    "low": 98.0,
                    "close": 104.0,
                    "volume": 100_000,
                },
            ),
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
            "display_name": "Performance User",
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


def _seed_due_report(db: Session) -> MarketReport:
    report = MarketReport(
        target_session_date=date(2020, 1, 2),
        status="complete",
        generated_at=datetime(2020, 1, 1, 15, 0, tzinfo=UTC),
        source_snapshot={"source_session_date": "2020-01-01"},
        market_summary={"title": "Historical report"},
    )
    db.add(report)
    db.flush()
    db.add(
        MarketReportItem(
            report_id=report.id,
            ticker="API",
            rank=1,
            score_bp=8000,
            payload={
                "ticker": "API",
                "rank": 1,
                "price_at_analysis": 100.0,
                "expected_direction": "up",
                "analysis": {"stop_loss": 95.0, "targets": [105.0, 110.0]},
            },
        )
    )
    db.commit()
    return report


def test_performance_ledger_admin_endpoints_are_protected_and_operational(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    admin_email = "performance-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers = _register_and_login(
        client,
        fake_email_service,
        email=admin_email,
    )
    user_headers = _register_and_login(
        client,
        fake_email_service,
        email="performance-user@example.com",
    )
    report = _seed_due_report(db_session)
    app.dependency_overrides[get_market_data_provider] = FakeAdminPerformanceProvider

    forbidden = client.get(
        "/api/v1/admin/operations/performance/evaluations",
        headers=user_headers,
    )
    assert forbidden.status_code == 403

    evaluated = client.post(
        "/api/v1/admin/operations/performance/evaluate-due",
        headers=admin_headers,
        json={"limit": 10},
    )
    assert evaluated.status_code == 200
    assert evaluated.json()["completed_reports"] == 1
    assert len(evaluated.json()["evaluation_ids"]) == 1

    listed = client.get(
        "/api/v1/admin/operations/performance/evaluations",
        headers=admin_headers,
    )
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["total"] == 1
    assert payload["items"][0]["report_id"] == str(report.id)
    assert payload["items"][0]["status"] == "complete"

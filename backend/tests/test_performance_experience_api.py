from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    MarketReport,
    MarketReportEvaluation,
    MarketReportItem,
    MarketReportItemOutcome,
)

PASSWORD = "StrongPass123"


def _register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str,
    display_name: str,
) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": display_name,
            "avatar_key": "avatar_04",
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


def _create_performance_fixture(db: Session) -> tuple[MarketReport, MarketReportItemOutcome]:
    report = MarketReport(
        target_session_date=date(2026, 7, 20),
        status="complete",
        generated_at=datetime(2026, 7, 19, 15, 0, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-19"},
        market_summary={},
    )
    db.add(report)
    db.flush()
    evaluation = MarketReportEvaluation(
        report_id=report.id,
        target_session_date=report.target_session_date,
        status="partial",
        attempt_count=1,
        evaluated_count=1,
        pending_count=1,
        failed_count=0,
        started_at=datetime(2026, 7, 20, 15, 0, tzinfo=UTC),
        last_attempt_at=datetime(2026, 7, 20, 15, 0, tzinfo=UTC),
        details={},
    )
    db.add(evaluation)
    db.flush()
    complete_item = MarketReportItem(
        report_id=report.id,
        ticker="COMI",
        rank=1,
        score_bp=8500,
        payload={"price_at_analysis": 100, "expected_direction": "up"},
    )
    pending_item = MarketReportItem(
        report_id=report.id,
        ticker="SWDY",
        rank=2,
        score_bp=8200,
        payload={"price_at_analysis": 100, "expected_direction": "up"},
    )
    db.add_all([complete_item, pending_item])
    db.flush()
    db.add(
        MarketReportItemOutcome(
            evaluation_id=evaluation.id,
            report_id=report.id,
            report_item_id=complete_item.id,
            ticker="COMI",
            rank=1,
            target_session_date=report.target_session_date,
            status="complete",
            expected_direction="up",
            price_at_analysis=Decimal("100"),
            session_open=Decimal("100"),
            session_high=Decimal("101"),
            session_low=Decimal("96"),
            session_close=Decimal("98"),
            return_bp=-200,
            max_upside_bp=100,
            max_drawdown_bp=-400,
            direction_correct=False,
            target_one=Decimal("105"),
            target_two=Decimal("110"),
            stop_loss=Decimal("95"),
            target_one_hit=False,
            target_two_hit=False,
            stop_loss_hit=False,
            provider="fixture",
            data_fingerprint="fixture-comi",
            data_as_of=datetime(2026, 7, 20, 15, 0, tzinfo=UTC),
            evaluated_at=datetime(2026, 7, 20, 15, 5, tzinfo=UTC),
            evaluator_version="report-performance-v1",
            evidence={"negative_results_retained": True},
        )
    )
    pending = MarketReportItemOutcome(
        evaluation_id=evaluation.id,
        report_id=report.id,
        report_item_id=pending_item.id,
        ticker="SWDY",
        rank=2,
        target_session_date=report.target_session_date,
        status="pending_data",
        expected_direction="up",
        price_at_analysis=Decimal("100"),
        target_one=Decimal("105"),
        target_two=Decimal("110"),
        stop_loss=Decimal("95"),
        evaluator_version="report-performance-v1",
        evidence={"reason": "target_session_candle_missing", "retryable": True},
    )
    db.add(pending)
    db.commit()
    return report, pending


def test_public_performance_and_admin_correction_flow(
    client: TestClient,
    db_session: Session,
    fake_email_service,
    monkeypatch,
) -> None:
    admin_email = "phase9-performance-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers = _register_and_login(
        client,
        fake_email_service,
        email=admin_email,
        display_name="Performance Admin",
    )
    user_headers = _register_and_login(
        client,
        fake_email_service,
        email="phase9-performance-user@example.com",
        display_name="Performance User",
    )
    report, pending = _create_performance_fixture(db_session)

    summary = client.get(
        "/api/v1/market/performance/summary?window=7",
        headers=user_headers,
    )
    assert summary.status_code == 200
    assert summary.json()["negative_count"] == 1
    assert summary.json()["data_completeness_pct"] == 50.0

    history = client.get(
        "/api/v1/market/performance/reports",
        headers=user_headers,
    )
    assert history.status_code == 200
    assert history.json()["items"][0]["report_id"] == str(report.id)

    detail = client.get(
        f"/api/v1/market/performance/reports/{report.id}",
        headers=user_headers,
    )
    assert detail.status_code == 200
    assert any(item["return_bp"] == -200 for item in detail.json()["outcomes"])

    forbidden = client.get(
        "/api/v1/admin/operations/performance/delayed",
        headers=user_headers,
    )
    assert forbidden.status_code == 403

    delayed = client.get(
        "/api/v1/admin/operations/performance/delayed",
        headers=admin_headers,
    )
    assert delayed.status_code == 200
    assert delayed.json()["total"] == 1

    csv_response = client.get(
        "/api/v1/admin/operations/performance/export.csv?window=7",
        headers=admin_headers,
    )
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.headers["content-type"]
    assert "-200" in csv_response.text

    correction = client.post(
        f"/api/v1/admin/operations/performance/outcomes/{pending.id}/corrections",
        headers=admin_headers,
        json={
            "reason": "Official provider published the corrected session candle.",
            "session_open": 100,
            "session_high": 111,
            "session_low": 98,
            "session_close": 109,
            "provider": "official-correction",
            "data_fingerprint": "official-swd-correction",
            "data_as_of": "2026-07-20T15:00:00Z",
        },
    )
    assert correction.status_code == 200
    assert correction.json()["outcome"]["return_bp"] == 900
    assert correction.json()["outcome"]["correction_count"] == 1
    assert correction.json()["revision"]["revision_number"] == 1

    refreshed = client.get(
        f"/api/v1/market/performance/reports/{report.id}",
        headers=user_headers,
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["evaluation_status"] == "complete"
    assert len(refreshed.json()["revisions"]) == 1

    invalid_window = client.get(
        "/api/v1/market/performance/summary?window=14",
        headers=user_headers,
    )
    assert invalid_window.status_code == 422

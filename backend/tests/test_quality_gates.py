from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.observability import RequestMetricsRegistry, request_metrics
from app.middleware.request_context import normalize_request_id

PASSWORD = "StrongPass123"


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
            "display_name": "Quality Admin",
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


def test_request_id_is_propagated_and_invalid_values_are_replaced(
    client: TestClient,
) -> None:
    valid = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "quality-test-123"},
    )
    assert valid.status_code == 200
    assert valid.headers["x-request-id"] == "quality-test-123"
    assert float(valid.headers["x-response-time-ms"]) >= 0

    invalid = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "bad request id with spaces"},
    )
    assert invalid.status_code == 200
    assert invalid.headers["x-request-id"] != "bad request id with spaces"
    assert len(invalid.headers["x-request-id"]) == 32


def test_request_metrics_registry_calculates_error_rate_and_p95() -> None:
    registry = RequestMetricsRegistry(max_samples=10)
    for duration, status_code in [(10.0, 200), (20.0, 200), (100.0, 500)]:
        registry.begin()
        registry.complete(
            status_code=status_code,
            duration_ms=duration,
            slow_threshold_ms=50,
        )

    snapshot = registry.snapshot()
    assert snapshot["total_requests"] == 3
    assert snapshot["error_requests"] == 1
    assert snapshot["error_rate_percent"] == 33.333
    assert snapshot["slow_requests"] == 1
    assert snapshot["p95_latency_ms"] == 100.0
    assert snapshot["status_counts"] == {"200": 2, "500": 1}


def test_readiness_and_admin_quality_are_protected(
    client: TestClient,
    fake_email_service,
    monkeypatch,
) -> None:
    request_metrics.reset()
    ready = client.get("/api/v1/health/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["checks"][0]["name"] == "database"

    forbidden = client.get("/api/v1/admin/operations/quality")
    assert forbidden.status_code == 401

    admin_email = "phase9-quality-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    headers = register_and_login(
        client,
        fake_email_service,
        email=admin_email,
    )
    response = client.get("/api/v1/admin/operations/quality", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"healthy", "degraded", "critical"}
    assert payload["request_metrics"]["total_requests"] >= 1
    assert payload["thresholds"]["minimum_requests"] >= 1
    assert isinstance(payload["alerts"], list)


def test_request_id_normalizer_accepts_only_safe_values() -> None:
    assert normalize_request_id("abcDEF12-._") == "abcDEF12-._"
    generated = normalize_request_id("short")
    assert len(generated) == 32
    assert generated != "short"

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Alert, User
from app.services.signal_lifecycle import open_signal

PASSWORD = "StrongPass123"


def _register_and_login(client: TestClient, fake_email_service, *, email: str) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "display_name": "Signals Tester"},
    )
    assert registered.status_code == 201
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verified.status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _payload(**overrides) -> dict:
    payload = {
        "ticker": "comi",
        "direction": "long",
        "entry": 100.0,
        "stop": 95.0,
        "t1": 105.0,
        "t2": 110.0,
        "t3": 115.0,
    }
    payload.update(overrides)
    return payload


def test_signal_and_alert_routes_require_authentication(client: TestClient) -> None:
    signal_id = str(uuid.uuid4())
    alert_id = str(uuid.uuid4())
    assert client.get("/api/v1/signals").status_code == 401
    assert client.get(f"/api/v1/signals/{signal_id}").status_code == 401
    assert client.post("/api/v1/signals", json=_payload()).status_code == 401
    assert client.post(f"/api/v1/signals/{signal_id}/advance", json={}).status_code == 401
    assert client.get("/api/v1/alerts").status_code == 401
    assert client.post(f"/api/v1/alerts/{alert_id}/read").status_code == 401
    assert client.post("/api/v1/alerts/read-all").status_code == 401


def test_create_list_and_get_manual_signal(
    client: TestClient,
    fake_email_service,
) -> None:
    headers = _register_and_login(client, fake_email_service, email="signals-owner@example.com")

    created = client.post("/api/v1/signals", json=_payload(), headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert body["state"] == "new"
    assert body["source"] == "manual"
    assert body["ticker"] == "COMI"
    assert body["direction"] == "long"
    assert body["user_id"] is not None
    signal_id = body["id"]

    listed = client.get("/api/v1/signals", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
    assert listed.json()["items"][0]["id"] == signal_id

    filtered = client.get("/api/v1/signals?state=new&ticker=comi&mine=true", headers=headers)
    assert filtered.status_code == 200
    assert filtered.json()["count"] == 1

    mismatch = client.get("/api/v1/signals?state=buy", headers=headers)
    assert mismatch.status_code == 200
    assert mismatch.json()["count"] == 0

    detail = client.get(f"/api/v1/signals/{signal_id}", headers=headers)
    assert detail.status_code == 200
    assert [event["event"] for event in detail.json()["events"]] == ["opened"]

    missing = client.get(f"/api/v1/signals/{uuid.uuid4()}", headers=headers)
    assert missing.status_code == 404


def test_create_signal_rejects_bad_payload(
    client: TestClient,
    fake_email_service,
) -> None:
    headers = _register_and_login(client, fake_email_service, email="signals-bad@example.com")

    bad_direction = client.post("/api/v1/signals", json=_payload(direction="sideways"), headers=headers)
    assert bad_direction.status_code == 400

    bad_entry = client.post("/api/v1/signals", json=_payload(entry=0), headers=headers)
    assert bad_entry.status_code == 422


def test_signal_visibility_shared_vs_private(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    owner_headers = _register_and_login(client, fake_email_service, email="signals-a@example.com")
    created = client.post("/api/v1/signals", json=_payload(), headers=owner_headers)
    owned_id = created.json()["id"]

    shared = open_signal(
        db_session,
        ticker="SWDY",
        direction="long",
        entry=50.0,
        stop=48.0,
        targets=(52.0, None, None),
        source="daily_top10",
    )

    other_headers = _register_and_login(client, fake_email_service, email="signals-b@example.com")
    other_list = client.get("/api/v1/signals", headers=other_headers)
    assert other_list.status_code == 200
    assert [item["id"] for item in other_list.json()["items"]] == [str(shared.id)]

    other_mine = client.get("/api/v1/signals?mine=true", headers=other_headers)
    assert other_mine.json()["count"] == 0

    assert client.get(f"/api/v1/signals/{owned_id}", headers=other_headers).status_code == 404
    assert client.get(f"/api/v1/signals/{shared.id}", headers=other_headers).status_code == 200


def test_advance_requires_admin_and_transitions(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    user_headers = _register_and_login(client, fake_email_service, email="signals-user@example.com")
    created = client.post("/api/v1/signals", json=_payload(), headers=user_headers)
    signal_id = created.json()["id"]

    forbidden = client.post(
        f"/api/v1/signals/{signal_id}/advance",
        json={"high": 101.0, "low": 99.0, "close": 100.5},
        headers=user_headers,
    )
    assert forbidden.status_code == 403

    admin_email = "signals-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers = _register_and_login(client, fake_email_service, email=admin_email)

    advanced = client.post(
        f"/api/v1/signals/{signal_id}/advance",
        json={"high": 101.0, "low": 99.0, "close": 100.5},
        headers=admin_headers,
    )
    assert advanced.status_code == 200
    assert advanced.json()["state"] == "buy"
    assert [event["event"] for event in advanced.json()["events"]] == ["opened", "buy"]

    missing = client.post(
        f"/api/v1/signals/{uuid.uuid4()}/advance",
        json={"high": 101.0, "low": 99.0, "close": 100.5},
        headers=admin_headers,
    )
    assert missing.status_code == 404


def test_alerts_list_read_and_read_all(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    headers = _register_and_login(client, fake_email_service, email="alerts-owner@example.com")
    user = db_session.query(User).filter(User.email == "alerts-owner@example.com").one()
    now = datetime.now(UTC)
    for index in range(3):
        db_session.add(
            Alert(
                user_id=user.id,
                type="signal_transition",
                title=f"تنبيه {index}",
                body=f"محتوى التنبيه {index}",
                created_at=now - timedelta(minutes=index),
            )
        )
    db_session.commit()

    listed = client.get("/api/v1/alerts", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["count"] == 3
    titles = [item["title"] for item in listed.json()["items"]]
    assert titles == ["تنبيه 0", "تنبيه 1", "تنبيه 2"]

    limited = client.get("/api/v1/alerts?limit=1", headers=headers)
    assert limited.json()["count"] == 1
    assert limited.json()["items"][0]["title"] == "تنبيه 0"

    unread = client.get("/api/v1/alerts?unreadOnly=true", headers=headers)
    assert unread.json()["count"] == 3

    first_id = listed.json()["items"][0]["id"]
    read = client.post(f"/api/v1/alerts/{first_id}/read", headers=headers)
    assert read.status_code == 200
    assert read.json()["is_read"] is True

    unread_after = client.get("/api/v1/alerts?unreadOnly=true", headers=headers)
    assert unread_after.json()["count"] == 2

    read_all = client.post("/api/v1/alerts/read-all", headers=headers)
    assert read_all.status_code == 200
    assert read_all.json()["updated"] == 2

    final = client.get("/api/v1/alerts", headers=headers)
    assert all(item["is_read"] for item in final.json()["items"])

    other_headers = _register_and_login(client, fake_email_service, email="alerts-other@example.com")
    foreign = client.post(f"/api/v1/alerts/{first_id}/read", headers=other_headers)
    assert foreign.status_code == 404

from __future__ import annotations

from email.message import EmailMessage

from fastapi.testclient import TestClient

from app.core.config import Environment, Settings
from app.services.email import AccountEmailService


def _registration_payload(email: str) -> dict[str, str]:
    return {
        "email": email,
        "password": "StrongPass123",
        "display_name": "مستخدم تجريبي",
        "avatar_key": "avatar_01",
    }


def test_registration_sends_six_digit_code_and_verifies(
    client: TestClient,
    fake_email_service,
) -> None:
    email = "otp-user@example.com"

    response = client.post("/api/v1/auth/register", json=_registration_payload(email))

    assert response.status_code == 201
    assert response.json()["verification_code_expires_in_seconds"] == 600
    assert response.json()["weekly_points_granted"] == 500
    code = fake_email_service.verification_codes[email]
    assert len(code) == 6
    assert code.isdigit()

    wrong = client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "code": "000000" if code != "000000" else "999999"},
    )
    assert wrong.status_code == 400

    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "code": code},
    )
    assert verified.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    first_profile = client.get("/api/v1/profile/me", headers=headers)
    second_profile = client.get("/api/v1/profile/me", headers=headers)
    history = client.get("/api/v1/wallet/history", headers=headers)

    assert first_profile.status_code == 200
    assert first_profile.json()["balance_points"] == 1_000
    assert second_profile.status_code == 200
    assert second_profile.json()["balance_points"] == 1_000
    assert history.status_code == 200
    assert history.json()["total"] == 2
    entry_types = {item["entry_type"] for item in history.json()["items"]}
    assert entry_types == {"weekly_plan_grant", "welcome_bonus"}


def test_resend_replaces_previous_verification_code(
    client: TestClient,
    fake_email_service,
) -> None:
    email = "otp-resend@example.com"
    client.post("/api/v1/auth/register", json=_registration_payload(email))
    first_code = fake_email_service.verification_codes[email]

    response = client.post(
        "/api/v1/auth/resend-verification",
        json={"email": email},
    )
    assert response.status_code == 200
    second_code = fake_email_service.verification_codes[email]
    assert len(second_code) == 6
    assert second_code.isdigit()

    old_code = client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "code": first_code},
    )
    if first_code != second_code:
        assert old_code.status_code == 400

    current_code = client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "code": second_code},
    )
    assert current_code.status_code == 200


def test_re_registration_recovers_pending_account_without_duplicate_grant(
    client: TestClient,
    fake_email_service,
) -> None:
    email = "pending-recovery@example.com"
    original_payload = _registration_payload(email)

    first = client.post("/api/v1/auth/register", json=original_payload)
    assert first.status_code == 201
    assert first.json()["weekly_points_granted"] == 500
    first_user_id = first.json()["user_id"]
    first_code = fake_email_service.verification_codes[email]

    retry_payload = {
        **original_payload,
        "password": "DifferentPass456",
        "display_name": "اسم مختلف",
    }
    recovered = client.post("/api/v1/auth/register", json=retry_payload)

    assert recovered.status_code == 201
    assert recovered.json()["user_id"] == first_user_id
    assert recovered.json()["weekly_points_granted"] == 0
    second_code = fake_email_service.verification_codes[email]
    assert len(second_code) == 6
    assert second_code.isdigit()

    if first_code != second_code:
        stale = client.post(
            "/api/v1/auth/verify-email",
            json={"email": email, "code": first_code},
        )
        assert stale.status_code == 400

    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "code": second_code},
    )
    assert verified.status_code == 200

    original_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": original_payload["password"]},
    )
    assert original_login.status_code == 200

    replacement_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": retry_payload["password"]},
    )
    assert replacement_login.status_code == 401

    headers = {"Authorization": f"Bearer {original_login.json()['access_token']}"}
    profile = client.get("/api/v1/profile/me", headers=headers)
    wallet = client.get("/api/v1/wallet", headers=headers)
    history = client.get("/api/v1/wallet/history", headers=headers)
    assert profile.status_code == 200
    assert wallet.status_code == 200
    assert wallet.json()["balance_points"] == 1_000
    assert history.status_code == 200
    assert history.json()["total"] == 2

    verified_duplicate = client.post("/api/v1/auth/register", json=original_payload)
    assert verified_duplicate.status_code == 409


def test_verification_email_contains_plain_text_and_branded_html(monkeypatch) -> None:
    captured: list[EmailMessage] = []

    class FakeSMTP:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def starttls(self) -> None:
            pass

        def login(self, _username: str, _password: str) -> None:
            pass

        def send_message(self, message: EmailMessage) -> None:
            captured.append(message)

    monkeypatch.setattr("app.services.email.smtplib.SMTP", FakeSMTP)
    settings = Settings(
        app_env=Environment.TEST,
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@example.com",
    )

    AccountEmailService(settings).send_email_verification(
        "recipient@example.com",
        "482193",
    )

    assert len(captured) == 1
    message = captured[0]
    assert message.is_multipart()
    plain = message.get_body(preferencelist=("plain",)).get_content()
    html = message.get_body(preferencelist=("html",)).get_content()
    assert "482193" in plain
    assert "482193" in html
    assert "سهمي كسبان" in html
    assert "10 دقائق" in html

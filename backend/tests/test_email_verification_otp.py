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
    code = fake_email_service.verification_tokens[email]
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


def test_resend_replaces_previous_verification_code(
    client: TestClient,
    fake_email_service,
) -> None:
    email = "otp-resend@example.com"
    client.post("/api/v1/auth/register", json=_registration_payload(email))
    first_code = fake_email_service.verification_tokens[email]

    response = client.post(
        "/api/v1/auth/resend-verification",
        json={"email": email},
    )
    assert response.status_code == 200
    second_code = fake_email_service.verification_tokens[email]
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

from fastapi.testclient import TestClient

EMAIL = "user@example.com"
PASSWORD = "StrongPass123"
NEW_PASSWORD = "NewStrongPass456"


def register_and_verify(client: TestClient, fake_email_service) -> dict:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": EMAIL,
            "password": PASSWORD,
            "display_name": "Test User",
            "avatar_key": "avatar_02",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["weekly_points_granted"] == 300

    login_before_verification = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert login_before_verification.status_code == 403

    token = fake_email_service.verification_tokens[EMAIL]
    verification_response = client.post(
        "/api/v1/auth/verify-email",
        json={"token": token},
    )
    assert verification_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert login_response.status_code == 200
    return login_response.json()


def auth_headers(tokens: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_registration_login_profile_and_wallet(
    client: TestClient,
    fake_email_service,
) -> None:
    tokens = register_and_verify(client, fake_email_service)
    headers = auth_headers(tokens)

    profile = client.get("/api/v1/profile/me", headers=headers)
    assert profile.status_code == 200
    profile_payload = profile.json()
    assert profile_payload["email"] == EMAIL
    assert profile_payload["avatar_key"] == "avatar_02"
    assert profile_payload["plan_code"] == "free"
    assert profile_payload["weekly_points"] == 300
    assert profile_payload["balance_points"] == 300
    assert profile_payload["balance_coins"] == "3.00"
    assert profile_payload["ads_enabled"] is True

    updated = client.patch(
        "/api/v1/profile/me",
        headers=headers,
        json={"display_name": "Updated User", "avatar_key": "avatar_05"},
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Updated User"
    assert updated.json()["avatar_key"] == "avatar_05"

    wallet = client.get("/api/v1/wallet", headers=headers)
    assert wallet.status_code == 200
    assert wallet.json()["balance_points"] == 300

    history = client.get("/api/v1/wallet/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["entry_type"] == "weekly_plan_grant"
    assert history.json()["items"][0]["amount_points"] == 300


def test_refresh_token_is_rotated_and_logout_is_idempotent(
    client: TestClient,
    fake_email_service,
) -> None:
    tokens = register_and_verify(client, fake_email_service)

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    old_refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert old_refresh.status_code == 401

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert logout.status_code == 200

    repeated_logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert repeated_logout.status_code == 200

    revoked_refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert revoked_refresh.status_code == 401


def test_password_reset_revokes_existing_access_tokens(
    client: TestClient,
    fake_email_service,
) -> None:
    tokens = register_and_verify(client, fake_email_service)

    forgot = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": EMAIL},
    )
    assert forgot.status_code == 200
    reset_token = fake_email_service.password_reset_tokens[EMAIL]

    reset = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": NEW_PASSWORD},
    )
    assert reset.status_code == 200

    old_access = client.get(
        "/api/v1/profile/me",
        headers=auth_headers(tokens),
    )
    assert old_access.status_code == 401

    old_password_login = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    assert old_password_login.status_code == 401

    new_password_login = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": NEW_PASSWORD},
    )
    assert new_password_login.status_code == 200


def test_change_password_and_soft_delete_account(
    client: TestClient,
    fake_email_service,
) -> None:
    tokens = register_and_verify(client, fake_email_service)
    headers = auth_headers(tokens)

    change = client.post(
        "/api/v1/profile/change-password",
        headers=headers,
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert change.status_code == 200

    stale_access = client.get("/api/v1/profile/me", headers=headers)
    assert stale_access.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": NEW_PASSWORD},
    )
    assert new_login.status_code == 200
    new_headers = auth_headers(new_login.json())

    delete_response = client.request(
        "DELETE",
        "/api/v1/profile/me",
        headers=new_headers,
        json={"password": NEW_PASSWORD},
    )
    assert delete_response.status_code == 200

    deleted_login = client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": NEW_PASSWORD},
    )
    assert deleted_login.status_code == 401


def test_duplicate_registration_and_generic_password_reset_response(
    client: TestClient,
    fake_email_service,
) -> None:
    register_and_verify(client, fake_email_service)

    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "email": EMAIL.upper(),
            "password": PASSWORD,
            "display_name": "Other User",
        },
    )
    assert duplicate.status_code == 409

    missing_account = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "missing@example.com"},
    )
    assert missing_account.status_code == 200
    assert "exists" in missing_account.json()["message"]


def test_avatar_options_are_fixed(client: TestClient) -> None:
    response = client.get("/api/v1/profile/avatars")
    assert response.status_code == 200
    avatars = response.json()["avatars"]
    assert len(avatars) == 12
    assert avatars[0]["key"] == "avatar_01"

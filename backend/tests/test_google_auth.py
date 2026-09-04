from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, WalletAccount
from app.services.referral import ensure_user_referral_code


def test_google_registration_and_login(client: TestClient, db_session: Session) -> None:
    db = db_session

    # 1. Register a referrer
    resp_ref = client.post(
        "/api/v1/auth/register",
        json={"email": "google_referrer@example.com", "password": "Password123!", "display_name": "الداعي"},
    )
    assert resp_ref.status_code == 201

    referrer = db.query(User).filter(User.email == "google_referrer@example.com").first()
    assert referrer is not None
    ref_code = ensure_user_referral_code(db, referrer)
    db.commit()

    # 2. Register new user via Google with referral code
    mock_token = "mock_google_token_:google_newuser@example.com:مستخدم جوجل الجديد"
    resp_google = client.post(
        "/api/v1/auth/google",
        json={"id_token": mock_token, "referral_code": ref_code},
    )
    assert resp_google.status_code == 200
    tokens = resp_google.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Verify new user state
    new_user = db.query(User).filter(User.email == "google_newuser@example.com").first()
    assert new_user is not None
    assert new_user.email_verified is True
    assert new_user.display_name == "مستخدم جوجل الجديد"
    assert new_user.referred_by_id == referrer.id

    # Verify referral reward points (1000 points = 10 coins) granted
    referee_wallet = db.query(WalletAccount).filter(WalletAccount.user_id == new_user.id).first()
    assert referee_wallet is not None
    assert referee_wallet.balance_points >= 1000

    # 3. Existing user logs in again via Google
    resp_login = client.post(
        "/api/v1/auth/google",
        json={"id_token": mock_token},
    )
    assert resp_login.status_code == 200
    login_tokens = resp_login.json()
    assert "access_token" in login_tokens

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, WalletAccount
from app.services.referral import ensure_user_referral_code


def test_referral_flow_registration_rewards_and_stats(client: TestClient, db_session: Session) -> None:
    db = db_session
    # 1. Register referrer user
    resp1 = client.post(
        "/api/v1/auth/register",
        json={
            "email": "referrer@example.com",
            "password": "Password123!",
            "display_name": "الداعي",
        },
    )
    assert resp1.status_code == 201

    referrer_user = db.query(User).filter(User.email == "referrer@example.com").first()
    assert referrer_user is not None
    code = ensure_user_referral_code(db, referrer_user)
    db.commit()

    # 2. Register referee user using referrer's code
    resp2 = client.post(
        "/api/v1/auth/register",
        json={
            "email": "referee@example.com",
            "password": "Password123!",
            "display_name": "المستدعى",
            "referral_code": code,
        },
    )
    assert resp2.status_code == 201

    referee_user = db.query(User).filter(User.email == "referee@example.com").first()
    assert referee_user is not None
    assert referee_user.referred_by_id == referrer_user.id

    # 3. Login referee to get token
    # Note: Email not verified yet, so login fails until verified or email_verified flag set
    referee_user.email_verified = True
    db.commit()

    # Process rewards manually or via email verification
    from app.services.referral import process_referral_rewards_on_email_verified
    rewarded = process_referral_rewards_on_email_verified(db, referee_user)
    assert rewarded is True
    db.commit()

    # Idempotency check
    rewarded_again = process_referral_rewards_on_email_verified(db, referee_user)
    assert rewarded_again is False

    # Check referrer wallet balance (welcome bonus/weekly + 1000 points referral reward)
    referrer_wallet = db.query(WalletAccount).filter(WalletAccount.user_id == referrer_user.id).first()
    assert referrer_wallet is not None
    assert referrer_wallet.balance_points >= 1000

    # 4. Check GET /api/v1/referrals/me for referrer
    referrer_user.email_verified = True
    db.commit()
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "referrer@example.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    stats_resp = client.get(
        "/api/v1/referrals/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    assert data["referral_code"] == code
    assert data["total_referred_count"] == 1
    assert data["total_earned_points"] == 1000
    assert data["total_earned_coins"] == "10.00"
    assert len(data["referred_users"]) == 1
    assert data["referred_users"][0]["display_name"] == "المستدعى"

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.config import Environment, Settings
from app.models import Subscription, User, WalletAccount
from app.services.monetization import (
    PurchaseOwnershipConflictError,
    RewardedAdsUnavailableError,
    create_rewarded_ad_session,
    process_google_play_purchase,
    process_rewarded_ad_callback,
    rewarded_ad_eligibility,
)
from app.services.monetization_security import (
    AdMobSsvVerifier,
    GooglePlayVerifier,
    MonetizationVerificationError,
    PurchaseTokenCipher,
)
from app.services.profile import get_active_subscription, get_wallet_balance


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": Environment.TEST,
        "secret_key": "test-secret-key-with-more-than-32-characters",
        "google_play_verification_mode": "stub",
        "admob_ssv_verification_mode": "stub",
        "ad_reward_cooldown_seconds": 0,
    }
    values.update(overrides)
    return Settings(**values)


def _provision_user(db: Session, email: str) -> User:
    now = datetime.now(UTC)
    user = User(
        email=email,
        password_hash="test-password-hash",
        display_name="Test User",
        email_verified=True,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=0))
    db.add(
        Subscription(
            user_id=user.id,
            plan_code="free",
            status="active",
            weekly_points=500,
            ads_enabled=True,
            started_at=now - timedelta(days=1),
            expires_at=None,
        )
    )
    db.flush()
    return user


def test_coin_purchase_is_idempotent_and_token_cannot_move_users(
    db_session: Session,
) -> None:
    settings = _settings()
    buyer = _provision_user(db_session, "buyer@example.com")
    other = _provision_user(db_session, "other@example.com")
    verifier = GooglePlayVerifier(settings)
    cipher = PurchaseTokenCipher(settings)
    token = "stub-purchased:coin-order:unique-token"

    first = asyncio.run(
        process_google_play_purchase(
            db_session,
            user_id=buyer.id,
            product_id="sahmi_coins_10",
            purchase_token=token,
            verifier=verifier,
            cipher=cipher,
        )
    )
    second = asyncio.run(
        process_google_play_purchase(
            db_session,
            user_id=buyer.id,
            product_id="sahmi_coins_10",
            purchase_token=token,
            verifier=verifier,
            cipher=cipher,
        )
    )

    assert first.entitlement_granted is True
    assert first.idempotent is False
    assert second.idempotent is True
    assert get_wallet_balance(db_session, buyer.id) == 1_000
    assert token not in first.purchase.purchase_token_encrypted
    assert cipher.decrypt(first.purchase.purchase_token_encrypted) == token

    with pytest.raises(PurchaseOwnershipConflictError):
        asyncio.run(
            process_google_play_purchase(
                db_session,
                user_id=other.id,
                product_id="sahmi_coins_10",
                purchase_token=token,
                verifier=verifier,
                cipher=cipher,
            )
        )


def test_subscription_purchase_activates_server_catalog_entitlement(
    db_session: Session,
) -> None:
    settings = _settings()
    user = _provision_user(db_session, "subscriber@example.com")

    result = asyncio.run(
        process_google_play_purchase(
            db_session,
            user_id=user.id,
            product_id="sahmi_basic_monthly",
            purchase_token="stub-purchased:subscription-order:basic-token",
            verifier=GooglePlayVerifier(settings),
            cipher=PurchaseTokenCipher(settings),
        )
    )

    subscription = get_active_subscription(db_session, user.id)
    assert result.plan_code == "basic"
    assert subscription.plan_code == "basic"
    assert subscription.weekly_points == 2_500
    assert subscription.ads_enabled is False
    assert subscription.expires_at is not None


def test_expired_paid_subscription_falls_back_to_free_plan(
    db_session: Session,
) -> None:
    settings = _settings()
    user = _provision_user(db_session, "fallback@example.com")
    asyncio.run(
        process_google_play_purchase(
            db_session,
            user_id=user.id,
            product_id="sahmi_basic_monthly",
            purchase_token="stub-purchased:fallback-order:basic-token",
            verifier=GooglePlayVerifier(settings),
            cipher=PurchaseTokenCipher(settings),
        )
    )
    paid = get_active_subscription(db_session, user.id)
    paid.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db_session.flush()

    fallback = get_active_subscription(db_session, user.id)
    assert fallback.plan_code == "free"
    assert fallback.weekly_points == 500
    assert fallback.ads_enabled is True


def test_rewarded_ad_claim_is_verified_once_and_credits_fixed_server_reward(
    db_session: Session,
) -> None:
    settings = _settings()
    user = _provision_user(db_session, "reward@example.com")
    now = datetime.now(UTC)
    started = create_rewarded_ad_session(
        db_session,
        user_id=user.id,
        platform="android",
        moment=now,
        settings=settings,
    )
    payload = {
        "ad_network": "5450213213286189855",
        "ad_unit": started.session.ad_unit_id,
        "custom_data": started.custom_data,
        "reward_amount": "1",
        "reward_item": "coins",
        "timestamp": str(int(now.timestamp() * 1000)),
        "transaction_id": "reward-transaction-1",
    }

    first = asyncio.run(
        process_rewarded_ad_callback(
            db_session,
            raw_payload=payload,
            moment=now,
            settings=settings,
        )
    )
    second = asyncio.run(
        process_rewarded_ad_callback(
            db_session,
            raw_payload=payload,
            moment=now,
            settings=settings,
        )
    )

    assert first.idempotent is False
    assert second.idempotent is True
    assert get_wallet_balance(db_session, user.id) == 75
    assert started.session.status == "completed"


def test_rewarded_ad_daily_limit_is_enforced_server_side(
    db_session: Session,
) -> None:
    settings = _settings(ad_reward_daily_limit=4)
    user = _provision_user(db_session, "daily-limit@example.com")
    now = datetime.now(UTC)

    for index in range(4):
        started = create_rewarded_ad_session(
            db_session,
            user_id=user.id,
            platform="android",
            moment=now,
            settings=settings,
        )
        asyncio.run(
            process_rewarded_ad_callback(
                db_session,
                raw_payload={
                    "ad_network": "5450213213286189855",
                    "ad_unit": started.session.ad_unit_id,
                    "custom_data": started.custom_data,
                    "reward_amount": "1",
                    "reward_item": "coins",
                    "timestamp": str(int(now.timestamp() * 1000)),
                    "transaction_id": f"reward-transaction-{index}",
                },
                moment=now,
                settings=settings,
            )
        )

    eligibility = rewarded_ad_eligibility(
        db_session,
        user.id,
        moment=now,
        settings=settings,
    )
    assert eligibility.eligible is False
    assert eligibility.reason == "daily_limit_reached"
    assert eligibility.used_today == 4
    assert get_wallet_balance(db_session, user.id) == 300

    with pytest.raises(RewardedAdsUnavailableError):
        create_rewarded_ad_session(
            db_session,
            user_id=user.id,
            platform="android",
            moment=now,
            settings=settings,
        )


def test_paid_subscription_disables_rewarded_ads(db_session: Session) -> None:
    user = _provision_user(db_session, "no-ads@example.com")
    subscription = get_active_subscription(db_session, user.id)
    subscription.ads_enabled = False
    db_session.flush()

    eligibility = rewarded_ad_eligibility(db_session, user.id, settings=_settings())
    assert eligibility.eligible is False
    assert eligibility.reason == "subscription_without_ads"


def test_stub_ssv_verifier_requires_explicit_stub_signature() -> None:
    verifier = AdMobSsvVerifier(_settings())
    valid = (
        "ad_network=1&ad_unit=test&reward_amount=1&reward_item=coins&"
        "timestamp=1&transaction_id=abc&signature=stub-valid&key_id=0"
    )
    asyncio.run(verifier.verify(valid))

    with pytest.raises(
        MonetizationVerificationError,
        match="Invalid stub AdMob signature",
    ):
        asyncio.run(verifier.verify(valid.replace("stub-valid", "invalid")))


def test_claim_rewarded_ad_session_instant_verification(db_session: Session) -> None:
    from app.services.monetization import claim_rewarded_ad_session

    settings = _settings()
    user = _provision_user(db_session, "instant-claim@example.com")
    now = datetime.now(UTC)

    started = create_rewarded_ad_session(
        db_session,
        user_id=user.id,
        platform="android",
        moment=now,
        settings=settings,
    )

    result = claim_rewarded_ad_session(
        db_session,
        user_id=user.id,
        session_id=started.session.id,
        custom_data=started.custom_data,
        moment=now,
        settings=settings,
    )

    assert result.idempotent is False
    assert result.balance_points == 75
    assert started.session.status == "completed"

    duplicate = claim_rewarded_ad_session(
        db_session,
        user_id=user.id,
        session_id=started.session.id,
        custom_data=started.custom_data,
        moment=now,
        settings=settings,
    )
    assert duplicate.idempotent is True
    assert duplicate.balance_points == 75

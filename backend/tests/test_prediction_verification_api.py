from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries
from app.models import Discussion, WalletEntry
from app.services.community_ai import get_community_ai_service
from sahmi_kasban.ai import AIProviderError

PASSWORD = "StrongPass123"


def register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str,
) -> tuple[dict, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": email.split("@", maxsplit=1)[0],
            "avatar_key": "avatar_04",
        },
    )
    assert registered.status_code == 201
    verification = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verification.status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    return login.json(), UUID(registered.json()["user_id"])


def headers(tokens: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def create_discussion(
    db: Session,
    *,
    user_id,
    published_at: datetime,
) -> Discussion:
    discussion = Discussion(
        id=uuid4(),
        user_id=user_id,
        ticker="COMI",
        title="توقع دقيق لاختبار واجهة التحقق",
        content="أتوقع الصعود إلى مستوى 108 بنهاية الجلسة القادمة.",
        period_type="next_session",
        status="published",
        moderation_result={"review_stage": "completed"},
        frozen_prediction={
            "ticker": "COMI",
            "direction": "up",
            "target_price": 108.0,
            "deadline": "نهاية الجلسة القادمة",
            "claims": ["الوصول إلى 108"],
            "specificity": 0.9,
        },
        published_at=published_at,
    )
    db.add(discussion)
    db.commit()
    return discussion


class FakeMarketProvider:
    name = "fake"

    def __init__(self) -> None:
        self.calls = 0

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        assert ticker == "COMI"
        assert period == "6mo"
        assert interval == "1d"
        return CandleSeries(
            ticker="COMI",
            provider="fake",
            interval="1d",
            period="6mo",
            fetched_at=datetime(2025, 1, 5, 16, tzinfo=UTC),
            data_as_of=datetime(2025, 1, 5, tzinfo=UTC),
            fingerprint="api-test",
            candles=(
                {
                    "timestamp": "2025-01-05T00:00:00+00:00",
                    "open": 100.0,
                    "high": 111.0,
                    "low": 99.0,
                    "close": 110.0,
                    "volume": 1_000_000,
                },
            ),
        )


class FakeVerificationAI:
    async def verify_prediction(self, *, prediction: dict, market_outcome: dict) -> dict:
        assert prediction["direction"] == "up"
        assert market_outcome["actual_direction"] == "up"
        return {
            "level": "rejected",
            "reward_coins": 0,
            "matched_claims": ["الوصول إلى 108"],
            "failed_claims": [],
            "reason": "تحقق الاتجاه والهدف خلال الفترة.",
        }


class FailingVerificationAI:
    async def verify_prediction(self, *, prediction: dict, market_outcome: dict) -> dict:
        raise AIProviderError("verification provider unavailable")


def test_prediction_verification_rewards_once_and_updates_stats(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    tokens, user_id = register_and_login(
        client,
        fake_email_service,
        email="verify-api@example.com",
    )
    discussion = create_discussion(
        db_session,
        user_id=user_id,
        published_at=datetime(2025, 1, 2, 12, tzinfo=UTC),
    )
    provider = FakeMarketProvider()
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_community_ai_service] = lambda: FakeVerificationAI()

    status_response = client.get(
        f"/api/v1/community/discussions/{discussion.id}/verification",
        headers=headers(tokens),
    )
    assert status_response.status_code == 200
    assert status_response.json()["state"] == "eligible"

    verified = client.post(
        f"/api/v1/community/discussions/{discussion.id}/verification",
        headers=headers(tokens),
    )
    assert verified.status_code == 200
    payload = verified.json()
    assert payload["verification"]["score_bp"] == 9900
    assert payload["verification"]["strength"] == "very_strong"
    assert payload["verification"]["reward_points"] == 200
    assert payload["verification"]["evidence"]["explanation"]["reward_ignored"] is True
    assert payload["balance_points"] == 1_200
    assert payload["idempotent"] is False

    repeated = client.post(
        f"/api/v1/community/discussions/{discussion.id}/verification",
        headers=headers(tokens),
    )
    assert repeated.status_code == 200
    assert repeated.json()["idempotent"] is True
    assert repeated.json()["balance_points"] == 1_200
    assert provider.calls == 1

    rewards = db_session.scalars(
        select(WalletEntry).where(WalletEntry.entry_type == "prediction_verification_reward")
    ).all()
    assert len(rewards) == 1
    assert rewards[0].amount_points == 200

    stats = client.get(
        "/api/v1/community/predictions/stats/mine",
        headers=headers(tokens),
    )
    assert stats.status_code == 200
    assert stats.json() == {
        "verified_predictions": 1,
        "accepted_predictions": 1,
        "accuracy_percent": 100.0,
        "average_score_percent": 99.0,
        "total_reward_points": 200,
        "total_reward_coins": "2.00",
    }


def test_prediction_verification_is_hidden_until_period_finishes(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    tokens, user_id = register_and_login(
        client,
        fake_email_service,
        email="verify-waiting@example.com",
    )
    discussion = create_discussion(
        db_session,
        user_id=user_id,
        published_at=datetime(2099, 1, 1, 12, tzinfo=UTC),
    )
    provider = FakeMarketProvider()
    app.dependency_overrides[get_market_data_provider] = lambda: provider
    app.dependency_overrides[get_community_ai_service] = lambda: FakeVerificationAI()

    status_response = client.get(
        f"/api/v1/community/discussions/{discussion.id}/verification",
        headers=headers(tokens),
    )
    assert status_response.status_code == 200
    assert status_response.json()["state"] == "waiting"
    assert status_response.json()["eligible_at"] is not None

    verify_response = client.post(
        f"/api/v1/community/discussions/{discussion.id}/verification",
        headers=headers(tokens),
    )
    assert verify_response.status_code == 409
    assert "لم تنتهِ فترة التوقع" in verify_response.json()["detail"]
    assert provider.calls == 0


def test_ai_failure_uses_fallback_without_changing_rule_reward(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    tokens, user_id = register_and_login(
        client,
        fake_email_service,
        email="verify-fallback@example.com",
    )
    discussion = create_discussion(
        db_session,
        user_id=user_id,
        published_at=datetime(2025, 1, 2, 12, tzinfo=UTC),
    )
    app.dependency_overrides[get_market_data_provider] = lambda: FakeMarketProvider()
    app.dependency_overrides[get_community_ai_service] = lambda: FailingVerificationAI()

    response = client.post(
        f"/api/v1/community/discussions/{discussion.id}/verification",
        headers=headers(tokens),
    )
    assert response.status_code == 200
    verification = response.json()["verification"]
    assert verification["reward_points"] == 200
    explanation = verification["evidence"]["explanation"]
    assert explanation["source"] == "deterministic_fallback"
    assert explanation["reward_ignored"] is True

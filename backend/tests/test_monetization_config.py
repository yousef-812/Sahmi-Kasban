from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Environment, Settings
from app.services.monetization import (
    RewardedAdsUnavailableError,
    create_rewarded_ad_session,
)


def test_rewarded_session_is_rejected_when_ssv_is_disabled(
    db_session: Session,
) -> None:
    settings = Settings(
        app_env=Environment.TEST,
        secret_key="test-secret-key-with-more-than-32-characters",
        admob_ssv_verification_mode="disabled",
    )

    with pytest.raises(
        RewardedAdsUnavailableError,
        match="verification_disabled",
    ):
        create_rewarded_ad_session(
            db_session,
            user_id=uuid4(),
            platform="android",
            settings=settings,
        )


def test_production_rejects_stub_verifiers_and_google_demo_ids() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env=Environment.PRODUCTION,
            debug=False,
            secret_key="production-secret-key-with-more-than-32-characters",
            database_url="postgresql+psycopg://user:pass@db/sahmi",
            smtp_host="smtp.example.com",
            google_play_verification_mode="stub",
            google_play_service_account_json='{"type":"service_account"}',
            billing_token_encryption_key=("dGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3Q="),
            admob_ssv_verification_mode="stub",
        )

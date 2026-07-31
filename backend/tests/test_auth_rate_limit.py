from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.services.auth_rate_limit import (
    AuthRateLimitExceeded,
    AuthRateLimitPolicy,
    record_auth_attempt,
)


def test_auth_rate_limit_persists_and_resets_after_window(
    db_session: Session,
) -> None:
    policy = AuthRateLimitPolicy(limit=2, window_seconds=60)
    started_at = datetime(2026, 7, 31, 7, 0, tzinfo=UTC)

    record_auth_attempt(
        db_session,
        action="login",
        identity="203.0.113.10:user@example.com",
        policy=policy,
        moment=started_at,
    )
    db_session.commit()
    record_auth_attempt(
        db_session,
        action="login",
        identity="203.0.113.10:user@example.com",
        policy=policy,
        moment=started_at + timedelta(seconds=1),
    )
    db_session.commit()

    with pytest.raises(AuthRateLimitExceeded) as error:
        record_auth_attempt(
            db_session,
            action="login",
            identity="203.0.113.10:user@example.com",
            policy=policy,
            moment=started_at + timedelta(seconds=2),
        )
    db_session.rollback()
    assert error.value.retry_after_seconds >= 58

    record_auth_attempt(
        db_session,
        action="login",
        identity="203.0.113.10:user@example.com",
        policy=policy,
        moment=started_at + timedelta(seconds=61),
    )
    db_session.commit()

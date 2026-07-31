from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AuthRateLimit


@dataclass(frozen=True, slots=True)
class AuthRateLimitPolicy:
    limit: int
    window_seconds: int


class AuthRateLimitExceeded(RuntimeError):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("Too many authentication attempts")
        self.retry_after_seconds = max(1, retry_after_seconds)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _key_hash(action: str, identity: str) -> str:
    normalized = f"{action}:{identity.strip().casefold()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def record_auth_attempt(
    db: Session,
    *,
    action: str,
    identity: str,
    policy: AuthRateLimitPolicy,
    moment: datetime | None = None,
) -> None:
    """Persist a privacy-safe fixed-window authentication attempt."""

    if policy.limit <= 0 or policy.window_seconds <= 0:
        raise ValueError("Authentication rate-limit policy must be positive")
    now = moment or datetime.now(UTC)
    key_hash = _key_hash(action, identity)
    row = db.scalar(
        select(AuthRateLimit)
        .where(
            AuthRateLimit.action == action,
            AuthRateLimit.key_hash == key_hash,
        )
        .with_for_update()
    )
    if row is None:
        row = AuthRateLimit(
            action=action,
            key_hash=key_hash,
            window_started_at=now,
            attempts=1,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
        try:
            db.flush()
            return
        except IntegrityError:
            # A concurrent request created the same fixed-window bucket first.
            db.rollback()
            row = db.scalar(
                select(AuthRateLimit)
                .where(
                    AuthRateLimit.action == action,
                    AuthRateLimit.key_hash == key_hash,
                )
                .with_for_update()
            )
            if row is None:
                raise

    window_started_at = _as_utc(row.window_started_at)
    window_end = window_started_at + timedelta(seconds=policy.window_seconds)
    if now >= window_end:
        row.window_started_at = now
        row.attempts = 1
        row.updated_at = now
        db.flush()
        return

    if row.attempts >= policy.limit:
        retry_after = int((window_end - now).total_seconds()) + 1
        raise AuthRateLimitExceeded(retry_after)

    row.attempts += 1
    row.updated_at = now
    db.flush()

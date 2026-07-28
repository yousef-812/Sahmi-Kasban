from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.avatars import DEFAULT_AVATAR_KEY, validate_avatar_key
from app.core.config import get_settings
from app.core.security import (
    InvalidVerificationReferenceError,
    create_access_token,
    decode_email_verification_reference,
    generate_numeric_code,
    generate_opaque_token,
    hash_account_code,
    hash_opaque_token,
    hash_password,
    verify_account_code_hash,
    verify_password,
)
from app.models import AccountToken, AuthSession, Subscription, User, WalletAccount
from app.services.wallet import grant_weekly_points_for_subscription

EMAIL_VERIFICATION = "email_verification"
PASSWORD_RESET = "password_reset"
EMAIL_VERIFICATION_CODE_MINUTES = 10


class AuthenticationError(RuntimeError):
    """Raised when supplied credentials are invalid."""


class EmailVerificationRequiredError(AuthenticationError):
    """Raised when a user must verify their email before login."""


class DuplicateEmailError(RuntimeError):
    """Raised when an email already belongs to an account."""


class InvalidAccountTokenError(RuntimeError):
    """Raised when an account action token is invalid or expired."""


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def _invalidate_open_account_tokens(
    db: Session,
    *,
    user_id: UUID,
    token_type: str,
    moment: datetime,
) -> None:
    db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user_id,
            AccountToken.token_type == token_type,
            AccountToken.used_at.is_(None),
        )
        .values(used_at=moment)
    )


def issue_account_token(
    db: Session,
    *,
    user_id: UUID,
    token_type: str,
    expires_at: datetime,
) -> str:
    now = datetime.now(UTC)
    _invalidate_open_account_tokens(
        db,
        user_id=user_id,
        token_type=token_type,
        moment=now,
    )
    raw_token = generate_opaque_token()
    db.add(
        AccountToken(
            user_id=user_id,
            token_hash=hash_opaque_token(raw_token),
            token_type=token_type,
            expires_at=expires_at,
        )
    )
    db.flush()
    return raw_token


def issue_email_verification_code(db: Session, *, user_id: UUID) -> str:
    now = datetime.now(UTC)
    _invalidate_open_account_tokens(
        db,
        user_id=user_id,
        token_type=EMAIL_VERIFICATION,
        moment=now,
    )
    code = generate_numeric_code(6)
    db.add(
        AccountToken(
            user_id=user_id,
            token_hash=hash_account_code(
                user_id=user_id,
                token_type=EMAIL_VERIFICATION,
                code=code,
            ),
            token_type=EMAIL_VERIFICATION,
            expires_at=now + timedelta(minutes=EMAIL_VERIFICATION_CODE_MINUTES),
        )
    )
    db.flush()
    return code


def consume_account_token(
    db: Session,
    *,
    raw_token: str,
    token_type: str,
) -> User:
    now = datetime.now(UTC)
    token = db.scalar(
        select(AccountToken)
        .where(
            AccountToken.token_hash == hash_opaque_token(raw_token),
            AccountToken.token_type == token_type,
            AccountToken.used_at.is_(None),
            AccountToken.expires_at > now,
        )
        .with_for_update()
    )
    if token is None:
        raise InvalidAccountTokenError("Invalid or expired account token")
    user = db.get(User, token.user_id)
    if user is None or user.status != "active":
        raise InvalidAccountTokenError("Account is unavailable")
    token.used_at = now
    db.flush()
    return user


def consume_email_verification_code(
    db: Session,
    *,
    email: str,
    code: str,
) -> User:
    normalized_email = normalize_email(email)
    user = db.scalar(
        select(User).where(User.email == normalized_email).with_for_update()
    )
    if user is None or user.status != "active":
        raise InvalidAccountTokenError("Invalid or expired verification code")
    if user.email_verified:
        return user

    now = datetime.now(UTC)
    token = db.scalar(
        select(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.token_type == EMAIL_VERIFICATION,
            AccountToken.used_at.is_(None),
            AccountToken.expires_at > now,
        )
        .order_by(AccountToken.created_at.desc())
        .with_for_update()
    )
    if token is None or not verify_account_code_hash(
        expected_hash=token.token_hash,
        user_id=user.id,
        token_type=EMAIL_VERIFICATION,
        code=code,
    ):
        raise InvalidAccountTokenError("Invalid or expired verification code")

    token.used_at = now
    db.flush()
    return user


def register_user(
    db: Session,
    *,
    email: str,
    password: str,
    display_name: str,
    avatar_key: str = DEFAULT_AVATAR_KEY,
) -> tuple[User, str]:
    normalized_email = normalize_email(email)
    existing = db.scalar(select(User.id).where(User.email == normalized_email))
    if existing is not None:
        raise DuplicateEmailError("Email is already registered")

    avatar = validate_avatar_key(avatar_key)
    now = datetime.now(UTC)
    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        display_name=display_name.strip(),
        avatar_key=avatar,
        status="active",
    )
    db.add(user)
    db.flush()

    wallet = WalletAccount(user_id=user.id, balance_points=0)
    subscription = Subscription(
        user_id=user.id,
        plan_code="free",
        status="active",
        weekly_points=300,
        ads_enabled=True,
        started_at=now,
    )
    db.add_all([wallet, subscription])
    db.flush()
    grant_weekly_points_for_subscription(db, subscription, moment=now)

    code = issue_email_verification_code(db, user_id=user.id)
    return user, code


def verify_user_email(db: Session, raw_token: str) -> User:
    """Consume old opaque links or signed compatibility references."""
    try:
        user = consume_account_token(
            db,
            raw_token=raw_token,
            token_type=EMAIL_VERIFICATION,
        )
    except InvalidAccountTokenError as legacy_error:
        try:
            email, code = decode_email_verification_reference(raw_token)
        except InvalidVerificationReferenceError:
            raise legacy_error from None
        return verify_user_email_code(db, email=email, code=code)

    if not user.email_verified:
        user.email_verified = True
        user.email_verified_at = datetime.now(UTC)
    db.flush()
    return user


def verify_user_email_code(db: Session, *, email: str, code: str) -> User:
    user = consume_email_verification_code(db, email=email, code=code)
    if not user.email_verified:
        user.email_verified = True
        user.email_verified_at = datetime.now(UTC)
    db.flush()
    return user


def create_email_verification_code(db: Session, user: User) -> str | None:
    if user.status != "active" or user.email_verified:
        return None
    return issue_email_verification_code(db, user_id=user.id)


def create_email_verification_token(db: Session, user: User) -> str | None:
    """Backward-compatible alias for callers that still use the old name."""
    return create_email_verification_code(db, user)


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None or user.status != "active":
        raise AuthenticationError("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    if not user.email_verified:
        raise EmailVerificationRequiredError("Email verification is required")
    return user


def create_token_pair(
    db: Session,
    user: User,
    *,
    user_agent: str | None = None,
) -> TokenPair:
    settings = get_settings()
    access_token, expires_in = create_access_token(user.id, user.auth_version)
    refresh_token = generate_opaque_token()
    db.add(
        AuthSession(
            user_id=user.id,
            refresh_token_hash=hash_opaque_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
            user_agent=(user_agent or "")[:500] or None,
        )
    )
    db.flush()
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


def rotate_refresh_token(
    db: Session,
    raw_refresh_token: str,
    *,
    user_agent: str | None = None,
) -> TokenPair:
    now = datetime.now(UTC)
    auth_session = db.scalar(
        select(AuthSession)
        .where(
            AuthSession.refresh_token_hash == hash_opaque_token(raw_refresh_token),
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
        )
        .with_for_update()
    )
    if auth_session is None:
        raise AuthenticationError("Invalid refresh token")
    user = db.get(User, auth_session.user_id)
    if user is None or user.status != "active":
        raise AuthenticationError("Account is unavailable")
    auth_session.revoked_at = now
    return create_token_pair(db, user, user_agent=user_agent)


def revoke_refresh_token(db: Session, raw_refresh_token: str) -> bool:
    auth_session = db.scalar(
        select(AuthSession)
        .where(AuthSession.refresh_token_hash == hash_opaque_token(raw_refresh_token))
        .with_for_update()
    )
    if auth_session is None:
        return False
    if auth_session.revoked_at is None:
        auth_session.revoked_at = datetime.now(UTC)
    db.flush()
    return True


def revoke_all_user_sessions(db: Session, user_id: UUID) -> None:
    db.execute(
        update(AuthSession)
        .where(
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )


def create_password_reset_token(db: Session, user: User) -> str:
    settings = get_settings()
    return issue_account_token(
        db,
        user_id=user.id,
        token_type=PASSWORD_RESET,
        expires_at=datetime.now(UTC) + timedelta(minutes=settings.password_reset_minutes),
    )


def reset_user_password(db: Session, *, raw_token: str, new_password: str) -> User:
    user = consume_account_token(
        db,
        raw_token=raw_token,
        token_type=PASSWORD_RESET,
    )
    user.password_hash = hash_password(new_password)
    user.auth_version += 1
    revoke_all_user_sessions(db, user.id)
    db.flush()
    return user

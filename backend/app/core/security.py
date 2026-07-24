from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()


class InvalidAccessTokenError(ValueError):
    """Raised when an access token is missing, invalid, or expired."""


def validate_password_strength(password: str) -> None:
    if len(password) < 10:
        raise ValueError("Password must contain at least 10 characters")
    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters")
    if not any(character.islower() for character in password):
        raise ValueError("Password must include a lowercase letter")
    if not any(character.isupper() for character in password):
        raise ValueError("Password must include an uppercase letter")
    if not any(character.isdigit() for character in password):
        raise ValueError("Password must include a number")


def hash_password(password: str) -> str:
    validate_password_strength(password)
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        return password_hash.verify(password, encoded_hash)
    except (ValueError, TypeError):
        return False


def generate_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def hash_opaque_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: UUID, auth_version: int) -> tuple[str, int]:
    settings = get_settings()
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=settings.access_token_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "ver": auth_version,
        "iat": issued_at,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, int((expires_at - issued_at).total_seconds())


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "type", "ver", "iat", "exp"]},
        )
    except InvalidTokenError as exc:
        raise InvalidAccessTokenError("Invalid or expired access token") from exc
    if payload.get("type") != "access":
        raise InvalidAccessTokenError("Invalid access token type")
    return payload

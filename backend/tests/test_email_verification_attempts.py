import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AccountToken
from app.services.auth import (
    EMAIL_VERIFICATION,
    EMAIL_VERIFICATION_MAX_ATTEMPTS,
    InvalidAccountCodeError,
    InvalidAccountTokenError,
    register_user,
    verify_user_email_code,
)


def test_verification_code_is_invalidated_after_repeated_failures(
    db_session: Session,
) -> None:
    user, correct_code = register_user(
        db_session,
        email="otp-limit@example.com",
        password="StrongPassword1!",
        display_name="OTP Limit",
    )
    db_session.commit()
    wrong_code = "000000" if correct_code != "000000" else "111111"

    for _ in range(EMAIL_VERIFICATION_MAX_ATTEMPTS):
        with pytest.raises(InvalidAccountCodeError):
            verify_user_email_code(
                db_session,
                email=user.email,
                code=wrong_code,
            )
        db_session.commit()

    token = db_session.scalar(
        select(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.token_type == EMAIL_VERIFICATION,
        )
        .order_by(AccountToken.created_at.desc())
    )
    assert token is not None
    assert token.failed_attempts == EMAIL_VERIFICATION_MAX_ATTEMPTS
    assert token.used_at is not None

    with pytest.raises(InvalidAccountTokenError):
        verify_user_email_code(
            db_session,
            email=user.email,
            code=correct_code,
        )

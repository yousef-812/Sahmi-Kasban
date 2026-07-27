from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.accounts import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.auth import (
    AuthenticationError,
    DuplicateEmailError,
    EmailVerificationRequiredError,
    InvalidAccountTokenError,
    authenticate_user,
    create_email_verification_code,
    create_password_reset_token,
    create_token_pair,
    normalize_email,
    register_user,
    reset_user_password,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_user_email,
    verify_user_email_code,
)
from app.services.email import AccountEmailService, get_account_email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
DatabaseSession = Annotated[Session, Depends(get_db)]
EmailService = Annotated[AccountEmailService, Depends(get_account_email_service)]
UserAgent = Annotated[str | None, Header(alias="User-Agent")]


def _token_response(token_pair) -> TokenResponse:
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )


def _validation_error(exc: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
    )


def _deliver_verification_email(
    email_service: AccountEmailService,
    email: str,
    code: str,
    user_id: str,
) -> None:
    try:
        email_service.send_email_verification(email, code)
    except Exception:
        logger.exception("Verification email delivery failed for user %s", user_id)


def _deliver_password_reset_email(
    email_service: AccountEmailService,
    email: str,
    token: str,
    user_id: str,
) -> None:
    try:
        email_service.send_password_reset(email, token)
    except Exception:
        logger.exception("Password reset email failed for user %s", user_id)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
    email_service: EmailService,
) -> RegisterResponse:
    try:
        user, verification_code = register_user(
            db,
            email=str(payload.email),
            password=payload.password,
            display_name=payload.display_name,
            avatar_key=payload.avatar_key,
        )
        db.commit()
    except DuplicateEmailError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise _validation_error(exc) from exc

    background_tasks.add_task(
        _deliver_verification_email,
        email_service,
        user.email,
        verification_code,
        str(user.id),
    )
    return RegisterResponse(user_id=user.id, email=user.email)


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyEmailRequest, db: DatabaseSession) -> MessageResponse:
    try:
        if payload.email is not None and payload.code is not None:
            verify_user_email_code(
                db,
                email=str(payload.email),
                code=payload.code,
            )
        else:
            verify_user_email(db, payload.token or "")
        db.commit()
    except InvalidAccountTokenError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        ) from exc
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(
    payload: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
    email_service: EmailService,
) -> MessageResponse:
    user = db.scalar(select(User).where(User.email == normalize_email(str(payload.email))))
    if user is not None:
        code = create_email_verification_code(db, user)
        db.commit()
        if code is not None:
            background_tasks.add_task(
                _deliver_verification_email,
                email_service,
                user.email,
                code,
                str(user.id),
            )
    return MessageResponse(
        message="If the account requires verification, a new code has been sent"
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: DatabaseSession,
    user_agent: UserAgent = None,
) -> TokenResponse:
    try:
        user = authenticate_user(db, email=str(payload.email), password=payload.password)
        token_pair = create_token_pair(db, user, user_agent=user_agent)
        db.commit()
    except EmailVerificationRequiredError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification is required",
        ) from exc
    except AuthenticationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc
    return _token_response(token_pair)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshRequest,
    db: DatabaseSession,
    user_agent: UserAgent = None,
) -> TokenResponse:
    try:
        token_pair = rotate_refresh_token(
            db,
            payload.refresh_token,
            user_agent=user_agent,
        )
        db.commit()
    except AuthenticationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc
    return _token_response(token_pair)


@router.post("/logout", response_model=MessageResponse)
def logout(payload: LogoutRequest, db: DatabaseSession) -> MessageResponse:
    revoke_refresh_token(db, payload.refresh_token)
    db.commit()
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
    email_service: EmailService,
) -> MessageResponse:
    user = db.scalar(select(User).where(User.email == normalize_email(str(payload.email))))
    if user is not None and user.status == "active":
        token = create_password_reset_token(db, user)
        db.commit()
        background_tasks.add_task(
            _deliver_password_reset_email,
            email_service,
            user.email,
            token,
            str(user.id),
        )
    return MessageResponse(
        message="If an active account exists, password reset instructions have been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: DatabaseSession) -> MessageResponse:
    try:
        reset_user_password(
            db,
            raw_token=payload.token,
            new_password=payload.new_password,
        )
        db.commit()
    except InvalidAccountTokenError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise _validation_error(exc) from exc
    return MessageResponse(message="Password reset successfully")

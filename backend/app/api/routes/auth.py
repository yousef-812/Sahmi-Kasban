from __future__ import annotations

import logging
from ipaddress import ip_address
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.accounts import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
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
    InvalidAccountCodeError,
    InvalidAccountTokenError,
    authenticate_or_register_with_google,
    authenticate_user,
    create_email_verification_code,
    create_password_reset_code,
    create_token_pair,
    normalize_email,
    register_user,
    reset_user_password_by_code,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_user_email,
    verify_user_email_code,
)
from app.services.auth_rate_limit import (
    AuthRateLimitExceeded,
    AuthRateLimitPolicy,
    record_auth_attempt,
)
from app.services.email import AccountEmailService, get_account_email_service
from app.services.monetization_catalog import get_plan
from app.services.welcome_bonus import grant_welcome_bonus_if_eligible

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
DatabaseSession = Annotated[Session, Depends(get_db)]
EmailService = Annotated[AccountEmailService, Depends(get_account_email_service)]
UserAgent = Annotated[str | None, Header(alias="User-Agent")]

_AUTH_POLICIES = {
    "register": AuthRateLimitPolicy(limit=5, window_seconds=3600),
    "verify_email": AuthRateLimitPolicy(limit=10, window_seconds=600),
    "resend_verification": AuthRateLimitPolicy(limit=3, window_seconds=900),
    "login": AuthRateLimitPolicy(limit=10, window_seconds=900),
    "forgot_password": AuthRateLimitPolicy(limit=5, window_seconds=900),
    "reset_password": AuthRateLimitPolicy(limit=10, window_seconds=900),
}


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


def _request_ip(request: Request) -> str:
    forwarded = request.headers.get("fly-client-ip", "").strip()
    if forwarded:
        try:
            return str(ip_address(forwarded))
        except ValueError:
            pass
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"


def _enforce_auth_limit(
    request: Request,
    db: Session,
    *,
    action: str,
    discriminator: str,
) -> None:
    identity = f"{_request_ip(request)}:{discriminator.strip().casefold()}"
    try:
        record_auth_attempt(
            db,
            action=action,
            identity=identity,
            policy=_AUTH_POLICIES[action],
        )
        db.commit()
    except AuthRateLimitExceeded as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc


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
    code: str,
    user_id: str,
) -> None:
    try:
        email_service.send_password_reset(email, code)
    except Exception:
        logger.exception("Password reset email failed for user %s", user_id)


def _recover_pending_registration(
    db: Session,
    *,
    email: str,
) -> tuple[User, str] | None:
    user = db.scalar(select(User).where(User.email == normalize_email(email)).with_for_update())
    if user is None or user.status != "active" or user.email_verified:
        return None

    verification_code = create_email_verification_code(db, user)
    if verification_code is None:
        return None
    db.commit()
    return user, verification_code


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
    email_service: EmailService,
) -> RegisterResponse:
    _enforce_auth_limit(
        request,
        db,
        action="register",
        discriminator=normalize_email(str(payload.email)),
    )
    recovered_pending_account = False
    try:
        user, verification_code = register_user(
            db,
            email=str(payload.email),
            password=payload.password,
            display_name=payload.display_name,
            avatar_key=payload.avatar_key,
            referral_code=payload.referral_code,
        )
        db.commit()
    except DuplicateEmailError as exc:
        db.rollback()
        recovered = _recover_pending_registration(
            db,
            email=str(payload.email),
        )
        if recovered is None:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            ) from exc
        user, verification_code = recovered
        recovered_pending_account = True
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
    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        weekly_points_granted=(0 if recovered_pending_account else get_plan("free").weekly_points),
    )


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    payload: VerifyEmailRequest,
    request: Request,
    db: DatabaseSession,
) -> MessageResponse:
    discriminator = normalize_email(str(payload.email)) if payload.email is not None else "token"
    _enforce_auth_limit(
        request,
        db,
        action="verify_email",
        discriminator=discriminator,
    )
    try:
        if payload.email is not None and payload.code is not None:
            user = verify_user_email_code(
                db,
                email=str(payload.email),
                code=payload.code,
            )
        else:
            user = verify_user_email(db, payload.token or "")
        grant_welcome_bonus_if_eligible(db, user)
        db.commit()
    except InvalidAccountCodeError as exc:
        # The failed-attempt counter is a security record and must survive the 400 response.
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        ) from exc
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
    request: Request,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
    email_service: EmailService,
) -> MessageResponse:
    normalized_email = normalize_email(str(payload.email))
    _enforce_auth_limit(
        request,
        db,
        action="resend_verification",
        discriminator=normalized_email,
    )
    user = db.scalar(select(User).where(User.email == normalized_email))
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
    return MessageResponse(message="If the account requires verification, a new code has been sent")


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: DatabaseSession,
    user_agent: UserAgent = None,
) -> TokenResponse:
    normalized_email = normalize_email(str(payload.email))
    _enforce_auth_limit(
        request,
        db,
        action="login",
        discriminator=normalized_email,
    )
    try:
        user = authenticate_user(db, email=normalized_email, password=payload.password)
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


@router.post("/google", response_model=TokenResponse)
def google_auth(
    payload: GoogleAuthRequest,
    request: Request,
    db: DatabaseSession,
    user_agent: UserAgent = None,
) -> TokenResponse:
    _enforce_auth_limit(
        request,
        db,
        action="login",
        discriminator="google_auth",
    )
    try:
        user, token_pair = authenticate_or_register_with_google(
            db,
            id_token=payload.id_token,
            referral_code=payload.referral_code,
            user_agent=user_agent,
        )
        grant_welcome_bonus_if_eligible(db, user)
        db.commit()
        return _token_response(token_pair)
    except AuthenticationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise _validation_error(exc) from exc


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
    request: Request,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
    email_service: EmailService,
) -> MessageResponse:
    normalized_email = normalize_email(str(payload.email))
    _enforce_auth_limit(
        request,
        db,
        action="forgot_password",
        discriminator=normalized_email,
    )
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user is not None and user.status == "active":
        code = create_password_reset_code(db, user)
        db.commit()
        background_tasks.add_task(
            _deliver_password_reset_email,
            email_service,
            user.email,
            code,
            str(user.id),
        )
    return MessageResponse(message="If an active account exists, password reset instructions have been sent")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: DatabaseSession,
) -> MessageResponse:
    normalized_email = normalize_email(str(payload.email))
    _enforce_auth_limit(
        request,
        db,
        action="reset_password",
        discriminator=normalized_email,
    )
    try:
        reset_user_password_by_code(
            db,
            email=str(payload.email),
            code=payload.code,
            new_password=payload.new_password,
        )
        db.commit()
    except InvalidAccountTokenError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code",
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise _validation_error(exc) from exc
    return MessageResponse(message="Password reset successfully")

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models import (
    BillingPurchase,
    RewardedAdClaim,
    RewardedAdSession,
    Subscription,
    WalletAccount,
)
from app.services.monetization_catalog import (
    COIN_PACKS,
    PLANS,
    CoinPackDefinition,
    PlanDefinition,
    get_coin_pack,
    get_plan_by_product_id,
    product_type_for,
)
from app.services.monetization_security import (
    GooglePlayVerifier,
    MonetizationVerificationError,
    PurchaseTokenCipher,
    VerifiedPurchase,
    hash_secret,
)
from app.services.profile import get_active_subscription, get_wallet_balance
from app.services.wallet import credit_points, get_wallet_account, points_to_coins


class MonetizationError(RuntimeError):
    """Base monetization workflow error."""


class UnsupportedProductError(MonetizationError):
    """Raised when a product ID is not in the server catalog."""


class PurchaseOwnershipConflictError(MonetizationError):
    """Raised when a purchase token was already used by another user."""


class PurchaseNotCompletedError(MonetizationError):
    """Raised when Google reports a pending, cancelled, or expired purchase."""


class RewardedAdsUnavailableError(MonetizationError):
    """Raised when the user cannot start or redeem a rewarded ad."""


class RewardedAdSessionError(MonetizationError):
    """Raised when a rewarded-ad session is invalid or expired."""


@dataclass(frozen=True, slots=True)
class RewardedAdEligibility:
    eligible: bool
    reason: str | None
    used_today: int
    remaining_today: int
    next_available_at: datetime | None


@dataclass(frozen=True, slots=True)
class RewardedAdSessionResult:
    session: RewardedAdSession
    custom_data: str


@dataclass(frozen=True, slots=True)
class PurchaseProcessingResult:
    purchase: BillingPurchase
    verified: VerifiedPurchase
    idempotent: bool
    entitlement_granted: bool
    plan_code: str
    balance_points: int
    subscription_expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class RewardClaimResult:
    claim: RewardedAdClaim
    idempotent: bool
    balance_points: int


def catalog_payload(settings: Settings | None = None) -> dict[str, object]:
    current = settings or get_settings()
    return {
        "plans": [_plan_payload(plan) for plan in PLANS],
        "coin_packs": [_coin_pack_payload(pack) for pack in COIN_PACKS],
        "ad_reward_points": current.ad_reward_points,
        "ad_reward_coins": points_to_coins(current.ad_reward_points),
        "ad_reward_daily_limit": current.ad_reward_daily_limit,
        "ad_reward_cooldown_seconds": current.ad_reward_cooldown_seconds,
    }


def rewarded_ad_eligibility(
    db: Session,
    user_id: UUID,
    *,
    moment: datetime | None = None,
    settings: Settings | None = None,
    lock_wallet: bool = False,
) -> RewardedAdEligibility:
    current_settings = settings or get_settings()
    now = moment or datetime.now(UTC)
    subscription = get_active_subscription(db, user_id)
    if not subscription.ads_enabled:
        return RewardedAdEligibility(
            eligible=False,
            reason="subscription_without_ads",
            used_today=0,
            remaining_today=0,
            next_available_at=None,
        )

    if lock_wallet:
        get_wallet_account(db, user_id, lock=True)

    zone = ZoneInfo(current_settings.market_timezone)
    local_date = now.astimezone(zone).date()
    used_today = int(
        db.scalar(
            select(func.count(RewardedAdClaim.id)).where(
                RewardedAdClaim.user_id == user_id,
                RewardedAdClaim.cairo_reward_date == local_date,
            )
        )
        or 0
    )
    remaining = max(0, current_settings.ad_reward_daily_limit - used_today)
    if remaining <= 0:
        return RewardedAdEligibility(
            eligible=False,
            reason="daily_limit_reached",
            used_today=used_today,
            remaining_today=0,
            next_available_at=None,
        )

    last_reward_at = db.scalar(
        select(func.max(RewardedAdClaim.verified_at)).where(
            RewardedAdClaim.user_id == user_id
        )
    )
    if last_reward_at is not None:
        next_available_at = last_reward_at + timedelta(
            seconds=current_settings.ad_reward_cooldown_seconds
        )
        if next_available_at > now:
            return RewardedAdEligibility(
                eligible=False,
                reason="cooldown_active",
                used_today=used_today,
                remaining_today=remaining,
                next_available_at=next_available_at,
            )

    return RewardedAdEligibility(
        eligible=True,
        reason=None,
        used_today=used_today,
        remaining_today=remaining,
        next_available_at=None,
    )


def create_rewarded_ad_session(
    db: Session,
    *,
    user_id: UUID,
    platform: str,
    moment: datetime | None = None,
    settings: Settings | None = None,
) -> RewardedAdSessionResult:
    current_settings = settings or get_settings()
    now = moment or datetime.now(UTC)
    eligibility = rewarded_ad_eligibility(
        db,
        user_id,
        moment=now,
        settings=current_settings,
        lock_wallet=True,
    )
    if not eligibility.eligible:
        raise RewardedAdsUnavailableError(eligibility.reason or "rewarded_ads_unavailable")

    if platform == "android":
        ad_unit_id = current_settings.admob_android_rewarded_ad_unit_id
    elif platform == "ios":
        ad_unit_id = current_settings.admob_ios_rewarded_ad_unit_id
    else:
        raise ValueError("Unsupported rewarded-ad platform")

    custom_data = secrets.token_urlsafe(32)
    session = RewardedAdSession(
        user_id=user_id,
        custom_data_hash=hash_secret(custom_data),
        ad_unit_id=ad_unit_id,
        status="pending",
        expires_at=now + timedelta(minutes=current_settings.ad_reward_session_minutes),
    )
    db.add(session)
    db.flush()
    return RewardedAdSessionResult(session=session, custom_data=custom_data)


async def process_google_play_purchase(
    db: Session,
    *,
    user_id: UUID,
    product_id: str,
    purchase_token: str,
    verifier: GooglePlayVerifier | None = None,
    cipher: PurchaseTokenCipher | None = None,
    moment: datetime | None = None,
) -> PurchaseProcessingResult:
    product_type = product_type_for(product_id)
    if product_type is None:
        raise UnsupportedProductError("Product is not present in the server catalog")

    token_hash = hash_secret(purchase_token)
    existing = db.scalar(
        select(BillingPurchase)
        .where(BillingPurchase.purchase_token_hash == token_hash)
        .with_for_update()
    )
    if existing is not None:
        if existing.user_id != user_id or existing.product_id != product_id:
            raise PurchaseOwnershipConflictError(
                "Purchase token is already attached to another entitlement"
            )
        subscription = get_active_subscription(db, user_id)
        balance = get_wallet_balance(db, user_id)
        return PurchaseProcessingResult(
            purchase=existing,
            verified=_verified_from_purchase(existing),
            idempotent=True,
            entitlement_granted=existing.state == "purchased",
            plan_code=subscription.plan_code,
            balance_points=balance,
            subscription_expires_at=subscription.expires_at,
        )

    active_verifier = verifier or GooglePlayVerifier()
    verified = await active_verifier.verify(
        product_id=product_id,
        product_type=product_type,
        purchase_token=purchase_token,
    )
    if not verified.purchased:
        raise PurchaseNotCompletedError(
            f"Google Play purchase is not complete: {verified.state}"
        )

    now = moment or datetime.now(UTC)
    active_cipher = cipher or PurchaseTokenCipher()
    purchase = BillingPurchase(
        user_id=user_id,
        platform="google_play",
        product_id=product_id,
        product_type=product_type,
        purchase_token_hash=token_hash,
        purchase_token_encrypted=active_cipher.encrypt(purchase_token),
        order_id=verified.order_id,
        state=verified.state,
        acknowledgement_state=verified.acknowledgement_state,
        quantity=verified.quantity,
        verified_at=now,
        expires_at=verified.expires_at,
        linked_purchase_token_hash=(
            hash_secret(verified.linked_purchase_token)
            if verified.linked_purchase_token
            else None
        ),
        raw_payload=verified.raw_payload,
    )
    db.add(purchase)

    if product_type == "coins":
        pack = get_coin_pack(product_id)
        if pack is None:
            raise UnsupportedProductError("Coin pack is missing from the catalog")
        wallet_entry = credit_points(
            db,
            user_id=user_id,
            amount_points=pack.points * verified.quantity,
            transaction_id=f"google-play:{token_hash}",
            entry_type="coin_purchase",
            reference_type="billing_purchase",
            reference_id=str(purchase.id),
            details={
                "product_id": product_id,
                "quantity": verified.quantity,
                "order_id": verified.order_id,
            },
        )
        purchase.wallet_transaction_id = wallet_entry.transaction_id
    else:
        plan = get_plan_by_product_id(product_id)
        if plan is None:
            raise UnsupportedProductError("Subscription plan is missing from the catalog")
        _replace_active_subscription(
            db,
            user_id=user_id,
            plan=plan,
            verified=verified,
            purchase=purchase,
            moment=now,
        )

    try:
        db.flush()
    except IntegrityError as exc:
        raise PurchaseOwnershipConflictError(
            "Purchase token was processed concurrently"
        ) from exc

    subscription = get_active_subscription(db, user_id)
    balance = get_wallet_balance(db, user_id)
    return PurchaseProcessingResult(
        purchase=purchase,
        verified=verified,
        idempotent=False,
        entitlement_granted=True,
        plan_code=subscription.plan_code,
        balance_points=balance,
        subscription_expires_at=subscription.expires_at,
    )


async def process_rewarded_ad_callback(
    db: Session,
    *,
    raw_payload: dict[str, str],
    moment: datetime | None = None,
    settings: Settings | None = None,
) -> RewardClaimResult:
    current_settings = settings or get_settings()
    now = moment or datetime.now(UTC)
    transaction_id = _required(raw_payload, "transaction_id")
    existing = db.scalar(
        select(RewardedAdClaim)
        .where(RewardedAdClaim.transaction_id == transaction_id)
        .with_for_update()
    )
    if existing is not None:
        return RewardClaimResult(
            claim=existing,
            idempotent=True,
            balance_points=get_wallet_balance(db, existing.user_id),
        )

    custom_data = _required(raw_payload, "custom_data")
    session = db.scalar(
        select(RewardedAdSession)
        .where(RewardedAdSession.custom_data_hash == hash_secret(custom_data))
        .with_for_update()
    )
    if session is None:
        raise RewardedAdSessionError("Rewarded-ad session does not exist")
    if session.status != "pending":
        raise RewardedAdSessionError("Rewarded-ad session was already completed")
    if session.expires_at < now:
        session.status = "expired"
        raise RewardedAdSessionError("Rewarded-ad session expired")

    callback_timestamp = _parse_admob_timestamp(_required(raw_payload, "timestamp"))
    age = abs((now - callback_timestamp).total_seconds())
    if age > current_settings.admob_ssv_max_callback_age_seconds:
        raise RewardedAdSessionError("AdMob callback timestamp is outside the allowed window")

    ad_unit_id = _required(raw_payload, "ad_unit")
    if ad_unit_id != session.ad_unit_id:
        raise RewardedAdSessionError("AdMob callback used a different ad unit")
    reward_item = _required(raw_payload, "reward_item")
    if reward_item != current_settings.admob_reward_item:
        raise RewardedAdSessionError("AdMob reward item does not match server settings")

    eligibility = rewarded_ad_eligibility(
        db,
        session.user_id,
        moment=now,
        settings=current_settings,
        lock_wallet=True,
    )
    if not eligibility.eligible:
        raise RewardedAdsUnavailableError(eligibility.reason or "rewarded_ads_unavailable")

    zone = ZoneInfo(current_settings.market_timezone)
    reported_amount = int(_required(raw_payload, "reward_amount"))
    wallet_transaction_id = f"admob:{transaction_id}"
    credit_points(
        db,
        user_id=session.user_id,
        amount_points=current_settings.ad_reward_points,
        transaction_id=wallet_transaction_id,
        entry_type="rewarded_ad",
        reference_type="rewarded_ad_claim",
        reference_id=transaction_id,
        details={
            "ad_unit_id": ad_unit_id,
            "ad_network": raw_payload.get("ad_network"),
            "reported_reward_amount": reported_amount,
            "reward_item": reward_item,
        },
    )
    claim = RewardedAdClaim(
        user_id=session.user_id,
        session_id=session.id,
        transaction_id=transaction_id,
        ad_network=_required(raw_payload, "ad_network"),
        ad_unit_id=ad_unit_id,
        reported_reward_amount=reported_amount,
        reward_item=reward_item,
        callback_timestamp=callback_timestamp,
        cairo_reward_date=now.astimezone(zone).date(),
        wallet_transaction_id=wallet_transaction_id,
        verified_at=now,
        raw_payload=raw_payload,
    )
    session.status = "completed"
    session.completed_at = now
    db.add(claim)
    db.flush()
    return RewardClaimResult(
        claim=claim,
        idempotent=False,
        balance_points=get_wallet_balance(db, session.user_id),
    )


def _replace_active_subscription(
    db: Session,
    *,
    user_id: UUID,
    plan: PlanDefinition,
    verified: VerifiedPurchase,
    purchase: BillingPurchase,
    moment: datetime,
) -> None:
    db.execute(
        update(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
        )
        .values(status="replaced", expires_at=moment)
    )
    if purchase.linked_purchase_token_hash:
        linked = db.scalar(
            select(BillingPurchase).where(
                BillingPurchase.purchase_token_hash
                == purchase.linked_purchase_token_hash
            )
        )
        if linked is not None and linked.subscription_id is not None:
            db.execute(
                update(Subscription)
                .where(Subscription.id == linked.subscription_id)
                .values(status="replaced", expires_at=moment)
            )

    subscription = Subscription(
        user_id=user_id,
        plan_code=plan.code,
        status="active",
        weekly_points=plan.weekly_points,
        ads_enabled=plan.ads_enabled,
        started_at=moment,
        expires_at=verified.expires_at,
        purchase_token_hash=purchase.purchase_token_hash,
    )
    db.add(subscription)
    db.flush()
    purchase.subscription_id = subscription.id


def _verified_from_purchase(purchase: BillingPurchase) -> VerifiedPurchase:
    return VerifiedPurchase(
        product_id=purchase.product_id,
        product_type=purchase.product_type,
        state=purchase.state,
        acknowledgement_state=purchase.acknowledgement_state,
        quantity=purchase.quantity,
        order_id=purchase.order_id,
        expires_at=purchase.expires_at,
        linked_purchase_token=None,
        raw_payload=purchase.raw_payload,
    )


def _required(payload: dict[str, str], key: str) -> str:
    value = payload.get(key)
    if value is None or not value:
        raise RewardedAdSessionError(f"Missing AdMob callback parameter: {key}")
    return value


def _parse_admob_timestamp(value: str) -> datetime:
    try:
        milliseconds = int(value)
    except ValueError as exc:
        raise RewardedAdSessionError("Invalid AdMob callback timestamp") from exc
    return datetime.fromtimestamp(milliseconds / 1000, tz=UTC)


def _plan_payload(plan: PlanDefinition) -> dict[str, object]:
    return {
        "code": plan.code,
        "display_name_ar": plan.display_name_ar,
        "weekly_points": plan.weekly_points,
        "weekly_coins": points_to_coins(plan.weekly_points),
        "ads_enabled": plan.ads_enabled,
        "product_id": plan.product_id,
        "history_limit": plan.history_limit,
        "report_history_days": plan.report_history_days,
        "badge_code": plan.badge_code,
    }


def _coin_pack_payload(pack: CoinPackDefinition) -> dict[str, object]:
    return {
        "product_id": pack.product_id,
        "display_name_ar": pack.display_name_ar,
        "points": pack.points,
        "coins": points_to_coins(pack.points),
    }

from __future__ import annotations

from urllib.parse import parse_qsl

from fastapi import APIRouter, HTTPException, Request, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.monetization import (
    GooglePlayPurchaseRequest,
    GooglePlayPurchaseResponse,
    MonetizationCatalogResponse,
    MonetizationStatusResponse,
    RewardedAdEligibilityResponse,
    RewardedAdSessionRequest,
    RewardedAdSessionResponse,
)
from app.services.monetization import (
    MonetizationError,
    PurchaseNotCompletedError,
    PurchaseOwnershipConflictError,
    RewardedAdEligibility,
    RewardedAdSessionError,
    RewardedAdsUnavailableError,
    UnsupportedProductError,
    catalog_payload,
    create_rewarded_ad_session,
    process_google_play_purchase,
    process_rewarded_ad_callback,
    rewarded_ad_eligibility,
)
from app.services.monetization_security import (
    AdMobSsvVerifier,
    GooglePlayVerifier,
    MonetizationConfigurationError,
    MonetizationVerificationError,
)
from app.services.profile import get_active_subscription
from app.services.wallet import points_to_coins

router = APIRouter(prefix="/monetization", tags=["monetization"])


@router.get("/catalog", response_model=MonetizationCatalogResponse)
def monetization_catalog(current_user: CurrentUser) -> MonetizationCatalogResponse:
    del current_user
    return MonetizationCatalogResponse.model_validate(catalog_payload())


@router.get("/status", response_model=MonetizationStatusResponse)
def monetization_status(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MonetizationStatusResponse:
    subscription = get_active_subscription(db, current_user.id)
    eligibility = rewarded_ad_eligibility(db, current_user.id)
    return MonetizationStatusResponse(
        plan_code=subscription.plan_code,
        subscription_status=subscription.status,
        subscription_expires_at=subscription.expires_at,
        weekly_points=subscription.weekly_points,
        weekly_coins=points_to_coins(subscription.weekly_points),
        ads_enabled=subscription.ads_enabled,
        rewarded_ad=_eligibility_response(eligibility),
    )


@router.post(
    "/rewarded-ads/session",
    response_model=RewardedAdSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_rewarded_ad_session(
    payload: RewardedAdSessionRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> RewardedAdSessionResponse:
    try:
        result = create_rewarded_ad_session(
            db,
            user_id=current_user.id,
            platform=payload.platform,
        )
        db.commit()
    except RewardedAdsUnavailableError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RewardedAdSessionResponse(
        session_id=result.session.id,
        ad_unit_id=result.session.ad_unit_id,
        custom_data=result.custom_data,
        expires_at=result.session.expires_at,
    )


@router.get("/admob/ssv", include_in_schema=False)
async def admob_ssv_callback(
    request: Request,
    db: DatabaseSession,
) -> dict[str, object]:
    raw_query = request.scope.get("query_string", b"").decode("utf-8")
    verifier = AdMobSsvVerifier()
    try:
        await verifier.verify(raw_query)
        callback_payload = dict(parse_qsl(raw_query, keep_blank_values=True))
        result = await process_rewarded_ad_callback(
            db,
            raw_payload=callback_payload,
        )
        db.commit()
    except MonetizationConfigurationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except MonetizationVerificationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except (RewardedAdSessionError, RewardedAdsUnavailableError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return {
        "ok": True,
        "idempotent": result.idempotent,
        "balance_points": result.balance_points,
        "balance_coins": points_to_coins(result.balance_points),
    }


@router.post(
    "/google-play/purchases/verify",
    response_model=GooglePlayPurchaseResponse,
)
async def verify_google_play_purchase(
    payload: GooglePlayPurchaseRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> GooglePlayPurchaseResponse:
    verifier = GooglePlayVerifier()
    try:
        result = await process_google_play_purchase(
            db,
            user_id=current_user.id,
            product_id=payload.product_id,
            purchase_token=payload.purchase_token,
            verifier=verifier,
        )
        db.commit()
    except UnsupportedProductError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PurchaseNotCompletedError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PurchaseOwnershipConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except MonetizationConfigurationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except MonetizationVerificationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except MonetizationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    acknowledgement_state = result.purchase.acknowledgement_state
    if acknowledgement_state != "acknowledged":
        try:
            await verifier.acknowledge(
                verified=result.verified,
                purchase_token=payload.purchase_token,
            )
        except MonetizationVerificationError:
            acknowledgement_state = "pending"
        else:
            result.purchase.acknowledgement_state = "acknowledged"
            acknowledgement_state = "acknowledged"
            db.commit()

    return GooglePlayPurchaseResponse(
        purchase_id=result.purchase.id,
        product_id=result.purchase.product_id,
        product_type=result.purchase.product_type,
        purchase_state=result.purchase.state,
        acknowledgement_state=acknowledgement_state,
        entitlement_granted=result.entitlement_granted,
        idempotent=result.idempotent,
        plan_code=result.plan_code,
        balance_points=result.balance_points,
        balance_coins=points_to_coins(result.balance_points),
        subscription_expires_at=result.subscription_expires_at,
    )


def _eligibility_response(
    eligibility: RewardedAdEligibility,
) -> RewardedAdEligibilityResponse:
    return RewardedAdEligibilityResponse(
        eligible=eligibility.eligible,
        reason=eligibility.reason,
        rewards_used_today=eligibility.used_today,
        rewards_remaining_today=eligibility.remaining_today,
        next_available_at=eligibility.next_available_at,
    )

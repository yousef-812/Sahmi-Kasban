from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.schemas.admin_wallet import AdminWalletCreditRequest, AdminWalletCreditResponse
from app.services.admin_wallet import AdminWalletUserNotFoundError, credit_user_coins
from app.services.wallet import WalletTransactionConflictError

router = APIRouter(prefix="/admin/operations/users", tags=["admin-wallet"])


@router.post(
    "/{user_id}/wallet-credit",
    response_model=AdminWalletCreditResponse,
)
def credit_admin_user_wallet(
    user_id: UUID,
    payload: AdminWalletCreditRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminWalletCreditResponse:
    try:
        result = credit_user_coins(
            db,
            admin_user_id=admin.id,
            target_user_id=user_id,
            amount_coins=payload.amount_coins,
            reason=payload.reason,
            request_id=payload.request_id,
        )
        db.commit()
    except AdminWalletUserNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WalletTransactionConflictError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return AdminWalletCreditResponse(**result)

"""Signal lifecycle + alert inbox endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select

from app.api.dependencies import CurrentAdmin, CurrentUser, DatabaseSession
from app.market_data.egx_symbols import normalize_egx_ticker
from app.models import Alert, Signal, User
from app.schemas.signals import (
    AlertBulkReadResponse,
    AlertListResponse,
    AlertOut,
    SignalAdvanceIn,
    SignalCreateIn,
    SignalDetailOut,
    SignalListResponse,
    SignalOut,
)
from app.services.signal_lifecycle import InvalidSignalTransition, advance_signal, open_signal

router = APIRouter(prefix="/signals", tags=["signals"])
alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


def _normalize_ticker(raw: str) -> str:
    try:
        return normalize_egx_ticker(raw)
    except Exception:
        return raw.strip().upper()


def _visible_scope(user: User, *, mine: bool):
    if mine:
        return Signal.user_id == user.id
    return or_(Signal.user_id == user.id, Signal.user_id.is_(None))


@router.get("", response_model=SignalListResponse)
async def list_signals(
    db: DatabaseSession,
    user: CurrentUser,
    state: str | None = Query(default=None, max_length=16),
    ticker: str | None = Query(default=None, max_length=24),
    mine: bool = Query(default=False),
) -> SignalListResponse:
    """List signals visible to the caller.

    Scoping rule: by default a user sees their own signals (``user_id`` set)
    plus source-generated shared signals (``user_id`` NULL, e.g. daily top-10).
    ``mine=true`` restricts the list to the caller's own signals only.
    """
    query = select(Signal).where(_visible_scope(user, mine=mine))
    if state:
        query = query.where(Signal.state == state.strip().lower())
    if ticker:
        query = query.where(Signal.ticker == _normalize_ticker(ticker))
    items = list(db.scalars(query.order_by(Signal.opened_at.desc())).all())
    return SignalListResponse(
        items=[SignalOut.model_validate(item) for item in items],
        count=len(items),
    )


@router.get("/{signal_id}", response_model=SignalDetailOut)
async def get_signal(
    signal_id: UUID,
    db: DatabaseSession,
    user: CurrentUser,
) -> SignalDetailOut:
    """Return one visible signal with its transition history."""
    signal = db.scalar(
        select(Signal).where(Signal.id == signal_id, _visible_scope(user, mine=False))
    )
    if signal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal was not found",
        )
    return SignalDetailOut.model_validate(signal)


@router.post("", response_model=SignalOut, status_code=status.HTTP_201_CREATED)
async def create_signal(
    payload: SignalCreateIn,
    db: DatabaseSession,
    user: CurrentUser,
) -> SignalOut:
    """Open a manual signal owned by the caller (any authenticated user).

    Admin users follow the same path; ownership always lands on the caller so
    manual signals stay private. Generated sources (daily top-10) never use
    this endpoint — they are opened server-side by the report generator.
    """
    try:
        signal = open_signal(
            db,
            ticker=_normalize_ticker(payload.ticker),
            direction=payload.direction,
            entry=payload.entry,
            stop=payload.stop,
            targets=(payload.t1, payload.t2, payload.t3),
            source="manual",
            user_id=user.id,
        )
    except (ValueError, InvalidSignalTransition) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return SignalOut.model_validate(signal)


@router.post("/{signal_id}/advance", response_model=SignalDetailOut)
async def advance_signal_endpoint(
    signal_id: UUID,
    payload: SignalAdvanceIn,
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> SignalDetailOut:
    """Admin-only helper: evaluate a signal against one candle snapshot."""
    signal = db.get(Signal, signal_id)
    if signal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal was not found",
        )
    try:
        advance_signal(db, signal, high=payload.high, low=payload.low, close=payload.close)
    except InvalidSignalTransition as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    db.refresh(signal)
    return SignalDetailOut.model_validate(signal)


@alerts_router.get("", response_model=AlertListResponse)
async def list_alerts(
    db: DatabaseSession,
    user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False, alias="unreadOnly"),
) -> AlertListResponse:
    """Return the caller's alerts, newest first."""
    query = select(Alert).where(Alert.user_id == user.id)
    if unread_only:
        query = query.where(Alert.is_read.is_(False))
    items = list(db.scalars(query.order_by(Alert.created_at.desc()).limit(limit)).all())
    return AlertListResponse(
        items=[AlertOut.model_validate(item) for item in items],
        count=len(items),
    )


@alerts_router.post("/{alert_id}/read", response_model=AlertOut)
async def mark_alert_read(
    alert_id: UUID,
    db: DatabaseSession,
    user: CurrentUser,
) -> AlertOut:
    """Mark one of the caller's alerts as read."""
    alert = db.scalar(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert was not found",
        )
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return AlertOut.model_validate(alert)


@alerts_router.post("/read-all", response_model=AlertBulkReadResponse)
async def mark_all_alerts_read(
    db: DatabaseSession,
    user: CurrentUser,
) -> AlertBulkReadResponse:
    """Mark every unread alert of the caller as read."""
    result = db.execute(
        select(Alert).where(Alert.user_id == user.id, Alert.is_read.is_(False))
    )
    alerts = list(result.scalars().all())
    for alert in alerts:
        alert.is_read = True
    db.commit()
    return AlertBulkReadResponse(updated=len(alerts))

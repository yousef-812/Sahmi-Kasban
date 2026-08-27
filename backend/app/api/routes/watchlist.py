"""Watchlist endpoints — CRUD + signal refresh."""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import CurrentUser, DatabaseSession
from app.market_data.egx_symbols import normalize_egx_ticker
from app.models import WatchlistItem
from app.schemas.watchlist import (
    WatchlistAddIn,
    WatchlistBulkAddIn,
    WatchlistItemOut,
    WatchlistResponse,
)
from app.services.watchlist_signals import refresh_watchlist_signal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

MAX_WATCHLIST_SIZE = 50


@router.get("", response_model=WatchlistResponse)
async def list_watchlist(
    db: DatabaseSession,
    user: CurrentUser,
) -> WatchlistResponse:
    """Return the user's watchlist ordered by most recent first."""
    items = list(
        db.scalars(
            select(WatchlistItem)
            .where(WatchlistItem.user_id == user.id)
            .order_by(WatchlistItem.created_at.desc())
        ).all()
    )
    return WatchlistResponse(
        items=[WatchlistItemOut.model_validate(item) for item in items],
        count=len(items),
        max_items=MAX_WATCHLIST_SIZE,
    )


@router.post("", response_model=WatchlistItemOut, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    payload: WatchlistAddIn,
    db: DatabaseSession,
    user: CurrentUser,
) -> WatchlistItemOut:
    """Add a single ticker to the user's watchlist."""
    try:
        ticker = normalize_egx_ticker(payload.ticker)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticker: {payload.ticker}",
        ) from exc

    existing_count = len(
        list(db.scalars(select(WatchlistItem).where(WatchlistItem.user_id == user.id)).all())
    )
    if existing_count >= MAX_WATCHLIST_SIZE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Watchlist is full (max {MAX_WATCHLIST_SIZE} items)",
        )

    item = WatchlistItem(
        user_id=user.id,
        ticker=ticker,
        notes=payload.notes or {},
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{ticker} is already in your watchlist",
        ) from exc

    db.refresh(item)
    return WatchlistItemOut.model_validate(item)


@router.post("/bulk", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def bulk_add_to_watchlist(
    payload: WatchlistBulkAddIn,
    db: DatabaseSession,
    user: CurrentUser,
) -> WatchlistResponse:
    """Add multiple tickers in one call (idempotent)."""
    normalized: list[str] = []
    for raw in payload.tickers:
        try:
            normalized.append(normalize_egx_ticker(raw))
        except Exception:
            continue

    existing = set(
        db.scalars(
            select(WatchlistItem.ticker).where(WatchlistItem.user_id == user.id)
        ).all()
    )

    current_count = len(existing)
    slots_available = MAX_WATCHLIST_SIZE - current_count

    added = 0
    for ticker in normalized:
        if ticker in existing or added >= slots_available:
            continue
        db.add(WatchlistItem(user_id=user.id, ticker=ticker))
        existing.add(ticker)
        added += 1

    db.commit()
    return await list_watchlist(db=db, user=user)


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    ticker: str,
    db: DatabaseSession,
    user: CurrentUser,
) -> None:
    """Remove a ticker from the user's watchlist."""
    try:
        normalized = normalize_egx_ticker(ticker)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticker: {ticker}",
        ) from exc

    item = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.user_id == user.id,
            WatchlistItem.ticker == normalized,
        )
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{normalized} is not in your watchlist",
        )

    db.delete(item)
    db.commit()


@router.post("/{ticker}/refresh", response_model=WatchlistItemOut)
async def refresh_signal(
    ticker: str,
    db: DatabaseSession,
    user: CurrentUser,
) -> WatchlistItemOut:
    """Re-run analysis for a single watchlist item and update cached signal."""
    try:
        normalized = normalize_egx_ticker(ticker)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticker: {ticker}",
        ) from exc

    item = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.user_id == user.id,
            WatchlistItem.ticker == normalized,
        )
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{normalized} is not in your watchlist",
        )

    try:
        snapshot = await refresh_watchlist_signal(db, user, normalized)
        item.last_signal = snapshot["signal"]
        item.last_score = snapshot["score"]
        item.last_price = snapshot["price"]
        item.last_change_pct = snapshot["change_pct"]
        item.last_checked_at = datetime.now(UTC)
        db.commit()
        db.refresh(item)
    except Exception as exc:
        logger.warning("Failed to refresh watchlist signal for %s: %s", normalized, exc)
        svc_unavail = getattr(
            status, "HTTP_533_SERVICE_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE
        )
        raise HTTPException(
            status_code=svc_unavail,
            detail="Market data temporarily unavailable",
        ) from exc

    return WatchlistItemOut.model_validate(item)

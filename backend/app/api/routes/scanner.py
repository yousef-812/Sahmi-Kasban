"""Scanner endpoints — technical, fibonacci, harmonic listings and on-demand SMC."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, DatabaseSession
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider
from app.schemas.scanner import ScannerItemOut, ScannerListResponse, ScannerSmcResponse
from app.services.scanner import (
    build_harmonic_item,
    build_smc_item,
    build_technical_item,
    get_scanner_item,
    get_scanner_items,
)

router = APIRouter(prefix="/scanner", tags=["scanner"])

MarketProvider = Annotated[MarketDataProvider, Depends(get_market_data_provider)]

NOT_FOUND_DETAIL = "No scanner snapshot for this symbol"


async def _list_response(
    db: Session,
    *,
    kind: str,
    sector: str | None,
    rating: str | None,
    min_score: float | None,
    limit: int,
) -> ScannerListResponse:
    try:
        items = await get_scanner_items(
            db,
            kind=kind,
            sector=sector,
            rating=rating,
            min_score=min_score,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ScannerListResponse(items=items, count=len(items))


async def _stored_item(db: Session, *, kind: str, symbol: str) -> dict | None:
    try:
        return await get_scanner_item(db, kind=kind, symbol=symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/technical", response_model=ScannerListResponse)
async def technical_scanner(
    db: DatabaseSession,
    user: CurrentUser,
    sector: str | None = Query(default=None, max_length=64),
    rating: str | None = Query(default=None, max_length=16),
    min_score: float | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=1000),
) -> ScannerListResponse:
    """Newest technical snapshot per symbol, sorted by score descending."""
    return await _list_response(
        db,
        kind="technical",
        sector=sector,
        rating=rating,
        min_score=min_score,
        limit=limit,
    )


@router.get("/technical/{symbol}", response_model=ScannerItemOut)
async def technical_scanner_symbol(
    symbol: str,
    db: DatabaseSession,
    user: CurrentUser,
    provider: MarketProvider,
) -> ScannerItemOut:
    """Return the stored technical snapshot, computed on demand when missing."""
    item = await _stored_item(db, kind="technical", symbol=symbol)
    if item is None:
        item = await build_technical_item(db, provider, symbol=symbol)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    return ScannerItemOut.model_validate(item)


@router.get("/fibonacci", response_model=ScannerListResponse)
async def fibonacci_scanner(
    db: DatabaseSession,
    user: CurrentUser,
    sector: str | None = Query(default=None, max_length=64),
    rating: str | None = Query(default=None, max_length=16),
    min_score: float | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=1000),
) -> ScannerListResponse:
    """Newest fibonacci snapshot per symbol, sorted by score descending."""
    return await _list_response(
        db,
        kind="fibonacci",
        sector=sector,
        rating=rating,
        min_score=min_score,
        limit=limit,
    )


@router.get("/fibonacci/{symbol}", response_model=ScannerItemOut)
async def fibonacci_scanner_symbol(
    symbol: str,
    db: DatabaseSession,
    user: CurrentUser,
) -> ScannerItemOut:
    """Return the stored fibonacci snapshot of one symbol."""
    item = await _stored_item(db, kind="fibonacci", symbol=symbol)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    return ScannerItemOut.model_validate(item)


@router.get("/harmonic/{symbol}", response_model=ScannerItemOut)
async def harmonic_scanner_symbol(
    symbol: str,
    db: DatabaseSession,
    user: CurrentUser,
    provider: MarketProvider,
) -> ScannerItemOut:
    """Return the stored harmonic snapshot, computed on demand when missing."""
    item = await _stored_item(db, kind="harmonic", symbol=symbol)
    if item is None:
        item = await build_harmonic_item(db, provider, symbol=symbol)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    return ScannerItemOut.model_validate(item)


@router.get("/smc/{symbol}", response_model=ScannerSmcResponse)
async def smc_scanner_symbol(
    symbol: str,
    db: DatabaseSession,
    user: CurrentUser,
    provider: MarketProvider,
) -> ScannerSmcResponse:
    """Run the SMC engine on cached candles and return details, score and reasons."""
    item = await build_smc_item(db, provider, symbol=symbol)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    return ScannerSmcResponse.model_validate(item)

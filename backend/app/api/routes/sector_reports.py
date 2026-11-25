from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import CurrentUser, DatabaseSession
from app.services.sector_reports import AVAILABLE_SECTORS, build_sector_leaderboard
from app.services.wallet import InsufficientBalanceError, debit_points

router = APIRouter(prefix="/reports/sectors", tags=["sector_reports"])

SECTOR_REPORT_COST_POINTS = 200  # 2.0 coins


class SectorLeaderboardItem(BaseModel):
    ticker: str
    company_name: str
    rank: int
    score: float | None
    rating: str
    signal: str
    atr: float | None
    relative_volume: float | None
    rsi14: float | None
    performance_20d_pct: float | None
    as_of: str


class SectorLeaderboardSummary(BaseModel):
    scanner_kind: str
    symbol_count: int
    average_score: float | None
    buy_count: int
    sell_count: int
    neutral_count: int
    best_ticker: str | None
    worst_ticker: str | None
    quality: dict | None


class SectorLeaderboardResponse(BaseModel):
    sector_code: str
    sector_name: str
    leader_ticker: str
    generated_at: str
    coins_deducted: float = 2.0
    degraded: bool = False
    summary: SectorLeaderboardSummary
    items: list[SectorLeaderboardItem]


@router.get("/{sector_id}/leaderboard", response_model=SectorLeaderboardResponse)
async def get_sector_leaderboard(
    sector_id: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> SectorLeaderboardResponse:
    clean_sector = sector_id.strip().lower()
    if clean_sector not in AVAILABLE_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"القطاع المطلوب غير موجود. القطاعات المتاحة: {list(AVAILABLE_SECTORS.keys())}",
        )

    # Debit 2.0 coins (200 points)
    try:
        tx_id = f"sector_report:{clean_sector}:{uuid4()}"
        debit_points(
            db,
            user_id=current_user.id,
            amount_points=SECTOR_REPORT_COST_POINTS,
            transaction_id=tx_id,
            entry_type="sector_report_purchase",
            details={"sector_code": clean_sector},
        )
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رصيد العملات غير كافٍ لعرض تقرير القطاع (التكلفة 2.0 عملة)",
        ) from exc

    leaderboard = await build_sector_leaderboard(db, sector_code=clean_sector)

    db.commit()

    return SectorLeaderboardResponse(
        sector_code=leaderboard["sector_code"],
        sector_name=leaderboard["sector_name"],
        leader_ticker=leaderboard["leader_ticker"],
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        coins_deducted=2.0,
        degraded=leaderboard["degraded"],
        summary=leaderboard["summary"],
        items=leaderboard["items"],
    )

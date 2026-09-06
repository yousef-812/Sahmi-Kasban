from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import SectorReport
from app.services.wallet import InsufficientBalanceError, debit_points

router = APIRouter(prefix="/reports/sectors", tags=["sector_reports"])

SECTOR_REPORT_COST_POINTS = 200  # 2.0 coins

AVAILABLE_SECTORS = {
    "banking": "قطاع البنوك",
    "real_estate": "قطاع العقارات والأراضي",
    "technology": "قطاع التكنولوجيا والاتصالات",
    "financial_services": "قطاع الخدمات المالية والسيولة",
    "basic_resources": "قطاع الموارد الأساسية والتعدين",
    "healthcare": "قطاع الرعاية الصحية والأدوية",
}


class SectorLeaderboardItem(BaseModel):
    ticker: str
    company_name: str
    rank: int
    score: int
    entry_price: float
    target_price: float
    stop_loss: float
    volume_zscore: float
    atr: float
    signal: str


class SectorLeaderboardResponse(BaseModel):
    sector_code: str
    sector_name: str
    leader_ticker: str
    generated_at: str
    coins_deducted: float = 2.0
    items: list[SectorLeaderboardItem]


@router.get("/{sector_id}/leaderboard", response_model=SectorLeaderboardResponse)
def get_sector_leaderboard(
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

    sector_name = AVAILABLE_SECTORS[clean_sector]

    # Generate sample sector leaderboard payload per sector
    items = _generate_sector_items(clean_sector)
    leader_ticker = items[0].ticker if items else "COMI"

    db.commit()

    return SectorLeaderboardResponse(
        sector_code=clean_sector,
        sector_name=sector_name,
        leader_ticker=leader_ticker,
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        coins_deducted=2.0,
        items=items,
    )


def _generate_sector_items(sector_code: str) -> list[SectorLeaderboardItem]:
    if sector_code == "banking":
        return [
            SectorLeaderboardItem(
                ticker="COMI",
                company_name="البنك التجاري الدولي",
                rank=1,
                score=92,
                entry_price=82.50,
                target_price=91.00,
                stop_loss=79.00,
                volume_zscore=2.4,
                atr=1.85,
                signal="شراء قوي",
            ),
            SectorLeaderboardItem(
                ticker="CIEB",
                company_name="كريدي أجريكول مصر",
                rank=2,
                score=86,
                entry_price=21.40,
                target_price=24.00,
                stop_loss=20.00,
                volume_zscore=1.8,
                atr=0.65,
                signal="شراء",
            ),
            SectorLeaderboardItem(
                ticker="ADIB",
                company_name="مصرف أبو ظبي الإسلامي",
                rank=3,
                score=81,
                entry_price=44.20,
                target_price=49.00,
                stop_loss=42.00,
                volume_zscore=1.3,
                atr=1.20,
                signal="مراقبة",
            ),
        ]
    elif sector_code == "real_estate":
        return [
            SectorLeaderboardItem(
                ticker="TMGH",
                company_name="مجموعة طلعت مصطفى القابضة",
                rank=1,
                score=94,
                entry_price=58.00,
                target_price=66.00,
                stop_loss=54.50,
                volume_zscore=3.1,
                atr=2.10,
                signal="شراء قوي",
            ),
            SectorLeaderboardItem(
                ticker="HELI",
                company_name="مصر الجديدة للإسكان والتعمير",
                rank=2,
                score=85,
                entry_price=11.20,
                target_price=13.00,
                stop_loss=10.40,
                volume_zscore=1.9,
                atr=0.45,
                signal="شراء",
            ),
            SectorLeaderboardItem(
                ticker="ORAS",
                company_name="اوراسكوم للتنمية مصر",
                rank=3,
                score=78,
                entry_price=15.80,
                target_price=18.00,
                stop_loss=14.80,
                volume_zscore=1.1,
                atr=0.55,
                signal="مراقبة",
            ),
        ]
    else:
        return [
            SectorLeaderboardItem(
                ticker="EKHO",
                company_name="المصرية الكويتية القابضة",
                rank=1,
                score=88,
                entry_price=0.88,
                target_price=1.02,
                stop_loss=0.82,
                volume_zscore=2.2,
                atr=0.04,
                signal="شراء قوي",
            ),
            SectorLeaderboardItem(
                ticker="SWDY",
                company_name="السويدي الكتريك",
                rank=2,
                score=84,
                entry_price=46.50,
                target_price=52.00,
                stop_loss=43.50,
                volume_zscore=1.7,
                atr=1.40,
                signal="شراء",
            ),
        ]

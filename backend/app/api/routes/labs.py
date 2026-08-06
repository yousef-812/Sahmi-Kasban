from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.market_calendar import EGXTradingCalendar
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider
from app.schemas.labs import (
    LabsBacktestParams,
    LabsBacktestSession,
    LabsBacktestSummary,
    LabsDailyBacktestResponse,
    LabsTrackedPoint,
)
from app.services.labs_daily_backtests import (
    LabsBacktestError,
    execute_daily_report_backtest,
)

router = APIRouter(prefix="/labs", tags=["labs"])
MarketProvider = Annotated[MarketDataProvider, Depends(get_market_data_provider)]


def _tracked_point_payload(point) -> dict[str, object]:
    return {
        "time": point.timestamp.strftime("%H:%M"),
        "price": round(float(point.price), 4),
        "high": round(float(point.high), 4),
        "low": round(float(point.low), 4),
    }


def _session_payload(trade) -> LabsBacktestSession:
    return LabsBacktestSession(
        target_session_date=trade.target_session_date,
        report_id=trade.report_id,
        rank=trade.rank,
        ticker=trade.ticker,
        score=trade.score,
        price_at_analysis=(
            round(float(trade.price_at_analysis), 4)
            if trade.price_at_analysis is not None
            else None
        ),
        targets=[round(float(target), 4) for target in trade.targets],
        stop_loss=(
            round(float(trade.stop_loss), 4)
            if trade.stop_loss is not None
            else None
        ),
        session_open=(
            round(float(trade.session_open), 4)
            if trade.session_open is not None
            else None
        ),
        exit_price=(
            round(float(trade.exit_price), 4)
            if trade.exit_price is not None
            else None
        ),
        exit_reason=trade.exit_reason,
        hit=trade.hit,
        minutes_to_exit=trade.minutes_to_exit,
        return_pct=trade.return_pct,
        tracked=[
            LabsTrackedPoint(**_tracked_point_payload(point))
            for point in trade.tracked
        ],
    )


@router.get("/daily-report-backtest", response_model=LabsDailyBacktestResponse)
async def run_daily_report_backtest(
    db: DatabaseSession,
    current_user: CurrentUser,
    provider: MarketProvider,
    start_date: date = Query(...),
    end_date: date = Query(...),
    rank: int | None = Query(default=None, ge=1, le=10),
    exit_mode: str = Query(
        default="target_2",
        pattern="^(target_2|highest)$",
    ),
) -> LabsDailyBacktestResponse:
    try:
        result = await execute_daily_report_backtest(
            db,
            provider,
            start_date=start_date,
            end_date=end_date,
            rank=rank,
            exit_mode=exit_mode,
            calendar=EGXTradingCalendar.from_settings(),
        )
    except LabsBacktestError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return LabsDailyBacktestResponse(
        params=LabsBacktestParams(**result.params),
        summary=LabsBacktestSummary(**result.summary),
        sessions=[_session_payload(trade) for trade in result.sessions],
        meta={
            "requested_by": str(current_user.id),
            "note": (
                "محاكاة شراء سهم تقرير الـ10 عند افتتاح الجلسة "
                "والخروج عند الهدف المختار، مع تتبع الأسعار كل 10 دقائق."
            ),
        },
    )

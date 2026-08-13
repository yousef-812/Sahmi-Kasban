from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.config import get_settings
from app.models import MarketReport, MarketReportItem
from app.schemas.reports import (
    MarketReportItemResponse,
    MarketReportPreviewResponse,
    MarketReportResponse,
    MarketReportUnlockResponse,
)
from app.services.daily_reports import (
    DailyReportGenerationError,
    MarketReportAccess,
    MarketReportLockedError,
    MarketReportNotFoundError,
    get_report_access,
    latest_complete_report,
    report_is_unlocked,
    unlock_market_report,
)
from app.services.wallet import InsufficientBalanceError, points_to_coins

router = APIRouter(prefix="/market/reports", tags=["market-reports"])


def _source_session_date(report: MarketReport) -> date:
    raw_value = report.source_snapshot.get("source_session_date")
    try:
        return date.fromisoformat(str(raw_value))
    except (TypeError, ValueError) as exc:
        raise DailyReportGenerationError(
            "Market report has an invalid source session date"
        ) from exc


def _report_response(access: MarketReportAccess) -> MarketReportResponse:
    report = access.report
    extended_entries = (report.extended_universe or {}).get("entries", []) or []
    return MarketReportResponse(
        report_id=report.id,
        source_session_date=_source_session_date(report),
        target_session_date=report.target_session_date,
        generated_at=report.generated_at,
        market_summary=report.market_summary,
        items=[
            MarketReportItemResponse(
                ticker=item.ticker,
                rank=item.rank,
                score=item.score_bp / 100,
                payload=item.payload,
            )
            for item in access.items
        ],
        extended_items=[
            MarketReportItemResponse(
                ticker=entry["ticker"],
                rank=entry["rank"],
                score=entry["score"],
                payload=entry,
            )
            for entry in extended_entries
            if isinstance(entry, dict) and entry.get("ticker") and entry.get("rank")
        ],
    )


@router.get("/latest/top10", response_model=MarketReportResponse)
def get_latest_report_top10(db: DatabaseSession) -> MarketReportResponse:
    """Serve the latest completed top-ten report to the on-device trading bot.

    No authentication or unlock is required: this is an internal endpoint for
    the device that executes trades (same owner). It returns the full payload
    of every ranked item, including the engine analysis and trade plan.
    """
    try:
        report = latest_complete_report(db)
    except MarketReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed market report is available",
        ) from exc
    except DailyReportGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The stored market report is invalid",
        ) from exc

    items = tuple(
        db.scalars(
            select(MarketReportItem)
            .where(MarketReportItem.report_id == report.id)
            .order_by(MarketReportItem.rank)
        ).all()
    )
    return _report_response(
        MarketReportAccess(report=report, items=items, unlocked=True)
    )


@router.get("/latest/preview", response_model=MarketReportPreviewResponse)
def get_latest_report_preview(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MarketReportPreviewResponse:
    settings = get_settings()
    try:
        report = latest_complete_report(db)
        source_session_date = _source_session_date(report)
    except MarketReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed market report is available",
        ) from exc
    except DailyReportGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The stored market report is invalid",
        ) from exc

    item_count = db.scalar(
        select(func.count(MarketReportItem.id)).where(
            MarketReportItem.report_id == report.id
        )
    )
    return MarketReportPreviewResponse(
        report_id=report.id,
        source_session_date=source_session_date,
        target_session_date=report.target_session_date,
        generated_at=report.generated_at,
        status=report.status,
        item_count=int(item_count or 0),
        unlocked=report_is_unlocked(
            db,
            user_id=current_user.id,
            report_id=report.id,
        ),
        unlock_cost_points=settings.daily_report_cost_points,
        unlock_cost_coins=points_to_coins(settings.daily_report_cost_points),
        market_summary=report.market_summary,
    )


@router.get("/{report_id}", response_model=MarketReportResponse)
def get_unlocked_market_report(
    report_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MarketReportResponse:
    try:
        access = get_report_access(
            db,
            user_id=current_user.id,
            report_id=report_id,
            require_unlock=True,
        )
        return _report_response(access)
    except MarketReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market report was not found",
        ) from exc
    except MarketReportLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Unlock this report before viewing its stocks",
        ) from exc


@router.post("/{report_id}/unlock", response_model=MarketReportUnlockResponse)
def unlock_report(
    report_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MarketReportUnlockResponse:
    try:
        execution = unlock_market_report(
            db,
            user=current_user,
            report_id=report_id,
        )
    except MarketReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market report was not found",
        ) from exc
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient coin balance to unlock this report",
        ) from exc
    except DailyReportGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Market report is incomplete and cannot be unlocked",
        ) from exc

    return MarketReportUnlockResponse(
        charged_points=execution.charged_points,
        charged_coins=points_to_coins(execution.charged_points),
        balance_points=execution.balance_points,
        balance_coins=points_to_coins(execution.balance_points),
        report=_report_response(execution.access),
    )

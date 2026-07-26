from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider
from app.schemas.operations import (
    AdminAuditEventResponse,
    AdminAuditListResponse,
    AdminBroadcastRequest,
    AdminBroadcastResponse,
    AdminOverviewResponse,
    AdminUserListItem,
    AdminUserListResponse,
    OperationalSettingResponse,
    OperationalSettingsResponse,
    OperationalSettingUpdateRequest,
    ReportEvaluationBackfillRequest,
    ReportEvaluationBackfillResponse,
    ReportEvaluationListResponse,
    ReportEvaluationResponse,
    ServiceHealthListResponse,
    ServiceHealthResponse,
)
from app.schemas.performance import (
    PerformanceCorrectionRequest,
    PerformanceCorrectionResponse,
    PerformanceDelayedListResponse,
)
from app.services.admin_operations import (
    get_admin_overview,
    list_admin_audit_events,
    list_admin_users,
    list_latest_service_health,
    probe_service_health,
)
from app.services.community_ai import get_community_ai_service
from app.services.notifications import NotificationError, broadcast_notifications
from app.services.operations_settings import (
    OperationalSettingError,
    list_operational_settings,
    setting_definitions,
    update_operational_setting,
)
from app.services.performance_experience import (
    PerformanceExperienceError,
    PerformanceCorrectionError,
    PerformanceReportNotFoundError,
    correct_performance_outcome,
    export_performance_csv,
    list_delayed_performance_reports,
    performance_outcome_response,
    performance_revision_response,
)
from app.services.report_performance import (
    ReportEvaluationAlreadyRunningError,
    ReportEvaluationNotDueError,
    ReportEvaluationNotFoundError,
    evaluate_due_market_reports,
    evaluate_market_report,
    list_report_evaluations,
)
from sahmi_kasban.ai import SahmiAIService

router = APIRouter(prefix="/admin/operations", tags=["admin-operations"])
AdminMarketProvider = Annotated[
    MarketDataProvider,
    Depends(get_market_data_provider),
]
AdminAIService = Annotated[
    SahmiAIService,
    Depends(get_community_ai_service),
]


def _setting_response(definition, stored) -> OperationalSettingResponse:
    return OperationalSettingResponse(
        key=definition.key,
        category=definition.category,
        label=definition.label,
        description=definition.description,
        kind=definition.kind,
        value=definition.default_value if stored is None else stored.value,
        default_value=definition.default_value,
        min_value=definition.min_value,
        max_value=definition.max_value,
        updated_at=None if stored is None else stored.updated_at,
    )


def _health_response(item) -> ServiceHealthResponse:
    return ServiceHealthResponse(
        id=item.id,
        component=item.component,
        provider=item.provider,
        status=item.status,
        latency_ms=item.latency_ms,
        details=item.details,
        observed_at=item.observed_at,
    )


def _evaluation_response(item) -> ReportEvaluationResponse:
    return ReportEvaluationResponse(
        id=item.id,
        report_id=item.report_id,
        target_session_date=item.target_session_date,
        status=item.status,
        attempt_count=item.attempt_count,
        evaluated_count=item.evaluated_count,
        pending_count=item.pending_count,
        failed_count=item.failed_count,
        started_at=item.started_at,
        completed_at=item.completed_at,
        last_attempt_at=item.last_attempt_at,
        details=item.details,
    )


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> AdminOverviewResponse:
    return AdminOverviewResponse(**get_admin_overview(db))


@router.get("/users", response_model=AdminUserListResponse)
def admin_users(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    q: str | None = Query(default=None, max_length=120),
    user_status: str | None = Query(default=None, max_length=24),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminUserListResponse:
    items, total = list_admin_users(
        db,
        query_text=q,
        status=user_status,
        limit=limit,
        offset=offset,
    )
    return AdminUserListResponse(
        items=[AdminUserListItem(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/settings", response_model=OperationalSettingsResponse)
def admin_settings(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> OperationalSettingsResponse:
    return OperationalSettingsResponse(
        items=[
            _setting_response(definition, stored)
            for definition, stored in list_operational_settings(db)
        ]
    )


@router.put(
    "/settings/{setting_key}",
    response_model=OperationalSettingResponse,
)
def update_admin_setting(
    setting_key: str,
    payload: OperationalSettingUpdateRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> OperationalSettingResponse:
    try:
        stored = update_operational_setting(
            db,
            admin_user_id=admin.id,
            key=setting_key,
            value=payload.value,
        )
        db.commit()
    except OperationalSettingError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    definition = setting_definitions()[setting_key]
    return _setting_response(definition, stored)


@router.get("/audit", response_model=AdminAuditListResponse)
def admin_audit(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    action: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> AdminAuditListResponse:
    items, total = list_admin_audit_events(
        db,
        action=action,
        limit=limit,
        offset=offset,
    )
    return AdminAuditListResponse(
        items=[
            AdminAuditEventResponse(
                id=item.id,
                actor_user_id=item.actor_user_id,
                target_user_id=item.target_user_id,
                discussion_id=item.discussion_id,
                action=item.action,
                reason_code=item.reason_code,
                details=item.details,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/providers", response_model=ServiceHealthListResponse)
def provider_health(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> ServiceHealthListResponse:
    return ServiceHealthListResponse(
        items=[_health_response(item) for item in list_latest_service_health(db)]
    )


@router.post("/providers/probe", response_model=ServiceHealthListResponse)
async def probe_providers(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    market_provider: AdminMarketProvider,
    ai_service: AdminAIService,
) -> ServiceHealthListResponse:
    items = await probe_service_health(
        db,
        market_provider=market_provider,
        ai_service=ai_service,
    )
    db.commit()
    return ServiceHealthListResponse(items=[_health_response(item) for item in items])


@router.get(
    "/performance/evaluations",
    response_model=ReportEvaluationListResponse,
)
def report_performance_evaluations(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    evaluation_status: str | None = Query(default=None, max_length=24),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ReportEvaluationListResponse:
    items, total = list_report_evaluations(
        db,
        evaluation_status=evaluation_status,
        limit=limit,
        offset=offset,
    )
    return ReportEvaluationListResponse(
        items=[_evaluation_response(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/performance/delayed",
    response_model=PerformanceDelayedListResponse,
)
def delayed_report_performance(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PerformanceDelayedListResponse:
    items, total = list_delayed_performance_reports(
        db,
        limit=limit,
        offset=offset,
    )
    return PerformanceDelayedListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/performance/evaluate-due",
    response_model=ReportEvaluationBackfillResponse,
)
async def evaluate_due_reports(
    payload: ReportEvaluationBackfillRequest,
    db: DatabaseSession,
    _admin: CurrentAdmin,
    market_provider: AdminMarketProvider,
) -> ReportEvaluationBackfillResponse:
    result = await evaluate_due_market_reports(
        db,
        provider=market_provider,
        limit=payload.limit,
    )
    return ReportEvaluationBackfillResponse(
        scanned_reports=result.scanned_reports,
        completed_reports=result.completed_reports,
        partial_reports=result.partial_reports,
        failed_reports=result.failed_reports,
        skipped_reports=result.skipped_reports,
        evaluation_ids=list(result.evaluation_ids),
    )


@router.post(
    "/performance/evaluations/{report_id}/retry",
    response_model=ReportEvaluationResponse,
)
async def retry_report_evaluation(
    report_id: UUID,
    db: DatabaseSession,
    _admin: CurrentAdmin,
    market_provider: AdminMarketProvider,
) -> ReportEvaluationResponse:
    try:
        result = await evaluate_market_report(
            db,
            report_id=report_id,
            provider=market_provider,
        )
        return _evaluation_response(result.evaluation)
    except ReportEvaluationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ReportEvaluationNotDueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ReportEvaluationAlreadyRunningError as exc:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=str(exc),
        ) from exc


@router.get("/performance/export.csv", response_class=PlainTextResponse)
def export_report_performance(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    window: int = Query(default=30),
) -> PlainTextResponse:
    try:
        content = export_performance_csv(db, window_sessions=window)
    except PerformanceExperienceError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return PlainTextResponse(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="sahmi-performance-{window}-sessions.csv"'
            )
        },
    )


@router.post(
    "/performance/outcomes/{outcome_id}/corrections",
    response_model=PerformanceCorrectionResponse,
)
def correct_report_performance(
    outcome_id: UUID,
    payload: PerformanceCorrectionRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> PerformanceCorrectionResponse:
    try:
        outcome, revision = correct_performance_outcome(
            db,
            outcome_id=outcome_id,
            actor_user_id=admin.id,
            reason=payload.reason,
            session_open=payload.session_open,
            session_high=payload.session_high,
            session_low=payload.session_low,
            session_close=payload.session_close,
            provider=payload.provider,
            data_fingerprint=payload.data_fingerprint,
            data_as_of=payload.data_as_of,
        )
    except PerformanceReportNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PerformanceCorrectionError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return PerformanceCorrectionResponse(
        outcome=performance_outcome_response(db, outcome),
        revision=performance_revision_response(revision),
    )


@router.post(
    "/notifications/broadcast",
    response_model=AdminBroadcastResponse,
)
def broadcast_admin_notification(
    payload: AdminBroadcastRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminBroadcastResponse:
    try:
        result = broadcast_notifications(
            db,
            admin_user_id=admin.id,
            title=payload.title,
            body=payload.body,
            category=payload.category,
            data=payload.data,
            audience=payload.audience,
            plan_code=payload.plan_code,
            user_ids=payload.user_ids,
        )
        db.commit()
    except NotificationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return AdminBroadcastResponse(
        targeted_users=result.targeted_users,
        notifications_created=result.notifications_created,
        push_sent=result.push_sent,
        push_failed=result.push_failed,
        push_skipped=result.push_skipped,
    )

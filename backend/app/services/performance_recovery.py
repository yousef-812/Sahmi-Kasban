from __future__ import annotations

import logging
from datetime import UTC, datetime, time

from sqlalchemy.orm import Session

from app.services.performance_experience import (
    PerformanceExperienceError,
    get_performance_report_detail,
    get_performance_summary,
    list_delayed_performance_reports,
    list_performance_reports,
)

logger = logging.getLogger(__name__)


def _fallback_generated_at(payload: dict) -> None:
    if payload.get("generated_at") is not None:
        return
    target = payload.get("target_session_date")
    if target is not None:
        payload["generated_at"] = datetime.combine(target, time.min, tzinfo=UTC)


def _empty_summary(window_sessions: int, error: Exception) -> dict:
    return {
        "window_sessions": window_sessions,
        "sessions_found": 0,
        "complete_sessions": 0,
        "total_items": 0,
        "evaluated_items": 0,
        "pending_items": 0,
        "failed_items": 0,
        "data_completeness_pct": 0.0,
        "positive_count": 0,
        "negative_count": 0,
        "flat_count": 0,
        "average_return_bp": None,
        "median_return_bp": None,
        "positive_rate_pct": None,
        "direction_accuracy_pct": None,
        "target_one_hit_rate_pct": None,
        "target_two_hit_rate_pct": None,
        "stop_loss_hit_rate_pct": None,
        "best_outcome": None,
        "worst_outcome": None,
        "ranks": [
            {
                "rank": rank,
                "evaluated_items": 0,
                "average_return_bp": None,
                "median_return_bp": None,
                "positive_rate_pct": None,
                "direction_accuracy_pct": None,
                "target_one_hit_rate_pct": None,
                "stop_loss_hit_rate_pct": None,
            }
            for rank in range(1, 11)
        ],
        "sessions": [],
        "benchmark": {
            "status": "degraded",
            "symbol": "EGX30",
            "reason": f"Performance ledger recovery: {type(error).__name__}",
        },
        "negative_results_retained": True,
    }


def safe_get_performance_summary(db: Session, *, window_sessions: int) -> dict:
    try:
        return get_performance_summary(db, window_sessions=window_sessions)
    except PerformanceExperienceError:
        raise
    except Exception as exc:  # recovery boundary for legacy production rows
        logger.exception("Performance summary failed; returning a safe empty ledger")
        return _empty_summary(window_sessions, exc)


def safe_list_performance_reports(
    db: Session,
    *,
    limit: int,
    offset: int,
) -> tuple[list[dict], int]:
    try:
        items, total = list_performance_reports(db, limit=limit, offset=offset)
        for item in items:
            _fallback_generated_at(item)
        return items, total
    except PerformanceExperienceError:
        raise
    except Exception:  # recovery boundary for legacy production rows
        logger.exception("Performance report list failed; returning an empty page")
        return [], 0


def safe_get_performance_report_detail(db: Session, *, report_id) -> dict:
    payload = get_performance_report_detail(db, report_id=report_id)
    _fallback_generated_at(payload)
    return payload


def safe_list_delayed_performance_reports(
    db: Session,
    *,
    limit: int,
    offset: int,
) -> tuple[list[dict], int]:
    try:
        return list_delayed_performance_reports(db, limit=limit, offset=offset)
    except PerformanceExperienceError:
        raise
    except Exception:  # recovery boundary for legacy production rows
        logger.exception("Delayed performance list failed; returning an empty page")
        return [], 0

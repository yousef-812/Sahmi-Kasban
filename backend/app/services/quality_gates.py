from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import Environment, get_settings
from app.core.observability import request_metrics, sentry_is_enabled
from app.services.admin_operations import list_latest_service_health


def build_quality_status(
    db: Session,
    *,
    moment: datetime | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    current = moment or datetime.now(UTC)
    metrics = request_metrics.snapshot()
    provider_events = list_latest_service_health(db)
    stale_before = current - timedelta(minutes=settings.quality_provider_stale_minutes)

    alerts: list[dict[str, Any]] = []
    if metrics["total_requests"] >= settings.quality_min_request_count:
        if metrics["error_rate_percent"] >= settings.quality_error_rate_alert_percent:
            alerts.append(
                {
                    "code": "request_error_rate_high",
                    "severity": "critical",
                    "message": "معدل أخطاء الخادم تجاوز الحد التشغيلي.",
                    "observed_value": metrics["error_rate_percent"],
                    "threshold": settings.quality_error_rate_alert_percent,
                }
            )
        if metrics["p95_latency_ms"] >= settings.quality_p95_latency_alert_ms:
            alerts.append(
                {
                    "code": "request_latency_high",
                    "severity": "warning",
                    "message": "زمن الاستجابة P95 تجاوز الحد التشغيلي.",
                    "observed_value": metrics["p95_latency_ms"],
                    "threshold": settings.quality_p95_latency_alert_ms,
                }
            )

    providers: list[dict[str, Any]] = []
    for event in provider_events:
        stale = event.observed_at < stale_before
        providers.append(
            {
                "component": event.component,
                "provider": event.provider,
                "status": event.status,
                "latency_ms": event.latency_ms,
                "observed_at": event.observed_at,
                "stale": stale,
            }
        )
        if event.status == "failed":
            alerts.append(
                {
                    "code": f"provider_failed:{event.component}",
                    "severity": "critical",
                    "message": f"فشل مزود الخدمة: {event.component}.",
                    "observed_value": event.status,
                    "threshold": "healthy",
                }
            )
        elif event.status != "healthy":
            alerts.append(
                {
                    "code": f"provider_degraded:{event.component}",
                    "severity": "warning",
                    "message": f"مزود الخدمة يعمل بحالة غير مستقرة: {event.component}.",
                    "observed_value": event.status,
                    "threshold": "healthy",
                }
            )
        if stale:
            alerts.append(
                {
                    "code": f"provider_probe_stale:{event.component}",
                    "severity": "warning",
                    "message": f"فحص مزود الخدمة قديم: {event.component}.",
                    "observed_value": event.observed_at.isoformat(),
                    "threshold": settings.quality_provider_stale_minutes,
                }
            )

    if settings.app_env in {Environment.STAGING, Environment.PRODUCTION} and not sentry_is_enabled():
        alerts.append(
            {
                "code": "error_reporting_disabled",
                "severity": "critical",
                "message": "مراقبة الأخطاء الخارجية غير مفعلة في بيئة تشغيلية.",
                "observed_value": "disabled",
                "threshold": "enabled",
            }
        )

    severities = {item["severity"] for item in alerts}
    if "critical" in severities:
        overall_status = "critical"
    elif "warning" in severities:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "status": overall_status,
        "generated_at": current,
        "sentry_enabled": sentry_is_enabled(),
        "request_metrics": metrics,
        "providers": providers,
        "alerts": alerts,
        "thresholds": {
            "error_rate_percent": settings.quality_error_rate_alert_percent,
            "p95_latency_ms": settings.quality_p95_latency_alert_ms,
            "minimum_requests": settings.quality_min_request_count,
            "provider_stale_minutes": settings.quality_provider_stale_minutes,
        },
    }

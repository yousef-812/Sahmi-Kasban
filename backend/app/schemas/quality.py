from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ReadinessCheckResponse(BaseModel):
    name: str
    status: str
    detail: str | None = None


class ReadinessResponse(BaseModel):
    status: str
    service: str
    environment: str
    checks: list[ReadinessCheckResponse]


class RequestMetricsResponse(BaseModel):
    started_at: datetime
    sample_capacity: int
    sample_count: int
    total_requests: int
    in_flight: int
    error_requests: int
    error_rate_percent: float
    slow_requests: int
    average_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float
    status_counts: dict[str, int]


class ProviderQualityResponse(BaseModel):
    component: str
    provider: str
    status: str
    latency_ms: int | None = None
    observed_at: datetime
    stale: bool


class QualityAlertResponse(BaseModel):
    code: str
    severity: str
    message: str
    observed_value: float | int | str | None = None
    threshold: float | int | str | None = None


class QualityStatusResponse(BaseModel):
    status: str
    generated_at: datetime
    sentry_enabled: bool
    request_metrics: RequestMetricsResponse
    providers: list[ProviderQualityResponse]
    alerts: list[QualityAlertResponse]
    thresholds: dict[str, float | int] = Field(default_factory=dict)

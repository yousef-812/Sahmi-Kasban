from __future__ import annotations

import logging
import re
import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings
from app.core.observability import (
    bind_error_context,
    capture_exception,
    request_metrics,
    reset_request_id,
    set_request_id,
)

logger = logging.getLogger("app.requests")
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{8,128}$")


def normalize_request_id(candidate: str | None) -> str:
    value = (candidate or "").strip()
    if _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return uuid4().hex


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        settings = get_settings()
        request_id = normalize_request_id(request.headers.get("x-request-id"))
        token = set_request_id(request_id)
        request.state.request_id = request_id
        request_metrics.begin()
        started = time.perf_counter()
        bind_error_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            request_metrics.complete(
                status_code=500,
                duration_ms=duration_ms,
                slow_threshold_ms=settings.request_slow_threshold_ms,
            )
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 3),
                    "exception_type": type(exc).__name__,
                },
            )
            capture_exception(exc)
            reset_request_id(token)
            raise

        duration_ms = (time.perf_counter() - started) * 1000
        request_metrics.complete(
            status_code=response.status_code,
            duration_ms=duration_ms,
            slow_threshold_ms=settings.request_slow_threshold_ms,
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.3f}"
        log_level = logging.ERROR if response.status_code >= 500 else logging.INFO
        logger.log(
            log_level,
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 3),
                "slow": duration_ms >= settings.request_slow_threshold_ms,
            },
        )
        reset_request_id(token)
        return response

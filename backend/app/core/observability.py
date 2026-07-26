from __future__ import annotations

import json
import logging
import math
import sys
from collections import Counter, deque
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from threading import Lock
from typing import Any

import sentry_sdk

from app.core.config import Settings

_request_id: ContextVar[str] = ContextVar("request_id", default="-")


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = current_request_id()
        return True


class JsonLogFormatter(logging.Formatter):
    """Small JSON formatter that avoids logging request bodies or credentials."""

    _reserved = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", current_request_id()),
        }
        for key, value in record.__dict__.items():
            if key in self._reserved or key.startswith("_") or key in payload:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class RequestMetricsRegistry:
    """Process-local rolling request metrics for readiness and operator diagnostics."""

    def __init__(self, *, max_samples: int = 5_000) -> None:
        self._lock = Lock()
        self._max_samples = max_samples
        self._latencies_ms: deque[float] = deque(maxlen=max_samples)
        self._status_counts: Counter[int] = Counter()
        self._total_requests = 0
        self._error_requests = 0
        self._slow_requests = 0
        self._in_flight = 0
        self._started_at = datetime.now(UTC)

    def begin(self) -> None:
        with self._lock:
            self._in_flight += 1

    def complete(
        self,
        *,
        status_code: int,
        duration_ms: float,
        slow_threshold_ms: int,
    ) -> None:
        with self._lock:
            self._in_flight = max(0, self._in_flight - 1)
            self._total_requests += 1
            self._status_counts[status_code] += 1
            self._latencies_ms.append(round(duration_ms, 3))
            if status_code >= 500:
                self._error_requests += 1
            if duration_ms >= slow_threshold_ms:
                self._slow_requests += 1

    def reset(self) -> None:
        with self._lock:
            self._latencies_ms.clear()
            self._status_counts.clear()
            self._total_requests = 0
            self._error_requests = 0
            self._slow_requests = 0
            self._in_flight = 0
            self._started_at = datetime.now(UTC)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            latencies = sorted(self._latencies_ms)
            total = self._total_requests
            average = sum(latencies) / len(latencies) if latencies else 0.0
            if latencies:
                index = max(0, math.ceil(len(latencies) * 0.95) - 1)
                p95 = latencies[index]
                maximum = latencies[-1]
            else:
                p95 = 0.0
                maximum = 0.0
            error_rate = (self._error_requests / total * 100) if total else 0.0
            return {
                "started_at": self._started_at,
                "sample_capacity": self._max_samples,
                "sample_count": len(latencies),
                "total_requests": total,
                "in_flight": self._in_flight,
                "error_requests": self._error_requests,
                "error_rate_percent": round(error_rate, 3),
                "slow_requests": self._slow_requests,
                "average_latency_ms": round(average, 3),
                "p95_latency_ms": round(p95, 3),
                "max_latency_ms": round(maximum, 3),
                "status_counts": {
                    str(code): count for code, count in sorted(self._status_counts.items())
                },
            }


request_metrics = RequestMetricsRegistry()
_observability_initialized = False
_sentry_enabled = False


def current_request_id() -> str:
    return _request_id.get()


def set_request_id(value: str) -> Token[str]:
    return _request_id.set(value)


def reset_request_id(token: Token[str]) -> None:
    _request_id.reset(token)


def configure_observability(settings: Settings) -> None:
    global _observability_initialized, _sentry_enabled

    if not _observability_initialized:
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        handler = logging.StreamHandler(sys.stdout)
        handler.addFilter(RequestContextFilter())
        if settings.log_json:
            handler.setFormatter(JsonLogFormatter())
        else:
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(name)s "
                    "request_id=%(request_id)s %(message)s"
                )
            )
        root_logger.addHandler(handler)
        root_logger.setLevel(settings.log_level)
        logging.captureWarnings(True)
        _observability_initialized = True

    _sentry_enabled = settings.sentry_enabled
    if settings.sentry_enabled:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env.value,
            release=settings.sentry_release or None,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            send_default_pii=False,
            attach_stacktrace=True,
            max_breadcrumbs=100,
        )


def sentry_is_enabled() -> bool:
    return _sentry_enabled


def bind_error_context(*, request_id: str, method: str, path: str) -> None:
    if not _sentry_enabled:
        return
    sentry_sdk.set_tag("request_id", request_id)
    sentry_sdk.set_tag("http.method", method)
    sentry_sdk.set_tag("http.route_path", path)


def capture_exception(exc: BaseException) -> None:
    if _sentry_enabled:
        sentry_sdk.capture_exception(exc)

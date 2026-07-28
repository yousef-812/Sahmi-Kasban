import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from datetime import UTC, date, datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Environment, get_settings
from app.core.observability import configure_observability
from app.db.session import SessionLocal
from app.jobs.generate_daily_top10 import run_daily_top10_scan
from app.jobs.retry_pending_ai_reviews import (
    ai_provider_is_configured,
    retry_pending_ai_reviews,
)
from app.market_calendar import EGXTradingCalendar
from app.market_data.catalog import ensure_market_instrument_catalog
from app.middleware.request_context import RequestContextMiddleware

settings = get_settings()
configure_observability(settings)
cors_origins = settings.cors_origin_list
logger = logging.getLogger(__name__)


async def _warm_market_instrument_catalog() -> None:
    try:
        with SessionLocal() as db:
            await ensure_market_instrument_catalog(db)
    except Exception:
        logger.exception("Market instrument catalog warm-up failed")


async def _daily_market_report_scheduler() -> None:
    """Run the Cairo 5 PM scan without requiring an external cron service."""

    last_attempt_at: datetime | None = None
    completed_session_date: date | None = None
    retry_interval = timedelta(minutes=15)
    while True:
        now = datetime.now(UTC)
        calendar = EGXTradingCalendar.from_settings()
        local = now.astimezone(calendar.timezone)
        due = (
            calendar.is_trading_session(local.date())
            and local.timetz().replace(tzinfo=None) >= calendar.scan_time
        )
        retry_due = last_attempt_at is None or now - last_attempt_at >= retry_interval
        if due and completed_session_date != local.date() and retry_due:
            last_attempt_at = now
            try:
                result = await run_daily_top10_scan(now)
                status = str(result.get("status", ""))
                logger.info("Scheduled daily market scan finished: %s", result)
                if status in {"created", "already_exists"}:
                    completed_session_date = local.date()
            except Exception:
                logger.exception("Scheduled daily market scan failed; retrying in 15 minutes")
        await asyncio.sleep(60)


async def _community_ai_retry_scheduler() -> None:
    """Retry provider-failed discussions after AI credentials become available."""

    while True:
        try:
            await retry_pending_ai_reviews()
        except Exception:
            logger.exception("Pending discussion AI retry batch failed")
        await asyncio.sleep(600)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    warmup_task: asyncio.Task[None] | None = None
    market_scheduler_task: asyncio.Task[None] | None = None
    ai_retry_task: asyncio.Task[None] | None = None
    if settings.app_env is not Environment.TEST:
        warmup_task = asyncio.create_task(_warm_market_instrument_catalog())
        market_scheduler_task = asyncio.create_task(_daily_market_report_scheduler())
        if ai_provider_is_configured():
            ai_retry_task = asyncio.create_task(_community_ai_retry_scheduler())
    yield
    for task in (warmup_task, market_scheduler_task, ai_retry_task):
        if task is not None and not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan,
)

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(RequestContextMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "running",
        "health": f"{settings.api_v1_prefix}/health",
    }

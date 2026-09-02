import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Environment, get_settings
from app.core.observability import configure_observability
from app.core.production_readiness import enforce_production_readiness
from app.db.session import SessionLocal
from app.jobs.retry_pending_ai_reviews import (
    ai_provider_is_configured,
    retry_pending_ai_reviews,
)
from app.jobs.scheduler import run_daily_scan_scheduler
from app.jobs.weekly_grants import run_weekly_grant_scheduler
from app.legal_pages import router as legal_router
from app.market_data.broadcaster import get_quote_broadcaster
from app.market_data.catalog import ensure_market_instrument_catalog
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()
enforce_production_readiness(settings)
configure_observability(settings)
cors_origins = settings.cors_origin_list
logger = logging.getLogger(__name__)


async def _warm_market_instrument_catalog() -> None:
    try:
        with SessionLocal() as db:
            await ensure_market_instrument_catalog(db)
    except Exception:
        logger.exception("Market instrument catalog warm-up failed")


async def _community_ai_retry_scheduler() -> None:
    """Retry discussions that were paused while the AI provider was unavailable."""

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
    weekly_grant_task: asyncio.Task[None] | None = None
    ai_retry_task: asyncio.Task[None] | None = None
    broadcaster = get_quote_broadcaster()
    if settings.app_env is not Environment.TEST:
        warmup_task = asyncio.create_task(_warm_market_instrument_catalog())
        market_scheduler_task = asyncio.create_task(run_daily_scan_scheduler())
        weekly_grant_task = asyncio.create_task(run_weekly_grant_scheduler())
        await broadcaster.start()
        if ai_provider_is_configured():
            ai_retry_task = asyncio.create_task(_community_ai_retry_scheduler())
    yield
    await broadcaster.stop()
    for task in (
        warmup_task,
        market_scheduler_task,
        weekly_grant_task,
        ai_retry_task,
    ):
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
app.add_middleware(SecurityHeadersMiddleware, hsts_enabled=settings.is_production)
app.include_router(legal_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "running",
        "health": f"{settings.api_v1_prefix}/health",
        "legal": "/legal",
        "privacy": "/privacy",
        "delete_account": "/delete-account",
        "app_ads": "/app-ads.txt",
    }

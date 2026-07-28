import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Environment, get_settings
from app.core.observability import configure_observability
from app.db.session import SessionLocal
from app.jobs.daily_scheduler import run_daily_report_scheduler
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


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    tasks: list[asyncio.Task[None]] = []
    if settings.app_env is not Environment.TEST:
        tasks.append(asyncio.create_task(_warm_market_instrument_catalog()))
        tasks.append(asyncio.create_task(run_daily_report_scheduler()))
    yield
    for task in tasks:
        if not task.done():
            task.cancel()
    for task in tasks:
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

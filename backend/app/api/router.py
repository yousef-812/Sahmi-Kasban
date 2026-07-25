from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.profile import router as profile_router
from app.api.routes.wallet import router as wallet_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(wallet_router)
api_router.include_router(market_router)
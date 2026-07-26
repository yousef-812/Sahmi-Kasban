from fastapi import APIRouter

from app.api.routes.admin_operations import router as admin_operations_router
from app.api.routes.auth import router as auth_router
from app.api.routes.community import router as community_router
from app.api.routes.community_admin import router as community_admin_router
from app.api.routes.community_admin_appeals import router as community_admin_appeals_router
from app.api.routes.community_appeals import router as community_appeals_router
from app.api.routes.community_verification import router as community_verification_router
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.monetization import router as monetization_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.profile import router as profile_router
from app.api.routes.reports import router as reports_router
from app.api.routes.wallet import router as wallet_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(wallet_router)
api_router.include_router(market_router)
api_router.include_router(reports_router)
api_router.include_router(monetization_router)
api_router.include_router(notifications_router)
api_router.include_router(community_router)
api_router.include_router(community_appeals_router)
api_router.include_router(community_verification_router)
api_router.include_router(community_admin_router)
api_router.include_router(community_admin_appeals_router)
api_router.include_router(admin_operations_router)

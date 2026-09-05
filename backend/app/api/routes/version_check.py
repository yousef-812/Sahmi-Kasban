from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/app", tags=["app"])


class AppVersionResponse(BaseModel):
    latest_version: str = "1.0.2+29"
    latest_version_code: int = 29
    min_required_version_code: int = 1
    play_store_url: str = (
        "https://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile"
    )
    title_ar: str = "يتوفر تحديث جديد للتطبيق"
    message_ar: str = (
        "يتوفر إصدار أحدث للتطبيق يحتوي على تحسينات هامة وميزات جديدة. "
        "يرجى التحديث الآن للحصول على أفضل تجربة."
    )
    force_update: bool = False


@router.get("/version", response_model=AppVersionResponse)
def get_app_version() -> AppVersionResponse:
    return AppVersionResponse()

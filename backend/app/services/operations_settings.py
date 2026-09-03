from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models import AppSetting, CommunityAdminEvent

SettingKind = Literal["int", "float", "bool", "str"]


class OperationalSettingError(ValueError):
    """Raised when an operational setting is unknown or invalid."""


@dataclass(frozen=True, slots=True)
class SettingDefinition:
    key: str
    category: str
    label: str
    description: str
    kind: SettingKind
    default_value: object
    min_value: int | float | None = None
    max_value: int | float | None = None


def _definitions() -> tuple[SettingDefinition, ...]:
    settings = get_settings()
    return (
        SettingDefinition(
            "analysis_cost_points",
            "pricing",
            "تكلفة تحليل السهم",
            "عدد النقاط المخصومة عند إنشاء تحليل جديد غير مخزن.",
            "int",
            settings.analysis_cost_points,
            1,
            10_000,
        ),
        SettingDefinition(
            "daily_report_cost_points",
            "pricing",
            "تكلفة فتح التقرير اليومي",
            "عدد النقاط المخصومة لفتح تقرير أفضل الأسهم.",
            "int",
            settings.daily_report_cost_points,
            1,
            10_000,
        ),
        SettingDefinition(
            "ad_reward_points",
            "rewards",
            "مكافأة الإعلان",
            "عدد النقاط المضافة بعد تحقق مشاهدة الإعلان.",
            "int",
            settings.ad_reward_points,
            1,
            5_000,
        ),
        SettingDefinition(
            "ad_reward_daily_limit",
            "limits",
            "الحد اليومي للإعلانات",
            "أقصى عدد مكافآت إعلانية لكل مستخدم في يوم القاهرة.",
            "int",
            settings.ad_reward_daily_limit,
            1,
            50,
        ),
        SettingDefinition(
            "ad_reward_cooldown_seconds",
            "limits",
            "فاصل الإعلانات بالثواني",
            "المدة الدنيا بين جلستي إعلان مكافئتين.",
            "int",
            settings.ad_reward_cooldown_seconds,
            0,
            86_400,
        ),
        SettingDefinition(
            "community_short_window_minutes",
            "limits",
            "نافذة الإرسال القصيرة",
            "عدد الدقائق المستخدمة لحساب حد مناقشات المدى القصير.",
            "int",
            15,
            1,
            1_440,
        ),
        SettingDefinition(
            "community_short_window_limit",
            "limits",
            "حد المناقشات القصير",
            "أقصى عدد مناقشات داخل النافذة القصيرة.",
            "int",
            3,
            1,
            100,
        ),
        SettingDefinition(
            "community_daily_limit",
            "limits",
            "حد المناقشات اليومي",
            "أقصى عدد مناقشات للمستخدم خلال 24 ساعة.",
            "int",
            10,
            1,
            500,
        ),
        SettingDefinition(
            "notifications_enabled",
            "features",
            "الإشعارات مفعلة",
            "السماح بإنشاء إشعارات جديدة وإرسال Push عند توفر FCM.",
            "bool",
            True,
        ),
        SettingDefinition(
            "ai_personas_enabled",
            "automation",
            "تفعيل شخصيات الذكاء الاصطناعي",
            "السماح بتشغيل الشخصيات الخمسة لإنشاء مناقشات آلية في المجتمع.",
            "bool",
            True,
        ),
    )


def setting_definitions() -> dict[str, SettingDefinition]:
    return {item.key: item for item in _definitions()}


def _validate_value(definition: SettingDefinition, value: object) -> object:
    if definition.kind == "bool":
        if not isinstance(value, bool):
            raise OperationalSettingError(f"{definition.key} must be boolean")
        return value
    if definition.kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise OperationalSettingError(f"{definition.key} must be an integer")
    elif definition.kind == "float":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise OperationalSettingError(f"{definition.key} must be numeric")
        value = float(value)
    elif definition.kind == "str":
        if not isinstance(value, str):
            raise OperationalSettingError(f"{definition.key} must be text")
        value = value.strip()
    if definition.min_value is not None and value < definition.min_value:
        raise OperationalSettingError(f"{definition.key} must be at least {definition.min_value}")
    if definition.max_value is not None and value > definition.max_value:
        raise OperationalSettingError(f"{definition.key} must be at most {definition.max_value}")
    return value


def get_setting_value(db: Session, key: str) -> object:
    definition = setting_definitions().get(key)
    if definition is None:
        raise OperationalSettingError(f"Unknown operational setting: {key}")
    stored = db.get(AppSetting, key)
    return definition.default_value if stored is None else stored.value


def get_int_setting(db: Session, key: str) -> int:
    value = get_setting_value(db, key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise OperationalSettingError(f"{key} is not an integer setting")
    return value


def get_bool_setting(db: Session, key: str) -> bool:
    value = get_setting_value(db, key)
    if not isinstance(value, bool):
        raise OperationalSettingError(f"{key} is not a boolean setting")
    return value


def runtime_monetization_settings(db: Session) -> Settings:
    runtime = get_settings().model_copy(deep=False)
    runtime.ad_reward_points = get_int_setting(db, "ad_reward_points")
    runtime.ad_reward_daily_limit = get_int_setting(db, "ad_reward_daily_limit")
    runtime.ad_reward_cooldown_seconds = get_int_setting(db, "ad_reward_cooldown_seconds")
    return runtime


def list_operational_settings(
    db: Session,
) -> list[tuple[SettingDefinition, AppSetting | None]]:
    stored = {item.key: item for item in db.scalars(select(AppSetting)).all()}
    return [(definition, stored.get(definition.key)) for definition in _definitions()]


def update_operational_setting(
    db: Session,
    *,
    admin_user_id: UUID,
    key: str,
    value: object,
) -> AppSetting:
    definition = setting_definitions().get(key)
    if definition is None:
        raise OperationalSettingError(f"Unknown operational setting: {key}")
    normalized = _validate_value(definition, value)
    setting = db.get(AppSetting, key)
    previous_value = definition.default_value if setting is None else setting.value
    if setting is None:
        setting = AppSetting(
            key=definition.key,
            category=definition.category,
            value=normalized,
            description=definition.description,
            updated_by_user_id=admin_user_id,
        )
        db.add(setting)
    else:
        setting.value = normalized
        setting.category = definition.category
        setting.description = definition.description
        setting.updated_by_user_id = admin_user_id
    db.add(
        CommunityAdminEvent(
            actor_user_id=admin_user_id,
            action="operational_setting_updated",
            reason_code=None,
            details={
                "key": key,
                "previous_value": previous_value,
                "new_value": normalized,
            },
        )
    )
    db.flush()
    return setting

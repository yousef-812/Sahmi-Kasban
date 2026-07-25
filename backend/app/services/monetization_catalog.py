from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanDefinition:
    code: str
    display_name_ar: str
    weekly_points: int
    ads_enabled: bool
    product_id: str | None
    history_limit: int
    report_history_days: int
    badge_code: str | None = None


@dataclass(frozen=True, slots=True)
class CoinPackDefinition:
    product_id: str
    display_name_ar: str
    points: int


PLANS: tuple[PlanDefinition, ...] = (
    PlanDefinition(
        code="free",
        display_name_ar="المجانية",
        weekly_points=300,
        ads_enabled=True,
        product_id=None,
        history_limit=20,
        report_history_days=1,
    ),
    PlanDefinition(
        code="basic",
        display_name_ar="الأساسية",
        weekly_points=1_000,
        ads_enabled=False,
        product_id="sahmi_basic_monthly",
        history_limit=100,
        report_history_days=30,
        badge_code="basic",
    ),
    PlanDefinition(
        code="advanced",
        display_name_ar="المتقدمة",
        weekly_points=1_500,
        ads_enabled=False,
        product_id="sahmi_advanced_monthly",
        history_limit=250,
        report_history_days=90,
        badge_code="advanced",
    ),
    PlanDefinition(
        code="pro",
        display_name_ar="الاحترافية",
        weekly_points=5_000,
        ads_enabled=False,
        product_id="sahmi_pro_monthly",
        history_limit=1_000,
        report_history_days=365,
        badge_code="pro",
    ),
)

COIN_PACKS: tuple[CoinPackDefinition, ...] = (
    CoinPackDefinition(
        product_id="sahmi_coins_5",
        display_name_ar="5 عملات",
        points=500,
    ),
    CoinPackDefinition(
        product_id="sahmi_coins_15",
        display_name_ar="15 عملة",
        points=1_500,
    ),
    CoinPackDefinition(
        product_id="sahmi_coins_40",
        display_name_ar="40 عملة",
        points=4_000,
    ),
    CoinPackDefinition(
        product_id="sahmi_coins_100",
        display_name_ar="100 عملة",
        points=10_000,
    ),
)

_PLAN_BY_CODE = {plan.code: plan for plan in PLANS}
_PLAN_BY_PRODUCT_ID = {
    plan.product_id: plan for plan in PLANS if plan.product_id is not None
}
_COIN_PACK_BY_PRODUCT_ID = {pack.product_id: pack for pack in COIN_PACKS}


def get_plan(code: str) -> PlanDefinition:
    try:
        return _PLAN_BY_CODE[code]
    except KeyError as exc:
        raise ValueError(f"Unsupported plan code: {code}") from exc


def get_plan_by_product_id(product_id: str) -> PlanDefinition | None:
    return _PLAN_BY_PRODUCT_ID.get(product_id)


def get_coin_pack(product_id: str) -> CoinPackDefinition | None:
    return _COIN_PACK_BY_PRODUCT_ID.get(product_id)


def product_type_for(product_id: str) -> str | None:
    if product_id in _PLAN_BY_PRODUCT_ID:
        return "subscription"
    if product_id in _COIN_PACK_BY_PRODUCT_ID:
        return "coins"
    return None

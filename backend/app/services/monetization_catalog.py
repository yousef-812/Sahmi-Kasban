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
    features: tuple[str, ...]
    comparison_monthly_allowance: int
    max_comparison_stocks: int
    priority_level: int
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
        weekly_points=500,
        ads_enabled=True,
        product_id=None,
        history_limit=20,
        report_history_days=1,
        features=(
            "5 عملات أسبوعيًا",
            "تحليل سهم كامل باستخدام المحركات الأساسية",
            "تقرير أفضل 10 لمدة يوم واحد",
            "مقارنة حتى 3 أسهم مقابل 0.5 عملة",
            "إمكانية كسب عملات من الإعلانات المكافئة",
        ),
        comparison_monthly_allowance=0,
        max_comparison_stocks=3,
        priority_level=0,
    ),
    PlanDefinition(
        code="basic",
        display_name_ar="الأساسية",
        weekly_points=2_500,
        ads_enabled=False,
        product_id="sahmi_basic_monthly",
        history_limit=200,
        report_history_days=30,
        features=(
            "25 عملة أسبوعيًا",
            "بدون إعلانات",
            "سجل موسع للتحليلات والتقارير",
            "شرح ذكاء اصطناعي موسع",
            "مقارنة سهمين أربع مرات شهريًا",
            "ملف مخاطرة شخصي",
        ),
        comparison_monthly_allowance=4,
        max_comparison_stocks=2,
        priority_level=1,
        badge_code="basic",
    ),
    PlanDefinition(
        code="advanced",
        display_name_ar="المتقدمة",
        weekly_points=6_000,
        ads_enabled=False,
        product_id="sahmi_advanced_monthly",
        history_limit=1_000,
        report_history_days=365,
        features=(
            "60 عملة أسبوعيًا",
            "كل مزايا الخطة الأساسية",
            "مقارنة حتى 3 أسهم 12 مرة شهريًا",
            "تفاصيل كاملة للتحليل متعدد الأطر الزمنية",
            "خطط دخول محافظة ومتوازنة وهجومية",
            "ملخص مخاطرة مخصص لرأس المال",
            "أولوية أعلى وقت الضغط",
        ),
        comparison_monthly_allowance=12,
        max_comparison_stocks=3,
        priority_level=2,
        badge_code="advanced",
    ),
    PlanDefinition(
        code="pro",
        display_name_ar="الاحترافية",
        weekly_points=15_000,
        ads_enabled=False,
        product_id="sahmi_pro_monthly",
        history_limit=5_000,
        report_history_days=3_650,
        features=(
            "150 عملة أسبوعيًا",
            "كل مزايا الخطة المتقدمة",
            "مقارنة حتى 5 أسهم 40 مرة شهريًا",
            "تحليل قطاع كامل",
            "تصدير ومشاركة التقارير",
            "عدة ملفات مخاطرة ومحاكاة صفقات",
            "أولوية قصوى ووصول مبكر للميزات",
        ),
        comparison_monthly_allowance=40,
        max_comparison_stocks=5,
        priority_level=3,
        badge_code="pro",
    ),
)

COIN_PACKS: tuple[CoinPackDefinition, ...] = (
    CoinPackDefinition(
        product_id="sahmi_coins_10",
        display_name_ar="10 عملات",
        points=1_000,
    ),
    CoinPackDefinition(
        product_id="sahmi_coins_30",
        display_name_ar="30 عملة",
        points=3_000,
    ),
    CoinPackDefinition(
        product_id="sahmi_coins_75",
        display_name_ar="75 عملة",
        points=7_500,
    ),
    CoinPackDefinition(
        product_id="sahmi_coins_200",
        display_name_ar="200 عملة",
        points=20_000,
    ),
)

_PLAN_BY_CODE = {plan.code: plan for plan in PLANS}
_PLAN_BY_PRODUCT_ID = {plan.product_id: plan for plan in PLANS if plan.product_id is not None}
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

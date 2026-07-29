from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.market_data.types import MarketDataProvider
from app.models import StockComparison, User
from app.services.monetization_catalog import get_plan
from app.services.profile import get_active_subscription
from app.services.stock_analysis import execute_stock_analysis
from app.services.wallet import debit_points, get_wallet_account
from sahmi_kasban.ai import SahmiAIService

COMPARISON_COST_POINTS = 50
CAIRO = ZoneInfo("Africa/Cairo")


class ComparisonConflictError(RuntimeError):
    """Raised when an idempotency key is reused with different tickers."""


class ComparisonPlanLimitError(RuntimeError):
    """Raised when the selected plan cannot compare the requested number of stocks."""


@dataclass(frozen=True, slots=True)
class StockComparisonExecution:
    comparison: StockComparison
    idempotent: bool
    balance_points: int
    allowance_used: int
    allowance_remaining: int


def _map(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _number(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0


def _text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _month_bounds(moment: datetime) -> tuple[datetime, datetime]:
    local = moment.astimezone(CAIRO)
    start_local = datetime(local.year, local.month, 1, tzinfo=CAIRO)
    if local.month == 12:
        end_local = datetime(local.year + 1, 1, 1, tzinfo=CAIRO)
    else:
        end_local = datetime(local.year, local.month + 1, 1, tzinfo=CAIRO)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def _included_usage(
    db: Session,
    *,
    user_id: UUID,
    moment: datetime,
) -> int:
    start, end = _month_bounds(moment)
    return int(
        db.scalar(
            select(func.count(StockComparison.id)).where(
                StockComparison.user_id == user_id,
                StockComparison.included_allowance.is_(True),
                StockComparison.created_at >= start,
                StockComparison.created_at < end,
            )
        )
        or 0
    )


def _analysis_item(analysis) -> dict[str, object]:
    root = _map(analysis.payload)
    report = _map(root.get("analysis"))
    engines = _map(report.get("engines"))
    qualification = _map(engines.get("stock_qualification"))
    qualification_details = _map(qualification.get("details"))
    technical = _map(engines.get("technical"))
    technical_details = _map(technical.get("details"))
    risk = _map(engines.get("risk"))
    risk_details = _map(risk.get("details"))
    quantitative = _map(engines.get("quantitative"))
    trade_plan = _map(report.get("trade_plan"))

    final_score = _number(report.get("final_score"))
    confidence = _number(report.get("confidence"))
    risk_score = _number(risk.get("score"))
    qualification_score = _number(qualification.get("score"))
    quantitative_score = _number(quantitative.get("score"))
    comparison_score = round(
        final_score * 0.60
        + confidence * 0.20
        + risk_score * 0.10
        + qualification_score * 0.05
        + quantitative_score * 0.05,
        2,
    )

    return {
        "ticker": analysis.ticker,
        "analysis_id": str(analysis.id),
        "data_as_of": analysis.data_as_of.isoformat(),
        "signal": _text(report.get("signal")) or "WATCH",
        "final_score": round(final_score, 2),
        "confidence": round(confidence, 2),
        "comparison_score": comparison_score,
        "trend": _text(technical_details.get("trend")) or "neutral",
        "rsi": round(_number(technical_details.get("rsi")), 2),
        "average_volume_20": round(
            _number(qualification_details.get("average_volume_20")),
            2,
        ),
        "risk_level": _text(risk_details.get("risk_level")) or "unknown",
        "risk_score": round(risk_score, 2),
        "entry": round(_number(trade_plan.get("entry")), 4),
        "stop_loss": round(_number(trade_plan.get("stop_loss")), 4),
        "target_1": round(_number(trade_plan.get("target_1")), 4),
        "target_2": round(_number(trade_plan.get("target_2")), 4),
        "reward_risk_1": round(_number(trade_plan.get("reward_risk_1")), 2),
    }


def _summary(items: list[dict[str, object]]) -> str:
    best = items[0]
    strongest_risk = max(items, key=lambda item: _number(item.get("risk_score")))
    most_liquid = max(items, key=lambda item: _number(item.get("average_volume_20")))
    fragments = [
        f"{best['ticker']} حصل على أعلى تقييم مقارن بدرجة {best['comparison_score']} من 100.",
        f"{strongest_risk['ticker']} هو الأفضل في تقييم إدارة المخاطر.",
        f"{most_liquid['ticker']} هو الأعلى في متوسط حجم التداول بين الأسهم المختارة.",
    ]
    return " ".join(dict.fromkeys(fragments))


def _execution_from_existing(
    db: Session,
    comparison: StockComparison,
    *,
    allowance: int,
    moment: datetime,
) -> StockComparisonExecution:
    used = _included_usage(db, user_id=comparison.user_id, moment=moment)
    account = get_wallet_account(db, comparison.user_id)
    return StockComparisonExecution(
        comparison=comparison,
        idempotent=True,
        balance_points=account.balance_points,
        allowance_used=used,
        allowance_remaining=max(allowance - used, 0),
    )


async def execute_stock_comparison(
    db: Session,
    *,
    user: User,
    request_key: str,
    tickers: list[str],
    provider: MarketDataProvider,
    ai_service: SahmiAIService,
    language: str = "ar",
    moment: datetime | None = None,
) -> StockComparisonExecution:
    now = moment or datetime.now(UTC)
    normalized = list(dict.fromkeys(ticker.strip().upper() for ticker in tickers))
    if len(normalized) < 2:
        raise ComparisonPlanLimitError("Choose at least two different stocks")

    existing = db.scalar(
        select(StockComparison).where(
            StockComparison.user_id == user.id,
            StockComparison.request_key == request_key,
        )
    )
    subscription = get_active_subscription(db, user.id)
    plan = get_plan(subscription.plan_code)
    max_stocks = max(plan.max_comparison_stocks, 2)
    if plan.code == "free":
        max_stocks = 3

    if existing is not None:
        if existing.tickers != normalized:
            raise ComparisonConflictError(
                "The comparison request key was already used with other stocks"
            )
        return _execution_from_existing(
            db,
            existing,
            allowance=plan.comparison_monthly_allowance,
            moment=now,
        )

    if len(normalized) > max_stocks:
        raise ComparisonPlanLimitError(
            f"The {plan.display_name_ar} plan compares up to {max_stocks} stocks"
        )

    executions = []
    for ticker in normalized:
        executions.append(
            await execute_stock_analysis(
                db,
                user=user,
                ticker=ticker,
                provider=provider,
                ai_service=ai_service,
                language=language,
            )
        )

    items = [_analysis_item(execution.analysis) for execution in executions]
    items.sort(
        key=lambda item: (
            _number(item.get("comparison_score")),
            _number(item.get("confidence")),
            _number(item.get("average_volume_20")),
        ),
        reverse=True,
    )
    for rank, item in enumerate(items, start=1):
        item["rank"] = rank

    allowance_used_before = _included_usage(db, user_id=user.id, moment=now)
    included = allowance_used_before < plan.comparison_monthly_allowance
    comparison_charge = 0 if included else COMPARISON_COST_POINTS
    analysis_charge = sum(execution.charged_points for execution in executions)

    wallet_transaction_id: str | None = None
    if comparison_charge:
        wallet_transaction_id = f"stock-comparison:{user.id}:{request_key}"
        debit_points(
            db,
            user_id=user.id,
            amount_points=comparison_charge,
            transaction_id=wallet_transaction_id,
            entry_type="stock_comparison_debit",
            reference_type="stock_comparison",
            reference_id=request_key,
            details={
                "tickers": normalized,
                "plan_code": plan.code,
                "included_allowance": False,
            },
        )

    payload: dict[str, object] = {
        "version": 1,
        "best_ticker": items[0]["ticker"],
        "summary": _summary(items),
        "items": items,
        "disclaimer": (
            "المقارنة تحليل آلي لدعم القرار وليست توصية شراء أو بيع، "
            "ولا تضمن تحقيق أرباح."
        ),
    }
    comparison = StockComparison(
        user_id=user.id,
        request_key=request_key,
        tickers=normalized,
        analysis_ids=[str(execution.analysis.id) for execution in executions],
        plan_code=plan.code,
        included_allowance=included,
        charged_points=comparison_charge,
        analysis_charged_points=analysis_charge,
        wallet_transaction_id=wallet_transaction_id,
        payload=payload,
    )
    db.add(comparison)
    db.commit()
    db.refresh(comparison)

    allowance_used = allowance_used_before + (1 if included else 0)
    account = get_wallet_account(db, user.id)
    return StockComparisonExecution(
        comparison=comparison,
        idempotent=False,
        balance_points=account.balance_points,
        allowance_used=allowance_used,
        allowance_remaining=max(plan.comparison_monthly_allowance - allowance_used, 0),
    )

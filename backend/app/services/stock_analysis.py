from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime
from functools import lru_cache
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.types import CandleSeries, MarketDataProvider
from app.models import StockAnalysis, StockAnalysisAccess, User, WalletEntry
from app.services.operations_settings import get_int_setting
from app.services.wallet import (
    InsufficientBalanceError,
    debit_points,
    get_wallet_account,
)
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.ai import AIProviderError, SahmiAIService

logger = logging.getLogger(__name__)

DISCLAIMER_AR = (
    "هذا تحليل آلي لدعم القرار وليس توصية شراء أو بيع، ولا يضمن تحقيق أرباح. "
    "راجع بيانات السوق وتحمل مسؤولية قرارك الاستثماري."
)


@dataclass(frozen=True, slots=True)
class StockAnalysisExecution:
    analysis: StockAnalysis
    cached: bool
    charged_points: int
    balance_points: int
    market_snapshot_cached: bool


class StockAnalysisExecutionError(RuntimeError):
    """Raised when a complete stock analysis cannot be produced."""


def _json_default(value: Any) -> object:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    item = getattr(value, "item", None)
    if callable(item):
        return item()
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        return tolist()
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def _json_safe(value: object) -> object:
    return json.loads(json.dumps(value, default=_json_default, ensure_ascii=False))


def _analysis_cache_key(series: CandleSeries, language: str) -> str:
    """Build one deterministic analysis per completed market-data session.

    The market fingerprint is intentionally not part of the identity. Providers can
    serialize the same daily session slightly differently after a reconnect. Using
    the final candle timestamp keeps reinstalling the app or reconnecting the data
    provider from creating another paid analysis for the same market session.
    """

    settings = get_settings()
    identity = {
        "ticker": series.ticker,
        "data_as_of": series.data_as_of.isoformat(),
        "interval": series.interval,
        "period": series.period,
        "language": language,
        "engine_version": settings.analysis_engine_version,
        "capital": settings.analysis_default_capital,
        "risk_per_trade": settings.analysis_risk_per_trade,
        "max_position_value": settings.analysis_max_position_value,
        "min_history": settings.market_data_min_candles,
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return "stock-analysis:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _deterministic_explanation(report: dict[str, object]) -> str:
    labels = {"BUY": "شراء مشروط", "WATCH": "مراقبة", "AVOID": "تجنب"}
    signal = str(report.get("signal", "WATCH"))
    score = float(report.get("final_score", 0))
    confidence = float(report.get("confidence", 0))
    qualified = bool(report.get("qualified", False))
    qualification_text = "اجتاز فلاتر التأهيل" if qualified else "لم يجتز كل فلاتر التأهيل"
    return (
        f"نتيجة المحركات: {labels.get(signal, signal)}. الدرجة النهائية {score:.1f} من 100 "
        f"بثقة {confidence:.1f}%. السهم {qualification_text}. "
        "راجع خطة المخاطر والتحذيرات داخل التقرير قبل اتخاذ أي قرار."
    )


def _find_account_access(
    db: Session,
    *,
    user: User,
    analysis: StockAnalysis,
) -> StockAnalysisAccess | None:
    access = db.scalar(
        select(StockAnalysisAccess).where(
            StockAnalysisAccess.user_id == user.id,
            StockAnalysisAccess.analysis_id == analysis.id,
        )
    )
    if access is not None:
        return access

    # Preserve ownership for analyses paid before the access table existed.
    legacy_debit = db.scalar(
        select(WalletEntry).where(
            WalletEntry.user_id == user.id,
            WalletEntry.entry_type == "stock_analysis_debit",
            WalletEntry.reference_type == "stock_analysis",
            WalletEntry.reference_id == str(analysis.id),
        )
    )
    if legacy_debit is None:
        return None

    access = StockAnalysisAccess(
        user_id=user.id,
        analysis_id=analysis.id,
        wallet_transaction_id=legacy_debit.transaction_id,
        unlocked_at=legacy_debit.confirmed_at or legacy_debit.created_at,
    )
    db.add(access)
    db.flush()
    return access


def _unlock_analysis_for_account(
    db: Session,
    *,
    user: User,
    analysis: StockAnalysis,
    analysis_cost_points: int,
) -> tuple[int, int]:
    if _find_account_access(db, user=user, analysis=analysis) is not None:
        account = get_wallet_account(db, user.id)
        return 0, account.balance_points

    account = get_wallet_account(db, user.id)
    if account.balance_points < analysis_cost_points:
        db.rollback()
        raise InsufficientBalanceError("Insufficient balance for stock analysis")

    transaction_id = f"stock-analysis:{user.id}:{analysis.id}"
    debit_points(
        db,
        user_id=user.id,
        amount_points=analysis_cost_points,
        transaction_id=transaction_id,
        entry_type="stock_analysis_debit",
        reference_type="stock_analysis",
        reference_id=str(analysis.id),
        details={
            "ticker": analysis.ticker,
            "data_as_of": analysis.data_as_of.isoformat(),
            "configured_cost_points": analysis_cost_points,
        },
    )
    db.add(
        StockAnalysisAccess(
            user_id=user.id,
            analysis_id=analysis.id,
            wallet_transaction_id=transaction_id,
            unlocked_at=datetime.now(UTC),
        )
    )
    db.flush()
    account = get_wallet_account(db, user.id)
    return analysis_cost_points, account.balance_points


@lru_cache
def get_stock_ai_service() -> SahmiAIService:
    return SahmiAIService()


async def execute_stock_analysis(
    db: Session,
    *,
    user: User,
    ticker: str,
    provider: MarketDataProvider,
    ai_service: SahmiAIService,
    language: str = "ar",
) -> StockAnalysisExecution:
    settings = get_settings()
    analysis_cost_points = get_int_setting(db, "analysis_cost_points")
    series, market_snapshot_cached = await get_cached_or_fresh_history(
        db,
        provider,
        ticker,
    )
    cache_key = _analysis_cache_key(series, language)
    existing = db.scalar(
        select(StockAnalysis).where(
            StockAnalysis.cache_key == cache_key,
            StockAnalysis.status == "complete",
        )
    )
    if existing is not None:
        try:
            charged_points, balance_points = _unlock_analysis_for_account(
                db,
                user=user,
                analysis=existing,
                analysis_cost_points=analysis_cost_points,
            )
            db.commit()
        except IntegrityError:
            db.rollback()
            access = _find_account_access(db, user=user, analysis=existing)
            if access is None:
                raise
            account = get_wallet_account(db, user.id)
            charged_points = 0
            balance_points = account.balance_points
        return StockAnalysisExecution(
            analysis=existing,
            cached=True,
            charged_points=charged_points,
            balance_points=balance_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    config = AnalysisConfig(
        capital=settings.analysis_default_capital,
        risk_per_trade=settings.analysis_risk_per_trade,
        max_position_value=settings.analysis_max_position_value,
        min_history=settings.market_data_min_candles,
    )
    analyzer = SahmiKasbanAnalyzer(config)
    try:
        report = analyzer.analyze(series.ticker, pd.DataFrame(series.candles))
    except Exception as exc:
        db.rollback()
        raise StockAnalysisExecutionError(
            f"Core analysis failed for {series.ticker}"
        ) from exc

    report_payload = _json_safe(report.to_dict())
    if not isinstance(report_payload, dict):
        db.rollback()
        raise StockAnalysisExecutionError("Analysis payload is invalid")

    explanation = _deterministic_explanation(report_payload)
    explanation_source = "deterministic"
    try:
        explanation = await ai_service.explain_stock_analysis(
            ticker=series.ticker,
            analysis_payload=report_payload,
            language=language,
        )
        explanation_source = "ai"
    except AIProviderError as exc:
        logger.info("AI explanation fallback for %s: %s", series.ticker, exc)

    payload = {
        "version": settings.analysis_engine_version,
        "market_data": {
            "provider": series.provider,
            "interval": series.interval,
            "period": series.period,
            "data_as_of": series.data_as_of.isoformat(),
            "fingerprint": series.fingerprint,
            "candle_count": series.candle_count,
        },
        "analysis": report_payload,
        "explanation": explanation,
        "explanation_source": explanation_source,
        "disclaimer": DISCLAIMER_AR,
    }
    analysis = StockAnalysis(
        ticker=series.ticker,
        data_as_of=series.data_as_of,
        cache_key=cache_key,
        status="complete",
        payload=payload,
    )
    db.add(analysis)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raced = db.scalar(
            select(StockAnalysis).where(
                StockAnalysis.cache_key == cache_key,
                StockAnalysis.status == "complete",
            )
        )
        if raced is None:
            raise
        charged_points, balance_points = _unlock_analysis_for_account(
            db,
            user=user,
            analysis=raced,
            analysis_cost_points=analysis_cost_points,
        )
        db.commit()
        return StockAnalysisExecution(
            analysis=raced,
            cached=True,
            charged_points=charged_points,
            balance_points=balance_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    try:
        charged_points, balance_points = _unlock_analysis_for_account(
            db,
            user=user,
            analysis=analysis,
            analysis_cost_points=analysis_cost_points,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return StockAnalysisExecution(
        analysis=analysis,
        cached=False,
        charged_points=charged_points,
        balance_points=balance_points,
        market_snapshot_cached=market_snapshot_cached,
    )

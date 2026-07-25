from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.types import CandleSeries, MarketDataProvider
from app.models import StockAnalysis, User
from app.services.wallet import (
    InsufficientBalanceError,
    debit_points,
    get_wallet_account,
)
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.ai import SahmiAIService

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
    settings = get_settings()
    identity = {
        "ticker": series.ticker,
        "fingerprint": series.fingerprint,
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
        db.commit()
        account = get_wallet_account(db, user.id)
        return StockAnalysisExecution(
            analysis=existing,
            cached=True,
            charged_points=0,
            balance_points=account.balance_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    account = get_wallet_account(db, user.id)
    if account.balance_points < settings.analysis_cost_points:
        db.rollback()
        raise InsufficientBalanceError("Insufficient balance for stock analysis")

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
    except Exception as exc:
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
        account = get_wallet_account(db, user.id)
        return StockAnalysisExecution(
            analysis=raced,
            cached=True,
            charged_points=0,
            balance_points=account.balance_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    try:
        debit_points(
            db,
            user_id=user.id,
            amount_points=settings.analysis_cost_points,
            transaction_id=f"stock-analysis:{user.id}:{analysis.id}",
            entry_type="stock_analysis_debit",
            reference_type="stock_analysis",
            reference_id=str(analysis.id),
            details={
                "ticker": series.ticker,
                "data_fingerprint": series.fingerprint,
                "engine_version": settings.analysis_engine_version,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    account = get_wallet_account(db, user.id)
    return StockAnalysisExecution(
        analysis=analysis,
        cached=False,
        charged_points=settings.analysis_cost_points,
        balance_points=account.balance_points,
        market_snapshot_cached=market_snapshot_cached,
    )
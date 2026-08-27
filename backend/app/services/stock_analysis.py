from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime
from functools import lru_cache
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.types import CandleSeries, MarketDataProvider
from app.models import StockAnalysis, User, UserStockAnalysisAccess, WalletEntry
from app.services.market_index import fetch_index_series, resolve_index_name
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


async def _fetch_index_or_none(
    db: Session,
    provider: MarketDataProvider,
    ticker: str,
) -> CandleSeries | None:
    """Fetch the ticker's market index, degrading gracefully on failure.

    The index only feeds the market_index context engine and its BUY->WATCH
    gate; when index data is unavailable the analysis still runs index-free.
    """
    try:
        index_name = resolve_index_name(ticker)
        return await fetch_index_series(db, provider, index_name)
    except Exception as exc:
        logger.warning("Index fetch failed for %s (index-free analysis): %s", ticker, exc)
        return None


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


def _analysis_cache_key(
    series: CandleSeries,
    language: str,
    index_series: CandleSeries | None = None,
) -> str:
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
        "index_ticker": index_series.ticker if index_series else None,
        "index_fingerprint": index_series.fingerprint if index_series else None,
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


def _access_for(
    db: Session,
    *,
    user_id: UUID,
    analysis_id: UUID,
) -> UserStockAnalysisAccess | None:
    return db.scalar(
        select(UserStockAnalysisAccess).where(
            UserStockAnalysisAccess.user_id == user_id,
            UserStockAnalysisAccess.analysis_id == analysis_id,
        )
    )


def _legacy_payment_exists(
    db: Session,
    *,
    user_id: UUID,
    analysis_id: UUID,
) -> bool:
    return (
        db.scalar(
            select(WalletEntry.id).where(
                WalletEntry.user_id == user_id,
                WalletEntry.entry_type == "stock_analysis_debit",
                WalletEntry.reference_type == "stock_analysis",
                WalletEntry.reference_id == str(analysis_id),
            )
        )
        is not None
    )


def _grant_access(
    db: Session,
    *,
    user: User,
    analysis: StockAnalysis,
    moment: datetime,
) -> UserStockAnalysisAccess:
    access = _access_for(db, user_id=user.id, analysis_id=analysis.id)
    if access is None:
        access = UserStockAnalysisAccess(
            user_id=user.id,
            analysis_id=analysis.id,
            ticker=analysis.ticker,
            last_viewed_at=moment,
        )
        db.add(access)
    else:
        access.last_viewed_at = moment
    db.flush()
    return access


def _deliver_existing_analysis(
    db: Session,
    *,
    user: User,
    analysis: StockAnalysis,
    analysis_cost_points: int,
    market_snapshot_cached: bool,
) -> StockAnalysisExecution:
    current = datetime.now(UTC)
    access = _access_for(db, user_id=user.id, analysis_id=analysis.id)
    if access is None and _legacy_payment_exists(
        db,
        user_id=user.id,
        analysis_id=analysis.id,
    ):
        access = _grant_access(db, user=user, analysis=analysis, moment=current)

    account = get_wallet_account(db, user.id)
    if access is not None:
        access.last_viewed_at = current
        db.commit()
        return StockAnalysisExecution(
            analysis=analysis,
            cached=True,
            charged_points=0,
            balance_points=account.balance_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    if account.balance_points < analysis_cost_points:
        db.rollback()
        raise InsufficientBalanceError("Insufficient balance for stock analysis")

    _grant_access(db, user=user, analysis=analysis, moment=current)
    debit_points(
        db,
        user_id=user.id,
        amount_points=analysis_cost_points,
        transaction_id=f"stock-analysis:{user.id}:{analysis.id}",
        entry_type="stock_analysis_debit",
        reference_type="stock_analysis",
        reference_id=str(analysis.id),
        details={
            "ticker": analysis.ticker,
            "data_as_of": analysis.data_as_of.isoformat(),
            "reused_computation": True,
            "configured_cost_points": analysis_cost_points,
        },
    )
    db.commit()
    account = get_wallet_account(db, user.id)
    return StockAnalysisExecution(
        analysis=analysis,
        cached=True,
        charged_points=analysis_cost_points,
        balance_points=account.balance_points,
        market_snapshot_cached=market_snapshot_cached,
    )


def _recover_latest_legacy_analysis(
    db: Session,
    *,
    user: User,
    ticker: str,
) -> StockAnalysis | None:
    entries = db.scalars(
        select(WalletEntry)
        .where(
            WalletEntry.user_id == user.id,
            WalletEntry.entry_type == "stock_analysis_debit",
            WalletEntry.reference_type == "stock_analysis",
            WalletEntry.reference_id.is_not(None),
        )
        .order_by(WalletEntry.created_at.desc())
        .limit(200)
    ).all()
    for entry in entries:
        try:
            analysis_id = UUID(str(entry.reference_id))
        except (TypeError, ValueError):
            continue
        analysis = db.get(StockAnalysis, analysis_id)
        if analysis is None or analysis.status != "complete" or analysis.ticker != ticker:
            continue
        _grant_access(
            db,
            user=user,
            analysis=analysis,
            moment=datetime.now(UTC),
        )
        db.commit()
        return analysis
    return None


def latest_owned_stock_analysis(
    db: Session,
    *,
    user: User,
    ticker: str,
) -> StockAnalysisExecution | None:
    row = db.execute(
        select(UserStockAnalysisAccess, StockAnalysis)
        .join(StockAnalysis, StockAnalysis.id == UserStockAnalysisAccess.analysis_id)
        .where(
            UserStockAnalysisAccess.user_id == user.id,
            UserStockAnalysisAccess.ticker == ticker,
            StockAnalysis.status == "complete",
        )
        .order_by(
            StockAnalysis.data_as_of.desc(),
            UserStockAnalysisAccess.created_at.desc(),
        )
        .limit(1)
    ).one_or_none()
    if row is None:
        analysis = _recover_latest_legacy_analysis(db, user=user, ticker=ticker)
        if analysis is None:
            return None
        access = _access_for(db, user_id=user.id, analysis_id=analysis.id)
        if access is None:
            return None
    else:
        access, analysis = row

    access.last_viewed_at = datetime.now(UTC)
    db.commit()
    account = get_wallet_account(db, user.id)
    return StockAnalysisExecution(
        analysis=analysis,
        cached=True,
        charged_points=0,
        balance_points=account.balance_points,
        market_snapshot_cached=True,
    )


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
    index_series = await _fetch_index_or_none(db, provider, series.ticker)
    cache_key = _analysis_cache_key(series, language, index_series)
    existing = db.scalar(
        select(StockAnalysis).where(
            StockAnalysis.cache_key == cache_key,
            StockAnalysis.status == "complete",
        )
    )
    if existing is not None:
        return _deliver_existing_analysis(
            db,
            user=user,
            analysis=existing,
            analysis_cost_points=analysis_cost_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    account = get_wallet_account(db, user.id)
    if account.balance_points < analysis_cost_points:
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
        report = analyzer.analyze(
            series.ticker,
            pd.DataFrame(series.candles),
            index=(
                (index_series.ticker, pd.DataFrame(index_series.candles))
                if index_series is not None
                else None
            ),
        )
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

    from app.services.sector_quality import compute_sector_quality

    tech_eng = report_payload.get("engines", {}).get("technical", {}).get("details", {}) if isinstance(report_payload.get("engines"), dict) and isinstance(report_payload.get("engines", {}).get("technical"), dict) else {}
    ret_20d = tech_eng.get("return_20d_pct") if isinstance(tech_eng, dict) else None
    score_val = float(report_payload.get("final_score", 0)) if isinstance(report_payload, dict) else 0.0
    sector_quality = compute_sector_quality(
        series.ticker,
        score=score_val,
        return_20d=float(ret_20d) if isinstance(ret_20d, (int, float)) else None,
    )

    payload = {
        "version": settings.analysis_engine_version,
        "market_data": {
            "provider": series.provider,
            "interval": series.interval,
            "period": series.period,
            "data_as_of": series.data_as_of.isoformat(),
            "fingerprint": series.fingerprint,
            "candle_count": series.candle_count,
            "sector": sector_quality["sector_name"],
        },
        "index": (
            {
                "name": index_series.ticker,
                "provider": index_series.provider,
                "interval": index_series.interval,
                "data_as_of": index_series.data_as_of.isoformat(),
                "fingerprint": index_series.fingerprint,
            }
            if index_series is not None
            else None
        ),
        "analysis": report_payload,
        "explanation": explanation,
        "explanation_source": explanation_source,
        "disclaimer": DISCLAIMER_AR,
        "sector_quality": sector_quality,
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
        return _deliver_existing_analysis(
            db,
            user=user,
            analysis=raced,
            analysis_cost_points=analysis_cost_points,
            market_snapshot_cached=market_snapshot_cached,
        )

    try:
        _grant_access(
            db,
            user=user,
            analysis=analysis,
            moment=datetime.now(UTC),
        )
        debit_points(
            db,
            user_id=user.id,
            amount_points=analysis_cost_points,
            transaction_id=f"stock-analysis:{user.id}:{analysis.id}",
            entry_type="stock_analysis_debit",
            reference_type="stock_analysis",
            reference_id=str(analysis.id),
            details={
                "ticker": series.ticker,
                "data_fingerprint": series.fingerprint,
                "engine_version": settings.analysis_engine_version,
                "configured_cost_points": analysis_cost_points,
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
        charged_points=analysis_cost_points,
        balance_points=account.balance_points,
        market_snapshot_cached=market_snapshot_cached,
    )

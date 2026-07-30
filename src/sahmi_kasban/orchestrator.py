from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from sahmi_kasban.engines import (
    MarketEnvironmentEngine,
    MultiTimeframeEngine,
    OpportunityQualityEngine,
    QuantitativeEngine,
    RiskEngine,
    ScenarioEngine,
    SMCEngine,
    StockQualificationEngine,
    TechnicalEngine,
)
from sahmi_kasban.indicators import enrich_indicators, prepare_candles
from sahmi_kasban.models import AnalysisConfig, AnalysisReport, EngineResult, TradePlan
from sahmi_kasban.scoring import calculate_score_diagnostics, score_to_signal


class SahmiKasbanAnalyzer:
    """Run the core analysis engines in a deterministic pipeline."""

    def __init__(self, config: AnalysisConfig | None = None):
        self.config = config or AnalysisConfig()

    def analyze(
        self,
        ticker: str,
        candles: pd.DataFrame | Iterable[Mapping[str, Any]],
    ) -> AnalysisReport:
        symbol = ticker.strip().upper()
        if not symbol:
            raise ValueError("ticker cannot be empty")

        prepared = enrich_indicators(prepare_candles(candles))
        context: dict[str, object] = {"ticker": symbol}
        results: dict[str, EngineResult] = {}
        warnings: list[str] = []

        qualification = StockQualificationEngine(self.config).analyze(prepared, context)
        results[qualification.name] = qualification
        qualified = bool(qualification.details.get("qualified"))

        pipeline = [
            MarketEnvironmentEngine(self.config),
            TechnicalEngine(self.config),
            SMCEngine(self.config),
            MultiTimeframeEngine(self.config),
            QuantitativeEngine(self.config),
            RiskEngine(self.config),
        ]

        for engine in pipeline:
            try:
                result = engine.analyze(prepared, context)
            except Exception as exc:
                result = EngineResult(
                    name=engine.name,
                    score=0,
                    confidence=0,
                    status="error",
                    details={"error": str(exc)},
                    reasons=[f"{engine.name} failed"],
                )
                warnings.append(f"Engine {engine.name} failed: {exc}")
            results[result.name] = result
            context[f"{result.name}_score"] = result.score

        try:
            scenario = ScenarioEngine(self.config).analyze(prepared, context)
        except Exception as exc:
            scenario = EngineResult(
                name="scenario",
                score=0,
                confidence=0,
                status="error",
                details={"error": str(exc)},
                reasons=["scenario failed"],
            )
            warnings.append(f"Engine scenario failed: {exc}")
        results[scenario.name] = scenario

        diagnostics = calculate_score_diagnostics(results)
        final_score = diagnostics.final_score
        confidence = diagnostics.confidence
        risk_result = results.get("risk", EngineResult("risk", 0, 0))
        signal = score_to_signal(final_score, qualified, risk_result.score)
        trade_plan = context.get("trade_plan")
        if not isinstance(trade_plan, TradePlan):
            trade_plan = None

        if not qualified:
            warnings.extend(qualification.reasons)

        if diagnostics.conflict:
            warnings.append("Directional engines disagree; confidence and score were reduced")

        if signal == "BUY" and (
            len(diagnostics.bullish_engines) < 3 or diagnostics.bearish_engines
        ):
            signal = "WATCH"
            warnings.append("BUY downgraded because directional confirmation is insufficient")

        risk_level = str(risk_result.details.get("risk_level", ""))
        if signal == "BUY" and risk_level == "high":
            signal = "WATCH"
            warnings.append("BUY downgraded because the risk engine classified risk as high")

        if signal == "BUY" and confidence < 65:
            signal = "WATCH"
            warnings.append("BUY downgraded because aggregate confidence is low")

        context.update(
            {
                "signal": signal,
                "qualified": qualified,
                "final_score": final_score,
                "aggregate_confidence": confidence,
                "bullish_engine_count": len(diagnostics.bullish_engines),
                "bearish_engine_count": len(diagnostics.bearish_engines),
                "directional_conflict": diagnostics.conflict,
                "risk_level": risk_level,
                "total_risk_pct": risk_result.details.get("total_risk_pct", 0),
                "zero_volume_ratio": qualification.details.get("zero_volume_ratio", 1),
            }
        )
        opportunity_quality = OpportunityQualityEngine(self.config).analyze(prepared, context)

        analysis_quality = diagnostics.to_dict()
        analysis_quality.update(
            {
                "engine_version": "core-v2.2",
                "elite_assessment": dict(opportunity_quality.details),
            }
        )
        if signal == "BUY" and final_score >= 80 and not bool(
            opportunity_quality.details.get("engine_ready")
        ):
            failed_checks = opportunity_quality.details.get("failed_checks", [])
            warnings.append(
                "High score was not promoted to elite because quality gates failed: "
                + ", ".join(str(item) for item in failed_checks)
            )

        return AnalysisReport(
            ticker=symbol,
            signal=signal,
            final_score=final_score,
            confidence=confidence,
            qualified=qualified,
            engines=results,
            trade_plan=trade_plan,
            warnings=warnings,
            analysis_quality=analysis_quality,
        )

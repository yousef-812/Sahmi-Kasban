from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from sahmi_kasban.engines import (
    MarketEnvironmentEngine,
    MultiTimeframeEngine,
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
    """Run the core analysis engines in a deterministic, auditable pipeline."""

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
        context[f"{qualification.name}_score"] = qualification.score
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
        final_score = float(diagnostics["final_score"])
        confidence = float(diagnostics["confidence"])
        risk_score = results.get("risk", EngineResult("risk", 0, 0)).score
        signal = score_to_signal(
            final_score,
            qualified,
            risk_score,
            buy_threshold=self.config.buy_score_threshold,
            avoid_threshold=self.config.avoid_score_threshold,
            minimum_buy_risk=self.config.min_buy_risk_score,
        )
        trade_plan = context.get("trade_plan")
        if not isinstance(trade_plan, TradePlan):
            trade_plan = None

        if not qualified:
            warnings.extend(qualification.reasons)
        engine_dispersion = float(diagnostics.get("engine_dispersion", 0.0))
        if signal == "BUY" and confidence < self.config.min_buy_confidence:
            signal = "WATCH"
            warnings.append("BUY downgraded because aggregate confidence is below policy")
        if signal == "BUY" and engine_dispersion > self.config.max_buy_engine_dispersion:
            signal = "WATCH"
            warnings.append("BUY downgraded because directional engines disagree")
        if signal == "BUY" and trade_plan is None:
            signal = "WATCH"
            warnings.append("BUY downgraded because no valid risk plan was produced")

        diagnostics.update(
            {
                "engine_version": "core-v2",
                "buy_policy": {
                    "score_threshold": self.config.buy_score_threshold,
                    "minimum_confidence": self.config.min_buy_confidence,
                    "minimum_risk_score": self.config.min_buy_risk_score,
                    "maximum_engine_dispersion": self.config.max_buy_engine_dispersion,
                },
                "data_points": len(prepared),
            }
        )
        return AnalysisReport(
            ticker=symbol,
            signal=signal,
            final_score=final_score,
            confidence=confidence,
            qualified=qualified,
            engines=results,
            trade_plan=trade_plan,
            warnings=list(dict.fromkeys(warnings)),
            diagnostics=diagnostics,
        )

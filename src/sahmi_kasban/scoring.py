from __future__ import annotations

from collections.abc import Mapping
from statistics import pstdev

from sahmi_kasban.models import EngineResult, Signal

DEFAULT_WEIGHTS: dict[str, float] = {
    "stock_qualification": 0.08,
    "market_environment": 0.10,
    "technical": 0.22,
    "smc": 0.14,
    "multi_timeframe": 0.16,
    "quantitative": 0.18,
    "risk": 0.12,
}

DIRECTIONAL_ENGINES = (
    "market_environment",
    "technical",
    "smc",
    "multi_timeframe",
    "quantitative",
)


def calculate_score_diagnostics(
    engines: Mapping[str, EngineResult],
    weights: Mapping[str, float] | None = None,
) -> dict[str, object]:
    selected_weights = dict(weights or DEFAULT_WEIGHTS)
    weighted_score = 0.0
    weighted_confidence = 0.0
    effective_weight = 0.0
    available_base_weight = 0.0
    total_base_weight = sum(weight for weight in selected_weights.values() if weight > 0)
    contributions: dict[str, dict[str, float]] = {}

    for name, base_weight in selected_weights.items():
        result = engines.get(name)
        if result is None or result.status == "error" or base_weight <= 0:
            continue
        confidence_factor = 0.35 + 0.65 * (result.confidence / 100.0)
        adjusted_weight = base_weight * confidence_factor
        weighted_score += result.score * adjusted_weight
        weighted_confidence += result.confidence * adjusted_weight
        effective_weight += adjusted_weight
        available_base_weight += base_weight
        contributions[name] = {
            "score": result.score,
            "confidence": result.confidence,
            "base_weight": round(base_weight, 4),
            "effective_weight": round(adjusted_weight, 4),
        }

    if effective_weight <= 0:
        return {
            "final_score": 0.0,
            "confidence": 0.0,
            "raw_score": 0.0,
            "engine_dispersion": 0.0,
            "agreement": 0.0,
            "coverage": 0.0,
            "contributions": contributions,
        }

    raw_score = weighted_score / effective_weight
    raw_confidence = weighted_confidence / effective_weight
    directional_scores = [
        engines[name].score
        for name in DIRECTIONAL_ENGINES
        if name in engines and engines[name].status != "error"
    ]
    dispersion = pstdev(directional_scores) if len(directional_scores) >= 2 else 0.0
    agreement = max(0.0, min(100.0, 100.0 - dispersion * 2.5))
    coverage = (
        available_base_weight / total_base_weight if total_base_weight > 0 else 0.0
    )

    agreement_multiplier = 0.72 + 0.28 * (agreement / 100.0)
    calibrated_score = 50.0 + (raw_score - 50.0) * agreement_multiplier
    calibrated_confidence = raw_confidence * (
        0.62 + 0.28 * (agreement / 100.0) + 0.10 * coverage
    )

    return {
        "final_score": round(max(0.0, min(100.0, calibrated_score)), 2),
        "confidence": round(max(0.0, min(100.0, calibrated_confidence)), 2),
        "raw_score": round(raw_score, 2),
        "raw_confidence": round(raw_confidence, 2),
        "engine_dispersion": round(dispersion, 2),
        "agreement": round(agreement, 2),
        "coverage": round(coverage * 100.0, 2),
        "contributions": contributions,
    }


def calculate_final_score(
    engines: Mapping[str, EngineResult],
    weights: Mapping[str, float] | None = None,
) -> tuple[float, float]:
    diagnostics = calculate_score_diagnostics(engines, weights)
    return float(diagnostics["final_score"]), float(diagnostics["confidence"])


def score_to_signal(
    score: float,
    qualified: bool,
    risk_score: float,
    *,
    buy_threshold: float = 67.0,
    avoid_threshold: float = 42.0,
    minimum_buy_risk: float = 50.0,
) -> Signal:
    if not qualified or risk_score < 35 or score < avoid_threshold:
        return "AVOID"
    if score >= buy_threshold and risk_score >= minimum_buy_risk:
        return "BUY"
    return "WATCH"

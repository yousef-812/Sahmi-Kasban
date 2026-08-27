from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass

from sahmi_kasban.models import EngineResult, Signal

# Only directional evidence belongs in the directional score. Qualification is
# an eligibility gate and risk is a sizing/downside gate; mixing either into the
# direction score makes a tradability or volatility decision look like a price
# forecast. These weights preserve the previous relative directional weights.
DEFAULT_WEIGHTS: dict[str, float] = {
    "market_environment": 0.15,
    "technical": 0.225,
    "smc": 0.225,
    "multi_timeframe": 0.15,
    "quantitative": 0.15,
    "sector_momentum": 0.10,
}

DIRECTIONAL_ENGINES = frozenset(DEFAULT_WEIGHTS)


@dataclass(frozen=True, slots=True)
class ScoreDiagnostics:
    raw_score: float
    final_score: float
    confidence: float
    base_confidence: float
    dispersion: float
    consensus: float
    bullish_engines: tuple[str, ...]
    bearish_engines: tuple[str, ...]
    neutral_engines: tuple[str, ...]
    failed_engines: tuple[str, ...]
    conflict: bool
    used_weight: float

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["bullish_engines"] = list(self.bullish_engines)
        payload["bearish_engines"] = list(self.bearish_engines)
        payload["neutral_engines"] = list(self.neutral_engines)
        payload["failed_engines"] = list(self.failed_engines)
        payload["scoring_version"] = "directional-v2.1"
        payload["non_directional_gates"] = ["stock_qualification", "risk"]
        return payload


def calculate_score_diagnostics(
    engines: Mapping[str, EngineResult],
    weights: Mapping[str, float] | None = None,
) -> ScoreDiagnostics:
    """Aggregate directional engine scores and penalize weak agreement."""

    selected_weights = dict(weights or DEFAULT_WEIGHTS)
    weighted_score = 0.0
    weighted_confidence = 0.0
    used_weight = 0.0
    observations: list[tuple[float, float]] = []
    failed: list[str] = []

    bullish: list[str] = []
    bearish: list[str] = []
    neutral: list[str] = []

    for name, weight in selected_weights.items():
        result = engines.get(name)
        if result is None or result.status == "error" or weight <= 0:
            if result is None or (result is not None and result.status == "error"):
                failed.append(name)
            continue

        reliability = max(0.25, result.confidence / 100.0)
        effective_weight = weight * reliability
        weighted_score += result.score * effective_weight
        weighted_confidence += result.confidence * effective_weight
        used_weight += effective_weight
        observations.append((result.score, effective_weight))

        if name in DIRECTIONAL_ENGINES:
            if result.score >= 60:
                bullish.append(name)
            elif result.score <= 40:
                bearish.append(name)
            else:
                neutral.append(name)

    if used_weight <= 0:
        return ScoreDiagnostics(
            raw_score=0.0,
            final_score=0.0,
            confidence=0.0,
            base_confidence=0.0,
            dispersion=0.0,
            consensus=0.0,
            bullish_engines=(),
            bearish_engines=(),
            neutral_engines=(),
            failed_engines=tuple(sorted(failed)),
            conflict=False,
            used_weight=0.0,
        )

    raw_score = weighted_score / used_weight
    base_confidence = weighted_confidence / used_weight
    variance = (
        sum(weight * (score - raw_score) ** 2 for score, weight in observations)
        / used_weight
    )
    dispersion = math.sqrt(max(0.0, variance))
    consensus = max(0.0, 1.0 - min(1.0, dispersion / 35.0))
    conflict = bool(bullish and bearish)

    confidence = base_confidence * (0.70 + 0.30 * consensus)
    confidence -= min(15.0, len(failed) * 5.0)
    if conflict:
        confidence -= 10.0

    score_strength = 0.72 + 0.28 * consensus
    if conflict:
        score_strength *= 0.85
    final_score = 50.0 + (raw_score - 50.0) * score_strength

    return ScoreDiagnostics(
        raw_score=round(raw_score, 2),
        final_score=round(max(0.0, min(100.0, final_score)), 2),
        confidence=round(max(0.0, min(100.0, confidence)), 2),
        base_confidence=round(base_confidence, 2),
        dispersion=round(dispersion, 2),
        consensus=round(consensus * 100.0, 2),
        bullish_engines=tuple(sorted(bullish)),
        bearish_engines=tuple(sorted(bearish)),
        neutral_engines=tuple(sorted(neutral)),
        failed_engines=tuple(sorted(failed)),
        conflict=conflict,
        used_weight=round(used_weight, 4),
    )


def calculate_final_score(
    engines: Mapping[str, EngineResult],
    weights: Mapping[str, float] | None = None,
) -> tuple[float, float]:
    diagnostics = calculate_score_diagnostics(engines, weights)
    return diagnostics.final_score, diagnostics.confidence


def score_to_signal(
    score: float,
    qualified: bool,
    risk_score: float,
    config: Any | None = None,
) -> Signal:
    buy_score = getattr(config, "signal_buy_score_threshold", 67.0) if config is not None else 67.0
    buy_risk = getattr(config, "signal_buy_risk_threshold", 50.0) if config is not None else 50.0
    avoid_score = getattr(config, "signal_avoid_score_threshold", 42.0) if config is not None else 42.0
    avoid_risk = getattr(config, "signal_avoid_risk_threshold", 35.0) if config is not None else 35.0

    if not qualified or risk_score < avoid_risk or score < avoid_score:
        return "AVOID"
    if score >= buy_score and risk_score >= buy_risk:
        return "BUY"
    return "WATCH"

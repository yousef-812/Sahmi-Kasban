# Project Structure & Contents: `src`

## Folder Tree

```
src/
├── sahmi_kasban
│   ├── ai
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── prompts.py
│   │   └── service.py
│   ├── engines
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── market.py
│   │   ├── market_index.py
│   │   ├── multi_timeframe.py
│   │   ├── opportunity_quality.py
│   │   ├── quantitative.py
│   │   ├── risk.py
│   │   ├── scenario.py
│   │   ├── smc.py
│   │   └── technical.py
│   ├── __init__.py
│   ├── backtesting.py
│   ├── index_resolver.py
│   ├── indicators.py
│   ├── models.py
│   ├── orchestrator.py
│   └── scoring.py
└── sahmi_kasban.egg-info
    ├── dependency_links.txt
    ├── PKG-INFO
    ├── requires.txt
    ├── SOURCES.txt
    └── top_level.txt
```

---

## File Contents

### File: `sahmi_kasban\__init__.py`

```py
from sahmi_kasban.backtesting import (
    BacktestObservation,
    BacktestSummary,
    walk_forward_backtest,
)
from sahmi_kasban.models import AnalysisConfig, AnalysisReport, EngineResult, TradePlan
from sahmi_kasban.orchestrator import SahmiKasbanAnalyzer
from sahmi_kasban.scoring import ScoreDiagnostics, calculate_score_diagnostics

__all__ = [
    "AnalysisConfig",
    "AnalysisReport",
    "BacktestObservation",
    "BacktestSummary",
    "EngineResult",
    "SahmiKasbanAnalyzer",
    "ScoreDiagnostics",
    "TradePlan",
    "calculate_score_diagnostics",
    "walk_forward_backtest",
]

```

---

### File: `sahmi_kasban\backtesting.py`

```py
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from statistics import median
from typing import Any, Protocol

import pandas as pd

from sahmi_kasban.indicators import enrich_indicators, prepare_candles
from sahmi_kasban.models import AnalysisReport


class AnalyzerProtocol(Protocol):
    def analyze(
        self,
        ticker: str,
        candles: pd.DataFrame | Iterable[Mapping[str, Any]],
        index: tuple[str, pd.DataFrame | Iterable[Mapping[str, Any]]] | None = None,
    ) -> AnalysisReport: ...

    def analyze_prepared(
        self,
        ticker: str,
        candles: pd.DataFrame,
        index: tuple[str, pd.DataFrame] | None = None,
    ) -> AnalysisReport: ...


@dataclass(frozen=True, slots=True)
class BacktestObservation:
    cutoff_index: int
    data_as_of: str | None
    signal: str
    score: float
    confidence: float
    entry: float
    exit: float
    forward_return_pct: float
    max_upside_pct: float
    max_drawdown_pct: float
    correct: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BacktestSummary:
    ticker: str
    horizon_sessions: int
    step_sessions: int
    observations: int
    buy_count: int
    watch_count: int
    avoid_count: int
    directional_accuracy_pct: float
    buy_hit_rate_pct: float
    avoid_hit_rate_pct: float
    watch_hit_rate_pct: float
    average_forward_return_pct: float
    median_forward_return_pct: float
    average_buy_return_pct: float
    average_buy_max_drawdown_pct: float
    profit_factor: float | None
    results: tuple[BacktestObservation, ...] = field(default_factory=tuple)

    def to_dict(self, *, include_results: bool = True) -> dict[str, object]:
        payload = asdict(self)
        payload["results"] = (
            [result.to_dict() for result in self.results] if include_results else []
        )
        return payload


def _percentage(numerator: int, denominator: int) -> float:
    return round(numerator / denominator * 100.0, 2) if denominator else 0.0


def _timestamp_at(frame: pd.DataFrame, index: int) -> str | None:
    if "timestamp" not in frame.columns:
        return None
    value = frame.iloc[index]["timestamp"]
    isoformat = getattr(value, "isoformat", None)
    return str(isoformat()) if callable(isoformat) else str(value)


def walk_forward_backtest(
    ticker: str,
    candles: pd.DataFrame | Iterable[Mapping[str, Any]],
    *,
    analyzer: AnalyzerProtocol | None = None,
    index: tuple[str, pd.DataFrame | Iterable[Mapping[str, Any]]] | None = None,
    min_train_size: int = 200,
    horizon_sessions: int = 5,
    step_sessions: int = 5,
    neutral_band_pct: float = 1.0,
) -> BacktestSummary:
    """Evaluate frozen historical signals without exposing future candles to the analyzer.

    ``index`` is an optional ``(index_name, candles)`` pair for the market_index
    context engine; the index history is sliced to each cutoff so no future
    index data leaks into the evaluation.
    """

    if min_train_size < 60:
        raise ValueError("min_train_size must be at least 60")
    if horizon_sessions <= 0:
        raise ValueError("horizon_sessions must be positive")
    if step_sessions <= 0:
        raise ValueError("step_sessions must be positive")
    if neutral_band_pct < 0:
        raise ValueError("neutral_band_pct cannot be negative")

    if analyzer is None:
        from sahmi_kasban.orchestrator import SahmiKasbanAnalyzer

        analyzer = SahmiKasbanAnalyzer()

    prepared = prepare_candles(candles)
    if len(prepared) < min_train_size + horizon_sessions:
        raise ValueError("not enough candles for the requested walk-forward backtest")

    has_analyze_prepared = hasattr(analyzer, "analyze_prepared")
    if has_analyze_prepared:
        enriched = enrich_indicators(prepared)
    else:
        enriched = prepared

    prepared_index = None
    if index is not None:
        index_name, index_candles = index
        index_name = (index_name or "").strip().upper()
        if not index_name:
            raise ValueError("index name cannot be empty")
        prepared_index = prepare_candles(index_candles)

    observations: list[BacktestObservation] = []
    for cutoff in range(
        min_train_size,
        len(prepared) - horizon_sessions + 1,
        step_sessions,
    ):
        history = enriched.iloc[:cutoff]
        future = prepared.iloc[cutoff : cutoff + horizon_sessions]
        report_index = None
        if prepared_index is not None:
            cutoff_ts = history.iloc[-1]["timestamp"]
            index_slice = prepared_index.loc[
                prepared_index["timestamp"] <= cutoff_ts
            ]
            if len(index_slice) >= 60:
                report_index = (index_name, index_slice)
        if has_analyze_prepared:
            report = analyzer.analyze_prepared(ticker, history, index=report_index)
        else:
            report = analyzer.analyze(ticker, history, index=report_index)

        entry = float(history.iloc[-1]["close"])
        exit_price = float(future.iloc[-1]["close"])
        forward_return = (exit_price / entry - 1.0) * 100.0
        max_upside = (float(future["high"].max()) / entry - 1.0) * 100.0
        max_drawdown = (float(future["low"].min()) / entry - 1.0) * 100.0

        if report.signal == "BUY":
            correct = forward_return > neutral_band_pct
        elif report.signal == "AVOID":
            correct = forward_return < -neutral_band_pct
        else:
            correct = abs(forward_return) <= neutral_band_pct

        observations.append(
            BacktestObservation(
                cutoff_index=cutoff,
                data_as_of=_timestamp_at(prepared, cutoff - 1),
                signal=report.signal,
                score=round(float(report.final_score), 2),
                confidence=round(float(report.confidence), 2),
                entry=round(entry, 4),
                exit=round(exit_price, 4),
                forward_return_pct=round(forward_return, 2),
                max_upside_pct=round(max_upside, 2),
                max_drawdown_pct=round(max_drawdown, 2),
                correct=correct,
            )
        )

    buys = [item for item in observations if item.signal == "BUY"]
    watches = [item for item in observations if item.signal == "WATCH"]
    avoids = [item for item in observations if item.signal == "AVOID"]
    directional = buys + avoids
    returns = [item.forward_return_pct for item in observations]
    buy_returns = [item.forward_return_pct for item in buys]

    gross_profit = sum(value for value in buy_returns if value > 0)
    gross_loss = abs(sum(value for value in buy_returns if value < 0))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else None

    return BacktestSummary(
        ticker=ticker.strip().upper(),
        horizon_sessions=horizon_sessions,
        step_sessions=step_sessions,
        observations=len(observations),
        buy_count=len(buys),
        watch_count=len(watches),
        avoid_count=len(avoids),
        directional_accuracy_pct=_percentage(
            sum(item.correct for item in directional), len(directional)
        ),
        buy_hit_rate_pct=_percentage(sum(item.correct for item in buys), len(buys)),
        avoid_hit_rate_pct=_percentage(sum(item.correct for item in avoids), len(avoids)),
        watch_hit_rate_pct=_percentage(sum(item.correct for item in watches), len(watches)),
        average_forward_return_pct=round(sum(returns) / len(returns), 2),
        median_forward_return_pct=round(median(returns), 2),
        average_buy_return_pct=round(sum(buy_returns) / len(buy_returns), 2)
        if buy_returns
        else 0.0,
        average_buy_max_drawdown_pct=round(
            sum(item.max_drawdown_pct for item in buys) / len(buys), 2
        )
        if buys
        else 0.0,
        profit_factor=profit_factor,
        results=tuple(observations),
    )

```

---

### File: `sahmi_kasban\index_resolver.py`

```py
from __future__ import annotations

EGX30_INDEX_NAME = "EGX30"
EGX70_INDEX_NAME = "EGX70"

# Curated EGX30 proxy seeded from the 2025 correlation study: tickers whose
# returns tracked the EGX30 distinctly better than the EGX70 among the most
# liquid names. Meant as a deterministic default; the authoritative list can be
# supplied at call time via egx30_tickers.
EGX30_TICKERS: frozenset[str] = frozenset(
    {
        "ABUK",
        "ADIB",
        "CCAP",
        "COMI",
        "EAST",
        "EFIH",
        "EGAL",
        "ETEL",
        "FWRY",
        "HRHO",
        "ISPH",
        "ORAS",
        "TMGH",
    }
)


def resolve_index_for_ticker(
    ticker: str | None,
    *,
    egx30_tickers: frozenset[str] | set[str] | None = None,
) -> str:
    symbol = (ticker or "").strip().upper()
    members = frozenset(egx30_tickers or EGX30_TICKERS)
    return EGX30_INDEX_NAME if symbol in members else EGX70_INDEX_NAME

```

---

### File: `sahmi_kasban\indicators.py`

```py
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("open", "high", "low", "close", "volume")


def prepare_candles(candles: pd.DataFrame | Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    df = candles.copy() if isinstance(candles, pd.DataFrame) else pd.DataFrame(candles)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"missing candle columns: {', '.join(missing)}")

    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df = df.sort_values("timestamp")

    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    df["volume"] = df["volume"].fillna(0.0).clip(lower=0.0)
    if df.empty:
        raise ValueError("no valid candles")
    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("prices must be positive")
    return df


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)
    avg_gain = gains.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = losses.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    values = 100.0 - (100.0 / (1.0 + rs))
    return values.fillna(50.0)


def true_range(df: pd.DataFrame) -> pd.Series:
    previous_close = df["close"].shift(1)
    ranges = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    return true_range(df).ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def rolling_vwap(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    حساب متوسط السعر المرجح بحجم التداول (Rolling VWAP)
    نستخدم نافذة متحركة (20 يوم افتراضياً) لأن بياناتنا يومية، وهذا يعكس 
    تكلفة الدخول المتوسطة للمؤسسات خلال الشهر الأخير.
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    volume = df["volume"].clip(lower=0.0)

    rolling_vp = (typical_price * volume).rolling(window=window, min_periods=1).sum()
    rolling_vol = volume.rolling(window=window, min_periods=1).sum()

    vwap = rolling_vp / rolling_vol.replace(0.0, pd.NA)
    return vwap.fillna(typical_price)


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["sma_20"] = sma(enriched["close"], 20)
    enriched["sma_50"] = sma(enriched["close"], 50)
    enriched["sma_200"] = sma(enriched["close"], 200)
    enriched["ema_12"] = ema(enriched["close"], 12)
    enriched["ema_26"] = ema(enriched["close"], 26)
    enriched["macd"] = enriched["ema_12"] - enriched["ema_26"]
    enriched["macd_signal"] = ema(enriched["macd"], 9)
    enriched["rsi"] = rsi(enriched["close"])
    enriched["atr"] = atr(enriched)
    enriched["avg_volume_20"] = enriched["volume"].rolling(20, min_periods=5).mean()
    enriched["vwap_20"] = rolling_vwap(enriched, window=20)
    enriched["return_1d"] = enriched["close"].pct_change()
    enriched["return_20d"] = enriched["close"].pct_change(20)
    enriched["volatility_20d"] = enriched["return_1d"].rolling(20, min_periods=10).std()
    return enriched


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return default if not np.isfinite(parsed) else parsed

```

---

### File: `sahmi_kasban\models.py`

```py
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Signal = Literal["BUY", "WATCH", "AVOID"]
EngineStatus = Literal["complete", "rejected", "error"]


@dataclass(slots=True)
class AnalysisConfig:
    capital: float = 150_000.0
    risk_per_trade: float = 0.01
    max_position_value: float = 40_000.0
    max_positions: int = 4
    min_history: int = 60
    min_average_volume: float = 100_000.0
    min_average_turnover_egp: float = 1_000_000.0
    atr_min_pct: float = 0.5
    atr_max_pct: float = 8.0
    min_qualification_score: float = 50.0
    stop_atr_multiple: float = 2.0
    target_1_r: float = 1.0
    target_2_r: float = 1.75
    # Opportunity quality & tuning thresholds
    elite_min_directional_score: float = 80.0
    elite_min_confidence: float = 70.0
    balanced_max_return_20d_pct: float = 30.0
    balanced_base_max_atr_pct: float = 4.5
    balanced_base_max_total_risk_pct: float = 30.0
    aggressive_min_return_20d_pct: float = 5.0
    aggressive_max_return_20d_pct: float = 45.0
    aggressive_max_return_5d_pct: float = 15.0
    aggressive_min_breakout_pct: float = 2.0
    aggressive_max_breakout_pct: float = 12.0
    aggressive_min_volume_ratio: float = 2.0
    aggressive_min_turnover_egp: float = 5_000_000.0
    elite_max_zero_volume_ratio: float = 0.10
    aggressive_max_zero_volume_ratio: float = 0.05
    # Signal thresholds
    signal_buy_score_threshold: float = 67.0
    signal_buy_risk_threshold: float = 50.0
    signal_avoid_score_threshold: float = 42.0
    signal_avoid_risk_threshold: float = 35.0
    # SMC Order Block thresholds
    smc_ob_displacement_multiplier: float = 1.5
    smc_ob_volume_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if not 0 < self.risk_per_trade <= 0.10:
            raise ValueError("risk_per_trade must be between 0 and 0.10")
        if self.max_position_value <= 0:
            raise ValueError("max_position_value must be positive")
        if self.min_average_volume < 0:
            raise ValueError("min_average_volume cannot be negative")
        if self.min_average_turnover_egp < 0:
            raise ValueError("min_average_turnover_egp cannot be negative")
        if self.atr_min_pct < 0 or self.atr_max_pct <= self.atr_min_pct:
            raise ValueError("invalid ATR range")
        if self.target_1_r <= 0 or self.target_2_r <= self.target_1_r:
            raise ValueError("reward targets must be positive and increasing")


@dataclass(slots=True)
class EngineResult:
    name: str
    score: float
    confidence: float
    status: EngineStatus = "complete"
    details: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.score = round(max(0.0, min(100.0, float(self.score))), 2)
        self.confidence = round(max(0.0, min(100.0, float(self.confidence))), 2)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TradePlan:
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_per_share: float
    reward_risk_1: float
    reward_risk_2: float
    position_size: int
    position_value: float
    risk_amount: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AnalysisReport:
    ticker: str
    signal: Signal
    final_score: float
    confidence: float
    qualified: bool
    engines: dict[str, EngineResult]
    trade_plan: TradePlan | None = None
    warnings: list[str] = field(default_factory=list)
    analysis_quality: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "signal": self.signal,
            "final_score": self.final_score,
            "confidence": self.confidence,
            "qualified": self.qualified,
            "engines": {name: result.to_dict() for name, result in self.engines.items()},
            "trade_plan": self.trade_plan.to_dict() if self.trade_plan else None,
            "warnings": list(self.warnings),
            "analysis_quality": dict(self.analysis_quality),
        }

```

---

### File: `sahmi_kasban\orchestrator.py`

```py
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd

from sahmi_kasban.engines import (
    MarketEnvironmentEngine,
    MarketIndexEngine,
    MultiTimeframeEngine,
    OpportunityQualityEngine,
    QuantitativeEngine,
    RiskEngine,
    ScenarioEngine,
    SMCEngine,
    StockQualificationEngine,
    TechnicalEngine,
)
from sahmi_kasban.indicators import enrich_indicators, prepare_candles, safe_float
from sahmi_kasban.models import AnalysisConfig, AnalysisReport, EngineResult, TradePlan
from sahmi_kasban.scoring import calculate_score_diagnostics, score_to_signal

_REQUIRED_PREPARED_COLUMNS = frozenset(
    {
        "open",
        "high",
        "low",
        "close",
        "volume",
        "sma_20",
        "sma_50",
        "sma_200",
        "macd",
        "macd_signal",
        "rsi",
        "atr",
        "avg_volume_20",
        "vwap_20",
        "return_1d",
        "return_20d",
        "volatility_20d",
    }
)


def _is_prepared_candles(candles: Any) -> bool:
    if not isinstance(candles, pd.DataFrame) or candles.empty:
        return False
    required = ("open", "high", "low", "close", "volume")
    if not set(required).issubset(candles.columns):
        return False
    if "timestamp" in candles.columns:
        if not pd.api.types.is_datetime64_any_dtype(candles["timestamp"]):
            return False
    return True


def _prepare_index(
    index: tuple[str, pd.DataFrame | Iterable[Mapping[str, Any]]] | None,
) -> tuple[str, pd.DataFrame] | None:
    if index is None:
        return None
    index_name, index_candles = index
    index_name = (index_name or "").strip().upper()
    if not index_name:
        raise ValueError("index name cannot be empty")
    if _is_prepared_candles(index_candles):
        return index_name, index_candles
    return index_name, prepare_candles(index_candles)


class SahmiKasbanAnalyzer:
    """Run the core analysis engines in a deterministic pipeline."""

    def __init__(self, config: AnalysisConfig | None = None):
        self.config = config or AnalysisConfig()

    @staticmethod
    def _symbol(ticker: str) -> str:
        symbol = ticker.strip().upper()
        if not symbol:
            raise ValueError("ticker cannot be empty")
        return symbol

    def analyze(
        self,
        ticker: str,
        candles: pd.DataFrame | Iterable[Mapping[str, Any]],
        index: tuple[str, pd.DataFrame | Iterable[Mapping[str, Any]]] | None = None,
    ) -> AnalysisReport:
        """Prepare raw candles and run the full analysis pipeline.

        ``index`` is an optional ``(index_name, candles)`` pair for the
        market_index context engine; when omitted the engine and its
        BUY->WATCH gate are skipped.
        """

        symbol = self._symbol(ticker)
        prepared = enrich_indicators(prepare_candles(candles))
        return self._analyze_enriched(symbol, prepared, _prepare_index(index))

    def analyze_prepared(
        self,
        ticker: str,
        candles: pd.DataFrame,
        index: tuple[str, pd.DataFrame] | None = None,
    ) -> AnalysisReport:
        """Analyze a causal indicator frame that was prepared once by a replay.

        Replay callers pass strict prefixes of a frame produced by
        ``enrich_indicators``. Every indicator is trailing-only, so this is
        equivalent to enriching each prefix separately without repeating the
        rolling calculations thousands of times.

        ``index`` is an optional ``(index_name, candles)`` pair for the
        market_index context engine.
        """

        symbol = self._symbol(ticker)
        if candles.empty:
            raise ValueError("no valid candles")
        missing = sorted(_REQUIRED_PREPARED_COLUMNS.difference(candles.columns))
        if missing:
            raise ValueError(
                "prepared candles are missing indicator columns: " + ", ".join(missing)
            )
        return self._analyze_enriched(symbol, candles, _prepare_index(index))

    def _analyze_enriched(
        self,
        symbol: str,
        prepared: pd.DataFrame,
        index: tuple[str, pd.DataFrame] | None = None,
    ) -> AnalysisReport:
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

        if index is not None:
            index_name, index_candles = index
            context["market_index_name"] = index_name
            stock_return_20d = safe_float(
                results.get(
                    "market_environment",
                    EngineResult("market_environment", 0, 0),
                )
                .details.get("return_20d_pct"),
                None,
            )
            try:
                market_index = MarketIndexEngine(self.config).analyze(
                    index_candles,
                    context,
                    index_name=index_name,
                    stock_return_20d_pct=stock_return_20d,
                )
            except Exception as exc:
                market_index = EngineResult(
                    name="market_index",
                    score=0,
                    confidence=0,
                    status="error",
                    details={"error": str(exc)},
                    reasons=["market_index failed"],
                )
                warnings.append(f"Engine market_index failed: {exc}")
            results[market_index.name] = market_index

        diagnostics = calculate_score_diagnostics(results)
        final_score = diagnostics.final_score
        confidence = diagnostics.confidence
        risk_result = results.get("risk", EngineResult("risk", 0, 0))
        signal = score_to_signal(final_score, qualified, risk_result.score, config=self.config)
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

        if signal == "BUY" and index is not None:
            index_trend = str(context.get("market_index_trend", ""))
            if index_trend == "bearish":
                signal = "WATCH"
                warnings.append("BUY downgraded because the market index trend is bearish")

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
                "average_turnover_egp": qualification.details.get(
                    "average_turnover_egp_20",
                    0,
                ),
            }
        )
        opportunity_quality = OpportunityQualityEngine(self.config).analyze(prepared, context)

        analysis_quality = diagnostics.to_dict()
        analysis_quality.update(
            {
                "engine_version": "core-v2.5",
                "elite_assessment": dict(opportunity_quality.details),
            }
        )
        if signal == "BUY" and final_score >= 80 and not bool(
            opportunity_quality.details.get("engine_ready")
        ):
            balanced_failed = opportunity_quality.details.get(
                "balanced_failed_checks",
                [],
            )
            aggressive_failed = opportunity_quality.details.get(
                "aggressive_failed_checks",
                [],
            )
            warnings.append(
                "High score was not promoted to elite because both Core v2.3 "
                "profiles failed. Balanced: "
                + ", ".join(str(item) for item in balanced_failed)
                + "; aggressive: "
                + ", ".join(str(item) for item in aggressive_failed)
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

```

---

### File: `sahmi_kasban\scoring.py`

```py
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
    "technical": 0.275,
    "smc": 0.225,
    "multi_timeframe": 0.175,
    "quantitative": 0.175,
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

```

---

### File: `sahmi_kasban\ai\__init__.py`

```py
from sahmi_kasban.ai.client import AIChatClient, AIClientConfig, AIProviderError
from sahmi_kasban.ai.service import SahmiAIService

__all__ = [
    "AIChatClient",
    "AIClientConfig",
    "AIProviderError",
    "SahmiAIService",
]

```

---

### File: `sahmi_kasban\ai\client.py`

```py
from __future__ import annotations

import asyncio
import os
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import httpx


class AIProviderError(RuntimeError):
    """Raised when all configured AI providers fail."""


@dataclass(frozen=True, slots=True)
class AIClientConfig:
    """Configuration for Open-WebUI and Groq-compatible chat APIs."""

    open_webui_url: str = ""
    open_webui_api_key: str = ""
    groq_api_keys: tuple[str, ...] = ()
    default_model: str = "llama-3.3-70b-versatile"
    timeout_seconds: float = 45.0
    max_tokens: int = 1800
    temperature: float = 0.2

    @classmethod
    def from_env(cls) -> AIClientConfig:
        raw_keys = os.getenv("GROQ_API_KEYS", "")
        keys = tuple(key.strip() for key in raw_keys.split(",") if key.strip())
        return cls(
            open_webui_url=os.getenv("OPEN_WEBUI_URL", "").strip(),
            open_webui_api_key=os.getenv("OPEN_WEBUI_API_KEY", "").strip(),
            groq_api_keys=keys,
            default_model=os.getenv("AI_MODEL", "llama-3.3-70b-versatile").strip(),
            timeout_seconds=float(os.getenv("AI_TIMEOUT_SECONDS", "45")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1800")),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.2")),
        )


class AIChatClient:
    """Async chat client with Open-WebUI primary and Groq key-rotation fallback."""

    GROQ_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, config: AIClientConfig | None = None) -> None:
        self.config = config or AIClientConfig.from_env()
        self._key_index = 0
        self._key_lock = asyncio.Lock()

    @staticmethod
    def _normalize_open_webui_base(url: str) -> str:
        base = url.rstrip("/")
        if not base:
            return ""
        if base.endswith("/chat/completions"):
            return base.removesuffix("/chat/completions")
        if base.endswith(("/v1", "/api/v1", "/api")):
            return base
        return f"{base}/api/v1"

    @staticmethod
    def _headers(api_key: str) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def _ordered_groq_keys(self) -> tuple[str, ...]:
        async with self._key_lock:
            keys = self.config.groq_api_keys
            if not keys:
                return ()
            start = self._key_index % len(keys)
            ordered = keys[start:] + keys[:start]
            self._key_index = (start + 1) % len(keys)
            return ordered

    async def _post_completion(
        self,
        *,
        base_url: str,
        api_key: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"{base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(url, headers=self._headers(api_key), json=payload)
        if response.status_code >= 400:
            detail = response.text[:500]
            raise AIProviderError(f"AI provider returned {response.status_code}: {detail}")
        try:
            return response.json()
        except ValueError as exc:
            raise AIProviderError("AI provider returned invalid JSON") from exc

    async def chat(
        self,
        messages: Iterable[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self.config.default_model,
            "messages": list(messages),
            "temperature": self.config.temperature if temperature is None else temperature,
            "max_tokens": self.config.max_tokens if max_tokens is None else max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        failures: list[str] = []
        open_webui_base = self._normalize_open_webui_base(self.config.open_webui_url)
        if open_webui_base:
            try:
                data = await self._post_completion(
                    base_url=open_webui_base,
                    api_key=self.config.open_webui_api_key,
                    payload=payload,
                )
                return self._extract_content(data)
            except (AIProviderError, httpx.HTTPError) as exc:
                failures.append(f"Open-WebUI: {exc}")

        for key in await self._ordered_groq_keys():
            try:
                data = await self._post_completion(
                    base_url=self.GROQ_BASE_URL,
                    api_key=key,
                    payload=payload,
                )
                return self._extract_content(data)
            except (AIProviderError, httpx.HTTPError) as exc:
                failures.append(f"Groq: {exc}")

        if not open_webui_base and not self.config.groq_api_keys:
            raise AIProviderError(
                "No AI provider configured. Set OPEN_WEBUI_URL or GROQ_API_KEYS."
            )
        raise AIProviderError("All AI providers failed. " + " | ".join(failures))

    async def list_models(self) -> list[str]:
        providers: list[tuple[str, str]] = []
        open_webui_base = self._normalize_open_webui_base(self.config.open_webui_url)
        if open_webui_base:
            providers.append((open_webui_base, self.config.open_webui_api_key))
        keys = await self._ordered_groq_keys()
        if keys:
            providers.append((self.GROQ_BASE_URL, keys[0]))

        for base_url, key in providers:
            try:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.get(
                        f"{base_url.rstrip('/')}/models",
                        headers=self._headers(key),
                    )
                response.raise_for_status()
                data = response.json()
                models = [item["id"] for item in data.get("data", []) if item.get("id")]
                if models:
                    return models
            except (httpx.HTTPError, ValueError, KeyError):
                continue
        return [self.config.default_model]

    @staticmethod
    def _extract_content(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("AI response is missing message content") from exc
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError("AI response content is empty")
        return content.strip()

```

---

### File: `sahmi_kasban\ai\prompts.py`

```py
STOCK_ANALYSIS_SYSTEM_PROMPT = """
أنت مساعد تحليل مالي متخصص في البورصة المصرية. تعتمد فقط على البيانات المرسلة من
محركات Sahmi-Kasban، ولا تخترع أسعارًا أو مؤشرات غير موجودة. ابدأ بقرار واضح، ثم
لخص أسباب القرار والمخاطر، واختم ببيان أن المحتوى تحليلي وليس ضمانًا للربح.
""".strip()

DISCUSSION_MODERATION_SYSTEM_PROMPT = """
أنت نظام مراجعة محتوى لمجتمع متخصص في أسهم البورصة المصرية. أعد JSON فقط.
اسمح بالنشر عندما تكون المناقشة مرتبطة بالأسهم أو السوق، ولا تحتوي على:
- أرقام هواتف أو بريد إلكتروني أو روابط تواصل أو أسماء مستخدمين بغرض التواصل.
- دعوة للانتقال إلى تطبيق أو قناة أو مجموعة خارجية.
- سبام أو إهانة أو محتوى غير متعلق بالاستثمار والأسهم.
- ادعاء مضمون بالربح أو انتحال صفة جهة رقابية.
صيغة الرد:
{
  "approved": true,
  "category": "clean",
  "reason": "سبب مختصر",
  "flags": []
}
""".strip()

PREDICTION_EXTRACTION_SYSTEM_PROMPT = """
استخرج توقع المستخدم من مناقشة سهم في صورة JSON فقط. لا تخمن معلومة غير مكتوبة.
صيغة الرد:
{
  "ticker": null,
  "company_name": null,
  "direction": "up|down|sideways|unknown",
  "target_price": null,
  "minimum_price": null,
  "maximum_price": null,
  "deadline": null,
  "path_description": null,
  "claims": [],
  "specificity": 0.0
}
القيمة specificity بين صفر وواحد حسب دقة التوقع وقابليته للقياس.
""".strip()

PREDICTION_VERIFICATION_SYSTEM_PROMPT = """
قيّم توقعًا سابقًا بعد انتهاء الفترة المحددة، بالاعتماد فقط على التوقع المستخرج
وبيانات السوق الفعلية. أعد JSON فقط بالصيغة التالية:
{
  "level": "rejected|weak|strong|very_strong",
  "score": 0.0,
  "reward_coins": 0.0,
  "matched_claims": [],
  "failed_claims": [],
  "reason": "تفسير مختصر"
}
قواعد المكافأة:
- rejected: صفر
- weak: 0.5
- strong: 1.0
- very_strong: 2.0
لا تمنح very_strong إلا لتوقع محدد متعدد العناصر ثبتت صحته بوضوح.
""".strip()

```

---

### File: `sahmi_kasban\ai\service.py`

```py
from __future__ import annotations

import json
import re
from typing import Any

from sahmi_kasban.ai.client import AIChatClient, AIProviderError
from sahmi_kasban.ai.prompts import (
    DISCUSSION_MODERATION_SYSTEM_PROMPT,
    PREDICTION_EXTRACTION_SYSTEM_PROMPT,
    PREDICTION_VERIFICATION_SYSTEM_PROMPT,
    STOCK_ANALYSIS_SYSTEM_PROMPT,
)


class SahmiAIService:
    """High-level AI operations used by the future API and Flutter application."""

    def __init__(self, client: AIChatClient | None = None) -> None:
        self.client = client or AIChatClient()

    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict[str, Any],
        language: str = "ar",
    ) -> str:
        user_payload = {
            "ticker": ticker.upper(),
            "language": language,
            "analysis": analysis_payload,
        }
        return await self.client.chat(
            [
                {"role": "system", "content": STOCK_ANALYSIS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False, default=str),
                },
            ]
        )

    async def moderate_discussion(self, text: str) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=DISCUSSION_MODERATION_SYSTEM_PROMPT,
            payload={"discussion": text},
        )
        result.setdefault("approved", False)
        result.setdefault("category", "unknown")
        result.setdefault("reason", "تعذر تحديد سبب واضح")
        result.setdefault("flags", [])
        return result

    async def extract_prediction(self, text: str) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=PREDICTION_EXTRACTION_SYSTEM_PROMPT,
            payload={"discussion": text},
        )
        result.setdefault("ticker", None)
        result.setdefault("direction", "unknown")
        result.setdefault("target_price", None)
        result.setdefault("deadline", None)
        result.setdefault("claims", [])
        result.setdefault("specificity", 0.0)
        return result

    async def verify_prediction(
        self,
        *,
        prediction: dict[str, Any],
        market_outcome: dict[str, Any],
    ) -> dict[str, Any]:
        result = await self._chat_json(
            system_prompt=PREDICTION_VERIFICATION_SYSTEM_PROMPT,
            payload={
                "prediction": prediction,
                "market_outcome": market_outcome,
            },
        )
        allowed_rewards = {
            "rejected": 0.0,
            "weak": 0.5,
            "strong": 1.0,
            "very_strong": 2.0,
        }
        level = str(result.get("level", "rejected"))
        if level not in allowed_rewards:
            level = "rejected"
        result["level"] = level
        result["reward_coins"] = allowed_rewards[level]
        result.setdefault("matched_claims", [])
        result.setdefault("failed_claims", [])
        result.setdefault("reason", "")
        return result

    async def _chat_json(
        self,
        *,
        system_prompt: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        content = await self.client.chat(
            [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False, default=str),
                },
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return self._parse_json_object(content)

    @staticmethod
    def _parse_json_object(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise AIProviderError("AI response did not contain a JSON object") from exc
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError as nested_exc:
                raise AIProviderError("AI response contained invalid JSON") from nested_exc
        if not isinstance(parsed, dict):
            raise AIProviderError("AI JSON response must be an object")
        return parsed

```

---

### File: `sahmi_kasban\engines\__init__.py`

```py
from sahmi_kasban.engines.market import MarketEnvironmentEngine, StockQualificationEngine
from sahmi_kasban.engines.market_index import MarketIndexEngine
from sahmi_kasban.engines.multi_timeframe import MultiTimeframeEngine
from sahmi_kasban.engines.opportunity_quality import OpportunityQualityEngine
from sahmi_kasban.engines.quantitative import QuantitativeEngine
from sahmi_kasban.engines.risk import RiskEngine
from sahmi_kasban.engines.scenario import ScenarioEngine
from sahmi_kasban.engines.smc import SMCEngine
from sahmi_kasban.engines.technical import TechnicalEngine

__all__ = [
    "MarketEnvironmentEngine",
    "MarketIndexEngine",
    "MultiTimeframeEngine",
    "OpportunityQualityEngine",
    "QuantitativeEngine",
    "RiskEngine",
    "SMCEngine",
    "ScenarioEngine",
    "StockQualificationEngine",
    "TechnicalEngine",
]

```

---

### File: `sahmi_kasban\engines\base.py`

```py
from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from sahmi_kasban.models import AnalysisConfig, EngineResult


class AnalysisEngine(ABC):
    name = "base"

    def __init__(self, config: AnalysisConfig):
        self.config = config

    @abstractmethod
    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        raise NotImplementedError

    @staticmethod
    def clamp(value: float) -> float:
        return max(0.0, min(100.0, value))

```

---

### File: `sahmi_kasban\engines\market.py`

```py
from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class MarketEnvironmentEngine(AnalysisEngine):
    name = "market_environment"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        sma_20 = safe_float(latest.get("sma_20"), close)
        sma_50 = safe_float(latest.get("sma_50"), close)
        sma_200 = safe_float(latest.get("sma_200"), sma_50)
        volatility = safe_float(latest.get("volatility_20d")) * (252**0.5) * 100
        atr_value = safe_float(latest.get("atr"))
        atr_pct = atr_value / close * 100.0 if close > 0 else 0.0
        volume = safe_float(latest.get("volume"))
        avg_volume = safe_float(latest.get("avg_volume_20"), volume)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 0.0
        return_20d_pct = safe_float(latest.get("return_20d")) * 100.0
        return_5d_pct = 0.0
        if len(candles) >= 6:
            close_5d = safe_float(candles.iloc[-6].get("close"))
            if close_5d > 0:
                return_5d_pct = (close / close_5d - 1.0) * 100.0

        bullish_points = sum(
            [
                close > sma_20,
                close > sma_50,
                sma_20 > sma_50,
                sma_50 > sma_200,
            ]
        )
        bearish_points = sum(
            [
                close < sma_20,
                close < sma_50,
                sma_20 < sma_50,
                sma_50 < sma_200,
            ]
        )

        if bullish_points >= 3:
            regime = "bullish"
            score = 72 + bullish_points * 5
        elif bearish_points >= 3:
            regime = "bearish"
            score = 28 - bearish_points * 3
        else:
            regime = "sideways"
            score = 50

        if regime == "bullish" and volume_ratio >= 1.5 and return_5d_pct > 2:
            profile = "breakout_bullish"
        elif regime == "bullish" and volatility > 65:
            profile = "speculative_bullish"
        elif regime == "bullish":
            profile = "trend_bullish"
        elif regime == "bearish" and volatility > 65:
            profile = "risk_off_volatile"
        elif regime == "bearish":
            profile = "trend_bearish"
        elif abs(return_20d_pct) <= 8 and volatility <= 55:
            profile = "sideways_rotation"
        else:
            profile = "mixed_volatile"

        if volatility > 65:
            score -= 8
        elif volatility < 35:
            score += 4
        if avg_volume > 0 and volume > avg_volume * 1.25:
            score += 4 if regime == "bullish" else -2 if regime == "bearish" else 1

        score = self.clamp(score)
        context["market_regime"] = regime
        context["market_regime_profile"] = profile
        context["annualized_volatility"] = volatility
        context["market_volume_ratio"] = volume_ratio
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(95.0, 55.0 + abs(score - 50.0)),
            details={
                "model_version": "market-regime-v2.3",
                "regime": regime,
                "regime_profile": profile,
                "annualized_volatility_pct": round(volatility, 2),
                "atr_pct": round(atr_pct, 2),
                "return_5d_pct": round(return_5d_pct, 2),
                "return_20d_pct": round(return_20d_pct, 2),
                "bullish_checks": bullish_points,
                "bearish_checks": bearish_points,
                "volume_ratio": round(volume_ratio, 2),
            },
            reasons=[f"Market regime: {regime} ({profile})"],
        )


class StockQualificationEngine(AnalysisEngine):
    name = "stock_qualification"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        history_count = len(candles)
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"))
        atr_pct = (atr_value / close * 100.0) if close > 0 else 0.0
        recent = candles.tail(20)
        average_volume = safe_float(recent["volume"].mean())
        average_turnover = safe_float((recent["close"] * recent["volume"]).mean())
        zero_volume_ratio = float((candles["volume"].tail(60) <= 0).mean())

        checks = {
            "history": history_count >= self.config.min_history,
            "liquidity": average_turnover >= self.config.min_average_turnover_egp,
            "atr_range": self.config.atr_min_pct <= atr_pct <= self.config.atr_max_pct,
            "volume_continuity": zero_volume_ratio <= 0.20,
            "valid_price": close > 0,
        }
        weights = {
            "history": 20.0,
            "liquidity": 30.0,
            "atr_range": 25.0,
            "volume_continuity": 15.0,
            "valid_price": 10.0,
        }
        score = sum(weights[key] for key, passed in checks.items() if passed)
        critical_checks = (
            checks["history"],
            checks["liquidity"],
            checks["atr_range"],
            checks["valid_price"],
        )
        qualified = score >= self.config.min_qualification_score and all(critical_checks)
        context["qualified"] = qualified
        context["atr_pct"] = atr_pct
        context["average_turnover_egp"] = average_turnover

        failed = [key for key, passed in checks.items() if not passed]
        return EngineResult(
            name=self.name,
            score=score,
            confidence=90.0 if history_count >= self.config.min_history else 55.0,
            status="complete" if qualified else "rejected",
            details={
                "qualified": qualified,
                "checks": checks,
                "history_count": history_count,
                "average_volume_20": round(average_volume, 2),
                "average_turnover_egp_20": round(average_turnover, 2),
                "liquidity_threshold_egp": round(
                    self.config.min_average_turnover_egp,
                    2,
                ),
                "atr_pct": round(atr_pct, 2),
                "zero_volume_ratio": round(zero_volume_ratio, 3),
            },
            reasons=[] if qualified else [f"Failed qualification: {', '.join(failed)}"],
        )

```

---

### File: `sahmi_kasban\engines\market_index.py`

```py
from __future__ import annotations

import numpy as np
import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class MarketIndexEngine(AnalysisEngine):
    """Context engine reporting the direction of a market index.

    The engine is advisory only: it is never blended into the directional
    score and never reweights ``DEFAULT_WEIGHTS``. Its trend feeds a
    BUY->WATCH gate in the orchestrator when the index is bearish.
    """

    name = "market_index"

    def analyze(
        self,
        candles: pd.DataFrame,
        context: dict[str, object],
        *,
        index_name: str = "",
        stock_return_20d_pct: float | None = None,
    ) -> EngineResult:
        frame = candles.reset_index(drop=True).copy()
        close = pd.to_numeric(frame["close"], errors="coerce")
        volume = pd.to_numeric(frame["volume"], errors="coerce").fillna(0.0)

        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        sma_200 = close.rolling(200).mean()
        returns = close.pct_change()
        annualized_vol = returns.rolling(20).std() * (252**0.5)
        avg_volume_20 = volume.rolling(20).mean()
        return_20d = close.pct_change(20)

        last_close = safe_float(close.iloc[-1], 0.0)
        last_sma20 = safe_float(sma_20.iloc[-1], last_close)
        last_sma50 = safe_float(sma_50.iloc[-1], last_close)
        last_sma200 = safe_float(sma_200.iloc[-1], last_sma50)
        last_vol = safe_float(annualized_vol.iloc[-1], 0.0) * 100.0
        last_volume = safe_float(volume.iloc[-1], 0.0)
        last_avg_volume = safe_float(avg_volume_20.iloc[-1], last_volume)
        index_return_20d = safe_float(return_20d.iloc[-1], 0.0) * 100.0

        bull = sum(
            [
                last_close > last_sma20,
                last_close > last_sma50,
                last_sma20 > last_sma50,
                last_sma50 > last_sma200,
            ]
        )
        bear = sum(
            [
                last_close < last_sma20,
                last_close < last_sma50,
                last_sma20 < last_sma50,
                last_sma50 < last_sma200,
            ]
        )

        if bull >= 3:
            trend = "bullish"
            score = 72.0 + bull * 5.0
        elif bear >= 3:
            trend = "bearish"
            score = 28.0 - bear * 3.0
        else:
            trend = "sideways"
            score = 50.0

        if last_vol > 65.0:
            score -= 8.0
        elif last_vol < 35.0:
            score += 4.0
        volume_ratio = last_volume / last_avg_volume if last_avg_volume > 0 else 0.0
        if last_avg_volume > 0 and last_volume > last_avg_volume * 1.25:
            score += 4.0 if trend == "bullish" else -2.0 if trend == "bearish" else 1.0

        score = self.clamp(score)

        rs_20d = None
        if stock_return_20d_pct is not None and np.isfinite(float(stock_return_20d_pct)):
            rs_20d = round(float(stock_return_20d_pct) - index_return_20d, 2)

        context["market_index_trend"] = trend
        context["market_index_score"] = score

        details: dict[str, object] = {
            "model_version": "market-index-v2.5",
            "index_name": index_name,
            "trend": trend,
            "index_close": round(last_close, 2),
            "index_return_20d_pct": round(index_return_20d, 2),
            "annualized_volatility_pct": round(last_vol, 2),
            "bullish_checks": bull,
            "bearish_checks": bear,
            "volume_ratio": round(volume_ratio, 2),
        }
        if rs_20d is not None:
            details["relative_strength_20d_pct"] = rs_20d

        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(95.0, 55.0 + abs(score - 50.0)),
            details=details,
            reasons=[f"Market index trend: {trend} ({index_name})"],
        )

```

---

### File: `sahmi_kasban\engines\multi_timeframe.py`

```py
from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class MultiTimeframeEngine(AnalysisEngine):
    name = "multi_timeframe"

    @staticmethod
    def _trend_score(close: pd.Series) -> tuple[str, float]:
        if len(close) < 8:
            return "insufficient", 50.0
        fast_window = min(5, max(2, len(close) // 4))
        slow_window = min(20, max(fast_window + 1, len(close) // 2))
        fast = safe_float(close.tail(fast_window).mean())
        slow = safe_float(close.tail(slow_window).mean())
        last = safe_float(close.iloc[-1])
        if last > fast > slow:
            return "bullish", 75.0
        if last < fast < slow:
            return "bearish", 25.0
        if last > slow:
            return "weak_bullish", 60.0
        if last < slow:
            return "weak_bearish", 40.0
        return "sideways", 50.0

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        daily_trend, daily_score = self._trend_score(candles["close"])

        if "timestamp" in candles.columns and candles["timestamp"].notna().all():
            indexed = candles.set_index("timestamp")
            weekly_close = indexed["close"].resample("W-FRI").last().dropna()
            monthly_close = indexed["close"].resample("ME").last().dropna()
        else:
            weekly_close = candles["close"].groupby(candles.index // 5).last()
            monthly_close = candles["close"].groupby(candles.index // 21).last()

        weekly_trend, weekly_score = self._trend_score(weekly_close)
        monthly_trend, monthly_score = self._trend_score(monthly_close)
        score = daily_score * 0.45 + weekly_score * 0.35 + monthly_score * 0.20

        bullish = sum(
            "bullish" in trend for trend in (daily_trend, weekly_trend, monthly_trend)
        )
        bearish = sum(
            "bearish" in trend for trend in (daily_trend, weekly_trend, monthly_trend)
        )
        aligned = bullish == 3 or bearish == 3
        if aligned:
            score += 5 if bullish == 3 else -5

        score = self.clamp(score)
        context["timeframe_alignment"] = (
            "bullish" if bullish >= 2 else "bearish" if bearish >= 2 else "mixed"
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=88.0 if aligned else 68.0,
            details={
                "daily": {"trend": daily_trend, "score": daily_score},
                "weekly": {"trend": weekly_trend, "score": weekly_score},
                "monthly": {"trend": monthly_trend, "score": monthly_score},
                "aligned": aligned,
                "alignment": context["timeframe_alignment"],
            },
            reasons=[f"Timeframe alignment: {context['timeframe_alignment']}"],
        )

```

---

### File: `sahmi_kasban\engines\opportunity_quality.py`

```py
from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult

ELITE_MIN_DIRECTIONAL_SCORE = 80.0
ELITE_MIN_CONFIDENCE = 70.0
BALANCED_MAX_RETURN_20D_PCT = 30.0
BALANCED_BASE_MAX_ATR_PCT = 4.5
BALANCED_BASE_MAX_TOTAL_RISK_PCT = 30.0
AGGRESSIVE_MIN_RETURN_20D_PCT = 5.0
AGGRESSIVE_MAX_RETURN_20D_PCT = 45.0
AGGRESSIVE_MAX_RETURN_5D_PCT = 15.0
AGGRESSIVE_MIN_BREAKOUT_PCT = 2.0
AGGRESSIVE_MAX_BREAKOUT_PCT = 12.0
AGGRESSIVE_MIN_VOLUME_RATIO = 2.0
AGGRESSIVE_MIN_TURNOVER_EGP = 5_000_000.0
ELITE_MAX_ZERO_VOLUME_RATIO = 0.10
AGGRESSIVE_MAX_ZERO_VOLUME_RATIO = 0.05


def _liquidity_tier(average_turnover_egp: float) -> str:
    if average_turnover_egp >= 20_000_000:
        return "high"
    if average_turnover_egp >= 5_000_000:
        return "medium"
    return "basic"


def _adaptive_limits(
    *,
    liquidity_tier: str,
    market_regime: str,
    balanced_base_atr: float = BALANCED_BASE_MAX_ATR_PCT,
    balanced_base_risk: float = BALANCED_BASE_MAX_TOTAL_RISK_PCT,
) -> dict[str, float]:
    balanced_atr = balanced_base_atr
    balanced_risk = balanced_base_risk
    aggressive_atr = 5.0
    aggressive_risk = 35.0

    if liquidity_tier == "medium":
        balanced_atr += 0.5
        balanced_risk += 2.5
        aggressive_atr = 5.5
        aggressive_risk = 40.0
    elif liquidity_tier == "high":
        balanced_atr += 1.0
        balanced_risk += 5.0
        aggressive_atr = 6.0
        aggressive_risk = 42.5

    if market_regime == "bearish":
        balanced_atr -= 0.5
        balanced_risk -= 2.5
        aggressive_atr -= 1.0
        aggressive_risk -= 5.0
    elif market_regime == "bullish":
        balanced_atr += 0.25

    return {
        "balanced_max_atr_pct": round(max(3.5, balanced_atr), 2),
        "balanced_max_total_risk_pct": round(max(25.0, balanced_risk), 2),
        "aggressive_max_atr_pct": round(max(5.0, aggressive_atr), 2),
        "aggressive_max_total_risk_pct": round(max(35.0, aggressive_risk), 2),
    }


def _weighted_score(checks: Mapping[str, bool], weights: Mapping[str, float]) -> float:
    return sum(weights[name] for name, passed in checks.items() if passed)


class OpportunityQualityEngine(AnalysisEngine):
    """Classify high-ranked BUY setups into balanced or aggressive elite profiles.

    Core v2.4 adaptively limits risk and atr while securing breakout momentum.
    """

    name = "opportunity_quality"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest.get("close"))
        return_20d_pct = safe_float(latest.get("return_20d")) * 100.0
        return_5d_pct = 0.0
        if len(candles) >= 6:
            close_5d = safe_float(candles.iloc[-6].get("close"))
            if close_5d > 0:
                return_5d_pct = (close / close_5d - 1.0) * 100.0

        prior = candles.iloc[-21:-1] if len(candles) >= 21 else candles.iloc[:-1]
        prior_high = safe_float(prior["high"].max()) if not prior.empty else close
        breakout_pct = (close / prior_high - 1.0) * 100.0 if prior_high > 0 else 0.0
        volume = safe_float(latest.get("volume"))
        average_volume = safe_float(latest.get("avg_volume_20"), volume)
        volume_ratio = volume / average_volume if average_volume > 0 else 0.0
        rsi = safe_float(latest.get("rsi"), 50.0)

        signal = str(context.get("signal", "WATCH")).upper()
        qualified = bool(context.get("qualified", False))
        final_score = safe_float(context.get("final_score"))
        confidence = safe_float(context.get("aggregate_confidence"))
        atr_pct = safe_float(context.get("atr_pct"))
        total_risk_pct = safe_float(context.get("total_risk_pct"))
        zero_volume_ratio = safe_float(context.get("zero_volume_ratio"))
        average_turnover_egp = safe_float(context.get("average_turnover_egp"))
        market_regime = str(context.get("market_regime", ""))
        market_regime_profile = str(context.get("market_regime_profile", market_regime))
        timeframe_alignment = str(context.get("timeframe_alignment", ""))
        risk_level = str(context.get("risk_level", ""))
        bullish_count = int(safe_float(context.get("bullish_engine_count")))
        bearish_count = int(safe_float(context.get("bearish_engine_count")))
        directional_conflict = bool(context.get("directional_conflict", False))

        cfg = self.config
        elite_min_dir_score = getattr(cfg, "elite_min_directional_score", ELITE_MIN_DIRECTIONAL_SCORE)
        elite_min_conf = getattr(cfg, "elite_min_confidence", ELITE_MIN_CONFIDENCE)
        balanced_max_ret_20d = getattr(cfg, "balanced_max_return_20d_pct", BALANCED_MAX_RETURN_20D_PCT)
        balanced_base_atr = getattr(cfg, "balanced_base_max_atr_pct", BALANCED_BASE_MAX_ATR_PCT)
        balanced_base_risk = getattr(cfg, "balanced_base_max_total_risk_pct", BALANCED_BASE_MAX_TOTAL_RISK_PCT)
        aggressive_min_ret_20d = getattr(cfg, "aggressive_min_return_20d_pct", AGGRESSIVE_MIN_RETURN_20D_PCT)
        aggressive_max_ret_20d = getattr(cfg, "aggressive_max_return_20d_pct", AGGRESSIVE_MAX_RETURN_20D_PCT)
        aggressive_max_ret_5d = getattr(cfg, "aggressive_max_return_5d_pct", AGGRESSIVE_MAX_RETURN_5D_PCT)
        aggressive_min_breakout = getattr(cfg, "aggressive_min_breakout_pct", AGGRESSIVE_MIN_BREAKOUT_PCT)
        aggressive_max_breakout = getattr(cfg, "aggressive_max_breakout_pct", AGGRESSIVE_MAX_BREAKOUT_PCT)
        aggressive_min_vol_ratio = getattr(cfg, "aggressive_min_volume_ratio", AGGRESSIVE_MIN_VOLUME_RATIO)
        aggressive_min_turnover = getattr(cfg, "aggressive_min_turnover_egp", AGGRESSIVE_MIN_TURNOVER_EGP)
        elite_max_zero_vol = getattr(cfg, "elite_max_zero_volume_ratio", ELITE_MAX_ZERO_VOLUME_RATIO)
        aggressive_max_zero_vol = getattr(cfg, "aggressive_max_zero_volume_ratio", AGGRESSIVE_MAX_ZERO_VOLUME_RATIO)

        liquidity_tier = _liquidity_tier(average_turnover_egp)
        limits = _adaptive_limits(
            liquidity_tier=liquidity_tier,
            market_regime=market_regime,
            balanced_base_atr=balanced_base_atr,
            balanced_base_risk=balanced_base_risk,
        )
        common_checks: dict[str, bool] = {
            "buy_signal": signal == "BUY",
            "qualified": qualified,
            "directional_score": final_score >= elite_min_dir_score,
            "aggregate_confidence": confidence >= elite_min_conf,
            "directional_consensus": (
                bullish_count >= 4 and bearish_count == 0 and not directional_conflict
            ),
            "bullish_market_regime": market_regime == "bullish",
            "bullish_timeframe_alignment": timeframe_alignment == "bullish",
        }
        balanced_checks = {
            **common_checks,
            "momentum_not_overextended": return_20d_pct <= balanced_max_ret_20d,
            "atr_controlled": 0 < atr_pct <= limits["balanced_max_atr_pct"],
            "risk_controlled": (
                risk_level != "high"
                and total_risk_pct <= limits["balanced_max_total_risk_pct"]
            ),
            "trading_continuity": zero_volume_ratio <= elite_max_zero_vol,
        }
        aggressive_checks = {
            **common_checks,
            "liquidity_supports_aggressive_profile": (
                average_turnover_egp >= aggressive_min_turnover
            ),
            "breakout_confirmed": (
                aggressive_min_breakout
                <= breakout_pct
                <= aggressive_max_breakout
            ),
            "volume_confirmation": volume_ratio >= aggressive_min_vol_ratio,
            "momentum_window": (
                aggressive_min_ret_20d
                <= return_20d_pct
                <= aggressive_max_ret_20d
                and 0 < return_5d_pct <= aggressive_max_ret_5d
                and return_20d_pct >= 1.3 * return_5d_pct
            ),
            "rsi_not_exhausted": 50 <= rsi <= 82,
            "atr_in_aggressive_band": 0 < atr_pct <= limits["aggressive_max_atr_pct"],
            "risk_within_aggressive_budget": (
                risk_level != "high"
                and total_risk_pct <= limits["aggressive_max_total_risk_pct"]
            ),
            "aggressive_trading_continuity": (
                zero_volume_ratio <= aggressive_max_zero_vol
            ),
        }
        balanced_weights: Mapping[str, float] = {
            "buy_signal": 8.0,
            "qualified": 8.0,
            "directional_score": 14.0,
            "aggregate_confidence": 10.0,
            "directional_consensus": 12.0,
            "bullish_market_regime": 8.0,
            "bullish_timeframe_alignment": 8.0,
            "momentum_not_overextended": 14.0,
            "atr_controlled": 10.0,
            "risk_controlled": 6.0,
            "trading_continuity": 2.0,
        }
        aggressive_weights: Mapping[str, float] = {
            "buy_signal": 6.0,
            "qualified": 6.0,
            "directional_score": 10.0,
            "aggregate_confidence": 8.0,
            "directional_consensus": 10.0,
            "bullish_market_regime": 8.0,
            "bullish_timeframe_alignment": 8.0,
            "liquidity_supports_aggressive_profile": 8.0,
            "breakout_confirmed": 10.0,
            "volume_confirmation": 8.0,
            "momentum_window": 6.0,
            "rsi_not_exhausted": 4.0,
            "atr_in_aggressive_band": 4.0,
            "risk_within_aggressive_budget": 2.0,
            "aggressive_trading_continuity": 2.0,
        }

        balanced_failed = [name for name, passed in balanced_checks.items() if not passed]
        aggressive_failed = [name for name, passed in aggressive_checks.items() if not passed]
        balanced_ready = not balanced_failed
        aggressive_ready = not aggressive_failed
        selected_profile = (
            "balanced" if balanced_ready else "aggressive" if aggressive_ready else "none"
        )
        balanced_score = _weighted_score(balanced_checks, balanced_weights)
        aggressive_score = _weighted_score(aggressive_checks, aggressive_weights)
        readiness_score = max(balanced_score, aggressive_score)
        engine_ready = selected_profile != "none"
        selected_failed = (
            []
            if engine_ready
            else balanced_failed
        )

        return EngineResult(
            name=self.name,
            score=readiness_score,
            confidence=92.0 if engine_ready else 76.0,
            status="complete" if engine_ready else "rejected",
            details={
                "model_version": "elite-quality-v2.4-regime-adaptive",
                "engine_ready": engine_ready,
                "selected_profile": selected_profile,
                "balanced_ready": balanced_ready,
                "aggressive_ready": aggressive_ready,
                "readiness_score": round(readiness_score, 2),
                "balanced_readiness_score": round(balanced_score, 2),
                "aggressive_readiness_score": round(aggressive_score, 2),
                "recommended_position_multiplier": (
                    0.5 if selected_profile == "aggressive" else 1.0
                ),
                "checks": (
                    balanced_checks if selected_profile != "aggressive" else aggressive_checks
                ),
                "failed_checks": selected_failed,
                "balanced_checks": balanced_checks,
                "balanced_failed_checks": balanced_failed,
                "aggressive_checks": aggressive_checks,
                "aggressive_failed_checks": aggressive_failed,
                "adaptive_limits": limits,
                "thresholds": {
                    "min_directional_score": ELITE_MIN_DIRECTIONAL_SCORE,
                    "min_confidence": ELITE_MIN_CONFIDENCE,
                    "balanced_max_return_20d_pct": BALANCED_MAX_RETURN_20D_PCT,
                    "aggressive_return_20d_pct": [
                        AGGRESSIVE_MIN_RETURN_20D_PCT,
                        AGGRESSIVE_MAX_RETURN_20D_PCT,
                    ],
                    "aggressive_max_return_5d_pct": AGGRESSIVE_MAX_RETURN_5D_PCT,
                    "aggressive_breakout_pct": [
                        AGGRESSIVE_MIN_BREAKOUT_PCT,
                        AGGRESSIVE_MAX_BREAKOUT_PCT,
                    ],
                    "aggressive_min_volume_ratio": AGGRESSIVE_MIN_VOLUME_RATIO,
                    "aggressive_min_turnover_egp": AGGRESSIVE_MIN_TURNOVER_EGP,
                    "balanced_max_zero_volume_ratio": ELITE_MAX_ZERO_VOLUME_RATIO,
                    "aggressive_max_zero_volume_ratio": AGGRESSIVE_MAX_ZERO_VOLUME_RATIO,
                },
                "metrics": {
                    "final_score": round(final_score, 2),
                    "aggregate_confidence": round(confidence, 2),
                    "return_20d_pct": round(return_20d_pct, 2),
                    "return_5d_pct": round(return_5d_pct, 2),
                    "breakout_pct": round(breakout_pct, 2),
                    "volume_ratio": round(volume_ratio, 2),
                    "rsi": round(rsi, 2),
                    "atr_pct": round(atr_pct, 2),
                    "total_risk_pct": round(total_risk_pct, 2),
                    "average_turnover_egp": round(average_turnover_egp, 2),
                    "liquidity_tier": liquidity_tier,
                    "zero_volume_ratio": round(zero_volume_ratio, 3),
                    "market_regime": market_regime,
                    "market_regime_profile": market_regime_profile,
                    "timeframe_alignment": timeframe_alignment,
                    "risk_level": risk_level,
                    "bullish_engine_count": bullish_count,
                    "bearish_engine_count": bearish_count,
                },
            },
            reasons=(
                [f"Elite {selected_profile} quality gates passed"]
                if engine_ready
                else [f"Balanced elite gate failed: {name}" for name in balanced_failed]
                + [f"Aggressive elite gate failed: {name}" for name in aggressive_failed]
            ),
        )

```

---

### File: `sahmi_kasban\engines\quantitative.py`

```py
from __future__ import annotations

import math

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class QuantitativeEngine(AnalysisEngine):
    name = "quantitative"

    @staticmethod
    def _logistic(value: float) -> float:
        value = max(-20.0, min(20.0, value))
        return 1.0 / (1.0 + math.exp(-value))

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        returns = candles["close"].pct_change().dropna()
        last = candles.iloc[-1]
        momentum_5 = safe_float(candles["close"].pct_change(5).iloc[-1])
        momentum_20 = safe_float(candles["close"].pct_change(20).iloc[-1])
        momentum_60 = safe_float(candles["close"].pct_change(60).iloc[-1])
        volatility = safe_float(returns.tail(20).std())
        downside = returns.tail(60)[returns.tail(60) < 0]
        downside_volatility = safe_float(downside.std(), volatility)

        volume_window = candles["volume"].tail(60)
        volume_std = safe_float(volume_window.std())
        volume_z = (
            (safe_float(last["volume"]) - safe_float(volume_window.mean())) / volume_std
            if volume_std > 0
            else 0.0
        )

        trend_factor = momentum_5 * 2.0 + momentum_20 * 3.0 + momentum_60 * 1.5
        risk_penalty = volatility * 4.0 + downside_volatility * 2.0
        volume_factor = max(-2.0, min(2.0, volume_z)) * 0.08
        raw_edge_before_extension = trend_factor - risk_penalty + volume_factor

        # Linear momentum rewards can mistake a late parabolic move for a safer
        # opportunity. Apply a nonlinear penalty only after the move exceeds the
        # replay-supported extension bands; normal positive momentum is preserved.
        overextension_penalty = (
            max(0.0, momentum_20 - 0.30) * 2.0
            + max(0.0, momentum_5 - 0.15) * 1.5
        )
        raw_edge = raw_edge_before_extension - overextension_penalty
        bullish_probability = self._logistic(raw_edge)
        score = bullish_probability * 100.0

        sample_quality = min(1.0, len(returns) / 252.0)
        edge_strength = min(1.0, abs(bullish_probability - 0.5) * 2.0)
        confidence = min(90.0, 50.0 + sample_quality * 25.0 + edge_strength * 15.0)

        context["bullish_probability"] = bullish_probability
        context["quantitative_overextension_penalty"] = overextension_penalty
        return EngineResult(
            name=self.name,
            score=score,
            confidence=confidence,
            details={
                "model_version": "momentum-logit-v4-overextension-aware",
                "sample_size": len(returns),
                "sample_quality_pct": round(sample_quality * 100, 2),
                "momentum_5d_pct": round(momentum_5 * 100, 2),
                "momentum_20d_pct": round(momentum_20 * 100, 2),
                "momentum_60d_pct": round(momentum_60 * 100, 2),
                "volatility_20d_pct": round(volatility * 100, 2),
                "downside_volatility_pct": round(downside_volatility * 100, 2),
                "volume_z_score": round(volume_z, 2),
                "raw_edge_before_extension": round(raw_edge_before_extension, 6),
                "overextension_penalty": round(overextension_penalty, 6),
                "raw_edge": round(raw_edge, 6),
                "bullish_probability_pct": round(bullish_probability * 100, 2),
            },
            reasons=[
                f"Model bullish probability: {bullish_probability * 100:.1f}%",
                f"Overextension penalty: {overextension_penalty:.3f}",
            ],
        )

```

---

### File: `sahmi_kasban\engines\risk.py`

```py
from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult, TradePlan

SHORT_HORIZON_SESSIONS = 5


class RiskEngine(AnalysisEngine):
    name = "risk"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        price = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"), price * 0.02)
        volatility = safe_float(latest.get("volatility_20d"))
        average_volume = safe_float(latest.get("avg_volume_20"))
        volume = safe_float(latest.get("volume"))
        volume_ratio = volume / average_volume if average_volume > 0 else 0.0
        atr_pct = atr_value / price * 100.0 if price > 0 else 100.0

        prior = candles.iloc[-21:-1] if len(candles) >= 21 else candles.iloc[:-1]
        prior_high = safe_float(prior["high"].max()) if not prior.empty else price
        breakout_pct = (price / prior_high - 1.0) * 100.0 if prior_high > 0 else 0.0
        aggressive_breakout = (
            0.5 <= breakout_pct <= 12.0
            and volume_ratio >= 1.5
            and atr_pct >= 3.0
        )

        entry = price
        stop_loss = max(0.01, entry - atr_value * self.config.stop_atr_multiple)
        risk_per_share = max(entry - stop_loss, entry * 0.005)
        risk_amount = self.config.capital * self.config.risk_per_trade
        by_risk = int(risk_amount / risk_per_share)
        by_value = int(self.config.max_position_value / entry) if entry > 0 else 0
        position_size = max(0, min(by_risk, by_value))
        position_value = position_size * entry

        target_1_r = self.config.target_1_r
        target_2_r = self.config.target_2_r
        plan_style = "balanced_5_session"
        if aggressive_breakout:
            target_1_r = max(target_1_r, 1.25)
            target_2_r = max(target_2_r, 2.0)
            plan_style = "aggressive_breakout_5_session"
        target_1 = entry + risk_per_share * target_1_r
        target_2 = entry + risk_per_share * target_2_r

        liquidity_risk = 35.0 if volume_ratio < 0.7 else 20.0 if volume_ratio < 1.0 else 10.0
        volatility_risk = min(60.0, volatility * 1000.0)
        atr_risk = min(40.0, atr_pct * 5.0)
        total_risk = min(
            100.0,
            volatility_risk * 0.45 + atr_risk * 0.35 + liquidity_risk * 0.20,
        )
        score = 100.0 - total_risk

        plan = TradePlan(
            entry=round(entry, 4),
            stop_loss=round(stop_loss, 4),
            target_1=round(target_1, 4),
            target_2=round(target_2, 4),
            risk_per_share=round(risk_per_share, 4),
            reward_risk_1=round(target_1_r, 2),
            reward_risk_2=round(target_2_r, 2),
            position_size=position_size,
            position_value=round(position_value, 2),
            risk_amount=round(min(position_size * risk_per_share, risk_amount), 2),
        )
        context["trade_plan"] = plan
        context["trade_plan_style"] = plan_style
        context["risk_level"] = (
            "low" if total_risk < 35 else "medium" if total_risk < 60 else "high"
        )

        warnings: list[str] = []
        if position_size <= 0:
            warnings.append("Position size is zero under current risk limits")
        if atr_pct > self.config.atr_max_pct:
            warnings.append("ATR exceeds configured maximum")
        return EngineResult(
            name=self.name,
            score=score,
            confidence=88.0,
            details={
                "model_version": "risk-plan-v2.3-atr-5-session",
                "risk_level": context["risk_level"],
                "total_risk_pct": round(total_risk, 2),
                "atr_pct": round(atr_pct, 2),
                "volume_ratio": round(volume_ratio, 2),
                "breakout_pct": round(breakout_pct, 2),
                "plan_style": plan_style,
                "horizon_sessions": SHORT_HORIZON_SESSIONS,
                "target_model": "atr_reward_targets_for_5_sessions",
                "recommended_position_multiplier": (
                    0.5 if aggressive_breakout else 1.0
                ),
                "trade_plan": plan.to_dict(),
            },
            reasons=warnings,
        )

```

---

### File: `sahmi_kasban\engines\scenario.py`

```py
from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult, TradePlan


class ScenarioEngine(AnalysisEngine):
    name = "scenario"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"), close * 0.02)
        technical_score = safe_float(context.get("technical_score"), 50.0)
        smc_score = safe_float(context.get("smc_score"), 50.0)
        quantitative_score = safe_float(context.get("quantitative_score"), 50.0)
        combined = technical_score * 0.4 + smc_score * 0.3 + quantitative_score * 0.3

        bullish_probability = self.clamp(combined)
        bearish_probability = self.clamp(100.0 - combined)
        base_probability = max(10.0, 100.0 - abs(combined - 50.0) * 1.6)
        total = bullish_probability + bearish_probability + base_probability
        bullish_probability = bullish_probability / total * 100.0
        bearish_probability = bearish_probability / total * 100.0
        base_probability = base_probability / total * 100.0

        plan = context.get("trade_plan")
        if isinstance(plan, TradePlan):
            bullish_target = plan.target_2
            base_target = plan.target_1
            bearish_target = plan.stop_loss
        else:
            bullish_target = close + atr_value * 3.5
            base_target = close + atr_value * 2.0
            bearish_target = max(0.01, close - atr_value * 2.0)

        score = self.clamp(bullish_probability + base_probability * 0.5)
        return EngineResult(
            name=self.name,
            score=score,
            confidence=75.0,
            details={
                "bullish": {
                    "probability_pct": round(bullish_probability, 2),
                    "target": round(bullish_target, 4),
                },
                "base": {
                    "probability_pct": round(base_probability, 2),
                    "target": round(base_target, 4),
                },
                "bearish": {
                    "probability_pct": round(bearish_probability, 2),
                    "target": round(bearish_target, 4),
                },
            },
            reasons=["Scenario probabilities are model estimates, not guarantees"],
        )

```

---

### File: `sahmi_kasban\engines\smc.py`

```py
from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class SMCEngine(AnalysisEngine):
    name = "smc"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        recent = candles.tail(min(60, len(candles))).copy()
        latest = recent.iloc[-1]
        close = safe_float(latest["close"])

        previous_20 = recent.iloc[-21:-1] if len(recent) >= 21 else recent.iloc[:-1]
        previous_10 = recent.iloc[-11:-1] if len(recent) >= 11 else recent.iloc[:-1]
        high_20 = safe_float(previous_20["high"].max(), close)
        low_20 = safe_float(previous_20["low"].min(), close)
        high_10 = safe_float(previous_10["high"].max(), close)
        low_10 = safe_float(previous_10["low"].min(), close)

        bullish_bos = close > high_20 if not previous_20.empty else False
        bearish_bos = close < low_20 if not previous_20.empty else False

        prior_trend_up = False
        if len(recent) >= 25:
            earlier = recent.iloc[-25:-10]
            later = recent.iloc[-10:]
            prior_trend_up = later["close"].mean() > earlier["close"].mean()
        choch = (prior_trend_up and bearish_bos) or (not prior_trend_up and bullish_bos)

        latest_low = safe_float(latest["low"])
        latest_high = safe_float(latest["high"])
        liquidity_sweep_low = latest_low < low_10 and close > low_10
        liquidity_sweep_high = latest_high > high_10 and close < high_10

        fvg_bullish = False
        fvg_bearish = False
        if len(recent) >= 3:
            first = recent.iloc[-3]
            third = recent.iloc[-1]
            fvg_bullish = safe_float(third["low"]) > safe_float(first["high"])
            fvg_bearish = safe_float(third["high"]) < safe_float(first["low"])

        range_size = max(high_20 - low_20, 1e-9)
        range_position = (close - low_20) / range_size
        zone = (
            "discount"
            if range_position <= 0.45
            else "premium"
            if range_position >= 0.55
            else "equilibrium"
        )

        body = (recent["close"] - recent["open"]).abs()
        body_median = safe_float(body.tail(20).median())
        volume_avg = safe_float(recent["volume"].tail(20).mean())
        displacement_mult = getattr(self.config, "smc_ob_displacement_multiplier", 1.5)
        volume_mult = getattr(self.config, "smc_ob_volume_multiplier", 1.0)

        bullish_order_blocks: list[dict[str, float]] = []
        bearish_order_blocks: list[dict[str, float]] = []
        for index in range(max(1, len(recent) - 12), len(recent) - 1):
            candle = recent.iloc[index]
            next_candle = recent.iloc[index + 1]
            candle_close = safe_float(candle["close"])
            candle_open = safe_float(candle["open"])
            candle_high = safe_float(candle["high"])
            candle_low = safe_float(candle["low"])
            candle_body = abs(candle_close - candle_open)

            next_close = safe_float(next_candle["close"])
            next_open = safe_float(next_candle["open"])
            next_volume = safe_float(next_candle["volume"])
            next_avg_vol = safe_float(next_candle.get("avg_volume_20"), volume_avg)
            displacement = abs(next_close - next_open)

            volume_confirmed = next_volume >= next_avg_vol * volume_mult

            if candle_body <= body_median and displacement >= body_median * displacement_mult and volume_confirmed:
                block = {
                    "low": round(candle_low, 4),
                    "high": round(candle_high, 4),
                }
                # Bullish OB: previous candle red, next candle green, next closes ABOVE previous high (Breakout)
                if (
                    candle_close < candle_open
                    and next_close > next_open
                    and next_close > candle_high
                ):
                    bullish_order_blocks.append(block)
                # Bearish OB: previous candle green, next candle red, next closes BELOW previous low (Breakout)
                elif (
                    candle_close > candle_open
                    and next_close < next_open
                    and next_close < candle_low
                ):
                    bearish_order_blocks.append(block)

        score = 50.0
        reasons: list[str] = []
        if bullish_bos:
            score += 18
            reasons.append("Bullish break of structure")
        if bearish_bos:
            score -= 18
            reasons.append("Bearish break of structure")
        if liquidity_sweep_low:
            score += 12
            reasons.append("Sell-side liquidity sweep")
        if liquidity_sweep_high:
            score -= 10
            reasons.append("Buy-side liquidity sweep")
        if fvg_bullish:
            score += 7
            reasons.append("Bullish fair value gap")
        if fvg_bearish:
            score -= 7
            reasons.append("Bearish fair value gap")
        if zone == "discount":
            score += 8
            reasons.append("Price in discount zone")
        elif zone == "premium":
            score -= 5
        if bullish_order_blocks:
            score += min(8, len(bullish_order_blocks) * 3)
        if bearish_order_blocks:
            score -= min(8, len(bearish_order_blocks) * 3)

        score = self.clamp(score)
        context["smc_bias"] = (
            "bullish" if score >= 60 else "bearish" if score <= 40 else "neutral"
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(92.0, 55.0 + len(reasons) * 6),
            details={
                "bullish_bos": bullish_bos,
                "bearish_bos": bearish_bos,
                "choch": choch,
                "liquidity_sweep_low": liquidity_sweep_low,
                "liquidity_sweep_high": liquidity_sweep_high,
                "fvg_bullish": fvg_bullish,
                "fvg_bearish": fvg_bearish,
                "range_position": round(range_position, 3),
                "zone": zone,
                "bullish_order_blocks": bullish_order_blocks[-3:],
                "bearish_order_blocks": bearish_order_blocks[-3:],
            },
            reasons=reasons,
        )

```

---

### File: `sahmi_kasban\engines\technical.py`

```py
from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


class TechnicalEngine(AnalysisEngine):
    name = "technical"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        close = safe_float(latest["close"])
        sma_20 = safe_float(latest.get("sma_20"), close)
        sma_50 = safe_float(latest.get("sma_50"), close)
        sma_200 = safe_float(latest.get("sma_200"), sma_50)
        rsi = safe_float(latest.get("rsi"), 50.0)
        macd = safe_float(latest.get("macd"))
        macd_signal = safe_float(latest.get("macd_signal"))
        volume = safe_float(latest.get("volume"))
        avg_volume = safe_float(latest.get("avg_volume_20"), volume)
        return_20d = safe_float(latest.get("return_20d")) * 100

        score = 50.0
        reasons: list[str] = []

        if close > sma_20:
            score += 7
            reasons.append("Price above SMA20")
        else:
            score -= 7
        if close > sma_50:
            score += 9
            reasons.append("Price above SMA50")
        else:
            score -= 9
        if sma_20 > sma_50:
            score += 8
            reasons.append("SMA20 above SMA50")
        else:
            score -= 5
        if sma_50 > sma_200 and sma_200 > 0:
            score += 9
            reasons.append("Long-term trend positive")
        elif sma_200 > 0:
            score -= 8

        vwap_20 = safe_float(latest.get("vwap_20"), close)
        if close > vwap_20:
            score += 6
            reasons.append("Price trading above 20-day VWAP (Institutional support)")
        elif close < vwap_20 * 0.95:
            score -= 6
            reasons.append("Price significantly below VWAP (Institutional distribution)")

        if 45 <= rsi <= 65:
            score += 10
            reasons.append("RSI in constructive range")
        elif 30 <= rsi < 45:
            score += 4
        elif rsi > 75:
            score -= 18
            reasons.append("RSI overbought and extension risk elevated")
        elif rsi < 25:
            score -= 5

        if macd > macd_signal:
            score += 10
            reasons.append("MACD bullish")
        else:
            score -= 7

        volume_ratio = volume / avg_volume if avg_volume > 0 else 0
        if volume_ratio >= 1.5:
            score += 8 if return_20d >= 0 else -5
            reasons.append("Volume expansion")

        # Core v2.1 rewarded every move above 8% equally. The historical replay
        # windows showed that extreme 20-day momentum often represented late
        # entry and larger drawdown rather than additional directional quality.
        if 8 < return_20d <= 20:
            score += 6
            reasons.append("Constructive 20-day momentum")
        elif 20 < return_20d <= 30:
            reasons.append("20-day momentum is stretched")
        elif return_20d > 30:
            score -= 10
            reasons.append("20-day move is overextended")
        elif return_20d < -8:
            score -= 8

        score = self.clamp(score)
        trend = "uptrend" if score >= 65 else "downtrend" if score <= 40 else "sideways"
        context["technical_trend"] = trend
        context["rsi"] = rsi
        context["return_20d_pct"] = return_20d
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(96.0, 60.0 + abs(score - 50.0) * 0.7),
            details={
                "model_version": "technical-v2.3-vwap-aware",
                "trend": trend,
                "close": round(close, 4),
                "sma_20": round(sma_20, 4),
                "sma_50": round(sma_50, 4),
                "sma_200": round(sma_200, 4),
                "vwap_20": round(vwap_20, 4),
                "rsi": round(rsi, 2),
                "macd": round(macd, 4),
                "macd_signal": round(macd_signal, 4),
                "volume_ratio": round(volume_ratio, 2),
                "return_20d_pct": round(return_20d, 2),
                "overextended": return_20d > 30 or rsi > 75,
            },
            reasons=reasons,
        )

```

---

### File: `sahmi_kasban.egg-info\PKG-INFO`

```
Metadata-Version: 2.4
Name: sahmi-kasban
Version: 0.1.0
Summary: Modular analysis engines for Egyptian Exchange equities
Requires-Python: >=3.11
Description-Content-Type: text/markdown
Requires-Dist: httpx>=0.27
Requires-Dist: numpy>=1.26
Requires-Dist: pandas>=2.1
Provides-Extra: dev
Requires-Dist: pytest>=8.0; extra == "dev"
Requires-Dist: ruff>=0.5; extra == "dev"

# Sahmi Kasban — Core Engines

نواة مستقلة لمحركات تحليل أسهم البورصة المصرية، منقولة ومُعاد تنظيمها من مشروع EGX-Pilot بدون الواجهة، المستخدمين، قاعدة البيانات أو جدولة السيرفر.

## خارطة طريق المنتج

تم اعتماد خطة المنتج الكاملة لتطبيق Flutter والـBackend والاشتراكات والمناقشات ونظام التوقعات في ملف [ROADMAP.md](ROADMAP.md).

## سجل التنفيذ

يتم تسجيل كل أعمال التطوير والقرارات والاختبارات في ملف [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md).

## الـBackend

بدأ تنفيذ Backend مستقل باستخدام FastAPI وPostgreSQL وAlembic داخل مجلد [backend](backend/README.md). يمكن تشغيل بيئة التطوير كاملة باستخدام `docker compose up --build`.

## المحركات الموجودة

- **Market Environment**: تحديد حالة السوق صاعد/هابط/عرضي ومستوى المخاطرة.
- **Stock Qualification**: فلترة السيولة، التاريخ السعري، ATR والانحرافات السعرية.
- **Technical Analysis**: الاتجاه، المتوسطات، RSI، MACD، ATR والحجم.
- **Smart Money Concepts (SMC)**: BOS، CHOCH، liquidity sweep، FVG ومناطق premium/discount.
- **Multi-Timeframe**: توافق الاتجاه على اليومي والأسبوعي والشهري.
- **Quantitative**: الزخم، التذبذب، volume z-score واحتمال الصعود.
- **Risk & Position Sizing**: نقطة الدخول، وقف الخسارة، الأهداف وحجم المركز وفق نسبة مخاطرة محددة.
- **Scenario Engine**: سيناريو صاعد وأساسي وهابط.
- **Final Scoring**: دمج المحركات بأوزان واضحة وإصدار BUY / WATCH / AVOID.

## تكامل الذكاء الاصطناعي

تم نقل تكامل Groq وOpen-WebUI من المشروع القديم إلى حزمة مستقلة. يدعم التكامل:

- استخدام Open-WebUI كمزود أساسي عند ضبط عنوانه.
- الرجوع إلى Groq وتدوير أكثر من مفتاح عند فشل المزود الأساسي.
- شرح نتائج تحليل السهم باستخدام بيانات المحركات فقط.
- مراجعة مناقشات المستخدمين قبل النشر.
- استخراج توقع قابل للقياس من نص المناقشة.
- تقييم التوقع بعد انتهاء الجلسة مع تثبيت المكافأة من السيرفر.

متغيرات التشغيل:

```text
OPEN_WEBUI_URL
OPEN_WEBUI_API_KEY
GROQ_API_KEYS
AI_MODEL
AI_TIMEOUT_SECONDS
AI_MAX_TOKENS
AI_TEMPERATURE
```

يجب حفظ المفاتيح في Secrets أو متغيرات البيئة وعدم وضعها داخل الكود أو تطبيق Flutter.

## مثال سريع

```python
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer

analyzer = SahmiKasbanAnalyzer(AnalysisConfig(capital=150_000, risk_per_trade=0.01))
report = analyzer.analyze("COMI", candles)
print(report.signal, report.final_score)
```

استخدام خدمة الذكاء الاصطناعي:

```python
from sahmi_kasban.ai import SahmiAIService

ai = SahmiAIService()
result = await ai.moderate_discussion("أتوقع صعود سهم معين خلال الجلسة القادمة")
print(result)
```

`candles` قائمة من السجلات وتحتوي على الأقل على:

```text
timestamp, open, high, low, close, volume
```

## ملاحظات

هذه المحركات أدوات تحليل ودعم قرار وليست ضمانًا للربح أو توصية مالية. يجب اختبار أي استراتيجية تاريخيًا وورقيًا قبل استخدامها بأموال حقيقية.

```

---

### File: `sahmi_kasban.egg-info\SOURCES.txt`

```txt
README.md
pyproject.toml
src/sahmi_kasban/__init__.py
src/sahmi_kasban/backtesting.py
src/sahmi_kasban/indicators.py
src/sahmi_kasban/models.py
src/sahmi_kasban/orchestrator.py
src/sahmi_kasban/scoring.py
src/sahmi_kasban.egg-info/PKG-INFO
src/sahmi_kasban.egg-info/SOURCES.txt
src/sahmi_kasban.egg-info/dependency_links.txt
src/sahmi_kasban.egg-info/requires.txt
src/sahmi_kasban.egg-info/top_level.txt
src/sahmi_kasban/ai/__init__.py
src/sahmi_kasban/ai/client.py
src/sahmi_kasban/ai/prompts.py
src/sahmi_kasban/ai/service.py
src/sahmi_kasban/engines/__init__.py
src/sahmi_kasban/engines/base.py
src/sahmi_kasban/engines/market.py
src/sahmi_kasban/engines/multi_timeframe.py
src/sahmi_kasban/engines/opportunity_quality.py
src/sahmi_kasban/engines/quantitative.py
src/sahmi_kasban/engines/risk.py
src/sahmi_kasban/engines/scenario.py
src/sahmi_kasban/engines/smc.py
src/sahmi_kasban/engines/technical.py
tests/test_ai_service.py
tests/test_android_signing_contract.py
tests/test_core_v2.py
tests/test_core_v23.py
tests/test_engines.py
tests/test_production_android_release_platform.py
tests/test_production_deployment_contract.py
tests/test_replay_prepared_analysis.py
```

---

### File: `sahmi_kasban.egg-info\dependency_links.txt`

```txt


```

---

### File: `sahmi_kasban.egg-info\requires.txt`

```txt
httpx>=0.27
numpy>=1.26
pandas>=2.1

[dev]
pytest>=8.0
ruff>=0.5

```

---

### File: `sahmi_kasban.egg-info\top_level.txt`

```txt
sahmi_kasban

```

---


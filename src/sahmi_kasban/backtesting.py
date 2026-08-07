from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from statistics import median
from typing import Any, Protocol

import pandas as pd

from sahmi_kasban.indicators import prepare_candles
from sahmi_kasban.models import AnalysisReport


class AnalyzerProtocol(Protocol):
    def analyze(
        self,
        ticker: str,
        candles: pd.DataFrame | Iterable[Mapping[str, Any]],
        index: tuple[str, pd.DataFrame | Iterable[Mapping[str, Any]]] | None = None,
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
        history = prepared.iloc[:cutoff].copy()
        future = prepared.iloc[cutoff : cutoff + horizon_sessions]
        report_index = None
        if prepared_index is not None:
            cutoff_ts = history.iloc[-1]["timestamp"]
            index_slice = prepared_index.loc[
                prepared_index["timestamp"] <= cutoff_ts
            ]
            if len(index_slice) >= 60:
                report_index = (index_name, index_slice)
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

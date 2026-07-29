from __future__ import annotations

import csv
import io
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AnalysisReplayJob, AnalysisReplayRow, AnalysisReplayTicker


@dataclass(frozen=True, slots=True)
class ReplayExportMetric:
    evaluation_scope: str
    benchmark_return_bp: int | None
    excess_return_bp: int | None
    benchmark_correct: bool | None
    score_percentile: float | None


def _pct(value: int | None) -> float | None:
    return None if value is None else round(value / 100.0, 2)


def _evaluation_scope(row: AnalysisReplayRow) -> str:
    stored = (row.analysis_quality or {}).get("evaluation_scope")
    if stored in {"directional", "eligibility_exclusion", "not_evaluated"}:
        return str(stored)
    if row.status in {"skipped", "failed"} or row.signal is None:
        return "not_evaluated"
    if row.qualified is False:
        return "eligibility_exclusion"
    return "directional"


def _average_rank_percentiles(
    rows: Iterable[AnalysisReplayRow],
) -> dict[object, float]:
    scored = [row for row in rows if row.qualified is True and row.score_bp is not None]
    scored.sort(key=lambda row: (int(row.score_bp or 0), row.ticker))
    count = len(scored)
    if count == 0:
        return {}

    result: dict[object, float] = {}
    cursor = 0
    while cursor < count:
        end = cursor + 1
        score = scored[cursor].score_bp
        while end < count and scored[end].score_bp == score:
            end += 1
        average_rank = ((cursor + 1) + end) / 2.0
        percentile = round(average_rank / count * 100.0, 2)
        for row in scored[cursor:end]:
            result[row.id] = percentile
        cursor = end
    return result


def calculate_replay_export_metrics(
    rows: Iterable[AnalysisReplayRow],
    *,
    neutral_band_bp: int,
) -> dict[object, ReplayExportMetric]:
    materialized = list(rows)
    by_date: dict[object, list[AnalysisReplayRow]] = defaultdict(list)
    for row in materialized:
        by_date[row.analysis_date].append(row)

    metrics: dict[object, ReplayExportMetric] = {}
    for date_rows in by_date.values():
        evaluated = [
            row
            for row in date_rows
            if row.status == "evaluated" and row.forward_return_bp is not None
        ]
        benchmark_bp = (
            int(round(sum(int(row.forward_return_bp or 0) for row in evaluated) / len(evaluated)))
            if evaluated
            else None
        )
        percentiles = _average_rank_percentiles(date_rows)

        for row in date_rows:
            scope = _evaluation_scope(row)
            excess_bp = (
                int(row.forward_return_bp) - benchmark_bp
                if benchmark_bp is not None and row.forward_return_bp is not None
                else None
            )
            benchmark_correct: bool | None = None
            if scope == "directional" and row.status == "evaluated" and excess_bp is not None:
                if row.signal == "BUY":
                    benchmark_correct = excess_bp > neutral_band_bp
                elif row.signal == "AVOID":
                    benchmark_correct = excess_bp < -neutral_band_bp
                elif row.signal == "WATCH":
                    benchmark_correct = abs(excess_bp) <= neutral_band_bp
            metrics[row.id] = ReplayExportMetric(
                evaluation_scope=scope,
                benchmark_return_bp=benchmark_bp,
                excess_return_bp=excess_bp,
                benchmark_correct=benchmark_correct,
                score_percentile=percentiles.get(row.id),
            )
    return metrics


_EXPORT_FIELDS = [
    "record_type",
    "job_id",
    "engine_version",
    "ticker",
    "analysis_date",
    "status",
    "provider",
    "data_fingerprint",
    "data_as_of",
    "candle_count",
    "signal",
    "score",
    "score_percentile",
    "confidence",
    "qualified",
    "evaluation_scope",
    "entry",
    "evaluation_date",
    "exit",
    "forward_return_pct",
    "market_benchmark_return_pct",
    "excess_return_pct",
    "max_upside_pct",
    "max_drawdown_pct",
    "correct",
    "benchmark_correct",
    "engines_json",
    "trade_plan_json",
    "warnings_json",
    "analysis_quality_json",
    "error_code",
    "error_message",
]


def build_historical_replay_csv(
    db: Session,
    *,
    job: AnalysisReplayJob,
) -> bytes:
    rows = list(
        db.scalars(
            select(AnalysisReplayRow)
            .where(AnalysisReplayRow.job_id == job.id)
            .order_by(
                AnalysisReplayRow.analysis_date.asc(),
                AnalysisReplayRow.ticker.asc(),
            )
        ).all()
    )
    ticker_tasks = list(
        db.scalars(
            select(AnalysisReplayTicker)
            .where(AnalysisReplayTicker.job_id == job.id)
            .order_by(AnalysisReplayTicker.ticker.asc())
        ).all()
    )
    metrics = calculate_replay_export_metrics(
        rows,
        neutral_band_bp=job.neutral_band_bp,
    )

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=_EXPORT_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        metric = metrics[row.id]
        writer.writerow(
            {
                "record_type": "analysis_row",
                "job_id": str(job.id),
                "engine_version": row.engine_version,
                "ticker": row.ticker,
                "analysis_date": row.analysis_date.isoformat(),
                "status": row.status,
                "provider": row.provider or "",
                "data_fingerprint": row.data_fingerprint or "",
                "data_as_of": row.data_as_of.isoformat() if row.data_as_of else "",
                "candle_count": row.candle_count,
                "signal": row.signal or "",
                "score": _pct(row.score_bp),
                "score_percentile": metric.score_percentile or "",
                "confidence": _pct(row.confidence_bp),
                "qualified": row.qualified if row.qualified is not None else "",
                "evaluation_scope": metric.evaluation_scope,
                "entry": row.entry if row.entry is not None else "",
                "evaluation_date": row.evaluation_date.isoformat() if row.evaluation_date else "",
                "exit": row.exit if row.exit is not None else "",
                "forward_return_pct": _pct(row.forward_return_bp),
                "market_benchmark_return_pct": _pct(metric.benchmark_return_bp),
                "excess_return_pct": _pct(metric.excess_return_bp),
                "max_upside_pct": _pct(row.max_upside_bp),
                "max_drawdown_pct": _pct(row.max_drawdown_bp),
                "correct": row.correct if row.correct is not None else "",
                "benchmark_correct": (
                    metric.benchmark_correct
                    if metric.benchmark_correct is not None
                    else ""
                ),
                "engines_json": json.dumps(
                    row.engines,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "trade_plan_json": (
                    json.dumps(
                        row.trade_plan,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    if row.trade_plan
                    else ""
                ),
                "warnings_json": json.dumps(
                    row.warnings,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "analysis_quality_json": json.dumps(
                    row.analysis_quality,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "error_code": row.error_code or "",
                "error_message": row.error_message or "",
            }
        )

    for task in ticker_tasks:
        if task.status != "failed":
            continue
        writer.writerow(
            {
                "record_type": "ticker_failure",
                "job_id": str(job.id),
                "engine_version": job.engine_version,
                "ticker": task.ticker,
                "status": "ticker_failed",
                "provider": task.provider or "",
                "data_fingerprint": task.data_fingerprint or "",
                "candle_count": task.candle_count,
                "evaluation_scope": "not_evaluated",
                "error_code": task.error_code or "provider_failure",
                "error_message": task.error_message or "تعذر تحميل بيانات السهم",
            }
        )

    return ("\ufeff" + output.getvalue()).encode("utf-8")

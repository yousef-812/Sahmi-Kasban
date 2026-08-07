from __future__ import annotations

from datetime import date
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import AnalysisReplayJob, AnalysisReplayRow
from app.services.historical_replay_exports import _evaluation_scope, _pct, calculate_replay_export_metrics


def export_full_2025_md():
    db = SessionLocal()
    try:
        jobs = db.scalars(
            select(AnalysisReplayJob)
            .where(
                AnalysisReplayJob.start_date >= date(2025, 1, 1),
                AnalysisReplayJob.start_date <= date(2025, 12, 31),
                AnalysisReplayJob.evaluated_rows > 0,
            )
            .order_by(AnalysisReplayJob.start_date)
        ).all()

        md_lines = []
        md_lines.append("# تقرير نتائج اختبار المحرك التنافسي — عام 2025 بالكامل (Core v2.4 Full Replay)")
        md_lines.append("")

        total_all_rows = 0
        for job in jobs:
            rows = db.scalars(
                select(AnalysisReplayRow)
                .where(AnalysisReplayRow.job_id == job.id)
                .order_by(AnalysisReplayRow.analysis_date, AnalysisReplayRow.ticker)
            ).all()

            metrics = calculate_replay_export_metrics(
                rows,
                neutral_band_bp=int(job.neutral_band_bp or 20),
            )

            total_all_rows += len(rows)
            md_lines.append(
                f"## شهر: {job.start_date.strftime('%B %Y')} "
                f"(من {job.start_date} إلى {job.end_date})"
            )
            md_lines.append(f"- **معرف البناء (Job ID)**: `{job.id}`")
            md_lines.append(f"- **إصدار المحرك**: `{job.engine_version}`")
            md_lines.append(f"- **حالة البناء**: `{job.status}`")
            md_lines.append(f"- **إجمالي التقييمات/الصفحات**: {len(rows)}")
            md_lines.append("")
            md_lines.append(
                "| التاريخ | السهم | الإشارة | السعر | التقييم/Scope | العائد % | "
                "أقصى صعود % | أقصى هبوط % | النتيجة | العائد الزائد % | النتيجة مقابل المؤشر |"
            )
            md_lines.append(
                "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | "
                ":---: | :---: | :---: |"
            )
            for r in rows:
                m = metrics.get(r.id)
                scope = m.evaluation_scope if m else _evaluation_scope(r)
                fwd_ret = _pct(r.forward_return_bp)
                max_up = _pct(r.max_upside_bp)
                max_down = _pct(r.max_drawdown_bp)
                exc_ret = _pct(m.excess_return_bp) if m else None
                
                correct_str = (
                    "✅ ناجحة" if r.correct is True else ("❌ خاسرة" if r.correct is False else "➖")
                )
                bench_str = (
                    "✅ متفوق"
                    if m and m.benchmark_correct is True
                    else ("❌ متراجع" if m and m.benchmark_correct is False else "➖")
                )

                row_parts = [
                    f"| {r.analysis_date} | `{r.ticker}` | **{r.signal or 'N/A'}** |",
                    f" {r.entry if r.entry is not None else 'N/A'} | `{scope}` |",
                    f" {fwd_ret if fwd_ret is not None else 'N/A'}% |",
                    f" {max_up if max_up is not None else 'N/A'}% |",
                    f" {max_down if max_down is not None else 'N/A'}% | {correct_str} |",
                    f" {exc_ret if exc_ret is not None else 'N/A'}% | {bench_str} |",
                ]
                md_lines.append("".join(row_parts))
            md_lines.append("")

        out_path = Path("/workspace/full_2025_replay.md")
        out_path.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"Successfully exported {total_all_rows} rows across {len(jobs)} jobs to {out_path}")

    finally:
        db.close()

if __name__ == "__main__":
    export_full_2025_md()

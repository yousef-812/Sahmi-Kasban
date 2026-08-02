from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import AnalysisReplayJob, AnalysisReplayRow
from app.services.historical_replay_exports import calculate_replay_export_metrics, _pct, _evaluation_scope

def export_jan_feb_2025_md():
    db = SessionLocal()
    try:
        jobs = db.scalars(
            select(AnalysisReplayJob)
            .order_by(AnalysisReplayJob.created_at.desc())
        ).all()

        print(f"Found {len(jobs)} jobs")
        for j in jobs:
            print(f"Job ID: {j.id} | Dates: {j.start_date} -> {j.end_date} | Status: {j.status} | Total Rows: {j.total_rows}")

        target_job = None
        for j in jobs:
            if j.total_rows > 0:
                target_job = j
                break

        if not target_job:
            print("No completed replay job with rows found.")
            return

        rows = db.scalars(
            select(AnalysisReplayRow)
            .where(AnalysisReplayRow.job_id == target_job.id)
            .order_by(AnalysisReplayRow.analysis_date, AnalysisReplayRow.ticker)
        ).all()

        metrics = calculate_replay_export_metrics(
            rows,
            neutral_band_bp=int(round(target_job.neutral_band_pct * 100.0)),
        )

        md_lines = []
        md_lines.append(f"# تقرير نتائج اختبار المحرك (Jan & Feb 2025 Historical Replay)")
        md_lines.append(f"- **معرف البناء (Job ID)**: `{target_job.id}`")
        md_lines.append(f"- **إصدار المحرك**: `{target_job.engine_version}`")
        md_lines.append(f"- **الفترة الزمنية**: من `{target_job.start_date}` إلى `{target_job.end_date}`")
        md_lines.append(f"- **إجمالي الصفحات/التقييمات**: {len(rows)}")
        md_lines.append("")
        md_lines.append("## جدول الصفقات والنتائج التفصيلية (Replay Ledger)")
        md_lines.append("")
        md_lines.append("| التاريخ | السهم | الإشارة | السعر | التقييم/Scope | العائد % | أقصى صعود % | أقصى هبوط % | النتيجة | العائد الزائد % | النتيجة مقابل المؤشر |")
        md_lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

        for r in rows:
            m = metrics.get(r.id)
            scope = m.evaluation_scope if m else _evaluation_scope(r)
            fwd_ret = _pct(r.forward_return_bp)
            max_up = _pct(r.max_upside_bp)
            max_down = _pct(r.max_drawdown_bp)
            exc_ret = _pct(m.excess_return_bp) if m else None
            
            correct_str = "✅ ناجحة" if r.correct is True else ("❌ خاسرة" if r.correct is False else "➖")
            bench_str = "✅ متفوق" if m and m.benchmark_correct is True else ("❌ متراجع" if m and m.benchmark_correct is False else "➖")

            md_lines.append(
                f"| {r.analysis_date} | `{r.ticker}` | **{r.signal or 'N/A'}** | {r.entry_price or 'N/A'} | `{scope}` | {fwd_ret if fwd_ret is not None else 'N/A'}% | {max_up if max_up is not None else 'N/A'}% | {max_down if max_down is not None else 'N/A'}% | {correct_str} | {exc_ret if exc_ret is not None else 'N/A'}% | {bench_str} |"
            )

        out_path = Path("/workspace/jan_feb_2025_replay.md")
        out_path.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"Exported {len(rows)} rows to {out_path}")

    finally:
        db.close()

if __name__ == "__main__":
    export_jan_feb_2025_md()

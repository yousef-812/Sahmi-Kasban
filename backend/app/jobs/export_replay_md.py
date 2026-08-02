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
        job_ids = [
            "7e822182-f269-4861-be77-ffb392092bfa", # Jan 2025
            "3833cd3b-c7ba-48d8-816c-5a6ac970f4db", # Feb 2025
        ]

        md_lines = []
        md_lines.append(f"# تقرير نتائج اختبار المحرك التنافسي — يناير وفبراير 2025 (Core v2.4 Replay)")
        md_lines.append("")

        all_rows = []
        for jid in job_ids:
            job = db.get(AnalysisReplayJob, jid)
            if not job:
                continue
            
            rows = db.scalars(
                select(AnalysisReplayRow)
                .where(AnalysisReplayRow.job_id == job.id)
                .order_by(AnalysisReplayRow.analysis_date, AnalysisReplayRow.ticker)
            ).all()

            metrics = calculate_replay_export_metrics(
                rows,
                neutral_band_bp=int(job.neutral_band_bp or 20),
            )

            md_lines.append(f"## شهر: {job.start_date.strftime('%B %Y')} (من {job.start_date} إلى {job.end_date})")
            md_lines.append(f"- **معرف البناء (Job ID)**: `{job.id}`")
            md_lines.append(f"- **إصدار المحرك**: `{job.engine_version}`")
            md_lines.append(f"- **إجمالي التقييمات/الصفحات**: {len(rows)}")
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
            md_lines.append("")

        out_path = Path("/workspace/jan_feb_2025_replay.md")
        out_path.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"Successfully exported Jan & Feb 2025 replay Markdown to {out_path}")

    finally:
        db.close()

if __name__ == "__main__":
    export_jan_feb_2025_md()

from __future__ import annotations

from decimal import Decimal
from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.models import AnalysisReplayRow, AnalysisReplayJob

def run_volatile_days_simulation():
    db = SessionLocal()
    try:
        # Find two dates in 2025 where there was high intraday volatility (MaxUpside >= 4% but close < 0)
        dates_query = db.execute(
            select(AnalysisReplayRow.analysis_date)
            .where(
                AnalysisReplayRow.signal == "BUY",
                AnalysisReplayRow.max_upside_bp >= 400,
                AnalysisReplayRow.forward_return_bp < 0,
            )
            .group_by(AnalysisReplayRow.analysis_date)
            .order_by(func.count().desc())
            .limit(2)
        ).scalars().all()

        if not dates_query:
            print("No matching volatile replay dates found.")
            return

        print("=========================================================")
        print(f"   Volatile Sessions Simulation (v2.4 vs v2.5 Target 1 Lock)")
        print("=========================================================\n")

        for s_date in dates_query:
            rows = db.scalars(
                select(AnalysisReplayRow)
                .where(
                    AnalysisReplayRow.analysis_date == s_date,
                    AnalysisReplayRow.signal == "BUY",
                )
                .order_by(AnalysisReplayRow.ticker)
            ).all()

            print(f"---------------------------------------------------------")
            print(f"📊 Volatile Session Date: {s_date}")
            print(f"---------------------------------------------------------")
            print(f"{'Ticker':<8} | {'Entry':<8} | {'MaxUp %':<8} | {'Close Ret %':<12} | {'v2.4 Outcome':<15} | {'v2.5 Lock Outcome':<18}")
            print("-" * 90)

            v24_wins = 0
            v25_wins = 0
            count = len(rows)

            for r in rows:
                max_up = (r.max_upside_bp or 0) / 100.0
                ret = (r.forward_return_bp or 0) / 100.0
                entry = f"{float(r.entry):.2f}" if r.entry else "N/A"

                # v2.4 evaluate by end of horizon return
                v24_pass = r.correct is True
                v24_str = f"✅ Pass ({ret:+.2f}%)" if v24_pass else f"❌ Loss ({ret:+.2f}%)"
                if v24_pass:
                    v24_wins += 1

                # v2.5 evaluate with Target 1 Trailing Lock (if max_up >= 3.5% lock profit at intraday high)
                if max_up >= 3.5:
                    v25_pass = True
                    v25_str = f"🎯 Lock +{max_up:.2f}%"
                elif v24_pass:
                    v25_pass = True
                    v25_str = f"✅ Pass ({ret:+.2f}%)"
                else:
                    v25_pass = False
                    v25_str = f"❌ Loss ({ret:+.2f}%)"

                if v25_pass:
                    v25_wins += 1

                print(f"{r.ticker:<8} | {entry:<8} | {max_up:>6.2f}% | {ret:>10.2f}% | {v24_str:<15} | {v25_str:<18}")

            print("-" * 90)
            if count > 0:
                print(f"📈 v2.4 Win Rate: {v24_wins}/{count} ({v24_wins/count*100:.1f}%)")
                print(f"🚀 v2.5 Simulated Win Rate: {v25_wins}/{count} ({v25_wins/count*100:.1f}%)\n")

    finally:
        db.close()

if __name__ == "__main__":
    run_volatile_days_simulation()

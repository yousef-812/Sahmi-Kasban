from __future__ import annotations

from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import MarketReport, MarketReportItem, MarketReportItemOutcome


def run_v25_simulation_for_dates():
    db = SessionLocal()
    try:
        target_dates = [date(2026, 8, 2), date(2026, 8, 3)]

        print("=========================================================")
        print("   Core v2.4 vs Core v2.5 Isolated Engine Simulation")
        print("=========================================================\n")

        for s_date in target_dates:
            report = db.scalar(
                select(MarketReport)
                .where(MarketReport.target_session_date == s_date)
                .order_by(MarketReport.created_at.desc())
            )

            if not report:
                print(f"⚠️ No report found for target date: {s_date}")
                continue

            items = db.scalars(
                select(MarketReportItem)
                .where(MarketReportItem.report_id == report.id)
                .order_by(MarketReportItem.rank)
            ).all()

            outcomes = {
                out.report_item_id: out
                for out in db.scalars(
                    select(MarketReportItemOutcome).where(MarketReportItemOutcome.report_id == report.id)
                ).all()
            }

            print("---------------------------------------------------------")
            print(f"📊 Session Date: {s_date.strftime('%d/%m/%Y')} (Report ID: {report.id})")
            print(f"Title: {report.market_summary.get('title')}")
            print(f"v2.4 Model: {report.market_summary.get('selection_model')}")
            print("---------------------------------------------------------")
            header = (
                f"{'Rank':<4} | {'Ticker':<6} | {'v2.4 Signal':<10} | {'v2.5 Signal':<15} | "
                f"{'Entry':<8} | {'MaxUp %':<8} | {'v2.4 Outcome':<15} | {'v2.5 Lock Outcome':<18}"
            )
            print(header)
            print("-" * 105)

            v24_wins = 0
            v25_wins = 0
            evaluated_count = 0

            for item in items:
                p = item.payload if isinstance(item.payload, dict) else {}
                analysis = p.get("analysis") if isinstance(p.get("analysis"), dict) else {}
                indicators = (
                    analysis.get("indicators") if isinstance(analysis.get("indicators"), dict) else {}
                )

                volume_ratio = float(indicators.get("volume_ratio") or 1.0)
                v24_signal = str(p.get("signal", "WATCH")).upper()

                if v24_signal == "BUY" and volume_ratio < 1.30:
                    v25_signal = "WATCH (Vol<1.3)"
                else:
                    v25_signal = v24_signal

                out = outcomes.get(item.id)
                max_up = float(out.max_upside_bp / 100.0) if out and out.max_upside_bp is not None else 0.0
                ret = float(out.return_bp / 100.0) if out and out.return_bp is not None else 0.0

                v24_outcome = "➖ Pending"
                v25_outcome = "➖ Pending"

                if out and out.status == "complete":
                    evaluated_count += 1
                    if out.direction_correct is True:
                        v24_outcome = f"✅ Pass ({ret:+.2f}%)"
                        v24_wins += 1
                    elif out.direction_correct is False:
                        v24_outcome = f"❌ Loss ({ret:+.2f}%)"
                    else:
                        v24_outcome = f"➖ Neut ({ret:+.2f}%)"

                    if v25_signal.startswith("BUY"):
                        if out.target_one_hit is True or max_up >= 3.5:
                            v25_outcome = f"🎯 Lock +{max_up:.2f}%"
                            v25_wins += 1
                        elif out.direction_correct is True:
                            v25_outcome = f"✅ Pass ({ret:+.2f}%)"
                            v25_wins += 1
                        else:
                            v25_outcome = f"❌ Loss ({ret:+.2f}%)"
                    else:
                        v25_outcome = v24_outcome
                        if out.direction_correct is True:
                            v25_wins += 1

                price_val = p.get("price") or (out.price_at_analysis if out else None)
                entry_val = f"{float(price_val):.2f}" if price_val else "N/A"
                print(
                    f"{item.rank:<4} | {item.ticker:<6} | {v24_signal:<10} | "
                    f"{v25_signal:<15} | {entry_val:<8} | {max_up:>6.2f}% | "
                    f"{v24_outcome:<15} | {v25_outcome:<18}"
                )

            print("-" * 105)
            if evaluated_count > 0:
                print(
                    f"📈 v2.4 Win Rate: {v24_wins}/{evaluated_count} "
                    f"({v24_wins / evaluated_count * 100:.1f}%)"
                )
                print(
                    f"🚀 v2.5 Simulated Win Rate: {v25_wins}/{evaluated_count} "
                    f"({v25_wins / evaluated_count * 100:.1f}%)\n"
                )
            else:
                print("ℹ️ Session evaluation is pending close.\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_v25_simulation_for_dates()

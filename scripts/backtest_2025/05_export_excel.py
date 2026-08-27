from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TRADES = ROOT / "backtest_2025" / "server_output" / "trades_2025.json"
OUT = ROOT / "backtest_2025" / "server_output" / "backtest_2025_result.xlsx"

STARTING_BALANCE = 10_000.0


def main() -> None:
    rows = json.loads(TRADES.read_text(encoding="utf-8"))
    traded = [r for r in rows if r.get("traded")]
    ledger = pd.DataFrame(traded)
    ledger["date"] = pd.to_datetime(ledger["date"])

    ledger = ledger.sort_values("date").reset_index(drop=True)
    ledger["balance"] = STARTING_BALANCE
    for index in ledger.index:
        if index == 0:
            ledger.loc[index, "balance"] = STARTING_BALANCE * (
                1 + ledger.loc[index, "return_pct"] / 100.0
            )
        else:
            ledger.loc[index, "balance"] = ledger.loc[index - 1, "balance"] * (
                1 + ledger.loc[index, "return_pct"] / 100.0
            )
    ledger["month"] = ledger["date"].dt.strftime("%Y-%m")

    monthly = (
        ledger.groupby("month")
        .agg(
            trades=("ticker", "count"),
            wins=("return_pct", lambda s: int((s > 0).sum())),
            avg_return_pct=("return_pct", "mean"),
            best_pct=("return_pct", "max"),
            worst_pct=("return_pct", "min"),
        )
        .reset_index()
    )
    monthly["win_rate_pct"] = (monthly["wins"] / monthly["trades"] * 100).round(2)
    month_balances = ledger.groupby("month")["balance"].last()
    monthly["month_balance"] = monthly["month"].map(month_balances).round(2)
    monthly["month_return_pct"] = (
        monthly["month_balance"] / monthly["month_balance"].shift(1) - 1
    ) * 100
    monthly.loc[0, "month_return_pct"] = (
        monthly.loc[0, "month_balance"] / STARTING_BALANCE - 1
    ) * 100
    monthly = monthly.round(2)

    summary = {
        "إجمالي الجلسات": len(rows),
        "عدد الصفقات المنفذة": len(traded),
        "أيام بلا صفقة": len(rows) - len(traded),
        "رأس المال المبدئي (جنيه)": STARTING_BALANCE,
        "الرصيد النهائي (جنيه)": round(ledger["balance"].iloc[-1], 2),
        "العائد التراكمي %": round(
            (ledger["balance"].iloc[-1] / STARTING_BALANCE - 1) * 100, 2
        ),
        "نسبة الصفقات الرابحة %": round((ledger["return_pct"] > 0).mean() * 100, 2),
        "متوسط عائد الصفقة %": round(ledger["return_pct"].mean(), 2),
        "أفضل صفقة %": round(ledger["return_pct"].max(), 2),
        "أسوأ صفقة %": round(ledger["return_pct"].min(), 2),
        "الانحراف المعياري %": round(ledger["return_pct"].std(), 2),
    }

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        pd.DataFrame(
            [{"البيان": k, "القيمة": v} for k, v in summary.items()]
        ).to_excel(writer, sheet_name="الملخص", index=False)
        monthly.to_excel(writer, sheet_name="الملخص الشهري", index=False)
        ledger[
            [
                "date",
                "ticker",
                "score",
                "signal",
                "qualified",
                "confidence",
                "turnover_egp",
                "entry",
                "exit",
                "return_pct",
                "balance",
            ]
        ].rename(
            columns={
                "date": "التاريخ",
                "ticker": "السهم",
                "score": "الدرجة",
                "signal": "الإشارة",
                "qualified": "مؤهل",
                "confidence": "الثقة",
                "turnover_egp": "متوسط السيولة (جنيه)",
                "entry": "سعر الشراء (فتح)",
                "exit": "سعر البيع (إغلاق)",
                "return_pct": "عائد اليوم %",
                "balance": "الرصيد (جنيه)",
            }
        ).to_excel(writer, sheet_name="دفتر الصفقات", index=False)

    print(f"Saved -> {OUT}")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("\n=== Monthly ===")
    print(monthly.to_string(index=False))


if __name__ == "__main__":
    main()

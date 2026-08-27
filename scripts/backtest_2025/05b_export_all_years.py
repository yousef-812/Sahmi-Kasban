from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "backtest_2025" / "server_output"
OUT_DIR = ROOT / "backtest_2025" / "server_output"

STARTING_BALANCE = 10_000.0
YEARS = [2022, 2023, 2024, 2025]


def build_ledger(year: int) -> pd.DataFrame:
    rows = json.loads((SRC / f"trades_{year}.json").read_text(encoding="utf-8"))
    traded = [r for r in rows if r.get("traded")]
    ledger = pd.DataFrame(traded)
    if ledger.empty:
        return ledger
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
    return ledger


def monthly_table(ledger: pd.DataFrame) -> pd.DataFrame:
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
    return monthly.round(2)


def summary_dict(year: int, ledger: pd.DataFrame) -> dict:
    if ledger.empty:
        return {"السنة": year, "لا توجد صفقات": "البيانات غير كافية"}
    r = ledger["return_pct"]
    cum = (1 + r / 100).cumprod()
    peak = cum.cummax()
    dd = (cum / peak - 1) * 100
    return {
        "السنة": year,
        "الجلسات الكلية": int(json.loads((SRC / f"trades_{year}.json").read_text(encoding="utf-8")).__len__()),
        "عدد الصفقات": len(ledger),
        "رأس المال المبدئي (جنيه)": STARTING_BALANCE,
        "الرصيد النهائي (جنيه)": round(ledger["balance"].iloc[-1], 2),
        "العائد التراكمي %": round((ledger["balance"].iloc[-1] / STARTING_BALANCE - 1) * 100, 2),
        "نسبة الصفقات الرابحة %": round((r > 0).mean() * 100, 2),
        "متوسط عائد الصفقة %": round(r.mean(), 2),
        "وسيط العائد %": round(r.median(), 2),
        "أفضل صفقة %": round(r.max(), 2),
        "أسوأ صفقة %": round(r.min(), 2),
        "الانحراف المعياري %": round(r.std(), 2),
        "أكبر تراجع %": round(dd.min(), 2),
    }


def main() -> None:
    for year in YEARS:
        trades_file = SRC / f"trades_{year}.json"
        if not trades_file.exists():
            print(f"skip {year}: no trades file")
            continue
        ledger = build_ledger(year)
        if ledger.empty:
            print(f"skip {year}: no traded rows")
            continue
        monthly = monthly_table(ledger)
        summary = summary_dict(year, ledger)
        out_path = OUT_DIR / f"backtest_{year}_result.xlsx"
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            pd.DataFrame(
                [{"البيان": k, "القيمة": v} for k, v in summary.items()]
            ).to_excel(writer, sheet_name="الملخص", index=False)
            monthly.to_excel(writer, sheet_name="الملخص الشهري", index=False)
            ledger[
                ["date", "ticker", "score", "signal", "qualified", "confidence",
                 "turnover_egp", "entry", "exit", "return_pct", "balance"]
            ].rename(columns={
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
            }).to_excel(writer, sheet_name="دفتر الصفقات", index=False)
        print(f"{year}: saved {out_path.name} | final={summary['الرصيد النهائي (جنيه)']} | "
              f"return={summary['العائد التراكمي %']}% | dd={summary['أكبر تراجع %']}%")


if __name__ == "__main__":
    main()

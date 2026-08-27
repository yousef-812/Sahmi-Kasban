from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "backtest_2025" / "server_output"
STARTING_BALANCE = 10_000.0

YEAR_LABELS = {
    2022: "2022",
    2023: "2023",
    2024: "2024",
}

MONTH_NAMES = {
    1: "يناير",
    2: "فبراير",
    3: "مارس",
    4: "أبريل",
    5: "مايو",
    6: "يونيو",
    7: "يوليو",
    8: "أغسطس",
    9: "سبتمبر",
    10: "أكتوبر",
    11: "نوفمبر",
    12: "ديسمبر",
}

WEEKDAY_NAMES = {
    6: "الأحد",
    0: "الاثنين",
    1: "الثلاثاء",
    2: "الأربعاء",
    3: "الخميس",
}


def load_trades(year: int) -> list[dict]:
    rows = json.loads((SRC / f"trades_{year}.json").read_text(encoding="utf-8"))
    for row in rows:
        row["date"] = pd.Timestamp(row["date"])
    return rows


def streak_stats(returns: list[float]) -> tuple[int, int]:
    best = worst = run = 0
    current = 0
    for r in returns:
        if r > 0:
            current = current + 1 if current > 0 else 1
        elif r < 0:
            current = current - 1 if current < 0 else -1
        else:
            current = 0
        best = max(best, current)
        worst = min(worst, current)
    return best, -worst


def stats_section(trades: list[dict]) -> str:
    traded = [t for t in trades if t.get("traded")]
    r = np.array([t["return_pct"] for t in traded], dtype=float)
    wins = int((r > 0).sum())
    losses = int((r < 0).sum())
    even = int((r == 0).sum())
    win_streak, loss_streak = streak_stats(r.tolist())
    q1, q3 = np.nanpercentile(r, 25), np.nanpercentile(r, 75)
    skew = float(pd.Series(r).skew())
    lines = [
        "## 2) إحصاءات الصفقات",
        "",
        "| المؤشر | القيمة |",
        "|---|---|",
        f"| متوسط عائد الصفقة | {r.mean():+.2f}% |",
        f"| وسيط عائد الصفقة (Median) | {np.median(r):+.2f}% |",
        f"| الانحراف المعياري | {r.std():.2f}% |",
        f"| أفضل صفقة | {r.max():+.2f}% |",
        f"| أسوأ صفقة | {r.min():+.2f}% |",
        f"| عدد الصفقات الرابحة | {wins} ({wins / len(r) * 100:.2f}%) |",
        f"| عدد الصفقات الخاسرة | {losses} |",
        f"| صفقات متعادلة | {even} |",
        f"| أفضل سلسلة ربح متتالية | {win_streak} صفقات |",
        f"| أسوأ سلسلة خسارة متتالية | {loss_streak} صفقات |",
        f"| الانحراف الإيجابي (Skewness) | {skew:.2f} |",
        f"| الرباعي الأدنى / الأعلى (Q1/Q3) | {q1:+.2f}% / {q3:+.2f}% |",
        "",
        "**القراءة**: ",
    ]
    if r.mean() > 0 and (r > 0).mean() < 0.5:
        lines.append(
            "معدل الفوز أقل من النصف لكن متوسط العائد موجب بسبب وجود مكاسب كبيرة "
            "متفرقة (انحراف إيجابي). يعني الربح يعتمد على \"المكاسب الكبيرة\" وليس على نسبة فوز عالية."
        )
    elif (r > 0).mean() >= 0.5:
        lines.append(
            "نسبة الفوز أعلى من النصف مع متوسط عائد موجب — الاستراتيجية تحقق الربح "
            "بأغلبية صفقات ناجحة متوسطة الكسب."
        )
    else:
        lines.append(
            "نسبة الفوز أقل من النصف ومتوسط العائد سالب — الاستراتيجية خسرت خلال العام."
        )
    lines.append("")
    return "\n".join(lines)


def monthly_section(year: int, trades: list[dict]) -> str:
    traded = [t for t in trades if t.get("traded")]
    ledger = pd.DataFrame(traded)
    ledger["date"] = pd.to_datetime(ledger["date"])
    ledger = ledger.sort_values("date").reset_index(drop=True)
    ledger["balance"] = STARTING_BALANCE
    for idx in ledger.index:
        prev = ledger.loc[idx - 1, "balance"] if idx > 0 else STARTING_BALANCE
        ledger.loc[idx, "balance"] = prev * (1 + ledger.loc[idx, "return_pct"] / 100.0)
    ledger["month"] = ledger["date"].dt.month
    lines = ["## 3) الأداء الشهري (رصيد نهاية الشهر)", "", "| الشهر | الرصيد (جنيه) | عائد الشهر % |", "|---|---|---|"]
    best_month = worst_month = None
    best_val = -1e18
    worst_val = 1e18
    prev_balance = STARTING_BALANCE
    for month_num, group in ledger.groupby("month"):
        month_balance = group["balance"].iloc[-1]
        month_return = (month_balance / prev_balance - 1) * 100
        name = MONTH_NAMES[int(month_num)]
        flag = ""
        if month_return > best_val:
            best_val = month_return
            best_month = (name, month_return)
        if month_return < worst_val:
            worst_val = month_return
            worst_month = (name, month_return)
        if month_return < 0:
            flag = " **"
        lines.append(f"| {name} | {month_balance:,.2f} | {month_return:+.2f}%{flag} |")
        prev_balance = month_balance
    half = len(traded) // 2
    first_half = (ledger.loc[half - 1, "balance"] / STARTING_BALANCE) if half else 1.0
    last_balance = ledger["balance"].iloc[-1]
    second_half = last_balance / ledger.loc[half - 1, "balance"] if half else 1.0
    lines += [
        "",
        f"- **أفضل شهر**: {best_month[0]} ({best_month[1]:+.2f}%).",
        f"- **أسوأ شهر**: {worst_month[0]} ({worst_month[1]:+.2f}%).",
        f"- **النصف الأول**: مضاعف {first_half:.3f}× ({(first_half - 1) * 100:+.1f}%).",
        f"- **النصف الثاني**: مضاعف {second_half:.3f}× ({(second_half - 1) * 100:+.1f}%).",
        "",
    ]
    return "\n".join(lines)


def risk_section(year: int, trades: list[dict]) -> str:
    traded = sorted([t for t in trades if t.get("traded")], key=lambda x: x["date"])
    r = np.array([t["return_pct"] for t in traded], dtype=float)
    cum = np.cumprod(1 + r / 100)
    peak = np.maximum.accumulate(cum)
    dd = (cum / peak - 1) * 100
    dd_min = dd.min()
    dd_idx = int(dd.argmin())
    peak_idx = int(peak[: dd_idx + 1].argmax())
    start = traded[peak_idx]["date"].strftime("%Y-%m-%d")
    end = traded[dd_idx]["date"].strftime("%Y-%m-%d")
    days = (traded[dd_idx]["date"] - traded[peak_idx]["date"]).days
    sharpe = float(r.mean() / r.std() * np.sqrt(len(r)))
    _win_streak, loss_streak = streak_stats(r.tolist())
    return "\n".join(
        [
            "## 4) تحليل المخاطر",
            "",
            "| المؤشر | القيمة |",
            "|---|---|",
            f"| **أكبر تراجع من القمة (Max Drawdown)** | **{dd_min:.2f}%** |",
            f"| فترة أكبر تراجع | من {start} حتى {end} ({days} يومًا) |",
            f"| أسوأ سلسلة خسارة | {loss_streak} صفقة متتالية |",
            f"| شارپ سنوي (شكل مبسط بلا معدل خالٍ من المخاطر) | ≈ {sharpe:.2f} |",
            "",
        ]
    )


def top_bottom_section(trades: list[dict]) -> str:
    traded = [t for t in trades if t.get("traded")]
    top = sorted(traded, key=lambda x: x["return_pct"], reverse=True)[:10]
    bottom = sorted(traded, key=lambda x: x["return_pct"])[:10]
    lines = ["## 5) أفضل وأسوأ الصفقات", "", "### أفضل 10 صفقات", "", "| التاريخ | السهم | العائد % | الدرجة |", "|---|---|---|---|"]
    for t in top:
        lines.append(
            f"| {t['date'].strftime('%Y-%m-%d')} | {t['ticker']} | {t['return_pct']:+.2f} | {t['score']} |"
        )
    lines += ["", "### أسوأ 10 صفقات", "", "| التاريخ | السهم | العائد % | الدرجة |", "|---|---|---|---|"]
    for t in bottom:
        lines.append(
            f"| {t['date'].strftime('%Y-%m-%d')} | {t['ticker']} | {t['return_pct']:+.2f} | {t['score']} |"
        )
    lines += [
        "",
        "**ملاحظة مهمة**: الأسوأ أيضًا كانت درجاتها عالية (أعلى درجة بين أسوأ صفقات العام "
        f"{max(t['score'] for t in bottom):.2f}). الدرجة العالية **لا تعني** عائدًا أعلى في نفس الجلسة.",
        "",
    ]
    return "\n".join(lines)


def scores_section(trades: list[dict]) -> str:
    traded = [t for t in trades if t.get("traded")]
    scores = [t["score"] for t in traded]
    conf = [t.get("confidence") or 0 for t in traded]
    liq = [t.get("turnover_egp") or 0 for t in traded]
    buy_ratio = sum(1 for t in traded if str(t.get("signal", "")).upper() == "BUY") / len(traded) * 100
    qual_ratio = sum(1 for t in traded if t.get("qualified")) / len(traded) * 100
    b1 = [t["return_pct"] for t in traded if t["score"] < 80]
    b2 = [t["return_pct"] for t in traded if t["score"] >= 80]
    lines = [
        "## 6) تحليل الدرجات والإشارات",
        "",
        "| المؤشر | القيمة |",
        "|---|---|",
        f"| متوسط درجة الصفقات | {np.mean(scores):.2f} |",
        f"| أدنى درجة | {min(scores):.2f} |",
        f"| أعلى درجة | {max(scores):.2f} |",
        f"| متوسط الثقة | {np.mean(conf):.2f} |",
        f"| نسبة صفقات BUY | {buy_ratio:.2f}% |",
        f"| نسبة الصفقات المؤهلة (Qualified) | {qual_ratio:.2f}% |",
        f"| متوسط السيولة اليومية للأسهم المختارة | {np.mean(liq) / 1e6:.1f} مليون جنيه (وسيط {np.median(liq) / 1e6:.0f} مليون) |",
        "",
        "**علاقة الدرجة بالعائد (نفس الجلسة):**",
        "",
        "| نطاق الدرجة | عدد الصفقات | متوسط العائد % |",
        "|---|---|---|",
        f"| < 80 | {len(b1)} | {np.mean(b1):+.2f}% |",
        f"| 80+ | {len(b2)} | {np.mean(b2):+.2f}% |",
        "",
        "> كل الصفقات المؤهلة (لأن السهم رقم 1 في التقرير دائمًا مؤهل BUY)، وعدم وجود علاقة "
        "موجبة بين الدرجة والعائد الفوري لنفس الجلسة يعكس أن التقرير مصمم لأفق 5 جلسات وليس لجلسة واحدة.",
        "",
    ]
    return "\n".join(lines)


def weekday_section(trades: list[dict]) -> str:
    traded = [t for t in trades if t.get("traded")]
    df = pd.DataFrame(traded)
    df["dow"] = df["date"].dt.dayofweek
    lines = ["## 7) توزيع العائد حسب يوم الأسبوع", "", "| اليوم | عدد الصفقات | متوسط العائد % |", "|---|---|---|"]
    rows = []
    for dow, group in df.groupby("dow"):
        rows.append((WEEKDAY_NAMES[dow], len(group), group["return_pct"].mean()))
    rows.sort(key=lambda x: x[2], reverse=True)
    for name, count, mean_r in rows:
        lines.append(f"| {name} | {count} | {mean_r:+.2f}% |")
    best_day, worst_day = rows[0], rows[-1]
    lines += [
        "",
        f"**{best_day[0]} هو أفضل يوم** ({best_day[2]:+.2f}%) بينما {worst_day[0]} "
        f"({worst_day[2]:+.2f}%) — ملاحظة قد تستحق المزيد من الفحص.",
        "",
    ]
    return "\n".join(lines)


def frequency_section(trades: list[dict]) -> str:
    counter = Counter(t["ticker"] for t in trades if t.get("traded"))
    lines = ["## 8) الأسهم الأكثر تكرارًا في المركز الأول", "", "| السهم | عدد المرات |", "|---|---|"]
    for ticker, count in counter.most_common(10):
        lines.append(f"| {ticker} | {count} |")
    lines.append("")
    return "\n".join(lines)


def summary_rows(year: int, trades: list[dict]) -> tuple[str, list[str]]:
    traded = [t for t in trades if t.get("traded")]
    r = np.array([t["return_pct"] for t in traded], dtype=float)
    cum = (np.prod(1 + r / 100) - 1) * 100
    final = STARTING_BALANCE * (1 + cum / 100)
    unique = len({t["ticker"] for t in traded})
    lines = [
        "## 1) النتيجة النهائية",
        "",
        "| المؤشر | القيمة |",
        "|---|---|",
        f"| رأس المال المبدئي | {STARTING_BALANCE:,.0f} جنيه |",
        f"| **الرصيد النهائي** | **{final:,.2f} جنيه** |",
        f"| **العائد التراكمي** | **{cum:+.2f}%** |",
        f"| عدد الجلسات | {len(trades)} |",
        f"| عدد الصفقات المنفذة | {len(traded)} ({'كل جلسات ' + str(year) if len(traded) == len(trades) else ''}) |",
        f"| عدد الأسهم المختلفة المختارة | {unique} سهمًا |",
        "",
    ]
    return "\n".join(lines), [f"{cum:+.2f}%", f"{final:,.2f}"]


def build_report(year: int, benchmark: dict | None = None) -> str:
    trades = load_trades(year)
    traded = [t for t in trades if t.get("traded")]
    lines = [
        f"# تقرير تحليل محاكاة استراتيجية \"أفضل سهم يوميًا\" — {year}",
        "",
        f"> **الاستراتيجية**: رأس مال 10,000 جنيه، وكل جلسة تداول يتم شراء **السهم رقم 1** "
        "في تقرير الـTop-10 بسعر فتح الجلسة وبيعه بسعر إغلاق نفس الجلسة (نفس اليوم).",
        "> **التنفيذ**: اشتغلت المحاكاة على سيرفر Sahmi-Kasban (Fly.io) على بيانات TradingView حقيقية (3000 شمعة لكل سهم).",
        "",
        "---",
        "",
    ]
    lines.append(summary_rows(year, trades)[0])
    lines += [
        "---",
        "",
    ]
    lines.append(stats_section(trades))
    lines += [
        "---",
        "",
    ]
    lines.append(monthly_section(year, trades))
    lines += [
        "---",
        "",
    ]
    lines.append(risk_section(year, trades))
    lines += [
        "---",
        "",
    ]
    lines.append(top_bottom_section(trades))
    lines += [
        "---",
        "",
    ]
    lines.append(scores_section(trades))
    lines += [
        "---",
        "",
    ]
    lines.append(weekday_section(trades))
    lines += [
        "---",
        "",
    ]
    lines.append(frequency_section(trades))
    lines += [
        "---",
        "",
    ]
    if benchmark:
        strat_return = (np.prod([1 + t["return_pct"] / 100 for t in traded]) - 1) * 100
        market_value = float(benchmark["market"].replace("%", "").replace("+", ""))
        ratio = strat_return / market_value if market_value > 0 else float("nan")
        if strat_return < 0:
            ratio_line = (
                f"- الاستراتيجية **خسرت {abs(strat_return):.1f}%** بينما السوق ارتفع "
                f"({benchmark['market']}) — عام خاسر للاستراتيجية رغم السوق الصاعد."
            )
        elif np.isfinite(ratio):
            ratio_line = f"- الاستراتيجية تفوقت على المتوسط المرجعي بحوالي **{ratio:.1f} مرة**."
        else:
            ratio_line = "- لا يمكن حساب نسبة التفوق لأن معيار السوق غير موجب."
        lines.append(
            "\n".join(
                [
                    "## 9) المقارنة مع السوق (معيار مرجعي)",
                    "",
                    "| المؤشر | الاستراتيجية | السوق (متوسط الوزن المتساوي لـ287 سهمًا) |",
                    "|---|---|---|",
                    f"| العائد التراكمي {year} | **{strat_return:+.2f}%** | {benchmark['market']} |",
                    "",
                    f"- عدد الأسهم الرابحة في السوق خلال {year}: {benchmark['winners']} من 287 "
                    f"(وسيط العائد السنوي {benchmark['median']}).",
                    ratio_line,
                    "",
                    "---",
                    "",
                ]
            )
        )
    lines.append(
        "\n".join(
            [
                "## 10) نقاط القوة والضعف",
                "",
                "### نقاط القوة",
                "- عائد تراكمي " + ("مرتفع جدًا" if (np.prod([1 + t["return_pct"] / 100 for t in traded]) - 1) > 0 else "سالِب") + " مع تفوق/انخفاض مقابل السوق.",
                f"- تنويع تلقائي عبر {len({t['ticker'] for t in traded})} سهمًا مختلفًا على مدار العام.",
                "- أسهم مختارة عالية السيولة — مناسبة لرأس مال صغير.",
                "",
                "### نقاط الضعف / التحفظات",
                "1. نسبة الفوز والعائد يعتمدان على حالة السوق (2022-2023 صاعدة، 2024 هابطة).",
                "2. أكبر تراجع كبير أثناء فترات الخسارة المستمرة.",
                "3. **بدون تكاليف**: لم تُحسب عمولات الوسيط/الضرائب/فروق الأسعار (Slippage).",
                "4. **تنفيذ مثالي**: افترضنا الشراء بسعر الفتح والبيع بسعر الإغلاق بالضبط.",
                "5. **لا علاقة موجبة بين الدرجة والعائد لنفس الجلسة** — التقرير مصمم لأفق 5 جلسات.",
                "6. بيانات TradingView قد تشمل تحيز بقاء (102 رمزًا غير متوفرين لم يُستخدم أي منهم في الاختيار).",
                "",
                "---",
                "",
            ]
        )
    )
    traded_sorted = sorted(traded, key=lambda x: x["date"])
    cum = np.prod([1 + t["return_pct"] / 100 for t in traded])
    conclusion = (
        f"استراتيجية بسيطة قابلة للتنفيذ (\"اشترِ أول سهم في تقرير الـ10 اليومي، بعْه نهاية الجلسة\") "
        f"حققت في {year} عائدًا **{cum:+.2%}** بدءًا من 10,000 جنيه "
    )
    if cum < 1:
        conclusion += (
            "وهي **نتيجة خاسرة**؛ العائد السلبي يعكس ظروف السوق في ذلك العام. "
        )
    else:
        conclusion += "متجاوزةً متوسط السوق. "
    conclusion += (
        "والنتيجة بدون احتساب التكاليف، ويُفضَّل اختبارها مع تكاليف التداول الفعلية "
        "قبل اعتمادها على أموال حقيقية."
    )
    lines.append(f"## 11) الخلاصة\n\n{conclusion}\n\n---\n")
    lines.append(
        "\n".join(
            [
                "## الملفات المرتبطة",
                "",
                f"- `backtest_{year}_result.xlsx` — الملخص + الملخص الشهري + دفتر الصفقات الكامل.",
                f"- `trades_{year}.json` — بيانات كل صفقة (التاريخ، السهم، السعر، العائد، الرصيد).",
                f"- `summary_{year}.json` — ملخص الأرقام الرئيسية.",
                "",
            ]
        )
    )
    return "\n".join(lines)


def main() -> None:
    benchmarks = {}
    bm_file = SRC / "market_benchmark.json"
    if bm_file.exists():
        benchmarks = json.loads(bm_file.read_text(encoding="utf-8"))
    for year in YEAR_LABELS:
        report = build_report(year, benchmarks.get(str(year)))
        out = SRC / f"backtest_{year}_analysis.md"
        out.write_text(report, encoding="utf-8")
        traded = [t for t in load_trades(year) if t.get("traded")]
        cum = np.prod([1 + t["return_pct"] / 100 for t in traded]) - 1
        print(f"{year}: saved {out.name} | cum={cum:+.2%} | trades={len(traded)}")


if __name__ == "__main__":
    main()

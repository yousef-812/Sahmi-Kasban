from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


@dataclass(frozen=True, slots=True)
class InvestmentMetrics:
    ticker: str
    current_price: float
    pe_ratio: float | None
    pb_ratio: float | None
    dividend_yield_pct: float | None
    roe_pct: float | None
    total_debt: float | None
    market_cap: float | None
    net_income: float | None
    eps: float | None
    fair_value: float | None
    margin_of_safety_pct: float | None
    investment_category: str  # "growth" | "dividend" | "value" | "balanced"
    investment_score: float  # 0 to 100
    strengths: tuple[str, ...]
    risks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FundamentalInvestmentEngine(AnalysisEngine):
    """Evaluates long-term corporate investment quality and intrinsic value for EGX stocks."""

    name = "investment"

    @staticmethod
    def calculate_metrics(
        ticker: str,
        current_price: float,
        *,
        pe_ratio: float | None = None,
        pb_ratio: float | None = None,
        dividend_yield_pct: float | None = None,
        roe_pct: float | None = None,
        total_debt: float | None = None,
        market_cap: float | None = None,
        net_income: float | None = None,
        eps: float | None = None,
        sma_200: float | None = None,
    ) -> InvestmentMetrics:
        price = max(0.01, current_price)
        strengths: list[str] = []
        risks: list[str] = []

        # 1. P/E Valuation Score (Weight: 25%)
        pe_score = 50.0
        if pe_ratio is not None:
            if pe_ratio <= 0:
                pe_score = 15.0
                risks.append("الشركة تسجل خسائر أو مكرر ربحية سالب")
            elif pe_ratio <= 7.0:
                pe_score = 95.0
                strengths.append(f"مكرر ربحية جذاب جداً ومغرٍ للشراء ({pe_ratio:.1f}x)")
            elif pe_ratio <= 12.0:
                pe_score = 80.0
                strengths.append(f"مكرر ربحية متوازن وفي النطاق العادل ({pe_ratio:.1f}x)")
            elif pe_ratio <= 18.0:
                pe_score = 60.0
            elif pe_ratio <= 28.0:
                pe_score = 40.0
                risks.append(f"مكرر ربحية مرتفع نسبياً ({pe_ratio:.1f}x)")
            else:
                pe_score = 25.0
                risks.append(f"مكرر ربحية مبالغ فيه ويفوق متوسط السوق ({pe_ratio:.1f}x)")

        # 2. Dividend Yield Score (Weight: 25%)
        div_score = 45.0
        if dividend_yield_pct is not None:
            if dividend_yield_pct >= 10.0:
                div_score = 98.0
                strengths.append(f"عائد توزيعات نقدية استثنائي يفوق الفائدة البنكية ({dividend_yield_pct:.1f}%)")
            elif dividend_yield_pct >= 7.0:
                div_score = 85.0
                strengths.append(f"توزيعات نقدية كاش قوية ومستقرة ({dividend_yield_pct:.1f}%)")
            elif dividend_yield_pct >= 4.0:
                div_score = 70.0
                strengths.append(f"توزيعات نقدية جيدة ({dividend_yield_pct:.1f}%)")
            elif dividend_yield_pct > 0.0:
                div_score = 55.0
            else:
                div_score = 35.0
                risks.append("لا توجد توزيعات أرباح نقدية معلنة حالياً")

        # 3. Capital Efficiency & ROE (Weight: 25%)
        roe_score = 50.0
        if roe_pct is not None:
            if roe_pct >= 25.0:
                roe_score = 98.0
                strengths.append(f"كفاءة استثنائية في توليد الأرباح من حقوق المساهمين (ROE: {roe_pct:.1f}%)")
            elif roe_pct >= 15.0:
                roe_score = 85.0
                strengths.append(f"عائد ممتاز على حقوق الملكية (ROE: {roe_pct:.1f}%)")
            elif roe_pct >= 8.0:
                roe_score = 65.0
            elif roe_pct > 0:
                roe_score = 45.0
            else:
                roe_score = 15.0
                risks.append("عائد سالب على حقوق الملكية")

        # 4. Solvency & Debt (Weight: 15%)
        solvency_score = 70.0
        if total_debt is not None and market_cap is not None and market_cap > 0:
            debt_ratio = (total_debt / market_cap) * 100.0
            if debt_ratio <= 15.0:
                solvency_score = 95.0
                strengths.append("موقف مالي ممتاز بدون ديون ثقيلة")
            elif debt_ratio <= 45.0:
                solvency_score = 75.0
            elif debt_ratio <= 80.0:
                solvency_score = 50.0
                risks.append("نسبة ديون متوسطة تتطلب المتابعة")
            else:
                solvency_score = 30.0
                risks.append("حجم الديون مرتفع بالنسبة للقيمة السوقية")

        # 5. Technical Long-term Base (Weight: 10%)
        trend_score = 60.0
        if sma_200 is not None and sma_200 > 0:
            if price >= sma_200:
                trend_score = 90.0
                strengths.append("السعر يتداول أعلى المتوسط طويل الأجل (SMA200) مؤكداً الاتجاه الإيجابي")
            else:
                trend_score = 40.0
                risks.append("السعر أدنى المتوسط طويل الأجل (SMA200)")

        total_score = (
            pe_score * 0.25
            + div_score * 0.25
            + roe_score * 0.25
            + solvency_score * 0.15
            + trend_score * 0.10
        )
        total_score = max(0.0, min(100.0, total_score))

        # Intrinsic Fair Value & Margin of Safety
        fair_value: float | None = None
        margin_of_safety: float | None = None

        if eps is not None and eps > 0:
            # Conservative target multiple for EGX is 11.5x earnings
            fair_value = round(eps * 11.5, 2)
            margin_of_safety = round(((fair_value - price) / price) * 100.0, 1)
        elif pe_ratio is not None and pe_ratio > 0:
            implied_eps = price / pe_ratio
            fair_value = round(implied_eps * 11.5, 2)
            margin_of_safety = round(((fair_value - price) / price) * 100.0, 1)

        # Categorization
        category = "balanced"
        if dividend_yield_pct is not None and dividend_yield_pct >= 7.0:
            category = "dividend"
        elif roe_pct is not None and roe_pct >= 16.0:
            category = "growth"
        elif margin_of_safety is not None and margin_of_safety >= 25.0:
            category = "value"

        return InvestmentMetrics(
            ticker=ticker,
            current_price=price,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            dividend_yield_pct=dividend_yield_pct,
            roe_pct=roe_pct,
            total_debt=total_debt,
            market_cap=market_cap,
            net_income=net_income,
            eps=eps,
            fair_value=fair_value,
            margin_of_safety_pct=margin_of_safety,
            investment_category=category,
            investment_score=round(total_score, 1),
            strengths=tuple(strengths),
            risks=tuple(risks),
        )

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        latest = candles.iloc[-1]
        price = safe_float(latest.get("close"), 1.0)
        sma_200 = safe_float(latest.get("sma_200"), price)
        ticker = str(context.get("ticker", "UNKNOWN"))

        pe_ratio = safe_float(context.get("pe_ratio")) or None
        pb_ratio = safe_float(context.get("pb_ratio")) or None
        dividend_yield_pct = safe_float(context.get("dividend_yield_pct")) or None
        roe_pct = safe_float(context.get("roe_pct")) or None
        total_debt = safe_float(context.get("total_debt")) or None
        market_cap = safe_float(context.get("market_cap")) or None
        net_income = safe_float(context.get("net_income")) or None
        eps = safe_float(context.get("eps")) or None

        metrics = self.calculate_metrics(
            ticker=ticker,
            current_price=price,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            dividend_yield_pct=dividend_yield_pct,
            roe_pct=roe_pct,
            total_debt=total_debt,
            market_cap=market_cap,
            net_income=net_income,
            eps=eps,
            sma_200=sma_200,
        )

        context["investment_metrics"] = metrics.to_dict()

        return EngineResult(
            name=self.name,
            score=metrics.investment_score,
            confidence=85.0 if metrics.pe_ratio is not None else 65.0,
            details=metrics.to_dict(),
            reasons=list(metrics.strengths[:3]),
        )

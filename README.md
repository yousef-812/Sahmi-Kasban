# Sahmi Kasban — Core Engines

نواة مستقلة لمحركات تحليل أسهم البورصة المصرية، منقولة ومُعاد تنظيمها من مشروع EGX-Pilot بدون الواجهة، المستخدمين، قاعدة البيانات أو جدولة السيرفر.

## المحركات الموجودة

- **Market Environment**: تحديد حالة السوق صاعد/هابط/عرضي ومستوى المخاطرة.
- **Stock Qualification**: فلترة السيولة، التاريخ السعري، ATR والانحرافات السعرية.
- **Technical Analysis**: الاتجاه، المتوسطات، RSI، MACD، ATR والحجم.
- **Smart Money Concepts (SMC)**: BOS، CHOCH، liquidity sweep، FVG ومناطق premium/discount.
- **Multi-Timeframe**: توافق الاتجاه على اليومي والأسبوعي والشهري.
- **Quantitative**: الزخم، التذبذب، volume z-score واحتمال الصعود.
- **Risk & Position Sizing**: نقطة الدخول، وقف الخسارة، الأهداف وحجم المركز وفق نسبة مخاطرة محددة.
- **Scenario Engine**: سيناريو صاعد وأساسي وهابط.
- **Final Scoring**: دمج المحركات بأوزان واضحة وإصدار BUY / WATCH / AVOID.

## مثال سريع

```python
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer

analyzer = SahmiKasbanAnalyzer(AnalysisConfig(capital=150_000, risk_per_trade=0.01))
report = analyzer.analyze("COMI", candles)
print(report.signal, report.final_score)
```

`candles` قائمة من السجلات وتحتوي على الأقل على:

```text
timestamp, open, high, low, close, volume
```

## ملاحظات

هذه المحركات أدوات تحليل ودعم قرار وليست ضمانًا للربح أو توصية مالية. يجب اختبار أي استراتيجية تاريخيًا وورقيًا قبل استخدامها بأموال حقيقية.

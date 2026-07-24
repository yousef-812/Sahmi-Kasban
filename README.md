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

## تكامل الذكاء الاصطناعي

تم نقل تكامل Groq وOpen-WebUI من المشروع القديم إلى حزمة مستقلة. يدعم التكامل:

- استخدام Open-WebUI كمزود أساسي عند ضبط عنوانه.
- الرجوع إلى Groq وتدوير أكثر من مفتاح عند فشل المزود الأساسي.
- شرح نتائج تحليل السهم باستخدام بيانات المحركات فقط.
- مراجعة مناقشات المستخدمين قبل النشر.
- استخراج توقع قابل للقياس من نص المناقشة.
- تقييم التوقع بعد انتهاء الجلسة مع تثبيت المكافأة من السيرفر.

متغيرات التشغيل:

```text
OPEN_WEBUI_URL
OPEN_WEBUI_API_KEY
GROQ_API_KEYS
AI_MODEL
AI_TIMEOUT_SECONDS
AI_MAX_TOKENS
AI_TEMPERATURE
```

يجب حفظ المفاتيح في Secrets أو متغيرات البيئة وعدم وضعها داخل الكود أو تطبيق Flutter.

## مثال سريع

```python
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer

analyzer = SahmiKasbanAnalyzer(AnalysisConfig(capital=150_000, risk_per_trade=0.01))
report = analyzer.analyze("COMI", candles)
print(report.signal, report.final_score)
```

استخدام خدمة الذكاء الاصطناعي:

```python
from sahmi_kasban.ai import SahmiAIService

ai = SahmiAIService()
result = await ai.moderate_discussion("أتوقع صعود سهم معين خلال الجلسة القادمة")
print(result)
```

`candles` قائمة من السجلات وتحتوي على الأقل على:

```text
timestamp, open, high, low, close, volume
```

## ملاحظات

هذه المحركات أدوات تحليل ودعم قرار وليست ضمانًا للربح أو توصية مالية. يجب اختبار أي استراتيجية تاريخيًا وورقيًا قبل استخدامها بأموال حقيقية.

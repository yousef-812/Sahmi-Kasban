# Sahmi Kasban — TradingView Migration Log

## 2026-07-25 — نقل وفحص موديول جلب البيانات

**الحالة:** العمل مستمر على الفرع `agent/tradingview-provider` داخل Pull Request رقم 8. لن يتم الدمج في `main` قبل نجاح الاختبارات العادية واختبار اتصال حي يعيد بيانات `COMI` الفعلية.

## طلب التنفيذ

نقل بيانات وطريقة اتصال TradingView المستخدمة في البوت القديم، واستخدام موديول مستقل باسم:

```text
backend/reusable_data_fetcher.py
```

الواجهة المطلوبة مبنية على الملف الكامل الذي أرسله المستخدم، وتشمل:

- `TradingViewConnector`
- `_ConnectionPool`
- `FundamentalsFetcher`
- `TechnicalAnalysisService`
- `StockDataFetcher`
- `get_full_data`
- `get_realtime_price`
- `get_historical_data`
- `get_fundamentals`
- `calculate_indicators`

## بيانات الاتصال المعتمدة

```text
WebSocket URL = wss://data.tradingview.com/socket.io/websocket
Origin = https://www.tradingview.com
User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Auth Token = unauthorized_user_token
EGX Symbol Format = EGX:COMI
```

لا توجد بيانات حساب خاصة أو Cookie أو كلمة مرور داخل الموديول. `unauthorized_user_token` هو التوكن العام الذي كان يستخدمه المشروع القديم.

## تدقيق الملف المرسل

تم اختبار الملف المرسل نفسه قبل تعديله، وظهرت المشكلات التالية:

1. بداية الوصف لم تكن مسبوقة بعلامة فتح `"""` مع وجود علامة الإغلاق، ولذلك فشل `py_compile` بخطأ `unterminated triple-quoted string`.
2. `StockDataFetcher(tv_token="CUSTOM_TOKEN")` لم يكن يمرر التوكن إلى الـConnection Pool؛ الاختبار أثبت أن الاتصالات أرسلت `unauthorized_user_token` بدل التوكن الممرر.
3. حلقة heartbeat كانت ترسل القيمة الثابتة `~h~5` كل 15 ثانية، ولا تعيد نبضة TradingView الفعلية المرسلة داخل إطار `~m~...~m~~h~...`.
4. الـPool كان يحتفظ بالقفل أثناء فتح اتصال شبكي، ويُنشئ اتصالًا إضافيًا خارج الحد المحدد عند انشغال جميع الاتصالات.
5. استدعاء Yahoo Finance كان متزامنًا داخل الدالة async، ما قد يحجب event loop.
6. إغلاق الاتصالات لم يكن ينتظر انتهاء مهام listener ولم يكن ينظف حالة الـPool بالكامل.
7. فشل الشموع كان يتحول إلى قائمة فارغة بدون إشارة واضحة تسمح للمستدعي بتمييز النتيجة الناقصة.

## الإصلاحات المطبقة

- إضافة docstring صحيحة ليصبح الملف Python صالحًا.
- إنشاء Pool مستقل لكل `StockDataFetcher` ويستخدم `tv_token` الذي مرره المستدعي.
- إعادة heartbeat الفعلي إلى TradingView بدل إرسال قيمة ثابتة.
- جعل الاتصال idempotent ومنع فتح الاتصال نفسه مرتين.
- استخدام `asyncio.Condition` لانتظار اتصال متاح مع احترام حد الـPool.
- تنظيف الشموع والتحقق من OHLCV وإزالة التكرار وترتيب timestamps.
- التعامل مع `series_error` و`protocol_error` و`critical_error`.
- تشغيل Yahoo Finance في thread منفصل داخل `get_full_data`.
- إغلاق listener والـWebSocket والـPool بصورة منتظمة.
- الحفاظ على الواجهة المطلوبة والمفاتيح:

```text
ticker
market
price
historical
indicators
fundamentals
errors
```

- إضافة دعم:
  - EGX / CASE
  - US / NASDAQ / NYSE
  - LSE بصيغة TradingView `LON:TICKER`
  - TADAWUL
  - DFM
  - ADX
  - QSE
  - BIST
  - الصيغة المباشرة `EXCHANGE:TICKER`

## توحيد مسار Backend

كان يوجد تنفيذ منفصل لبروتوكول TradingView في:

```text
backend/app/market_data/tradingview.py
```

تمت إزالة تكرار البروتوكول، وأصبح مزود الـBackend يستخدم نفس `TradingViewConnector` الموجود في `reusable_data_fetcher.py`. هذا يمنع إصلاح الموديول وترك خطأ مختلف في مسار تحليل الأسهم الحقيقي.

الإعداد الحالي:

```text
MARKET_DATA_PRIMARY=tradingview
MARKET_DATA_FALLBACK=yfinance
```

## التحقق المحلي المنفذ

### 1. فحص Syntax

النسخة المصححة نجحت في:

```text
python -m py_compile reusable_data_fetcher.py
```

### 2. محاكاة TradingView WebSocket

تم تشغيل WebSocket محلي يحاكي رسائل TradingView التالية:

- `set_auth_token`
- heartbeat
- `quote_add_symbols`
- `qsd`
- `create_series`
- `timescale_update`

ثم تم تشغيل:

```python
fetcher = StockDataFetcher(tv_token="CUSTOM_TOKEN", pool_size=2)
data = await fetcher.get_full_data("COMI", market="EGX")
```

نتيجة الاختبار:

```json
{
  "status": "ok",
  "tokens": ["CUSTOM_TOKEN", "CUSTOM_TOKEN"],
  "heartbeat_echoes": 2,
  "candles": 200,
  "price": 72.5
}
```

هذا يثبت محليًا أن:

- التوكن الممرر يصل إلى الاتصالين.
- heartbeat يتم إرجاعه بصورة صحيحة.
- السعر اللحظي يصل إلى الـFacade.
- 200 شمعة تصل وتُعاد بالترتيب.
- `get_full_data` يجمع السعر والشموع والمؤشرات والأساسيات.
- إغلاق الـPool لا يترك الاتصال مفتوحًا.

هذا اختبار بروتوكول محلي، وليس دليلًا بعد على أن TradingView الخارجي متاح من بيئة الإنتاج.

## الاختبارات المضافة للريبو

- تحويل الرموز لكل الأسواق المطلوبة.
- تنظيف الشموع وإزالة التكرارات والصفوف غير المنطقية.
- حساب المؤشرات من 240 شمعة.
- fallback إلى آخر إغلاق عند تعذر السعر اللحظي.
- اختبار WebSocket محلي كامل للتوكن والـheartbeat والسعر و200 شمعة.
- اختبار تحويل مزود الـBackend للـtimestamps والبيانات.
- اختبار الفواصل الزمنية وعدد الشموع المطلوبة.

## Smoke Test الحي الإلزامي

الملف:

```text
backend/scripts/tradingview_smoke.py
```

يشغل:

```python
data = await StockDataFetcher().get_full_data("COMI", market="EGX")
```

ولا يعتبر ناجحًا إلا إذا تحقق الآتي:

- `errors` فارغة.
- 200 شمعة يومية على الأقل.
- آخر إغلاق أكبر من صفر.
- سعر حالي أو historical fallback صالح.
- RSI وMACD محسوبان.
- إغلاق الاتصالات بدون خطأ.

## عائق التحقق الحي الحالي

بيئة التنفيذ المحلية لا تستطيع حل DNS للنطاقات الخارجية:

```text
data.tradingview.com
query1.finance.yahoo.com
github.com
```

كما أن GitHub Actions Runs السابقة:

- `30154439734`
- `30154736380`
- `30154822281`

أنهت جميع الوظائف قبل إنشاء أي Step، حتى وظائف lint والاختبارات غير المتصلة بالإنترنت. أعاد GitHub `steps: None` ولم يوفر Logs، ولذلك لا يمكن نسبة الفشل إلى كود TradingView.

## قرار المرحلة

- Pull Request رقم 8 يظل Draft.
- لا دمج في `main` حاليًا.
- لا انتقال إلى المرحلة التالية.
- النجاح المحلي للمحاكاة شرط ضروري لكنه غير كافٍ وحده.
- الدمج يتطلب Runner متصلًا بالإنترنت ينفذ `tradingview_smoke.py` ويعرض بيانات `COMI` الفعلية.

## الملفات الرئيسية

- `backend/reusable_data_fetcher.py`
- `backend/app/market_data/tradingview.py`
- `backend/app/market_data/provider.py`
- `backend/scripts/tradingview_smoke.py`
- `backend/tests/test_reusable_data_fetcher.py`
- `backend/tests/test_tradingview_provider.py`
- `docs/REUSABLE_DATA_FETCHER.md`
- `.github/workflows/ci.yml`

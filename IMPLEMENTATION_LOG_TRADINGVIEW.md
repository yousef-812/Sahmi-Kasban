# Sahmi Kasban — TradingView Migration Log

## 2026-07-25 — نقل موديول جلب البيانات القديم

**الحالة:** تم تنفيذ النقل على الفرع `agent/tradingview-provider` داخل Pull Request رقم 8. لم يتم الدمج في `main` حتى ينجح اختبار اتصال حي.

## طلب التنفيذ

نقل بيانات وطريقة اتصال TradingView المستخدمة في البوت القديم، ثم تجربة جلب بيانات أسهم حقيقية داخل مشروع `Sahmi-Kasban`.

بعد توضيح واجهة الموديول المطلوبة، تم اعتماد الملف:

```text
backend/reusable_data_fetcher.py
```

## ما وُجد في EGX-Pilot

الملف `reusable_data_fetcher.py` لم يكن موجودًا داخل الريبو القديم كملف منفرد، لكن مكوناته كانت موجودة في:

- `backend/app/services/tv_connector.py`
- `backend/app/services/data_provider.py`
- `backend/app/services/exchange_map.py`
- `backend/app/services/fundamentals_fetcher.py`
- `backend/app/services/technical_analysis.py`

تم تجميع هذه المكونات في واجهة واحدة مطابقة للاستخدام المطلوب.

## بيانات اتصال TradingView المنقولة

```text
WebSocket URL = wss://data.tradingview.com/socket.io/websocket
Origin = https://www.tradingview.com
User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Auth Token = unauthorized_user_token
EGX Symbol Format = EGX:COMI
```

المشروع القديم لم يكن يحتوي على اسم مستخدم أو كلمة مرور أو Session Cookie لحساب TradingView. الاتصال كان يستخدم التوكن العام `unauthorized_user_token`.

## الموديول القابل لإعادة الاستخدام

تم تنفيذ:

- `TradingViewConnector`
- `_ConnectionPool`
- `FundamentalsFetcher`
- `TechnicalAnalysisService`
- `StockDataFetcher`

### الواجهة الرئيسية

```python
fetcher = StockDataFetcher(tv_token="unauthorized_user_token")

data = await fetcher.get_full_data("COMI", market="EGX")

price = await fetcher.get_realtime_price("COMI", market="EGX")
candles = await fetcher.get_historical_data(
    "COMI",
    market="EGX",
    timeframe="1D",
    count=200,
)
fundamentals = fetcher.get_fundamentals("COMI", market="EGX")
indicators = fetcher.calculate_indicators(candles)

await fetcher.close()
```

## دعم الأسواق

تمت إضافة تحويلات أولية للأسواق:

- `EGX` و`CASE` إلى `EGX:TICKER` و`TICKER.CA`.
- `US` و`NASDAQ` إلى `NASDAQ:TICKER`.
- `NYSE` إلى `NYSE:TICKER`.
- `LSE` إلى `LSE:TICKER` و`TICKER.L`.
- دعم الصيغة المباشرة مثل `EGX:COMI`.

## البيانات التي يعيدها get_full_data

```text
symbol
market
price
historical
indicators
fundamentals
```

- السعر اللحظي والشموع من TradingView.
- البيانات الأساسية من Yahoo Finance.
- المؤشرات محسوبة محليًا باستخدام `ta` و`pandas`.
- إذا فشل السعر اللحظي تستخدم آخر شمعة تاريخية كـfallback.
- إذا فشلت الشموع التاريخية تفشل العملية لأن التحليل لا يمكن حسابه.

## المؤشرات المنفذة

- SMA 20 / 50 / 200
- EMA 9 / 12 / 21 / 26
- RSI
- MACD / Signal / Histogram
- Stochastic K / D
- Williams %R
- ROC
- CCI
- Bollinger Bands
- ATR
- ADX / DI+ / DI-
- VWAP
- MFI
- اتجاه عام

## دمج TradingView في Backend

تم ضبط:

```text
MARKET_DATA_PRIMARY=tradingview
MARKET_DATA_FALLBACK=yfinance
```

تمت إضافة `TradingViewMarketDataProvider` إلى طبقة مزودي السوق الحالية، مع استمرار yfinance كبديل في حالة فشل TradingView.

## الاختبارات المضافة

تمت كتابة اختبارات لـ:

- ثبات بيانات الاتصال المنقولة من المشروع القديم.
- ترميز وفك رسائل بروتوكول TradingView.
- تحويل الفواصل الزمنية وعدد الشموع.
- تنظيف OHLCV وترتيبه وإزالة التكرار.
- تحويل الرموز بين TradingView وYahoo.
- حساب المؤشرات من 240 شمعة تجريبية.
- استخدام آخر إغلاق عند فشل السعر اللحظي.
- واجهة `get_full_data` المجمعة.

## Smoke Test الحي

تم إنشاء:

```text
backend/scripts/tradingview_smoke.py
```

ويشغل فعليًا:

```python
data = await StockDataFetcher().get_full_data("COMI", market="EGX")
```

ويشترط:

- 200 شمعة يومية على الأقل.
- آخر إغلاق أكبر من صفر.
- وجود RSI وMACD.
- وجود سعر لحظي أو fallback من آخر إغلاق.
- محاولة إرجاع اسم الشركة والقيمة السوقية.

## عائق التحقق الحالي

تم تشغيل GitHub Actions عدة مرات على PR رقم 8، ومنها Run IDs:

- `30154439734`
- `30154736380`
- `30154822281`

في كل تشغيل انتهت جميع الوظائف بالحالة `failure` قبل إنشاء أي Step، بما فيها:

- Core lint
- Core tests
- Backend lint
- Backend tests
- TradingView live smoke

الـAPI الخاص بـGitHub يعيد `steps: None` ولا يوفر Logs للوظائف. هذا يعني أن الـRunner لم يبدأ تنفيذ الأوامر أصلًا، ويرجح وجود مشكلة في توفر GitHub Actions أو دقائق الحساب، وليس فشلًا صادرًا من كود TradingView.

كما أن بيئة التنفيذ المحلية الحالية لا تستطيع حل DNS للنطاقات الخارجية، ومنها:

```text
data.tradingview.com
query1.finance.yahoo.com
github.com
```

لذلك لا يمكن الادعاء أن تجربة الجلب الحي نجحت حتى الآن.

## قرار الدمج

تم إبقاء Pull Request رقم 8 كـDraft وعدم دمجه في `main` للأسباب التالية:

1. مزود البيانات جزء حساس وأساسي في التطبيق.
2. الاختبار الحي لم يبدأ فعليًا بسبب عائق البنية التحتية.
3. لا يجب اعتبار فشل Runner نجاحًا أو فشلًا للاتصال.
4. سيتم الدمج فقط بعد نجاح `tradingview-live-smoke` وإظهار بيانات `COMI` الفعلية.

## الملفات الرئيسية

- `backend/reusable_data_fetcher.py`
- `backend/app/market_data/tradingview.py`
- `backend/app/market_data/provider.py`
- `backend/scripts/tradingview_smoke.py`
- `backend/tests/test_reusable_data_fetcher.py`
- `backend/tests/test_tradingview_provider.py`
- `docs/REUSABLE_DATA_FETCHER.md`
- `.github/workflows/ci.yml`

## المطلوب قبل الدمج

- عودة GitHub Actions للعمل أو توفير Runner بديل متصل بالإنترنت.
- نجاح lint والاختبارات العادية.
- نجاح `get_full_data("COMI")` حيًا.
- تسجيل عدد الشموع وآخر سعر ومصدر السعر وقيم RSI وMACD.
- إزالة الـlive smoke المؤقت من CI بعد إثبات الاتصال، مع إبقاء السكربت اليدوي.

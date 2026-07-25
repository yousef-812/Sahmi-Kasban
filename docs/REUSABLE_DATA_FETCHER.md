# Reusable Stock Data Fetcher

الملف التنفيذي:

```text
backend/reusable_data_fetcher.py
```

يجمع الموديول الخدمات التي كانت موزعة داخل مشروع `EGX-Pilot` في واجهة واحدة قابلة لإعادة الاستخدام.

## المكونات

| المكون | الوظيفة |
|---|---|
| `TradingViewConnector` | اتصال WebSocket دائم مع TradingView باستخدام نفس بيانات الاتصال القديمة |
| `_ConnectionPool` | إعادة استخدام أكثر من اتصال ومنع فتح اتصال جديد لكل طلب |
| `FundamentalsFetcher` | جلب البيانات الأساسية من Yahoo Finance |
| `TechnicalAnalysisService` | حساب المؤشرات الفنية من شموع OHLCV |
| `StockDataFetcher` | الواجهة الرئيسية لجميع الوظائف |

## المتطلبات

يتم تثبيتها تلقائيًا من `backend/pyproject.toml`:

```bash
pip install websockets yfinance pandas numpy ta
```

## الاستخدام الكامل

من داخل مجلد `backend` أو بعد تثبيت الحزمة:

```python
import asyncio

from reusable_data_fetcher import StockDataFetcher


async def main() -> None:
    fetcher = StockDataFetcher(tv_token="unauthorized_user_token")
    try:
        data = await fetcher.get_full_data("COMI", market="EGX")

        print(data["price"])
        print(data["historical"])
        print(data["indicators"])
        print(data["fundamentals"])
    finally:
        await fetcher.close()


asyncio.run(main())
```

## استخدام كل وظيفة منفردة

```python
fetcher = StockDataFetcher()

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

## الأسواق المدعومة حاليًا

```python
await fetcher.get_full_data("COMI", market="EGX")
await fetcher.get_full_data("AAPL", market="US")
await fetcher.get_full_data("VOD", market="LSE")
await fetcher.get_full_data("EGX:COMI")
```

الرموز الأمريكية بدون Exchange صريح تُرسل افتراضيًا إلى `NASDAQ`. يمكن استخدام `NYSE:IBM` أو `NASDAQ:AAPL` لتحديد البورصة مباشرة.

## بيانات اتصال TradingView المنقولة

```text
WebSocket URL: wss://data.tradingview.com/socket.io/websocket
Origin: https://www.tradingview.com
Auth token: unauthorized_user_token
Symbol format: EGX:COMI
```

لا يحتوي التكامل القديم على اسم مستخدم أو كلمة مرور أو Cookie خاصة بحساب TradingView. القيمة `unauthorized_user_token` هي القيمة العامة المستخدمة في المشروع القديم.

## المؤشرات

الموديول يعيد أحدث قيم:

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
- تصنيف الاتجاه

## اختبار الاتصال الحي

```bash
PYTHONPATH=backend python backend/scripts/tradingview_smoke.py
```

الاختبار يطلب `get_full_data("COMI", market="EGX")` ويتأكد من:

- وجود 200 شمعة يومية على الأقل.
- أن آخر إغلاق أكبر من صفر.
- حساب RSI وMACD.
- إرجاع السعر اللحظي أو استخدام آخر إغلاق كـfallback.
- محاولة جلب اسم الشركة والقيمة السوقية من Yahoo Finance.

## ملاحظات تشغيلية

- السعر والشموع يأتون من TradingView.
- البيانات الأساسية تأتي من Yahoo Finance.
- تعطل السعر اللحظي لا يمنع إرجاع التقرير؛ يُستخدم آخر إغلاق تاريخي.
- فشل البيانات التاريخية يعتبر فشلًا للعملية لأن المؤشرات لا يمكن حسابها بدونها.
- يجب دائمًا استدعاء `close()` عند انتهاء الاستخدام.
- قبل الإطلاق التجاري يجب مراجعة شروط استخدام وإعادة عرض بيانات كل مزود.

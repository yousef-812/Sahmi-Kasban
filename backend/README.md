# Sahmi Kasban API

Backend مستقل مبني باستخدام FastAPI وPostgreSQL، ومسؤول عن جميع العمليات الحساسة التي لا يجب تنفيذها داخل Flutter.

## التشغيل باستخدام Docker

من جذر المشروع:

```bash
docker compose up --build
```

بعد التشغيل:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`
- Database Health: `http://localhost:8000/api/v1/health/database`

## التشغيل محليًا بدون Docker

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

على Windows استخدم أمر تفعيل البيئة المناسب بدل `source`.

## حسابات المستخدمين

الـAPI يدعم:

- التسجيل بالبريد وكلمة المرور.
- تأكيد البريد باستخدام توكن أحادي الاستخدام.
- إعادة إرسال رسالة التأكيد دون كشف وجود الحساب.
- تسجيل الدخول بعد تأكيد البريد.
- Access Token قصير العمر وRefresh Token مخزن كـhash وقابل للإلغاء.
- تدوير Refresh Token وإلغاء القديم تلقائيًا.
- نسيان وإعادة تعيين كلمة المرور.
- تغيير كلمة المرور مع إلغاء جميع الجلسات.
- حذف ناعم للحساب مع الاحتفاظ بسجلات العمليات للتدقيق.

أهم المسارات:

```text
POST /api/v1/auth/register
POST /api/v1/auth/verify-email
POST /api/v1/auth/resend-verification
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
GET  /api/v1/profile/avatars
GET  /api/v1/profile/me
PATCH /api/v1/profile/me
POST /api/v1/profile/change-password
DELETE /api/v1/profile/me
```

## المحفظة والخطة المجانية

عند التسجيل يتم إنشاء:

- Wallet Account منفصل.
- اشتراك مجاني.
- 300 نقطة = 3 عملات للأسبوع الحالي.
- Ledger Entry وWeekly Grant بمعرفات فريدة.

مسارات القراءة:

```text
GET /api/v1/wallet
GET /api/v1/wallet/history
```

لا يوجد مسار عام يسمح لتطبيق Flutter بإضافة العملات. عمليات الإضافة والخصم تتم عبر خدمات السيرفر فقط وباستخدام `transaction_id` فريد، مع قفل صف المحفظة أثناء التعديل.

تشغيل توزيع الأسبوع الحالي يدويًا أو من Scheduled Machine:

```bash
python -m app.jobs.grant_weekly_points
```

تشغيل الأمر أكثر من مرة في الأسبوع نفسه لا يكرر المكافأة.

## بيانات EGX وتحليل السهم

المسارات:

```text
GET  /api/v1/market/instruments
POST /api/v1/stocks/{ticker}/analysis
```

مسار الرموز يعرض Seed Registry من 154 رمزًا بعد إزالة التكرارات من القائمة القديمة. هذه القائمة مناسبة للتطوير والاختبارات، لكنها ليست بديلًا عن Master List رسمي ومحدث من البورصة أو مزود بيانات مرخص.

طلب التحليل يحتاج Access Token، ويقبل جسمًا اختياريًا:

```json
{
  "language": "ar"
}
```

قواعد التنفيذ:

- تكلفة التحليل الجديد `50` نقطة = `0.50` عملة.
- لا يحدث الخصم إلا بعد اكتمال محركات التحليل بنجاح وإنشاء النتيجة.
- إذا فشل مزود البيانات أو المحركات أو قاعدة البيانات، تُلغى المعاملة ولا يُخصم الرصيد.
- إذا كانت بصمة البيانات وإصدار المحرك وإعداداته لم تتغير، تُعاد النتيجة المخزنة دون خصم.
- Snapshot الأسعار، نتيجة التحليل، وLedger debit تُحفظ داخل معاملة قاعدة بيانات واحدة.
- فشل خدمة AI لا يلغي التحليل الرقمي؛ يُستخدم شرح عربي ثابت ويُوضح المصدر داخل `explanation_source`.
- كل تقرير يحتوي وقت البيانات، المزود الفعلي، عدد الشموع، بصمة البيانات، إصدار المحرك، وإخلاء مسؤولية واضح.

إعدادات السوق والتحليل الأساسية:

```text
MARKET_DATA_PRIMARY=tradingview
MARKET_DATA_FALLBACK=yfinance
MARKET_TIMEZONE=Africa/Cairo
MARKET_DATA_PERIOD=1y
MARKET_DATA_INTERVAL=1d
MARKET_DATA_CACHE_MINUTES=30
MARKET_DATA_TIMEOUT_SECONDS=20
MARKET_DATA_MIN_CANDLES=200
ANALYSIS_COST_POINTS=50
ANALYSIS_DEFAULT_CAPITAL=150000
ANALYSIS_RISK_PER_TRADE=0.01
ANALYSIS_MAX_POSITION_VALUE=40000
ANALYSIS_ENGINE_VERSION=core-v1
```

TradingView هو المصدر الأساسي الحالي للشموع والسعر اللحظي، و`yfinance` fallback للشموع ومصدر للبيانات الأساسية. قبل الإطلاق العام يجب مراجعة التراخيص وشروط التخزين وإعادة العرض واعتماد مصدر رسمي أو تجاري مناسب.

## تقرير أفضل 10 للجلسة القادمة

يتم تشغيل المسح اليومي الساعة 5:00 مساءً بتوقيت القاهرة:

```bash
python -m app.jobs.generate_daily_top10
```

المهمة تتحقق داخليًا من:

- أن اليوم جلسة تداول فعلية من الأحد إلى الخميس.
- أن اليوم ليس ضمن `EGX_HOLIDAYS`.
- أن وقت التنفيذ وصل إلى الموعد المحدد.
- أن آخر شمعة لكل سهم تخص جلسة اليوم، وليست بيانات قديمة.
- أن السهم اجتاز حد التاريخ والسيولة وانتظام الحجم.
- أن المحركات أعادت `BUY` أو `WATCH`.

يتم ترتيب المرشحين حتميًا حسب التأهيل، القرار، الدرجة، الثقة، والسيولة. الـAI لا يختار الأسهم ولا يرتبها؛ يستخدم فقط لشرح أفضل 10 بعد اختيارهم، مع شرح ثابت عند تعطل مزود AI.

لو لم ينتج المسح 10 أسهم مؤهلة، لا يتم نشر تقرير جزئي ويُسجل فشل المسح للتدقيق.

مسارات المستخدم:

```text
GET  /api/v1/market/reports/latest/preview
POST /api/v1/market/reports/{report_id}/unlock
GET  /api/v1/market/reports/{report_id}
```

قواعد الفتح:

- الـPreview مجاني ولا يعرض أسماء أو تفاصيل الأسهم.
- فتح التقرير يكلف `100` نقطة = `1.00` عملة.
- نفس المستخدم لا يُخصم منه مرتين لنفس التقرير.
- الخصم وسجل الفتح يتمان داخل معاملة واحدة.
- التقرير الناقص أو غير الموجود لا يستهلك الرصيد.
- التقرير الكامل يظل مفتوحًا للمستخدم بعد الدفع.

أهم الإعدادات:

```text
EGX_HOLIDAYS=
DAILY_SCAN_HOUR=17
DAILY_SCAN_MINUTE=0
DAILY_SCAN_MAX_CONCURRENCY=4
DAILY_SCAN_MIN_AVERAGE_TURNOVER_EGP=1000000
DAILY_SCAN_MIN_NONZERO_VOLUME_RATIO=0.80
DAILY_REPORT_SIZE=10
DAILY_REPORT_COST_POINTS=100
```

تفاصيل التشغيل والصيانة موجودة في `docs/DAILY_TOP10_PIPELINE.md`.

## البريد الإلكتروني

في Development وTest، إذا لم يتم ضبط SMTP تُكتب رسالة تحذير في السجل بدل إرسال البريد. في Staging وProduction يجب ضبط:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_USE_TLS
```

لا تُعاد توكنات التأكيد أو استعادة كلمة المرور في استجابة الـAPI.

## المهاجرات

تشغيل أحدث مخطط:

```bash
alembic upgrade head
```

الرجوع Migration واحدة:

```bash
alembic downgrade -1
```

الرجوع إلى قاعدة فارغة ثم إعادة البناء:

```bash
alembic downgrade base
alembic upgrade head
```

إنشاء Migration جديدة بعد تعديل النماذج:

```bash
alembic revision --autogenerate -m "describe change"
```

يجب مراجعة ملف الـMigration الناتج قبل تشغيله أو دمجه.

## الاختبارات

```bash
pytest -q
ruff check .
```

## البيئات

القيم المدعومة لـ`APP_ENV`:

- `development`
- `test`
- `staging`
- `production`

في Staging وProduction:

- يجب أن يكون `SECRET_KEY` بطول 32 حرفًا على الأقل.
- يجب استخدام PostgreSQL.
- يجب ضبط SMTP.
- لا تُعرض Swagger أو OpenAPI للعامة افتراضيًا.

## الأسرار

لا تضع أي مفتاح حقيقي داخل الكود أو `.env.example`. تُحفظ أسرار الإنتاج في Secrets الخاصة بمنصة الاستضافة فقط.

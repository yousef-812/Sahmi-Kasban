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

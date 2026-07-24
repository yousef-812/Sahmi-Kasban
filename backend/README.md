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
- لا تُعرض Swagger أو OpenAPI للعامة افتراضيًا.

## الأسرار

لا تضع أي مفتاح حقيقي داخل الكود أو `.env.example`. تُحفظ أسرار الإنتاج في Secrets الخاصة بمنصة الاستضافة فقط.

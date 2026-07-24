# Sahmi Kasban — Implementation Log

هذا الملف هو السجل الدائم لكل أعمال التطوير التي يتم تنفيذها في المشروع. يتم تحديثه مع كل مرحلة أو تعديل مهم، ويجب ألا تُنفذ تغييرات جوهرية دون توثيقها هنا.

## قواعد السجل

- تُسجل التغييرات حسب التاريخ والمرحلة.
- يُذكر ما تم إنجازه والملفات المتأثرة والاختبارات المنفذة.
- تُذكر القرارات التقنية وأسبابها.
- تُذكر الأعمال المتبقية أو القيود المعروفة بوضوح.

---

## 2026-07-25 — المرحلة 0: تثبيت المتطلبات والبنية

**الحالة:** مكتملة وجاهزة للدمج عبر Pull Request رقم 3

### النطاق المعتمد

- تأسيس Backend مستقل باستخدام FastAPI.
- إعداد PostgreSQL وSQLAlchemy وAlembic.
- إعداد Development / Staging / Production.
- إنشاء Health API وفحص اتصال قاعدة البيانات.
- تعريف النماذج الأساسية التي ستُبنى عليها المراحل التالية.
- إعداد Docker Compose للتطوير المحلي.
- توسيع CI لفحص الـBackend والمهاجرات والاختبارات.
- عدم وضع أي أسرار حقيقية داخل الريبو.

### ما تم تنفيذه

#### بنية الـBackend

- إنشاء مشروع Python مستقل داخل `backend/`.
- إضافة نقطة تشغيل FastAPI في `backend/app/main.py`.
- إضافة API version prefix افتراضي `/api/v1`.
- إضافة Health endpoint وفحص مستقل لاتصال قاعدة البيانات.
- تعطيل Swagger وOpenAPI تلقائيًا في Production.
- تفعيل CORS فقط عند وجود قائمة Origins محددة؛ دون استخدام wildcard.

#### البيئات والأسرار

- إضافة إعدادات Development / Test / Staging / Production.
- إضافة `backend/.env.example` بدون أي أسرار حقيقية.
- منع تشغيل Staging أو Production إذا كان `SECRET_KEY` أقصر من 32 حرفًا.
- منع استخدام SQLite في Staging وProduction.
- إضافة متغيرات مزودي AI وبيانات السوق دون قيم سرية.
- تحديث `.gitignore` و`.dockerignore` لمنع ملفات البيئة وقواعد البيانات والتغطية من الدخول للريبو.

#### قاعدة البيانات

- إعداد SQLAlchemy 2 وقاعدة Declarative موحدة مع naming convention للقيود.
- إعداد Session factory وفحص `SELECT 1` لصحة الاتصال.
- إضافة Alembic وإعداد القراءة من `DATABASE_URL`.
- إنشاء Migration أولى قابلة للتشغيل والرجوع.

#### النماذج الأساسية

تم تعريف الجداول التالية:

- `users`
- `wallet_entries`
- `subscriptions`
- `market_reports`
- `market_report_items`
- `stock_analyses`
- `discussions`
- `prediction_verifications`

تم تثبيت الخطة المجانية داخل نموذج الاشتراك على:

- `300` نقطة أسبوعيًا = `3` عملات.
- الإعلانات مفعلة افتراضيًا.

تمت إضافة قيود تمنع:

- تكرار `transaction_id` في سجل العملات.
- تكرار رمز أو ترتيب داخل تقرير أفضل 10.
- خروج ترتيب التقرير عن 1 إلى 10.
- خروج درجات التحليل والتوقع عن النطاق المسموح.
- تكرار التحقق من نفس المناقشة.
- مكافآت توقع سالبة.

#### التشغيل المحلي

- إضافة `backend/Dockerfile`.
- إضافة `docker-compose.yml` لتشغيل PostgreSQL والـAPI.
- تشغيل migrations تلقائيًا عند بدء حاوية التطوير.
- إضافة `backend/README.md` بأوامر التشغيل والمهاجرات والاختبارات.

#### استراتيجية بيانات السوق

- إضافة `docs/MARKET_DATA_STRATEGY.md`.
- اعتماد واجهة مزود موحدة مستقبلًا بدل ربط المحركات بمزود مباشر.
- اعتبار TradingView مرشحًا أساسيًا وyfinance fallback مبدئيًا.
- اشتراط تقييم مزود رسمي أو تجاري مرخص قبل الإنتاج.
- اعتماد `Africa/Cairo` للجدولة بدل UTC ثابت.
- توثيق قواعد رفض البيانات الناقصة أو المتعارضة.

#### الاختبارات وCI

تمت إضافة اختبارات تغطي:

- Root endpoint.
- Health endpoint.
- Database health endpoint.
- قبول قاعدة محلية في Development.
- رفض الأسرار الضعيفة في Production.
- رفض SQLite في Production.
- تحليل قائمة CORS المفصولة بفواصل.
- تسجيل كل الجداول الأساسية.
- تثبيت 3 عملات أسبوعيًا للخطة المجانية.
- وجود unique constraint لمعرف عملية المحفظة.

تم تقسيم GitHub Actions إلى أربع وظائف مستقلة:

- `core-lint`: فحص تنسيق محركات التحليل والـAI.
- `core-tests`: compilation واختبارات المحركات.
- `backend-lint`: فحص تنسيق الـBackend وAlembic.
- `backend-tests`: اختبارات الـBackend على PostgreSQL 16 وتشغيل Alembic `upgrade → downgrade base → upgrade`.

### الملاحظات التي ظهرت أثناء CI وكيف عولجت

- ظهرت 7 مخالفات Ruff غير منطقية: ترتيب imports، type annotations مقتبسة، وسطران أطول من الحد.
- تم إصلاح مخالفة في `src/sahmi_kasban/ai/client.py` وست مخالفات في ملفات الـBackend والاختبارات.
- تم ضبط Ruff على اعتبار `app` حزمة first-party داخل مشروع الـBackend.
- تم اكتشاف أن تشغيل Ruff مباشرة عبر arguments الخاصة بالـAction كان غير مستقر للمسار الأساسي؛ تم اعتماد تثبيت Ruff عبر الـAction ثم تشغيل أمر `ruff check` صراحة.
- تمت إزالة صلاحية كتابة Pull Request وخطوات التعليقات التشخيصية المؤقتة بعد انتهاء التصحيح.

### نتيجة التحقق النهائية

نجح Workflow رقم `17`، Run ID `30133904672`، في جميع الوظائف الأربع:

- Core lint: ناجح.
- Core compilation and tests: ناجحة.
- Backend lint: ناجح.
- Backend compilation and tests: ناجحة.
- Alembic upgrade إلى أحدث مخطط: ناجح.
- Alembic downgrade إلى قاعدة فارغة: ناجح.
- Alembic upgrade مرة أخرى: ناجح.

### الملفات الرئيسية المضافة أو المعدلة

- `backend/pyproject.toml`
- `backend/.env.example`
- `backend/Dockerfile`
- `backend/README.md`
- `backend/app/`
- `backend/alembic.ini`
- `backend/alembic/`
- `backend/tests/`
- `docker-compose.yml`
- `docs/MARKET_DATA_STRATEGY.md`
- `.github/workflows/ci.yml`
- `.gitignore`
- `.dockerignore`
- `README.md`
- `IMPLEMENTATION_LOG.md`
- `src/sahmi_kasban/ai/client.py`

### القرارات التقنية

- الإبقاء على محركات التحليل الحالية كحزمة Python مستقلة في جذر الريبو.
- إنشاء تطبيق السيرفر داخل مجلد `backend/` حتى يظل الفصل واضحًا بين المحركات والـAPI.
- استخدام PostgreSQL في التشغيل الفعلي، مع SQLite داخل اختبارات الوحدة السريعة فقط.
- إدارة إعدادات التشغيل من متغيرات البيئة عبر `pydantic-settings`.
- استخدام Alembic كمصدر وحيد لتغييرات مخطط قاعدة البيانات.
- تخزين العملات كنقاط صحيحة؛ 100 نقطة تساوي عملة واحدة.
- عدم إنشاء الجداول تلقائيًا عند تشغيل FastAPI.

### الخطوة التالية بعد الدمج

المرحلة 1: الحسابات والملف الشخصي وWallet Ledger والتوزيع الأسبوعي للخطة المجانية.

# ملف ذاكرة مشروع Sahmi Kasban للشات الجديد

> هذا الملف مخصص لرفعه في أي شات جديد حتى يتم استكمال المشروع من نفس النقطة من دون إعادة شرح التاريخ السابق.  
> آخر تحديث: 2026-07-26

## الرسالة التي ترسلها في بداية الشات الجديد

انسخ هذه الجملة بعد رفع الملف:

> اقرأ ملف `PROJECT_MEMORY_HANDOFF.md` كاملًا، ثم افتح مستودع `yousef-812/Sahmi-Kasban` وراجع Draft PR #15 والفرع `agent/phase-6-community-core`. أكمل من قسم "الخطوة التالية" فقط. لا تدمج PR ولا تنتقل إلى المرحلة 7 إلا بعد اكتمال Flutter ونجاح CI النهائي. سجّل كل تعديل جديد داخل سجل المرحلة في الريبو.

---

## 1. هوية المشروع

- اسم المشروع: **Sahmi Kasban**.
- مستودع GitHub: `yousef-812/Sahmi-Kasban`.
- التطبيق: Flutter عربي موجه للبورصة المصرية.
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Alembic.
- Core analysis package: Python package باسم `sahmi_kasban`.
- مزود بيانات السوق الأساسي: TradingView WebSocket.
- fallback: yfinance/Yahoo عند الحاجة.
- AI: Open-WebUI وGroq من السيرفر فقط.
- المنطقة الزمنية التشغيلية: `Africa/Cairo`.
- المبدأ الأساسي: كل الخصومات والمكافآت والمراجعات الحساسة تتم على السيرفر، وليس داخل Flutter.

---

## 2. الحالة العامة للمراحل

المراحل المدمجة في `main`:

- المرحلة 0: البنية وFastAPI/PostgreSQL/CI.
- المرحلة 1: الحسابات والملف الشخصي والمحفظة والتوزيع الأسبوعي.
- المرحلة 2: بيانات EGX وتحليل سهم مدفوع.
- المرحلة 3: تقرير أفضل 10 للجلسة القادمة.
- المرحلة 4: تطبيق Flutter الأساسي.
- المرحلة 5: الإعلانات والاشتراكات والعملات.

المرحلة الحالية:

- **المرحلة 6 — المجتمع والمناقشات**.
- الفرع: `agent/phase-6-community-core`.
- PR: `#15 — Build Phase 6 community core`.
- الرابط: `https://github.com/yousef-812/Sahmi-Kasban/pull/15`.
- PR ما زال Draft ومفتوحًا وقابلًا للدمج تقنيًا، لكن لا يجب دمجه قبل اكتمال Flutter.

آخر حالة موثقة قبل ملفات التوثيق:

```text
Head: d790acc9089a7d34a0e9f9e1644c4808de520be1
Workflow: 30178050549
Result: success
```

نجح في:

- Repository lint.
- Core وBackend compile/Ruff/tests.
- PostgreSQL test database.
- Alembic upgrade/downgrade/rebuild.
- Flutter format/analyze/tests.
- Android debug APK.

تمت إضافة ملفين توثيقيين بعد ذلك على نفس الفرع:

- `IMPLEMENTATION_LOG_PHASE_6.md`
- `PROJECT_MEMORY_HANDOFF.md`

يجب مراجعة أحدث Workflow بعد آخر commit قبل أي دمج.

---

## 3. ما تم تنفيذه في المرحلة 6

### 3.1 إنشاء المناقشة والمحفظة

- تكلفة إرسال المناقشة: `50` نقطة = `0.5` عملة.
- يتم عمل Wallet Hold وقت الإرسال.
- القبول يؤكد الحجز بدل خصم جديد.
- الرفض يحرر الحجز ويعيد النقاط مرة واحدة فقط.
- كل عملية لها transaction ID فريد.
- نفس `submission_key` يعمل idempotently.
- نفس المحتوى بمفتاح مختلف يتم اكتشافه ببصمة SHA-256 ولا يخصم مرة أخرى.

### 3.2 قواعد المنع الثابتة

تم تنفيذ Regex وقواعد لمنع:

- أرقام الهواتف.
- بيانات التواصل.
- الروابط الخارجية.
- قنوات ومجموعات وتطبيقات خارجية.
- الإعلانات.
- الربح المضمون وعدم وجود خسارة.
- بعض أنماط الإساءة.

المحتوى الذي يفشل القواعد يرفض فورًا ويسترد الرصيد من دون استدعاء AI.

### 3.3 AI moderation

- يستخدم `SahmiAIService` الموجود في Core.
- يدعم Open-WebUI ثم Groq fallback.
- AI يراجع المحتوى ويستخرج توقعًا منظمًا.
- التوقع يتم تجميده وقت النشر ويحتوي على السهم والاتجاه والهدف والفترة والادعاءات وSHA-256 للنص.
- AI لا يحدد الرصيد أو المكافأة.
- عند فشل مزود AI:
  - لا يتم النشر.
  - لا يتم الخصم النهائي.
  - تظل المناقشة `pending_review`.
  - يظل الحجز موجودًا.
  - تسجل محاولة فاشلة للمراجعة اليدوية أو إعادة المحاولة.

### 3.4 الحماية من السبام

- حد أقصى `3` مناقشات خلال `15` دقيقة.
- حد أقصى `10` مناقشات خلال `24` ساعة.
- API يرجع `429` و`Retry-After` عند تجاوز الحد.
- يتم قفل صف المحفظة لحماية العدادات من الطلبات المتزامنة.

### 3.5 المجتمع

تم تنفيذ Backend APIs لـ:

- إنشاء مناقشة.
- عرض Feed المنشور.
- الفلترة حسب السهم.
- عرض تفاصيل المناقشة.
- صفحة مناقشاتي.
- الإبلاغ عن مناقشة.
- كتم مستخدم وإلغاء كتمه.
- إخفاء المكتومين من Feed.

### 3.6 الإدارة

صلاحية الإدارة تعتمد على:

```text
ADMIN_EMAILS=admin@example.com,other@example.com
```

تم تنفيذ:

- طابور المناقشات.
- قبول يدوي مع توقع منظم.
- رفض يدوي وإرجاع الحجز.
- إخفاء مناقشة منشورة.
- استعادة مناقشة مخفية.
- حظر مستخدم.
- إلغاء حظر مستخدم.
- إبطال جلسات المستخدم الموقوف عبر زيادة `auth_version`.
- رفض المناقشات المعلقة للمستخدم الموقوف وإعادة حجوزاتها.
- إخفاء منشوراته المنشورة.
- إغلاق البلاغات المفتوحة.
- Audit Logs للإدارة والمراجعة.

### 3.7 الاستئنافات

- المستخدم يستطيع استئناف مناقشة `rejected` أو `hidden` مرة واحدة.
- تكرار نفس الاستئناف يعمل idempotently.
- الإدارة تعرض طابور الاستئنافات وتقبل أو ترفض.
- قبول استئناف مناقشة مخفية يعيدها من دون خصم جديد.
- قبول استئناف مناقشة مرفوضة يحتاج توقعًا منظمًا ويخصم `50` نقطة عند النشر، لأن الرصيد الأصلي كان قد عاد للمستخدم.
- لا يمكن إعادة نشر محتوى لمستخدم موقوف.
- جميع القرارات مسجلة في Audit Events.

---

## 4. Migrations الحالية

```text
0006_community_core
0007_community_appeals
```

`0006` يضيف:

- حقول lifecycle للمناقشات.
- submission key.
- content fingerprint.
- wallet hold transaction ID.
- reports.
- user mutes.
- moderation events.
- admin events.

`0007` يضيف:

- discussion appeals.
- حالة القرار الإداري.
- transaction ID لإعادة النشر بعد الاستئناف.

لا يتم تعديل قاعدة البيانات يدويًا؛ استخدم Alembic فقط.

---

## 5. أهم الملفات الحالية

### Backend services

```text
backend/app/services/community.py
backend/app/services/community_ai.py
backend/app/services/community_safety.py
backend/app/services/community_admin.py
backend/app/services/community_appeals.py
backend/app/services/wallet.py
```

### API routes

```text
backend/app/api/routes/community.py
backend/app/api/routes/community_appeals.py
backend/app/api/routes/community_admin.py
backend/app/api/routes/community_admin_appeals.py
```

### Models and schemas

```text
backend/app/models/community.py
backend/app/models/entities.py
backend/app/schemas/community.py
```

### Tests

```text
backend/tests/test_community_service.py
backend/tests/test_community_api.py
backend/tests/test_community_ai.py
backend/tests/test_community_safety.py
backend/tests/test_community_admin.py
```

### Documentation

```text
IMPLEMENTATION_LOG_PHASE_6.md
PROJECT_MEMORY_HANDOFF.md
ROADMAP.md
```

---

## 6. أهم API endpoints

كل المسارات تحت `/api/v1`.

### User community

```text
POST   /community/discussions
GET    /community/discussions
GET    /community/discussions/mine
GET    /community/discussions/{discussion_id}
POST   /community/discussions/{discussion_id}/reports
PUT    /community/users/{user_id}/mute
DELETE /community/users/{user_id}/mute
POST   /community/discussions/{discussion_id}/appeals
GET    /community/appeals/mine
```

### Admin community

```text
GET  /admin/community/discussions
POST /admin/community/discussions/{discussion_id}/action
POST /admin/community/users/{user_id}/block
POST /admin/community/users/{user_id}/unblock
GET  /admin/community/appeals
POST /admin/community/appeals/{appeal_id}/resolve
```

---

## 7. قرارات مهمة لا تتغير من دون سبب موثق

1. Flutter لا يخصم أو يضيف رصيدًا بنفسه.
2. تكلفة المناقشة `50` نقطة.
3. الرفض النهائي لا يكلف المستخدم شيئًا.
4. فشل AI لا ينشر المحتوى تلقائيًا.
5. AI لا يقرر المكافآت أو الرصيد.
6. لا يتم تعديل التوقع المجمد بعد النشر.
7. أي إعادة إرسال يجب أن تكون idempotent.
8. أي إجراء إداري أو مالي يجب أن يكون قابلًا للتتبع.
9. المستخدم المكتوم يختفي من Feed الخاص بمن كتمه فقط.
10. المستخدم الموقوف لا يستطيع استخدام APIs التي تحتاج `CurrentUser` لأن حالته ليست `active`.
11. لا يتم دمج PR #15 قبل واجهات Flutter وCI النهائي.
12. لا تبدأ المرحلة 7 قبل دمج المرحلة 6 وتحديث ROADMAP.

---

## 8. الخطوة التالية — ابدأ من هنا

**لا تعيد بناء Backend المجتمع.**

ابدأ بمراجعة بنية Flutter الحالية على نفس الفرع، ثم نفذ بالترتيب:

1. Community models لقراءة Responses الحالية.
2. Community repository باستخدام API client الحالي وtoken refresh الحالي.
3. اختبارات parsing، pagination، أخطاء 409/422/429، و`Retry-After`.
4. صفحة Community Feed بالعربية وRTL.
5. فلتر السهم والتحديث والسحب لإعادة التحميل.
6. صفحة تفاصيل المناقشة.
7. نموذج إنشاء مناقشة مع:
   - اختيار السهم
   - العنوان
   - المحتوى
   - الفترة
   - تنبيه حجز `0.5` عملة
   - submission key ثابت للمحاولة لمنع الخصم المكرر
8. صفحة مناقشاتي وحالات:
   - pending review
   - published
   - rejected + reason
   - hidden
9. الإبلاغ والكتم وإلغاء الكتم.
10. واجهة إنشاء الاستئناف وعرض حالته.
11. تحديث الرصيد بعد كل عملية تغيره.
12. Widget/repository tests.
13. Flutter format + analyze + tests + Android debug APK.
14. تحديث `IMPLEMENTATION_LOG_PHASE_6.md` بنتيجة آخر Workflow.
15. تحديث PR #15 وإزالة Draft فقط بعد اكتمال كل ما سبق.

---

## 9. ما لا يزال غير مختبر على بيئة إنتاج

- AI provider live integration للمجتمع لم يتم اعتماده كاختبار إنتاج نهائي؛ الاختبارات الحالية تستخدم خدمات Fake/controlled.
- يجب ضبط `ADMIN_EMAILS` في البيئة الفعلية.
- مرحلة 5 ما زال لها اختبارا إطلاق إلزاميان:
  - شراء حقيقي عبر Google Play Internal Testing.
  - AdMob SSV حي وموقع من وحدة المشروع.
- TradingView العام مناسب للتطوير والتحقق الحالي، لكن مصدر بيانات مرخص يظل مطلوبًا قبل إطلاق تجاري جاد.

---

## 10. أوامر المراجعة المحلية المفيدة

من جذر المشروع:

```bash
git checkout agent/phase-6-community-core
git pull origin agent/phase-6-community-core
```

Backend:

```bash
cd backend
python -m compileall -q app tests alembic scripts reusable_data_fetcher.py
ruff check app tests alembic/env.py scripts reusable_data_fetcher.py --config pyproject.toml
pytest -q tests
python -m alembic upgrade head
```

Flutter:

```bash
cd mobile
flutter pub get
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
flutter build apk --debug
```

راجع المسارات الفعلية في workflow إذا اختلف اسم مجلد Flutter؛ لا تخمن ولا تنشئ مشروع Flutter جديدًا.

---

## 11. أسلوب العمل المطلوب في الشات الجديد

- افتح الملفات الفعلية قبل التعديل.
- نفذ على الفرع الحالي، وليس `main`.
- كل حزمة منطقية يجب أن يكون لها اختبارات.
- راقب GitHub Actions بعد كل مجموعة تغييرات مهمة.
- أصلح أي فشل قبل البناء فوقه.
- سجل القرارات والنتائج داخل `IMPLEMENTATION_LOG_PHASE_6.md`.
- لا تدّع نجاح اختبار لم يتم تشغيله.
- لا تضع مفاتيح أو بيانات حقيقية في Git.
- لا تدمج PR تلقائيًا قبل البوابة النهائية.

---

## 12. جملة الاستكمال السريعة

> نحن على Draft PR #15 في الفرع `agent/phase-6-community-core`. Backend المرحلة 6، الحجز، Regex، AI moderation، التوقع المجمد، rate limiting، المجتمع، الإدارة، الحظر، البلاغات، الكتم والاستئنافات منفذة ومختبرة. أحدث كود موثق كان أخضر بالكامل في workflow `30178050549`. المطلوب الآن هو Flutter community UI/repository/tests ثم CI نهائي وتوثيق ودمج، وبعدها فقط المرحلة 7.

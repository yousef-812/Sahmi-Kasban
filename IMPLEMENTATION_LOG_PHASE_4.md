# Sahmi Kasban — Phase 4 Implementation Log

## المرحلة

**المرحلة 4: تطبيق Flutter الأساسي**  
**الفرع:** `agent/flutter-core-app`  
**Pull Request:** #11  
**تاريخ البدء:** 2026-07-25  
**الحالة:** قيد التنفيذ — الدفعة التأسيسية ناجحة وبدأ استكمال تدفقات الحساب.

## الهدف

بناء تطبيق Flutter عربي يستهلك الـAPIs المنفذة في المراحل 1–3، مع الحفاظ على جميع العمليات الحساسة والمالية داخل السيرفر.

## قرارات البداية

- إنشاء التطبيق داخل `mobile/` لأن الريبو لم يكن يحتوي مشروع Flutter سابقًا.
- عدم استخدام code generation في الدفعة الأولى لتقليل التعقيد وتسريع التحقق.
- استخدام Riverpod لإدارة الحالة وGoRouter للتنقل.
- استخدام Dio للاتصال بالـBackend.
- تخزين Access وRefresh tokens في `flutter_secure_storage` بدل SharedPreferences.
- استخدام SharedPreferences فقط لحالة إكمال الـOnboarding.
- تمرير عنوان الـAPI بواسطة `--dart-define=API_BASE_URL=...` وعدم تثبيت عنوان إنتاج داخل الكود.
- تنفيذ تجديد تلقائي للـAccess Token عند `401` باستخدام Refresh Token دوار.
- تنفيذ Logout محلي حتى عند انقطاع الشبكة، حتى لا يبقى المستخدم محبوسًا داخل جلسة منتهية.

## ما تم تنفيذه في الدفعة الأولى

### التأسيس

- `mobile/pubspec.yaml`
- `mobile/analysis_options.yaml`
- نقطة تشغيل ProviderScope.
- Theme عربي Material 3.
- إعداد API base URL حسب بيئة البناء.
- CI مستقل لـFlutter يخزن الـSDK وPub Cache داخل Workspace الريبو.

### الشبكة والجلسة

- `TokenStore` آمن.
- `ApiClient` يضيف Bearer Token تلقائيًا.
- منع تكرار طلبات Refresh المتزامنة عبر Future مشتركة.
- تدوير Refresh Token وحفظ الزوج الجديد.
- إعادة الطلب الأصلي مرة واحدة فقط بعد التجديد.
- مسح التوكنات عند فشل التجديد.
- تحويل أخطاء Dio إلى `ApiException` موحدة.

### عقود البيانات

تمت مطابقة الموديلات مع Schemas الـBackend الحالية:

- Token pair.
- Registration result.
- User profile.
- Wallet summary.
- Market report preview.

### التدفقات والشاشات

- Splash.
- Onboarding من ثلاث صفحات.
- تسجيل حساب.
- تسجيل دخول.
- استعادة الجلسة المخزنة عند بدء التطبيق.
- Dashboard بأربع وجهات: الرئيسية، التحليل، المحفظة، وحسابي.
- تحميل الملف الشخصي والمحفظة ومقدمة أحدث تقرير.
- Refresh بالسحب.
- Logout.
- إخلاء مسؤولية ظاهر في الصفحة الرئيسية.

## تحديث ROADMAP

تم تحديث `ROADMAP.md` إلى النسخة `1.1` ليعكس الحالة الفعلية:

- المراحل 0 و1 و2 و3 مكتملة ومدمجة.
- المرحلة 4 قيد التنفيذ.
- Flutter application هو المكوّن الجاري تطويره.
- أزيلت العلامات القديمة التي كانت تعرض Backend وWallet Ledger والمسح اليومي كأعمال غير مكتملة.

## ملاحظات CI التي ظهرت وعولجت

- فشل أول فحص Flutter في خطوة التنسيق فقط.
- اتضح أن Formatter المؤقت شُغل قبل `flutter pub get`، بينما فحص CI شُغل بعد تحديد Language Version للمشروع؛ فنتج تنسيقان مختلفان.
- تم تثبيت الترتيب الصحيح: `flutter pub get` ثم استخدام Dart المرفق بنفس Flutter SDK للتنسيق والفحص.
- تم حذف وظائف Autofix المؤقتة بعد تطبيق التنسيق.
- بقي Workflow بصلاحية قراءة فقط وبثلاث وظائف دائمة: Repository lint، Repository tests، Flutter checks.

## نتيجة التحقق للدفعة التأسيسية

نجح Workflow Run ID `30163540791` على commit `bc46d96f1f484265b603f1a8291acae42f82a5c5`:

- Flutter SDK installation: ناجح.
- Flutter package resolution: ناجح.
- Flutter formatting: ناجح.
- Flutter analyze: ناجح دون مخالفات.
- Flutter tests: ناجحة.
- Core وBackend lint: ناجح.
- Core وBackend tests: ناجحة.
- PostgreSQL 16: ناجح.
- Alembic upgrade / downgrade / rebuild: ناجحة.

## الأعمال المتبقية داخل المرحلة 4

- إنشاء ملفات Android وiOS النهائية.
- تأكيد البريد وإعادة إرسال رسالة التأكيد — قيد التنفيذ الآن.
- نسيان وإعادة تعيين كلمة المرور — قيد التنفيذ الآن.
- تعديل الملف الشخصي واختيار Avatar.
- سجل المحفظة مع pagination.
- البحث في رموز EGX.
- تشغيل تحليل سهم وعرض التقرير الكامل.
- فتح تقرير أفضل 10 وعرض عناصره دون خصم مكرر.
- معالجة حالات Offline وإعادة المحاولة الآمنة.
- اختبارات Widget وRepository وToken refresh.
- استكمال التصميم البصري والأيقونات وشاشة الإقلاع الأصلية.

## بوابة الدمج

لن تُدمج المرحلة قبل نجاح:

- `dart format --set-exit-if-changed`.
- `flutter analyze`.
- `flutter test`.
- مراجعة عدم وجود أسرار أو عنوان إنتاج ثابت.
- اختبار تدفق الجلسة والتجديد والخروج.
- اختبار رحلة المستخدم من التسجيل حتى فتح تقرير أو تنفيذ تحليل.
- تحديث `ROADMAP.md` بحالة المرحلة النهائية.

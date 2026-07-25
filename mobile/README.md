# Sahmi Kasban Mobile

تطبيق Flutter العربي الخاص بمشروع سهمي كسبان.

## ما تم تنفيذه في المرحلة 4

- Splash أصلي وFlutter Splash بهوية سهمي كسبان.
- Onboarding محفوظ محليًا.
- التسجيل والدخول وتأكيد البريد وإعادة إرسال رسالة التأكيد.
- نسيان وإعادة تعيين كلمة المرور.
- تخزين Access وRefresh tokens في `flutter_secure_storage`.
- تدوير Refresh Token وتجديد Access Token تلقائيًا عند `401`.
- مشاركة عملية Refresh واحدة بين الطلبات المتزامنة.
- حماية التنقل حسب حالة الجلسة.
- تعديل الاسم واختيار واحدة من 12 صورة رمزية WebP مضغوطة.
- عرض الرصيد وسجل المحفظة مع Pagination.
- البحث في Registry أسهم EGX.
- تشغيل تحليل سهم مدفوع وعرض النتيجة.
- فتح تقرير أفضل 10 وعرض عناصره دون خصم مكرر.
- رسائل أخطاء واضحة وRefresh وإعادة محاولة آمنة.
- Android وiOS projects وLauncher icons وNative splash.

## المنصات والهوية

- Android application ID: `com.sahmikasban.sahmi_kasban_mobile`.
- اسم التطبيق الظاهر: «سهمي كسبان».
- أيقونات Android وiOS مولدة داخل مجلدات المنصات الرسمية.
- أصل الشعار عالي الدقة:

```text
assets/branding/app_icon.png
```

- الصور الرمزية:

```text
assets/avatars/avatar_01.webp
...
assets/avatars/avatar_12.webp
```

## التشغيل

### Android Emulator مع Backend محلي

```bash
cd mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

يسمح Android بالـHTTP المحلي في **Debug manifest فقط**. نسخة الإنتاج لا تسمح بـCleartext traffic.

### جهاز حقيقي أو iOS

استخدم Backend بعنوان HTTPS يمكن للجهاز الوصول إليه:

```bash
flutter run --dart-define=API_BASE_URL=https://api.example.com
```

عنوان الإنتاج يمرر من إعدادات البناء ولا يثبت داخل الكود.

## الفحص

```bash
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
```

يغطي الاختبار الحالي:

- Parsing لعقود الحساب والمحفظة والتحليل والتقرير.
- دورة التخزين الآمن للتوكنات.
- عدم إضافة Authorization للطلبات العامة.
- تدوير التوكن وعملية Refresh واحدة للطلبات المتزامنة.
- Registry الصور الرمزية.
- Widget smoke test لعرض بيانات التحليل.

## قواعد الأمان المالي في الواجهة

- زر التحليل أو فتح التقرير يتعطل أثناء الطلب.
- يظهر تأكيد التكلفة قبل العملية.
- لا تعتمد الواجهة على نفسها لمنع الخصم المكرر؛ السيرفر هو المرجع النهائي.
- إذا ضاع رد الشبكة بعد نجاح العملية، إعادة الطلب تعتمد على Cache/Unlock idempotency في السيرفر ولا تكرر الخصم.
- Logout يمسح التوكنات محليًا حتى عند تعذر الاتصال بالسيرفر.

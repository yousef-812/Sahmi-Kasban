# Project Structure & Contents: `mobile`

## Folder Tree

```
mobile/
├── android
│   ├── app
│   │   ├── src
│   │   │   ├── debug
│   │   │   │   └── AndroidManifest.xml
│   │   │   ├── main
│   │   │   │   ├── java
│   │   │   │   │   └── io
│   │   │   │   │       └── flutter
│   │   │   │   │           └── plugins
│   │   │   │   │               └── GeneratedPluginRegistrant.java
│   │   │   │   ├── kotlin
│   │   │   │   │   └── com
│   │   │   │   │       └── sahmikasban
│   │   │   │   │           └── sahmi_kasban_mobile
│   │   │   │   │               └── MainActivity.kt
│   │   │   │   ├── res
│   │   │   │   │   ├── drawable
│   │   │   │   │   │   ├── launch_background.xml
│   │   │   │   │   │   └── launch_logo.png
│   │   │   │   │   ├── drawable-v21
│   │   │   │   │   │   ├── launch_background.xml
│   │   │   │   │   │   └── launch_logo.png
│   │   │   │   │   ├── mipmap-hdpi
│   │   │   │   │   │   └── ic_launcher.png
│   │   │   │   │   ├── mipmap-mdpi
│   │   │   │   │   │   └── ic_launcher.png
│   │   │   │   │   ├── mipmap-xhdpi
│   │   │   │   │   │   └── ic_launcher.png
│   │   │   │   │   ├── mipmap-xxhdpi
│   │   │   │   │   │   └── ic_launcher.png
│   │   │   │   │   ├── mipmap-xxxhdpi
│   │   │   │   │   │   └── ic_launcher.png
│   │   │   │   │   ├── values
│   │   │   │   │   │   └── styles.xml
│   │   │   │   │   └── values-night
│   │   │   │   │       └── styles.xml
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── profile
│   │   │       └── AndroidManifest.xml
│   │   └── build.gradle.kts
│   ├── gradle
│   │   └── wrapper
│   │       ├── gradle-wrapper.jar
│   │       └── gradle-wrapper.properties
│   ├── build.gradle.kts
│   ├── gradle.properties
│   ├── gradlew
│   ├── gradlew.bat
│   ├── local.properties
│   └── settings.gradle.kts
├── assets
│   ├── avatars
│   │   ├── avatar_01.webp
│   │   ├── avatar_02.webp
│   │   ├── avatar_03.webp
│   │   ├── avatar_04.webp
│   │   ├── avatar_05.webp
│   │   ├── avatar_06.webp
│   │   ├── avatar_07.webp
│   │   ├── avatar_08.webp
│   │   ├── avatar_09.webp
│   │   ├── avatar_10.webp
│   │   ├── avatar_11.webp
│   │   └── avatar_12.webp
│   └── branding
│       ├── app_icon.png
│       └── splash_symbol.png
├── ios
│   ├── Flutter
│   │   ├── ephemeral
│   │   │   ├── Packages
│   │   │   │   └── FlutterGeneratedPluginSwiftPackage
│   │   │   │       ├── Sources
│   │   │   │       │   └── FlutterGeneratedPluginSwiftPackage
│   │   │   │       │       └── FlutterGeneratedPluginSwiftPackage.swift
│   │   │   │       └── Package.swift
│   │   │   ├── flutter_lldb_helper.py
│   │   │   ├── flutter_lldbinit
│   │   │   └── flutter_native_integration.env
│   │   ├── AppFrameworkInfo.plist
│   │   ├── Debug.xcconfig
│   │   ├── flutter_export_environment.sh
│   │   ├── Generated.xcconfig
│   │   └── Release.xcconfig
│   ├── Runner
│   │   ├── Assets.xcassets
│   │   │   ├── AppIcon.appiconset
│   │   │   │   ├── Contents.json
│   │   │   │   ├── Icon-App-1024x1024@1x.png
│   │   │   │   ├── Icon-App-20x20@1x.png
│   │   │   │   ├── Icon-App-20x20@2x.png
│   │   │   │   ├── Icon-App-20x20@3x.png
│   │   │   │   ├── Icon-App-29x29@1x.png
│   │   │   │   ├── Icon-App-29x29@2x.png
│   │   │   │   ├── Icon-App-29x29@3x.png
│   │   │   │   ├── Icon-App-40x40@1x.png
│   │   │   │   ├── Icon-App-40x40@2x.png
│   │   │   │   ├── Icon-App-40x40@3x.png
│   │   │   │   ├── Icon-App-60x60@2x.png
│   │   │   │   ├── Icon-App-60x60@3x.png
│   │   │   │   ├── Icon-App-76x76@1x.png
│   │   │   │   ├── Icon-App-76x76@2x.png
│   │   │   │   └── Icon-App-83.5x83.5@2x.png
│   │   │   └── LaunchImage.imageset
│   │   │       ├── Contents.json
│   │   │       ├── LaunchImage.png
│   │   │       ├── LaunchImage@2x.png
│   │   │       ├── LaunchImage@3x.png
│   │   │       └── README.md
│   │   ├── Base.lproj
│   │   │   ├── LaunchScreen.storyboard
│   │   │   └── Main.storyboard
│   │   ├── AppDelegate.swift
│   │   ├── GeneratedPluginRegistrant.h
│   │   ├── GeneratedPluginRegistrant.m
│   │   ├── Info.plist
│   │   ├── Runner-Bridging-Header.h
│   │   └── SceneDelegate.swift
│   ├── Runner.xcodeproj
│   │   ├── project.xcworkspace
│   │   │   ├── xcshareddata
│   │   │   │   ├── IDEWorkspaceChecks.plist
│   │   │   │   └── WorkspaceSettings.xcsettings
│   │   │   └── contents.xcworkspacedata
│   │   ├── xcshareddata
│   │   │   └── xcschemes
│   │   │       └── Runner.xcscheme
│   │   └── project.pbxproj
│   ├── Runner.xcworkspace
│   │   ├── xcshareddata
│   │   │   ├── IDEWorkspaceChecks.plist
│   │   │   └── WorkspaceSettings.xcsettings
│   │   └── contents.xcworkspacedata
│   └── RunnerTests
│       └── RunnerTests.swift
├── lib
│   ├── app
│   │   ├── app.dart
│   │   ├── router.dart
│   │   └── theme.dart
│   ├── core
│   │   ├── config
│   │   │   ├── app_config.dart
│   │   │   └── demo_mode.dart
│   │   ├── network
│   │   │   ├── api_client.dart
│   │   │   ├── api_exception.dart
│   │   │   └── token_store.dart
│   │   ├── observability
│   │   │   └── app_observability.dart
│   │   ├── ui
│   │   │   └── app_notice.dart
│   │   └── avatar_assets.dart
│   ├── data
│   │   └── backend_repository.dart
│   ├── domain
│   │   └── models.dart
│   ├── features
│   │   ├── admin
│   │   │   ├── admin_dashboard_screen.dart
│   │   │   ├── admin_models.dart
│   │   │   ├── admin_providers.dart
│   │   │   ├── admin_repository.dart
│   │   │   ├── admin_wallet_credit_screen.dart
│   │   │   ├── historical_replay_control_screen.dart
│   │   │   ├── historical_replay_models.dart
│   │   │   ├── historical_replay_providers.dart
│   │   │   └── historical_replay_screen.dart
│   │   ├── auth
│   │   │   ├── account_recovery_screens.dart
│   │   │   ├── auth_screens.dart
│   │   │   └── session_controller.dart
│   │   ├── bootstrap
│   │   │   └── splash_screen.dart
│   │   ├── community
│   │   │   ├── community_create_screen.dart
│   │   │   ├── community_detail_screen.dart
│   │   │   ├── community_feed_tab.dart
│   │   │   ├── community_models.dart
│   │   │   ├── community_providers.dart
│   │   │   ├── community_repository.dart
│   │   │   ├── my_discussions_screen.dart
│   │   │   ├── prediction_models.dart
│   │   │   ├── prediction_providers.dart
│   │   │   ├── prediction_repository.dart
│   │   │   └── prediction_verification_card.dart
│   │   ├── home
│   │   │   └── dashboard_screen.dart
│   │   ├── labs
│   │   │   ├── labs_models.dart
│   │   │   ├── labs_providers.dart
│   │   │   ├── labs_repository.dart
│   │   │   └── labs_screen.dart
│   │   ├── market
│   │   │   ├── market_quotes_providers.dart
│   │   │   ├── stock_analysis_report.dart
│   │   │   ├── stock_analysis_screen.dart
│   │   │   ├── stock_analysis_tab.dart
│   │   │   ├── stock_comparison_models.dart
│   │   │   ├── stock_comparison_repository.dart
│   │   │   ├── stock_comparison_screen.dart
│   │   │   ├── stock_detail_screen.dart
│   │   │   ├── stock_quote_card.dart
│   │   │   └── stocks_screen.dart
│   │   ├── monetization
│   │   │   ├── free_plan_ads.dart
│   │   │   ├── monetization_controller.dart
│   │   │   ├── monetization_models.dart
│   │   │   ├── monetization_page.dart
│   │   │   ├── monetization_repository.dart
│   │   │   ├── monetization_screen.dart
│   │   │   ├── plan_banner_ad.dart
│   │   │   └── rewarded_ad_gateway.dart
│   │   ├── notifications
│   │   │   ├── notification_messaging.dart
│   │   │   ├── notification_messaging_shell.dart
│   │   │   ├── notification_models.dart
│   │   │   ├── notification_providers.dart
│   │   │   ├── notification_repository.dart
│   │   │   └── notification_screen.dart
│   │   ├── onboarding
│   │   │   ├── onboarding_controller.dart
│   │   │   └── onboarding_screen.dart
│   │   ├── performance
│   │   │   ├── performance_admin_screen.dart
│   │   │   ├── performance_models.dart
│   │   │   ├── performance_providers.dart
│   │   │   ├── performance_report_screen.dart
│   │   │   ├── performance_repository.dart
│   │   │   ├── performance_screen.dart
│   │   │   └── performance_widgets.dart
│   │   ├── profile
│   │   │   └── profile_edit_screen.dart
│   │   ├── reports
│   │   │   ├── market_report_screen.dart
│   │   │   ├── report_providers.dart
│   │   │   └── reports_screen.dart
│   │   └── wallet
│   │       ├── wallet_history_screen.dart
│   │       └── wallet_providers.dart
│   ├── widgets
│   │   └── structured_data_card.dart
│   └── main.dart
├── test
│   ├── core
│   │   └── config
│   │       └── app_config_test.dart
│   ├── features
│   │   └── market
│   │       └── stock_analysis_report_test.dart
│   ├── api_client_test.dart
│   ├── app_observability_test.dart
│   ├── community_models_test.dart
│   ├── community_repository_test.dart
│   ├── community_widgets_test.dart
│   ├── domain_models_test.dart
│   ├── historical_replay_models_test.dart
│   ├── labs_models_test.dart
│   ├── market_report_screen_test.dart
│   ├── monetization_models_test.dart
│   ├── monetization_plan_features_test.dart
│   ├── performance_models_test.dart
│   ├── performance_presentation_test.dart
│   ├── phase4_models_test.dart
│   ├── phase8_models_test.dart
│   ├── prediction_models_test.dart
│   ├── prediction_repository_test.dart
│   ├── prediction_widgets_test.dart
│   ├── stock_comparison_and_ads_test.dart
│   ├── token_store_test.dart
│   ├── wallet_history_screen_test.dart
│   ├── widget_smoke_test.dart
│   └── workmanager_manifest_test.dart
├── analysis_options.yaml
├── DEMO_BUILD.md
├── pubspec.lock
├── pubspec.yaml
└── README.md
```

---

## File Contents

### File: `DEMO_BUILD.md`

```md
# Demo preview build

This branch builds the Android preview with `DEMO_MODE=true`, providing an automatic local demo session without production credentials.

```

---

### File: `README.md`

```md
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

```

---

### File: `analysis_options.yaml`

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  exclude:
    - build/**
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true

linter:
  rules:
    avoid_print: true
    prefer_final_locals: true
    use_super_parameters: true

```

---

### File: `pubspec.lock`

```lock
# Generated by pub
# See https://dart.dev/tools/pub/glossary#lockfile
packages:
  _flutterfire_internals:
    dependency: transitive
    description:
      name: _flutterfire_internals
      sha256: ff0a84a2734d9e1089f8aedd5c0af0061b82fb94e95260d943404e0ef2134b11
      url: "https://pub.dev"
    source: hosted
    version: "1.3.59"
  args:
    dependency: transitive
    description:
      name: args
      sha256: d0481093c50b1da8910eb0bb301626d4d8eb7284aa739614d2b394ee09e3ea04
      url: "https://pub.dev"
    source: hosted
    version: "2.7.0"
  async:
    dependency: transitive
    description:
      name: async
      sha256: e2eb0491ba5ddb6177742d2da23904574082139b07c1e33b8503b9f46f3e1a37
      url: "https://pub.dev"
    source: hosted
    version: "2.13.1"
  boolean_selector:
    dependency: transitive
    description:
      name: boolean_selector
      sha256: "8aab1771e1243a5063b8b0ff68042d67334e3feab9e95b9490f9a6ebf73b42ea"
      url: "https://pub.dev"
    source: hosted
    version: "2.1.2"
  characters:
    dependency: transitive
    description:
      name: characters
      sha256: faf38497bda5ead2a8c7615f4f7939df04333478bf32e4173fcb06d428b5716b
      url: "https://pub.dev"
    source: hosted
    version: "1.4.1"
  clock:
    dependency: transitive
    description:
      name: clock
      sha256: fddb70d9b5277016c77a80201021d40a2247104d9f4aa7bab7157b7e3f05b84b
      url: "https://pub.dev"
    source: hosted
    version: "1.1.2"
  code_assets:
    dependency: transitive
    description:
      name: code_assets
      sha256: bf394f466ba9205f1812a0433b392d6af280f155f56651eda7c18cc32ed493b8
      url: "https://pub.dev"
    source: hosted
    version: "1.2.1"
  collection:
    dependency: transitive
    description:
      name: collection
      sha256: "2f5709ae4d3d59dd8f7cd309b4e023046b57d8a6c82130785d2b0e5868084e76"
      url: "https://pub.dev"
    source: hosted
    version: "1.19.1"
  crypto:
    dependency: transitive
    description:
      name: crypto
      sha256: c8ea0233063ba03258fbcf2ca4d6dadfefe14f02fab57702265467a19f27fadf
      url: "https://pub.dev"
    source: hosted
    version: "3.0.7"
  cupertino_icons:
    dependency: "direct main"
    description:
      name: cupertino_icons
      sha256: "41e005c33bd814be4d3096aff55b1908d419fde52ca656c8c47719ec745873cd"
      url: "https://pub.dev"
    source: hosted
    version: "1.0.9"
  dio:
    dependency: "direct main"
    description:
      name: dio
      sha256: "0df44ebba85e503958eb75d07eedd3c86275a58c1d3eda2f2ce8f0a2c3abbb3c"
      url: "https://pub.dev"
    source: hosted
    version: "5.11.0"
  dio_web_adapter:
    dependency: transitive
    description:
      name: dio_web_adapter
      sha256: "0786d0b7295a373de356fc0af4f6f1d0ab2844ed31b19dfc5e7556b70e24212c"
      url: "https://pub.dev"
    source: hosted
    version: "2.2.1"
  fake_async:
    dependency: transitive
    description:
      name: fake_async
      sha256: "5368f224a74523e8d2e7399ea1638b37aecfca824a3cc4dfdf77bf1fa905ac44"
      url: "https://pub.dev"
    source: hosted
    version: "1.3.3"
  ffi:
    dependency: transitive
    description:
      name: ffi
      sha256: "6d7fd89431262d8f3125e81b50d3847a091d846eafcd4fdb88dd06f36d705a45"
      url: "https://pub.dev"
    source: hosted
    version: "2.2.0"
  file:
    dependency: transitive
    description:
      name: file
      sha256: a3b4f84adafef897088c160faf7dfffb7696046cb13ae90b508c2cbc95d3b8d4
      url: "https://pub.dev"
    source: hosted
    version: "7.0.1"
  firebase_core:
    dependency: "direct main"
    description:
      name: firebase_core
      sha256: "7be63a3f841fc9663342f7f3a011a42aef6a61066943c90b1c434d79d5c995c5"
      url: "https://pub.dev"
    source: hosted
    version: "3.15.2"
  firebase_core_platform_interface:
    dependency: transitive
    description:
      name: firebase_core_platform_interface
      sha256: "0ecda14c1bfc9ed8cac303dd0f8d04a320811b479362a9a4efb14fd331a473ce"
      url: "https://pub.dev"
    source: hosted
    version: "6.0.3"
  firebase_core_web:
    dependency: transitive
    description:
      name: firebase_core_web
      sha256: "0ed0dc292e8f9ac50992e2394e9d336a0275b6ae400d64163fdf0a8a8b556c37"
      url: "https://pub.dev"
    source: hosted
    version: "2.24.1"
  firebase_messaging:
    dependency: "direct main"
    description:
      name: firebase_messaging
      sha256: "60be38574f8b5658e2f22b7e311ff2064bea835c248424a383783464e8e02fcc"
      url: "https://pub.dev"
    source: hosted
    version: "15.2.10"
  firebase_messaging_platform_interface:
    dependency: transitive
    description:
      name: firebase_messaging_platform_interface
      sha256: "685e1771b3d1f9c8502771ccc9f91485b376ffe16d553533f335b9183ea99754"
      url: "https://pub.dev"
    source: hosted
    version: "4.6.10"
  firebase_messaging_web:
    dependency: transitive
    description:
      name: firebase_messaging_web
      sha256: "0d1be17bc89ed3ff5001789c92df678b2e963a51b6fa2bdb467532cc9dbed390"
      url: "https://pub.dev"
    source: hosted
    version: "3.10.10"
  fixnum:
    dependency: transitive
    description:
      name: fixnum
      sha256: b6dc7065e46c974bc7c5f143080a6764ec7a4be6da1285ececdc37be96de53be
      url: "https://pub.dev"
    source: hosted
    version: "1.1.1"
  flutter:
    dependency: "direct main"
    description: flutter
    source: sdk
    version: "0.0.0"
  flutter_lints:
    dependency: "direct dev"
    description:
      name: flutter_lints
      sha256: "5398f14efa795ffb7a33e9b6a08798b26a180edac4ad7db3f231e40f82ce11e1"
      url: "https://pub.dev"
    source: hosted
    version: "5.0.0"
  flutter_riverpod:
    dependency: "direct main"
    description:
      name: flutter_riverpod
      sha256: "9532ee6db4a943a1ed8383072a2e3eeda041db5657cdf6d2acecf3c21ecbe7e1"
      url: "https://pub.dev"
    source: hosted
    version: "2.6.1"
  flutter_secure_storage:
    dependency: "direct main"
    description:
      name: flutter_secure_storage
      sha256: "9cad52d75ebc511adfae3d447d5d13da15a55a92c9410e50f67335b6d21d16ea"
      url: "https://pub.dev"
    source: hosted
    version: "9.2.4"
  flutter_secure_storage_linux:
    dependency: transitive
    description:
      name: flutter_secure_storage_linux
      sha256: be76c1d24a97d0b98f8b54bce6b481a380a6590df992d0098f868ad54dc8f688
      url: "https://pub.dev"
    source: hosted
    version: "1.2.3"
  flutter_secure_storage_macos:
    dependency: transitive
    description:
      name: flutter_secure_storage_macos
      sha256: "6c0a2795a2d1de26ae202a0d78527d163f4acbb11cde4c75c670f3a0fc064247"
      url: "https://pub.dev"
    source: hosted
    version: "3.1.3"
  flutter_secure_storage_platform_interface:
    dependency: transitive
    description:
      name: flutter_secure_storage_platform_interface
      sha256: cf91ad32ce5adef6fba4d736a542baca9daf3beac4db2d04be350b87f69ac4a8
      url: "https://pub.dev"
    source: hosted
    version: "1.1.2"
  flutter_secure_storage_web:
    dependency: transitive
    description:
      name: flutter_secure_storage_web
      sha256: f4ebff989b4f07b2656fb16b47852c0aab9fed9b4ec1c70103368337bc1886a9
      url: "https://pub.dev"
    source: hosted
    version: "1.2.1"
  flutter_secure_storage_windows:
    dependency: transitive
    description:
      name: flutter_secure_storage_windows
      sha256: b20b07cb5ed4ed74fc567b78a72936203f587eba460af1df11281c9326cd3709
      url: "https://pub.dev"
    source: hosted
    version: "3.1.2"
  flutter_test:
    dependency: "direct dev"
    description: flutter
    source: sdk
    version: "0.0.0"
  flutter_web_plugins:
    dependency: transitive
    description: flutter
    source: sdk
    version: "0.0.0"
  go_router:
    dependency: "direct main"
    description:
      name: go_router
      sha256: f02fd7d2a4dc512fec615529824fdd217fecb3a3d3de68360293a551f21634b3
      url: "https://pub.dev"
    source: hosted
    version: "14.8.1"
  google_mobile_ads:
    dependency: "direct main"
    description:
      name: google_mobile_ads
      sha256: "6029f6c48bc9b6b47767ddbb4847683048a2f006d418c871bd93c5eb6a8e5c3c"
      url: "https://pub.dev"
    source: hosted
    version: "9.0.0"
  hooks:
    dependency: transitive
    description:
      name: hooks
      sha256: "9a62a50b50b769a737bc0a8ff381f333529df3ab746b2f6b02e83760231455ba"
      url: "https://pub.dev"
    source: hosted
    version: "2.0.2"
  http:
    dependency: transitive
    description:
      name: http
      sha256: "87721a4a50b19c7f1d49001e51409bddc46303966ce89a65af4f4e6004896412"
      url: "https://pub.dev"
    source: hosted
    version: "1.6.0"
  http_parser:
    dependency: transitive
    description:
      name: http_parser
      sha256: "178d74305e7866013777bab2c3d8726205dc5a4dd935297175b19a23a2e66571"
      url: "https://pub.dev"
    source: hosted
    version: "4.1.2"
  in_app_purchase:
    dependency: "direct main"
    description:
      name: in_app_purchase
      sha256: "0e9510b80b0074e89ab0a8e0fc901439b779dc9ae575ab8d419253c6e1627716"
      url: "https://pub.dev"
    source: hosted
    version: "3.3.0"
  in_app_purchase_android:
    dependency: transitive
    description:
      name: in_app_purchase_android
      sha256: c04e2cad0470fc868cb0ea06477648f003220b1b6612909db83528ca83ac0905
      url: "https://pub.dev"
    source: hosted
    version: "0.5.2"
  in_app_purchase_platform_interface:
    dependency: transitive
    description:
      name: in_app_purchase_platform_interface
      sha256: "0b0076cac8ce4fa7048f01e76af8b123aeb6a7c4e0dea2a5206d6664454f3e36"
      url: "https://pub.dev"
    source: hosted
    version: "1.4.1"
  in_app_purchase_storekit:
    dependency: transitive
    description:
      name: in_app_purchase_storekit
      sha256: "702a23c3d2ddc177b075d521d264900e82f01663881e4ef3ce17775de298c0e3"
      url: "https://pub.dev"
    source: hosted
    version: "0.4.11"
  intl:
    dependency: "direct main"
    description:
      name: intl
      sha256: "1ca20c894b1717686a2319b8548763d812bc0aabdac580420a44c5178c57a867"
      url: "https://pub.dev"
    source: hosted
    version: "0.20.3"
  jni:
    dependency: transitive
    description:
      name: jni
      sha256: d2c361082d554d4593c3012e26f6b188f902acd291330f13d6427641a92b3da1
      url: "https://pub.dev"
    source: hosted
    version: "0.14.2"
  js:
    dependency: transitive
    description:
      name: js
      sha256: f2c445dce49627136094980615a031419f7f3eb393237e4ecd97ac15dea343f3
      url: "https://pub.dev"
    source: hosted
    version: "0.6.7"
  json_annotation:
    dependency: transitive
    description:
      name: json_annotation
      sha256: "2a743920d81b7910627f68ee2c9ac1fc0bfee32b9fc3403587d7c6791ca12f80"
      url: "https://pub.dev"
    source: hosted
    version: "4.12.0"
  leak_tracker:
    dependency: transitive
    description:
      name: leak_tracker
      sha256: "33e2e26bdd85a0112ec15400c8cbffea70d0f9c3407491f672a2fad47915e2de"
      url: "https://pub.dev"
    source: hosted
    version: "11.0.2"
  leak_tracker_flutter_testing:
    dependency: transitive
    description:
      name: leak_tracker_flutter_testing
      sha256: "1dbc140bb5a23c75ea9c4811222756104fbcd1a27173f0c34ca01e16bea473c1"
      url: "https://pub.dev"
    source: hosted
    version: "3.0.10"
  leak_tracker_testing:
    dependency: transitive
    description:
      name: leak_tracker_testing
      sha256: "8d5a2d49f4a66b49744b23b018848400d23e54caf9463f4eb20df3eb8acb2eb1"
      url: "https://pub.dev"
    source: hosted
    version: "3.0.2"
  lints:
    dependency: transitive
    description:
      name: lints
      sha256: c35bb79562d980e9a453fc715854e1ed39e24e7d0297a880ef54e17f9874a9d7
      url: "https://pub.dev"
    source: hosted
    version: "5.1.1"
  logging:
    dependency: transitive
    description:
      name: logging
      sha256: c8245ada5f1717ed44271ed1c26b8ce85ca3228fd2ffdb75468ab01979309d61
      url: "https://pub.dev"
    source: hosted
    version: "1.3.0"
  matcher:
    dependency: transitive
    description:
      name: matcher
      sha256: dc0b7dc7651697ea4ff3e69ef44b0407ea32c487a39fff6a4004fa585e901861
      url: "https://pub.dev"
    source: hosted
    version: "0.12.19"
  material_color_utilities:
    dependency: transitive
    description:
      name: material_color_utilities
      sha256: "9c337007e82b1889149c82ed242ed1cb24a66044e30979c44912381e9be4c48b"
      url: "https://pub.dev"
    source: hosted
    version: "0.13.0"
  meta:
    dependency: transitive
    description:
      name: meta
      sha256: "1741988757a65eb6b36abe716829688cf01910bbf91c34354ff7ec1c3de2b349"
      url: "https://pub.dev"
    source: hosted
    version: "1.18.0"
  mime:
    dependency: transitive
    description:
      name: mime
      sha256: "41a20518f0cb1256669420fdba0cd90d21561e560ac240f26ef8322e45bb7ed6"
      url: "https://pub.dev"
    source: hosted
    version: "2.0.0"
  mocktail:
    dependency: "direct dev"
    description:
      name: mocktail
      sha256: "5e1bf53cc7baa8062a33b84424deb61513858ea05c601b8509e683815b5914aa"
      url: "https://pub.dev"
    source: hosted
    version: "1.0.5"
  objective_c:
    dependency: transitive
    description:
      name: objective_c
      sha256: "6cb691c686fa2838c6deb34980d426145c2a5d537491cb83d463c33cdbc726ed"
      url: "https://pub.dev"
    source: hosted
    version: "9.4.1"
  package_config:
    dependency: transitive
    description:
      name: package_config
      sha256: f096c55ebb7deb7e384101542bfba8c52696c1b56fca2eb62827989ef2353bbc
      url: "https://pub.dev"
    source: hosted
    version: "2.2.0"
  package_info_plus:
    dependency: transitive
    description:
      name: package_info_plus
      sha256: "468c26b4254ab01979fa5e4a98cb343ea3631b9acee6f21028997419a80e1a20"
      url: "https://pub.dev"
    source: hosted
    version: "9.0.1"
  package_info_plus_platform_interface:
    dependency: transitive
    description:
      name: package_info_plus_platform_interface
      sha256: "202a487f08836a592a6bd4f901ac69b3a8f146af552bbd14407b6b41e1c3f086"
      url: "https://pub.dev"
    source: hosted
    version: "3.2.1"
  path:
    dependency: transitive
    description:
      name: path
      sha256: "75cca69d1490965be98c73ceaea117e8a04dd21217b37b292c9ddbec0d955bc5"
      url: "https://pub.dev"
    source: hosted
    version: "1.9.1"
  path_provider:
    dependency: transitive
    description:
      name: path_provider
      sha256: a7f4874f987173da295a61c181b8ee71dab59b332a486b391babf26a1b884825
      url: "https://pub.dev"
    source: hosted
    version: "2.1.6"
  path_provider_android:
    dependency: transitive
    description:
      name: path_provider_android
      sha256: "149441ca6e4f38193b2e004c0ca6376a3d11f51fa5a77552d8bd4d2b0c0912ba"
      url: "https://pub.dev"
    source: hosted
    version: "2.2.23"
  path_provider_foundation:
    dependency: transitive
    description:
      name: path_provider_foundation
      sha256: "2a376b7d6392d80cd3705782d2caa734ca4727776db0b6ec36ef3f1855197699"
      url: "https://pub.dev"
    source: hosted
    version: "2.6.0"
  path_provider_linux:
    dependency: transitive
    description:
      name: path_provider_linux
      sha256: "58c2005f147315b11e9b4a7bc889cd5203e250cba8e3f012dae259b4972b5c16"
      url: "https://pub.dev"
    source: hosted
    version: "2.2.2"
  path_provider_platform_interface:
    dependency: transitive
    description:
      name: path_provider_platform_interface
      sha256: "484838772624c3a4b94f1e44a3e19897fee738f2d5c4ce448443b0417f7c9dda"
      url: "https://pub.dev"
    source: hosted
    version: "2.1.3"
  path_provider_windows:
    dependency: transitive
    description:
      name: path_provider_windows
      sha256: bd6f00dbd873bfb70d0761682da2b3a2c2fccc2b9e84c495821639601d81afe7
      url: "https://pub.dev"
    source: hosted
    version: "2.3.0"
  platform:
    dependency: transitive
    description:
      name: platform
      sha256: "5d6b1b0036a5f331ebc77c850ebc8506cbc1e9416c27e59b439f917a902a4984"
      url: "https://pub.dev"
    source: hosted
    version: "3.1.6"
  plugin_platform_interface:
    dependency: transitive
    description:
      name: plugin_platform_interface
      sha256: "4820fbfdb9478b1ebae27888254d445073732dae3d6ea81f0b7e06d5dedc3f02"
      url: "https://pub.dev"
    source: hosted
    version: "2.1.8"
  pub_semver:
    dependency: transitive
    description:
      name: pub_semver
      sha256: "5bfcf68ca79ef689f8990d1160781b4bad40a3bd5e5218ad4076ddb7f4081585"
      url: "https://pub.dev"
    source: hosted
    version: "2.2.0"
  record_use:
    dependency: transitive
    description:
      name: record_use
      sha256: "2551bd8eecfe95d14ae75f6021ad0248be5c27f138c2ec12fcb52b500b3ba1ed"
      url: "https://pub.dev"
    source: hosted
    version: "0.6.0"
  riverpod:
    dependency: transitive
    description:
      name: riverpod
      sha256: "59062512288d3056b2321804332a13ffdd1bf16df70dcc8e506e411280a72959"
      url: "https://pub.dev"
    source: hosted
    version: "2.6.1"
  sentry:
    dependency: transitive
    description:
      name: sentry
      sha256: "330a341076e16b87aa8a4f97b0bd48c085737d087e81ef337aee2b4c3e8896f9"
      url: "https://pub.dev"
    source: hosted
    version: "9.26.0"
  sentry_flutter:
    dependency: "direct main"
    description:
      name: sentry_flutter
      sha256: "163685070e173b9b28cd10e56eb76fdaca34067831bd7e3563f98a5bc5866165"
      url: "https://pub.dev"
    source: hosted
    version: "9.26.0"
  shared_preferences:
    dependency: "direct main"
    description:
      name: shared_preferences
      sha256: c3025c5534b01739267eb7d76959bbc25a6d10f6988e1c2a3036940133dd10bf
      url: "https://pub.dev"
    source: hosted
    version: "2.5.5"
  shared_preferences_android:
    dependency: transitive
    description:
      name: shared_preferences_android
      sha256: "0634e64bd719f89c012f392938e173521f535d3ecaf66558fa94a056d22b5cc7"
      url: "https://pub.dev"
    source: hosted
    version: "2.4.27"
  shared_preferences_foundation:
    dependency: transitive
    description:
      name: shared_preferences_foundation
      sha256: "4e7eaffc2b17ba398759f1151415869a34771ba11ebbccd1b0145472a619a64f"
      url: "https://pub.dev"
    source: hosted
    version: "2.5.6"
  shared_preferences_linux:
    dependency: transitive
    description:
      name: shared_preferences_linux
      sha256: "580abfd40f415611503cae30adf626e6656dfb2f0cee8f465ece7b6defb40f2f"
      url: "https://pub.dev"
    source: hosted
    version: "2.4.1"
  shared_preferences_platform_interface:
    dependency: transitive
    description:
      name: shared_preferences_platform_interface
      sha256: "649dc798a33931919ea356c4305c2d1f81619ea6e92244070b520187b5140ef9"
      url: "https://pub.dev"
    source: hosted
    version: "2.4.2"
  shared_preferences_web:
    dependency: transitive
    description:
      name: shared_preferences_web
      sha256: c49bd060261c9a3f0ff445892695d6212ff603ef3115edbb448509d407600019
      url: "https://pub.dev"
    source: hosted
    version: "2.4.3"
  shared_preferences_windows:
    dependency: transitive
    description:
      name: shared_preferences_windows
      sha256: "94ef0f72b2d71bc3e700e025db3710911bd51a71cefb65cc609dd0d9a982e3c1"
      url: "https://pub.dev"
    source: hosted
    version: "2.4.1"
  sky_engine:
    dependency: transitive
    description: flutter
    source: sdk
    version: "0.0.0"
  source_span:
    dependency: transitive
    description:
      name: source_span
      sha256: "56a02f1f4cd1a2d96303c0144c93bd6d909eea6bee6bf5a0e0b685edbd4c47ab"
      url: "https://pub.dev"
    source: hosted
    version: "1.10.2"
  stack_trace:
    dependency: transitive
    description:
      name: stack_trace
      sha256: "8b27215b45d22309b5cddda1aa2b19bdfec9df0e765f2de506401c071d38d1b1"
      url: "https://pub.dev"
    source: hosted
    version: "1.12.1"
  state_notifier:
    dependency: transitive
    description:
      name: state_notifier
      sha256: b8677376aa54f2d7c58280d5a007f9e8774f1968d1fb1c096adcb4792fba29bb
      url: "https://pub.dev"
    source: hosted
    version: "1.0.0"
  stream_channel:
    dependency: transitive
    description:
      name: stream_channel
      sha256: "969e04c80b8bcdf826f8f16579c7b14d780458bd97f56d107d3950fdbeef059d"
      url: "https://pub.dev"
    source: hosted
    version: "2.1.4"
  string_scanner:
    dependency: transitive
    description:
      name: string_scanner
      sha256: "921cd31725b72fe181906c6a94d987c78e3b98c2e205b397ea399d4054872b43"
      url: "https://pub.dev"
    source: hosted
    version: "1.4.1"
  term_glyph:
    dependency: transitive
    description:
      name: term_glyph
      sha256: "7f554798625ea768a7518313e58f83891c7f5024f88e46e7182a4558850a4b8e"
      url: "https://pub.dev"
    source: hosted
    version: "1.2.2"
  test_api:
    dependency: transitive
    description:
      name: test_api
      sha256: "949a932224383300f01be9221c39180316445ecb8e7547f70a41a35bf421fb9e"
      url: "https://pub.dev"
    source: hosted
    version: "0.7.11"
  typed_data:
    dependency: transitive
    description:
      name: typed_data
      sha256: f9049c039ebfeb4cf7a7104a675823cd72dba8297f264b6637062516699fa006
      url: "https://pub.dev"
    source: hosted
    version: "1.4.0"
  uuid:
    dependency: transitive
    description:
      name: uuid
      sha256: "9b129329f58692f6e6578329498a8fe9fbe98f090beb764ffbb8ee2eadd01dcd"
      url: "https://pub.dev"
    source: hosted
    version: "4.6.0"
  vector_math:
    dependency: transitive
    description:
      name: vector_math
      sha256: d530bd74fea330e6e364cda7a85019c434070188383e1cd8d9777ee586914c5b
      url: "https://pub.dev"
    source: hosted
    version: "2.2.0"
  vm_service:
    dependency: transitive
    description:
      name: vm_service
      sha256: "0016aef94fc66495ac78af5859181e3f3bf2026bd8eecc72b9565601e19ab360"
      url: "https://pub.dev"
    source: hosted
    version: "15.2.0"
  web:
    dependency: transitive
    description:
      name: web
      sha256: "868d88a33d8a87b18ffc05f9f030ba328ffefba92d6c127917a2ba740f9cfe4a"
      url: "https://pub.dev"
    source: hosted
    version: "1.1.1"
  webview_flutter:
    dependency: "direct main"
    description:
      name: webview_flutter
      sha256: d53e1ccf5516f25017e3c9d44c39034db352d20fa34fe200674270242c2c5111
      url: "https://pub.dev"
    source: hosted
    version: "4.14.1"
  webview_flutter_android:
    dependency: transitive
    description:
      name: webview_flutter_android
      sha256: a97db7a44f8e71af2f3971c45550a08cce1fb60059c1b8e534251e6cfb753490
      url: "https://pub.dev"
    source: hosted
    version: "4.13.0"
  webview_flutter_platform_interface:
    dependency: transitive
    description:
      name: webview_flutter_platform_interface
      sha256: "1221c1b12f5278791042f2ec2841743784cf25c5a644e23d6680e5d718824f04"
      url: "https://pub.dev"
    source: hosted
    version: "2.15.1"
  webview_flutter_wkwebview:
    dependency: transitive
    description:
      name: webview_flutter_wkwebview
      sha256: c879dd64b87c452aa84381b244d5469da57ba7e8cca6884c7b1e0d406372c12d
      url: "https://pub.dev"
    source: hosted
    version: "3.26.0"
  win32:
    dependency: transitive
    description:
      name: win32
      sha256: d7cb55e04cd34096cd3a79b3330245f54cb96a370a1c27adb3c84b917de8b08e
      url: "https://pub.dev"
    source: hosted
    version: "5.15.0"
  xdg_directories:
    dependency: transitive
    description:
      name: xdg_directories
      sha256: "7a3f37b05d989967cdddcbb571f1ea834867ae2faa29725fd085180e0883aa15"
      url: "https://pub.dev"
    source: hosted
    version: "1.1.0"
  yaml:
    dependency: transitive
    description:
      name: yaml
      sha256: b9da305ac7c39faa3f030eccd175340f968459dae4af175130b3fc47e40d76ce
      url: "https://pub.dev"
    source: hosted
    version: "3.1.3"
sdks:
  dart: ">=3.12.0 <4.0.0"
  flutter: ">=3.44.0"

```

---

### File: `pubspec.yaml`

```yaml
name: sahmi_kasban_mobile
description: Arabic-first Flutter client for the Sahmi Kasban backend.
publish_to: none
version: 0.9.8+24

environment:
  sdk: ">=3.10.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8
  dio: ^5.8.0+1
  firebase_core: ^3.15.2
  firebase_messaging: ^15.2.10
  flutter_riverpod: ^2.6.1
  flutter_secure_storage: ^9.2.4
  go_router: ^14.8.1
  google_mobile_ads: ^9.0.0
  in_app_purchase: ^3.3.0
  intl: ^0.20.2
  webview_flutter: ^4.10.0
  sentry_flutter: ^9.25.0
  shared_preferences: ^2.5.3

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0
  mocktail: ^1.0.4

flutter:
  uses-material-design: true
  assets:
    - assets/avatars/
    - assets/branding/

```

---

### File: `android\build.gradle.kts`

```kts
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}

```

---

### File: `android\gradle.properties`

```properties
org.gradle.jvmargs=-Xmx8G -XX:MaxMetaspaceSize=4G -XX:ReservedCodeCacheSize=512m -XX:+HeapDumpOnOutOfMemoryError
android.useAndroidX=true
# This newDsl flag was added by the Flutter template
android.newDsl=false
# This builtInKotlin flag was added by the Flutter template
android.builtInKotlin=false

```

---

### File: `android\gradlew`

```
#!/usr/bin/env bash

##############################################################################
##
##  Gradle start up script for UN*X
##
##############################################################################

# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS=""

APP_NAME="Gradle"
APP_BASE_NAME=`basename "$0"`

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD="maximum"

warn ( ) {
    echo "$*"
}

die ( ) {
    echo
    echo "$*"
    echo
    exit 1
}

# OS specific support (must be 'true' or 'false').
cygwin=false
msys=false
darwin=false
case "`uname`" in
  CYGWIN* )
    cygwin=true
    ;;
  Darwin* )
    darwin=true
    ;;
  MINGW* )
    msys=true
    ;;
esac

# Attempt to set APP_HOME
# Resolve links: $0 may be a link
PRG="$0"
# Need this for relative symlinks.
while [ -h "$PRG" ] ; do
    ls=`ls -ld "$PRG"`
    link=`expr "$ls" : '.*-> \(.*\)$'`
    if expr "$link" : '/.*' > /dev/null; then
        PRG="$link"
    else
        PRG=`dirname "$PRG"`"/$link"
    fi
done
SAVED="`pwd`"
cd "`dirname \"$PRG\"`/" >/dev/null
APP_HOME="`pwd -P`"
cd "$SAVED" >/dev/null

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD="java"
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Increase the maximum file descriptors if we can.
if [ "$cygwin" = "false" -a "$darwin" = "false" ] ; then
    MAX_FD_LIMIT=`ulimit -H -n`
    if [ $? -eq 0 ] ; then
        if [ "$MAX_FD" = "maximum" -o "$MAX_FD" = "max" ] ; then
            MAX_FD="$MAX_FD_LIMIT"
        fi
        ulimit -n $MAX_FD
        if [ $? -ne 0 ] ; then
            warn "Could not set maximum file descriptor limit: $MAX_FD"
        fi
    else
        warn "Could not query maximum file descriptor limit: $MAX_FD_LIMIT"
    fi
fi

# For Darwin, add options to specify how the application appears in the dock
if $darwin; then
    GRADLE_OPTS="$GRADLE_OPTS \"-Xdock:name=$APP_NAME\" \"-Xdock:icon=$APP_HOME/media/gradle.icns\""
fi

# For Cygwin, switch paths to Windows format before running java
if $cygwin ; then
    APP_HOME=`cygpath --path --mixed "$APP_HOME"`
    CLASSPATH=`cygpath --path --mixed "$CLASSPATH"`
    JAVACMD=`cygpath --unix "$JAVACMD"`

    # We build the pattern for arguments to be converted via cygpath
    ROOTDIRSRAW=`find -L / -maxdepth 1 -mindepth 1 -type d 2>/dev/null`
    SEP=""
    for dir in $ROOTDIRSRAW ; do
        ROOTDIRS="$ROOTDIRS$SEP$dir"
        SEP="|"
    done
    OURCYGPATTERN="(^($ROOTDIRS))"
    # Add a user-defined pattern to the cygpath arguments
    if [ "$GRADLE_CYGPATTERN" != "" ] ; then
        OURCYGPATTERN="$OURCYGPATTERN|($GRADLE_CYGPATTERN)"
    fi
    # Now convert the arguments - kludge to limit ourselves to /bin/sh
    i=0
    for arg in "$@" ; do
        CHECK=`echo "$arg"|egrep -c "$OURCYGPATTERN" -`
        CHECK2=`echo "$arg"|egrep -c "^-"`                                 ### Determine if an option

        if [ $CHECK -ne 0 ] && [ $CHECK2 -eq 0 ] ; then                    ### Added a condition
            eval `echo args$i`=`cygpath --path --ignore --mixed "$arg"`
        else
            eval `echo args$i`="\"$arg\""
        fi
        i=$((i+1))
    done
    case $i in
        (0) set -- ;;
        (1) set -- "$args0" ;;
        (2) set -- "$args0" "$args1" ;;
        (3) set -- "$args0" "$args1" "$args2" ;;
        (4) set -- "$args0" "$args1" "$args2" "$args3" ;;
        (5) set -- "$args0" "$args1" "$args2" "$args3" "$args4" ;;
        (6) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" ;;
        (7) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" "$args6" ;;
        (8) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" "$args6" "$args7" ;;
        (9) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" "$args6" "$args7" "$args8" ;;
    esac
fi

# Split up the JVM_OPTS And GRADLE_OPTS values into an array, following the shell quoting and substitution rules
function splitJvmOpts() {
    JVM_OPTS=("$@")
}
eval splitJvmOpts $DEFAULT_JVM_OPTS $JAVA_OPTS $GRADLE_OPTS
JVM_OPTS[${#JVM_OPTS[*]}]="-Dorg.gradle.appname=$APP_BASE_NAME"

exec "$JAVACMD" "${JVM_OPTS[@]}" -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"

```

---

### File: `android\gradlew.bat`

```bat
@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  Gradle startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto init

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto init

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:init
@rem Get command-line arguments, handling Windowz variants

if not "%OS%" == "Windows_NT" goto win9xME_args
if "%@eval[2+2]" == "4" goto 4NT_args

:win9xME_args
@rem Slurp the command line arguments.
set CMD_LINE_ARGS=
set _SKIP=2

:win9xME_args_slurp
if "x%~1" == "x" goto execute

set CMD_LINE_ARGS=%*
goto execute

:4NT_args
@rem Get arguments from the 4NT Shell from JP Software
set CMD_LINE_ARGS=%$

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar

@rem Execute Gradle
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %CMD_LINE_ARGS%

:end
@rem End local scope for the variables with windows NT shell
if "%ERRORLEVEL%"=="0" goto mainEnd

:fail
rem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
if  not "" == "%GRADLE_EXIT_CONSOLE%" exit 1
exit /b 1

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega

```

---

### File: `android\local.properties`

```properties
sdk.dir=C:\\AndroidSDK
flutter.sdk=C:\\src\\flutter
flutter.buildMode=release
flutter.versionName=0.9.6
flutter.versionCode=21
```

---

### File: `android\settings.gradle.kts`

```kts
pluginManagement {
    val flutterSdkPath =
        run {
            val properties = java.util.Properties()
            file("local.properties").inputStream().use { properties.load(it) }
            val flutterSdkPath = properties.getProperty("flutter.sdk")
            require(flutterSdkPath != null) { "flutter.sdk not set in local.properties" }
            flutterSdkPath
        }

    includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

plugins {
    id("dev.flutter.flutter-plugin-loader") version "1.0.0"
    id("com.android.application") version "9.0.1" apply false
    id("org.jetbrains.kotlin.android") version "2.3.20" apply false
    id("com.google.gms.google-services") version "4.5.0" apply false
}

include(":app")

```

---

### File: `android\app\build.gradle.kts`

```kts
import java.util.Properties
import org.gradle.api.GradleException

plugins {
    id("com.android.application")
    id("dev.flutter.flutter-gradle-plugin")
}

val keystorePropertiesFile = rootProject.file("key.properties")
val googleServicesFile = file("google-services.json")
val ciPreviewBuild =
    providers.environmentVariable("SAHMI_CI_PREVIEW_BUILD").orNull == "true"
if (googleServicesFile.exists() && !ciPreviewBuild) {
    apply(plugin = "com.google.gms.google-services")
}

val keystoreProperties = Properties()
val releaseSigningConfigured = keystorePropertiesFile.exists().also { exists ->
    if (exists) {
        keystorePropertiesFile.inputStream().use(keystoreProperties::load)
    }
}
val allowCiPreviewSigning =
    ciPreviewBuild ||
        providers.environmentVariable("SAHMI_ALLOW_CI_PREVIEW_SIGNING").orNull == "true"
val productionBuild =
    providers.environmentVariable("SAHMI_PRODUCTION_BUILD").orNull == "true"
val admobAndroidAppId =
    providers.environmentVariable("ADMOB_ANDROID_APP_ID").orNull
        ?: "ca-app-pub-3940256099942544~3347511713"

if (productionBuild) {
    if (!releaseSigningConfigured) {
        throw GradleException("Production Android builds require the protected release signing key.")
    }
    if (!googleServicesFile.exists()) {
        throw GradleException("Production Android builds require google-services.json.")
    }
    if (ciPreviewBuild) {
        throw GradleException("Production Android builds cannot use the CI preview package.")
    }
    if (admobAndroidAppId.contains("3940256099942544")) {
        throw GradleException("Production Android builds must not use the Google AdMob test app ID.")
    }
}

android {
    namespace = "com.sahmikasban.sahmi_kasban_mobile"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        applicationId = "com.sahmikasban.sahmi_kasban_mobile"
        minSdk = 24
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
        manifestPlaceholders["admobAppId"] = admobAndroidAppId
    }

    signingConfigs {
        if (releaseSigningConfigured) {
            create("release") {
                keyAlias = keystoreProperties.getProperty("keyAlias")
                keyPassword = keystoreProperties.getProperty("keyPassword")
                storeFile = file(keystoreProperties.getProperty("storeFile"))
                storePassword = keystoreProperties.getProperty("storePassword")
                enableV1Signing = true
                enableV2Signing = true
            }
        }
    }

    buildTypes {
        release {
            when {
                releaseSigningConfigured -> {
                    signingConfig = signingConfigs.getByName("release")
                }
                allowCiPreviewSigning -> {
                    // CI previews are deliberately a different Android package. They can be
                    // installed beside the real app but can never be mistaken for an update.
                    signingConfig = signingConfigs.getByName("debug")
                    applicationIdSuffix = ".ci"
                    versionNameSuffix = "-ci"
                }
                else -> {
                    throw GradleException(
                        "Release signing is not configured. Use Signed Android Release, or set " +
                            "SAHMI_CI_PREVIEW_BUILD=true for a separate .ci preview package.",
                    )
                }
            }
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}

```

---

### File: `android\app\src\debug\AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Development-only network access. The production manifest does not allow cleartext traffic. -->
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:usesCleartextTraffic="true" />
</manifest>

```

---

### File: `android\app\src\main\AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.INTERNET"/>

    <application
        android:label="سهمي كسبان"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="false"
        android:fullBackupContent="false">
        <meta-data
            android:name="com.google.android.gms.ads.APPLICATION_ID"
            android:value="${admobAppId}"/>

        <!-- WorkManager is not used by the app. Keep it off Android's eager
             startup path so a stale WorkDatabase cannot terminate startup
             before Flutter reaches main(). -->
        <provider
            android:name="androidx.startup.InitializationProvider"
            android:authorities="${applicationId}.androidx-startup"
            android:exported="false"
            tools:node="merge">
            <meta-data
                android:name="androidx.work.WorkManagerInitializer"
                tools:node="remove" />
        </provider>

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:taskAffinity=""
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"
              />
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <meta-data
            android:name="flutterEmbedding"
            android:value="2" />
    </application>
    <queries>
        <intent>
            <action android:name="android.intent.action.PROCESS_TEXT"/>
            <data android:mimeType="text/plain"/>
        </intent>
    </queries>
</manifest>

```

---

### File: `android\app\src\main\java\io\flutter\plugins\GeneratedPluginRegistrant.java`

```java
package io.flutter.plugins;

import androidx.annotation.Keep;
import androidx.annotation.NonNull;
import io.flutter.Log;

import io.flutter.embedding.engine.FlutterEngine;

/**
 * Generated file. Do not edit.
 * This file is generated by the Flutter tool based on the
 * plugins that support the Android platform.
 */
@Keep
public final class GeneratedPluginRegistrant {
  private static final String TAG = "GeneratedPluginRegistrant";
  public static void registerWith(@NonNull FlutterEngine flutterEngine) {
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.firebase.core.FlutterFirebaseCorePlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin firebase_core, io.flutter.plugins.firebase.core.FlutterFirebaseCorePlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.firebase.messaging.FlutterFirebaseMessagingPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin firebase_messaging, io.flutter.plugins.firebase.messaging.FlutterFirebaseMessagingPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new com.it_nomads.fluttersecurestorage.FlutterSecureStoragePlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin flutter_secure_storage, com.it_nomads.fluttersecurestorage.FlutterSecureStoragePlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.googlemobileads.GoogleMobileAdsPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin google_mobile_ads, io.flutter.plugins.googlemobileads.GoogleMobileAdsPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.inapppurchase.InAppPurchasePlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin in_app_purchase_android, io.flutter.plugins.inapppurchase.InAppPurchasePlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new com.github.dart_lang.jni.JniPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin jni, com.github.dart_lang.jni.JniPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new dev.fluttercommunity.plus.packageinfo.PackageInfoPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin package_info_plus, dev.fluttercommunity.plus.packageinfo.PackageInfoPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.pathprovider.PathProviderPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin path_provider_android, io.flutter.plugins.pathprovider.PathProviderPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.sentry.flutter.SentryFlutterPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin sentry_flutter, io.sentry.flutter.SentryFlutterPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.sharedpreferences.SharedPreferencesPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin shared_preferences_android, io.flutter.plugins.sharedpreferences.SharedPreferencesPlugin", e);
    }
    try {
      flutterEngine.getPlugins().add(new io.flutter.plugins.webviewflutter.WebViewFlutterPlugin());
    } catch (Exception e) {
      Log.e(TAG, "Error registering plugin webview_flutter_android, io.flutter.plugins.webviewflutter.WebViewFlutterPlugin", e);
    }
  }
}

```

---

### File: `android\app\src\main\kotlin\com\sahmikasban\sahmi_kasban_mobile\MainActivity.kt`

```kt
package com.sahmikasban.sahmi_kasban_mobile

import android.content.ContentValues
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File

class MainActivity : FlutterActivity() {
    private val downloadsChannel = "sahmi_kasban/downloads"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            downloadsChannel,
        ).setMethodCallHandler { call, result ->
            if (call.method != "saveCsv") {
                result.notImplemented()
                return@setMethodCallHandler
            }
            val requestedName = call.argument<String>("filename") ?: "sahmi-engine-replay.csv"
            val bytes = call.argument<ByteArray>("bytes")
            if (bytes == null || bytes.isEmpty()) {
                result.error("EMPTY_FILE", "CSV payload is empty", null)
                return@setMethodCallHandler
            }
            try {
                result.success(saveCsv(requestedName, bytes))
            } catch (error: Exception) {
                result.error("SAVE_FAILED", error.message, null)
            }
        }
    }

    private fun saveCsv(requestedName: String, bytes: ByteArray): String {
        val safeName = requestedName
            .replace(Regex("[^A-Za-z0-9._-]"), "-")
            .let { if (it.endsWith(".csv", ignoreCase = true)) it else "$it.csv" }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, safeName)
                put(MediaStore.Downloads.MIME_TYPE, "text/csv")
                put(
                    MediaStore.Downloads.RELATIVE_PATH,
                    Environment.DIRECTORY_DOWNLOADS + "/SahmiKasban",
                )
                put(MediaStore.Downloads.IS_PENDING, 1)
            }
            val resolver = contentResolver
            val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                ?: error("Could not create a Downloads file")
            try {
                resolver.openOutputStream(uri)?.use { stream ->
                    stream.write(bytes)
                    stream.flush()
                } ?: error("Could not open the Downloads file")
                values.clear()
                values.put(MediaStore.Downloads.IS_PENDING, 0)
                resolver.update(uri, values, null, null)
                return uri.toString()
            } catch (error: Exception) {
                resolver.delete(uri, null, null)
                throw error
            }
        }

        val directory = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
            ?: filesDir
        val file = File(directory, safeName)
        file.writeBytes(bytes)
        return file.absolutePath
    }
}

```

---

### File: `android\app\src\main\res\drawable\launch_background.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#074D30" />
        </shape>
    </item>
    <item>
        <bitmap android:gravity="center" android:src="@drawable/launch_logo" />
    </item>
</layer-list>

```

---

### File: `android\app\src\main\res\drawable\launch_logo.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\drawable-v21\launch_background.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#074D30" />
        </shape>
    </item>
    <item>
        <bitmap android:gravity="center" android:src="@drawable/launch_logo" />
    </item>
</layer-list>

```

---

### File: `android\app\src\main\res\drawable-v21\launch_logo.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\mipmap-hdpi\ic_launcher.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\mipmap-mdpi\ic_launcher.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\mipmap-xhdpi\ic_launcher.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\mipmap-xxhdpi\ic_launcher.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\mipmap-xxxhdpi\ic_launcher.png`

*(Binary or non-text file content omitted)*

---

### File: `android\app\src\main\res\values\styles.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Theme applied to the Android Window while the process is starting when the OS's Dark Mode setting is off -->
    <style name="LaunchTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <!-- Show a splash screen on the activity. Automatically removed when
             the Flutter engine draws its first frame -->
        <item name="android:windowBackground">@drawable/launch_background</item>
    </style>
    <!-- Theme applied to the Android Window as soon as the process has started.
         This theme determines the color of the Android Window while your
         Flutter UI initializes, as well as behind your Flutter UI while its
         running.

         This Theme is only used starting with V2 of Flutter's Android embedding. -->
    <style name="NormalTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <item name="android:windowBackground">?android:colorBackground</item>
    </style>
</resources>

```

---

### File: `android\app\src\main\res\values-night\styles.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Theme applied to the Android Window while the process is starting when the OS's Dark Mode setting is on -->
    <style name="LaunchTheme" parent="@android:style/Theme.Black.NoTitleBar">
        <!-- Show a splash screen on the activity. Automatically removed when
             the Flutter engine draws its first frame -->
        <item name="android:windowBackground">@drawable/launch_background</item>
    </style>
    <!-- Theme applied to the Android Window as soon as the process has started.
         This theme determines the color of the Android Window while your
         Flutter UI initializes, as well as behind your Flutter UI while its
         running.

         This Theme is only used starting with V2 of Flutter's Android embedding. -->
    <style name="NormalTheme" parent="@android:style/Theme.Black.NoTitleBar">
        <item name="android:windowBackground">?android:colorBackground</item>
    </style>
</resources>

```

---

### File: `android\app\src\profile\AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- The INTERNET permission is required for development. Specifically,
         the Flutter tool needs it to communicate with the running application
         to allow setting breakpoints, to provide hot reload, etc.
    -->
    <uses-permission android:name="android.permission.INTERNET"/>
</manifest>

```

---

### File: `android\gradle\wrapper\gradle-wrapper.jar`

*(Binary or non-text file content omitted)*

---

### File: `android\gradle\wrapper\gradle-wrapper.properties`

```properties
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-9.1.0-all.zip

```

---

### File: `assets\avatars\avatar_01.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_02.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_03.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_04.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_05.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_06.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_07.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_08.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_09.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_10.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_11.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\avatars\avatar_12.webp`

*(Binary or non-text file content omitted)*

---

### File: `assets\branding\app_icon.png`

*(Binary or non-text file content omitted)*

---

### File: `assets\branding\splash_symbol.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Flutter\AppFrameworkInfo.plist`

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>App</string>
  <key>CFBundleIdentifier</key>
  <string>io.flutter.flutter.app</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>App</string>
  <key>CFBundlePackageType</key>
  <string>FMWK</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundleSignature</key>
  <string>????</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
</dict>
</plist>

```

---

### File: `ios\Flutter\Debug.xcconfig`

```xcconfig
#include "Generated.xcconfig"
ADMOB_IOS_APP_ID=ca-app-pub-3940256099942544~1458002511

```

---

### File: `ios\Flutter\Generated.xcconfig`

```xcconfig
// This is a generated file; do not edit or check into version control.
FLUTTER_ROOT=C:\src\flutter
FLUTTER_APPLICATION_PATH=H:\project\Sahmi-Kasban\Sahmi-Kasban-git\mobile
FLUTTER_FRAMEWORK_SWIFT_PACKAGE_PATH=H:\project\Sahmi-Kasban\Sahmi-Kasban-git\mobile\ios\Flutter\ephemeral\Packages\.packages\FlutterFramework
COCOAPODS_PARALLEL_CODE_SIGN=true
FLUTTER_TARGET=lib\main.dart
FLUTTER_BUILD_DIR=build
FLUTTER_BUILD_NAME=0.9.6
FLUTTER_BUILD_NUMBER=21
EXCLUDED_ARCHS[sdk=iphonesimulator*]=i386
EXCLUDED_ARCHS[sdk=iphoneos*]=armv7
DART_OBFUSCATION=false
TRACK_WIDGET_CREATION=true
TREE_SHAKE_ICONS=false
PACKAGE_CONFIG=.dart_tool/package_config.json

```

---

### File: `ios\Flutter\Release.xcconfig`

```xcconfig
#include "Generated.xcconfig"
// Override this build setting in the production archive command or Xcode scheme.
ADMOB_IOS_APP_ID=ca-app-pub-3940256099942544~1458002511

```

---

### File: `ios\Flutter\flutter_export_environment.sh`

```sh
#!/bin/sh
# This is a generated file; do not edit or check into version control.
export "FLUTTER_ROOT=C:\src\flutter"
export "FLUTTER_APPLICATION_PATH=H:\project\Sahmi-Kasban\Sahmi-Kasban-git\mobile"
export "FLUTTER_FRAMEWORK_SWIFT_PACKAGE_PATH=H:\project\Sahmi-Kasban\Sahmi-Kasban-git\mobile\ios\Flutter\ephemeral\Packages\.packages\FlutterFramework"
export "COCOAPODS_PARALLEL_CODE_SIGN=true"
export "FLUTTER_TARGET=lib\main.dart"
export "FLUTTER_BUILD_DIR=build"
export "FLUTTER_BUILD_NAME=0.9.6"
export "FLUTTER_BUILD_NUMBER=21"
export "DART_OBFUSCATION=false"
export "TRACK_WIDGET_CREATION=true"
export "TREE_SHAKE_ICONS=false"
export "PACKAGE_CONFIG=.dart_tool/package_config.json"

```

---

### File: `ios\Flutter\ephemeral\flutter_lldb_helper.py`

```py
#
# Generated file, do not edit.
#

import lldb

def handle_new_rx_page(frame: lldb.SBFrame, bp_loc, extra_args, intern_dict):
    """Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages."""
    base = frame.register["x0"].GetValueAsAddress()
    page_len = frame.register["x1"].GetValueAsUnsigned()

    # Note: NOTIFY_DEBUGGER_ABOUT_RX_PAGES will check contents of the
    # first page to see if handled it correctly. This makes diagnosing
    # misconfiguration (e.g. missing breakpoint) easier.
    data = bytearray(page_len)
    data[0:8] = b'IHELPED!'

    error = lldb.SBError()
    frame.GetThread().GetProcess().WriteMemory(base, data, error)
    if not error.Success():
        print(f'Failed to write into {base}[+{page_len}]', error)
        return

def __lldb_init_module(debugger: lldb.SBDebugger, _):
    target = debugger.GetDummyTarget()
    # Caveat: must use BreakpointCreateByRegEx here and not
    # BreakpointCreateByName. For some reasons callback function does not
    # get carried over from dummy target for the later.
    bp = target.BreakpointCreateByRegex("^NOTIFY_DEBUGGER_ABOUT_RX_PAGES$")
    bp.SetScriptCallbackFunction('{}.handle_new_rx_page'.format(__name__))
    bp.SetAutoContinue(True)
    print("-- LLDB integration loaded --")

```

---

### File: `ios\Flutter\ephemeral\flutter_lldbinit`

```
#
# Generated file, do not edit.
#

command script import --relative-to-command-file flutter_lldb_helper.py

```

---

### File: `ios\Flutter\ephemeral\flutter_native_integration.env`

```env
FLUTTER_ROOT=C:\src\flutter
FLUTTER_APPLICATION_PATH=H:\project\Sahmi-Kasban\Sahmi-Kasban-git\mobile
FLUTTER_FRAMEWORK_SWIFT_PACKAGE_PATH=H:\project\Sahmi-Kasban\Sahmi-Kasban-git\mobile\ios\Flutter\ephemeral\Packages\.packages\FlutterFramework
COCOAPODS_PARALLEL_CODE_SIGN=true
FLUTTER_TARGET=lib\main.dart
FLUTTER_BUILD_DIR=build
FLUTTER_BUILD_NAME=0.9.6
FLUTTER_BUILD_NUMBER=21
DART_OBFUSCATION=false
TRACK_WIDGET_CREATION=true
TREE_SHAKE_ICONS=false
PACKAGE_CONFIG=.dart_tool/package_config.json

```

---

### File: `ios\Flutter\ephemeral\Packages\FlutterGeneratedPluginSwiftPackage\Package.swift`

```swift
// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.
//
// Generated file. Do not edit.
//

import PackageDescription

let package = Package(
    name: "FlutterGeneratedPluginSwiftPackage",
    platforms: [
        .iOS("13.0")
    ],
    products: [
        .library(name: "FlutterGeneratedPluginSwiftPackage", type: .static, targets: ["FlutterGeneratedPluginSwiftPackage"])
    ],
    dependencies: [
        
    ],
    targets: [
        .target(
            name: "FlutterGeneratedPluginSwiftPackage"
        )
    ]
)

```

---

### File: `ios\Flutter\ephemeral\Packages\FlutterGeneratedPluginSwiftPackage\Sources\FlutterGeneratedPluginSwiftPackage\FlutterGeneratedPluginSwiftPackage.swift`

```swift
//
// Generated file. Do not edit.
//

```

---

### File: `ios\Runner\AppDelegate.swift`

```swift
import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
  }
}

```

---

### File: `ios\Runner\GeneratedPluginRegistrant.h`

```h
//
//  Generated file. Do not edit.
//

// clang-format off

#ifndef GeneratedPluginRegistrant_h
#define GeneratedPluginRegistrant_h

#import <Flutter/Flutter.h>

NS_ASSUME_NONNULL_BEGIN

@interface GeneratedPluginRegistrant : NSObject
+ (void)registerWithRegistry:(NSObject<FlutterPluginRegistry>*)registry;
@end

NS_ASSUME_NONNULL_END
#endif /* GeneratedPluginRegistrant_h */

```

---

### File: `ios\Runner\GeneratedPluginRegistrant.m`

```m
//
//  Generated file. Do not edit.
//

// clang-format off

#import "GeneratedPluginRegistrant.h"

#if __has_include(<firebase_core/FLTFirebaseCorePlugin.h>)
#import <firebase_core/FLTFirebaseCorePlugin.h>
#else
@import firebase_core;
#endif

#if __has_include(<firebase_messaging/FLTFirebaseMessagingPlugin.h>)
#import <firebase_messaging/FLTFirebaseMessagingPlugin.h>
#else
@import firebase_messaging;
#endif

#if __has_include(<flutter_secure_storage/FlutterSecureStoragePlugin.h>)
#import <flutter_secure_storage/FlutterSecureStoragePlugin.h>
#else
@import flutter_secure_storage;
#endif

#if __has_include(<google_mobile_ads/FLTGoogleMobileAdsPlugin.h>)
#import <google_mobile_ads/FLTGoogleMobileAdsPlugin.h>
#else
@import google_mobile_ads;
#endif

#if __has_include(<in_app_purchase_storekit/InAppPurchasePlugin.h>)
#import <in_app_purchase_storekit/InAppPurchasePlugin.h>
#else
@import in_app_purchase_storekit;
#endif

#if __has_include(<package_info_plus/FPPPackageInfoPlusPlugin.h>)
#import <package_info_plus/FPPPackageInfoPlusPlugin.h>
#else
@import package_info_plus;
#endif

#if __has_include(<sentry_flutter/SentryFlutterPlugin.h>)
#import <sentry_flutter/SentryFlutterPlugin.h>
#else
@import sentry_flutter;
#endif

#if __has_include(<shared_preferences_foundation/SharedPreferencesPlugin.h>)
#import <shared_preferences_foundation/SharedPreferencesPlugin.h>
#else
@import shared_preferences_foundation;
#endif

#if __has_include(<webview_flutter_wkwebview/WebViewFlutterPlugin.h>)
#import <webview_flutter_wkwebview/WebViewFlutterPlugin.h>
#else
@import webview_flutter_wkwebview;
#endif

@implementation GeneratedPluginRegistrant

+ (void)registerWithRegistry:(NSObject<FlutterPluginRegistry>*)registry {
  [FLTFirebaseCorePlugin registerWithRegistrar:[registry registrarForPlugin:@"FLTFirebaseCorePlugin"]];
  [FLTFirebaseMessagingPlugin registerWithRegistrar:[registry registrarForPlugin:@"FLTFirebaseMessagingPlugin"]];
  [FlutterSecureStoragePlugin registerWithRegistrar:[registry registrarForPlugin:@"FlutterSecureStoragePlugin"]];
  [FLTGoogleMobileAdsPlugin registerWithRegistrar:[registry registrarForPlugin:@"FLTGoogleMobileAdsPlugin"]];
  [InAppPurchasePlugin registerWithRegistrar:[registry registrarForPlugin:@"InAppPurchasePlugin"]];
  [FPPPackageInfoPlusPlugin registerWithRegistrar:[registry registrarForPlugin:@"FPPPackageInfoPlusPlugin"]];
  [SentryFlutterPlugin registerWithRegistrar:[registry registrarForPlugin:@"SentryFlutterPlugin"]];
  [SharedPreferencesPlugin registerWithRegistrar:[registry registrarForPlugin:@"SharedPreferencesPlugin"]];
  [WebViewFlutterPlugin registerWithRegistrar:[registry registrarForPlugin:@"WebViewFlutterPlugin"]];
}

@end

```

---

### File: `ios\Runner\Info.plist`

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CADisableMinimumFrameDurationOnPhone</key>
	<true/>
	<key>CFBundleDevelopmentRegion</key>
	<string>$(DEVELOPMENT_LANGUAGE)</string>
	<key>CFBundleDisplayName</key>
	<string>Sahmi Kasban Mobile</string>
	<key>CFBundleExecutable</key>
	<string>$(EXECUTABLE_NAME)</string>
	<key>CFBundleIdentifier</key>
	<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>سهمي كسبان</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>$(FLUTTER_BUILD_NAME)</string>
	<key>CFBundleSignature</key>
	<string>????</string>
	<key>CFBundleVersion</key>
	<string>$(FLUTTER_BUILD_NUMBER)</string>
	<key>GADApplicationIdentifier</key>
	<string>$(ADMOB_IOS_APP_ID)</string>
	<key>LSRequiresIPhoneOS</key>
	<true/>
	<key>UIApplicationSceneManifest</key>
	<dict>
		<key>UIApplicationSupportsMultipleScenes</key>
		<false/>
		<key>UISceneConfigurations</key>
		<dict>
			<key>UIWindowSceneSessionRoleApplication</key>
			<array>
				<dict>
					<key>UISceneClassName</key>
					<string>UIWindowScene</string>
					<key>UISceneConfigurationName</key>
					<string>flutter</string>
					<key>UISceneDelegateClassName</key>
					<string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
					<key>UISceneStoryboardFile</key>
					<string>Main</string>
				</dict>
			</array>
		</dict>
	</dict>
	<key>UIApplicationSupportsIndirectInputEvents</key>
	<true/>
	<key>UILaunchStoryboardName</key>
	<string>LaunchScreen</string>
	<key>UIMainStoryboardFile</key>
	<string>Main</string>
	<key>UISupportedInterfaceOrientations</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
	<key>UISupportedInterfaceOrientations~ipad</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationPortraitUpsideDown</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
</dict>
</plist>

```

---

### File: `ios\Runner\Runner-Bridging-Header.h`

```h
#import "GeneratedPluginRegistrant.h"

```

---

### File: `ios\Runner\SceneDelegate.swift`

```swift
import Flutter
import UIKit

class SceneDelegate: FlutterSceneDelegate {

}

```

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Contents.json`

```json
{
  "images" : [
    {
      "size" : "20x20",
      "idiom" : "iphone",
      "filename" : "Icon-App-20x20@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "20x20",
      "idiom" : "iphone",
      "filename" : "Icon-App-20x20@3x.png",
      "scale" : "3x"
    },
    {
      "size" : "29x29",
      "idiom" : "iphone",
      "filename" : "Icon-App-29x29@1x.png",
      "scale" : "1x"
    },
    {
      "size" : "29x29",
      "idiom" : "iphone",
      "filename" : "Icon-App-29x29@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "29x29",
      "idiom" : "iphone",
      "filename" : "Icon-App-29x29@3x.png",
      "scale" : "3x"
    },
    {
      "size" : "40x40",
      "idiom" : "iphone",
      "filename" : "Icon-App-40x40@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "40x40",
      "idiom" : "iphone",
      "filename" : "Icon-App-40x40@3x.png",
      "scale" : "3x"
    },
    {
      "size" : "60x60",
      "idiom" : "iphone",
      "filename" : "Icon-App-60x60@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "60x60",
      "idiom" : "iphone",
      "filename" : "Icon-App-60x60@3x.png",
      "scale" : "3x"
    },
    {
      "size" : "20x20",
      "idiom" : "ipad",
      "filename" : "Icon-App-20x20@1x.png",
      "scale" : "1x"
    },
    {
      "size" : "20x20",
      "idiom" : "ipad",
      "filename" : "Icon-App-20x20@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "29x29",
      "idiom" : "ipad",
      "filename" : "Icon-App-29x29@1x.png",
      "scale" : "1x"
    },
    {
      "size" : "29x29",
      "idiom" : "ipad",
      "filename" : "Icon-App-29x29@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "40x40",
      "idiom" : "ipad",
      "filename" : "Icon-App-40x40@1x.png",
      "scale" : "1x"
    },
    {
      "size" : "40x40",
      "idiom" : "ipad",
      "filename" : "Icon-App-40x40@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "76x76",
      "idiom" : "ipad",
      "filename" : "Icon-App-76x76@1x.png",
      "scale" : "1x"
    },
    {
      "size" : "76x76",
      "idiom" : "ipad",
      "filename" : "Icon-App-76x76@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "83.5x83.5",
      "idiom" : "ipad",
      "filename" : "Icon-App-83.5x83.5@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "1024x1024",
      "idiom" : "ios-marketing",
      "filename" : "Icon-App-1024x1024@1x.png",
      "scale" : "1x"
    }
  ],
  "info" : {
    "version" : 1,
    "author" : "xcode"
  }
}

```

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-1024x1024@1x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-20x20@1x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-20x20@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-20x20@3x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-29x29@1x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-29x29@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-29x29@3x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-40x40@1x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-40x40@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-40x40@3x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-60x60@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-60x60@3x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-76x76@1x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-76x76@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\AppIcon.appiconset\Icon-App-83.5x83.5@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\LaunchImage.imageset\Contents.json`

```json
{
  "images" : [
    {
      "idiom" : "universal",
      "filename" : "LaunchImage.png",
      "scale" : "1x"
    },
    {
      "idiom" : "universal",
      "filename" : "LaunchImage@2x.png",
      "scale" : "2x"
    },
    {
      "idiom" : "universal",
      "filename" : "LaunchImage@3x.png",
      "scale" : "3x"
    }
  ],
  "info" : {
    "version" : 1,
    "author" : "xcode"
  }
}

```

---

### File: `ios\Runner\Assets.xcassets\LaunchImage.imageset\LaunchImage.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\LaunchImage.imageset\LaunchImage@2x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\LaunchImage.imageset\LaunchImage@3x.png`

*(Binary or non-text file content omitted)*

---

### File: `ios\Runner\Assets.xcassets\LaunchImage.imageset\README.md`

```md
# Launch Screen Assets

You can customize the launch screen with your own desired assets by replacing the image files in this directory.

You can also do it by opening your Flutter project's Xcode project with `open ios/Runner.xcworkspace`, selecting `Runner/Assets.xcassets` in the Project Navigator and dropping in the desired images.
```

---

### File: `ios\Runner\Base.lproj\LaunchScreen.storyboard`

```storyboard
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="12121" systemVersion="16G29" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" launchScreen="YES" colorMatched="YES" initialViewController="01J-lp-oVM">
    <dependencies>
        <deployment identifier="iOS"/>
        <plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="12089"/>
    </dependencies>
    <scenes>
        <!--View Controller-->
        <scene sceneID="EHf-IW-A2E">
            <objects>
                <viewController id="01J-lp-oVM" sceneMemberID="viewController">
                    <layoutGuides>
                        <viewControllerLayoutGuide type="top" id="Ydg-fD-yQy"/>
                        <viewControllerLayoutGuide type="bottom" id="xbc-2k-c8Z"/>
                    </layoutGuides>
                    <view key="view" contentMode="scaleToFill" id="Ze5-6b-2t3">
                        <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
                        <subviews>
                            <imageView opaque="NO" clipsSubviews="YES" multipleTouchEnabled="YES" contentMode="center" image="LaunchImage" translatesAutoresizingMaskIntoConstraints="NO" id="YRO-k0-Ey4">
                            </imageView>
                        </subviews>
                        <color key="backgroundColor" red="0.027" green="0.302" blue="0.188" alpha="1" colorSpace="custom" customColorSpace="sRGB"/>
                        <constraints>
                            <constraint firstItem="YRO-k0-Ey4" firstAttribute="centerX" secondItem="Ze5-6b-2t3" secondAttribute="centerX" id="1a2-6s-vTC"/>
                            <constraint firstItem="YRO-k0-Ey4" firstAttribute="centerY" secondItem="Ze5-6b-2t3" secondAttribute="centerY" id="4X2-HB-R7a"/>
                        </constraints>
                    </view>
                </viewController>
                <placeholder placeholderIdentifier="IBFirstResponder" id="iYj-Kq-Ea1" userLabel="First Responder" sceneMemberID="firstResponder"/>
            </objects>
            <point key="canvasLocation" x="53" y="375"/>
        </scene>
    </scenes>
    <resources>
        <image name="LaunchImage" width="168" height="185"/>
    </resources>
</document>

```

---

### File: `ios\Runner\Base.lproj\Main.storyboard`

```storyboard
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="10117" systemVersion="15F34" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" useTraitCollections="YES" initialViewController="BYZ-38-t0r">
    <dependencies>
        <deployment identifier="iOS"/>
        <plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="10085"/>
    </dependencies>
    <scenes>
        <!--Flutter View Controller-->
        <scene sceneID="tne-QT-ifu">
            <objects>
                <viewController id="BYZ-38-t0r" customClass="FlutterViewController" sceneMemberID="viewController">
                    <layoutGuides>
                        <viewControllerLayoutGuide type="top" id="y3c-jy-aDJ"/>
                        <viewControllerLayoutGuide type="bottom" id="wfy-db-euE"/>
                    </layoutGuides>
                    <view key="view" contentMode="scaleToFill" id="8bC-Xf-vdC">
                        <rect key="frame" x="0.0" y="0.0" width="600" height="600"/>
                        <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
                        <color key="backgroundColor" white="1" alpha="1" colorSpace="custom" customColorSpace="calibratedWhite"/>
                    </view>
                </viewController>
                <placeholder placeholderIdentifier="IBFirstResponder" id="dkx-z0-nzr" sceneMemberID="firstResponder"/>
            </objects>
        </scene>
    </scenes>
</document>

```

---

### File: `ios\Runner.xcodeproj\project.pbxproj`

```pbxproj
// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {
	};
	objectVersion = 54;
	objects = {

/* Begin PBXBuildFile section */
		1498D2341E8E89220040F4C2 /* GeneratedPluginRegistrant.m in Sources */ = {isa = PBXBuildFile; fileRef = 1498D2331E8E89220040F4C2 /* GeneratedPluginRegistrant.m */; };
		331C808B294A63AB00263BE5 /* RunnerTests.swift in Sources */ = {isa = PBXBuildFile; fileRef = 331C807B294A618700263BE5 /* RunnerTests.swift */; };
		3B3967161E833CAA004F5970 /* AppFrameworkInfo.plist in Resources */ = {isa = PBXBuildFile; fileRef = 3B3967151E833CAA004F5970 /* AppFrameworkInfo.plist */; };
		74858FAF1ED2DC5600515810 /* AppDelegate.swift in Sources */ = {isa = PBXBuildFile; fileRef = 74858FAE1ED2DC5600515810 /* AppDelegate.swift */; };
		7884E8682EC3CC0700C636F2 /* SceneDelegate.swift in Sources */ = {isa = PBXBuildFile; fileRef = 7884E8672EC3CC0400C636F2 /* SceneDelegate.swift */; };
		78A318202AECB46A00862997 /* FlutterGeneratedPluginSwiftPackage in Frameworks */ = {isa = PBXBuildFile; productRef = 78A3181F2AECB46A00862997 /* FlutterGeneratedPluginSwiftPackage */; };
		97C146FC1CF9000F007C117D /* Main.storyboard in Resources */ = {isa = PBXBuildFile; fileRef = 97C146FA1CF9000F007C117D /* Main.storyboard */; };
		97C146FE1CF9000F007C117D /* Assets.xcassets in Resources */ = {isa = PBXBuildFile; fileRef = 97C146FD1CF9000F007C117D /* Assets.xcassets */; };
		97C147011CF9000F007C117D /* LaunchScreen.storyboard in Resources */ = {isa = PBXBuildFile; fileRef = 97C146FF1CF9000F007C117D /* LaunchScreen.storyboard */; };
/* End PBXBuildFile section */

/* Begin PBXContainerItemProxy section */
		331C8085294A63A400263BE5 /* PBXContainerItemProxy */ = {
			isa = PBXContainerItemProxy;
			containerPortal = 97C146E61CF9000F007C117D /* Project object */;
			proxyType = 1;
			remoteGlobalIDString = 97C146ED1CF9000F007C117D;
			remoteInfo = Runner;
		};
/* End PBXContainerItemProxy section */

/* Begin PBXCopyFilesBuildPhase section */
		9705A1C41CF9048500538489 /* Embed Frameworks */ = {
			isa = PBXCopyFilesBuildPhase;
			buildActionMask = 2147483647;
			dstPath = "";
			dstSubfolderSpec = 10;
			files = (
			);
			name = "Embed Frameworks";
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXCopyFilesBuildPhase section */

/* Begin PBXFileReference section */
		1498D2321E8E86230040F4C2 /* GeneratedPluginRegistrant.h */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.c.h; path = GeneratedPluginRegistrant.h; sourceTree = "<group>"; };
		1498D2331E8E89220040F4C2 /* GeneratedPluginRegistrant.m */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.c.objc; path = GeneratedPluginRegistrant.m; sourceTree = "<group>"; };
		331C807B294A618700263BE5 /* RunnerTests.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = RunnerTests.swift; sourceTree = "<group>"; };
		331C8081294A63A400263BE5 /* RunnerTests.xctest */ = {isa = PBXFileReference; explicitFileType = wrapper.cfbundle; includeInIndex = 0; path = RunnerTests.xctest; sourceTree = BUILT_PRODUCTS_DIR; };
		3B3967151E833CAA004F5970 /* AppFrameworkInfo.plist */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = text.plist.xml; name = AppFrameworkInfo.plist; path = Flutter/AppFrameworkInfo.plist; sourceTree = "<group>"; };
		74858FAD1ED2DC5600515810 /* Runner-Bridging-Header.h */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.c.h; path = "Runner-Bridging-Header.h"; sourceTree = "<group>"; };
		74858FAE1ED2DC5600515810 /* AppDelegate.swift */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = sourcecode.swift; path = AppDelegate.swift; sourceTree = "<group>"; };
		7884E8672EC3CC0400C636F2 /* SceneDelegate.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = SceneDelegate.swift; sourceTree = "<group>"; };
		78E0A7A72DC9AD7400C4905E /* FlutterGeneratedPluginSwiftPackage */ = {isa = PBXFileReference; lastKnownFileType = wrapper; name = FlutterGeneratedPluginSwiftPackage; path = Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage; sourceTree = "<group>"; };
		7AFA3C8E1D35360C0083082E /* Release.xcconfig */ = {isa = PBXFileReference; lastKnownFileType = text.xcconfig; name = Release.xcconfig; path = Flutter/Release.xcconfig; sourceTree = "<group>"; };
		9740EEB21CF90195004384FC /* Debug.xcconfig */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = text.xcconfig; name = Debug.xcconfig; path = Flutter/Debug.xcconfig; sourceTree = "<group>"; };
		9740EEB31CF90195004384FC /* Generated.xcconfig */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = text.xcconfig; name = Generated.xcconfig; path = Flutter/Generated.xcconfig; sourceTree = "<group>"; };
		97C146EE1CF9000F007C117D /* Runner.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = Runner.app; sourceTree = BUILT_PRODUCTS_DIR; };
		97C146FB1CF9000F007C117D /* Base */ = {isa = PBXFileReference; lastKnownFileType = file.storyboard; name = Base; path = Base.lproj/Main.storyboard; sourceTree = "<group>"; };
		97C146FD1CF9000F007C117D /* Assets.xcassets */ = {isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; };
		97C147001CF9000F007C117D /* Base */ = {isa = PBXFileReference; lastKnownFileType = file.storyboard; name = Base; path = Base.lproj/LaunchScreen.storyboard; sourceTree = "<group>"; };
		97C147021CF9000F007C117D /* Info.plist */ = {isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; };
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		97C146EB1CF9000F007C117D /* Frameworks */ = {
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
				78A318202AECB46A00862997 /* FlutterGeneratedPluginSwiftPackage in Frameworks */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		331C8082294A63A400263BE5 /* RunnerTests */ = {
			isa = PBXGroup;
			children = (
				331C807B294A618700263BE5 /* RunnerTests.swift */,
			);
			path = RunnerTests;
			sourceTree = "<group>";
		};
		9740EEB11CF90186004384FC /* Flutter */ = {
			isa = PBXGroup;
			children = (
				78E0A7A72DC9AD7400C4905E /* FlutterGeneratedPluginSwiftPackage */,
				3B3967151E833CAA004F5970 /* AppFrameworkInfo.plist */,
				9740EEB21CF90195004384FC /* Debug.xcconfig */,
				7AFA3C8E1D35360C0083082E /* Release.xcconfig */,
				9740EEB31CF90195004384FC /* Generated.xcconfig */,
			);
			name = Flutter;
			sourceTree = "<group>";
		};
		97C146E51CF9000F007C117D = {
			isa = PBXGroup;
			children = (
				9740EEB11CF90186004384FC /* Flutter */,
				97C146F01CF9000F007C117D /* Runner */,
				97C146EF1CF9000F007C117D /* Products */,
				331C8082294A63A400263BE5 /* RunnerTests */,
			);
			sourceTree = "<group>";
		};
		97C146EF1CF9000F007C117D /* Products */ = {
			isa = PBXGroup;
			children = (
				97C146EE1CF9000F007C117D /* Runner.app */,
				331C8081294A63A400263BE5 /* RunnerTests.xctest */,
			);
			name = Products;
			sourceTree = "<group>";
		};
		97C146F01CF9000F007C117D /* Runner */ = {
			isa = PBXGroup;
			children = (
				97C146FA1CF9000F007C117D /* Main.storyboard */,
				97C146FD1CF9000F007C117D /* Assets.xcassets */,
				97C146FF1CF9000F007C117D /* LaunchScreen.storyboard */,
				97C147021CF9000F007C117D /* Info.plist */,
				1498D2321E8E86230040F4C2 /* GeneratedPluginRegistrant.h */,
				1498D2331E8E89220040F4C2 /* GeneratedPluginRegistrant.m */,
				74858FAE1ED2DC5600515810 /* AppDelegate.swift */,
				7884E8672EC3CC0400C636F2 /* SceneDelegate.swift */,
				74858FAD1ED2DC5600515810 /* Runner-Bridging-Header.h */,
			);
			path = Runner;
			sourceTree = "<group>";
		};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		331C8080294A63A400263BE5 /* RunnerTests */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = 331C8087294A63A400263BE5 /* Build configuration list for PBXNativeTarget "RunnerTests" */;
			buildPhases = (
				331C807D294A63A400263BE5 /* Sources */,
				331C807F294A63A400263BE5 /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
				331C8086294A63A400263BE5 /* PBXTargetDependency */,
			);
			name = RunnerTests;
			productName = RunnerTests;
			productReference = 331C8081294A63A400263BE5 /* RunnerTests.xctest */;
			productType = "com.apple.product-type.bundle.unit-test";
		};
		97C146ED1CF9000F007C117D /* Runner */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = 97C147051CF9000F007C117D /* Build configuration list for PBXNativeTarget "Runner" */;
			buildPhases = (
				9740EEB61CF901F6004384FC /* Run Script */,
				97C146EA1CF9000F007C117D /* Sources */,
				97C146EB1CF9000F007C117D /* Frameworks */,
				97C146EC1CF9000F007C117D /* Resources */,
				9705A1C41CF9048500538489 /* Embed Frameworks */,
				3B06AD1E1E4923F5004D2608 /* Thin Binary */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = Runner;
			packageProductDependencies = (
				78A3181F2AECB46A00862997 /* FlutterGeneratedPluginSwiftPackage */,
			);
			productName = Runner;
			productReference = 97C146EE1CF9000F007C117D /* Runner.app */;
			productType = "com.apple.product-type.application";
		};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		97C146E61CF9000F007C117D /* Project object */ = {
			isa = PBXProject;
			attributes = {
				BuildIndependentTargetsInParallel = YES;
				LastUpgradeCheck = 1510;
				ORGANIZATIONNAME = "";
				TargetAttributes = {
					331C8080294A63A400263BE5 = {
						CreatedOnToolsVersion = 14.0;
						TestTargetID = 97C146ED1CF9000F007C117D;
					};
					97C146ED1CF9000F007C117D = {
						CreatedOnToolsVersion = 7.3.1;
						LastSwiftMigration = 1100;
					};
				};
			};
			buildConfigurationList = 97C146E91CF9000F007C117D /* Build configuration list for PBXProject "Runner" */;
			compatibilityVersion = "Xcode 9.3";
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = 97C146E51CF9000F007C117D;
			packageReferences = (
				781AD8BC2B33823900A9FFBB /* XCLocalSwiftPackageReference "Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage" */,
			);
			productRefGroup = 97C146EF1CF9000F007C117D /* Products */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
				97C146ED1CF9000F007C117D /* Runner */,
				331C8080294A63A400263BE5 /* RunnerTests */,
			);
		};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		331C807F294A63A400263BE5 /* Resources */ = {
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
		97C146EC1CF9000F007C117D /* Resources */ = {
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				97C147011CF9000F007C117D /* LaunchScreen.storyboard in Resources */,
				3B3967161E833CAA004F5970 /* AppFrameworkInfo.plist in Resources */,
				97C146FE1CF9000F007C117D /* Assets.xcassets in Resources */,
				97C146FC1CF9000F007C117D /* Main.storyboard in Resources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXResourcesBuildPhase section */

/* Begin PBXShellScriptBuildPhase section */
		3B06AD1E1E4923F5004D2608 /* Thin Binary */ = {
			isa = PBXShellScriptBuildPhase;
			alwaysOutOfDate = 1;
			buildActionMask = 2147483647;
			files = (
			);
			inputPaths = (
				"${TARGET_BUILD_DIR}/${INFOPLIST_PATH}",
			);
			name = "Thin Binary";
			outputPaths = (
			);
			runOnlyForDeploymentPostprocessing = 0;
			shellPath = /bin/sh;
			shellScript = "/bin/sh \"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh\" embed_and_thin";
		};
		9740EEB61CF901F6004384FC /* Run Script */ = {
			isa = PBXShellScriptBuildPhase;
			alwaysOutOfDate = 1;
			buildActionMask = 2147483647;
			files = (
			);
			inputPaths = (
			);
			name = "Run Script";
			outputPaths = (
			);
			runOnlyForDeploymentPostprocessing = 0;
			shellPath = /bin/sh;
			shellScript = "/bin/sh \"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh\" build";
		};
/* End PBXShellScriptBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		331C807D294A63A400263BE5 /* Sources */ = {
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				331C808B294A63AB00263BE5 /* RunnerTests.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
		97C146EA1CF9000F007C117D /* Sources */ = {
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				74858FAF1ED2DC5600515810 /* AppDelegate.swift in Sources */,
				1498D2341E8E89220040F4C2 /* GeneratedPluginRegistrant.m in Sources */,
				7884E8682EC3CC0700C636F2 /* SceneDelegate.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXSourcesBuildPhase section */

/* Begin PBXTargetDependency section */
		331C8086294A63A400263BE5 /* PBXTargetDependency */ = {
			isa = PBXTargetDependency;
			target = 97C146ED1CF9000F007C117D /* Runner */;
			targetProxy = 331C8085294A63A400263BE5 /* PBXContainerItemProxy */;
		};
/* End PBXTargetDependency section */

/* Begin PBXVariantGroup section */
		97C146FA1CF9000F007C117D /* Main.storyboard */ = {
			isa = PBXVariantGroup;
			children = (
				97C146FB1CF9000F007C117D /* Base */,
			);
			name = Main.storyboard;
			sourceTree = "<group>";
		};
		97C146FF1CF9000F007C117D /* LaunchScreen.storyboard */ = {
			isa = PBXVariantGroup;
			children = (
				97C147001CF9000F007C117D /* Base */,
			);
			name = LaunchScreen.storyboard;
			sourceTree = "<group>";
		};
/* End PBXVariantGroup section */

/* Begin XCBuildConfiguration section */
		249021D3217E4FDB00AE95B9 /* Profile */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++0x";
				CLANG_CXX_LIBRARY = "libc++";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = NO;
				GCC_C_LANGUAGE_STANDARD = gnu99;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 13.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				SDKROOT = iphoneos;
				SUPPORTED_PLATFORMS = iphoneos;
				TARGETED_DEVICE_FAMILY = "1,2";
				VALIDATE_PRODUCT = YES;
			};
			name = Profile;
		};
		249021D4217E4FDB00AE95B9 /* Profile */ = {
			isa = XCBuildConfiguration;
			baseConfigurationReference = 7AFA3C8E1D35360C0083082E /* Release.xcconfig */;
			buildSettings = {
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				CLANG_ENABLE_MODULES = YES;
				CURRENT_PROJECT_VERSION = "$(FLUTTER_BUILD_NUMBER)";
				ENABLE_BITCODE = NO;
				INFOPLIST_FILE = Runner/Info.plist;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				PRODUCT_BUNDLE_IDENTIFIER = com.sahmikasban.sahmiKasbanMobile;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_OBJC_BRIDGING_HEADER = "Runner/Runner-Bridging-Header.h";
				SWIFT_VERSION = 5.0;
				VERSIONING_SYSTEM = "apple-generic";
			};
			name = Profile;
		};
		331C8088294A63A400263BE5 /* Debug */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				BUNDLE_LOADER = "$(TEST_HOST)";
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				GENERATE_INFOPLIST_FILE = YES;
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.sahmikasban.sahmiKasbanMobile.RunnerTests;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
				SWIFT_VERSION = 5.0;
				TEST_HOST = "$(BUILT_PRODUCTS_DIR)/Runner.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/Runner";
			};
			name = Debug;
		};
		331C8089294A63A400263BE5 /* Release */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				BUNDLE_LOADER = "$(TEST_HOST)";
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				GENERATE_INFOPLIST_FILE = YES;
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.sahmikasban.sahmiKasbanMobile.RunnerTests;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_VERSION = 5.0;
				TEST_HOST = "$(BUILT_PRODUCTS_DIR)/Runner.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/Runner";
			};
			name = Release;
		};
		331C808A294A63A400263BE5 /* Profile */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				BUNDLE_LOADER = "$(TEST_HOST)";
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				GENERATE_INFOPLIST_FILE = YES;
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.sahmikasban.sahmiKasbanMobile.RunnerTests;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_VERSION = 5.0;
				TEST_HOST = "$(BUILT_PRODUCTS_DIR)/Runner.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/Runner";
			};
			name = Profile;
		};
		97C147031CF9000F007C117D /* Debug */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++0x";
				CLANG_CXX_LIBRARY = "libc++";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = NO;
				GCC_C_LANGUAGE_STANDARD = gnu99;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 13.0;
				MTL_ENABLE_DEBUG_INFO = YES;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = iphoneos;
				TARGETED_DEVICE_FAMILY = "1,2";
			};
			name = Debug;
		};
		97C147041CF9000F007C117D /* Release */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++0x";
				CLANG_CXX_LIBRARY = "libc++";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = NO;
				GCC_C_LANGUAGE_STANDARD = gnu99;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 13.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				SDKROOT = iphoneos;
				SUPPORTED_PLATFORMS = iphoneos;
				SWIFT_COMPILATION_MODE = wholemodule;
				SWIFT_OPTIMIZATION_LEVEL = "-O";
				TARGETED_DEVICE_FAMILY = "1,2";
				VALIDATE_PRODUCT = YES;
			};
			name = Release;
		};
		97C147061CF9000F007C117D /* Debug */ = {
			isa = XCBuildConfiguration;
			baseConfigurationReference = 9740EEB21CF90195004384FC /* Debug.xcconfig */;
			buildSettings = {
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				CLANG_ENABLE_MODULES = YES;
				CURRENT_PROJECT_VERSION = "$(FLUTTER_BUILD_NUMBER)";
				ENABLE_BITCODE = NO;
				INFOPLIST_FILE = Runner/Info.plist;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				PRODUCT_BUNDLE_IDENTIFIER = com.sahmikasban.sahmiKasbanMobile;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_OBJC_BRIDGING_HEADER = "Runner/Runner-Bridging-Header.h";
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
				SWIFT_VERSION = 5.0;
				VERSIONING_SYSTEM = "apple-generic";
			};
			name = Debug;
		};
		97C147071CF9000F007C117D /* Release */ = {
			isa = XCBuildConfiguration;
			baseConfigurationReference = 7AFA3C8E1D35360C0083082E /* Release.xcconfig */;
			buildSettings = {
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				CLANG_ENABLE_MODULES = YES;
				CURRENT_PROJECT_VERSION = "$(FLUTTER_BUILD_NUMBER)";
				ENABLE_BITCODE = NO;
				INFOPLIST_FILE = Runner/Info.plist;
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				PRODUCT_BUNDLE_IDENTIFIER = com.sahmikasban.sahmiKasbanMobile;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SWIFT_OBJC_BRIDGING_HEADER = "Runner/Runner-Bridging-Header.h";
				SWIFT_VERSION = 5.0;
				VERSIONING_SYSTEM = "apple-generic";
			};
			name = Release;
		};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		331C8087294A63A400263BE5 /* Build configuration list for PBXNativeTarget "RunnerTests" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				331C8088294A63A400263BE5 /* Debug */,
				331C8089294A63A400263BE5 /* Release */,
				331C808A294A63A400263BE5 /* Profile */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
		97C146E91CF9000F007C117D /* Build configuration list for PBXProject "Runner" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				97C147031CF9000F007C117D /* Debug */,
				97C147041CF9000F007C117D /* Release */,
				249021D3217E4FDB00AE95B9 /* Profile */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
		97C147051CF9000F007C117D /* Build configuration list for PBXNativeTarget "Runner" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				97C147061CF9000F007C117D /* Debug */,
				97C147071CF9000F007C117D /* Release */,
				249021D4217E4FDB00AE95B9 /* Profile */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
/* End XCConfigurationList section */

/* Begin XCLocalSwiftPackageReference section */
		781AD8BC2B33823900A9FFBB /* XCLocalSwiftPackageReference "Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage" */ = {
			isa = XCLocalSwiftPackageReference;
			relativePath = Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage;
		};
/* End XCLocalSwiftPackageReference section */

/* Begin XCSwiftPackageProductDependency section */
		78A3181F2AECB46A00862997 /* FlutterGeneratedPluginSwiftPackage */ = {
			isa = XCSwiftPackageProductDependency;
			productName = FlutterGeneratedPluginSwiftPackage;
		};
/* End XCSwiftPackageProductDependency section */
	};
	rootObject = 97C146E61CF9000F007C117D /* Project object */;
}

```

---

### File: `ios\Runner.xcodeproj\project.xcworkspace\contents.xcworkspacedata`

```xcworkspacedata
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:">
   </FileRef>
</Workspace>

```

---

### File: `ios\Runner.xcodeproj\project.xcworkspace\xcshareddata\IDEWorkspaceChecks.plist`

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEDidComputeMac32BitWarning</key>
	<true/>
</dict>
</plist>

```

---

### File: `ios\Runner.xcodeproj\project.xcworkspace\xcshareddata\WorkspaceSettings.xcsettings`

```xcsettings
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PreviewsEnabled</key>
	<false/>
</dict>
</plist>

```

---

### File: `ios\Runner.xcodeproj\xcshareddata\xcschemes\Runner.xcscheme`

```xcscheme
<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "1510"
   version = "1.3">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <PreActions>
         <ExecutionAction
            ActionType = "Xcode.IDEStandardExecutionActionsCore.ExecutionActionType.ShellScriptAction">
            <ActionContent
               title = "Run Prepare Flutter Framework Script"
               scriptText = "/bin/sh &quot;$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh&quot; prepare&#10;">
               <EnvironmentBuildable>
                  <BuildableReference
                     BuildableIdentifier = "primary"
                     BlueprintIdentifier = "97C146ED1CF9000F007C117D"
                     BuildableName = "Runner.app"
                     BlueprintName = "Runner"
                     ReferencedContainer = "container:Runner.xcodeproj">
                  </BuildableReference>
               </EnvironmentBuildable>
            </ActionContent>
         </ExecutionAction>
      </PreActions>
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "97C146ED1CF9000F007C117D"
               BuildableName = "Runner.app"
               BlueprintName = "Runner"
               ReferencedContainer = "container:Runner.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      customLLDBInitFile = "$(SRCROOT)/Flutter/ephemeral/flutter_lldbinit"
      shouldUseLaunchSchemeArgsEnv = "YES">
      <MacroExpansion>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "97C146ED1CF9000F007C117D"
            BuildableName = "Runner.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </MacroExpansion>
      <Testables>
         <TestableReference
            skipped = "NO"
            parallelizable = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "331C8080294A63A400263BE5"
               BuildableName = "RunnerTests.xctest"
               BlueprintName = "RunnerTests"
               ReferencedContainer = "container:Runner.xcodeproj">
            </BuildableReference>
         </TestableReference>
      </Testables>
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      customLLDBInitFile = "$(SRCROOT)/Flutter/ephemeral/flutter_lldbinit"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      enableGPUValidationMode = "1"
      allowLocationSimulation = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "97C146ED1CF9000F007C117D"
            BuildableName = "Runner.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Profile"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "97C146ED1CF9000F007C117D"
            BuildableName = "Runner.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>

```

---

### File: `ios\Runner.xcworkspace\contents.xcworkspacedata`

```xcworkspacedata
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "group:Runner.xcodeproj">
   </FileRef>
</Workspace>

```

---

### File: `ios\Runner.xcworkspace\xcshareddata\IDEWorkspaceChecks.plist`

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEDidComputeMac32BitWarning</key>
	<true/>
</dict>
</plist>

```

---

### File: `ios\Runner.xcworkspace\xcshareddata\WorkspaceSettings.xcsettings`

```xcsettings
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PreviewsEnabled</key>
	<false/>
</dict>
</plist>

```

---

### File: `ios\RunnerTests\RunnerTests.swift`

```swift
import Flutter
import UIKit
import XCTest

class RunnerTests: XCTestCase {

  func testExample() {
    // If you add code to the Runner application, consider adding tests here.
    // See https://developer.apple.com/documentation/xctest for more information about using XCTest.
  }

}

```

---

### File: `lib\main.dart`

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'package:intl/date_symbol_data_local.dart';

import 'app/app.dart';
import 'core/observability/app_observability.dart';
import 'features/notifications/notification_messaging.dart';

Future<void> _initializeServices() async {
  try {
    await initializeDateFormatting('ar');
  } on Object catch (error, stackTrace) {
    debugPrint(
      'Arabic date formatting initialization skipped: $error\n$stackTrace',
    );
  }

  try {
    await Firebase.initializeApp().timeout(const Duration(seconds: 10));
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
  } on Object catch (error, stackTrace) {
    debugPrint('Firebase initialization skipped: $error\n$stackTrace');
  }

  try {
    await MobileAds.instance.initialize().timeout(const Duration(seconds: 10));
  } on Object catch (error, stackTrace) {
    debugPrint('Mobile Ads initialization skipped: $error\n$stackTrace');
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppObservability.bootstrap(
    initializeServices: _initializeServices,
    app: const ProviderScope(child: SahmiKasbanApp()),
  );
}

```

---

### File: `lib\app\app.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../features/monetization/free_plan_ads.dart';
import '../features/notifications/notification_messaging_shell.dart';
import 'router.dart';
import 'theme.dart';

class SahmiKasbanApp extends ConsumerWidget {
  const SahmiKasbanApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    return MaterialApp.router(
      title: 'سهمي كسبان',
      debugShowCheckedModeBanner: false,
      theme: SahmiTheme.light(),
      routerConfig: router,
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: NotificationMessagingShell(
            child: FreePlanAdShell(child: child ?? const SizedBox.shrink()),
          ),
        );
      },
    );
  }
}

```

---

### File: `lib\app\router.dart`

```dart
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/observability/app_observability.dart';
import '../domain/models.dart';
import '../features/admin/admin_dashboard_screen.dart';
import '../features/admin/admin_wallet_credit_screen.dart';
import '../features/admin/historical_replay_control_screen.dart';
import '../features/auth/account_recovery_screens.dart';
import '../features/auth/auth_screens.dart';
import '../features/auth/session_controller.dart';
import '../features/bootstrap/splash_screen.dart';
import '../features/community/community_create_screen.dart';
import '../features/community/community_detail_screen.dart';
import '../features/community/my_discussions_screen.dart';
import '../features/home/dashboard_screen.dart';
import '../features/market/stock_analysis_screen.dart';
import '../features/market/stock_comparison_screen.dart';
import '../features/market/stock_detail_screen.dart';
import '../features/market/stocks_screen.dart';
import '../features/monetization/monetization_page.dart';
import '../features/notifications/notification_screen.dart';
import '../features/onboarding/onboarding_controller.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/performance/performance_admin_screen.dart';
import '../features/performance/performance_report_screen.dart';
import '../features/performance/performance_screen.dart';
import '../features/profile/profile_edit_screen.dart';
import '../features/reports/market_report_screen.dart';
import '../features/reports/reports_screen.dart';
import '../features/wallet/wallet_history_screen.dart';

class _RouterRefreshNotifier extends ChangeNotifier {
  void refresh() => notifyListeners();
}

final appRouterProvider = Provider<GoRouter>((ref) {
  final refreshNotifier = _RouterRefreshNotifier();
  ref.onDispose(refreshNotifier.dispose);
  ref.listen<AsyncValue<bool>>(
    onboardingControllerProvider,
    (_, __) => refreshNotifier.refresh(),
  );
  ref.listen<SessionState>(
    sessionControllerProvider,
    (_, __) => refreshNotifier.refresh(),
  );

  return GoRouter(
    initialLocation: '/splash',
    observers: AppObservability.navigatorObservers,
    refreshListenable: refreshNotifier,
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/verify-email',
        builder: (context, state) =>
            VerifyEmailScreen(email: state.uri.queryParameters['email']),
      ),
      GoRoute(
        path: '/forgot-password',
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: '/reset-password',
        builder: (context, state) =>
            ResetPasswordScreen(email: state.uri.queryParameters['email']),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/stocks',
        builder: (context, state) => const StocksScreen(),
      ),
      GoRoute(
        path: '/stocks/:ticker',
        builder: (context, state) =>
            StockDetailScreen(ticker: state.pathParameters['ticker']!),
      ),
      GoRoute(
        path: '/reports',
        builder: (context, state) => const ReportsScreen(),
      ),
      GoRoute(
        path: '/market/compare',
        builder: (context, state) => const StockComparisonScreen(),
      ),
      GoRoute(
        path: '/market/analyze/:ticker',
        builder: (context, state) =>
            StockAnalysisScreen(ticker: state.pathParameters['ticker']!),
      ),
      GoRoute(
        path: '/profile/edit',
        builder: (context, state) => const ProfileEditScreen(),
      ),
      GoRoute(
        path: '/wallet/history',
        builder: (context, state) => const WalletHistoryScreen(),
      ),
      GoRoute(
        path: '/monetization',
        builder: (context, state) => const MonetizationPage(),
      ),
      GoRoute(
        path: '/notifications',
        builder: (context, state) => const NotificationScreen(),
      ),
      GoRoute(
        path: '/performance',
        builder: (context, state) => const PerformanceScreen(),
      ),
      GoRoute(
        path: '/performance/reports/:reportId',
        builder: (context, state) => PerformanceReportScreen(
          reportId: state.pathParameters['reportId']!,
        ),
      ),
      GoRoute(
        path: '/admin',
        builder: (context, state) => const AdminDashboardScreen(),
      ),
      GoRoute(
        path: '/admin/performance',
        builder: (context, state) => const PerformanceAdminScreen(),
      ),
      GoRoute(
        path: '/admin/wallet-credit',
        builder: (context, state) => const AdminWalletCreditScreen(),
      ),
      GoRoute(
        path: '/admin/historical-replays',
        builder: (context, state) => const HistoricalReplayControlScreen(),
      ),
      GoRoute(
        path: '/community/new',
        builder: (context, state) => const CommunityCreateScreen(),
      ),
      GoRoute(
        path: '/community/mine',
        builder: (context, state) => const MyDiscussionsScreen(),
      ),
      GoRoute(
        path: '/community/:discussionId',
        builder: (context, state) => CommunityDetailScreen(
          discussionId: state.pathParameters['discussionId']!,
        ),
      ),
      GoRoute(
        path: '/reports/:reportId',
        builder: (context, state) => MarketReportScreen(
          reportId: state.pathParameters['reportId']!,
          preview: state.extra is MarketReportPreview
              ? state.extra! as MarketReportPreview
              : null,
        ),
      ),
    ],
    redirect: (context, state) {
      final onboarding = ref.read(onboardingControllerProvider);
      final session = ref.read(sessionControllerProvider);
      final location = state.matchedLocation;
      final onboardingLoading = onboarding.isLoading;
      final sessionLoading = session.status == SessionStatus.loading;
      if (onboardingLoading || sessionLoading) {
        return location == '/splash' ? null : '/splash';
      }

      final onboardingComplete = onboarding.value ?? false;
      if (!onboardingComplete) {
        return location == '/onboarding' ? null : '/onboarding';
      }

      final authenticated = session.status == SessionStatus.authenticated;
      final publicAccountRoutes = <String>{
        '/login',
        '/register',
        '/verify-email',
        '/forgot-password',
        '/reset-password',
      };
      final publicAccountRoute = publicAccountRoutes.contains(location);
      if (!authenticated) {
        return publicAccountRoute ? null : '/login';
      }
      if (location.startsWith('/admin') && session.profile?.isAdmin != true) {
        return '/home';
      }
      if (publicAccountRoute ||
          location == '/splash' ||
          location == '/onboarding') {
        return '/home';
      }
      return null;
    },
  );
});

```

---

### File: `lib\app\theme.dart`

```dart
import 'package:flutter/material.dart';

class SahmiTheme {
  const SahmiTheme._();

  static ThemeData light() {
    const seed = Color(0xFF1F6B52);
    final scheme = ColorScheme.fromSeed(
      seedColor: seed,
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: const Color(0xFFF6F7F4),
      appBarTheme: const AppBarTheme(centerTitle: false),
      cardTheme: const CardThemeData(
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(20)),
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}

```

---

### File: `lib\core\avatar_assets.dart`

```dart
const avatarKeys = <String>[
  'avatar_01',
  'avatar_02',
  'avatar_03',
  'avatar_04',
  'avatar_05',
  'avatar_06',
  'avatar_07',
  'avatar_08',
  'avatar_09',
  'avatar_10',
  'avatar_11',
  'avatar_12',
];

String avatarAssetPath(String key) {
  final safeKey = avatarKeys.contains(key) ? key : avatarKeys.first;
  return 'assets/avatars/$safeKey.webp';
}

```

---

### File: `lib\core\config\app_config.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.admobAndroidBannerId,
    required this.admobIosBannerId,
    required this.admobAndroidNativeId,
    required this.admobIosNativeId,
    required this.admobAndroidInterstitialId,
    required this.admobIosInterstitialId,
    this.appEnvironment = 'development',
    this.releasePlatform = 'android',
  });

  static const String googleTestPublisherId = '3940256099942544';

  final String apiBaseUrl;
  final String admobAndroidBannerId;
  final String admobIosBannerId;
  final String admobAndroidNativeId;
  final String admobIosNativeId;
  final String admobAndroidInterstitialId;
  final String admobIosInterstitialId;
  final String appEnvironment;
  final String releasePlatform;

  bool get isProduction => appEnvironment.trim().toLowerCase() == 'production';

  void validateForRuntime() {
    if (!isProduction) {
      return;
    }
    final uri = Uri.tryParse(apiBaseUrl);
    if (uri == null || uri.scheme != 'https' || uri.host.isEmpty) {
      throw StateError(
        'Production builds require an absolute HTTPS API_BASE_URL.',
      );
    }

    final normalizedPlatform = releasePlatform.trim().toLowerCase();
    final adUnitIds = switch (normalizedPlatform) {
      'android' => <String>[
        admobAndroidBannerId,
        admobAndroidNativeId,
        admobAndroidInterstitialId,
      ],
      'ios' => <String>[
        admobIosBannerId,
        admobIosNativeId,
        admobIosInterstitialId,
      ],
      _ => throw StateError(
        'Production builds require RELEASE_PLATFORM=android or ios.',
      ),
    };
    if (adUnitIds.any(
      (id) => id.trim().isEmpty || id.contains(googleTestPublisherId),
    )) {
      throw StateError(
        'Production builds require non-test AdMob banner, native, and interstitial IDs for the selected release platform.',
      );
    }
  }

  factory AppConfig.fromEnvironment() {
    const configuredUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:8000',
    );
    const environment = String.fromEnvironment(
      'APP_ENV',
      defaultValue: 'development',
    );
    const configuredReleasePlatform = String.fromEnvironment(
      'RELEASE_PLATFORM',
      defaultValue: 'android',
    );
    const androidBannerId = String.fromEnvironment(
      'ADMOB_ANDROID_BANNER_ID',
      defaultValue: 'ca-app-pub-3940256099942544/9214589741',
    );
    const iosBannerId = String.fromEnvironment(
      'ADMOB_IOS_BANNER_ID',
      defaultValue: 'ca-app-pub-3940256099942544/2435281174',
    );
    const androidNativeId = String.fromEnvironment(
      'ADMOB_ANDROID_NATIVE_ID',
      defaultValue: 'ca-app-pub-3940256099942544/2247696110',
    );
    const iosNativeId = String.fromEnvironment(
      'ADMOB_IOS_NATIVE_ID',
      defaultValue: 'ca-app-pub-3940256099942544/3986624511',
    );
    const androidInterstitialId = String.fromEnvironment(
      'ADMOB_ANDROID_INTERSTITIAL_ID',
      defaultValue: 'ca-app-pub-3940256099942544/1033173712',
    );
    const iosInterstitialId = String.fromEnvironment(
      'ADMOB_IOS_INTERSTITIAL_ID',
      defaultValue: 'ca-app-pub-3940256099942544/4411468910',
    );
    const config = AppConfig(
      apiBaseUrl: configuredUrl,
      admobAndroidBannerId: androidBannerId,
      admobIosBannerId: iosBannerId,
      admobAndroidNativeId: androidNativeId,
      admobIosNativeId: iosNativeId,
      admobAndroidInterstitialId: androidInterstitialId,
      admobIosInterstitialId: iosInterstitialId,
      appEnvironment: environment,
      releasePlatform: configuredReleasePlatform,
    );
    config.validateForRuntime();
    return config;
  }
}

final appConfigProvider = Provider<AppConfig>((ref) {
  return AppConfig.fromEnvironment();
});

```

---

### File: `lib\core\config\demo_mode.dart`

```dart
class DemoMode {
  const DemoMode._();

  static const enabled = bool.fromEnvironment('DEMO_MODE', defaultValue: false);
}

```

---

### File: `lib\core\network\api_client.dart`

```dart
import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';
import 'api_exception.dart';
import 'token_store.dart';

BaseOptions _apiOptions(String baseUrl) {
  return BaseOptions(
    baseUrl: '$baseUrl/api/v1',
    connectTimeout: const Duration(seconds: 12),
    sendTimeout: const Duration(seconds: 20),
    receiveTimeout: const Duration(seconds: 30),
    headers: const <String, String>{'Accept': 'application/json'},
  );
}

class ApiClient {
  ApiClient({
    required String baseUrl,
    required TokenStore tokenStore,
    Dio? dio,
    Dio? refreshDio,
  }) : _tokenStore = tokenStore,
       _dio = dio ?? Dio(_apiOptions(baseUrl)),
       _refreshDio = refreshDio ?? Dio(_apiOptions(baseUrl)) {
    _dio.interceptors.add(
      InterceptorsWrapper(onRequest: _onRequest, onError: _onError),
    );
  }

  final TokenStore _tokenStore;
  final Dio _dio;
  final Dio _refreshDio;
  Future<String?>? _refreshFuture;

  Dio get dio => _dio;

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (options.extra['anonymous'] == true) {
      handler.next(options);
      return;
    }
    final accessToken = await _tokenStore.readAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  Future<void> _onError(
    DioException error,
    ErrorInterceptorHandler handler,
  ) async {
    final request = error.requestOptions;
    final shouldRefresh =
        error.response?.statusCode == 401 &&
        request.extra['anonymous'] != true &&
        request.extra['retried'] != true &&
        !request.path.endsWith('/auth/refresh');
    if (!shouldRefresh) {
      handler.next(error);
      return;
    }

    final accessToken = await _refreshAccessToken();
    if (accessToken == null) {
      handler.next(error);
      return;
    }

    request.extra['retried'] = true;
    request.headers['Authorization'] = 'Bearer $accessToken';
    try {
      final response = await _dio.fetch<Object?>(request);
      handler.resolve(response);
    } on DioException catch (retryError) {
      handler.next(retryError);
    }
  }

  Future<String?> _refreshAccessToken() {
    final activeRefresh = _refreshFuture;
    if (activeRefresh != null) {
      return activeRefresh;
    }
    final refresh = _performRefresh();
    _refreshFuture = refresh;
    return refresh.whenComplete(() => _refreshFuture = null);
  }

  Future<String?> _performRefresh() async {
    final refreshToken = await _tokenStore.readRefreshToken();
    if (refreshToken == null) {
      return null;
    }
    try {
      final response = await _refreshDio.post<Map<String, dynamic>>(
        '/auth/refresh',
        data: <String, dynamic>{'refresh_token': refreshToken},
      );
      final data = response.data;
      final accessToken = data?['access_token'] as String?;
      final rotatedRefreshToken = data?['refresh_token'] as String?;
      if (accessToken == null || rotatedRefreshToken == null) {
        await _tokenStore.clear();
        return null;
      }
      await _tokenStore.save(
        accessToken: accessToken,
        refreshToken: rotatedRefreshToken,
      );
      return accessToken;
    } on DioException {
      await _tokenStore.clear();
      return null;
    }
  }

  ApiException mapError(Object error) {
    if (error is ApiException) {
      return error;
    }
    if (error is DioException) {
      final response = error.response;
      final payload = response?.data;
      return ApiException(
        message: _networkMessage(error, payload),
        statusCode: response?.statusCode,
        payload: payload,
        retryAfterSeconds: _parseRetryAfter(response?.headers),
      );
    }
    return ApiException(message: error.toString());
  }

  String _networkMessage(DioException error, Object? payload) {
    if (payload is Map) {
      return _extractMessage(payload);
    }
    return switch (error.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout =>
        'الخادم استغرق وقتًا أطول من المتوقع. حاول مرة أخرى.',
      DioExceptionType.connectionError =>
        'تعذر الوصول إلى الخادم. تحقق من الإنترنت وحاول مجددًا.',
      _ => 'تعذر الاتصال بالخادم. حاول مرة أخرى.',
    };
  }

  String _extractMessage(Object? payload) {
    const fallback = 'تعذر الاتصال بالخادم. حاول مرة أخرى.';
    if (payload is! Map) {
      return fallback;
    }
    final detail = payload['detail'];
    if (detail is String && detail.trim().isNotEmpty) {
      return detail.trim();
    }
    if (detail is List) {
      final messages = detail
          .map((item) {
            if (item is Map) {
              final message = item['msg'];
              if (message is String && message.trim().isNotEmpty) {
                return message.trim();
              }
            }
            return null;
          })
          .whereType<String>()
          .toList(growable: false);
      if (messages.isNotEmpty) {
        return messages.join('\n');
      }
    }
    return fallback;
  }

  int? _parseRetryAfter(Headers? headers) {
    if (headers == null) {
      return null;
    }
    return int.tryParse(headers.value('retry-after') ?? '');
  }
}

final apiClientProvider = Provider<ApiClient>((ref) {
  final config = ref.watch(appConfigProvider);
  final tokenStore = ref.watch(tokenStoreProvider);
  return ApiClient(baseUrl: config.apiBaseUrl, tokenStore: tokenStore);
});

```

---

### File: `lib\core\network\api_exception.dart`

```dart
class ApiException implements Exception {
  const ApiException({
    required this.message,
    this.statusCode,
    this.payload,
    this.retryAfterSeconds,
  });

  final String message;
  final int? statusCode;
  final Object? payload;
  final int? retryAfterSeconds;

  @override
  String toString() => 'ApiException($statusCode): $message';
}

```

---

### File: `lib\core\network\token_store.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StoredTokens {
  const StoredTokens({required this.accessToken, required this.refreshToken});

  final String accessToken;
  final String refreshToken;
}

class TokenStore {
  TokenStore(this._storage);

  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  final FlutterSecureStorage _storage;

  Future<StoredTokens?> read() async {
    try {
      final values = await _storage.readAll();
      final accessToken = values[_accessKey];
      final refreshToken = values[_refreshKey];
      if (accessToken == null || refreshToken == null) {
        return null;
      }
      return StoredTokens(accessToken: accessToken, refreshToken: refreshToken);
    } on Object {
      return null;
    }
  }

  Future<String?> readAccessToken() => _storage.read(key: _accessKey);

  Future<String?> readRefreshToken() => _storage.read(key: _refreshKey);

  Future<void> save({
    required String accessToken,
    required String refreshToken,
  }) async {
    await Future.wait([
      _storage.write(key: _accessKey, value: accessToken),
      _storage.write(key: _refreshKey, value: refreshToken),
    ]);
  }

  Future<void> clear() async {
    await Future.wait([
      _storage.delete(key: _accessKey),
      _storage.delete(key: _refreshKey),
    ]);
  }
}

final tokenStoreProvider = Provider<TokenStore>((ref) {
  const storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );
  return TokenStore(storage);
});

```

---

### File: `lib\core\observability\app_observability.dart`

```dart
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

class AppObservability {
  AppObservability._();

  static const String dsn = String.fromEnvironment('SENTRY_DSN');
  static const String environment = String.fromEnvironment(
    'APP_ENV',
    defaultValue: 'development',
  );
  static const String release = String.fromEnvironment('SENTRY_RELEASE');
  static const String _traceSampleRate = String.fromEnvironment(
    'SENTRY_TRACES_SAMPLE_RATE',
    defaultValue: '0.0',
  );

  static bool get enabled => dsn.trim().isNotEmpty;

  static double get tracesSampleRate => parseSampleRate(_traceSampleRate);

  static double parseSampleRate(String raw) {
    final value = double.tryParse(raw) ?? 0;
    return value.clamp(0.0, 1.0).toDouble();
  }

  static List<NavigatorObserver> get navigatorObservers => enabled
      ? <NavigatorObserver>[SentryNavigatorObserver()]
      : const <NavigatorObserver>[];

  static Future<void> bootstrap({
    required Future<void> Function() initializeServices,
    required Widget app,
  }) async {
    ErrorWidget.builder = buildErrorWidget;

    Future<void> appRunner() async {
      await initializeServices();
      runApp(app);
    }

    if (!enabled) {
      FlutterError.onError = FlutterError.presentError;
      ui.PlatformDispatcher.instance.onError = (error, stack) {
        debugPrint('Uncaught platform error: $error\n$stack');
        return false;
      };
      await appRunner();
      return;
    }

    await SentryFlutter.init((options) {
      options.dsn = dsn;
      options.environment = environment;
      if (release.trim().isNotEmpty) {
        options.release = release;
      }
      options.tracesSampleRate = tracesSampleRate;
      options.sendDefaultPii = false;
      options.attachScreenshot = false;
      options.enableAutoSessionTracking = true;
    }, appRunner: appRunner);
  }

  @visibleForTesting
  static Widget buildErrorWidget(FlutterErrorDetails details) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: ColoredBox(
        color: const Color(0xFFF7F2EA),
        child: Center(
          child: Semantics(
            liveRegion: true,
            label: 'حدث خطأ غير متوقع. حاول فتح الشاشة مرة أخرى.',
            child: const Padding(
              padding: EdgeInsets.all(24),
              child: Text(
                'حدث خطأ غير متوقع\nحاول فتح الشاشة مرة أخرى.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, height: 1.5),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

```

---

### File: `lib\core\ui\app_notice.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';

enum AppNoticeTone { success, error, warning, info }

class AppNotice {
  AppNotice._();

  static OverlayEntry? _activeEntry;
  static Timer? _dismissTimer;

  static void show(
    BuildContext context, {
    required String message,
    String? title,
    AppNoticeTone tone = AppNoticeTone.info,
    Duration duration = const Duration(seconds: 4),
  }) {
    _dismissTimer?.cancel();
    _removeActive();

    final overlay = Overlay.maybeOf(context, rootOverlay: true);
    if (overlay == null) {
      return;
    }

    late final OverlayEntry entry;
    entry = OverlayEntry(
      builder: (overlayContext) => _AppNoticeBanner(
        title: title,
        message: message,
        tone: tone,
        onDismiss: () {
          if (identical(_activeEntry, entry)) {
            _dismissTimer?.cancel();
            _activeEntry = null;
          }
          entry.remove();
        },
      ),
    );
    _activeEntry = entry;
    overlay.insert(entry);
    _dismissTimer = Timer(duration, () {
      if (identical(_activeEntry, entry)) {
        _removeActive();
      }
    });
  }

  static void _removeActive() {
    _dismissTimer?.cancel();
    _dismissTimer = null;
    final entry = _activeEntry;
    _activeEntry = null;
    entry?.remove();
  }
}

class _AppNoticeBanner extends StatefulWidget {
  const _AppNoticeBanner({
    required this.message,
    required this.tone,
    required this.onDismiss,
    this.title,
  });

  final String? title;
  final String message;
  final AppNoticeTone tone;
  final VoidCallback onDismiss;

  @override
  State<_AppNoticeBanner> createState() => _AppNoticeBannerState();
}

class _AppNoticeBannerState extends State<_AppNoticeBanner>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<Offset> _slide;
  late final Animation<double> _fade;
  bool _closing = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 280),
      reverseDuration: const Duration(milliseconds: 180),
    );
    final curve = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
      reverseCurve: Curves.easeInCubic,
    );
    _slide = Tween<Offset>(
      begin: const Offset(0, -1.15),
      end: Offset.zero,
    ).animate(curve);
    _fade = Tween<double>(begin: 0, end: 1).animate(curve);
    _controller.forward();
  }

  Future<void> _dismiss() async {
    if (_closing) {
      return;
    }
    _closing = true;
    await _controller.reverse();
    widget.onDismiss();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final palette = _palette(theme.colorScheme, widget.tone);
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        minimum: const EdgeInsets.fromLTRB(14, 10, 14, 0),
        child: SlideTransition(
          position: _slide,
          child: FadeTransition(
            opacity: _fade,
            child: Material(
              color: Colors.transparent,
              child: Container(
                constraints: const BoxConstraints(maxWidth: 560),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                padding: const EdgeInsetsDirectional.fromSTEB(16, 14, 8, 14),
                decoration: BoxDecoration(
                  color: palette.background,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: palette.border),
                  boxShadow: const [
                    BoxShadow(
                      blurRadius: 24,
                      offset: Offset(0, 10),
                      color: Color(0x24000000),
                    ),
                  ],
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: palette.iconBackground,
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: Icon(palette.icon, color: palette.foreground),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (widget.title?.trim().isNotEmpty == true) ...[
                            Text(
                              widget.title!,
                              style: theme.textTheme.titleSmall?.copyWith(
                                color: palette.foreground,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 3),
                          ],
                          Text(
                            widget.message,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: palette.foreground,
                              height: 1.45,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      tooltip: 'إغلاق',
                      onPressed: _dismiss,
                      visualDensity: VisualDensity.compact,
                      icon: Icon(
                        Icons.close_rounded,
                        color: palette.foreground.withValues(alpha: 0.75),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

_NoticePalette _palette(ColorScheme scheme, AppNoticeTone tone) {
  return switch (tone) {
    AppNoticeTone.success => const _NoticePalette(
      background: Color(0xFFF0F9F4),
      border: Color(0xFFB8DFC9),
      iconBackground: Color(0xFFD8F0E2),
      foreground: Color(0xFF145A43),
      icon: Icons.check_circle_rounded,
    ),
    AppNoticeTone.error => _NoticePalette(
      background: scheme.errorContainer,
      border: scheme.error.withValues(alpha: 0.28),
      iconBackground: scheme.error.withValues(alpha: 0.12),
      foreground: scheme.onErrorContainer,
      icon: Icons.error_rounded,
    ),
    AppNoticeTone.warning => const _NoticePalette(
      background: Color(0xFFFFF8E7),
      border: Color(0xFFF0D391),
      iconBackground: Color(0xFFFFE8B1),
      foreground: Color(0xFF6B4B00),
      icon: Icons.warning_amber_rounded,
    ),
    AppNoticeTone.info => _NoticePalette(
      background: scheme.surfaceContainerHighest,
      border: scheme.outlineVariant,
      iconBackground: scheme.primary.withValues(alpha: 0.12),
      foreground: scheme.onSurface,
      icon: Icons.info_rounded,
    ),
  };
}

class _NoticePalette {
  const _NoticePalette({
    required this.background,
    required this.border,
    required this.iconBackground,
    required this.foreground,
    required this.icon,
  });

  final Color background;
  final Color border;
  final Color iconBackground;
  final Color foreground;
  final IconData icon;
}

```

---

### File: `lib\data\backend_repository.dart`

```dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/network/api_client.dart';
import '../core/network/api_exception.dart';
import '../core/network/token_store.dart';
import '../domain/models.dart';

class BackendRepository {
  BackendRepository({
    required ApiClient apiClient,
    required TokenStore tokenStore,
  }) : _apiClient = apiClient,
       _tokenStore = tokenStore;

  final ApiClient _apiClient;
  final TokenStore _tokenStore;

  Future<RegistrationResult> register({
    required String email,
    required String password,
    required String displayName,
    String avatarKey = 'avatar_01',
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/auth/register',
        data: <String, dynamic>{
          'email': email.trim(),
          'password': password,
          'display_name': displayName.trim(),
          'avatar_key': avatarKey,
        },
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );
      return RegistrationResult.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<String> verifyEmail({required String email, required String code}) {
    return _anonymousMessage(
      path: '/auth/verify-email',
      data: <String, dynamic>{'email': email.trim(), 'code': code.trim()},
    );
  }

  Future<String> resendVerification(String email) {
    return _anonymousMessage(
      path: '/auth/resend-verification',
      data: <String, dynamic>{'email': email.trim()},
    );
  }

  Future<String> forgotPassword(String email) {
    return _anonymousMessage(
      path: '/auth/forgot-password',
      data: <String, dynamic>{'email': email.trim()},
    );
  }

  Future<String> resetPassword({
    required String email,
    required String code,
    required String newPassword,
  }) {
    return _anonymousMessage(
      path: '/auth/reset-password',
      data: <String, dynamic>{
        'email': email.trim(),
        'code': code.trim(),
        'new_password': newPassword,
      },
    );
  }

  Future<TokenPair> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/auth/login',
        data: <String, dynamic>{'email': email.trim(), 'password': password},
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );
      final tokens = TokenPair.fromJson(_requiredData(response));
      await _tokenStore.save(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );
      return tokens;
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> logout() async {
    final refreshToken = await _tokenStore.readRefreshToken();
    try {
      if (refreshToken != null) {
        await _apiClient.dio.post<Map<String, dynamic>>(
          '/auth/logout',
          data: <String, dynamic>{'refresh_token': refreshToken},
        );
      }
    } on Object {
      // Local logout must still complete if the network is unavailable.
    } finally {
      await _tokenStore.clear();
    }
  }

  Future<UserProfile> getProfile() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/profile/me',
      );
      return UserProfile.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AvatarOption>> getAvatarOptions() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/profile/avatars',
      );
      final payload = _requiredData(response);
      final rawItems = payload['avatars'];
      if (rawItems is! List) {
        throw const ApiException(message: 'قائمة الصور الرمزية غير صالحة.');
      }
      return rawItems
          .map((item) => AvatarOption.fromJson(_requiredMap(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<UserProfile> updateProfile({
    required String displayName,
    required String avatarKey,
  }) async {
    try {
      final response = await _apiClient.dio.patch<Map<String, dynamic>>(
        '/profile/me',
        data: <String, dynamic>{
          'display_name': displayName.trim(),
          'avatar_key': avatarKey,
        },
      );
      return UserProfile.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<WalletSummary> getWallet() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/wallet',
      );
      return WalletSummary.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<WalletHistoryPage> getWalletHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/wallet/history',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return WalletHistoryPage.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<MarketInstrument>> searchInstruments(
    String query, {
    int limit = 30,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/instruments',
        queryParameters: <String, dynamic>{
          'query': query.trim().toUpperCase(),
          'limit': limit,
        },
      );
      final payload = _requiredData(response);
      final rawItems = payload['items'];
      if (rawItems is! List) {
        throw const ApiException(message: 'قائمة الأسهم غير صالحة.');
      }
      return rawItems
          .map((item) => MarketInstrument.fromJson(_requiredMap(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<StockAnalysisResult> analyzeStock(String ticker) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/stocks/${ticker.trim().toUpperCase()}/analysis',
        data: const <String, dynamic>{'language': 'ar'},
      );
      return StockAnalysisResult.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<StockAnalysisResult?> getLatestOwnedStockAnalysis(
    String ticker,
  ) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/stocks/${ticker.trim().toUpperCase()}/analysis/latest',
      );
      return StockAnalysisResult.fromJson(_requiredData(response));
    } on DioException catch (error) {
      if (error.response?.statusCode == 404) {
        return null;
      }
      throw _apiClient.mapError(error);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketReportPreview?> getLatestReportPreview() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/reports/latest/preview',
      );
      return MarketReportPreview.fromJson(_requiredData(response));
    } on DioException catch (error) {
      if (error.response?.statusCode == 404) {
        return null;
      }
      throw _apiClient.mapError(error);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketReport> getMarketReport(String reportId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/reports/$reportId',
      );
      return MarketReport.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketQuotesSnapshot> getMarketQuotes() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/quotes',
      );
      return MarketQuotesSnapshot.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketQuote> getMarketQuote(
    String ticker, {
    bool forceRefresh = false,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/quotes/${ticker.trim().toUpperCase()}',
        queryParameters: <String, dynamic>{
          if (forceRefresh) 'force_refresh': 'true',
        },
      );
      return MarketQuote.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketReportUnlockResult> unlockMarketReport(String reportId) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/market/reports/$reportId/unlock',
      );
      return MarketReportUnlockResult.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<String> _anonymousMessage({
    required String path,
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        path,
        data: data,
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );
      return (_requiredData(response)['message'] as String?) ??
          'تم تنفيذ الطلب.';
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

Map<String, dynamic> _requiredData(Response<Map<String, dynamic>> response) {
  final data = response.data;
  if (data == null) {
    throw const ApiException(message: 'استجابة الخادم غير صالحة.');
  }
  return data;
}

Map<String, dynamic> _requiredMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return value.map((key, item) => MapEntry(key.toString(), item));
  }
  throw const ApiException(message: 'صيغة البيانات غير صالحة.');
}

final backendRepositoryProvider = Provider<BackendRepository>((ref) {
  return BackendRepository(
    apiClient: ref.watch(apiClientProvider),
    tokenStore: ref.watch(tokenStoreProvider),
  );
});

```

---

### File: `lib\domain\models.dart`

```dart
class TokenPair {
  const TokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  final String accessToken;
  final String refreshToken;
  final int expiresIn;

  factory TokenPair.fromJson(Map<String, dynamic> json) {
    return TokenPair(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      expiresIn: json['expires_in'] as int,
    );
  }
}

class RegistrationResult {
  const RegistrationResult({
    required this.userId,
    required this.email,
    required this.requiresEmailVerification,
    required this.weeklyPointsGranted,
  });

  final String userId;
  final String email;
  final bool requiresEmailVerification;
  final int weeklyPointsGranted;

  factory RegistrationResult.fromJson(Map<String, dynamic> json) {
    return RegistrationResult(
      userId: json['user_id'] as String,
      email: json['email'] as String,
      requiresEmailVerification:
          json['requires_email_verification'] as bool? ?? true,
      weeklyPointsGranted: json['weekly_points_granted'] as int? ?? 300,
    );
  }
}

class UserProfile {
  const UserProfile({
    required this.id,
    required this.email,
    required this.displayName,
    required this.avatarKey,
    required this.emailVerified,
    this.isAdmin = false,
    required this.planCode,
    required this.balancePoints,
    required this.balanceCoins,
    required this.weeklyCoins,
    required this.adsEnabled,
  });

  final String id;
  final String email;
  final String displayName;
  final String avatarKey;
  final bool emailVerified;
  final bool isAdmin;
  final String planCode;
  final int balancePoints;
  final String balanceCoins;
  final String weeklyCoins;
  final bool adsEnabled;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String,
      avatarKey: json['avatar_key'] as String,
      emailVerified: json['email_verified'] as bool,
      isAdmin: json['is_admin'] as bool? ?? false,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
    );
  }
}

class AvatarOption {
  const AvatarOption({required this.key, required this.assetPath});

  final String key;
  final String assetPath;

  factory AvatarOption.fromJson(Map<String, dynamic> json) {
    return AvatarOption(
      key: json['key'] as String,
      assetPath: json['asset_path'] as String,
    );
  }
}

class WalletSummary {
  const WalletSummary({
    required this.balancePoints,
    required this.balanceCoins,
    required this.planCode,
    required this.weeklyCoins,
    required this.adsEnabled,
  });

  final int balancePoints;
  final String balanceCoins;
  final String planCode;
  final String weeklyCoins;
  final bool adsEnabled;

  factory WalletSummary.fromJson(Map<String, dynamic> json) {
    return WalletSummary(
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      planCode: json['plan_code'] as String,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
    );
  }
}

class WalletEntryModel {
  const WalletEntryModel({
    required this.transactionId,
    required this.entryType,
    required this.amountPoints,
    required this.amountCoins,
    required this.status,
    required this.referenceType,
    required this.referenceId,
    required this.details,
    required this.createdAt,
    required this.confirmedAt,
  });

  final String transactionId;
  final String entryType;
  final int amountPoints;
  final String amountCoins;
  final String status;
  final String? referenceType;
  final String? referenceId;
  final Map<String, dynamic> details;
  final DateTime createdAt;
  final DateTime? confirmedAt;

  factory WalletEntryModel.fromJson(Map<String, dynamic> json) {
    return WalletEntryModel(
      transactionId: json['transaction_id'] as String,
      entryType: json['entry_type'] as String,
      amountPoints: json['amount_points'] as int,
      amountCoins: json['amount_coins'] as String,
      status: json['status'] as String,
      referenceType: json['reference_type'] as String?,
      referenceId: json['reference_id'] as String?,
      details: _map(json['details']),
      createdAt: DateTime.parse(json['created_at'] as String),
      confirmedAt: json['confirmed_at'] == null
          ? null
          : DateTime.parse(json['confirmed_at'] as String),
    );
  }
}

class WalletHistoryPage {
  const WalletHistoryPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<WalletEntryModel> items;
  final int total;
  final int limit;
  final int offset;

  factory WalletHistoryPage.fromJson(Map<String, dynamic> json) {
    return WalletHistoryPage(
      items: _list(json['items'])
          .map((item) => WalletEntryModel.fromJson(_map(item)))
          .toList(growable: false),
      total: json['total'] as int,
      limit: json['limit'] as int,
      offset: json['offset'] as int,
    );
  }
}

class MarketInstrument {
  const MarketInstrument({
    required this.ticker,
    required this.providerSymbol,
    required this.exchange,
    this.description = '',
  });

  final String ticker;
  final String providerSymbol;
  final String exchange;
  final String description;

  factory MarketInstrument.fromJson(Map<String, dynamic> json) {
    return MarketInstrument(
      ticker: json['ticker'] as String,
      providerSymbol: json['provider_symbol'] as String,
      exchange: json['exchange'] as String,
      description: json['description'] as String? ?? '',
    );
  }
}

class MarketQuote {
  const MarketQuote({
    required this.ticker,
    required this.description,
    required this.exchange,
    this.sector,
    this.currentPrice,
    this.openPrice,
    this.previousClose,
    this.sessionHigh,
    this.sessionLow,
    this.change,
    this.changePercent,
    this.volume,
    this.week52High,
    this.week52Low,
    this.marketOpen = false,
    this.sessionChangePercent,
    this.sessionDate,
    this.nextSessionOpen,
  });

  final String ticker;
  final String description;
  final String exchange;
  final String? sector;
  final double? currentPrice;
  final double? openPrice;
  final double? previousClose;
  final double? sessionHigh;
  final double? sessionLow;
  final double? change;
  final double? changePercent;
  final double? volume;
  final double? week52High;
  final double? week52Low;
  final bool marketOpen;
  final double? sessionChangePercent;
  final String? sessionDate;
  final DateTime? nextSessionOpen;

  factory MarketQuote.fromJson(Map<String, dynamic> json) {
    return MarketQuote(
      ticker: json['ticker'] as String,
      description: json['description'] as String? ?? '',
      exchange: json['exchange'] as String? ?? 'EGX',
      sector: json['sector'] as String?,
      currentPrice: _asDouble(json['current_price']),
      openPrice: _asDouble(json['open_price']),
      previousClose: _asDouble(json['previous_close']),
      sessionHigh: _asDouble(json['session_high']),
      sessionLow: _asDouble(json['session_low']),
      change: _asDouble(json['change']),
      changePercent: _asDouble(json['change_percent']),
      volume: _asDouble(json['volume']),
      week52High: _asDouble(json['week52_high']),
      week52Low: _asDouble(json['week52_low']),
      marketOpen: json['market_open'] as bool? ?? false,
      sessionChangePercent: _asDouble(json['session_change_percent']),
      sessionDate: json['session_date'] as String?,
      nextSessionOpen: json['next_session_open'] == null
          ? null
          : DateTime.tryParse(json['next_session_open'] as String),
    );
  }
}

class MarketQuotesSnapshot {
  const MarketQuotesSnapshot({
    required this.source,
    required this.generatedAt,
    required this.marketOpen,
    required this.items,
    this.nextSessionOpen,
  });

  final String source;
  final DateTime generatedAt;
  final bool marketOpen;
  final DateTime? nextSessionOpen;
  final List<MarketQuote> items;

  factory MarketQuotesSnapshot.fromJson(Map<String, dynamic> json) {
    return MarketQuotesSnapshot(
      source: json['source'] as String,
      generatedAt: DateTime.parse(json['generated_at'] as String),
      marketOpen: json['market_open'] as bool? ?? false,
      nextSessionOpen: json['next_session_open'] == null
          ? null
          : DateTime.tryParse(json['next_session_open'] as String),
      items: _list(
        json['items'],
      ).map((item) => MarketQuote.fromJson(_map(item))).toList(growable: false),
    );
  }
}

class StockAnalysisResult {
  const StockAnalysisResult({
    required this.analysisId,
    required this.ticker,
    required this.cached,
    required this.marketSnapshotCached,
    required this.chargedPoints,
    required this.chargedCoins,
    required this.balancePoints,
    required this.balanceCoins,
    required this.dataAsOf,
    required this.payload,
  });

  final String analysisId;
  final String ticker;
  final bool cached;
  final bool marketSnapshotCached;
  final int chargedPoints;
  final String chargedCoins;
  final int balancePoints;
  final String balanceCoins;
  final DateTime dataAsOf;
  final Map<String, dynamic> payload;

  factory StockAnalysisResult.fromJson(Map<String, dynamic> json) {
    return StockAnalysisResult(
      analysisId: json['analysis_id'] as String,
      ticker: json['ticker'] as String,
      cached: json['cached'] as bool,
      marketSnapshotCached: json['market_snapshot_cached'] as bool,
      chargedPoints: json['charged_points'] as int,
      chargedCoins: json['charged_coins'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      dataAsOf: DateTime.parse(json['data_as_of'] as String),
      payload: _map(json['payload']),
    );
  }
}

class MarketReportPreview {
  const MarketReportPreview({
    required this.reportId,
    required this.sourceSessionDate,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.status,
    required this.itemCount,
    required this.unlocked,
    required this.unlockCostPoints,
    required this.unlockCostCoins,
    required this.marketSummary,
  });

  final String reportId;
  final DateTime sourceSessionDate;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final String status;
  final int itemCount;
  final bool unlocked;
  final int unlockCostPoints;
  final String unlockCostCoins;
  final Map<String, dynamic> marketSummary;

  factory MarketReportPreview.fromJson(Map<String, dynamic> json) {
    return MarketReportPreview(
      reportId: json['report_id'] as String,
      sourceSessionDate: DateTime.parse(json['source_session_date'] as String),
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      status: json['status'] as String,
      itemCount: json['item_count'] as int,
      unlocked: json['unlocked'] as bool,
      unlockCostPoints: json['unlock_cost_points'] as int,
      unlockCostCoins: json['unlock_cost_coins'] as String,
      marketSummary: _map(json['market_summary']),
    );
  }
}

class MarketReportItem {
  const MarketReportItem({
    required this.ticker,
    required this.rank,
    required this.score,
    required this.payload,
  });

  final String ticker;
  final int rank;
  final double score;
  final Map<String, dynamic> payload;

  factory MarketReportItem.fromJson(Map<String, dynamic> json) {
    return MarketReportItem(
      ticker: json['ticker'] as String,
      rank: json['rank'] as int,
      score: (json['score'] as num).toDouble(),
      payload: _map(json['payload']),
    );
  }
}

class MarketReport {
  const MarketReport({
    required this.reportId,
    required this.sourceSessionDate,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.marketSummary,
    required this.items,
    required this.extendedItems,
  });

  final String reportId;
  final DateTime sourceSessionDate;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final Map<String, dynamic> marketSummary;
  final List<MarketReportItem> items;
  final List<MarketReportItem> extendedItems;

  factory MarketReport.fromJson(Map<String, dynamic> json) {
    return MarketReport(
      reportId: json['report_id'] as String,
      sourceSessionDate: DateTime.parse(json['source_session_date'] as String),
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      marketSummary: _map(json['market_summary']),
      items: _list(json['items'])
          .map((item) => MarketReportItem.fromJson(_map(item)))
          .toList(growable: false),
      extendedItems: _list(json['extended_items'])
          .map((item) => MarketReportItem.fromJson(_map(item)))
          .toList(growable: false),
    );
  }
}

class MarketReportUnlockResult {
  const MarketReportUnlockResult({
    required this.chargedPoints,
    required this.chargedCoins,
    required this.balancePoints,
    required this.balanceCoins,
    required this.report,
  });

  final int chargedPoints;
  final String chargedCoins;
  final int balancePoints;
  final String balanceCoins;
  final MarketReport report;

  factory MarketReportUnlockResult.fromJson(Map<String, dynamic> json) {
    return MarketReportUnlockResult(
      chargedPoints: json['charged_points'] as int,
      chargedCoins: json['charged_coins'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      report: MarketReport.fromJson(_map(json['report'])),
    );
  }
}

double? _asDouble(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  if (value is String) {
    return double.tryParse(value);
  }
  return null;
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

List<dynamic> _list(Object? value) {
  return value is List ? value : const <dynamic>[];
}

```

---

### File: `lib\features\admin\admin_dashboard_screen.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import 'admin_models.dart';
import 'admin_providers.dart';
import 'admin_repository.dart';
import 'historical_replay_models.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 7,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مركز الإدارة'),
          actions: [
            IconButton(
              onPressed: () => context.push('/admin/performance'),
              icon: const Icon(Icons.assessment_outlined),
              tooltip: 'تشغيل سجل الأداء',
            ),
          ],
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'نظرة عامة'),
              Tab(text: 'المراجعة'),
              Tab(text: 'المستخدمون'),
              Tab(text: 'الإعدادات'),
              Tab(text: 'الإشعارات'),
              Tab(text: 'التدقيق'),
              Tab(text: 'وظائف إعادة اللعب'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            _OverviewTab(),
            _ModerationTab(),
            _UsersTab(),
            _SettingsTab(),
            _BroadcastTab(),
            _AuditTab(),
            _ReplayJobsTab(),
          ],
        ),
      ),
    );
  }
}

class _OverviewTab extends ConsumerWidget {
  const _OverviewTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final overview = ref.watch(adminOverviewProvider);
    final providers = ref.watch(adminProvidersProvider);
    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(adminOverviewProvider);
        ref.invalidate(adminProvidersProvider);
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          overview.when(
            loading: () => const _Loading(),
            error: (_, __) => const _Failure('تعذر تحميل مؤشرات الإدارة.'),
            data: (item) => Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _Metric('المستخدمون', item.usersTotal),
                _Metric('النشطون', item.usersActive),
                _Metric('الموقوفون', item.usersSuspended),
                _Metric('قيد المراجعة', item.discussionsPending),
                _Metric('البلاغات المفتوحة', item.openReports),
                _Metric('الاستئنافات', item.openAppeals),
                _Metric('توقعات متحققة', item.verifiedPredictions),
                _Metric('إشعارات اليوم', item.notificationsToday),
              ],
            ),
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              const Expanded(child: Text('حالة المزودات')),
              FilledButton.icon(
                onPressed: () async {
                  await ref
                      .read(adminRepositoryProvider)
                      .providers(probe: true);
                  ref.invalidate(adminProvidersProvider);
                },
                icon: const Icon(Icons.health_and_safety_outlined),
                label: const Text('فحص الآن'),
              ),
            ],
          ),
          const SizedBox(height: 10),
          providers.when(
            loading: () => const _Loading(),
            error: (_, __) => const _Failure('لا توجد حالة مزودات متاحة.'),
            data: (items) => Column(
              children: items
                  .map(
                    (item) => Card(
                      child: ListTile(
                        leading: Icon(
                          item.status == 'healthy'
                              ? Icons.check_circle_outline
                              : item.status == 'degraded'
                              ? Icons.warning_amber_rounded
                              : Icons.error_outline,
                        ),
                        title: Text('${item.component} — ${item.provider}'),
                        subtitle: Text(
                          '${item.status} • ${item.latencyMs ?? '-'} ms',
                        ),
                      ),
                    ),
                  )
                  .toList(growable: false),
            ),
          ),
        ],
      ),
    );
  }
}

class _ModerationTab extends ConsumerWidget {
  const _ModerationTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final discussions = ref.watch(adminDiscussionsProvider);
    return discussions.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل طابور المراجعة.'),
      data: (items) => RefreshIndicator(
        onRefresh: () async => ref.invalidate(adminDiscussionsProvider),
        child: items.isEmpty
            ? ListView(
                children: const [
                  SizedBox(height: 100),
                  Center(child: Text('الطابور فارغ.')),
                ],
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: items.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) {
                  final item = items[index];
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            '${item.discussion.ticker} — ${item.discussion.title}',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          Text(item.discussion.content),
                          if (item.openReportCount > 0)
                            Text('بلاغات مفتوحة: ${item.openReportCount}'),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: FilledButton(
                                  onPressed: () => _approve(context, ref, item),
                                  child: const Text('قبول'),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: OutlinedButton(
                                  onPressed: () => _reject(context, ref, item),
                                  child: const Text('رفض'),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
      ),
    );
  }

  Future<void> _approve(
    BuildContext context,
    WidgetRef ref,
    AdminDiscussionItem item,
  ) async {
    final direction = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('اتجاه التوقع'),
        children: [
          for (final value in const ['up', 'down', 'neutral'])
            SimpleDialogOption(
              onPressed: () => Navigator.pop(context, value),
              child: Text(value),
            ),
        ],
      ),
    );
    if (direction == null || !context.mounted) return;
    await _run(
      context,
      () => ref
          .read(adminRepositoryProvider)
          .moderateDiscussion(
            discussionId: item.discussion.id,
            action: 'approve',
            prediction: <String, dynamic>{
              'direction': direction,
              'target_price': item.discussion.frozenPrediction['target_price'],
              'deadline': item.discussion.frozenPrediction['deadline'],
              'claims':
                  item.discussion.frozenPrediction['claims'] ?? <String>[],
              'specificity':
                  item.discussion.frozenPrediction['specificity'] ?? 0.5,
            },
          ),
    );
    ref.invalidate(adminDiscussionsProvider);
    ref.invalidate(adminOverviewProvider);
  }

  Future<void> _reject(
    BuildContext context,
    WidgetRef ref,
    AdminDiscussionItem item,
  ) async {
    await _run(
      context,
      () => ref
          .read(adminRepositoryProvider)
          .moderateDiscussion(
            discussionId: item.discussion.id,
            action: 'reject',
            reasonCode: 'manual_rejection',
          ),
    );
    ref.invalidate(adminDiscussionsProvider);
    ref.invalidate(adminOverviewProvider);
  }
}

class _UsersTab extends ConsumerWidget {
  const _UsersTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final users = ref.watch(adminUsersProvider);
    return users.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل المستخدمين.'),
      data: (items) => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final user = items[index];
          final blocked = user.status == 'suspended';
          return Card(
            child: ListTile(
              title: Text(user.displayName),
              subtitle: Text(
                '${user.email}\n${user.planCode} • ${user.balancePoints} نقطة • ${user.discussionsCount} مناقشة',
              ),
              isThreeLine: true,
              trailing: OutlinedButton(
                onPressed: () async {
                  await _run(
                    context,
                    () => ref
                        .read(adminRepositoryProvider)
                        .setUserBlocked(user, !blocked),
                  );
                  ref.invalidate(adminUsersProvider);
                },
                child: Text(blocked ? 'إلغاء الحظر' : 'حظر'),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _SettingsTab extends ConsumerWidget {
  const _SettingsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(adminSettingsProvider);
    return settings.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل الإعدادات.'),
      data: (items) => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final item = items[index];
          return Card(
            child: ListTile(
              title: Text(item.label),
              subtitle: Text('${item.description}\nالقيمة: ${item.value}'),
              isThreeLine: true,
              trailing: const Icon(Icons.edit_outlined),
              onTap: () async {
                final value = await _editSetting(context, item);
                if (value == null || !context.mounted) return;
                await _run(
                  context,
                  () => ref
                      .read(adminRepositoryProvider)
                      .updateSetting(item.key, value),
                );
                ref.invalidate(adminSettingsProvider);
              },
            ),
          );
        },
      ),
    );
  }

  Future<Object?> _editSetting(
    BuildContext context,
    OperationalSetting item,
  ) async {
    if (item.kind == 'bool') {
      return showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(item.label),
          content: const Text('اختر حالة الإعداد.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('إيقاف'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('تفعيل'),
            ),
          ],
        ),
      );
    }
    final controller = TextEditingController(text: item.value.toString());
    return showDialog<Object>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(item.label),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () {
              final parsed = item.kind == 'float'
                  ? double.tryParse(controller.text)
                  : int.tryParse(controller.text);
              Navigator.pop(context, parsed);
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }
}

class _BroadcastTab extends ConsumerStatefulWidget {
  const _BroadcastTab();

  @override
  ConsumerState<_BroadcastTab> createState() => _BroadcastTabState();
}

class _BroadcastTabState extends ConsumerState<_BroadcastTab> {
  final _title = TextEditingController();
  final _body = TextEditingController();
  bool _busy = false;

  @override
  void dispose() {
    _title.dispose();
    _body.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        TextField(
          controller: _title,
          decoration: const InputDecoration(labelText: 'عنوان الإشعار'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _body,
          minLines: 4,
          maxLines: 8,
          decoration: const InputDecoration(labelText: 'نص الإشعار'),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          onPressed: _busy ? null : _send,
          icon: const Icon(Icons.campaign_outlined),
          label: const Text('إرسال للمستخدمين النشطين'),
        ),
      ],
    );
  }

  Future<void> _send() async {
    if (_title.text.trim().length < 3 || _body.text.trim().length < 3) return;
    setState(() => _busy = true);
    try {
      final result = await ref
          .read(adminRepositoryProvider)
          .broadcast(title: _title.text, body: _body.text);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم إنشاء ${result['notifications_created']} إشعار.'),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}

class _AuditTab extends ConsumerWidget {
  const _AuditTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final audit = ref.watch(adminAuditProvider);
    return audit.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل سجل التدقيق.'),
      data: (items) => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) => Card(
          child: ListTile(
            title: Text(items[index].action),
            subtitle: Text(
              '${items[index].reasonCode ?? ''}\n${items[index].details}',
            ),
            isThreeLine: true,
          ),
        ),
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric(this.label, this.value);
  final String label;
  final int value;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 155,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text('$value', style: Theme.of(context).textTheme.headlineMedium),
            Text(label, textAlign: TextAlign.center),
          ],
        ),
      ),
    ),
  );
}

class _Loading extends StatelessWidget {
  const _Loading();
  @override
  Widget build(BuildContext context) => const Padding(
    padding: EdgeInsets.all(32),
    child: Center(child: CircularProgressIndicator()),
  );
}

class _Failure extends StatelessWidget {
  const _Failure(this.message);
  final String message;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(32),
    child: Center(child: Text(message)),
  );
}

Future<void> _run(BuildContext context, Future<void> Function() action) async {
  try {
    await action();
    if (context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('تم تنفيذ الإجراء.')));
    }
  } on ApiException catch (error) {
    if (context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.message)));
    }
  }
}

class _ReplayJobsTab extends ConsumerStatefulWidget {
  const _ReplayJobsTab();

  @override
  ConsumerState<_ReplayJobsTab> createState() => _ReplayJobsTabState();
}

class _ReplayJobsTabState extends ConsumerState<_ReplayJobsTab> {
  late DateTime _startDate;
  late DateTime _endDate;
  int? _rank;
  String _exitMode = 'target_2';
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<HistoricalReplayJob> _jobs = const [];
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _previousMonth(notify: false);
    unawaited(_load());
    _pollTimer = Timer.periodic(
      const Duration(seconds: 8),
      (_) => unawaited(_load(silent: true)),
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load({bool silent = false}) async {
    if (!silent && mounted) setState(() => _loading = true);
    try {
      final jobs = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _loading = false;
        _error = null;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  void _previousMonth({bool notify = true}) {
    final firstCurrent = DateTime(DateTime.now().year, DateTime.now().month);
    final end = firstCurrent.subtract(const Duration(days: 1));
    final start = DateTime(end.year, end.month);
    if (notify) {
      setState(() {
        _startDate = start;
        _endDate = end;
      });
    } else {
      _startDate = start;
      _endDate = end;
    }
  }

  void _currentMonth() {
    final now = DateTime.now();
    setState(() {
      _startDate = DateTime(now.year, now.month);
      _endDate = DateTime(now.year, now.month, now.day);
    });
  }

  Future<void> _pickDate({required bool start}) async {
    final today = DateTime.now();
    final latestEnd = _startDate.add(const Duration(days: 45));
    final picked = await showDatePicker(
      context: context,
      initialDate: start
          ? _startDate
          : (_endDate.isAfter(latestEnd) ? latestEnd : _endDate),
      firstDate: start
          ? today.subtract(const Duration(days: 365 * 5))
          : _startDate,
      lastDate: start ? today : (latestEnd.isBefore(today) ? latestEnd : today),
      helpText: start ? 'اختر تاريخ البداية' : 'اختر تاريخ النهاية',
    );
    if (picked == null) return;
    setState(() {
      if (start) {
        _startDate = picked;
        if (_endDate.isBefore(picked)) _endDate = picked;
        if (_endDate.difference(picked).inDays > 45) {
          _endDate = picked.add(const Duration(days: 45));
        }
      } else {
        _endDate = picked;
      }
    });
  }

  bool _validateWindow() {
    final days = _endDate.difference(_startDate).inDays + 1;
    if (days < 1 || days > 45) {
      _message('الحد الأقصى لكل فترة هو 45 يومًا.');
      return false;
    }
    return true;
  }

  Future<void> _startLabsBacktest() async {
    if (!_validateWindow()) return;
    await _submit(() async {
      await ref
          .read(adminRepositoryProvider)
          .createLabsReplayJob(
            startDate: _startDate,
            endDate: _endDate,
            rank: _rank,
            exitMode: _exitMode,
          );
      _message('تم تشغيل محاكاة المختببرات على Worker منفصل.');
    });
  }

  Future<void> _submit(Future<void> Function() operation) async {
    setState(() => _submitting = true);
    try {
      await operation();
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) {
        _message(error is ApiException ? error.message : error.toString());
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _control(HistoricalReplayJob job, String action) async {
    try {
      final repository = ref.read(adminRepositoryProvider);
      switch (action) {
        case 'pause':
          await repository.pauseHistoricalReplay(job.id);
        case 'resume':
          await repository.resumeHistoricalReplay(job.id);
        case 'cancel':
          await repository.cancelHistoricalReplay(job.id);
      }
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) {
        _message(error is ApiException ? error.message : error.toString());
      }
    }
  }

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(text)));
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('d MMMM y', 'ar');
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'تشغيل محاكاة المختببرات (Worker منفصل)',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'محاكاة تقرير الـ10 اليومي على Worker الاختبارات المنفصل دون إبطاء مستخدمي التطبيق.',
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    children: [
                      OutlinedButton(
                        onPressed: _previousMonth,
                        child: const Text('الشهر السابق'),
                      ),
                      OutlinedButton(
                        onPressed: _currentMonth,
                        child: const Text('الشهر الحالي'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _pickDate(start: true),
                          child: Text('من\n${dateFormat.format(_startDate)}'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _pickDate(start: false),
                          child: Text('إلى\n${dateFormat.format(_endDate)}'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<int?>(
                    initialValue: _rank,
                    decoration: const InputDecoration(
                      labelText: 'رتبة السهم في التقرير (اختياري)',
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      const DropdownMenuItem<int?>(
                        value: null,
                        child: Text('كل الرتب (1-10)'),
                      ),
                      for (var r = 1; r <= 10; r++)
                        DropdownMenuItem<int?>(
                          value: r,
                          child: Text('الرتبة $r'),
                        ),
                    ],
                    onChanged: _submitting
                        ? null
                        : (value) => setState(() => _rank = value),
                  ),
                  const SizedBox(height: 12),
                  SegmentedButton<String>(
                    showSelectedIcon: false,
                    segments: const [
                      ButtonSegment(
                        value: 'target_2',
                        label: Text('الهدف الثاني'),
                      ),
                      ButtonSegment(value: 'highest', label: Text('أعلى هدف')),
                    ],
                    selected: <String>{_exitMode},
                    onSelectionChanged: _submitting
                        ? null
                        : (selection) =>
                              setState(() => _exitMode = selection.single),
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _submitting ? null : _startLabsBacktest,
                    icon: _submitting
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.play_arrow),
                    label: const Text('بدء المحاكاة'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'قائمة مهام Worker',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          if (_loading) const Center(child: CircularProgressIndicator()),
          if (_error != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: const Text('تعذر تحميل الوظائف'),
                subtitle: Text(_error!),
              ),
            ),
          if (!_loading && _jobs.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('لا توجد مهام مسجلة.')),
              ),
            ),
          for (final job in _jobs)
            Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            '${dateFormat.format(job.startDate)} — ${dateFormat.format(job.endDate)}',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ),
                        Chip(label: Text(job.status)),
                      ],
                    ),
                    LinearProgressIndicator(
                      value: job.totalTickers == 0
                          ? null
                          : job.progressPct / 100,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '${job.progressPct.toStringAsFixed(1)}% • ${job.processedTickers}/${job.totalTickers} سهم',
                    ),
                    if (job.errorMessage != null) Text(job.errorMessage!),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: [
                        if (job.canPause)
                          OutlinedButton(
                            onPressed: () => _control(job, 'pause'),
                            child: const Text('إيقاف مؤقت'),
                          ),
                        if (job.canResume)
                          FilledButton.tonal(
                            onPressed: () => _control(job, 'resume'),
                            child: const Text('استكمال'),
                          ),
                        if (job.canCancel)
                          TextButton(
                            onPressed: () => _control(job, 'cancel'),
                            child: const Text('إلغاء'),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

```

---

### File: `lib\features\admin\admin_models.dart`

```dart
import 'dart:collection';

import '../community/community_models.dart';

class AdminOverview {
  const AdminOverview({
    required this.usersTotal,
    required this.usersActive,
    required this.usersSuspended,
    required this.discussionsPending,
    required this.discussionsPublished,
    required this.discussionsHidden,
    required this.openReports,
    required this.openAppeals,
    required this.verifiedPredictions,
    required this.walletPointsTotal,
    required this.notificationsToday,
  });

  final int usersTotal;
  final int usersActive;
  final int usersSuspended;
  final int discussionsPending;
  final int discussionsPublished;
  final int discussionsHidden;
  final int openReports;
  final int openAppeals;
  final int verifiedPredictions;
  final int walletPointsTotal;
  final int notificationsToday;

  factory AdminOverview.fromJson(Map<String, dynamic> json) {
    int value(String key) => json[key] as int? ?? 0;
    return AdminOverview(
      usersTotal: value('users_total'),
      usersActive: value('users_active'),
      usersSuspended: value('users_suspended'),
      discussionsPending: value('discussions_pending'),
      discussionsPublished: value('discussions_published'),
      discussionsHidden: value('discussions_hidden'),
      openReports: value('open_reports'),
      openAppeals: value('open_appeals'),
      verifiedPredictions: value('verified_predictions'),
      walletPointsTotal: value('wallet_points_total'),
      notificationsToday: value('notifications_today'),
    );
  }
}

class OperationalSetting {
  const OperationalSetting({
    required this.key,
    required this.category,
    required this.label,
    required this.description,
    required this.kind,
    required this.value,
    required this.minValue,
    required this.maxValue,
  });

  final String key;
  final String category;
  final String label;
  final String description;
  final String kind;
  final Object value;
  final num? minValue;
  final num? maxValue;

  factory OperationalSetting.fromJson(Map<String, dynamic> json) {
    return OperationalSetting(
      key: json['key'] as String,
      category: json['category'] as String,
      label: json['label'] as String,
      description: json['description'] as String,
      kind: json['kind'] as String,
      value: json['value'] as Object,
      minValue: json['min_value'] as num?,
      maxValue: json['max_value'] as num?,
    );
  }
}

class ServiceHealth {
  const ServiceHealth({
    required this.component,
    required this.provider,
    required this.status,
    required this.latencyMs,
    required this.observedAt,
  });

  final String component;
  final String provider;
  final String status;
  final int? latencyMs;
  final DateTime observedAt;

  String get componentLabel => switch (component) {
    'market_data' => 'بيانات السوق',
    'ai' => 'الذكاء الاصطناعي',
    _ => 'خدمة تشغيلية',
  };

  String get providerLabel => switch (provider) {
    'tradingview' => 'TradingView',
    'yfinance' => 'Yahoo Finance الاحتياطي',
    'tradingview+yfinance' => 'TradingView ثم Yahoo Finance',
    'configured_ai' => 'مزود الذكاء الاصطناعي',
    _ => provider,
  };

  String get statusLabel => switch (status) {
    'healthy' => 'سليم',
    'degraded' => 'يعمل بصورة جزئية',
    'failed' => 'متعطل',
    _ => 'غير معروف',
  };

  factory ServiceHealth.fromJson(Map<String, dynamic> json) {
    return ServiceHealth(
      component: json['component'] as String,
      provider: json['provider'] as String,
      status: json['status'] as String,
      latencyMs: json['latency_ms'] as int?,
      observedAt: DateTime.parse(json['observed_at'] as String),
    );
  }
}

class AdminUserItem {
  const AdminUserItem({
    required this.id,
    required this.email,
    required this.displayName,
    required this.status,
    required this.planCode,
    required this.balancePoints,
    required this.discussionsCount,
  });

  final String id;
  final String email;
  final String displayName;
  final String status;
  final String planCode;
  final int balancePoints;
  final int discussionsCount;

  factory AdminUserItem.fromJson(Map<String, dynamic> json) {
    return AdminUserItem(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String,
      status: json['status'] as String,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int? ?? 0,
      discussionsCount: json['discussions_count'] as int? ?? 0,
    );
  }
}

class AdminAuditItem {
  const AdminAuditItem({
    required this.action,
    required this.reasonCode,
    required this.details,
    required this.createdAt,
  });

  final String action;
  final String? reasonCode;
  final Map<String, dynamic> details;
  final DateTime createdAt;

  factory AdminAuditItem.fromJson(Map<String, dynamic> json) {
    final rawReason = json['reason_code'] as String?;
    return AdminAuditItem(
      action: _auditActionLabel(json['action'] as String? ?? ''),
      reasonCode: rawReason == null ? null : _auditReasonLabel(rawReason),
      details: _ReadableAuditDetails(_map(json['details'])),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class AdminDiscussionItem {
  const AdminDiscussionItem({
    required this.discussion,
    required this.openReportCount,
  });

  final CommunityDiscussion discussion;
  final int openReportCount;

  factory AdminDiscussionItem.fromJson(Map<String, dynamic> json) {
    return AdminDiscussionItem(
      discussion: CommunityDiscussion.fromJson(_map(json['discussion'])),
      openReportCount: json['open_report_count'] as int? ?? 0,
    );
  }
}

class _ReadableAuditDetails extends MapBase<String, dynamic> {
  _ReadableAuditDetails(this._source);

  final Map<String, dynamic> _source;

  @override
  dynamic operator [](Object? key) => _source[key];

  @override
  void operator []=(String key, dynamic value) => _source[key] = value;

  @override
  void clear() => _source.clear();

  @override
  Iterable<String> get keys => _source.keys;

  @override
  dynamic remove(Object? key) => _source.remove(key);

  @override
  String toString() {
    final lines = <String>[];
    for (final entry in _source.entries) {
      if (_hiddenAuditKeys.contains(entry.key)) continue;
      final label = _auditDetailLabel(entry.key);
      final value = _auditValue(entry.value);
      if (value.isNotEmpty) lines.add('$label: $value');
    }
    return lines.isEmpty ? 'لا توجد تفاصيل إضافية.' : lines.join('\n');
  }
}

const _hiddenAuditKeys = <String>{
  'request_id',
  'idempotency_key',
  'data_fingerprint',
  'before_payload',
  'after_payload',
  'token_hash',
};

String _auditActionLabel(String value) => switch (value) {
  'discussion_approved' || 'approve_discussion' => 'قبول مناقشة ونشرها',
  'discussion_rejected' || 'reject_discussion' => 'رفض مناقشة',
  'discussion_hidden' || 'hide_discussion' => 'إخفاء مناقشة',
  'discussion_restored' || 'restore_discussion' => 'استعادة مناقشة',
  'user_blocked' || 'block_user' => 'حظر مستخدم',
  'user_unblocked' || 'unblock_user' => 'إلغاء حظر مستخدم',
  'setting_updated' || 'update_operational_setting' => 'تعديل إعداد تشغيلي',
  'notification_broadcast' || 'broadcast_notification' => 'إرسال إشعار جماعي',
  'performance_outcome_corrected' ||
  'correct_performance_outcome' => 'تصحيح نتيجة أداء موثقة',
  'admin_wallet_credit' ||
  'wallet_credit' ||
  'credit_user_wallet' => 'إضافة عملات لمستخدم',
  'report_refund' || 'refund_discussion' => 'إرجاع رصيد لمستخدم',
  _ => 'إجراء إداري',
};

String _auditReasonLabel(String value) => switch (value) {
  'manual_rejection' => 'رفض يدوي بعد المراجعة',
  'policy_violation' => 'مخالفة سياسة النشر',
  'provider_unavailable' => 'تعذر مزود الخدمة',
  'admin_credit' => 'إضافة رصيد بواسطة الإدارة',
  'performance_correction' => 'تصحيح بيانات جلسة السوق',
  'user_request' => 'بناءً على طلب المستخدم',
  _ => 'سبب إداري مسجل',
};

String _auditDetailLabel(String key) => switch (key) {
  'setting_key' || 'key' => 'الإعداد',
  'old_value' || 'before' => 'القيمة السابقة',
  'new_value' || 'after' => 'القيمة الجديدة',
  'amount_coins' => 'العملات المضافة',
  'amount_points' => 'النقاط المضافة',
  'balance_before_points' => 'الرصيد قبل العملية',
  'balance_after_points' => 'الرصيد بعد العملية',
  'title' => 'العنوان',
  'body' => 'النص',
  'notifications_created' || 'recipients' => 'عدد المستلمين',
  'ticker' => 'السهم',
  'report_id' => 'التقرير',
  'discussion_id' => 'المناقشة',
  'target_user_id' || 'user_id' => 'المستخدم',
  'provider' => 'المزود',
  'status' => 'الحالة',
  'reason' => 'السبب',
  'score_bp' => 'الدرجة',
  'strength' => 'التقييم',
  _ => 'تفصيل',
};

String _auditValue(Object? value) {
  if (value == null) return '';
  if (value is bool) return value ? 'نعم' : 'لا';
  if (value is num) return value.toString();
  if (value is List) {
    return value.map(_auditValue).where((item) => item.isNotEmpty).join('، ');
  }
  if (value is Map) {
    final readable = _ReadableAuditDetails(Map<String, dynamic>.from(value));
    return readable.toString().replaceAll('\n', '، ');
  }
  final text = value.toString();
  return switch (text) {
    'active' => 'نشط',
    'suspended' => 'محظور',
    'free' => 'مجانية',
    'basic' => 'أساسية',
    'advanced' => 'متقدمة',
    'pro' => 'احترافية',
    'healthy' => 'سليم',
    'degraded' => 'جزئي',
    'failed' => 'فاشل',
    _ =>
      text.length > 36 && text.contains('-')
          ? '${text.substring(0, 8)}…'
          : text,
  };
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return <String, dynamic>{};
}

```

---

### File: `lib\features\admin\admin_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_models.dart';
import 'admin_repository.dart';

final adminOverviewProvider = FutureProvider.autoDispose<AdminOverview>((ref) {
  return ref.watch(adminRepositoryProvider).overview();
});

final adminSettingsProvider =
    FutureProvider.autoDispose<List<OperationalSetting>>((ref) {
      return ref.watch(adminRepositoryProvider).settings();
    });

final adminProvidersProvider = FutureProvider.autoDispose<List<ServiceHealth>>((
  ref,
) {
  return ref.watch(adminRepositoryProvider).providers();
});

final adminUsersProvider = FutureProvider.autoDispose<List<AdminUserItem>>((
  ref,
) {
  return ref.watch(adminRepositoryProvider).users();
});

final adminAuditProvider = FutureProvider.autoDispose<List<AdminAuditItem>>((
  ref,
) {
  return ref.watch(adminRepositoryProvider).audit();
});

final adminDiscussionsProvider =
    FutureProvider.autoDispose<List<AdminDiscussionItem>>((ref) {
      return ref.watch(adminRepositoryProvider).discussions();
    });

```

---

### File: `lib\features\admin\admin_repository.dart`

```dart
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'admin_models.dart';
import 'historical_replay_models.dart';

class AdminRepository {
  const AdminRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<AdminOverview> overview() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/overview',
      );
      return AdminOverview.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<OperationalSetting>> settings() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/settings',
      );
      return _list(_required(response.data)['items'])
          .map((item) => OperationalSetting.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> updateSetting(String key, Object value) async {
    try {
      await _apiClient.dio.put<Map<String, dynamic>>(
        '/admin/operations/settings/$key',
        data: <String, dynamic>{'value': value},
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<ServiceHealth>> providers({bool probe = false}) async {
    try {
      final response = probe
          ? await _apiClient.dio.post<Map<String, dynamic>>(
              '/admin/operations/providers/probe',
            )
          : await _apiClient.dio.get<Map<String, dynamic>>(
              '/admin/operations/providers',
            );
      return _list(_required(response.data)['items'])
          .map((item) => ServiceHealth.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AdminUserItem>> users() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/users',
        queryParameters: const <String, dynamic>{'limit': 100},
      );
      return _list(_required(response.data)['items'])
          .map((item) => AdminUserItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> creditUserCoins({
    required String userId,
    required int amountCoins,
    required String reason,
    required String requestId,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/users/$userId/wallet-credit',
        data: <String, dynamic>{
          'amount_coins': amountCoins,
          'reason': reason.trim(),
          'request_id': requestId,
        },
      );
      return _required(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<HistoricalReplayJob>> historicalReplayJobs() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs',
        queryParameters: const <String, dynamic>{'limit': 50},
      );
      return _list(_required(response.data)['items'])
          .map((item) => HistoricalReplayJob.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> createHistoricalReplay({
    required DateTime startDate,
    required DateTime endDate,
    required int horizonSessions,
  }) async {
    try {
      final requestKey = 'replay_${DateTime.now().microsecondsSinceEpoch}';
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs',
        data: <String, dynamic>{
          'request_key': requestKey,
          'start_date': _dateOnly(startDate),
          'end_date': _dateOnly(endDate),
          'horizon_sessions': horizonSessions,
          'min_train_size': 200,
          'neutral_band_pct': 1.0,
        },
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> createLabsReplayJob({
    required DateTime startDate,
    required DateTime endDate,
    int? rank,
    String exitMode = 'target_2',
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs/labs-backtest',
        data: <String, dynamic>{
          'start_date': _dateOnly(startDate),
          'end_date': _dateOnly(endDate),
          'rank': rank,
          'exit_mode': exitMode,
        },
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<HistoricalReplayJob>> createHistoricalReplayBatch({
    required List<HistoricalReplayWindow> windows,
    required int horizonSessions,
  }) async {
    if (windows.length < 2) {
      throw const FormatException('أضف فترتين على الأقل لتشغيل دفعة.');
    }
    try {
      final requestKeyPrefix =
          'replay_batch_${DateTime.now().microsecondsSinceEpoch}';
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/batches',
        data: <String, dynamic>{
          'request_key_prefix': requestKeyPrefix,
          'windows': windows.map((window) => window.toJson()).toList(),
          'horizon_sessions': horizonSessions,
          'min_train_size': 200,
          'neutral_band_pct': 1.0,
        },
      );
      return _list(_required(response.data)['items'])
          .map((item) => HistoricalReplayJob.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> historicalReplayJob(String jobId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs/$jobId',
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> pauseHistoricalReplay(String jobId) {
    return _controlHistoricalReplay(jobId, 'pause');
  }

  Future<HistoricalReplayJob> resumeHistoricalReplay(String jobId) {
    return _controlHistoricalReplay(jobId, 'resume');
  }

  Future<HistoricalReplayJob> cancelHistoricalReplay(String jobId) {
    return _controlHistoricalReplay(jobId, 'cancel');
  }

  Future<void> deleteHistoricalReplay(String jobId) async {
    try {
      await _apiClient.dio.delete<void>(
        '/admin/operations/historical-replays/jobs/$jobId',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> _controlHistoricalReplay(
    String jobId,
    String action,
  ) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs/$jobId/$action',
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<({Uint8List bytes, String filename})> downloadHistoricalReplay(
    String jobId,
  ) async {
    try {
      final response = await _apiClient.dio.get<List<int>>(
        '/admin/operations/historical-replays/jobs/$jobId/export.csv',
        options: Options(responseType: ResponseType.bytes),
      );
      final data = response.data;
      if (data == null || data.isEmpty) {
        throw const FormatException('ملف الاختبار فارغ.');
      }
      final disposition = response.headers.value('content-disposition') ?? '';
      final filename =
          RegExp('filename="?([^";]+)').firstMatch(disposition)?.group(1) ??
          'sahmi-engine-replay-$jobId.csv';
      return (bytes: Uint8List.fromList(data), filename: filename);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AdminAuditItem>> audit() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/audit',
        queryParameters: const <String, dynamic>{'limit': 100},
      );
      return _list(_required(response.data)['items'])
          .map((item) => AdminAuditItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AdminDiscussionItem>> discussions({
    String status = 'pending_review',
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/community/discussions',
        queryParameters: <String, dynamic>{
          'discussion_status': status,
          'limit': 100,
        },
      );
      return _list(_required(response.data)['items'])
          .map((item) => AdminDiscussionItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> moderateDiscussion({
    required String discussionId,
    required String action,
    String? reasonCode,
    Map<String, dynamic>? prediction,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/community/discussions/$discussionId/action',
        data: <String, dynamic>{
          'action': action,
          if (reasonCode != null) 'reason_code': reasonCode,
          'details': 'Flutter administration dashboard',
          if (prediction != null) 'prediction': prediction,
        },
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> setUserBlocked(AdminUserItem user, bool blocked) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/community/users/${user.id}/${blocked ? 'block' : 'unblock'}',
        data: const <String, dynamic>{
          'reason_code': 'manual_admin_action',
          'details': 'Flutter administration dashboard',
        },
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> broadcast({
    required String title,
    required String body,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/notifications/broadcast',
        data: <String, dynamic>{
          'title': title,
          'body': body,
          'category': 'announcement',
          'audience': 'active',
        },
      );
      return _required(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  String _dateOnly(DateTime value) {
    return '${value.year.toString().padLeft(4, '0')}-'
        '${value.month.toString().padLeft(2, '0')}-'
        '${value.day.toString().padLeft(2, '0')}';
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) throw const FormatException('Admin response is empty.');
    return value;
  }

  List<dynamic> _list(Object? value) => value is List ? value : const [];
  Map<String, dynamic> _map(Object? value) => value is Map<String, dynamic>
      ? value
      : value is Map
      ? Map<String, dynamic>.from(value)
      : <String, dynamic>{};
}

final adminRepositoryProvider = Provider<AdminRepository>((ref) {
  return AdminRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\admin\admin_wallet_credit_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'admin_models.dart';
import 'admin_providers.dart';
import 'admin_repository.dart';

class AdminWalletCreditScreen extends ConsumerStatefulWidget {
  const AdminWalletCreditScreen({super.key});

  @override
  ConsumerState<AdminWalletCreditScreen> createState() =>
      _AdminWalletCreditScreenState();
}

class _AdminWalletCreditScreenState
    extends ConsumerState<AdminWalletCreditScreen> {
  final _search = TextEditingController();
  String? _creditingUserId;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final users = ref.watch(adminUsersProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('إضافة عملات للمستخدمين')),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: TextField(
                controller: _search,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search_rounded),
                  labelText: 'ابحث بالاسم أو البريد الإلكتروني',
                ),
              ),
            ),
            Expanded(
              child: users.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, __) =>
                    _Failure(retry: () => ref.invalidate(adminUsersProvider)),
                data: (items) {
                  final query = _search.text.trim().toLowerCase();
                  final filtered = items
                      .where(
                        (item) =>
                            query.isEmpty ||
                            item.displayName.toLowerCase().contains(query) ||
                            item.email.toLowerCase().contains(query),
                      )
                      .toList(growable: false);
                  if (filtered.isEmpty) {
                    return const Center(child: Text('لا يوجد مستخدم مطابق.'));
                  }
                  return RefreshIndicator(
                    onRefresh: () async {
                      final refreshed = ref.refresh(adminUsersProvider.future);
                      await refreshed;
                    },
                    child: ListView.separated(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.all(16),
                      itemCount: filtered.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (context, index) {
                        final user = filtered[index];
                        final busy = _creditingUserId == user.id;
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                Text(
                                  user.displayName,
                                  style: Theme.of(context).textTheme.titleMedium
                                      ?.copyWith(fontWeight: FontWeight.w900),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  user.email,
                                  textDirection: TextDirection.ltr,
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  'الخطة: ${user.planCode} • الرصيد: '
                                  '${_coins(user.balancePoints)} عملة',
                                ),
                                const SizedBox(height: 12),
                                FilledButton.icon(
                                  onPressed: busy ? null : () => _credit(user),
                                  icon: busy
                                      ? const SizedBox.square(
                                          dimension: 18,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                          ),
                                        )
                                      : const Icon(Icons.add_card_rounded),
                                  label: const Text('إضافة عملات'),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _credit(AdminUserItem user) async {
    final form = await showDialog<_CreditFormData>(
      context: context,
      builder: (context) => _CreditDialog(user: user),
    );
    if (form == null || !mounted) return;

    setState(() => _creditingUserId = user.id);
    try {
      final result = await ref
          .read(adminRepositoryProvider)
          .creditUserCoins(
            userId: user.id,
            amountCoins: form.amountCoins,
            reason: form.reason,
            requestId:
                'mobile-${DateTime.now().microsecondsSinceEpoch}-${user.id.substring(0, 8)}',
          );
      ref.invalidate(adminUsersProvider);
      ref.invalidate(adminOverviewProvider);
      ref.invalidate(adminAuditProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'تمت إضافة ${form.amountCoins} عملة إلى ${user.displayName}. '
              'الرصيد الجديد: ${result['balance_coins'] ?? '-'} عملة.',
            ),
          ),
        );
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } finally {
      if (mounted) setState(() => _creditingUserId = null);
    }
  }
}

class _CreditDialog extends StatefulWidget {
  const _CreditDialog({required this.user});

  final AdminUserItem user;

  @override
  State<_CreditDialog> createState() => _CreditDialogState();
}

class _CreditDialogState extends State<_CreditDialog> {
  final _amount = TextEditingController();
  final _reason = TextEditingController();
  String? _error;

  @override
  void dispose() {
    _amount.dispose();
    _reason.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('إضافة عملات إلى ${widget.user.displayName}'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('الرصيد الحالي: ${_coins(widget.user.balancePoints)} عملة'),
            const SizedBox(height: 14),
            TextField(
              controller: _amount,
              keyboardType: TextInputType.number,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'عدد العملات',
                prefixIcon: Icon(Icons.monetization_on_outlined),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _reason,
              minLines: 2,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'سبب الإضافة',
                hintText: 'مثال: تعويض عن مشكلة في التقرير',
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 10),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        FilledButton(onPressed: _submit, child: const Text('تأكيد الإضافة')),
      ],
    );
  }

  void _submit() {
    final amount = int.tryParse(_amount.text.trim());
    final reason = _reason.text.trim();
    if (amount == null || amount < 1 || amount > 100000) {
      setState(() => _error = 'أدخل عدد عملات صحيحًا من 1 إلى 100000.');
      return;
    }
    if (reason.length < 4) {
      setState(() => _error = 'اكتب سببًا واضحًا لا يقل عن 4 أحرف.');
      return;
    }
    Navigator.pop(
      context,
      _CreditFormData(amountCoins: amount, reason: reason),
    );
  }
}

class _CreditFormData {
  const _CreditFormData({required this.amountCoins, required this.reason});

  final int amountCoins;
  final String reason;
}

class _Failure extends StatelessWidget {
  const _Failure({required this.retry});

  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('تعذر تحميل المستخدمين.'),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: retry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

String _coins(int points) => (points / 100).toStringAsFixed(2);

```

---

### File: `lib\features\admin\historical_replay_control_screen.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import '../labs/labs_screen.dart';
import 'admin_repository.dart';
import 'historical_replay_models.dart';

class HistoricalReplayControlScreen extends ConsumerStatefulWidget {
  const HistoricalReplayControlScreen({super.key});

  @override
  ConsumerState<HistoricalReplayControlScreen> createState() =>
      _HistoricalReplayControlScreenState();
}

class _HistoricalReplayControlScreenState
    extends ConsumerState<HistoricalReplayControlScreen> {
  static const _downloads = MethodChannel('sahmi_kasban/downloads');
  static const _horizons = <int>[1, 3, 5, 10, 20];

  late DateTime _startDate;
  late DateTime _endDate;
  int _horizonSessions = 5;
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<HistoricalReplayJob> _jobs = const [];
  List<HistoricalReplayWindow> _batchWindows = const [];
  final Set<String> _busyJobs = <String>{};
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _previousMonth(notify: false);
    unawaited(_load());
    _pollTimer = Timer.periodic(
      const Duration(seconds: 8),
      (_) => unawaited(_load(silent: true)),
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load({bool silent = false}) async {
    if (!silent && mounted) setState(() => _loading = true);
    try {
      final jobs = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _loading = false;
        _error = null;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = _errorText(error);
      });
    }
  }

  void _previousMonth({bool notify = true}) {
    final firstCurrent = DateTime(DateTime.now().year, DateTime.now().month);
    final end = firstCurrent.subtract(const Duration(days: 1));
    final start = DateTime(end.year, end.month);
    if (notify) {
      setState(() {
        _startDate = start;
        _endDate = end;
      });
    } else {
      _startDate = start;
      _endDate = end;
    }
  }

  void _currentMonth() {
    final now = DateTime.now();
    setState(() {
      _startDate = DateTime(now.year, now.month);
      _endDate = DateTime(now.year, now.month, now.day);
    });
  }

  Future<void> _pickDate({required bool start}) async {
    final today = DateTime.now();
    final latestEnd = _startDate.add(const Duration(days: 30));
    final picked = await showDatePicker(
      context: context,
      initialDate: start
          ? _startDate
          : (_endDate.isAfter(latestEnd) ? latestEnd : _endDate),
      firstDate: start
          ? today.subtract(const Duration(days: 365 * 5))
          : _startDate,
      lastDate: start ? today : (latestEnd.isBefore(today) ? latestEnd : today),
      helpText: start ? 'اختر تاريخ البداية' : 'اختر تاريخ النهاية',
    );
    if (picked == null) return;
    setState(() {
      if (start) {
        _startDate = picked;
        if (_endDate.isBefore(picked)) _endDate = picked;
        if (_endDate.difference(picked).inDays > 30) {
          _endDate = picked.add(const Duration(days: 30));
        }
      } else {
        _endDate = picked;
      }
    });
  }

  bool _validateWindow() {
    final days = _endDate.difference(_startDate).inDays + 1;
    if (days < 1 || days > 31) {
      _message('الحد الأقصى لكل فترة هو 31 يومًا.');
      return false;
    }
    return true;
  }

  Future<void> _startSingle() async {
    if (!_validateWindow()) return;
    await _submit(() async {
      await ref
          .read(adminRepositoryProvider)
          .createHistoricalReplay(
            startDate: _startDate,
            endDate: _endDate,
            horizonSessions: _horizonSessions,
          );
      _message('بدأ الاختبار على Worker منفصل عن مستخدمي التطبيق.');
    });
  }

  void _addWindow() {
    if (!_validateWindow()) return;
    final duplicate = _batchWindows.any(
      (window) =>
          _sameDay(window.startDate, _startDate) &&
          _sameDay(window.endDate, _endDate),
    );
    if (duplicate) {
      _message('الفترة موجودة بالفعل داخل الدفعة.');
      return;
    }
    setState(() {
      _batchWindows = [
        ..._batchWindows,
        HistoricalReplayWindow(startDate: _startDate, endDate: _endDate),
      ];
    });
  }

  Future<void> _startBatch() async {
    if (_batchWindows.length < 2) {
      _message('أضف فترتين على الأقل لتشغيل دفعة.');
      return;
    }
    await _submit(() async {
      final jobs = await ref
          .read(adminRepositoryProvider)
          .createHistoricalReplayBatch(
            windows: _batchWindows,
            horizonSessions: _horizonSessions,
          );
      if (mounted) setState(() => _batchWindows = const []);
      _message(
        'تمت إضافة ${jobs.length} فترات. ستعمل بالترتيب وتشارك Cache البيانات.',
      );
    });
  }

  Future<void> _submit(Future<void> Function() operation) async {
    setState(() => _submitting = true);
    try {
      await operation();
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _control(HistoricalReplayJob job, String action) async {
    if (_busyJobs.contains(job.id)) return;
    if (action == 'cancel') {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('إلغاء الاختبار؟'),
          content: const Text(
            'سيتم الاحتفاظ بالنتائج المكتملة وإيقاف الأسهم المتبقية.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('رجوع'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('إلغاء الاختبار'),
            ),
          ],
        ),
      );
      if (confirmed != true) return;
    }

    setState(() => _busyJobs.add(job.id));
    try {
      final repository = ref.read(adminRepositoryProvider);
      switch (action) {
        case 'pause':
          await repository.pauseHistoricalReplay(job.id);
        case 'resume':
          await repository.resumeHistoricalReplay(job.id);
        case 'cancel':
          await repository.cancelHistoricalReplay(job.id);
      }
      if (mounted) {
        _message(switch (action) {
          'pause' => 'تم طلب الإيقاف بعد الدفعة الحالية.',
          'resume' => 'تم استكمال الاختبار.',
          _ => 'تم إلغاء الاختبار.',
        });
      }
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    } finally {
      if (mounted) setState(() => _busyJobs.remove(job.id));
    }
  }

  Future<void> _delete(HistoricalReplayJob job) async {
    if (_busyJobs.contains(job.id)) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف نهائي؟'),
        content: const Text(
          'سيتم حذف هذا الاختبار وجميع نتائجه نهائيًا. لا يمكن التراجع عن هذا الإجراء.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('رجوع'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('حذف نهائي'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    setState(() => _busyJobs.add(job.id));
    try {
      await ref.read(adminRepositoryProvider).deleteHistoricalReplay(job.id);
      if (mounted) _message('تم حذف الاختبار نهائيًا.');
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    } finally {
      if (mounted) setState(() => _busyJobs.remove(job.id));
    }
  }

  Future<void> _download(HistoricalReplayJob job) async {
    try {
      final file = await ref
          .read(adminRepositoryProvider)
          .downloadHistoricalReplay(job.id);
      final location = await _downloads.invokeMethod<String>('saveCsv', {
        'filename': file.filename,
        'bytes': file.bytes,
      });
      if (mounted) {
        _message(
          location == null ? 'تم تنزيل النتائج.' : 'تم التنزيل في: $location',
        );
      }
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    }
  }

  Future<void> _details(HistoricalReplayJob job) async {
    try {
      final detailed = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJob(job.id);
      if (!mounted) return;
      await showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        builder: (context) => DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.75,
          builder: (context, controller) => ListView(
            controller: controller,
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                'تفاصيل الأسهم',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              if (detailed.tickers.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('لم تبدأ معالجة الأسهم بعد.')),
                ),
              for (final ticker in detailed.tickers)
                ListTile(
                  dense: true,
                  leading: Icon(_tickerIcon(ticker.status)),
                  title: Text(ticker.ticker),
                  subtitle: Text(
                    '${_statusLabel(ticker.status)} • '
                    '${ticker.rowsWritten} تقرير • '
                    '${ticker.evaluatedRows} مُقيّم • '
                    '${ticker.pendingRows} منتظر',
                  ),
                  trailing: ticker.failedRows > 0
                      ? Text('${ticker.failedRows} فشل')
                      : null,
                ),
            ],
          ),
        ),
      );
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    }
  }

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(text)));
  }

  String _errorText(Object error) {
    return error is ApiException ? error.message : error.toString();
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('d MMMM y', 'ar');
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('اختبار المحركات'),
          actions: [
            IconButton(
              onPressed: _load,
              tooltip: 'تحديث',
              icon: const Icon(Icons.refresh),
            ),
          ],
          bottom: const TabBar(
            tabs: [
              Tab(text: 'المحركات التاريخي'),
              Tab(text: 'المختببرات'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildReplayTab(dateFormat),
            const LabsScreen(embedded: true),
          ],
        ),
      ),
    );
  }

  Widget _buildReplayTab(DateFormat dateFormat) {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _ReplaySetupCard(
            dateFormat: dateFormat,
            startDate: _startDate,
            endDate: _endDate,
            horizonSessions: _horizonSessions,
            horizons: _horizons,
            submitting: _submitting,
            windows: _batchWindows,
            onPreviousMonth: _previousMonth,
            onCurrentMonth: _currentMonth,
            onPickStart: () => _pickDate(start: true),
            onPickEnd: () => _pickDate(start: false),
            onHorizonChanged: (value) =>
                setState(() => _horizonSessions = value),
            onStartSingle: _startSingle,
            onAddWindow: _addWindow,
            onRemoveWindow: (index) => setState(() {
              _batchWindows = [
                for (var i = 0; i < _batchWindows.length; i++)
                  if (i != index) _batchWindows[i],
              ];
            }),
            onStartBatch: _startBatch,
          ),
          const SizedBox(height: 16),
          Text('اختبارات حسابي', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          if (_loading) const Center(child: CircularProgressIndicator()),
          if (_error != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: const Text('تعذر تحميل الاختبارات'),
                subtitle: Text(_error!),
              ),
            ),
          if (!_loading && _jobs.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('لم تبدأ أي اختبارات بعد.')),
              ),
            ),
          for (final job in _jobs)
            _ReplayJobCard(
              job: job,
              dateFormat: dateFormat,
              busy: _busyJobs.contains(job.id),
              onDetails: () => _details(job),
              onDownload: job.downloadReady ? () => _download(job) : null,
              onPause: job.canPause ? () => _control(job, 'pause') : null,
              onResume: job.canResume ? () => _control(job, 'resume') : null,
              onCancel: job.canCancel ? () => _control(job, 'cancel') : null,
              onDelete: () => _delete(job),
            ),
        ],
      ),
    );
  }
}

class _ReplaySetupCard extends StatelessWidget {
  const _ReplaySetupCard({
    required this.dateFormat,
    required this.startDate,
    required this.endDate,
    required this.horizonSessions,
    required this.horizons,
    required this.submitting,
    required this.windows,
    required this.onPreviousMonth,
    required this.onCurrentMonth,
    required this.onPickStart,
    required this.onPickEnd,
    required this.onHorizonChanged,
    required this.onStartSingle,
    required this.onAddWindow,
    required this.onRemoveWindow,
    required this.onStartBatch,
  });

  final DateFormat dateFormat;
  final DateTime startDate;
  final DateTime endDate;
  final int horizonSessions;
  final List<int> horizons;
  final bool submitting;
  final List<HistoricalReplayWindow> windows;
  final VoidCallback onPreviousMonth;
  final VoidCallback onCurrentMonth;
  final VoidCallback onPickStart;
  final VoidCallback onPickEnd;
  final ValueChanged<int> onHorizonChanged;
  final VoidCallback onStartSingle;
  final VoidCallback onAddWindow;
  final ValueChanged<int> onRemoveWindow;
  final VoidCallback onStartBatch;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'تشغيل اختبار جديد',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            const Text(
              'الاختبارات تعمل على Worker منفصل، لذلك لا تبطئ مستخدمي التطبيق. '
              'يمكن تشغيل فترة واحدة أو إضافة عدة فترات إلى دفعة متسلسلة.',
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              children: [
                OutlinedButton(
                  onPressed: onPreviousMonth,
                  child: const Text('الشهر السابق'),
                ),
                OutlinedButton(
                  onPressed: onCurrentMonth,
                  child: const Text('الشهر الحالي'),
                ),
              ],
            ),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: onPickStart,
                    child: Text('من\n${dateFormat.format(startDate)}'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: onPickEnd,
                    child: Text('إلى\n${dateFormat.format(endDate)}'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<int>(
              initialValue: horizonSessions,
              decoration: const InputDecoration(
                labelText: 'التقييم بعد عدد جلسات',
                border: OutlineInputBorder(),
              ),
              items: [
                for (final value in horizons)
                  DropdownMenuItem(value: value, child: Text('$value جلسات')),
              ],
              onChanged: submitting
                  ? null
                  : (value) {
                      if (value != null) onHorizonChanged(value);
                    },
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton.icon(
                  onPressed: submitting ? null : onStartSingle,
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('تشغيل الفترة'),
                ),
                OutlinedButton.icon(
                  onPressed: submitting ? null : onAddWindow,
                  icon: const Icon(Icons.playlist_add),
                  label: const Text('إضافة للدفعة'),
                ),
              ],
            ),
            if (windows.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('دفعة الفترات (${windows.length})'),
              for (final indexed in windows.indexed)
                ListTile(
                  dense: true,
                  leading: CircleAvatar(child: Text('${indexed.$1 + 1}')),
                  title: Text(
                    '${dateFormat.format(indexed.$2.startDate)} — '
                    '${dateFormat.format(indexed.$2.endDate)}',
                  ),
                  trailing: IconButton(
                    onPressed: submitting
                        ? null
                        : () => onRemoveWindow(indexed.$1),
                    icon: const Icon(Icons.close),
                  ),
                ),
              FilledButton.tonalIcon(
                onPressed: submitting || windows.length < 2
                    ? null
                    : onStartBatch,
                icon: const Icon(Icons.queue_play_next),
                label: Text('تشغيل ${windows.length} فترات بالترتيب'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ReplayJobCard extends StatelessWidget {
  const _ReplayJobCard({
    required this.job,
    required this.dateFormat,
    required this.busy,
    required this.onDetails,
    this.onDownload,
    this.onPause,
    this.onResume,
    this.onCancel,
    this.onDelete,
  });

  final HistoricalReplayJob job;
  final DateFormat dateFormat;
  final bool busy;
  final VoidCallback onDetails;
  final VoidCallback? onDownload;
  final VoidCallback? onPause;
  final VoidCallback? onResume;
  final VoidCallback? onCancel;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    final progress = job.totalTickers == 0 ? null : job.progressPct / 100;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(_jobIcon(job.controlState)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${dateFormat.format(job.startDate)} — '
                    '${dateFormat.format(job.endDate)}',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(label: Text(_statusLabel(job.controlState))),
              ],
            ),
            LinearProgressIndicator(value: progress),
            const SizedBox(height: 6),
            Text(
              '${job.progressPct.toStringAsFixed(1)}% • '
              '${job.processedTickers}/${job.totalTickers} سهم',
            ),
            if (job.estimatedSecondsRemaining != null && job.isActive)
              Text(
                'المتبقي تقريبًا ${_durationLabel(job.estimatedSecondsRemaining!)}'
                '${job.throughputTickersPerMinute == null ? '' : ' • ${job.throughputTickersPerMinute!.toStringAsFixed(1)} سهم/دقيقة'}',
              ),
            Text(
              '${job.totalRows} تقرير • ${job.evaluatedRows} مُقيّم • '
              '${job.pendingRows} منتظر • ${job.failedTickers} متعطل',
            ),
            if (job.workerIsolated)
              const Text('Worker منفصل: لا يستهلك موارد واجهة المستخدمين.'),
            if (job.errorMessage != null) Text(job.errorMessage!),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: busy ? null : onDetails,
                  icon: const Icon(Icons.list_alt_outlined),
                  label: const Text('التفاصيل'),
                ),
                if (onPause != null)
                  OutlinedButton.icon(
                    onPressed: busy ? null : onPause,
                    icon: const Icon(Icons.pause),
                    label: const Text('إيقاف مؤقت'),
                  ),
                if (onResume != null)
                  FilledButton.tonalIcon(
                    onPressed: busy ? null : onResume,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('استكمال'),
                  ),
                if (onCancel != null)
                  TextButton.icon(
                    onPressed: busy ? null : onCancel,
                    icon: const Icon(Icons.cancel_outlined),
                    label: const Text('إلغاء'),
                  ),
                if (onDelete != null)
                  TextButton.icon(
                    onPressed: busy ? null : onDelete,
                    style: TextButton.styleFrom(
                      foregroundColor: Theme.of(context).colorScheme.error,
                    ),
                    icon: const Icon(Icons.delete_outline_rounded),
                    label: const Text('حذف نهائي'),
                  ),
                if (onDownload != null)
                  FilledButton.icon(
                    onPressed: busy ? null : onDownload,
                    icon: const Icon(Icons.download_outlined),
                    label: const Text('تنزيل CSV'),
                  ),
                if (busy)
                  const SizedBox.square(
                    dimension: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

String _statusLabel(String value) => switch (value) {
  'pending' => 'في الانتظار',
  'running' => 'جاري التشغيل',
  'paused' => 'متوقف مؤقتًا',
  'cancelled' => 'ملغي',
  'complete' => 'مكتمل',
  'partial' => 'مكتمل جزئيًا',
  'failed' => 'فشل',
  _ => value,
};

IconData _jobIcon(String value) => switch (value) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' || 'cancelled' => Icons.error_outline,
  'running' => Icons.sync,
  'paused' => Icons.pause_circle_outline,
  _ => Icons.schedule,
};

IconData _tickerIcon(String value) => switch (value) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' => Icons.error_outline,
  'running' => Icons.sync,
  _ => Icons.schedule,
};

bool _sameDay(DateTime first, DateTime second) {
  return first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;
}

String _durationLabel(int seconds) {
  final duration = Duration(seconds: seconds.clamp(0, 86400 * 30).toInt());
  if (duration.inHours >= 1) {
    final minutes = duration.inMinutes.remainder(60);
    return minutes == 0
        ? '${duration.inHours} ساعة'
        : '${duration.inHours} ساعة و$minutes دقيقة';
  }
  if (duration.inMinutes >= 1) return '${duration.inMinutes} دقيقة';
  return 'أقل من دقيقة';
}

```

---

### File: `lib\features\admin\historical_replay_models.dart`

```dart
class HistoricalReplayWindow {
  const HistoricalReplayWindow({
    required this.startDate,
    required this.endDate,
  });

  final DateTime startDate;
  final DateTime endDate;

  Map<String, dynamic> toJson() => <String, dynamic>{
    'start_date': _dateOnly(startDate),
    'end_date': _dateOnly(endDate),
  };

  static String _dateOnly(DateTime value) {
    return '${value.year.toString().padLeft(4, '0')}-'
        '${value.month.toString().padLeft(2, '0')}-'
        '${value.day.toString().padLeft(2, '0')}';
  }
}

class HistoricalReplayTicker {
  const HistoricalReplayTicker({
    required this.ticker,
    required this.status,
    required this.rowsWritten,
    required this.evaluatedRows,
    required this.pendingRows,
    required this.failedRows,
    this.provider,
    this.errorMessage,
  });

  factory HistoricalReplayTicker.fromJson(Map<String, dynamic> json) {
    return HistoricalReplayTicker(
      ticker: json['ticker'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      provider: json['provider'] as String?,
      rowsWritten: (json['rows_written'] as num?)?.toInt() ?? 0,
      evaluatedRows: (json['evaluated_rows'] as num?)?.toInt() ?? 0,
      pendingRows: (json['pending_rows'] as num?)?.toInt() ?? 0,
      failedRows: (json['failed_rows'] as num?)?.toInt() ?? 0,
      errorMessage: json['error_message'] as String?,
    );
  }

  final String ticker;
  final String status;
  final String? provider;
  final int rowsWritten;
  final int evaluatedRows;
  final int pendingRows;
  final int failedRows;
  final String? errorMessage;
}

class HistoricalReplayJob {
  const HistoricalReplayJob({
    required this.id,
    required this.engineVersion,
    required this.status,
    required this.startDate,
    required this.endDate,
    required this.horizonSessions,
    required this.parallelism,
    required this.totalTickers,
    required this.processedTickers,
    required this.successfulTickers,
    required this.failedTickers,
    required this.totalRows,
    required this.evaluatedRows,
    required this.pendingRows,
    required this.progressPct,
    required this.downloadReady,
    required this.createdAt,
    this.controlState = 'pending',
    this.workerIsolated = false,
    this.canPause = false,
    this.canResume = false,
    this.canCancel = false,
    this.throughputTickersPerMinute,
    this.estimatedSecondsRemaining,
    this.startedAt,
    this.heartbeatAt,
    this.completedAt,
    this.errorMessage,
    this.tickers = const <HistoricalReplayTicker>[],
  });

  factory HistoricalReplayJob.fromJson(Map<String, dynamic> json) {
    final rawTickers = json['tickers'];
    final status = json['status'] as String? ?? 'pending';
    return HistoricalReplayJob(
      id: json['id'] as String? ?? '',
      engineVersion: json['engine_version'] as String? ?? '',
      status: status,
      controlState: json['control_state'] as String? ?? status,
      workerIsolated: json['worker_isolated'] as bool? ?? false,
      canPause: json['can_pause'] as bool? ?? false,
      canResume: json['can_resume'] as bool? ?? false,
      canCancel: json['can_cancel'] as bool? ?? false,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      horizonSessions: (json['horizon_sessions'] as num?)?.toInt() ?? 5,
      parallelism: (json['parallelism'] as num?)?.toInt() ?? 5,
      totalTickers: (json['total_tickers'] as num?)?.toInt() ?? 0,
      processedTickers: (json['processed_tickers'] as num?)?.toInt() ?? 0,
      successfulTickers: (json['successful_tickers'] as num?)?.toInt() ?? 0,
      failedTickers: (json['failed_tickers'] as num?)?.toInt() ?? 0,
      totalRows: (json['total_rows'] as num?)?.toInt() ?? 0,
      evaluatedRows: (json['evaluated_rows'] as num?)?.toInt() ?? 0,
      pendingRows: (json['pending_rows'] as num?)?.toInt() ?? 0,
      progressPct: (json['progress_pct'] as num?)?.toDouble() ?? 0,
      throughputTickersPerMinute:
          (json['throughput_tickers_per_minute'] as num?)?.toDouble(),
      estimatedSecondsRemaining: (json['estimated_seconds_remaining'] as num?)
          ?.toInt(),
      downloadReady: json['download_ready'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      startedAt: _optionalDateTime(json['started_at']),
      heartbeatAt: _optionalDateTime(json['heartbeat_at']),
      completedAt: _optionalDateTime(json['completed_at']),
      errorMessage: json['error_message'] as String?,
      tickers: rawTickers is List
          ? rawTickers
                .whereType<Map<String, dynamic>>()
                .map(HistoricalReplayTicker.fromJson)
                .toList(growable: false)
          : const <HistoricalReplayTicker>[],
    );
  }

  final String id;
  final String engineVersion;
  final String status;
  final String controlState;
  final bool workerIsolated;
  final bool canPause;
  final bool canResume;
  final bool canCancel;
  final DateTime startDate;
  final DateTime endDate;
  final int horizonSessions;
  final int parallelism;
  final int totalTickers;
  final int processedTickers;
  final int successfulTickers;
  final int failedTickers;
  final int totalRows;
  final int evaluatedRows;
  final int pendingRows;
  final double progressPct;
  final double? throughputTickersPerMinute;
  final int? estimatedSecondsRemaining;
  final bool downloadReady;
  final DateTime createdAt;
  final DateTime? startedAt;
  final DateTime? heartbeatAt;
  final DateTime? completedAt;
  final String? errorMessage;
  final List<HistoricalReplayTicker> tickers;

  bool get isActive => status == 'pending' || status == 'running';
  bool get isPaused => controlState == 'paused';
  bool get isCancelled => controlState == 'cancelled';
}

DateTime? _optionalDateTime(Object? value) {
  if (value is! String || value.isEmpty) return null;
  return DateTime.tryParse(value);
}

```

---

### File: `lib\features\admin\historical_replay_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'historical_replay_models.dart';
import 'admin_repository.dart';

final historicalReplayJobsProvider =
    FutureProvider.autoDispose<List<HistoricalReplayJob>>((ref) {
      return ref.watch(adminRepositoryProvider).historicalReplayJobs();
    });

final historicalReplayJobProvider = FutureProvider.autoDispose
    .family<HistoricalReplayJob, String>((ref, jobId) {
      return ref.watch(adminRepositoryProvider).historicalReplayJob(jobId);
    });

```

---

### File: `lib\features\admin\historical_replay_screen.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import 'admin_repository.dart';
import 'historical_replay_models.dart';

class HistoricalReplayScreen extends ConsumerStatefulWidget {
  const HistoricalReplayScreen({super.key});

  @override
  ConsumerState<HistoricalReplayScreen> createState() =>
      _HistoricalReplayScreenState();
}

class _HistoricalReplayScreenState
    extends ConsumerState<HistoricalReplayScreen> {
  static const _downloads = MethodChannel('sahmi_kasban/downloads');
  static const _horizons = <int>[1, 3, 5, 10, 20];

  late DateTime _startDate;
  late DateTime _endDate;
  int _horizonSessions = 5;
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<HistoricalReplayJob> _jobs = const [];
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _selectPreviousMonth(notify: false);
    unawaited(_load());
    _pollTimer = Timer.periodic(
      const Duration(seconds: 8),
      (_) => unawaited(_load(silent: true)),
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load({bool silent = false}) async {
    if (!silent && mounted) setState(() => _loading = true);
    try {
      final jobs = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _error = null;
        _loading = false;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error is ApiException ? error.message : error.toString();
        _loading = false;
      });
    }
  }

  void _selectPreviousMonth({bool notify = true}) {
    final today = DateTime.now();
    final firstCurrentMonth = DateTime(today.year, today.month);
    final previousEnd = firstCurrentMonth.subtract(const Duration(days: 1));
    final previousStart = DateTime(previousEnd.year, previousEnd.month);
    if (notify) {
      setState(() {
        _startDate = previousStart;
        _endDate = previousEnd;
      });
    } else {
      _startDate = previousStart;
      _endDate = previousEnd;
    }
  }

  void _selectCurrentMonth() {
    final today = DateTime.now();
    setState(() {
      _startDate = DateTime(today.year, today.month);
      _endDate = DateTime(today.year, today.month, today.day);
    });
  }

  Future<void> _pickStart() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365 * 5)),
      lastDate: DateTime.now(),
      helpText: 'اختر تاريخ بداية الاختبار',
    );
    if (picked == null) return;
    setState(() {
      _startDate = picked;
      if (_endDate.isBefore(picked)) _endDate = picked;
      if (_endDate.difference(_startDate).inDays > 30) {
        _endDate = _startDate.add(const Duration(days: 30));
      }
    });
  }

  Future<void> _pickEnd() async {
    final latest = _startDate.add(const Duration(days: 30));
    final today = DateTime.now();
    final lastDate = latest.isBefore(today) ? latest : today;
    final picked = await showDatePicker(
      context: context,
      initialDate: _endDate.isAfter(lastDate) ? lastDate : _endDate,
      firstDate: _startDate,
      lastDate: lastDate,
      helpText: 'اختر تاريخ نهاية الاختبار',
    );
    if (picked == null) return;
    setState(() => _endDate = picked);
  }

  Future<void> _start() async {
    final days = _endDate.difference(_startDate).inDays + 1;
    if (days < 1 || days > 31) {
      _showMessage('الحد الأقصى لكل تشغيل هو 31 يومًا.');
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref
          .read(adminRepositoryProvider)
          .createHistoricalReplay(
            startDate: _startDate,
            endDate: _endDate,
            horizonSessions: _horizonSessions,
          );
      if (!mounted) return;
      _showMessage(
        'بدأ الاختبار على السيرفر. يمكنك الخروج من التطبيق والعودة لاحقًا.',
      );
      await _load(silent: true);
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _download(HistoricalReplayJob job) async {
    try {
      final file = await ref
          .read(adminRepositoryProvider)
          .downloadHistoricalReplay(job.id);
      final location = await _downloads.invokeMethod<String>('saveCsv', {
        'filename': file.filename,
        'bytes': file.bytes,
      });
      if (!mounted) return;
      _showMessage(
        location == null
            ? 'تم تنزيل ملف النتائج.'
            : 'تم تنزيل ملف النتائج في: $location',
      );
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    }
  }

  Future<void> _showDetails(HistoricalReplayJob job) async {
    try {
      final detailed = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJob(job.id);
      if (!mounted) return;
      await showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        builder: (context) => DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.75,
          builder: (context, controller) => ListView(
            controller: controller,
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                'تفاصيل الأسهم',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              for (final ticker in detailed.tickers)
                ListTile(
                  dense: true,
                  leading: Icon(_tickerIcon(ticker.status)),
                  title: Text(ticker.ticker),
                  subtitle: Text(
                    '${_statusLabel(ticker.status)} • '
                    '${ticker.rowsWritten} تقرير • '
                    '${ticker.evaluatedRows} مُقيّم • '
                    '${ticker.pendingRows} منتظر',
                  ),
                  trailing: ticker.failedRows > 0
                      ? Text('${ticker.failedRows} فشل')
                      : null,
                ),
            ],
          ),
        ),
      );
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    }
  }

  Future<void> _delete(HistoricalReplayJob job) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف نهائي؟'),
        content: const Text(
          'سيتم حذف هذا الاختبار وجميع نتائجه نهائيًا. لا يمكن التراجع عن هذا الإجراء.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('رجوع'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('حذف نهائي'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    try {
      await ref.read(adminRepositoryProvider).deleteHistoricalReplay(job.id);
      if (!mounted) return;
      _showMessage('تم حذف الاختبار نهائيًا.');
      await _load(silent: true);
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('d MMMM y', 'ar');
    return Scaffold(
      appBar: AppBar(
        title: const Text('اختبار المحركات التاريخي'),
        actions: [
          IconButton(
            onPressed: () => _load(),
            tooltip: 'تحديث',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'تشغيل اختبار جديد',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'المحركات ترى فقط البيانات السابقة لكل يوم. '
                      'السيرفر يعالج 5 أسهم بالتوازي ويحفظ التقدم في قاعدة البيانات.',
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        OutlinedButton(
                          onPressed: _selectPreviousMonth,
                          child: const Text('الشهر السابق'),
                        ),
                        OutlinedButton(
                          onPressed: _selectCurrentMonth,
                          child: const Text('الشهر الحالي'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _DateButton(
                            label: 'من',
                            value: dateFormat.format(_startDate),
                            onPressed: _pickStart,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _DateButton(
                            label: 'إلى',
                            value: dateFormat.format(_endDate),
                            onPressed: _pickEnd,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<int>(
                      initialValue: _horizonSessions,
                      decoration: const InputDecoration(
                        labelText: 'مدة تقييم التوقع بعد التحليل',
                        border: OutlineInputBorder(),
                      ),
                      items: [
                        for (final value in _horizons)
                          DropdownMenuItem(
                            value: value,
                            child: Text('$value جلسات تداول'),
                          ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setState(() => _horizonSessions = value);
                        }
                      },
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'الفترة المختارة: '
                      '${_endDate.difference(_startDate).inDays + 1} يوم '
                      '• الحد الأقصى 31 يومًا',
                    ),
                    const SizedBox(height: 12),
                    FilledButton.icon(
                      onPressed: _submitting ? null : _start,
                      icon: _submitting
                          ? const SizedBox.square(
                              dimension: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.play_arrow_rounded),
                      label: const Text('بدء الاختبار على السيرفر'),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'يمكنك الخروج من التطبيق. عند العودة ستجد نسبة التقدم '
                      'وزر التنزيل مربوطين بحساب الأدمن.',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'اختبارات حسابي',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            if (_loading) const Center(child: CircularProgressIndicator()),
            if (_error != null)
              Card(
                child: ListTile(
                  leading: const Icon(Icons.error_outline),
                  title: const Text('تعذر تحميل الاختبارات'),
                  subtitle: Text(_error!),
                ),
              ),
            if (!_loading && _jobs.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('لم تبدأ أي اختبارات بعد.')),
                ),
              ),
            for (final job in _jobs)
              _JobCard(
                job: job,
                dateFormat: dateFormat,
                onDownload: job.downloadReady ? () => _download(job) : null,
                onDetails: () => _showDetails(job),
                onDelete: () => _delete(job),
              ),
          ],
        ),
      ),
    );
  }
}

class _DateButton extends StatelessWidget {
  const _DateButton({
    required this.label,
    required this.value,
    required this.onPressed,
  });

  final String label;
  final String value;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      ),
      child: Column(
        children: [
          Text(label),
          const SizedBox(height: 4),
          Text(value, textAlign: TextAlign.center),
        ],
      ),
    );
  }
}

class _JobCard extends StatelessWidget {
  const _JobCard({
    required this.job,
    required this.dateFormat,
    required this.onDetails,
    this.onDownload,
    this.onDelete,
  });

  final HistoricalReplayJob job;
  final DateFormat dateFormat;
  final VoidCallback onDetails;
  final VoidCallback? onDownload;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    final progress = job.totalTickers == 0 ? null : job.progressPct / 100;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(_jobIcon(job.status)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${dateFormat.format(job.startDate)} — '
                    '${dateFormat.format(job.endDate)}',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(label: Text(_statusLabel(job.status))),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(value: progress),
            const SizedBox(height: 6),
            Text(
              '${job.progressPct.toStringAsFixed(1)}% • '
              '${job.processedTickers}/${job.totalTickers} سهم • '
              '${job.parallelism} أسهم بالتوازي',
            ),
            const SizedBox(height: 4),
            Text(
              '${job.totalRows} تقرير يومي • '
              '${job.evaluatedRows} مُقيّم • '
              '${job.pendingRows} منتظر النتيجة • '
              '${job.failedTickers} سهم متعطل',
            ),
            Text(
              'المحرك ${job.engineVersion} • التقييم بعد '
              '${job.horizonSessions} جلسات',
            ),
            if (job.errorMessage != null) ...[
              const SizedBox(height: 6),
              Text(job.errorMessage!),
            ],
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: onDetails,
                  icon: const Icon(Icons.list_alt_outlined),
                  label: const Text('تفاصيل الأسهم'),
                ),
                if (onDownload != null)
                  FilledButton.icon(
                    onPressed: onDownload,
                    icon: const Icon(Icons.download_outlined),
                    label: const Text('تنزيل CSV'),
                  ),
                if (onDelete != null)
                  TextButton.icon(
                    onPressed: onDelete,
                    style: TextButton.styleFrom(
                      foregroundColor: Theme.of(context).colorScheme.error,
                    ),
                    icon: const Icon(Icons.delete_outline_rounded),
                    label: const Text('حذف نهائي'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

String _statusLabel(String value) => switch (value) {
  'pending' => 'في الانتظار',
  'running' => 'جاري التشغيل',
  'complete' => 'مكتمل',
  'partial' => 'مكتمل جزئيًا',
  'failed' => 'فشل',
  _ => value,
};

IconData _jobIcon(String status) => switch (status) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' => Icons.error_outline,
  'running' => Icons.sync,
  _ => Icons.schedule,
};

IconData _tickerIcon(String status) => switch (status) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' => Icons.error_outline,
  'running' => Icons.sync,
  _ => Icons.schedule,
};

```

---

### File: `lib\features\auth\account_recovery_screens.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import '../../data/backend_repository.dart';

class VerifyEmailScreen extends ConsumerStatefulWidget {
  const VerifyEmailScreen({super.key, this.email});

  final String? email;

  @override
  ConsumerState<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends ConsumerState<VerifyEmailScreen> {
  final _codeController = TextEditingController();
  late final TextEditingController _emailController;
  Timer? _cooldownTimer;
  bool _verifying = false;
  bool _resending = false;
  int _resendCooldown = 0;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.email ?? '');
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    _codeController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    final email = _emailController.text.trim();
    final code = _codeController.text.trim();
    if (!_isValidEmail(email)) {
      _showNotice('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    if (!RegExp(r'^\d{6}$').hasMatch(code) || _verifying) {
      _showNotice(
        'أدخل رمز التأكيد المكوّن من 6 أرقام.',
        AppNoticeTone.warning,
      );
      return;
    }
    setState(() => _verifying = true);
    try {
      await ref
          .read(backendRepositoryProvider)
          .verifyEmail(email: email, code: code);
      if (!mounted) {
        return;
      }
      _showNotice(
        'تم تأكيد بريدك بنجاح. يمكنك تسجيل الدخول الآن.',
        AppNoticeTone.success,
        title: 'تم التأكيد',
      );
      context.go('/login');
    } on ApiException catch (error) {
      _showNotice(error.message, AppNoticeTone.error, title: 'تعذر التأكيد');
    } finally {
      if (mounted) {
        setState(() => _verifying = false);
      }
    }
  }

  Future<void> _resend() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email)) {
      _showNotice('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    if (_resending || _resendCooldown > 0) {
      return;
    }
    setState(() => _resending = true);
    try {
      await ref.read(backendRepositoryProvider).resendVerification(email);
      if (!mounted) {
        return;
      }
      _startResendCooldown();
      _showNotice(
        'أرسلنا رمزًا جديدًا إلى بريدك. راجع البريد غير الهام أيضًا.',
        AppNoticeTone.success,
        title: 'تم إرسال الرمز',
      );
    } on ApiException catch (error) {
      _showNotice(error.message, AppNoticeTone.error, title: 'تعذر الإرسال');
    } finally {
      if (mounted) {
        setState(() => _resending = false);
      }
    }
  }

  void _startResendCooldown() {
    _cooldownTimer?.cancel();
    setState(() => _resendCooldown = 30);
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted || _resendCooldown <= 1) {
        timer.cancel();
        if (mounted) {
          setState(() => _resendCooldown = 0);
        }
        return;
      }
      setState(() => _resendCooldown -= 1);
    });
  }

  void _showNotice(String message, AppNoticeTone tone, {String? title}) {
    if (!mounted) {
      return;
    }
    AppNotice.show(context, message: message, title: title, tone: tone);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return _AccountActionScaffold(
      icon: Icons.mark_email_read_outlined,
      title: 'تأكيد البريد الإلكتروني',
      subtitle: 'أدخل الكود المكوّن من 6 أرقام الذي أرسلناه إلى بريدك.',
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: theme.colorScheme.primaryContainer.withValues(alpha: 0.35),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: theme.colorScheme.outlineVariant),
          ),
          child: Row(
            children: [
              Icon(Icons.schedule_rounded, color: theme.colorScheme.primary),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'الكود صالح لمدة 10 دقائق. لا تشاركه مع أي شخص.',
                  style: TextStyle(height: 1.5, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          textDirection: TextDirection.ltr,
          autofillHints: const [AutofillHints.email],
          decoration: const InputDecoration(
            labelText: 'البريد الإلكتروني',
            prefixIcon: Icon(Icons.alternate_email_rounded),
          ),
        ),
        const SizedBox(height: 18),
        TextField(
          controller: _codeController,
          autofocus: true,
          keyboardType: TextInputType.number,
          textInputAction: TextInputAction.done,
          autofillHints: const [AutofillHints.oneTimeCode],
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
            LengthLimitingTextInputFormatter(6),
          ],
          maxLength: 6,
          textAlign: TextAlign.center,
          textDirection: TextDirection.ltr,
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.w800,
            letterSpacing: 12,
          ),
          decoration: InputDecoration(
            counterText: '',
            hintText: '000000',
            hintStyle: TextStyle(
              color: theme.colorScheme.outlineVariant,
              letterSpacing: 12,
            ),
            filled: true,
            fillColor: theme.colorScheme.surfaceContainerLowest,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 20,
              vertical: 22,
            ),
          ),
          onSubmitted: (_) => _verify(),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          onPressed: _verifying ? null : _verify,
          icon: _verifying
              ? const _ButtonLoader()
              : const Icon(Icons.verified_rounded),
          label: Text(_verifying ? 'جاري التأكيد...' : 'تأكيد البريد'),
        ),
        const SizedBox(height: 24),
        const Divider(),
        const SizedBox(height: 14),
        OutlinedButton.icon(
          onPressed: _resending || _resendCooldown > 0 ? null : _resend,
          icon: _resending
              ? const _ButtonLoader()
              : const Icon(Icons.refresh_rounded),
          label: Text(
            _resending
                ? 'جاري الإرسال...'
                : _resendCooldown > 0
                ? 'إعادة الإرسال بعد $_resendCooldown ثانية'
                : 'إعادة إرسال الكود',
          ),
        ),
        TextButton(
          onPressed: () => context.go('/login'),
          child: const Text('العودة لتسجيل الدخول'),
        ),
      ],
    );
  }
}

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email) || _submitting) {
      _showMessage('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref.read(backendRepositoryProvider).forgotPassword(email);
      if (!mounted) {
        return;
      }
      _showMessage(
        'إذا كان الحساب موجودًا فستصلك تعليمات الاستعادة.',
        AppNoticeTone.success,
      );
      context.go('/reset-password?email=${Uri.encodeQueryComponent(email)}');
    } on ApiException catch (error) {
      _showMessage(error.message, AppNoticeTone.error);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  void _showMessage(String message, AppNoticeTone tone) {
    if (mounted) {
      AppNotice.show(context, message: message, tone: tone);
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AccountActionScaffold(
      icon: Icons.lock_reset_rounded,
      title: 'نسيت كلمة المرور؟',
      subtitle: 'أدخل بريدك وسنرسل تعليمات الاستعادة دون الكشف عن وجود الحساب.',
      children: [
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'البريد الإلكتروني',
            prefixIcon: Icon(Icons.alternate_email_rounded),
          ),
          onSubmitted: (_) => _submit(),
        ),
        const SizedBox(height: 18),
        FilledButton(
          onPressed: _submitting ? null : _submit,
          child: _submitting
              ? const _ButtonLoader()
              : const Text('إرسال تعليمات الاستعادة'),
        ),
        TextButton(
          onPressed: () => context.go('/login'),
          child: const Text('العودة لتسجيل الدخول'),
        ),
      ],
    );
  }
}

class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({super.key, this.email});

  final String? email;

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  late final TextEditingController _emailController;
  final _passwordController = TextEditingController();
  final _confirmationController = TextEditingController();
  final _otpFocusNode = FocusNode();
  final _otpController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;
  Timer? _cooldownTimer;
  bool _resending = false;
  int _resendCooldown = 0;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.email ?? '');
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmationController.dispose();
    _otpFocusNode.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _resend() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email) || _resending || _resendCooldown > 0) return;
    setState(() => _resending = true);
    try {
      await ref.read(backendRepositoryProvider).forgotPassword(email);
      if (!mounted) return;
      _startResendCooldown();
      _showMessage('تم إرسال رمز جديد إلى بريدك.', AppNoticeTone.success);
    } on ApiException catch (error) {
      _showMessage(error.message, AppNoticeTone.error);
    } finally {
      if (mounted) setState(() => _resending = false);
    }
  }

  void _startResendCooldown() {
    _cooldownTimer?.cancel();
    setState(() => _resendCooldown = 60);
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted || _resendCooldown <= 1) {
        timer.cancel();
        if (mounted) setState(() => _resendCooldown = 0);
        return;
      }
      setState(() => _resendCooldown -= 1);
    });
  }

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    final code = _otpController.text.trim();
    final password = _passwordController.text;
    if (!_isValidEmail(email)) {
      _showMessage('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    if (!RegExp(r'^\d{6}$').hasMatch(code)) {
      _showMessage(
        'أدخل رمز التحقق المكوّن من 6 أرقام.',
        AppNoticeTone.warning,
      );
      return;
    }
    final passwordError = _passwordError(password);
    if (passwordError != null) {
      _showMessage(passwordError, AppNoticeTone.warning);
      return;
    }
    if (password != _confirmationController.text) {
      _showMessage('تأكيد كلمة المرور غير مطابق.', AppNoticeTone.warning);
      return;
    }
    if (_submitting) return;
    setState(() => _submitting = true);
    try {
      await ref
          .read(backendRepositoryProvider)
          .resetPassword(email: email, code: code, newPassword: password);
      if (!mounted) return;
      _showMessage(
        'تم تغيير كلمة المرور. سجّل الدخول بالكلمة الجديدة.',
        AppNoticeTone.success,
      );
      context.go('/login');
    } on ApiException catch (error) {
      _showMessage(error.message, AppNoticeTone.error);
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _showMessage(String message, AppNoticeTone tone) {
    if (mounted) AppNotice.show(context, message: message, tone: tone);
  }

  @override
  Widget build(BuildContext context) {
    final email = widget.email;
    return _AccountActionScaffold(
      icon: Icons.lock_reset_rounded,
      title: 'إعادة تعيين كلمة المرور',
      subtitle: email != null
          ? 'أرسلنا رمزًا مكوّنًا من 6 أرقام إلى $email'
          : 'أدخل بريدك ورمز التحقق الذي أرسلناه إليك.',
      children: [
        if (email == null) ...[
          TextField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            textDirection: TextDirection.ltr,
            decoration: const InputDecoration(
              labelText: 'البريد الإلكتروني',
              prefixIcon: Icon(Icons.alternate_email_rounded),
            ),
          ),
          const SizedBox(height: 18),
        ],
        // ─── OTP 6-Box Widget ────────────────────────────────────────
        _OtpBoxField(
          controller: _otpController,
          focusNode: _otpFocusNode,
          onCompleted: (_) => FocusScope.of(context).nextFocus(),
        ),
        const SizedBox(height: 18),
        // ─── Password fields ─────────────────────────────────────────
        TextField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          textDirection: TextDirection.ltr,
          decoration: InputDecoration(
            labelText: 'كلمة المرور الجديدة',
            helperText: '10 أحرف على الأقل وحرف كبير وصغير ورقم.',
            prefixIcon: const Icon(Icons.lock_outline_rounded),
            suffixIcon: IconButton(
              onPressed: () =>
                  setState(() => _obscurePassword = !_obscurePassword),
              icon: Icon(
                _obscurePassword
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
              ),
            ),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _confirmationController,
          obscureText: _obscurePassword,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'تأكيد كلمة المرور',
            prefixIcon: Icon(Icons.verified_user_outlined),
          ),
          onSubmitted: (_) => _submit(),
        ),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: _submitting ? null : _submit,
          icon: _submitting
              ? const _ButtonLoader()
              : const Icon(Icons.check_circle_rounded),
          label: Text(
            _submitting ? 'جارٍ الحفظ...' : 'حفظ كلمة المرور الجديدة',
          ),
        ),
        const SizedBox(height: 14),
        OutlinedButton.icon(
          onPressed: _resending || _resendCooldown > 0 ? null : _resend,
          icon: _resending
              ? const _ButtonLoader()
              : const Icon(Icons.refresh_rounded),
          label: Text(
            _resending
                ? 'جارٍ الإرسال...'
                : _resendCooldown > 0
                ? 'إعادة الإرسال بعد $_resendCooldown ثانية'
                : 'إعادة إرسال الرمز',
          ),
        ),
        TextButton(
          onPressed: () => context.go('/login'),
          child: const Text('العودة لتسجيل الدخول'),
        ),
      ],
    );
  }
}

// ─── Custom 6-box OTP input widget ──────────────────────────────────────────
class _OtpBoxField extends StatefulWidget {
  const _OtpBoxField({
    required this.controller,
    required this.focusNode,
    this.onCompleted,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final ValueChanged<String>? onCompleted;

  @override
  State<_OtpBoxField> createState() => _OtpBoxFieldState();
}

class _OtpBoxFieldState extends State<_OtpBoxField> {
  static const int _length = 6;

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onTextChanged);
  }

  void _onTextChanged() {
    setState(() {});
    if (widget.controller.text.length == _length) {
      widget.onCompleted?.call(widget.controller.text);
    }
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onTextChanged);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final code = widget.controller.text;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        GestureDetector(
          onTap: () => widget.focusNode.requestFocus(),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(_length, (i) {
              final isFilled = i < code.length;
              final isActive = i == code.length && widget.focusNode.hasFocus;
              return AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                margin: const EdgeInsets.symmetric(horizontal: 5),
                width: 46,
                height: 56,
                decoration: BoxDecoration(
                  color: isFilled
                      ? theme.colorScheme.primaryContainer.withValues(
                          alpha: 0.5,
                        )
                      : theme.colorScheme.surfaceContainerLowest,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isActive
                        ? theme.colorScheme.primary
                        : isFilled
                        ? theme.colorScheme.primary.withValues(alpha: 0.5)
                        : theme.colorScheme.outlineVariant,
                    width: isActive ? 2.2 : 1.5,
                  ),
                ),
                alignment: Alignment.center,
                child: isFilled
                    ? Text(
                        code[i],
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: theme.colorScheme.onSurface,
                        ),
                      )
                    : isActive
                    ? Container(
                        width: 2,
                        height: 24,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      )
                    : null,
              );
            }),
          ),
        ),
        // Hidden real text field
        SizedBox(
          height: 0,
          child: Opacity(
            opacity: 0,
            child: TextField(
              controller: widget.controller,
              focusNode: widget.focusNode,
              keyboardType: TextInputType.number,
              autofillHints: const [AutofillHints.oneTimeCode],
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(_length),
              ],
              maxLength: _length,
            ),
          ),
        ),
      ],
    );
  }
}

class _AccountActionScaffold extends StatelessWidget {
  const _AccountActionScaffold({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.children,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    icon,
                    size: 58,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    title,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    subtitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.6,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 28),
                  ...children,
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ButtonLoader extends StatelessWidget {
  const _ButtonLoader();

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: 22,
      height: 22,
      child: CircularProgressIndicator(strokeWidth: 2.5),
    );
  }
}

bool _isValidEmail(String email) {
  return RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email);
}

String? _passwordError(String password) {
  if (password.length < 10) {
    return 'كلمة المرور يجب أن تكون 10 أحرف على الأقل.';
  }
  if (!RegExp('[a-z]').hasMatch(password) ||
      !RegExp('[A-Z]').hasMatch(password) ||
      !RegExp('[0-9]').hasMatch(password)) {
    return 'يجب أن تحتوي كلمة المرور على حرف كبير وصغير ورقم.';
  }
  return null;
}

```

---

### File: `lib\features\auth\auth_screens.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import 'session_controller.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _submitting) {
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref
          .read(sessionControllerProvider.notifier)
          .login(
            email: _emailController.text,
            password: _passwordController.text,
          );
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      AppNotice.show(
        context,
        title: error.statusCode == 403
            ? 'البريد غير مؤكد'
            : 'تعذر تسجيل الدخول',
        message: error.statusCode == 403
            ? 'أكد بريدك بالكود المرسل أولًا.'
            : error.message,
        tone: error.statusCode == 403
            ? AppNoticeTone.warning
            : AppNoticeTone.error,
      );
      if (error.statusCode == 403) {
        final email = Uri.encodeQueryComponent(_emailController.text.trim());
        context.go('/verify-email?email=$email');
      }
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AuthScaffold(
      title: 'مرحبًا بعودتك',
      subtitle: 'سجّل الدخول للوصول إلى التقارير والتحليلات ورصيدك.',
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              textDirection: TextDirection.ltr,
              decoration: const InputDecoration(
                labelText: 'البريد الإلكتروني',
                prefixIcon: Icon(Icons.alternate_email_rounded),
              ),
              validator: _validateEmail,
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _passwordController,
              obscureText: _obscurePassword,
              textDirection: TextDirection.ltr,
              decoration: InputDecoration(
                labelText: 'كلمة المرور',
                prefixIcon: const Icon(Icons.lock_outline_rounded),
                suffixIcon: IconButton(
                  onPressed: () =>
                      setState(() => _obscurePassword = !_obscurePassword),
                  icon: Icon(
                    _obscurePassword
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                  ),
                ),
              ),
              validator: (value) =>
                  value == null || value.isEmpty ? 'أدخل كلمة المرور.' : null,
              onFieldSubmitted: (_) => _submit(),
            ),
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child: TextButton(
                onPressed: () => context.go('/forgot-password'),
                child: const Text('نسيت كلمة المرور؟'),
              ),
            ),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2.5),
                    )
                  : const Text('تسجيل الدخول'),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => context.go('/register'),
              child: const Text('ليس لديك حساب؟ أنشئ حسابًا'),
            ),
          ],
        ),
      ),
    );
  }
}

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _submitting) {
      return;
    }
    setState(() => _submitting = true);
    try {
      final result = await ref
          .read(sessionControllerProvider.notifier)
          .register(
            email: _emailController.text,
            password: _passwordController.text,
            displayName: _nameController.text,
          );
      if (!mounted) {
        return;
      }
      final recoveredPendingAccount = result.weeklyPointsGranted == 0;
      AppNotice.show(
        context,
        title: recoveredPendingAccount
            ? 'استكمال تأكيد الحساب'
            : 'تم إنشاء الحساب',
        message: recoveredPendingAccount
            ? 'الحساب موجود لكنه لم يُؤكد بعد. أرسلنا كودًا جديدًا إلى بريدك دون إنشاء حساب أو رصيد مكرر.'
            : 'أضفنا ${result.weeklyPointsGranted ~/ 100} عملات إلى خطتك المجانية وأرسلنا كود التأكيد إلى بريدك.',
        tone: AppNoticeTone.success,
        duration: const Duration(seconds: 5),
      );
      final email = Uri.encodeQueryComponent(result.email);
      context.go('/verify-email?email=$email');
    } on ApiException catch (error) {
      if (mounted) {
        AppNotice.show(
          context,
          title: 'تعذر إنشاء الحساب',
          message: error.message,
          tone: AppNoticeTone.error,
        );
      }
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AuthScaffold(
      title: 'إنشاء حساب جديد',
      subtitle: 'ابدأ بالخطة المجانية واحصل على 3 عملات أسبوعيًا.',
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'الاسم الظاهر',
                prefixIcon: Icon(Icons.person_outline_rounded),
              ),
              validator: (value) {
                final cleaned = value?.trim() ?? '';
                return cleaned.length < 2 ? 'الاسم قصير جدًا.' : null;
              },
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              textDirection: TextDirection.ltr,
              decoration: const InputDecoration(
                labelText: 'البريد الإلكتروني',
                prefixIcon: Icon(Icons.alternate_email_rounded),
              ),
              validator: _validateEmail,
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _passwordController,
              obscureText: _obscurePassword,
              textDirection: TextDirection.ltr,
              decoration: InputDecoration(
                labelText: 'كلمة المرور',
                helperText: '10 أحرف على الأقل وحرف كبير وصغير ورقم.',
                prefixIcon: const Icon(Icons.lock_outline_rounded),
                suffixIcon: IconButton(
                  onPressed: () =>
                      setState(() => _obscurePassword = !_obscurePassword),
                  icon: Icon(
                    _obscurePassword
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                  ),
                ),
              ),
              validator: _validatePassword,
            ),
            const SizedBox(height: 22),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2.5),
                    )
                  : const Text('إنشاء الحساب'),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => context.go('/login'),
              child: const Text('لديك حساب بالفعل؟ سجّل الدخول'),
            ),
          ],
        ),
      ),
    );
  }
}

class _AuthScaffold extends StatelessWidget {
  const _AuthScaffold({
    required this.title,
    required this.subtitle,
    required this.child,
  });

  final String title;
  final String subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    Icons.show_chart_rounded,
                    size: 52,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    title,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    subtitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.6,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 28),
                  child,
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

String? _validateEmail(String? value) {
  final email = value?.trim() ?? '';
  final valid = RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email);
  return valid ? null : 'أدخل بريدًا إلكترونيًا صحيحًا.';
}

String? _validatePassword(String? value) {
  final password = value ?? '';
  if (password.length < 10) {
    return 'كلمة المرور يجب أن تكون 10 أحرف على الأقل.';
  }
  if (!RegExp('[a-z]').hasMatch(password) ||
      !RegExp('[A-Z]').hasMatch(password) ||
      !RegExp('[0-9]').hasMatch(password)) {
    return 'يجب أن تحتوي على حرف كبير وصغير ورقم.';
  }
  return null;
}

```

---

### File: `lib\features\auth\session_controller.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/demo_mode.dart';
import '../../core/network/api_exception.dart';
import '../../core/network/token_store.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';

enum SessionStatus { loading, unauthenticated, authenticated }

class SessionState {
  const SessionState({required this.status, this.profile, this.errorMessage});
  const SessionState.loading() : this(status: SessionStatus.loading);
  const SessionState.unauthenticated({String? errorMessage})
    : this(status: SessionStatus.unauthenticated, errorMessage: errorMessage);
  const SessionState.authenticated(UserProfile profile)
    : this(status: SessionStatus.authenticated, profile: profile);

  final SessionStatus status;
  final UserProfile? profile;
  final String? errorMessage;
}

class SessionController extends StateNotifier<SessionState> {
  SessionController({
    required BackendRepository repository,
    required TokenStore tokenStore,
  }) : _repository = repository,
       _tokenStore = tokenStore,
       super(const SessionState.loading()) {
    restore();
  }

  final BackendRepository _repository;
  final TokenStore _tokenStore;

  Future<void> restore() async {
    if (DemoMode.enabled) {
      loginAsDemo();
      return;
    }

    state = const SessionState.loading();
    try {
      final tokens = await _tokenStore.read();
      if (tokens == null) {
        state = const SessionState.unauthenticated();
        return;
      }

      final profile = await _repository.getProfile();
      state = SessionState.authenticated(profile);
    } on ApiException catch (error) {
      if (error.statusCode == 401) {
        await _clearTokensSafely();
      }
      state = SessionState.unauthenticated(errorMessage: error.message);
    } on Object {
      await _clearTokensSafely();
      state = const SessionState.unauthenticated(
        errorMessage: 'تعذر استعادة الجلسة السابقة. سجل الدخول مرة أخرى.',
      );
    }
  }

  Future<void> _clearTokensSafely() async {
    try {
      await _tokenStore.clear();
    } on Object {
      // Corrupted or restored encrypted storage must not prevent app startup.
    }
  }

  Future<void> login({required String email, required String password}) async {
    state = const SessionState.loading();
    try {
      await _repository.login(email: email, password: password);
      final profile = await _repository.getProfile();
      state = SessionState.authenticated(profile);
    } on ApiException catch (error) {
      state = SessionState.unauthenticated(errorMessage: error.message);
      rethrow;
    }
  }

  void loginAsDemo() {
    state = const SessionState.authenticated(
      UserProfile(
        id: 'demo-user',
        email: 'demo@sahmi-kasban.local',
        displayName: 'مستخدم تجريبي',
        avatarKey: 'avatar_1',
        emailVerified: true,
        planCode: 'free',
        balancePoints: 300,
        balanceCoins: '3.00',
        weeklyCoins: '3.00',
        adsEnabled: true,
      ),
    );
  }

  Future<RegistrationResult> register({
    required String email,
    required String password,
    required String displayName,
  }) {
    return _repository.register(
      email: email,
      password: password,
      displayName: displayName,
    );
  }

  Future<void> refreshProfile() async {
    if (state.status != SessionStatus.authenticated) {
      return;
    }
    final profile = await _repository.getProfile();
    state = SessionState.authenticated(profile);
  }

  Future<UserProfile> updateProfile({
    required String displayName,
    required String avatarKey,
  }) async {
    final profile = await _repository.updateProfile(
      displayName: displayName,
      avatarKey: avatarKey,
    );
    state = SessionState.authenticated(profile);
    return profile;
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const SessionState.unauthenticated();
  }
}

final sessionControllerProvider =
    StateNotifierProvider<SessionController, SessionState>((ref) {
      return SessionController(
        repository: ref.watch(backendRepositoryProvider),
        tokenStore: ref.watch(tokenStoreProvider),
      );
    });

```

---

### File: `lib\features\bootstrap\splash_screen.dart`

```dart
import 'package:flutter/material.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Directionality(
        textDirection: TextDirection.rtl,
        child: DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: [Color(0xFF041F18), Color(0xFF07543A), Color(0xFF0B382A)],
            ),
          ),
          child: Stack(
            fit: StackFit.expand,
            children: [
              _AmbientCircle(
                alignment: Alignment.topLeft,
                size: 260,
                color: Color(0x1FC9A85C),
              ),
              _AmbientCircle(
                alignment: Alignment.bottomRight,
                size: 310,
                color: Color(0x1F2EB67D),
              ),
              SafeArea(
                child: Center(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 32),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _BrandMark(),
                        SizedBox(height: 28),
                        Text(
                          'سهمي كسبان',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 38,
                            height: 1.15,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.2,
                          ),
                        ),
                        SizedBox(height: 10),
                        Text(
                          'تحليل أذكى • قرارات أوضح',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFFE8D39A),
                            fontSize: 16,
                            height: 1.5,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        SizedBox(height: 34),
                        SizedBox(
                          width: 104,
                          child: LinearProgressIndicator(
                            minHeight: 4,
                            borderRadius: BorderRadius.all(Radius.circular(20)),
                            backgroundColor: Color(0x33FFFFFF),
                            color: Color(0xFFD8B867),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BrandMark extends StatelessWidget {
  const _BrandMark();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 132,
      height: 132,
      padding: const EdgeInsets.all(7),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(36),
        gradient: const LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [Color(0xFFF2D996), Color(0xFFB98B2F)],
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x66000000),
            blurRadius: 30,
            offset: Offset(0, 14),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(30),
        child: Image.asset(
          'assets/branding/app_icon.png',
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return const ColoredBox(
              color: Color(0xFF07543A),
              child: Icon(
                Icons.trending_up_rounded,
                size: 56,
                color: Color(0xFFD8B867),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _AmbientCircle extends StatelessWidget {
  const _AmbientCircle({
    required this.alignment,
    required this.size,
    required this.color,
  });

  final Alignment alignment;
  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Transform.translate(
        offset: Offset(
          alignment.x.isNegative ? -size * 0.34 : size * 0.34,
          alignment.y.isNegative ? -size * 0.34 : size * 0.34,
        ),
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\community\community_create_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'community_providers.dart';
import 'community_repository.dart';

class CommunityCreateScreen extends ConsumerStatefulWidget {
  const CommunityCreateScreen({super.key});

  @override
  ConsumerState<CommunityCreateScreen> createState() =>
      _CommunityCreateScreenState();
}

class _CommunityCreateScreenState extends ConsumerState<CommunityCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  late final String _submissionKey;
  MarketInstrument? _selectedInstrument;
  String _periodType = 'next_session';
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _submissionKey =
        'discussion-${DateTime.now().microsecondsSinceEpoch.toString()}';
  }

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _selectTicker() async {
    final selected = await showModalBottomSheet<MarketInstrument>(
      context: context,
      isScrollControlled: true,
      builder: (context) => const _TickerPickerSheet(),
    );
    if (selected != null && mounted) {
      setState(() => _selectedInstrument = selected);
    }
  }

  Future<void> _submit() async {
    if (_submitting || !_formKey.currentState!.validate()) {
      return;
    }
    final instrument = _selectedInstrument;
    if (instrument == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('اختر السهم المرتبط بالمناقشة.')),
      );
      return;
    }

    setState(() => _submitting = true);
    try {
      final result = await ref
          .read(communityRepositoryProvider)
          .submitDiscussion(
            submissionKey: _submissionKey,
            ticker: instrument.ticker,
            title: _titleController.text,
            content: _contentController.text,
            periodType: _periodType,
          );
      ref.invalidate(communityFeedProvider);
      ref.invalidate(myDiscussionsProvider);
      ref.invalidate(walletSummaryProvider);
      await ref.read(sessionControllerProvider.notifier).refreshProfile();
      if (!mounted) {
        return;
      }
      await ref
          .read(freePlanInterstitialProvider)
          .recordMeaningfulAction(
            enabled:
                ref.read(sessionControllerProvider).profile?.adsEnabled == true,
          );
      if (!mounted) {
        return;
      }
      final message = switch (result.discussion.status) {
        'published' => 'تم قبول المناقشة ونشرها وتأكيد خصم 0.5 عملة.',
        'rejected' => 'تم رفض المناقشة وإعادة الرصيد كاملًا.',
        _ => 'تم إرسال المناقشة وهي قيد المراجعة مع حجز 0.5 عملة مؤقتًا.',
      };
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
      context.pop();
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      final retry = error.retryAfterSeconds;
      final message = retry == null
          ? error.message
          : '${error.message}\nأعد المحاولة بعد $retry ثانية.';
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('إنشاء مناقشة')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.account_balance_wallet_outlined,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text(
                        'سيتم حجز 0.5 عملة مؤقتًا. عند القبول يتحول الحجز إلى خصم نهائي، وعند الرفض يعود الرصيد كاملًا.',
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _submitting ? null : _selectTicker,
              icon: const Icon(Icons.candlestick_chart_outlined),
              label: Text(
                _selectedInstrument == null
                    ? 'اختر السهم'
                    : 'السهم: ${_selectedInstrument!.ticker}',
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _titleController,
              enabled: !_submitting,
              maxLength: 180,
              decoration: const InputDecoration(
                labelText: 'عنوان المناقشة',
                hintText: 'اكتب عنوانًا واضحًا لا يقل عن 10 أحرف',
              ),
              validator: (value) {
                final cleaned = value?.trim() ?? '';
                if (cleaned.length < 10) {
                  return 'العنوان يجب أن يحتوي على 10 أحرف على الأقل.';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _contentController,
              enabled: !_submitting,
              minLines: 6,
              maxLines: 12,
              maxLength: 5000,
              decoration: const InputDecoration(
                labelText: 'المحتوى والتوقع',
                hintText:
                    'اشرح توقعك وأسبابه من دون روابط أو أرقام هاتف أو ادعاءات ربح مضمون.',
                alignLabelWithHint: true,
              ),
              validator: (value) {
                final cleaned = value?.trim() ?? '';
                if (cleaned.length < 20) {
                  return 'المحتوى يجب أن يحتوي على 20 حرفًا على الأقل.';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _periodType,
              decoration: const InputDecoration(labelText: 'مدة التوقع'),
              items: const [
                DropdownMenuItem(
                  value: 'next_session',
                  child: Text('الجلسة القادمة'),
                ),
                DropdownMenuItem(value: 'week', child: Text('أسبوع')),
                DropdownMenuItem(value: 'month', child: Text('شهر')),
              ],
              onChanged: _submitting
                  ? null
                  : (value) =>
                        setState(() => _periodType = value ?? 'next_session'),
            ),
            const SizedBox(height: 22),
            FilledButton.icon(
              onPressed: _submitting ? null : _submit,
              icon: _submitting
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send_rounded),
              label: Text(
                _submitting ? 'جارٍ الإرسال والمراجعة...' : 'إرسال للمراجعة',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TickerPickerSheet extends ConsumerStatefulWidget {
  const _TickerPickerSheet();

  @override
  ConsumerState<_TickerPickerSheet> createState() => _TickerPickerSheetState();
}

class _TickerPickerSheetState extends ConsumerState<_TickerPickerSheet> {
  final _searchController = TextEditingController();
  List<MarketInstrument> _items = const [];
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) {
      setState(() => _error = 'اكتب رمز السهم أو جزءًا منه.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(query, limit: 30);
      if (mounted) {
        setState(() => _items = items);
      }
    } on Object catch (error) {
      if (mounted) {
        setState(() => _error = error.toString());
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          20,
          20,
          20,
          20 + MediaQuery.viewInsetsOf(context).bottom,
        ),
        child: SizedBox(
          height: MediaQuery.sizeOf(context).height * 0.65,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'اختيار سهم من EGX',
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: _searchController,
                autofocus: true,
                textCapitalization: TextCapitalization.characters,
                textInputAction: TextInputAction.search,
                decoration: InputDecoration(
                  labelText: 'رمز السهم',
                  hintText: 'COMI',
                  suffixIcon: IconButton(
                    onPressed: _loading ? null : _search,
                    icon: const Icon(Icons.search_rounded),
                  ),
                ),
                onSubmitted: (_) => _search(),
              ),
              if (_error != null) ...[
                const SizedBox(height: 10),
                Text(
                  _error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: 12),
              Expanded(
                child: _loading
                    ? const Center(child: CircularProgressIndicator())
                    : _items.isEmpty
                    ? const Center(child: Text('ابحث لاختيار السهم.'))
                    : ListView.separated(
                        itemCount: _items.length,
                        separatorBuilder: (context, index) => const Divider(),
                        itemBuilder: (context, index) {
                          final item = _items[index];
                          return ListTile(
                            title: Text(item.ticker),
                            subtitle: Text(
                              item.description.isEmpty
                                  ? '${item.exchange} — ${item.providerSymbol}'
                                  : item.description,
                              textDirection: item.description.isEmpty
                                  ? TextDirection.ltr
                                  : TextDirection.rtl,
                            ),
                            trailing: const Icon(Icons.chevron_left_rounded),
                            onTap: () => Navigator.of(context).pop(item),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\community\community_detail_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../../core/network/api_exception.dart';
import '../../widgets/structured_data_card.dart';
import '../auth/session_controller.dart';
import 'community_models.dart';
import 'community_providers.dart';
import 'community_repository.dart';
import 'prediction_verification_card.dart';

class CommunityDetailScreen extends ConsumerStatefulWidget {
  const CommunityDetailScreen({required this.discussionId, super.key});

  final String discussionId;

  @override
  ConsumerState<CommunityDetailScreen> createState() =>
      _CommunityDetailScreenState();
}

class _CommunityDetailScreenState extends ConsumerState<CommunityDetailScreen> {
  bool _mutedLocally = false;
  bool _actionBusy = false;

  Future<void> _refresh() async {
    ref.invalidate(communityDiscussionProvider(widget.discussionId));
    await ref.read(communityDiscussionProvider(widget.discussionId).future);
  }

  Future<void> _report(CommunityDiscussion discussion) async {
    final result = await showDialog<_ReportInput>(
      context: context,
      builder: (context) => const _ReportDialog(),
    );
    if (result == null) {
      return;
    }
    await _runAction(
      () => ref
          .read(communityRepositoryProvider)
          .reportDiscussion(
            discussionId: discussion.id,
            reasonCode: result.reasonCode,
            details: result.details,
          ),
      successMessage: 'تم إرسال البلاغ للمراجعة.',
    );
  }

  Future<void> _toggleMute(CommunityDiscussion discussion) async {
    if (_mutedLocally) {
      await _runAction(
        () => ref
            .read(communityRepositoryProvider)
            .unmuteUser(discussion.author.userId),
        successMessage: 'تم إلغاء كتم المستخدم.',
        afterSuccess: () => setState(() => _mutedLocally = false),
      );
    } else {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('كتم المستخدم'),
          content: const Text(
            'ستختفي مناقشات هذا المستخدم من صفحة المجتمع الخاصة بك.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('إلغاء'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('كتم'),
            ),
          ],
        ),
      );
      if (confirmed != true) {
        return;
      }
      await _runAction(
        () => ref
            .read(communityRepositoryProvider)
            .muteUser(discussion.author.userId),
        successMessage: 'تم كتم المستخدم وإخفاء مناقشاته من المجتمع.',
        afterSuccess: () => setState(() => _mutedLocally = true),
      );
    }
    ref.invalidate(communityFeedProvider);
  }

  Future<void> _appeal(CommunityDiscussion discussion) async {
    final message = await showDialog<String>(
      context: context,
      builder: (context) => const _AppealDialog(),
    );
    if (message == null) {
      return;
    }
    await _runAction(
      () => ref
          .read(communityRepositoryProvider)
          .submitAppeal(discussionId: discussion.id, message: message),
      successMessage: 'تم إرسال الاستئناف للمراجعة.',
      afterSuccess: () {
        ref.invalidate(myAppealsProvider);
        ref.invalidate(myDiscussionsProvider);
      },
    );
  }

  Future<void> _runAction(
    Future<Object?> Function() action, {
    required String successMessage,
    VoidCallback? afterSuccess,
  }) async {
    if (_actionBusy) {
      return;
    }
    setState(() => _actionBusy = true);
    try {
      await action();
      afterSuccess?.call();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(successMessage)));
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    } finally {
      if (mounted) {
        setState(() => _actionBusy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final discussion = ref.watch(
      communityDiscussionProvider(widget.discussionId),
    );
    final currentUserId = ref.watch(sessionControllerProvider).profile?.id;

    return Scaffold(
      appBar: AppBar(title: const Text('تفاصيل المناقشة')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: discussion.when(
          loading: () => ListView(
            children: [
              SizedBox(height: 240),
              Center(child: CircularProgressIndicator()),
            ],
          ),
          error: (error, stackTrace) => ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Text('تعذر تحميل المناقشة.'),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        onPressed: () => ref.invalidate(
                          communityDiscussionProvider(widget.discussionId),
                        ),
                        child: const Text('إعادة المحاولة'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          data: (item) {
            final isOwner = currentUserId == item.author.userId;
            return ListView(
              padding: const EdgeInsets.all(20),
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 24,
                              backgroundImage: AssetImage(
                                avatarAssetPath(item.author.avatarKey),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                item.author.displayName,
                                style: Theme.of(context).textTheme.titleMedium
                                    ?.copyWith(fontWeight: FontWeight.w800),
                              ),
                            ),
                            Chip(label: Text(item.ticker)),
                          ],
                        ),
                        const SizedBox(height: 18),
                        Text(
                          item.title,
                          style: Theme.of(context).textTheme.titleLarge
                              ?.copyWith(fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(height: 12),
                        Text(item.content),
                        const SizedBox(height: 16),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            Chip(label: Text(item.periodLabel)),
                            Chip(label: Text(item.statusLabel)),
                          ],
                        ),
                        if (item.rejectionCode != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            'سبب الرفض: ${item.rejectionCode}',
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                if (item.frozenPrediction.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  StructuredDataCard(
                    title: 'التوقع المجمد وقت النشر',
                    data: item.frozenPrediction,
                  ),
                ],
                if (isOwner && item.status == 'published') ...[
                  const SizedBox(height: 14),
                  PredictionVerificationCard(discussionId: item.id),
                ],
                if (item.moderationResult.isNotEmpty && isOwner) ...[
                  const SizedBox(height: 14),
                  StructuredDataCard(
                    title: 'نتيجة المراجعة',
                    data: item.moderationResult,
                  ),
                ],
                const SizedBox(height: 18),
                if (isOwner && item.canAppeal)
                  FilledButton.icon(
                    onPressed: _actionBusy ? null : () => _appeal(item),
                    icon: const Icon(Icons.gavel_outlined),
                    label: const Text('تقديم استئناف'),
                  ),
                if (!isOwner) ...[
                  OutlinedButton.icon(
                    onPressed: _actionBusy ? null : () => _report(item),
                    icon: const Icon(Icons.flag_outlined),
                    label: const Text('الإبلاغ عن المناقشة'),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    onPressed: _actionBusy ? null : () => _toggleMute(item),
                    icon: Icon(
                      _mutedLocally
                          ? Icons.volume_up_outlined
                          : Icons.volume_off_outlined,
                    ),
                    label: Text(
                      _mutedLocally ? 'إلغاء كتم المستخدم' : 'كتم المستخدم',
                    ),
                  ),
                ],
                if (_actionBusy) ...[
                  const SizedBox(height: 16),
                  const Center(child: CircularProgressIndicator()),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}

class _ReportInput {
  const _ReportInput({required this.reasonCode, required this.details});

  final String reasonCode;
  final String details;
}

class _ReportDialog extends StatefulWidget {
  const _ReportDialog();

  @override
  State<_ReportDialog> createState() => _ReportDialogState();
}

class _ReportDialogState extends State<_ReportDialog> {
  final _detailsController = TextEditingController();
  String _reasonCode = 'spam';

  @override
  void dispose() {
    _detailsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('الإبلاغ عن المناقشة'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _reasonCode,
            decoration: const InputDecoration(labelText: 'سبب البلاغ'),
            items: const [
              DropdownMenuItem(
                value: 'spam',
                child: Text('محتوى مكرر أو مزعج'),
              ),
              DropdownMenuItem(value: 'abuse', child: Text('إساءة')),
              DropdownMenuItem(value: 'misleading', child: Text('محتوى مضلل')),
              DropdownMenuItem(
                value: 'contact_info',
                child: Text('بيانات تواصل'),
              ),
              DropdownMenuItem(value: 'off_topic', child: Text('خارج الموضوع')),
              DropdownMenuItem(value: 'other', child: Text('سبب آخر')),
            ],
            onChanged: (value) => setState(() => _reasonCode = value ?? 'spam'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _detailsController,
            maxLength: 1000,
            minLines: 2,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: 'تفاصيل إضافية',
              alignLabelWithHint: true,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('إلغاء'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(
            _ReportInput(
              reasonCode: _reasonCode,
              details: _detailsController.text,
            ),
          ),
          child: const Text('إرسال البلاغ'),
        ),
      ],
    );
  }
}

class _AppealDialog extends StatefulWidget {
  const _AppealDialog();

  @override
  State<_AppealDialog> createState() => _AppealDialogState();
}

class _AppealDialogState extends State<_AppealDialog> {
  final _controller = TextEditingController();
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submit() {
    final message = _controller.text.trim();
    if (message.length < 20) {
      setState(() => _error = 'اكتب سببًا واضحًا لا يقل عن 20 حرفًا.');
      return;
    }
    Navigator.of(context).pop(message);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('تقديم استئناف'),
      content: TextField(
        controller: _controller,
        autofocus: true,
        minLines: 4,
        maxLines: 8,
        maxLength: 2000,
        decoration: InputDecoration(
          labelText: 'وضح سبب طلب إعادة المراجعة',
          alignLabelWithHint: true,
          errorText: _error,
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('إلغاء'),
        ),
        FilledButton(onPressed: _submit, child: const Text('إرسال الاستئناف')),
      ],
    );
  }
}

```

---

### File: `lib\features\community\community_feed_tab.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/avatar_assets.dart';
import '../monetization/free_plan_ads.dart';
import 'community_models.dart';
import 'community_providers.dart';

class CommunityFeedTab extends ConsumerStatefulWidget {
  const CommunityFeedTab({super.key});

  @override
  ConsumerState<CommunityFeedTab> createState() => _CommunityFeedTabState();
}

class _CommunityFeedTabState extends ConsumerState<CommunityFeedTab> {
  final _tickerController = TextEditingController();

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  Future<void> _refresh() async {
    ref.invalidate(communityFeedProvider);
    await ref.read(communityFeedProvider.future);
  }

  void _applyTickerFilter() {
    final value = _tickerController.text.trim().toUpperCase();
    ref.read(communityTickerFilterProvider.notifier).state = value.isEmpty
        ? null
        : value;
  }

  void _clearTickerFilter() {
    _tickerController.clear();
    ref.read(communityTickerFilterProvider.notifier).state = null;
  }

  @override
  Widget build(BuildContext context) {
    final feed = ref.watch(communityFeedProvider);
    final activeTicker = ref.watch(communityTickerFilterProvider);

    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: () => context.push('/community/new'),
                  icon: const Icon(Icons.add_comment_outlined),
                  label: const Text('إنشاء مناقشة'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/community/mine'),
                  icon: const Icon(Icons.forum_outlined),
                  label: const Text('مناقشاتي'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _tickerController,
            textCapitalization: TextCapitalization.characters,
            textInputAction: TextInputAction.search,
            decoration: InputDecoration(
              labelText: 'فلترة برمز السهم',
              hintText: 'مثال: COMI',
              prefixIcon: const Icon(Icons.search_rounded),
              suffixIcon: activeTicker == null
                  ? IconButton(
                      onPressed: _applyTickerFilter,
                      icon: const Icon(Icons.tune_rounded),
                      tooltip: 'تطبيق الفلتر',
                    )
                  : IconButton(
                      onPressed: _clearTickerFilter,
                      icon: const Icon(Icons.close_rounded),
                      tooltip: 'إلغاء الفلتر',
                    ),
            ),
            onSubmitted: (_) => _applyTickerFilter(),
          ),
          if (activeTicker != null) ...[
            const SizedBox(height: 10),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Chip(label: Text('السهم: $activeTicker')),
            ),
          ],
          const SizedBox(height: 14),
          const FreePlanNativeAd(),
          const SizedBox(height: 14),
          feed.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(36),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (error, stackTrace) => _CommunityErrorCard(
              message: 'تعذر تحميل مناقشات المجتمع.',
              onRetry: () => ref.invalidate(communityFeedProvider),
            ),
            data: (page) {
              if (page.items.isEmpty) {
                return const _EmptyCommunityCard();
              }
              return Column(
                children: [
                  for (final discussion in page.items) ...[
                    CommunityDiscussionCard(discussion: discussion),
                    const SizedBox(height: 12),
                  ],
                  if (page.hasMore)
                    const Padding(
                      padding: EdgeInsets.only(top: 4),
                      child: Text(
                        'توجد مناقشات إضافية وسيتم تحميلها في تحديث لاحق للصفحة.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class CommunityDiscussionCard extends StatelessWidget {
  const CommunityDiscussionCard({
    required this.discussion,
    this.showStatus = false,
    super.key,
  });

  final CommunityDiscussion discussion;
  final bool showStatus;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/community/${discussion.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundImage: AssetImage(
                      avatarAssetPath(discussion.author.avatarKey),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          discussion.author.displayName,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        Text(
                          _formatDate(
                            discussion.publishedAt ?? discussion.createdAt,
                          ),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                  Chip(label: Text(discussion.ticker)),
                ],
              ),
              const SizedBox(height: 14),
              Text(
                discussion.title,
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              Text(
                discussion.content,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  Chip(label: Text(discussion.periodLabel)),
                  if (showStatus) Chip(label: Text(discussion.statusLabel)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyCommunityCard extends StatelessWidget {
  const _EmptyCommunityCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(28),
        child: Column(
          children: [
            Icon(Icons.forum_outlined, size: 44),
            SizedBox(height: 12),
            Text(
              'لا توجد مناقشات منشورة تطابق الفلتر الحالي.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _CommunityErrorCard extends StatelessWidget {
  const _CommunityErrorCard({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: onRetry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

String _formatDate(DateTime value) {
  final local = value.toLocal();
  String two(int number) => number.toString().padLeft(2, '0');
  return '${two(local.day)}/${two(local.month)}/${local.year} '
      '${two(local.hour)}:${two(local.minute)}';
}

```

---

### File: `lib\features\community\community_models.dart`

```dart
class CommunityAuthor {
  const CommunityAuthor({
    required this.userId,
    required this.displayName,
    required this.avatarKey,
  });

  final String userId;
  final String displayName;
  final String avatarKey;

  factory CommunityAuthor.fromJson(Map<String, dynamic> json) {
    return CommunityAuthor(
      userId: _requiredString(json, 'user_id'),
      displayName: _requiredString(json, 'display_name'),
      avatarKey: _requiredString(json, 'avatar_key'),
    );
  }
}

class CommunityDiscussion {
  const CommunityDiscussion({
    required this.id,
    required this.ticker,
    required this.title,
    required this.content,
    required this.periodType,
    required this.status,
    required this.moderationResult,
    required this.frozenPrediction,
    required this.rejectionCode,
    required this.createdAt,
    required this.reviewedAt,
    required this.publishedAt,
    required this.author,
  });

  final String id;
  final String ticker;
  final String title;
  final String content;
  final String periodType;
  final String status;
  final Map<String, dynamic> moderationResult;
  final Map<String, dynamic> frozenPrediction;
  final String? rejectionCode;
  final DateTime createdAt;
  final DateTime? reviewedAt;
  final DateTime? publishedAt;
  final CommunityAuthor author;

  bool get canAppeal => status == 'rejected' || status == 'hidden';

  String get periodLabel => switch (periodType) {
    'next_session' => 'الجلسة القادمة',
    'week' => 'أسبوع',
    'month' => 'شهر',
    _ => periodType,
  };

  String get statusLabel => switch (status) {
    'pending_review' => 'قيد المراجعة',
    'published' => 'منشورة',
    'rejected' => 'مرفوضة',
    'hidden' => 'مخفية',
    _ => status,
  };

  factory CommunityDiscussion.fromJson(Map<String, dynamic> json) {
    return CommunityDiscussion(
      id: _requiredString(json, 'id'),
      ticker: _requiredString(json, 'ticker'),
      title: _requiredString(json, 'title'),
      content: _requiredString(json, 'content'),
      periodType: _requiredString(json, 'period_type'),
      status: _requiredString(json, 'status'),
      moderationResult: _mapOrEmpty(json['moderation_result']),
      frozenPrediction: _mapOrEmpty(json['frozen_prediction']),
      rejectionCode: json['rejection_code'] as String?,
      createdAt: _requiredDate(json, 'created_at'),
      reviewedAt: _optionalDate(json['reviewed_at']),
      publishedAt: _optionalDate(json['published_at']),
      author: CommunityAuthor.fromJson(_requiredMap(json['author'])),
    );
  }
}

class CommunityDiscussionPage {
  const CommunityDiscussionPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<CommunityDiscussion> items;
  final int total;
  final int limit;
  final int offset;

  bool get hasMore => offset + items.length < total;

  factory CommunityDiscussionPage.fromJson(Map<String, dynamic> json) {
    return CommunityDiscussionPage(
      items: _requiredList(json['items'])
          .map((item) => CommunityDiscussion.fromJson(_requiredMap(item)))
          .toList(growable: false),
      total: _requiredInt(json, 'total'),
      limit: _requiredInt(json, 'limit'),
      offset: _requiredInt(json, 'offset'),
    );
  }
}

class CommunityDiscussionSubmission {
  const CommunityDiscussionSubmission({
    required this.discussion,
    required this.heldPoints,
    required this.heldCoins,
    required this.balancePoints,
    required this.balanceCoins,
    required this.idempotent,
  });

  final CommunityDiscussion discussion;
  final int heldPoints;
  final String heldCoins;
  final int balancePoints;
  final String balanceCoins;
  final bool idempotent;

  factory CommunityDiscussionSubmission.fromJson(Map<String, dynamic> json) {
    return CommunityDiscussionSubmission(
      discussion: CommunityDiscussion.fromJson(
        _requiredMap(json['discussion']),
      ),
      heldPoints: _requiredInt(json, 'held_points'),
      heldCoins: _requiredString(json, 'held_coins'),
      balancePoints: _requiredInt(json, 'balance_points'),
      balanceCoins: _requiredString(json, 'balance_coins'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class CommunityReportResult {
  const CommunityReportResult({
    required this.reportId,
    required this.discussionId,
    required this.status,
    required this.idempotent,
  });

  final String reportId;
  final String discussionId;
  final String status;
  final bool idempotent;

  factory CommunityReportResult.fromJson(Map<String, dynamic> json) {
    return CommunityReportResult(
      reportId: _requiredString(json, 'report_id'),
      discussionId: _requiredString(json, 'discussion_id'),
      status: _requiredString(json, 'status'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class CommunityMuteResult {
  const CommunityMuteResult({
    required this.mutedUserId,
    required this.muted,
    required this.idempotent,
  });

  final String mutedUserId;
  final bool muted;
  final bool idempotent;

  factory CommunityMuteResult.fromJson(Map<String, dynamic> json) {
    return CommunityMuteResult(
      mutedUserId: _requiredString(json, 'muted_user_id'),
      muted: _requiredBool(json, 'muted'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class CommunityAppeal {
  const CommunityAppeal({
    required this.id,
    required this.discussionId,
    required this.userId,
    required this.sourceStatus,
    required this.message,
    required this.status,
    required this.createdAt,
    required this.resolvedAt,
    required this.resolutionReasonCode,
    required this.resolutionDetails,
  });

  final String id;
  final String discussionId;
  final String userId;
  final String sourceStatus;
  final String message;
  final String status;
  final DateTime createdAt;
  final DateTime? resolvedAt;
  final String? resolutionReasonCode;
  final Map<String, dynamic> resolutionDetails;

  String get statusLabel => switch (status) {
    'open' => 'قيد المراجعة',
    'accepted' => 'مقبول',
    'rejected' => 'مرفوض',
    _ => status,
  };

  factory CommunityAppeal.fromJson(Map<String, dynamic> json) {
    return CommunityAppeal(
      id: _requiredString(json, 'id'),
      discussionId: _requiredString(json, 'discussion_id'),
      userId: _requiredString(json, 'user_id'),
      sourceStatus: _requiredString(json, 'source_status'),
      message: _requiredString(json, 'message'),
      status: _requiredString(json, 'status'),
      createdAt: _requiredDate(json, 'created_at'),
      resolvedAt: _optionalDate(json['resolved_at']),
      resolutionReasonCode: json['resolution_reason_code'] as String?,
      resolutionDetails: _mapOrEmpty(json['resolution_details']),
    );
  }
}

class CommunityAppealPage {
  const CommunityAppealPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<CommunityAppeal> items;
  final int total;
  final int limit;
  final int offset;

  factory CommunityAppealPage.fromJson(Map<String, dynamic> json) {
    return CommunityAppealPage(
      items: _requiredList(json['items'])
          .map((item) => CommunityAppeal.fromJson(_requiredMap(item)))
          .toList(growable: false),
      total: _requiredInt(json, 'total'),
      limit: _requiredInt(json, 'limit'),
      offset: _requiredInt(json, 'offset'),
    );
  }
}

class CommunityAppealSubmission {
  const CommunityAppealSubmission({
    required this.appeal,
    required this.idempotent,
  });

  final CommunityAppeal appeal;
  final bool idempotent;

  factory CommunityAppealSubmission.fromJson(Map<String, dynamic> json) {
    return CommunityAppealSubmission(
      appeal: CommunityAppeal.fromJson(_requiredMap(json['appeal'])),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

Map<String, dynamic> _requiredMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  throw const FormatException('Expected a JSON object.');
}

Map<String, dynamic> _mapOrEmpty(Object? value) {
  if (value == null) {
    return const <String, dynamic>{};
  }
  return _requiredMap(value);
}

List<Object?> _requiredList(Object? value) {
  if (value is List) {
    return List<Object?>.from(value);
  }
  throw const FormatException('Expected a JSON list.');
}

String _requiredString(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

int _requiredInt(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is int) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

bool _requiredBool(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is bool) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

DateTime _requiredDate(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is String) {
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return parsed;
    }
  }
  throw FormatException('Missing or invalid $key.');
}

DateTime? _optionalDate(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is String) {
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return parsed;
    }
  }
  throw const FormatException('Invalid optional date.');
}

```

---

### File: `lib\features\community\community_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'community_models.dart';
import 'community_repository.dart';

final communityTickerFilterProvider = StateProvider.autoDispose<String?>((ref) {
  return null;
});

final communityFeedProvider =
    FutureProvider.autoDispose<CommunityDiscussionPage>((ref) {
      final ticker = ref.watch(communityTickerFilterProvider);
      return ref
          .watch(communityRepositoryProvider)
          .listDiscussions(ticker: ticker);
    });

final myDiscussionsProvider =
    FutureProvider.autoDispose<CommunityDiscussionPage>((ref) {
      return ref.watch(communityRepositoryProvider).listMyDiscussions();
    });

final myAppealsProvider = FutureProvider.autoDispose<CommunityAppealPage>((
  ref,
) {
  return ref.watch(communityRepositoryProvider).listMyAppeals();
});

final communityDiscussionProvider = FutureProvider.autoDispose
    .family<CommunityDiscussion, String>((ref, discussionId) {
      return ref.watch(communityRepositoryProvider).getDiscussion(discussionId);
    });

```

---

### File: `lib\features\community\community_repository.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'community_models.dart';

class CommunityRepository {
  const CommunityRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<CommunityDiscussionPage> listDiscussions({
    String? ticker,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions',
        queryParameters: <String, dynamic>{
          if (ticker != null && ticker.trim().isNotEmpty)
            'ticker': ticker.trim().toUpperCase(),
          'limit': limit,
          'offset': offset,
        },
      );
      return CommunityDiscussionPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussionPage> listMyDiscussions({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions/mine',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return CommunityDiscussionPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussion> getDiscussion(String discussionId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions/$discussionId',
      );
      return CommunityDiscussion.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussionSubmission> submitDiscussion({
    required String submissionKey,
    required String ticker,
    required String title,
    required String content,
    required String periodType,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions',
        data: <String, dynamic>{
          'submission_key': submissionKey,
          'ticker': ticker.trim().toUpperCase(),
          'title': title.trim(),
          'content': content.trim(),
          'period_type': periodType,
        },
      );
      return CommunityDiscussionSubmission.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityReportResult> reportDiscussion({
    required String discussionId,
    required String reasonCode,
    String details = '',
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/reports',
        data: <String, dynamic>{
          'reason_code': reasonCode,
          'details': details.trim(),
        },
      );
      return CommunityReportResult.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityMuteResult> muteUser(String userId) async {
    try {
      final response = await _apiClient.dio.put<Map<String, dynamic>>(
        '/community/users/$userId/mute',
      );
      return CommunityMuteResult.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityMuteResult> unmuteUser(String userId) async {
    try {
      final response = await _apiClient.dio.delete<Map<String, dynamic>>(
        '/community/users/$userId/mute',
      );
      return CommunityMuteResult.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityAppealSubmission> submitAppeal({
    required String discussionId,
    required String message,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/appeals',
        data: <String, dynamic>{'message': message.trim()},
      );
      return CommunityAppealSubmission.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityAppealPage> listMyAppeals({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/appeals/mine',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return CommunityAppealPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _requiredData(Map<String, dynamic>? data) {
    if (data == null) {
      throw const FormatException('Community response is empty.');
    }
    return data;
  }
}

final communityRepositoryProvider = Provider<CommunityRepository>((ref) {
  return CommunityRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\community\my_discussions_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'community_feed_tab.dart';
import 'community_models.dart';
import 'community_providers.dart';
import 'prediction_models.dart';
import 'prediction_providers.dart';
import 'prediction_verification_card.dart';

class MyDiscussionsScreen extends ConsumerWidget {
  const MyDiscussionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مناقشاتي'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'المناقشات'),
              Tab(text: 'الاستئنافات'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [_MyDiscussionList(), _MyAppealList()],
        ),
      ),
    );
  }
}

class _MyDiscussionList extends ConsumerWidget {
  const _MyDiscussionList();

  Future<void> _refresh(WidgetRef ref) async {
    ref.invalidate(myDiscussionsProvider);
    ref.invalidate(myPredictionStatsProvider);
    await Future.wait([
      ref.read(myDiscussionsProvider.future),
      ref.read(myPredictionStatsProvider.future),
    ]);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final discussions = ref.watch(myDiscussionsProvider);
    return RefreshIndicator(
      onRefresh: () => _refresh(ref),
      child: discussions.when(
        loading: () => const _LoadingList(),
        error: (error, stackTrace) => _ErrorList(
          message: 'تعذر تحميل مناقشاتك.',
          onRetry: () => ref.invalidate(myDiscussionsProvider),
        ),
        data: (page) {
          if (page.items.isEmpty) {
            return ListView(
              padding: const EdgeInsets.all(16),
              children: const [
                _PredictionStatsSection(),
                SizedBox(height: 60),
                Icon(Icons.forum_outlined, size: 52),
                SizedBox(height: 14),
                Text(
                  'لم ترسل أي مناقشة حتى الآن.',
                  textAlign: TextAlign.center,
                ),
              ],
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const _PredictionStatsSection(),
              const SizedBox(height: 14),
              for (final discussion in page.items) ...[
                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    CommunityDiscussionCard(
                      discussion: discussion,
                      showStatus: true,
                    ),
                    if (discussion.status == 'rejected' &&
                        discussion.rejectionCode != null)
                      Padding(
                        padding: const EdgeInsetsDirectional.only(
                          start: 16,
                          end: 16,
                          top: 6,
                        ),
                        child: Text(
                          'سبب الرفض: ${discussion.rejectionCode}',
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                    if (discussion.status == 'published') ...[
                      const SizedBox(height: 8),
                      PredictionVerificationCard(discussionId: discussion.id),
                    ],
                  ],
                ),
                const SizedBox(height: 12),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _PredictionStatsSection extends ConsumerWidget {
  const _PredictionStatsSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stats = ref.watch(myPredictionStatsProvider);
    return stats.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(18),
          child: LinearProgressIndicator(),
        ),
      ),
      error: (error, stackTrace) => Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              const Expanded(child: Text('تعذر تحميل إحصاءات التوقعات.')),
              TextButton(
                onPressed: () => ref.invalidate(myPredictionStatsProvider),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
      data: (value) => _PredictionStatsCard(stats: value),
    );
  }
}

class _PredictionStatsCard extends StatelessWidget {
  const _PredictionStatsCard({required this.stats});

  final PredictionStats stats;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'أداء توقعاتي',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text('تم التحقق: ${stats.verifiedPredictions}')),
                Chip(
                  label: Text(
                    'نسبة القبول: ${stats.accuracyPercent.toStringAsFixed(1)}%',
                  ),
                ),
                Chip(
                  label: Text(
                    'متوسط الدرجة: '
                    '${stats.averageScorePercent.toStringAsFixed(1)}%',
                  ),
                ),
                Chip(
                  label: Text(
                    'إجمالي المكافآت: ${stats.totalRewardCoins} عملة',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MyAppealList extends ConsumerWidget {
  const _MyAppealList();

  Future<void> _refresh(WidgetRef ref) async {
    ref.invalidate(myAppealsProvider);
    await ref.read(myAppealsProvider.future);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appeals = ref.watch(myAppealsProvider);
    return RefreshIndicator(
      onRefresh: () => _refresh(ref),
      child: appeals.when(
        loading: () => const _LoadingList(),
        error: (error, stackTrace) => _ErrorList(
          message: 'تعذر تحميل الاستئنافات.',
          onRetry: () => ref.invalidate(myAppealsProvider),
        ),
        data: (page) {
          if (page.items.isEmpty) {
            return const _EmptyList(
              icon: Icons.gavel_outlined,
              message: 'لا توجد استئنافات مسجلة.',
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: page.items.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) =>
                _AppealCard(appeal: page.items[index]),
          );
        },
      ),
    );
  }
}

class _AppealCard extends StatelessWidget {
  const _AppealCard({required this.appeal});

  final CommunityAppeal appeal;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'استئناف مناقشة',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Chip(label: Text(appeal.statusLabel)),
              ],
            ),
            const SizedBox(height: 8),
            Text('الحالة الأصلية: ${_sourceStatusLabel(appeal.sourceStatus)}'),
            const SizedBox(height: 10),
            Text(appeal.message),
            if (appeal.resolutionReasonCode != null) ...[
              const SizedBox(height: 10),
              Text('سبب القرار: ${appeal.resolutionReasonCode}'),
            ],
            if (appeal.resolutionDetails.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                appeal.resolutionDetails.toString(),
                textDirection: TextDirection.ltr,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _LoadingList extends StatelessWidget {
  const _LoadingList();

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: const [
        SizedBox(height: 220),
        Center(child: CircularProgressIndicator()),
      ],
    );
  }
}

class _EmptyList extends StatelessWidget {
  const _EmptyList({required this.icon, required this.message});

  final IconData icon;
  final String message;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SizedBox(height: 100),
        Icon(icon, size: 52),
        const SizedBox(height: 14),
        Text(message, textAlign: TextAlign.center),
      ],
    );
  }
}

class _ErrorList extends StatelessWidget {
  const _ErrorList({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SizedBox(height: 80),
        Text(message, textAlign: TextAlign.center),
        const SizedBox(height: 14),
        Center(
          child: OutlinedButton(
            onPressed: onRetry,
            child: const Text('إعادة المحاولة'),
          ),
        ),
      ],
    );
  }
}

String _sourceStatusLabel(String status) {
  return switch (status) {
    'rejected' => 'مرفوضة',
    'hidden' => 'مخفية',
    _ => status,
  };
}

```

---

### File: `lib\features\community\prediction_models.dart`

```dart
class PredictionVerification {
  const PredictionVerification({
    required this.id,
    required this.discussionId,
    required this.scoreBp,
    required this.scorePercent,
    required this.strength,
    required this.rewardPoints,
    required this.rewardCoins,
    required this.evidence,
    required this.verifiedAt,
  });

  final String id;
  final String discussionId;
  final int scoreBp;
  final double scorePercent;
  final String strength;
  final int rewardPoints;
  final String rewardCoins;
  final Map<String, dynamic> evidence;
  final DateTime verifiedAt;

  String get strengthLabel => switch (strength) {
    'rejected' => 'غير مقبولة',
    'weak' => 'ضعيفة',
    'strong' => 'قوية',
    'very_strong' => 'قوية جدًا',
    _ => strength,
  };

  String get explanation {
    final value = evidence['explanation'];
    if (value is Map) {
      final reason = value['reason'];
      if (reason is String && reason.trim().isNotEmpty) {
        return reason.trim();
      }
    }
    return 'تم حساب النتيجة من بيانات السوق والقواعد الثابتة.';
  }

  factory PredictionVerification.fromJson(Map<String, dynamic> json) {
    return PredictionVerification(
      id: _requiredString(json, 'id'),
      discussionId: _requiredString(json, 'discussion_id'),
      scoreBp: _requiredInt(json, 'score_bp'),
      scorePercent: _requiredDouble(json, 'score_percent'),
      strength: _requiredString(json, 'strength'),
      rewardPoints: _requiredInt(json, 'reward_points'),
      rewardCoins: _requiredString(json, 'reward_coins'),
      evidence: _requiredMap(json['evidence']),
      verifiedAt: _requiredDate(json, 'verified_at'),
    );
  }
}

class PredictionVerificationStatus {
  const PredictionVerificationStatus({
    required this.discussionId,
    required this.state,
    required this.eligibleAt,
    required this.verification,
  });

  final String discussionId;
  final String state;
  final DateTime? eligibleAt;
  final PredictionVerification? verification;

  bool get isEligible => state == 'eligible';
  bool get isWaiting => state == 'waiting';
  bool get isVerified => state == 'verified' && verification != null;

  factory PredictionVerificationStatus.fromJson(Map<String, dynamic> json) {
    final verificationJson = json['verification'];
    return PredictionVerificationStatus(
      discussionId: _requiredString(json, 'discussion_id'),
      state: _requiredString(json, 'state'),
      eligibleAt: _optionalDate(json['eligible_at']),
      verification: verificationJson == null
          ? null
          : PredictionVerification.fromJson(_requiredMap(verificationJson)),
    );
  }
}

class PredictionVerificationSubmission {
  const PredictionVerificationSubmission({
    required this.verification,
    required this.balancePoints,
    required this.balanceCoins,
    required this.idempotent,
  });

  final PredictionVerification verification;
  final int balancePoints;
  final String balanceCoins;
  final bool idempotent;

  factory PredictionVerificationSubmission.fromJson(Map<String, dynamic> json) {
    return PredictionVerificationSubmission(
      verification: PredictionVerification.fromJson(
        _requiredMap(json['verification']),
      ),
      balancePoints: _requiredInt(json, 'balance_points'),
      balanceCoins: _requiredString(json, 'balance_coins'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class PredictionStats {
  const PredictionStats({
    required this.verifiedPredictions,
    required this.acceptedPredictions,
    required this.accuracyPercent,
    required this.averageScorePercent,
    required this.totalRewardPoints,
    required this.totalRewardCoins,
  });

  final int verifiedPredictions;
  final int acceptedPredictions;
  final double accuracyPercent;
  final double averageScorePercent;
  final int totalRewardPoints;
  final String totalRewardCoins;

  factory PredictionStats.fromJson(Map<String, dynamic> json) {
    return PredictionStats(
      verifiedPredictions: _requiredInt(json, 'verified_predictions'),
      acceptedPredictions: _requiredInt(json, 'accepted_predictions'),
      accuracyPercent: _requiredDouble(json, 'accuracy_percent'),
      averageScorePercent: _requiredDouble(json, 'average_score_percent'),
      totalRewardPoints: _requiredInt(json, 'total_reward_points'),
      totalRewardCoins: _requiredString(json, 'total_reward_coins'),
    );
  }
}

Map<String, dynamic> _requiredMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  throw const FormatException('Expected a JSON object.');
}

String _requiredString(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

int _requiredInt(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is int) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

double _requiredDouble(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is num) {
    return value.toDouble();
  }
  throw FormatException('Missing or invalid $key.');
}

bool _requiredBool(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is bool) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

DateTime _requiredDate(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is String) {
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return parsed;
    }
  }
  throw FormatException('Missing or invalid $key.');
}

DateTime? _optionalDate(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is String) {
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return parsed;
    }
  }
  throw const FormatException('Invalid optional date.');
}

```

---

### File: `lib\features\community\prediction_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'prediction_models.dart';
import 'prediction_repository.dart';

final predictionVerificationStatusProvider = FutureProvider.autoDispose
    .family<PredictionVerificationStatus, String>((ref, discussionId) {
      return ref
          .watch(predictionRepositoryProvider)
          .getVerificationStatus(discussionId);
    });

final myPredictionStatsProvider = FutureProvider.autoDispose<PredictionStats>((
  ref,
) {
  return ref.watch(predictionRepositoryProvider).getMyStats();
});

```

---

### File: `lib\features\community\prediction_repository.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'prediction_models.dart';

class PredictionRepository {
  const PredictionRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<PredictionVerificationStatus> getVerificationStatus(
    String discussionId,
  ) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions/$discussionId/verification',
      );
      return PredictionVerificationStatus.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PredictionVerificationSubmission> verifyPrediction(
    String discussionId,
  ) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/verification',
      );
      return PredictionVerificationSubmission.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PredictionStats> getMyStats() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/predictions/stats/mine',
      );
      return PredictionStats.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _requiredData(Map<String, dynamic>? data) {
    if (data == null) {
      throw const FormatException('Prediction response is empty.');
    }
    return data;
  }
}

final predictionRepositoryProvider = Provider<PredictionRepository>((ref) {
  return PredictionRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\community\prediction_verification_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'community_providers.dart';
import 'prediction_models.dart';
import 'prediction_providers.dart';
import 'prediction_repository.dart';

class PredictionVerificationCard extends ConsumerStatefulWidget {
  const PredictionVerificationCard({required this.discussionId, super.key});

  final String discussionId;

  @override
  ConsumerState<PredictionVerificationCard> createState() =>
      _PredictionVerificationCardState();
}

class _PredictionVerificationCardState
    extends ConsumerState<PredictionVerificationCard> {
  bool _verifying = false;

  Future<void> _verify() async {
    if (_verifying) {
      return;
    }
    setState(() => _verifying = true);
    try {
      final result = await ref
          .read(predictionRepositoryProvider)
          .verifyPrediction(widget.discussionId);
      ref.invalidate(predictionVerificationStatusProvider(widget.discussionId));
      ref.invalidate(myPredictionStatsProvider);
      ref.invalidate(myDiscussionsProvider);
      ref.invalidate(walletSummaryProvider);
      await ref.read(sessionControllerProvider.notifier).refreshProfile();
      if (!mounted) {
        return;
      }
      final reward = result.verification.rewardCoins;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            result.verification.rewardPoints > 0
                ? 'تم تقييم التوقع وإضافة $reward عملة إلى رصيدك.'
                : 'تم تقييم التوقع. لا توجد مكافأة لهذه النتيجة.',
          ),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    } finally {
      if (mounted) {
        setState(() => _verifying = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(
      predictionVerificationStatusProvider(widget.discussionId),
    );
    return status.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(18),
          child: Row(
            children: [
              SizedBox.square(
                dimension: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              SizedBox(width: 12),
              Expanded(child: Text('جاري التحقق من موعد تقييم التوقع...')),
            ],
          ),
        ),
      ),
      error: (error, stackTrace) => Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              const Expanded(child: Text('تعذر تحميل حالة تقييم التوقع.')),
              TextButton(
                onPressed: () => ref.invalidate(
                  predictionVerificationStatusProvider(widget.discussionId),
                ),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
      data: (value) => switch (value.state) {
        'waiting' => _WaitingCard(status: value),
        'eligible' => _EligibleCard(verifying: _verifying, onVerify: _verify),
        'verified' when value.verification != null => _VerificationResultCard(
          verification: value.verification!,
        ),
        _ => const SizedBox.shrink(),
      },
    );
  }
}

class _WaitingCard extends StatelessWidget {
  const _WaitingCard({required this.status});

  final PredictionVerificationStatus status;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.schedule_outlined,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'التوقع لم يصبح جاهزًا للتحقق بعد',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  if (status.eligibleAt != null) ...[
                    const SizedBox(height: 6),
                    Text(
                      'موعد التحقق المتوقع: ${_formatDate(status.eligibleAt!)}',
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EligibleCard extends StatelessWidget {
  const _EligibleCard({required this.verifying, required this.onVerify});

  final bool verifying;
  final VoidCallback onVerify;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.fact_check_outlined,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'انتهت فترة التوقع وأصبحت بياناته جاهزة للمقارنة.',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: verifying ? null : onVerify,
              icon: verifying
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.verified_outlined),
              label: const Text('تحقق من صحة توقعي'),
            ),
          ],
        ),
      ),
    );
  }
}

class _VerificationResultCard extends StatelessWidget {
  const _VerificationResultCard({required this.verification});

  final PredictionVerification verification;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.verified_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'نتيجة تقييم التوقع',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Chip(label: Text(verification.strengthLabel)),
              ],
            ),
            const SizedBox(height: 14),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _MetricChip(
                  label: 'الدرجة',
                  value: '${verification.scorePercent.toStringAsFixed(2)}%',
                ),
                _MetricChip(
                  label: 'المكافأة',
                  value: '${verification.rewardCoins} عملة',
                ),
              ],
            ),
            const SizedBox(height: 14),
            Text(verification.explanation),
            const SizedBox(height: 8),
            Text(
              'تم التقييم في ${_formatDate(verification.verifiedAt)}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Chip(label: Text('$label: $value'));
  }
}

String _formatDate(DateTime value) {
  final local = value.toLocal();
  String two(int number) => number.toString().padLeft(2, '0');
  return '${two(local.day)}/${two(local.month)}/${local.year} '
      '${two(local.hour)}:${two(local.minute)}';
}

```

---

### File: `lib\features\home\dashboard_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/avatar_assets.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../community/community_feed_tab.dart';
import '../market/stock_analysis_tab.dart';
import '../market/stocks_screen.dart';
import '../notifications/notification_providers.dart';
import '../reports/reports_screen.dart';
import '../wallet/wallet_providers.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _selectedIndex = 0;

  static const _navItems = <(String, IconData, String)>[
    ('stocks', Icons.home_rounded, 'الرئيسية'),
    ('reports', Icons.assessment_outlined, 'التقارير'),
    ('analyze', Icons.query_stats_outlined, 'تحليل سهم'),
    ('community', Icons.forum_outlined, 'المجتمع'),
    ('wallet', Icons.account_balance_wallet_outlined, 'المحفظة'),
    ('profile', Icons.person_outline_rounded, 'حسابي'),
  ];

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(sessionControllerProvider).profile;

    return Scaffold(
      appBar: AppBar(
        title: Text(_navItems[_selectedIndex].$3),
        actions: [
          if (profile?.isAdmin == true)
            IconButton(
              onPressed: () => context.push('/admin'),
              icon: const Icon(Icons.admin_panel_settings_outlined),
              tooltip: 'الإدارة',
            ),
          IconButton(
            onPressed: () => context.push('/performance'),
            icon: const Icon(Icons.assessment_outlined),
            tooltip: 'سجل الأداء',
          ),
          IconButton(
            onPressed: () => context.push('/notifications'),
            icon: Badge(
              isLabelVisible:
                  ref
                      .watch(notificationInboxProvider)
                      .valueOrNull
                      ?.unreadCount !=
                  0,
              label: Text(
                '${ref.watch(notificationInboxProvider).valueOrNull?.unreadCount ?? 0}',
              ),
              child: const Icon(Icons.notifications_outlined),
            ),
            tooltip: 'الإشعارات',
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            _DrawerHeader(profile: profile),
            const Divider(),
            for (var item in _navItems)
              ListTile(
                leading: Icon(item.$2),
                title: Text(item.$3),
                selected: _selectedIndex == _navItems.indexOf(item),
                onTap: () {
                  setState(() => _selectedIndex = _navItems.indexOf(item));
                  Navigator.pop(context);
                },
              ),
            if (profile?.isAdmin == true) ...[
              const Divider(),
              ListTile(
                leading: const Icon(Icons.admin_panel_settings_outlined),
                title: const Text('لوحة الإدارة'),
                onTap: () {
                  context.push('/admin');
                  Navigator.pop(context);
                },
              ),
            ],
          ],
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return const StocksScreen();
      case 1:
        return const ReportsScreen();
      case 2:
        return const StockAnalysisTab();
      case 3:
        return const CommunityFeedTab();
      case 4:
        return const WalletTab();
      case 5:
        return const ProfileTab();
      default:
        return const StocksScreen();
    }
  }
}

class _DrawerHeader extends StatelessWidget {
  const _DrawerHeader({required this.profile});
  final UserProfile? profile;

  @override
  Widget build(BuildContext context) {
    return UserAccountsDrawerHeader(
      currentAccountPicture: CircleAvatar(
        backgroundImage: AssetImage(
          avatarAssetPath(profile?.avatarKey ?? avatarKeys.first),
        ),
      ),
      accountName: Text(profile?.displayName ?? 'مستخدم'),
      accountEmail: Text(profile?.email ?? ''),
    );
  }
}

class WalletTab extends ConsumerWidget {
  const WalletTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wallet = ref.watch(walletSummaryProvider);
    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(walletSummaryProvider),
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(22),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'الرصيد الحالي',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  wallet.when(
                    loading: () =>
                        const Center(child: CircularProgressIndicator()),
                    error: (error, stackTrace) => Text('تعذر تحميل المحفظة.'),
                    data: (summary) => Text(
                      '${summary.balanceCoins} عملة',
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.w900,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  wallet.when(
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                    data: (summary) => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('الخطة: ${summary.planCode}'),
                        Text('التوزيع الأسبوعي: ${summary.weeklyCoins} عملة'),
                        Text(
                          summary.adsEnabled
                              ? 'الإعلانات مفعلة'
                              : 'الخطة بدون إعلانات',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  OutlinedButton.icon(
                    onPressed: () => context.push('/wallet/history'),
                    icon: const Icon(Icons.receipt_long_outlined),
                    label: const Text('عرض سجل العمليات'),
                  ),
                  const SizedBox(height: 10),
                  FilledButton.icon(
                    onPressed: () => context.push('/monetization'),
                    icon: const Icon(Icons.workspace_premium_outlined),
                    label: const Text('الخطط وشراء العملات'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ProfileTab extends ConsumerWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(sessionControllerProvider).profile;
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 48,
                  backgroundImage: AssetImage(
                    avatarAssetPath(profile?.avatarKey ?? avatarKeys.first),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  profile?.displayName ?? '',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                Text(
                  profile?.email ?? '',
                  textDirection: TextDirection.ltr,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 8),
                Text('الخطة: ${profile?.planCode ?? '-'}'),
                Text('الرصيد: ${profile?.balanceCoins ?? '0'} عملة'),
                const SizedBox(height: 20),
                FilledButton.icon(
                  onPressed: () => context.push('/profile/edit'),
                  icon: const Icon(Icons.edit_outlined),
                  label: const Text('تعديل الاسم والصورة'),
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed: () =>
                      ref.read(sessionControllerProvider.notifier).logout(),
                  icon: const Icon(Icons.logout_rounded),
                  label: const Text('تسجيل الخروج'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

```

---

### File: `lib\features\labs\labs_models.dart`

```dart
class LabsBacktestParams {
  const LabsBacktestParams({
    required this.startDate,
    required this.endDate,
    required this.rank,
    required this.exitMode,
    required this.trackIntervalMinutes,
    required this.sourceInterval,
  });

  final DateTime startDate;
  final DateTime endDate;
  final int? rank;
  final String exitMode;
  final int trackIntervalMinutes;
  final String sourceInterval;

  factory LabsBacktestParams.fromJson(Map<String, dynamic> json) {
    return LabsBacktestParams(
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      rank: json['rank'] as int?,
      exitMode: json['exit_mode'] as String,
      trackIntervalMinutes: json['track_interval_minutes'] as int? ?? 10,
      sourceInterval: json['source_interval'] as String? ?? '5m',
    );
  }
}

class LabsBacktestSummary {
  const LabsBacktestSummary({
    required this.reportsScanned,
    required this.trades,
    required this.hits,
    required this.misses,
    required this.skipped,
    required this.hitRatePct,
    required this.avgReturnPct,
    required this.medianReturnPct,
    required this.avgHitReturnPct,
    required this.avgMissReturnPct,
    required this.medianMinutesToHit,
    required this.bestReturnPct,
    required this.worstReturnPct,
    required this.cumulativeReturnPct,
  });

  final int reportsScanned;
  final int trades;
  final int hits;
  final int misses;
  final int skipped;
  final double hitRatePct;
  final double avgReturnPct;
  final double? medianReturnPct;
  final double avgHitReturnPct;
  final double avgMissReturnPct;
  final double? medianMinutesToHit;
  final double bestReturnPct;
  final double worstReturnPct;
  final double cumulativeReturnPct;

  factory LabsBacktestSummary.fromJson(Map<String, dynamic> json) {
    return LabsBacktestSummary(
      reportsScanned: json['reports_scanned'] as int? ?? 0,
      trades: json['trades'] as int? ?? 0,
      hits: json['hits'] as int? ?? 0,
      misses: json['misses'] as int? ?? 0,
      skipped: json['skipped'] as int? ?? 0,
      hitRatePct: (json['hit_rate_pct'] as num?)?.toDouble() ?? 0,
      avgReturnPct: (json['avg_return_pct'] as num?)?.toDouble() ?? 0,
      medianReturnPct: _doubleOrNull(json['median_return_pct']),
      avgHitReturnPct: (json['avg_hit_return_pct'] as num?)?.toDouble() ?? 0,
      avgMissReturnPct: (json['avg_miss_return_pct'] as num?)?.toDouble() ?? 0,
      medianMinutesToHit: _doubleOrNull(json['median_minutes_to_hit']),
      bestReturnPct: (json['best_return_pct'] as num?)?.toDouble() ?? 0,
      worstReturnPct: (json['worst_return_pct'] as num?)?.toDouble() ?? 0,
      cumulativeReturnPct:
          (json['cumulative_return_pct'] as num?)?.toDouble() ?? 0,
    );
  }
}

class LabsTrackedPoint {
  const LabsTrackedPoint({
    required this.time,
    required this.price,
    required this.high,
    required this.low,
  });

  final String time;
  final double price;
  final double high;
  final double low;

  factory LabsTrackedPoint.fromJson(Map<String, dynamic> json) {
    return LabsTrackedPoint(
      time: json['time'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0,
      high: (json['high'] as num?)?.toDouble() ?? 0,
      low: (json['low'] as num?)?.toDouble() ?? 0,
    );
  }
}

class LabsBacktestSession {
  const LabsBacktestSession({
    required this.targetSessionDate,
    required this.reportId,
    required this.rank,
    required this.ticker,
    required this.score,
    required this.priceAtAnalysis,
    required this.targets,
    required this.stopLoss,
    required this.sessionOpen,
    required this.exitPrice,
    required this.exitReason,
    required this.hit,
    required this.minutesToExit,
    required this.returnPct,
    required this.tracked,
  });

  final DateTime targetSessionDate;
  final String reportId;
  final int rank;
  final String ticker;
  final double score;
  final double? priceAtAnalysis;
  final List<double> targets;
  final double? stopLoss;
  final double? sessionOpen;
  final double? exitPrice;
  final String exitReason;
  final bool hit;
  final int? minutesToExit;
  final double? returnPct;
  final List<LabsTrackedPoint> tracked;

  factory LabsBacktestSession.fromJson(Map<String, dynamic> json) {
    return LabsBacktestSession(
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      reportId: json['report_id'] as String,
      rank: json['rank'] as int? ?? 0,
      ticker: json['ticker'] as String? ?? '',
      score: (json['score'] as num?)?.toDouble() ?? 0,
      priceAtAnalysis: _doubleOrNull(json['price_at_analysis']),
      targets: _doubleList(json['targets']),
      stopLoss: _doubleOrNull(json['stop_loss']),
      sessionOpen: _doubleOrNull(json['session_open']),
      exitPrice: _doubleOrNull(json['exit_price']),
      exitReason: json['exit_reason'] as String? ?? 'skipped',
      hit: json['hit'] as bool? ?? false,
      minutesToExit: json['minutes_to_exit'] as int?,
      returnPct: _doubleOrNull(json['return_pct']),
      tracked: _mapList(
        json['tracked'],
      ).map(LabsTrackedPoint.fromJson).toList(growable: false),
    );
  }
}

class LabsBacktestResult {
  const LabsBacktestResult({
    required this.params,
    required this.summary,
    required this.sessions,
    required this.meta,
  });

  final LabsBacktestParams params;
  final LabsBacktestSummary summary;
  final List<LabsBacktestSession> sessions;
  final Map<String, dynamic> meta;

  factory LabsBacktestResult.fromJson(Map<String, dynamic> json) {
    return LabsBacktestResult(
      params: LabsBacktestParams.fromJson(_map(json['params'])),
      summary: LabsBacktestSummary.fromJson(_map(json['summary'])),
      sessions: _mapList(
        json['sessions'],
      ).map(LabsBacktestSession.fromJson).toList(growable: false),
      meta: _map(json['meta']),
    );
  }
}

class LabsBacktestQuery {
  const LabsBacktestQuery({
    required this.startDate,
    required this.endDate,
    required this.rank,
    required this.exitMode,
  });

  final DateTime startDate;
  final DateTime endDate;
  final int? rank;
  final String exitMode;

  @override
  bool operator ==(Object other) {
    return other is LabsBacktestQuery &&
        other.startDate == startDate &&
        other.endDate == endDate &&
        other.rank == rank &&
        other.exitMode == exitMode;
  }

  @override
  int get hashCode => Object.hash(startDate, endDate, rank, exitMode);
}

class LabsBacktestJob {
  const LabsBacktestJob({
    required this.id,
    required this.status,
    required this.startDate,
    required this.endDate,
    required this.rank,
    required this.exitMode,
    required this.createdAt,
    this.params,
    this.summary,
    this.sessions = const <LabsBacktestSession>[],
    this.errorMessage,
    this.startedAt,
    this.completedAt,
  });

  factory LabsBacktestJob.fromJson(Map<String, dynamic> json) {
    final rawParams = json['params'];
    final rawSummary = json['summary'];
    final rawSessions = json['sessions'];
    return LabsBacktestJob(
      id: json['id'] as String? ?? '',
      status: json['status'] as String? ?? 'queued',
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      rank: json['rank'] as int?,
      exitMode: json['exit_mode'] as String? ?? 'target_2',
      params: rawParams is Map
          ? LabsBacktestParams.fromJson(_map(rawParams))
          : null,
      summary: rawSummary is Map
          ? LabsBacktestSummary.fromJson(_map(rawSummary))
          : null,
      sessions: rawSessions is List
          ? rawSessions
                .whereType<Map<String, dynamic>>()
                .map(LabsBacktestSession.fromJson)
                .toList(growable: false)
          : const <LabsBacktestSession>[],
      errorMessage: json['error_message'] as String?,
      startedAt: _optionalDateTime(json['started_at']),
      completedAt: _optionalDateTime(json['completed_at']),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  final String id;
  final String status;
  final DateTime startDate;
  final DateTime endDate;
  final int? rank;
  final String exitMode;
  final LabsBacktestParams? params;
  final LabsBacktestSummary? summary;
  final List<LabsBacktestSession> sessions;
  final String? errorMessage;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final DateTime createdAt;

  bool get isActive => status == 'queued' || status == 'running';
}

DateTime? _optionalDateTime(Object? value) {
  if (value is! String || value.isEmpty) return null;
  return DateTime.tryParse(value);
}

double? _doubleOrNull(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return null;
}

List<double> _doubleList(Object? value) {
  if (value is List) {
    return value
        .whereType<num>()
        .map((item) => item.toDouble())
        .toList(growable: false);
  }
  return const <double>[];
}

List<Map<String, dynamic>> _mapList(Object? value) {
  if (value is List) {
    return value
        .map((item) => _map(item))
        .where((item) => item.isNotEmpty)
        .toList(growable: false);
  }
  return const <Map<String, dynamic>>[];
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

```

---

### File: `lib\features\labs\labs_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'labs_models.dart';
import 'labs_repository.dart';

final labsBacktestJobsProvider = FutureProvider<List<LabsBacktestJob>>((ref) {
  return ref.watch(labsRepositoryProvider).backtestJobs();
});

final labsBacktestJobProvider = FutureProvider.autoDispose
    .family<LabsBacktestJob, String>(
      (ref, jobId) => ref.watch(labsRepositoryProvider).backtestJob(jobId),
    );

```

---

### File: `lib\features\labs\labs_repository.dart`

```dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'labs_models.dart';

class LabsRepository {
  const LabsRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<LabsBacktestJob> createBacktestJob(LabsBacktestQuery query) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/labs/backtest-jobs',
        data: <String, dynamic>{
          'start_date': _formatDate(query.startDate),
          'end_date': _formatDate(query.endDate),
          if (query.rank != null) 'rank': query.rank,
          'exit_mode': query.exitMode,
        },
        options: Options(receiveTimeout: const Duration(seconds: 30)),
      );
      return LabsBacktestJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<LabsBacktestJob> backtestJob(String jobId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/labs/backtest-jobs/$jobId',
      );
      return LabsBacktestJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> deleteBacktestJob(String jobId) async {
    try {
      await _apiClient.dio.delete<void>('/labs/backtest-jobs/$jobId');
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<LabsBacktestJob>> backtestJobs({int limit = 50}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/labs/backtest-jobs',
        queryParameters: <String, dynamic>{'limit': limit},
      );
      final rawItems = _required(response.data)['items'];
      if (rawItems is! List) {
        return const <LabsBacktestJob>[];
      }
      return rawItems
          .whereType<Map<String, dynamic>>()
          .map(LabsBacktestJob.fromJson)
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  String _formatDate(DateTime value) {
    final month = value.month.toString().padLeft(2, '0');
    final day = value.day.toString().padLeft(2, '0');
    return '${value.year}-$month-$day';
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Labs response is empty.');
    }
    return value;
  }
}

final labsRepositoryProvider = Provider<LabsRepository>((ref) {
  return LabsRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\labs\labs_screen.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;

import '../../core/network/api_exception.dart';
import 'labs_models.dart';
import 'labs_providers.dart';
import 'labs_repository.dart';

class LabsScreen extends ConsumerStatefulWidget {
  const LabsScreen({super.key, this.embedded = false});

  final bool embedded;

  @override
  ConsumerState<LabsScreen> createState() => _LabsScreenState();
}

class _LabsScreenState extends ConsumerState<LabsScreen> {
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 21));
  DateTime _endDate = DateTime.now();
  int? _rank;
  String _exitMode = 'target_2';
  bool _submitting = false;
  String? _activeJobId;
  String? _error;
  List<LabsBacktestJob> _jobs = const [];
  bool _loadingJobs = true;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    unawaited(_load());
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final jobs = await ref.read(labsRepositoryProvider).backtestJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _loadingJobs = false;
        _error = null;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loadingJobs = false;
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  Future<void> _pickStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365 * 3)),
      lastDate: _endDate,
      helpText: 'اختر بداية النطاق',
    );
    if (picked != null) {
      setState(() => _startDate = picked);
    }
  }

  Future<void> _pickEndDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _endDate,
      firstDate: _startDate,
      lastDate: DateTime.now(),
      helpText: 'اختر نهاية النطاق',
    );
    if (picked != null) {
      setState(() => _endDate = picked);
    }
  }

  Future<void> _run() async {
    final query = LabsBacktestQuery(
      startDate: _startDate,
      endDate: _endDate,
      rank: _rank,
      exitMode: _exitMode,
    );
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final job = await ref
          .read(labsRepositoryProvider)
          .createBacktestJob(query);
      if (!mounted) return;
      setState(() {
        _activeJobId = job.id;
        _submitting = false;
      });
      _startPolling();
      await _load();
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  void _startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(
      const Duration(seconds: 6),
      (_) => unawaited(_poll()),
    );
  }

  Future<void> _poll() async {
    final jobId = _activeJobId;
    if (jobId == null) return;
    try {
      final job = await ref.read(labsRepositoryProvider).backtestJob(jobId);
      if (!mounted) return;
      if (job.status == 'complete' || job.status == 'failed') {
        _pollTimer?.cancel();
        setState(() => _activeJobId = null);
      }
      await _load();
    } on Object {
      // Transient polling failures are retried on the next tick.
    }
  }

  Future<void> _openJob(LabsBacktestJob job) async {
    setState(() {
      _activeJobId = job.id;
      _startDate = job.startDate;
      _endDate = job.endDate;
      _rank = job.rank;
      _exitMode = job.exitMode;
    });
    if (job.isActive) {
      _startPolling();
    }
    await _load();
  }

  Future<void> _deleteJob(LabsBacktestJob job) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف المحاكاة'),
        content: const Text(
          'سيتم حذف هذه المحاكاة نهائيًا من قاعدة البيانات. لا يمكن التراجع عن هذا الإجراء.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('حذف نهائي'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }
    try {
      await ref.read(labsRepositoryProvider).deleteBacktestJob(job.id);
      if (!mounted) {
        return;
      }
      if (_activeJobId == job.id) {
        _pollTimer?.cancel();
        setState(() => _activeJobId = null);
      }
      await _load();
    } on Object catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  String _formatDate(DateTime value) {
    try {
      return DateFormat('d MMMM yyyy', 'ar').format(value.toLocal());
    } on Object {
      return '${value.day}/${value.month}/${value.year}';
    }
  }

  Widget _body() {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const _LabsNotice(),
          const SizedBox(height: 14),
          _buildControls(context),
          const SizedBox(height: 16),
          if (_error != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: const Text('تعذر تشغيل المحاكاة'),
                subtitle: Text(_error!),
              ),
            ),
          if (_submitting)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(
                  child: Text('جارٍ إرسال المحاكاة إلى Worker الاختبارات...'),
                ),
              ),
            ),
          if (_activeJobId != null) _buildActiveJob(context),
          const SizedBox(height: 8),
          Text(
            'محاولاتي',
            style: Theme.of(
              context,
            ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          if (_loadingJobs) const Center(child: CircularProgressIndicator()),
          if (!_loadingJobs && _jobs.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('لم تشغّل أي محاكاة بعد.')),
              ),
            ),
          for (final job in _jobs)
            _JobCard(
              job: job,
              dateFormat: DateFormat('d MMM yyyy', 'ar'),
              active: _activeJobId == job.id,
              onOpen: () => _openJob(job),
              onDelete: () => _deleteJob(job),
            ),
        ],
      ),
    );
  }

  Widget _buildActiveJob(BuildContext context) {
    final jobId = _activeJobId!;
    return FutureBuilder<LabsBacktestJob>(
      future: ref.read(labsBacktestJobProvider(jobId).future),
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          final error = snapshot.error;
          return Card(
            child: ListTile(
              leading: const Icon(Icons.error_outline),
              title: const Text('تعذر تحميل نتيجة المحاكاة'),
              subtitle: Text(error is ApiException ? error.message : '$error'),
            ),
          );
        }
        if (snapshot.hasData) {
          final job = snapshot.data!;
          if (job.status == 'complete' && job.summary != null) {
            return _LabsResults(job: job);
          }
          if (job.status == 'failed') {
            return Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    const Icon(Icons.error_outline, size: 32),
                    const SizedBox(height: 10),
                    Text(
                      job.errorMessage ?? 'فشلت المحاكاة.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          }
        }
        return const Card(
          child: Padding(
            padding: EdgeInsets.all(32),
            child: Column(
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 14),
                Text(
                  'المحاكاة تعمل الآن على Worker الاختبارات... سيظهر الملخص هنا تلقائيًا.',
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final body = _body();
    if (widget.embedded) {
      return body;
    }
    return Scaffold(
      appBar: AppBar(title: const Text('المختببرات')),
      body: SafeArea(child: body),
    );
  }

  Widget _buildControls(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'محاكاة تقرير الـ10 اليومي',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submitting ? null : _pickStartDate,
                    icon: const Icon(Icons.event_outlined),
                    label: Text('من: ${_formatDate(_startDate)}'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submitting ? null : _pickEndDate,
                    icon: const Icon(Icons.event_available_outlined),
                    label: Text('إلى: ${_formatDate(_endDate)}'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<int?>(
              initialValue: _rank,
              decoration: const InputDecoration(
                labelText: 'رتبة السهم في التقرير',
                border: OutlineInputBorder(),
              ),
              items: [
                const DropdownMenuItem<int?>(
                  value: null,
                  child: Text('كل الرتب (1-10)'),
                ),
                for (var rank = 1; rank <= 10; rank++)
                  DropdownMenuItem<int?>(
                    value: rank,
                    child: Text('الرتبة $rank'),
                  ),
              ],
              onChanged: _submitting
                  ? null
                  : (value) => setState(() => _rank = value),
            ),
            const SizedBox(height: 14),
            SegmentedButton<String>(
              showSelectedIcon: false,
              segments: const [
                ButtonSegment(value: 'target_2', label: Text('الهدف الثاني')),
                ButtonSegment(value: 'highest', label: Text('أعلى هدف')),
              ],
              selected: <String>{_exitMode},
              onSelectionChanged: _submitting
                  ? null
                  : (selection) {
                      setState(() => _exitMode = selection.single);
                    },
            ),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: _submitting ? null : _run,
              icon: _submitting
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.play_arrow_rounded),
              label: const Text('تشغيل المحاكاة على Worker الاختبارات'),
            ),
            const SizedBox(height: 8),
            const Text(
              'يمكنك الخروج من الصفحة. عند العودة ستجد النتيجة محفوظة في محاولاتك.',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class _LabsNotice extends StatelessWidget {
  const _LabsNotice();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.science_outlined),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                'محاكاة شراء أسهم تقرير الـ10 اليومي عند افتتاح الجلسة وبيعها عند تحقق الهدف المختار، مع تتبع الأسعار كل 10 دقائق خلال الجلسة. النطاق محدود بآخر 45 يومًا. المحاكاة تعمل على Worker الاختبارات المنفصل، فلا تؤثر على مستخدمي التطبيق.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _JobCard extends StatelessWidget {
  const _JobCard({
    required this.job,
    required this.dateFormat,
    required this.active,
    required this.onOpen,
    required this.onDelete,
  });

  final LabsBacktestJob job;
  final DateFormat dateFormat;
  final bool active;
  final VoidCallback onOpen;
  final VoidCallback onDelete;

  static const _statusLabels = <String, String>{
    'queued': 'في الانتظار',
    'running': 'جاري التشغيل',
    'complete': 'مكتمل',
    'failed': 'فشل',
  };

  @override
  Widget build(BuildContext context) {
    final statusLabel = _statusLabels[job.status] ?? job.status;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(switch (job.status) {
          'complete' => Icons.check_circle_outline,
          'failed' => Icons.error_outline,
          'running' => Icons.sync,
          _ => Icons.schedule,
        }),
        title: Text(
          '${dateFormat.format(job.startDate)} — '
          '${dateFormat.format(job.endDate)}'
          '${job.rank == null ? '' : ' • الرتبة ${job.rank}'}',
        ),
        subtitle: Text(
          active
              ? 'جاري عرض النتيجة...'
              : '$statusLabel • '
                    '${job.exitMode == 'highest' ? 'أعلى هدف' : 'الهدف الثاني'}',
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              tooltip: 'حذف نهائي',
              visualDensity: VisualDensity.compact,
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline_rounded),
              color: Theme.of(context).colorScheme.error,
            ),
            const Icon(Icons.chevron_left_rounded),
          ],
        ),
        onTap: onOpen,
      ),
    );
  }
}

class _LabsResults extends StatelessWidget {
  const _LabsResults({required this.job});

  final LabsBacktestJob job;

  @override
  Widget build(BuildContext context) {
    final summary = job.summary!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'ملخص المحاكاة',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 14),
                _SummaryRow(
                  label: 'نسبة تحقق الهدف',
                  value: '${summary.hitRatePct.toStringAsFixed(1)}%',
                  highlighted: true,
                ),
                const Divider(height: 20),
                _SummaryRow(
                  label: 'متوسط العائد عند النجاح',
                  value: _formatPercent(summary.avgHitReturnPct),
                ),
                _SummaryRow(
                  label: 'متوسط العائد عند الإخفاق',
                  value: _formatPercent(summary.avgMissReturnPct),
                ),
                _SummaryRow(
                  label: 'متوسط العائد الإجمالي',
                  value: _formatPercent(summary.avgReturnPct),
                ),
                _SummaryRow(
                  label: 'الوسيط الزمني لتحقيق الهدف',
                  value: summary.medianMinutesToHit == null
                      ? '-'
                      : '${summary.medianMinutesToHit!.round()} دقيقة',
                ),
                const Divider(height: 20),
                _SummaryRow(
                  label: 'الصفقات المكتملة',
                  value:
                      '${summary.trades} (نجاح ${summary.hits} / إخفاق ${summary.misses})',
                ),
                _SummaryRow(
                  label: 'جلسات تم فحصها',
                  value: '${summary.reportsScanned}',
                ),
                if (summary.skipped > 0)
                  _SummaryRow(
                    label: 'بدون بيانات',
                    value: '${summary.skipped}',
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'تفاصيل الصفقات',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 10),
        if (job.sessions.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Text(
                'لا توجد صفقات ضمن هذا النطاق.',
                textAlign: TextAlign.center,
              ),
            ),
          )
        else
          Column(
            children: job.sessions
                .map((trade) => _TradeCard(trade: trade))
                .toList(growable: false),
          ),
      ],
    );
  }

  String _formatPercent(double? value) {
    if (value == null) return '-';
    final prefix = value > 0 ? '+' : '';
    return '$prefix${value.toStringAsFixed(2)}%';
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({
    required this.label,
    required this.value,
    this.highlighted = false,
  });

  final String label;
  final String value;
  final bool highlighted;

  @override
  Widget build(BuildContext context) {
    final style = highlighted
        ? Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w900,
            color: Theme.of(context).colorScheme.primary,
          )
        : Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Text(value, textDirection: TextDirection.ltr, style: style),
        ],
      ),
    );
  }
}

class _TradeCard extends StatelessWidget {
  const _TradeCard({required this.trade});

  final LabsBacktestSession trade;

  static const _exitLabels = <String, String>{
    'target': 'تحقق الهدف',
    'stop': 'وقف الخسارة',
    'close': 'إغلاق الجلسة',
    'skipped': 'بدون بيانات',
  };

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final returnColor = (trade.returnPct ?? 0) >= 0
        ? Colors.green.shade700
        : Colors.red.shade700;
    final isHit = trade.hit;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ExpansionTile(
        shape: const Border(),
        collapsedShape: const Border(),
        leading: CircleAvatar(
          backgroundColor: isHit
              ? colorScheme.primaryContainer
              : colorScheme.surfaceContainerHighest,
          child: Icon(
            isHit ? Icons.check_rounded : Icons.close_rounded,
            color: isHit ? colorScheme.primary : colorScheme.outline,
          ),
        ),
        title: Row(
          children: [
            Text(
              trade.ticker,
              textDirection: TextDirection.ltr,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(width: 8),
            Chip(
              visualDensity: VisualDensity.compact,
              label: Text('الرتبة ${trade.rank}'),
            ),
          ],
        ),
        subtitle: Text(
          'جلسة ${_formatDate(trade.targetSessionDate)} • '
          '${_exitLabels[trade.exitReason] ?? trade.exitReason}'
          '${trade.minutesToExit != null ? ' • بعد ${trade.minutesToExit} دقيقة' : ''}',
        ),
        trailing: Text(
          trade.returnPct == null
              ? '-'
              : '${(trade.returnPct! > 0 ? '+' : '')}${trade.returnPct!.toStringAsFixed(2)}%',
          textDirection: TextDirection.ltr,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w900,
            color: returnColor,
          ),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _TradeDetailRow(
                  label: 'فتح الجلسة',
                  value: _formatPrice(trade.sessionOpen),
                ),
                _TradeDetailRow(
                  label: 'سعر الخروج',
                  value: _formatPrice(trade.exitPrice),
                ),
                if (trade.priceAtAnalysis != null)
                  _TradeDetailRow(
                    label: 'سعر التحليل',
                    value: _formatPrice(trade.priceAtAnalysis),
                  ),
                _TradeDetailRow(
                  label: 'الأهداف',
                  value: trade.targets.map(_formatPrice).join(' / '),
                ),
                if (trade.stopLoss != null)
                  _TradeDetailRow(
                    label: 'وقف الخسارة',
                    value: _formatPrice(trade.stopLoss),
                  ),
                const SizedBox(height: 8),
                Text(
                  'التتبع كل 10 دقائق',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 6),
                SizedBox(
                  height: 200,
                  child: trade.tracked.isEmpty
                      ? const Center(child: Text('لا توجد نقاط تتبع.'))
                      : _TrackedChart(points: trade.tracked),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime value) {
    try {
      return DateFormat('d MMM yyyy', 'ar').format(value.toLocal());
    } on Object {
      return '${value.day}/${value.month}/${value.year}';
    }
  }

  String _formatPrice(double? value) {
    return value == null ? '-' : value.toStringAsFixed(3);
  }
}

class _TradeDetailRow extends StatelessWidget {
  const _TradeDetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class _TrackedChart extends StatelessWidget {
  const _TrackedChart({required this.points});

  final List<LabsTrackedPoint> points;

  @override
  Widget build(BuildContext context) {
    final prices = points.map((point) => point.price).toList(growable: false);
    final minPrice = prices.reduce((a, b) => a < b ? a : b);
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);
    final range = (maxPrice - minPrice).abs() < 0.0001
        ? 1.0
        : (maxPrice - minPrice);

    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final height = constraints.maxHeight;
        final step = width / (points.length - 1).clamp(1, points.length);
        final line = <Offset>[];
        for (var index = 0; index < points.length; index++) {
          final dx = index * step;
          final dy =
              height -
              ((points[index].price - minPrice) / range) * (height - 20) -
              10;
          line.add(Offset(dx, dy.toDouble()));
        }
        return CustomPaint(
          size: Size(width, height),
          painter: _TrackedPainter(
            line: line,
            maxPrice: maxPrice,
            minPrice: minPrice,
            firstTime: points.first.time,
            lastTime: points.last.time,
            color: Theme.of(context).colorScheme.primary,
          ),
        );
      },
    );
  }
}

class _TrackedPainter extends CustomPainter {
  const _TrackedPainter({
    required this.line,
    required this.maxPrice,
    required this.minPrice,
    required this.firstTime,
    required this.lastTime,
    required this.color,
  });

  final List<Offset> line;
  final double maxPrice;
  final double minPrice;
  final String firstTime;
  final String lastTime;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = color.withValues(alpha: 0.12)
      ..strokeWidth = 1;
    for (var index = 1; index < 4; index++) {
      final dy = size.height * index / 4;
      canvas.drawLine(Offset(0, dy), Offset(size.width, dy), gridPaint);
    }
    final linePaint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    if (line.length >= 2) {
      final path = Path()..moveTo(line.first.dx, line.first.dy);
      for (final point in line.skip(1)) {
        path.lineTo(point.dx, point.dy);
      }
      canvas.drawPath(path, linePaint);
    } else if (line.isNotEmpty) {
      canvas.drawCircle(line.first, 3, Paint()..color = color);
    }
    final labelPaint = Paint()..color = color.withValues(alpha: 0.75);
    final textStyle = TextStyle(color: labelPaint.color, fontSize: 10);
    _drawText(canvas, '$minPrice', const Offset(4, 2), textStyle);
    _drawText(canvas, '$maxPrice', Offset(4, size.height - 16), textStyle);
    _drawText(canvas, firstTime, Offset(size.width - 30, 2), textStyle);
  }

  void _drawText(Canvas canvas, String text, Offset offset, TextStyle style) {
    final textPainter = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(_TrackedPainter oldDelegate) {
    return oldDelegate.line != line || oldDelegate.color != color;
  }
}

```

---

### File: `lib\features\market\market_quotes_providers.dart`

```dart
import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

const marketQuotesPollInterval = Duration(seconds: 5);

/// Live EGX market quotes, refreshed periodically while the home/stock
/// screens are visible using the backend-side cached scanner response.
final marketQuotesProvider = StreamProvider.autoDispose<MarketQuotesSnapshot>((
  ref,
) {
  final repository = ref.watch(backendRepositoryProvider);
  return Stream.periodic(
    marketQuotesPollInterval,
    (_) => (),
  ).asyncMap((_) => repository.getMarketQuotes());
});

/// Single stock quote used by the stock detail screen. Falls back to a
/// one-shot fetch and re-runs when the reference ticker changes.
class StockQuoteNotifier
    extends AutoDisposeFamilyAsyncNotifier<MarketQuote, String> {
  @override
  Future<MarketQuote> build(String arg) {
    return ref.watch(backendRepositoryProvider).getMarketQuote(arg);
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
      () => ref
          .watch(backendRepositoryProvider)
          .getMarketQuote(arg, forceRefresh: true),
    );
  }
}

final stockQuoteProvider =
    AutoDisposeAsyncNotifierProviderFamily<
      StockQuoteNotifier,
      MarketQuote,
      String
    >(StockQuoteNotifier.new);

```

---

### File: `lib\features\market\stock_analysis_report.dart`

```dart
import 'package:flutter/material.dart';

import '../../domain/models.dart';
import '../../widgets/structured_data_card.dart';

class StockAnalysisReport extends StatelessWidget {
  const StockAnalysisReport({required this.analysis, super.key});

  final StockAnalysisResult analysis;

  @override
  Widget build(BuildContext context) {
    final payload = _asMap(analysis.payload);
    final analysisData = _asMap(payload['analysis']);
    final marketData = _asMap(payload['market_data']);
    final engines = _asMap(analysisData['engines']);
    final technical = _engineDetails(engines, 'technical');
    final marketEnvironment = _engineDetails(engines, 'market_environment');
    final risk = _engineDetails(engines, 'risk');
    final scenario = _engineDetails(engines, 'scenario');
    final tradePlan = _asMap(analysisData['trade_plan']);
    final explanation = _text(payload['explanation']);
    final disclaimer = _text(payload['disclaimer']);
    final warnings = _asList(analysisData['warnings'])
        .map((item) => item.toString())
        .where((item) => item.trim().isNotEmpty)
        .toList(growable: false);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _DecisionCard(
          ticker: analysis.ticker,
          signal: _text(analysisData['signal']),
          score: _number(analysisData['final_score']),
          confidence: _number(analysisData['confidence']),
          explanation: explanation,
          cached: analysis.cached,
          chargedCoins: analysis.chargedCoins,
          balanceCoins: analysis.balanceCoins,
        ),
        const SizedBox(height: 12),
        _TradePlanCard(tradePlan: tradePlan, risk: risk),
        const SizedBox(height: 12),
        _TechnicalOverviewCard(
          technical: technical,
          marketEnvironment: marketEnvironment,
          risk: risk,
        ),
        const SizedBox(height: 12),
        _ScenarioCard(scenario: scenario),
        const SizedBox(height: 12),
        _EngineScoresCard(engines: engines),
        const SizedBox(height: 12),
        _MarketDataCard(marketData: marketData, dataAsOf: analysis.dataAsOf),
        if (warnings.isNotEmpty) ...[
          const SizedBox(height: 12),
          _NoticeCard(
            icon: Icons.warning_amber_rounded,
            title: 'تنبيهات التحليل',
            body: warnings.join('\n'),
            isWarning: true,
          ),
        ],
        if (disclaimer.isNotEmpty) ...[
          const SizedBox(height: 12),
          _NoticeCard(
            icon: Icons.info_outline_rounded,
            title: 'تنبيه مهم',
            body: disclaimer,
          ),
        ],
        const SizedBox(height: 12),
        StructuredDataCard(
          title: 'البيانات التقنية الخام',
          data: analysis.payload,
          initiallyExpanded: false,
        ),
      ],
    );
  }
}

class _DecisionCard extends StatelessWidget {
  const _DecisionCard({
    required this.ticker,
    required this.signal,
    required this.score,
    required this.confidence,
    required this.explanation,
    required this.cached,
    required this.chargedCoins,
    required this.balanceCoins,
  });

  final String ticker;
  final String signal;
  final double? score;
  final double? confidence;
  final String explanation;
  final bool cached;
  final String chargedCoins;
  final String balanceCoins;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final normalizedSignal = signal.toUpperCase();
    final signalLabel = _signalLabel(normalizedSignal);
    final signalIcon = switch (normalizedSignal) {
      'BUY' => Icons.trending_up_rounded,
      'SELL' => Icons.trending_down_rounded,
      _ => Icons.horizontal_rule_rounded,
    };
    final background = switch (normalizedSignal) {
      'SELL' => scheme.errorContainer,
      'BUY' => scheme.secondaryContainer,
      _ => scheme.surfaceContainerHighest,
    };

    return Card(
      color: background,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.headlineMedium
                            ?.copyWith(fontWeight: FontWeight.w900),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'القرار الآلي: $signalLabel',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(signalIcon, size: 42),
              ],
            ),
            const SizedBox(height: 16),
            _MetricGrid(
              items: [
                _MetricData(
                  label: 'الدرجة النهائية',
                  value: '${_formatNumber(score)}/100',
                ),
                _MetricData(
                  label: 'الثقة',
                  value: '${_formatNumber(confidence)}%',
                ),
              ],
            ),
            if (score != null) ...[
              const SizedBox(height: 12),
              LinearProgressIndicator(
                value: (score! / 100).clamp(0.0, 1.0).toDouble(),
                minHeight: 8,
                borderRadius: BorderRadius.circular(99),
              ),
            ],
            if (explanation.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(explanation, style: Theme.of(context).textTheme.bodyLarge),
            ],
            const SizedBox(height: 12),
            Text(
              cached
                  ? 'تم عرض تحليل محفوظ سابقًا، ولم يتم خصم عملات جديدة.'
                  : 'تم خصم $chargedCoins عملة بعد نجاح التحليل.',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            Text('الرصيد الحالي: $balanceCoins عملة'),
          ],
        ),
      ),
    );
  }
}

class _TradePlanCard extends StatelessWidget {
  const _TradePlanCard({required this.tradePlan, required this.risk});

  final Map<String, dynamic> tradePlan;
  final Map<String, dynamic> risk;

  @override
  Widget build(BuildContext context) {
    if (tradePlan.isEmpty) {
      return const SizedBox.shrink();
    }
    return _SectionCard(
      icon: Icons.route_rounded,
      title: 'خطة التداول الافتراضية',
      subtitle:
          'الأرقام محسوبة آليًا وفق إعدادات رأس المال والمخاطر داخل النظام.',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'سعر الدخول',
            value: _formatMoney(tradePlan['entry']),
          ),
          _MetricData(
            label: 'وقف الخسارة',
            value: _formatMoney(tradePlan['stop_loss']),
          ),
          _MetricData(
            label: 'الهدف الأول',
            value: _formatMoney(tradePlan['target_1']),
          ),
          _MetricData(
            label: 'الهدف الثاني',
            value: _formatMoney(tradePlan['target_2']),
          ),
          _MetricData(
            label: 'العائد/المخاطرة 1',
            value: _formatNumber(tradePlan['reward_risk_1']),
          ),
          _MetricData(
            label: 'العائد/المخاطرة 2',
            value: _formatNumber(tradePlan['reward_risk_2']),
          ),
          _MetricData(
            label: 'حجم المركز المقترح',
            value: _formatInteger(tradePlan['position_size']),
          ),
          _MetricData(
            label: 'قيمة المركز',
            value: '${_formatNumber(tradePlan['position_value'])} ج.م',
          ),
          _MetricData(
            label: 'مبلغ المخاطرة',
            value: '${_formatNumber(tradePlan['risk_amount'])} ج.م',
          ),
          _MetricData(
            label: 'مستوى المخاطرة',
            value: _riskLabel(_text(risk['risk_level'])),
          ),
        ],
      ),
    );
  }
}

class _TechnicalOverviewCard extends StatelessWidget {
  const _TechnicalOverviewCard({
    required this.technical,
    required this.marketEnvironment,
    required this.risk,
  });

  final Map<String, dynamic> technical;
  final Map<String, dynamic> marketEnvironment;
  final Map<String, dynamic> risk;

  @override
  Widget build(BuildContext context) {
    return _SectionCard(
      icon: Icons.query_stats_rounded,
      title: 'الملخص الفني',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'الاتجاه',
            value: _trendLabel(_text(technical['trend'])),
          ),
          _MetricData(
            label: 'حالة السوق',
            value: _trendLabel(_text(marketEnvironment['regime'])),
          ),
          _MetricData(
            label: 'الإغلاق',
            value: _formatMoney(technical['close']),
          ),
          _MetricData(label: 'RSI', value: _formatNumber(technical['rsi'])),
          _MetricData(
            label: 'متوسط 20 يوم',
            value: _formatMoney(technical['sma_20']),
          ),
          _MetricData(
            label: 'متوسط 50 يوم',
            value: _formatMoney(technical['sma_50']),
          ),
          _MetricData(
            label: 'متوسط 200 يوم',
            value: _formatMoney(technical['sma_200']),
          ),
          _MetricData(
            label: 'MACD',
            value: _formatNumber(technical['macd'], decimals: 4),
          ),
          _MetricData(
            label: 'عائد 20 يوم',
            value: '${_formatNumber(technical['return_20d_pct'])}%',
          ),
          _MetricData(
            label: 'نسبة الحجم',
            value: _formatNumber(technical['volume_ratio']),
          ),
          _MetricData(
            label: 'إجمالي المخاطرة',
            value: '${_formatNumber(risk['total_risk_pct'])}%',
          ),
          _MetricData(
            label: 'ATR',
            value: '${_formatNumber(risk['atr_pct'])}%',
          ),
        ],
      ),
    );
  }
}

class _ScenarioCard extends StatelessWidget {
  const _ScenarioCard({required this.scenario});

  final Map<String, dynamic> scenario;

  @override
  Widget build(BuildContext context) {
    if (scenario.isEmpty) {
      return const SizedBox.shrink();
    }
    final bullish = _asMap(scenario['bullish']);
    final base = _asMap(scenario['base']);
    final bearish = _asMap(scenario['bearish']);
    return _SectionCard(
      icon: Icons.alt_route_rounded,
      title: 'السيناريوهات المحتملة',
      subtitle: 'احتمالات نموذجية وليست ضمانًا لحركة السعر.',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'الصعود',
            value: '${_formatNumber(bullish['probability_pct'])}%',
            subtitle: 'هدف ${_formatMoney(bullish['target'])}',
          ),
          _MetricData(
            label: 'السيناريو الأساسي',
            value: '${_formatNumber(base['probability_pct'])}%',
            subtitle: 'هدف ${_formatMoney(base['target'])}',
          ),
          _MetricData(
            label: 'الهبوط',
            value: '${_formatNumber(bearish['probability_pct'])}%',
            subtitle: 'مستوى ${_formatMoney(bearish['target'])}',
          ),
        ],
      ),
    );
  }
}

class _EngineScoresCard extends StatelessWidget {
  const _EngineScoresCard({required this.engines});

  final Map<String, dynamic> engines;

  @override
  Widget build(BuildContext context) {
    final entries = engines.entries
        .map((entry) => MapEntry(entry.key, _asMap(entry.value)))
        .where((entry) => entry.value.isNotEmpty)
        .toList(growable: false);
    if (entries.isEmpty) {
      return const SizedBox.shrink();
    }
    return _SectionCard(
      icon: Icons.hub_rounded,
      title: 'درجات محركات التحليل',
      child: Column(
        children: [
          for (var index = 0; index < entries.length; index++) ...[
            _EngineScoreRow(
              name: _engineLabel(entries[index].key),
              score: _number(entries[index].value['score']),
              confidence: _number(entries[index].value['confidence']),
            ),
            if (index != entries.length - 1) const Divider(height: 22),
          ],
        ],
      ),
    );
  }
}

class _EngineScoreRow extends StatelessWidget {
  const _EngineScoreRow({
    required this.name,
    required this.score,
    required this.confidence,
  });

  final String name;
  final double? score;
  final double? confidence;

  @override
  Widget build(BuildContext context) {
    final progress = ((score ?? 0) / 100).clamp(0.0, 1.0).toDouble();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                name,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
            Text('${_formatNumber(score)}/100'),
          ],
        ),
        const SizedBox(height: 6),
        LinearProgressIndicator(
          value: progress,
          minHeight: 7,
          borderRadius: BorderRadius.circular(99),
        ),
        if (confidence != null) ...[
          const SizedBox(height: 5),
          Text(
            'الثقة ${_formatNumber(confidence)}%',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ],
    );
  }
}

class _MarketDataCard extends StatelessWidget {
  const _MarketDataCard({required this.marketData, required this.dataAsOf});

  final Map<String, dynamic> marketData;
  final DateTime dataAsOf;

  @override
  Widget build(BuildContext context) {
    final provider = _text(marketData['provider']);
    return _SectionCard(
      icon: Icons.storage_rounded,
      title: 'بيانات السوق المستخدمة',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'المصدر',
            value: provider.toLowerCase() == 'tradingview'
                ? 'TradingView'
                : provider,
          ),
          _MetricData(
            label: 'عدد الشموع',
            value: _formatInteger(marketData['candle_count']),
          ),
          _MetricData(
            label: 'الإطار الزمني',
            value: _intervalLabel(_text(marketData['interval'])),
          ),
          _MetricData(
            label: 'الفترة',
            value: _periodLabel(_text(marketData['period'])),
          ),
          _MetricData(
            label: 'آخر تحديث للبيانات',
            value: _formatArabicDate(dataAsOf),
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.icon,
    required this.title,
    required this.child,
    this.subtitle,
  });

  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(icon),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            if (subtitle case final text?) ...[
              const SizedBox(height: 6),
              Text(text, style: Theme.of(context).textTheme.bodySmall),
            ],
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}

class _MetricGrid extends StatelessWidget {
  const _MetricGrid({required this.items});

  final List<_MetricData> items;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final useTwoColumns = constraints.maxWidth >= 320;
        final width = useTwoColumns
            ? (constraints.maxWidth - 10) / 2
            : constraints.maxWidth;
        return Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            for (final item in items)
              SizedBox(
                width: width,
                child: _MetricTile(data: item),
              ),
          ],
        );
      },
    );
  }
}

class _MetricData {
  const _MetricData({required this.label, required this.value, this.subtitle});

  final String label;
  final String value;
  final String? subtitle;
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({required this.data});

  final _MetricData data;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 88),
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(data.label, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 6),
          Text(
            data.value.isEmpty ? '—' : data.value,
            textDirection: _containsLatinOrNumber(data.value)
                ? TextDirection.ltr
                : TextDirection.rtl,
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
          if (data.subtitle case final subtitle?) ...[
            const SizedBox(height: 4),
            Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
          ],
        ],
      ),
    );
  }
}

class _NoticeCard extends StatelessWidget {
  const _NoticeCard({
    required this.icon,
    required this.title,
    required this.body,
    this.isWarning = false,
  });

  final IconData icon;
  final String title;
  final String body;
  final bool isWarning;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      color: isWarning ? scheme.errorContainer : scheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  Text(body),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

Map<String, dynamic> _asMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return value.map((key, item) => MapEntry(key.toString(), item));
  }
  return const {};
}

List<Object?> _asList(Object? value) {
  return value is List ? value.cast<Object?>() : const [];
}

Map<String, dynamic> _engineDetails(Map<String, dynamic> engines, String key) {
  return _asMap(_asMap(engines[key])['details']);
}

double? _number(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '');
}

String _text(Object? value) => value?.toString().trim() ?? '';

String _formatNumber(Object? value, {int decimals = 2}) {
  final number = _number(value);
  if (number == null) {
    return '—';
  }
  var text = number.toStringAsFixed(decimals);
  if (text.contains('.')) {
    text = text.replaceFirst(RegExp(r'0+$'), '');
    text = text.replaceFirst(RegExp(r'\.$'), '');
  }
  return text;
}

String _formatInteger(Object? value) {
  final number = _number(value);
  return number == null ? '—' : number.round().toString();
}

String _formatMoney(Object? value) {
  final formatted = _formatNumber(value, decimals: 4);
  return formatted == '—' ? formatted : '$formatted ج.م';
}

String _signalLabel(String signal) {
  return switch (signal) {
    'BUY' => 'شراء مشروط',
    'SELL' => 'بيع أو خروج',
    'HOLD' => 'انتظار',
    _ => signal.isEmpty ? 'غير محدد' : signal,
  };
}

String _trendLabel(String value) {
  return switch (value.toLowerCase()) {
    'bullish' => 'صاعد',
    'weak_bullish' => 'صاعد ضعيف',
    'uptrend' => 'اتجاه صاعد',
    'bearish' => 'هابط',
    'weak_bearish' => 'هابط ضعيف',
    'downtrend' => 'اتجاه هابط',
    'sideways' || 'neutral' => 'عرضي / محايد',
    _ => value.isEmpty ? '—' : value,
  };
}

String _riskLabel(String value) {
  return switch (value.toLowerCase()) {
    'low' => 'منخفض',
    'medium' => 'متوسط',
    'high' => 'مرتفع',
    _ => value.isEmpty ? '—' : value,
  };
}

String _engineLabel(String key) {
  return switch (key) {
    'stock_qualification' => 'تأهيل السهم',
    'market_environment' => 'بيئة السوق',
    'technical' => 'التحليل الفني',
    'smc' => 'هيكل السوق SMC',
    'multi_timeframe' => 'تعدد الأطر الزمنية',
    'quantitative' => 'التحليل الكمي',
    'risk' => 'إدارة المخاطر',
    'scenario' => 'السيناريوهات',
    _ => key,
  };
}

String _intervalLabel(String value) {
  return switch (value) {
    '1d' => 'يومي',
    '1h' => 'ساعة',
    '1w' => 'أسبوعي',
    _ => value.isEmpty ? '—' : value,
  };
}

String _periodLabel(String value) {
  return switch (value) {
    '1y' => 'سنة',
    '6mo' => '6 أشهر',
    '3mo' => '3 أشهر',
    _ => value.isEmpty ? '—' : value,
  };
}

String _formatArabicDate(DateTime value) {
  const months = [
    'يناير',
    'فبراير',
    'مارس',
    'أبريل',
    'مايو',
    'يونيو',
    'يوليو',
    'أغسطس',
    'سبتمبر',
    'أكتوبر',
    'نوفمبر',
    'ديسمبر',
  ];
  final local = value.toLocal();
  final hour = local.hour == 0
      ? 12
      : (local.hour > 12 ? local.hour - 12 : local.hour);
  final minute = local.minute.toString().padLeft(2, '0');
  final period = local.hour >= 12 ? 'م' : 'ص';
  return '${local.day} ${months[local.month - 1]} ${local.year}، $hour:$minute $period';
}

bool _containsLatinOrNumber(String value) {
  return RegExp(r'[A-Za-z0-9]').hasMatch(value);
}

```

---

### File: `lib\features\market\stock_analysis_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'stock_analysis_report.dart';

class StockAnalysisScreen extends ConsumerStatefulWidget {
  const StockAnalysisScreen({super.key, required this.ticker});

  final String ticker;

  @override
  ConsumerState<StockAnalysisScreen> createState() =>
      _StockAnalysisScreenState();
}

class _StockAnalysisScreenState extends ConsumerState<StockAnalysisScreen> {
  StockAnalysisResult? _analysis;
  bool _loadingSaved = false;
  bool _analyzing = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    Future<void>.microtask(_loadSavedAnalysis);
  }

  Future<void> _loadSavedAnalysis() async {
    if (!mounted) {
      return;
    }
    setState(() => _loadingSaved = true);
    try {
      final saved = await ref
          .read(backendRepositoryProvider)
          .getLatestOwnedStockAnalysis(widget.ticker);
      if (mounted && saved != null) {
        setState(() => _analysis = saved);
      }
    } on ApiException {
      // A saved analysis is optional; the user can still request a fresh one.
    } finally {
      if (mounted) {
        setState(() => _loadingSaved = false);
      }
    }
  }

  Future<void> _analyze() async {
    if (_analyzing) {
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('تحليل ${widget.ticker}'),
        content: const Text(
          'تكلفة التحليل بالبيانات الجديدة 0.5 عملة. التحليل المحفوظ لنفس الحساب ونفس بيانات السوق يُعرض دون خصم جديد.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('متابعة'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    setState(() {
      _analyzing = true;
      _error = null;
    });
    try {
      final analysis = await ref
          .read(backendRepositoryProvider)
          .analyzeStock(widget.ticker);
      if (mounted) {
        setState(() => _analysis = analysis);
      }
      ref.invalidate(walletSummaryProvider);
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      } on Object {
        // The completed analysis must remain visible even if the optional
        // profile refresh fails. Wallet data will retry through its provider.
      }
      if (mounted) {
        await ref
            .read(freePlanInterstitialProvider)
            .recordMeaningfulAction(
              enabled:
                  ref.read(sessionControllerProvider).profile?.adsEnabled ==
                  true,
            );
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _analyzing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('تحليل ${widget.ticker}')),
      body: RefreshIndicator(
        onRefresh: _loadSavedAnalysis,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'تحليل ${widget.ticker}',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'التقرير أدناه مبني على البيانات الفنية والكمية للسهم.',
                    ),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed: _analyzing ? null : _analyze,
                      icon: _analyzing
                          ? const SizedBox.square(
                              dimension: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                              ),
                            )
                          : const Icon(Icons.auto_graph_rounded),
                      label: const Text('تحليل بالبيانات الجديدة — 0.5 عملة'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            if (_loadingSaved) ...[
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox.square(
                    dimension: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('جاري البحث عن آخر تحليل محفوظ للحساب...'),
                ],
              ),
              const SizedBox(height: 12),
            ],
            if (_error != null) ...[
              const SizedBox(height: 12),
              Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(_error!, textAlign: TextAlign.center),
                ),
              ),
            ],
            if (_analysis case final analysis?) ...[
              const SizedBox(height: 16),
              StockAnalysisReport(analysis: analysis),
            ],
          ],
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\market\stock_analysis_tab.dart`

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'stock_analysis_report.dart';

class StockAnalysisTab extends ConsumerStatefulWidget {
  const StockAnalysisTab({super.key});

  @override
  ConsumerState<StockAnalysisTab> createState() => _StockAnalysisTabState();
}

class _StockAnalysisTabState extends ConsumerState<StockAnalysisTab> {
  final _queryController = TextEditingController();
  Timer? _searchDebounce;
  int _searchRevision = 0;
  List<MarketInstrument> _results = const [];
  MarketInstrument? _selected;
  StockAnalysisResult? _analysis;
  bool _searching = false;
  bool _loadingSaved = false;
  bool _analyzing = false;
  String? _error;

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _queryController.dispose();
    super.dispose();
  }

  void _onQueryChanged(String value) {
    _searchDebounce?.cancel();
    final normalizedQuery = value.trim().toUpperCase();
    final revision = ++_searchRevision;
    setState(() {
      _selected = null;
      _results = const [];
      _error = null;
      _analysis = null;
      _loadingSaved = false;
      _searching = normalizedQuery.isNotEmpty;
    });
    if (normalizedQuery.isEmpty) {
      return;
    }
    _searchDebounce = Timer(
      const Duration(milliseconds: 350),
      () => _search(query: normalizedQuery, revision: revision),
    );
  }

  Future<void> _search({String? query, int? revision}) async {
    _searchDebounce?.cancel();
    final normalizedQuery = (query ?? _queryController.text)
        .trim()
        .toUpperCase();
    final requestRevision = revision ?? ++_searchRevision;
    if (normalizedQuery.isEmpty) {
      if (mounted) {
        setState(() {
          _results = const [];
          _selected = null;
          _analysis = null;
          _searching = false;
          _error = 'اكتب رمز السهم أو اسم الشركة أولًا.';
        });
      }
      return;
    }
    if (mounted) {
      setState(() {
        _searching = true;
        _error = null;
        _analysis = null;
      });
    }
    try {
      final results = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(normalizedQuery);
      if (!mounted || requestRevision != _searchRevision) {
        return;
      }
      MarketInstrument? exactMatch;
      for (final instrument in results) {
        if (instrument.ticker == normalizedQuery) {
          exactMatch = instrument;
          break;
        }
      }
      exactMatch ??= results.length == 1 ? results.first : null;
      setState(() {
        _results = results;
        _selected = exactMatch;
        _error = results.isEmpty
            ? 'لم نعثر على سهم مصري مطابق في كتالوج السوق.'
            : null;
      });
      if (exactMatch != null) {
        unawaited(_loadSavedAnalysis(exactMatch, requestRevision));
      }
    } on ApiException catch (error) {
      if (mounted && requestRevision == _searchRevision) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted && requestRevision == _searchRevision) {
        setState(() => _searching = false);
      }
    }
  }

  void _selectInstrument(MarketInstrument instrument) {
    final revision = ++_searchRevision;
    setState(() {
      _selected = instrument;
      _analysis = null;
      _error = null;
    });
    unawaited(_loadSavedAnalysis(instrument, revision));
  }

  Future<void> _loadSavedAnalysis(
    MarketInstrument instrument,
    int revision,
  ) async {
    if (mounted) {
      setState(() => _loadingSaved = true);
    }
    try {
      final saved = await ref
          .read(backendRepositoryProvider)
          .getLatestOwnedStockAnalysis(instrument.ticker);
      if (!mounted || revision != _searchRevision) {
        return;
      }
      if (_selected?.ticker == instrument.ticker) {
        setState(() => _analysis = saved);
      }
    } on ApiException {
      // A saved analysis is optional; the user can still request a fresh one.
    } finally {
      if (mounted && revision == _searchRevision) {
        setState(() => _loadingSaved = false);
      }
    }
  }

  Future<void> _analyze() async {
    final instrument = _selected;
    if (instrument == null || _analyzing) {
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('تحليل ${instrument.ticker}'),
        content: const Text(
          'تكلفة التحليل بالبيانات الجديدة 0.5 عملة. التحليل المحفوظ لنفس الحساب ونفس بيانات السوق يُعرض دون خصم جديد.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('متابعة'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    setState(() {
      _analyzing = true;
      _error = null;
    });
    try {
      final analysis = await ref
          .read(backendRepositoryProvider)
          .analyzeStock(instrument.ticker);
      if (mounted) {
        setState(() => _analysis = analysis);
      }
      ref.invalidate(walletSummaryProvider);
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      } on Object {
        // The completed analysis must remain visible even if the optional
        // profile refresh fails. Wallet data will retry through its provider.
      }
      if (mounted) {
        await ref
            .read(freePlanInterstitialProvider)
            .recordMeaningfulAction(
              enabled:
                  ref.read(sessionControllerProvider).profile?.adsEnabled ==
                  true,
            );
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _analyzing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'تحليل سهم من البورصة المصرية',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 8),
                const Text(
                  'اكتب رمز السهم أو اسم الشركة، وستظهر النتائج تلقائيًا.',
                ),
                const SizedBox(height: 18),
                TextField(
                  controller: _queryController,
                  textDirection: TextDirection.ltr,
                  textCapitalization: TextCapitalization.characters,
                  decoration: InputDecoration(
                    labelText: 'رمز السهم أو اسم الشركة',
                    hintText: 'COMI',
                    prefixIcon: IconButton(
                      tooltip: 'تحديث البحث',
                      onPressed: _searching ? null : () => _search(),
                      icon: _searching
                          ? const SizedBox.square(
                              dimension: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.search_rounded),
                    ),
                  ),
                  onChanged: _onQueryChanged,
                  onSubmitted: (_) => _search(),
                ),
                if (_results.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    '${_results.length} نتيجة',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 4),
                  for (final instrument in _results)
                    Builder(
                      builder: (context) {
                        final selected = _selected?.ticker == instrument.ticker;
                        return Card(
                          color: selected
                              ? Theme.of(context).colorScheme.secondaryContainer
                              : null,
                          child: ListTile(
                            onTap: () => _selectInstrument(instrument),
                            leading: Icon(
                              selected
                                  ? Icons.radio_button_checked_rounded
                                  : Icons.radio_button_unchecked_rounded,
                            ),
                            title: Text(
                              instrument.ticker,
                              textDirection: TextDirection.ltr,
                            ),
                            subtitle: Text(
                              instrument.description.isEmpty
                                  ? '${instrument.exchange} — ${instrument.providerSymbol}'
                                  : '${instrument.description} • ${instrument.exchange}',
                              textDirection: instrument.description.isEmpty
                                  ? TextDirection.ltr
                                  : TextDirection.rtl,
                            ),
                          ),
                        );
                      },
                    ),
                ],
                if (_loadingSaved) ...[
                  const SizedBox(height: 10),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox.square(
                        dimension: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      SizedBox(width: 8),
                      Text('جاري البحث عن آخر تحليل محفوظ للحساب...'),
                    ],
                  ),
                ],
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: _selected == null || _analyzing ? null : _analyze,
                  icon: _analyzing
                      ? const SizedBox.square(
                          dimension: 20,
                          child: CircularProgressIndicator(strokeWidth: 2.5),
                        )
                      : const Icon(Icons.auto_graph_rounded),
                  label: const Text('تحليل السهم — 0.5 عملة'),
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed: _analyzing
                      ? null
                      : () => context.push('/market/compare'),
                  icon: const Icon(Icons.compare_arrows_rounded),
                  label: const Text('مقارنة سهمين أو أكثر'),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        const FreePlanNativeAd(),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Card(
            color: Theme.of(context).colorScheme.errorContainer,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(_error!, textAlign: TextAlign.center),
            ),
          ),
        ],
        if (_analysis case final analysis?) ...[
          const SizedBox(height: 16),
          StockAnalysisReport(analysis: analysis),
        ],
      ],
    );
  }
}

```

---

### File: `lib\features\market\stock_comparison_models.dart`

```dart
class StockComparisonItem {
  const StockComparisonItem({
    required this.rank,
    required this.ticker,
    required this.analysisId,
    required this.dataAsOf,
    required this.signal,
    required this.finalScore,
    required this.confidence,
    required this.comparisonScore,
    required this.trend,
    required this.rsi,
    required this.averageVolume20,
    required this.riskLevel,
    required this.riskScore,
    required this.entry,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.rewardRisk1,
  });

  final int rank;
  final String ticker;
  final String analysisId;
  final DateTime dataAsOf;
  final String signal;
  final double finalScore;
  final double confidence;
  final double comparisonScore;
  final String trend;
  final double rsi;
  final double averageVolume20;
  final String riskLevel;
  final double riskScore;
  final double entry;
  final double stopLoss;
  final double target1;
  final double target2;
  final double rewardRisk1;

  factory StockComparisonItem.fromJson(Map<String, dynamic> json) {
    return StockComparisonItem(
      rank: _int(json['rank']),
      ticker: _string(json['ticker']),
      analysisId: _string(json['analysis_id']),
      dataAsOf: DateTime.parse(_string(json['data_as_of'])),
      signal: _string(json['signal']),
      finalScore: _double(json['final_score']),
      confidence: _double(json['confidence']),
      comparisonScore: _double(json['comparison_score']),
      trend: _string(json['trend']),
      rsi: _double(json['rsi']),
      averageVolume20: _double(json['average_volume_20']),
      riskLevel: _string(json['risk_level']),
      riskScore: _double(json['risk_score']),
      entry: _double(json['entry']),
      stopLoss: _double(json['stop_loss']),
      target1: _double(json['target_1']),
      target2: _double(json['target_2']),
      rewardRisk1: _double(json['reward_risk_1']),
    );
  }
}

class StockComparisonFailure {
  const StockComparisonFailure({
    required this.ticker,
    required this.code,
    required this.message,
    required this.retryable,
  });

  final String ticker;
  final String code;
  final String message;
  final bool retryable;

  factory StockComparisonFailure.fromJson(Map<String, dynamic> json) {
    return StockComparisonFailure(
      ticker: _string(json['ticker']),
      code: _string(json['code']),
      message: _string(json['message']),
      retryable: json['retryable'] as bool? ?? true,
    );
  }
}

class StockComparisonResult {
  const StockComparisonResult({
    required this.comparisonId,
    required this.requestKey,
    required this.tickers,
    required this.bestTicker,
    required this.summary,
    required this.items,
    required this.failedItems,
    required this.includedAllowance,
    required this.comparisonChargedPoints,
    required this.comparisonChargedCoins,
    required this.analysisChargedPoints,
    required this.analysisChargedCoins,
    required this.allowanceUsed,
    required this.allowanceRemaining,
    required this.idempotent,
    required this.balancePoints,
    required this.balanceCoins,
    required this.disclaimer,
  });

  final String comparisonId;
  final String requestKey;
  final List<String> tickers;
  final String bestTicker;
  final String summary;
  final List<StockComparisonItem> items;
  final List<StockComparisonFailure> failedItems;
  final bool includedAllowance;
  final int comparisonChargedPoints;
  final String comparisonChargedCoins;
  final int analysisChargedPoints;
  final String analysisChargedCoins;
  final int allowanceUsed;
  final int allowanceRemaining;
  final bool idempotent;
  final int balancePoints;
  final String balanceCoins;
  final String disclaimer;

  factory StockComparisonResult.fromJson(Map<String, dynamic> json) {
    return StockComparisonResult(
      comparisonId: _string(json['comparison_id']),
      requestKey: _string(json['request_key']),
      tickers: _list(json['tickers']).map(_string).toList(growable: false),
      bestTicker: _string(json['best_ticker']),
      summary: _string(json['summary']),
      items: _list(json['items'])
          .map((item) => StockComparisonItem.fromJson(_map(item)))
          .toList(growable: false),
      failedItems: _list(json['failed_items'])
          .map((item) => StockComparisonFailure.fromJson(_map(item)))
          .toList(growable: false),
      includedAllowance: json['included_allowance'] as bool? ?? false,
      comparisonChargedPoints: _int(json['comparison_charged_points']),
      comparisonChargedCoins: _string(json['comparison_charged_coins']),
      analysisChargedPoints: _int(json['analysis_charged_points']),
      analysisChargedCoins: _string(json['analysis_charged_coins']),
      allowanceUsed: _int(json['allowance_used']),
      allowanceRemaining: _int(json['allowance_remaining']),
      idempotent: json['idempotent'] as bool? ?? false,
      balancePoints: _int(json['balance_points']),
      balanceCoins: _string(json['balance_coins']),
      disclaimer: _string(json['disclaimer']),
    );
  }
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

List<dynamic> _list(Object? value) => value is List ? value : const [];

String _string(Object? value) => value?.toString() ?? '';

int _int(Object? value) {
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.round();
  }
  return int.tryParse(_string(value)) ?? 0;
}

double _double(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(_string(value)) ?? 0;
}

```

---

### File: `lib\features\market\stock_comparison_repository.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import '../../core/network/api_exception.dart';
import 'stock_comparison_models.dart';

class StockComparisonRepository {
  const StockComparisonRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<StockComparisonResult> compare({
    required String requestKey,
    required List<String> tickers,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/market/comparisons',
        data: <String, dynamic>{
          'request_key': requestKey,
          'tickers': tickers,
          'language': 'ar',
        },
      );
      final data = response.data;
      if (data == null) {
        throw const ApiException(message: 'استجابة المقارنة غير صالحة.');
      }
      return StockComparisonResult.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

final stockComparisonRepositoryProvider = Provider<StockComparisonRepository>((
  ref,
) {
  return StockComparisonRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\market\stock_comparison_screen.dart`

```dart
import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'stock_comparison_models.dart';
import 'stock_comparison_repository.dart';

class StockComparisonScreen extends ConsumerStatefulWidget {
  const StockComparisonScreen({super.key});

  @override
  ConsumerState<StockComparisonScreen> createState() =>
      _StockComparisonScreenState();
}

class _StockComparisonScreenState extends ConsumerState<StockComparisonScreen> {
  final _queryController = TextEditingController();
  Timer? _debounce;
  int _searchRevision = 0;
  List<MarketInstrument> _results = const [];
  final List<MarketInstrument> _selected = [];
  bool _searching = false;
  bool _comparing = false;
  String? _error;
  String? _requestKey;
  StockComparisonResult? _result;

  @override
  void dispose() {
    _debounce?.cancel();
    _queryController.dispose();
    super.dispose();
  }

  int get _maxStocks {
    final plan =
        ref.read(sessionControllerProvider).profile?.planCode ?? 'free';
    return switch (plan) {
      'basic' => 2,
      'advanced' => 3,
      'pro' => 5,
      _ => 3,
    };
  }

  void _onQueryChanged(String value) {
    _debounce?.cancel();
    final query = value.trim().toUpperCase();
    final revision = ++_searchRevision;
    setState(() {
      _results = const [];
      _error = null;
      _searching = query.isNotEmpty;
    });
    if (query.isEmpty) {
      return;
    }
    _debounce = Timer(
      const Duration(milliseconds: 350),
      () => _search(query, revision),
    );
  }

  Future<void> _search(String query, int revision) async {
    try {
      final items = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(query, limit: 20);
      if (!mounted || revision != _searchRevision) {
        return;
      }
      final selectedTickers = _selected.map((item) => item.ticker).toSet();
      setState(() {
        _results = items
            .where((item) => !selectedTickers.contains(item.ticker))
            .toList(growable: false);
        _error = items.isEmpty ? 'لم نعثر على سهم مطابق.' : null;
      });
    } on ApiException catch (error) {
      if (mounted && revision == _searchRevision) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted && revision == _searchRevision) {
        setState(() => _searching = false);
      }
    }
  }

  void _select(MarketInstrument instrument) {
    if (_selected.length >= _maxStocks) {
      setState(() => _error = 'خطتك تسمح بمقارنة حتى $_maxStocks أسهم.');
      return;
    }
    setState(() {
      _selected.add(instrument);
      _results = const [];
      _queryController.clear();
      _error = null;
      _result = null;
      _requestKey = null;
    });
  }

  void _remove(MarketInstrument instrument) {
    setState(() {
      _selected.removeWhere((item) => item.ticker == instrument.ticker);
      _result = null;
      _requestKey = null;
      _error = null;
    });
  }

  String _newRequestKey() {
    final random = Random.secure();
    final suffix = List<int>.generate(
      12,
      (_) => random.nextInt(36),
    ).map((value) => value.toRadixString(36)).join();
    return 'comparison_${DateTime.now().microsecondsSinceEpoch}_$suffix';
  }

  Future<void> _compare() async {
    if (_selected.length < 2 || _comparing) {
      return;
    }
    final profile = ref.read(sessionControllerProvider).profile;
    final planCode = profile?.planCode ?? 'free';
    final paidAllowance = planCode != 'free';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تأكيد مقارنة الأسهم'),
        content: Text(
          paidAllowance
              ? 'ستُستخدم المقارنات الشهرية المتضمنة في خطتك أولًا. أي سهم لا تملك تحليله الحالي قد يكلف 0.5 عملة.'
              : 'تكلفة المقارنة 0.5 عملة، بالإضافة إلى 0.5 عملة لكل سهم لا تملك تحليله الحالي. الأسهم المحللة والمحفوظة لا تُخصم مرة أخرى.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('ابدأ المقارنة'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    final requestKey = _requestKey ?? _newRequestKey();
    _requestKey = requestKey;
    setState(() {
      _comparing = true;
      _error = null;
    });
    try {
      final result = await ref
          .read(stockComparisonRepositoryProvider)
          .compare(
            requestKey: requestKey,
            tickers: _selected
                .map((item) => item.ticker)
                .toList(growable: false),
          );
      if (!mounted) {
        return;
      }
      setState(() => _result = result);
      ref.invalidate(walletSummaryProvider);
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      } on Object {
        // The comparison remains visible if the optional wallet refresh fails.
      }
      if (!mounted) {
        return;
      }
      await ref
          .read(freePlanInterstitialProvider)
          .recordMeaningfulAction(enabled: profile?.adsEnabled == true);
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _comparing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final planCode =
        ref.watch(sessionControllerProvider).profile?.planCode ?? 'free';
    return Scaffold(
      appBar: AppBar(title: const Text('مقارنة الأسهم')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'اختر من سهمين إلى $_maxStocks أسهم',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      planCode == 'free'
                          ? 'المقارنة نفسها تكلف 0.5 عملة، والتحليلات المحفوظة لا تُخصم مرة أخرى.'
                          : 'يتم استخدام المقارنات الشهرية المتضمنة في خطتك قبل الخصم.',
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _queryController,
                      textDirection: TextDirection.ltr,
                      textCapitalization: TextCapitalization.characters,
                      decoration: InputDecoration(
                        labelText: 'ابحث بالرمز أو اسم الشركة',
                        hintText: 'COMI',
                        prefixIcon: _searching
                            ? const Padding(
                                padding: EdgeInsets.all(14),
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.search_rounded),
                      ),
                      onChanged: _onQueryChanged,
                    ),
                    if (_results.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      for (final instrument in _results.take(8))
                        ListTile(
                          title: Text(
                            instrument.ticker,
                            textDirection: TextDirection.ltr,
                          ),
                          subtitle: Text(
                            instrument.description.isEmpty
                                ? instrument.exchange
                                : instrument.description,
                            textDirection: instrument.description.isEmpty
                                ? TextDirection.ltr
                                : TextDirection.rtl,
                          ),
                          trailing: const Icon(
                            Icons.add_circle_outline_rounded,
                          ),
                          onTap: () => _select(instrument),
                        ),
                    ],
                  ],
                ),
              ),
            ),
            if (_selected.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final instrument in _selected)
                    InputChip(
                      label: Text(instrument.ticker),
                      onDeleted: _comparing ? null : () => _remove(instrument),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: _selected.length < 2 || _comparing ? null : _compare,
                icon: _comparing
                    ? const SizedBox.square(
                        dimension: 20,
                        child: CircularProgressIndicator(strokeWidth: 2.5),
                      )
                    : const Icon(Icons.compare_arrows_rounded),
                label: Text(
                  _comparing
                      ? 'جاري تحليل المقارنة...'
                      : 'قارن الأسهم المختارة',
                ),
              ),
            ],
            if (_error != null) ...[
              const SizedBox(height: 12),
              Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(_error!, textAlign: TextAlign.center),
                ),
              ),
            ],
            const SizedBox(height: 12),
            const FreePlanNativeAd(),
            if (_result case final result?)
              _ComparisonResultView(result: result),
          ],
        ),
      ),
    );
  }
}

class _ComparisonResultView extends StatelessWidget {
  const _ComparisonResultView({required this.result});

  final StockComparisonResult result;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'الأفضل في المقارنة: ${result.bestTicker}',
                  textDirection: TextDirection.rtl,
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 8),
                Text(result.summary),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    Chip(
                      label: Text(
                        result.includedAllowance
                            ? 'المقارنة متضمنة في الخطة'
                            : 'تكلفة المقارنة: ${result.comparisonChargedCoins} عملة',
                      ),
                    ),
                    Chip(
                      label: Text(
                        'تكلفة التحليلات الجديدة: ${result.analysisChargedCoins} عملة',
                      ),
                    ),
                    Chip(label: Text('الرصيد: ${result.balanceCoins} عملة')),
                    if (result.includedAllowance)
                      Chip(
                        label: Text(
                          'المتبقي هذا الشهر: ${result.allowanceRemaining}',
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
        for (final item in result.items) _ComparisonItemCard(item: item),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              result.disclaimer,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ),
      ],
    );
  }
}

class _ComparisonItemCard extends StatelessWidget {
  const _ComparisonItemCard({required this.item});

  final StockComparisonItem item;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${item.rank}')),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    item.ticker,
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Chip(
                  label: Text(
                    '${item.comparisonScore.toStringAsFixed(1)} / 100',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text(_signal(item.signal))),
                Chip(
                  label: Text('الثقة ${item.confidence.toStringAsFixed(1)}%'),
                ),
                Chip(label: Text('الاتجاه ${_trend(item.trend)}')),
                Chip(label: Text('المخاطرة ${_risk(item.riskLevel)}')),
              ],
            ),
            const Divider(height: 24),
            _ValueRow(label: 'الدخول', value: _price(item.entry)),
            _ValueRow(label: 'وقف الخسارة', value: _price(item.stopLoss)),
            _ValueRow(label: 'الهدف الأول', value: _price(item.target1)),
            _ValueRow(label: 'الهدف الثاني', value: _price(item.target2)),
            _ValueRow(
              label: 'العائد مقابل المخاطرة',
              value: item.rewardRisk1 > 0
                  ? '${item.rewardRisk1.toStringAsFixed(1)} : 1'
                  : '—',
            ),
            _ValueRow(
              label: 'RSI',
              value: item.rsi > 0 ? item.rsi.toStringAsFixed(1) : '—',
            ),
          ],
        ),
      ),
    );
  }
}

class _ValueRow extends StatelessWidget {
  const _ValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Expanded(child: Text(label)),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}

String _price(double value) => value > 0 ? value.toStringAsFixed(2) : '—';

String _signal(String value) {
  return switch (value.toUpperCase()) {
    'BUY' => 'شراء مشروط',
    'AVOID' => 'تجنب حاليًا',
    _ => 'مراقبة',
  };
}

String _trend(String value) {
  return switch (value.toLowerCase()) {
    'uptrend' || 'bullish' || 'weak_bullish' => 'صاعد',
    'downtrend' || 'bearish' || 'weak_bearish' => 'هابط',
    _ => 'عرضي',
  };
}

String _risk(String value) {
  return switch (value.toLowerCase()) {
    'low' => 'منخفضة',
    'high' => 'مرتفعة',
    _ => 'متوسطة',
  };
}

```

---

### File: `lib\features\market\stock_detail_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'market_quotes_providers.dart';
import 'stock_quote_card.dart';

class StockDetailScreen extends ConsumerStatefulWidget {
  const StockDetailScreen({super.key, required this.ticker});

  final String ticker;

  @override
  ConsumerState<StockDetailScreen> createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends ConsumerState<StockDetailScreen> {
  bool _fullscreenOpen = false;
  bool _autoFullscreen = false;
  bool _rotationCheckScheduled = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_rotationCheckScheduled) {
      return;
    }
    _rotationCheckScheduled = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _rotationCheckScheduled = false;
      if (!mounted) {
        return;
      }
      final orientation = MediaQuery.orientationOf(context);
      if (orientation == Orientation.landscape && !_fullscreenOpen) {
        _openFullscreenChart(auto: true);
      } else if (orientation == Orientation.portrait && _autoFullscreen) {
        _autoFullscreen = false;
        Navigator.of(context).pop();
        _fullscreenOpen = false;
      }
    });
  }

  Future<void> _openFullscreenChart({bool auto = false}) async {
    if (_fullscreenOpen) {
      return;
    }
    _fullscreenOpen = true;
    _autoFullscreen = auto;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => Scaffold(
          backgroundColor: const Color(0xFFF7F7F7),
          body: SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) => TradingViewWidget(
                symbol: widget.ticker,
                height: constraints.maxHeight,
              ),
            ),
          ),
        ),
      ),
    );
    _fullscreenOpen = false;
    _autoFullscreen = false;
  }

  @override
  Widget build(BuildContext context) {
    final quoteState = ref.watch(stockQuoteProvider(widget.ticker));
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.ticker, textDirection: TextDirection.ltr),
        actions: [
          IconButton(
            tooltip: 'تحديث',
            onPressed: quoteState.isLoading
                ? null
                : () => ref
                      .read(stockQuoteProvider(widget.ticker).notifier)
                      .refresh(),
            icon: quoteState.isLoading
                ? const SizedBox.square(
                    dimension: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: quoteState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => _ErrorView(
          error: error,
          onRetry: () => ref.invalidate(stockQuoteProvider(widget.ticker)),
        ),
        data: (quote) => _DetailContent(
          quote: quote,
          ticker: widget.ticker,
          onOpenFullscreen: _openFullscreenChart,
        ),
      ),
    );
  }
}

class _DetailContent extends ConsumerWidget {
  const _DetailContent({
    required this.quote,
    required this.ticker,
    required this.onOpenFullscreen,
  });

  final MarketQuote quote;
  final String ticker;
  final VoidCallback onOpenFullscreen;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _Header(quote: quote),
        ),
        const SizedBox(height: 12),
        _StatsRow(quote: quote),
        const SizedBox(height: 8),
        _AnnualRange(quote: quote),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _QuickActions(ticker: ticker, quote: quote),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  'الرسم البياني اللحظي',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              IconButton(
                tooltip: 'ملء الشاشة',
                onPressed: onOpenFullscreen,
                icon: const Icon(Icons.fullscreen_rounded),
                color: Theme.of(context).colorScheme.primary,
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        TradingViewWidget(symbol: ticker),
        const SizedBox(height: 8),
      ],
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.quote});

  final MarketQuote quote;

  @override
  Widget build(BuildContext context) {
    final isUp = (quote.changePercent ?? 0) > 0;
    final isDown = (quote.changePercent ?? 0) < 0;
    final accent = isUp
        ? Colors.green
        : isDown
        ? Colors.redAccent
        : Theme.of(context).colorScheme.primary;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    quote.description.isEmpty
                        ? quote.ticker
                        : quote.description,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                if (quote.sector != null)
                  Chip(
                    label: Text(quote.sector!),
                    labelStyle: Theme.of(context).textTheme.labelSmall,
                    visualDensity: VisualDensity.compact,
                  ),
              ],
            ),
            const SizedBox(height: 14),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  formatPrice(quote.currentPrice),
                  textDirection: TextDirection.ltr,
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.w900,
                    color: accent,
                  ),
                ),
                const SizedBox(width: 12),
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    formatChangePercent(quote.changePercent),
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: changeColor(context, quote.changePercent),
                    ),
                  ),
                ),
                const Spacer(),
                if (quote.volume != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'الحجم',
                          style: Theme.of(context).textTheme.bodySmall
                              ?.copyWith(
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                        ),
                        Text(
                          _formatVolume(quote.volume),
                          textDirection: TextDirection.ltr,
                          style: Theme.of(context).textTheme.titleSmall
                              ?.copyWith(fontWeight: FontWeight.w700),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _StatsRow extends StatelessWidget {
  const _StatsRow({required this.quote});

  final MarketQuote quote;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          _Stat(
            label: 'الفتح',
            value: formatPrice(quote.openPrice),
            color: Theme.of(context).colorScheme.onSurface,
          ),
          _Stat(
            label: 'سعر الإغلاق',
            value: formatPrice(quote.currentPrice),
            color: Theme.of(context).colorScheme.onSurface,
          ),
          _Stat(
            label: 'الأعلى',
            value: formatPrice(quote.sessionHigh ?? quote.week52High),
            color: Colors.green,
          ),
          _Stat(
            label: 'الأدنى',
            value: formatPrice(quote.sessionLow ?? quote.week52Low),
            color: Colors.redAccent,
          ),
        ],
      ),
    );
  }
}

class _AnnualRange extends StatelessWidget {
  const _AnnualRange({required this.quote});

  final MarketQuote quote;

  @override
  Widget build(BuildContext context) {
    final hasHigh = quote.week52High != null;
    final hasLow = quote.week52Low != null;
    if (!hasHigh && !hasLow) {
      return const SizedBox.shrink();
    }
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'النطاق السنوي (52 أسبوع)',
              style: Theme.of(
                context,
              ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _Stat(
                  label: 'أعلى سعر سنوي',
                  value: formatPrice(quote.week52High),
                  color: Colors.green,
                ),
                _Stat(
                  label: 'أدنى سعر سنوي',
                  value: formatPrice(quote.week52Low),
                  color: Colors.redAccent,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value, required this.color});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            textDirection: TextDirection.ltr,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _QuickActions extends ConsumerWidget {
  const _QuickActions({required this.ticker, required this.quote});

  final String ticker;
  final MarketQuote quote;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Row(
      children: [
        Expanded(
          child: FilledButton.icon(
            onPressed: () => context.push('/market/analyze/${quote.ticker}'),
            icon: const Icon(Icons.auto_graph_rounded),
            label: const Text('تحليل'),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => context.push('/market/compare'),
            icon: const Icon(Icons.compare_arrows_rounded),
            label: const Text('مقارنة'),
          ),
        ),
      ],
    );
  }
}

class TradingViewWidget extends StatefulWidget {
  const TradingViewWidget({super.key, required this.symbol, this.height = 420});

  final String symbol;
  final double height;
  final bool dark = false;

  @override
  State<TradingViewWidget> createState() => _TradingViewWidgetState();
}

class _TradingViewWidgetState extends State<TradingViewWidget> {
  late final WebViewController _controller;
  late final String _html;

  @override
  void initState() {
    super.initState();
    _html = _buildHtml();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFFFFFFF));
  }

  String _buildHtml() {
    final symbol = widget.symbol.toUpperCase();
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  html, body {
    margin: 0; padding: 0; height: 100%; background: #ffffff;
    font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  #tv { width: 100%; height: 100%; }
  body.loading #tv { visibility: hidden; }
  .center { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; }
  .spinner { width: 28px; height: 28px; border: 3px solid #e0e0e0; border-top-color: #1f6feb; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body class="loading">
<div class="center"><div class="spinner"></div></div>
<div id="tv"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
  new TradingView.widget({
    "container_id": "tv",
    "autosize": true,
    "width": "100%",
    "height": "100%",
    "symbol": "EGX:$symbol",
    "interval": "D",
    "timezone": "Africa/Cairo",
    "theme": "light",
    "style": "1",
    "locale": "ar_AE",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "hide_top_toolbar": false,
    "studies": ["Volume@tv-basicstudies"],
    "details": true,
    "hotlist": true,
    "calendar": false,
    "support_host": "https://www.tradingview.com"
  });
  function ready() {
    document.body.classList.remove('loading');
  }
  setTimeout(ready, 1200);
</script>
</body>
</html>
''';
  }

  @override
  void didUpdateWidget(covariant TradingViewWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.symbol != widget.symbol) {
      _html = _buildHtml();
      _controller
        ..loadHtmlString(_html)
        ..reload();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: widget.height,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            const Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(color: Color(0xFFF7F7F7)),
                child: Center(child: CircularProgressIndicator()),
              ),
            ),
            Positioned.fill(
              child: WebViewWidget(
                controller: _controller..loadHtmlString(_html),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 48),
            const SizedBox(height: 12),
            Text(
              error is ApiException
                  ? (error as ApiException).message
                  : 'تعذر تحميل بيانات السهم.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

String _formatVolume(double? value) {
  if (value == null) {
    return '—';
  }
  if (value >= 1000000) {
    return '${(value / 1000000).toStringAsFixed(2)}M';
  }
  if (value >= 1000) {
    return '${(value / 1000).toStringAsFixed(1)}K';
  }
  return value.toStringAsFixed(0);
}

```

---

### File: `lib\features\market\stock_quote_card.dart`

```dart
import 'package:flutter/material.dart';

import '../../domain/models.dart';

String formatPrice(double? value) {
  if (value == null) {
    return '—';
  }
  final text = value.toStringAsFixed(2);
  // Use Arabic-friendly rendering; the trailing zeros are intentional.
  return text;
}

String formatChangePercent(double? value) {
  if (value == null) {
    return '—';
  }
  final sign = value > 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(2)}%';
}

Color changeColor(BuildContext context, double? value) {
  if (value == null) {
    return Theme.of(context).colorScheme.onSurfaceVariant;
  }
  if (value > 0) {
    return Colors.green;
  }
  if (value < 0) {
    return Colors.redAccent;
  }
  return Theme.of(context).colorScheme.onSurfaceVariant;
}

class StockQuoteCard extends StatelessWidget {
  const StockQuoteCard({super.key, required this.quote, required this.onTap});

  final MarketQuote quote;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isUp = (quote.changePercent ?? 0) > 0;
    final isDown = (quote.changePercent ?? 0) < 0;
    final accent = isUp
        ? Colors.green
        : isDown
        ? Colors.redAccent
        : Theme.of(context).colorScheme.primary;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(
                        context,
                      ).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      quote.ticker,
                      textDirection: TextDirection.ltr,
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    isUp
                        ? Icons.trending_up_rounded
                        : isDown
                        ? Icons.trending_down_rounded
                        : Icons.trending_flat_rounded,
                    color: accent,
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                quote.description.isEmpty ? quote.ticker : quote.description,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 10),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    formatPrice(quote.currentPrice),
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: accent,
                    ),
                  ),
                  if (quote.volume != null) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _formatVolume(quote.volume),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 6),
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: Text(
                  formatChangePercent(quote.changePercent),
                  textDirection: TextDirection.ltr,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: changeColor(context, quote.changePercent),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatVolume(double? value) {
    if (value == null) {
      return '';
    }
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(1)}M';
    }
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}K';
    }
    return value.toStringAsFixed(0);
  }
}

```

---

### File: `lib\features\market\stocks_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'market_quotes_providers.dart';
import 'stock_quote_card.dart';

class StocksScreen extends ConsumerStatefulWidget {
  const StocksScreen({super.key});

  @override
  ConsumerState<StocksScreen> createState() => _StocksScreenState();
}

class _StocksScreenState extends ConsumerState<StocksScreen> {
  String _query = '';
  bool _showFallers = false;
  bool _showOnlyActive = false;

  @override
  Widget build(BuildContext context) {
    final snapshot = ref.watch(marketQuotesProvider).valueOrNull;
    final items = _visibleItems(snapshot);

    final header = snapshot == null
        ? null
        : QuoteSessionHeader(snapshot: snapshot);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(marketQuotesProvider);
        await ref.read(marketQuotesProvider.future);
      },
      child: Column(
        children: [
          if (header != null) header,
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
            child: TextField(
              textDirection: TextDirection.ltr,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search_rounded),
                hintText: 'بحث برمز السهم أو الاسم — COMI',
                isDense: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(14)),
                ),
              ),
              onChanged: (value) =>
                  setState(() => _query = value.trim().toUpperCase()),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
            child: Wrap(
              spacing: 8,
              runSpacing: 4,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                FilterChip(
                  label: const Text('الأكثر هبوطًا'),
                  selected: _showFallers,
                  onSelected: (value) => setState(() => _showFallers = value),
                ),
                FilterChip(
                  label: const Text('المتداولة فقط'),
                  selected: _showOnlyActive,
                  onSelected: (value) =>
                      setState(() => _showOnlyActive = value),
                ),
              ],
            ),
          ),
          Expanded(
            child: ref
                .watch(marketQuotesProvider)
                .when(
                  loading: () =>
                      const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => _ErrorView(
                    error: error,
                    onRetry: () => ref.invalidate(marketQuotesProvider),
                  ),
                  data: (_) => _buildGrid(context, items),
                ),
          ),
        ],
      ),
    );
  }

  List<MarketQuote> _visibleItems(MarketQuotesSnapshot? snapshot) {
    if (snapshot == null) {
      return const [];
    }
    final items = snapshot.items
        .where((quote) {
          if (_query.isNotEmpty) {
            final match =
                quote.ticker.contains(_query) ||
                quote.description.contains(_query);
            if (!match) {
              return false;
            }
          }
          if (_showOnlyActive && quote.currentPrice == null) {
            return false;
          }
          return true;
        })
        .toList(growable: false);

    items.sort((a, b) {
      if (_showFallers) {
        final aChange = a.changePercent ?? 0;
        final bChange = b.changePercent ?? 0;
        return aChange.compareTo(bChange);
      }
      return a.ticker.compareTo(b.ticker);
    });
    return items;
  }

  Widget _buildGrid(BuildContext context, List<MarketQuote> items) {
    if (items.isEmpty) {
      return ListView(
        padding: const EdgeInsets.all(24),
        children: const [
          Icon(Icons.search_off_rounded, size: 48),
          SizedBox(height: 12),
          Text(
            'لا توجد أسهم مطابقة للبحث الحالي.',
            textAlign: TextAlign.center,
          ),
        ],
      );
    }
    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 220,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.92,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final quote = items[index];
        return StockQuoteCard(
          quote: quote,
          onTap: () => context.push('/stocks/${quote.ticker}'),
        );
      },
    );
  }
}

class QuoteSessionHeader extends StatelessWidget {
  const QuoteSessionHeader({super.key, required this.snapshot});

  final MarketQuotesSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final open = snapshot.marketOpen;
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: open
              ? [
                  Theme.of(context).colorScheme.primaryContainer,
                  Theme.of(context).colorScheme.primary.withValues(alpha: 0.4),
                ]
              : [
                  Theme.of(context).colorScheme.surfaceContainerHigh,
                  Theme.of(context).colorScheme.surfaceContainerLow,
                ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(
            open
                ? Icons.show_chart_rounded
                : Icons.pause_circle_outline_rounded,
            size: 34,
            color: open
                ? Colors.green
                : Theme.of(context).colorScheme.onSurface,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  open ? 'السوق مفتوح الآن' : 'السوق مغلق',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  _subtitle(context, open),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          if (snapshot.items.isNotEmpty)
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${snapshot.items.length} سهم',
                  style: Theme.of(
                    context,
                  ).textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 2),
                Text(
                  'تحديث كل ${marketQuotesPollInterval.inSeconds} ث',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  String _subtitle(BuildContext context, bool open) {
    final next = snapshot.nextSessionOpen;
    if (next == null) {
      return open ? 'التداول جارٍ' : 'سيُفتح السوق قريبًا';
    }
    if (open) {
      final now = DateTime.now();
      final diff = next.difference(now);
      if (diff.isNegative) {
        return 'سيغلق السوق في نهاية الجلسة.';
      }
      final minutes = diff.inMinutes.remainder(60);
      final hours = diff.inHours;
      return 'باقي على إغلاق السوق '
          '${hours > 0 ? '$hours س ' : ''}$minutes د';
    }
    return 'باقي على فتح السوق '
        '${_untilOpen(next)}';
  }

  String _untilOpen(DateTime next) {
    final now = DateTime.now();
    final diff = next.difference(now);
    if (diff.isNegative) {
      return 'قريبًا';
    }
    final minutes = diff.inMinutes.remainder(60);
    final hours = diff.inHours;
    return '${hours > 0 ? '$hours س ' : ''}$minutes د';
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 48),
            const SizedBox(height: 12),
            Text(
              error is ApiException
                  ? (error as ApiException).message
                  : 'تعذر تحميل أسعار السوق.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\monetization\free_plan_ads.dart`

```dart
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/config/app_config.dart';
import '../auth/session_controller.dart';
import 'plan_banner_ad.dart';

class FreePlanAdShell extends ConsumerWidget {
  const FreePlanAdShell({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(sessionControllerProvider).profile;
    final enabled = profile?.adsEnabled == true;
    return Column(
      children: [
        Expanded(child: child),
        PlanBannerAd(enabled: enabled),
      ],
    );
  }
}

class FreePlanNativeAd extends ConsumerStatefulWidget {
  const FreePlanNativeAd({this.enabledOverride, super.key});

  final bool? enabledOverride;

  @override
  ConsumerState<FreePlanNativeAd> createState() => _FreePlanNativeAdState();
}

class _FreePlanNativeAdState extends ConsumerState<FreePlanNativeAd> {
  NativeAd? _ad;
  bool _loaded = false;
  String? _activeAdUnitId;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncAd();
  }

  @override
  void didUpdateWidget(covariant FreePlanNativeAd oldWidget) {
    super.didUpdateWidget(oldWidget);
    _syncAd();
  }

  void _syncAd() {
    final profile = ref.read(sessionControllerProvider).profile;
    final enabled = widget.enabledOverride ?? profile?.adsEnabled == true;
    if (!enabled || !(Platform.isAndroid || Platform.isIOS)) {
      _disposeAd();
      return;
    }

    final config = ref.read(appConfigProvider);
    final adUnitId = Platform.isAndroid
        ? config.admobAndroidNativeId
        : config.admobIosNativeId;
    if (adUnitId.isEmpty || (_ad != null && _activeAdUnitId == adUnitId)) {
      return;
    }

    _disposeAd();
    _activeAdUnitId = adUnitId;
    final ad = NativeAd(
      adUnitId: adUnitId,
      request: const AdRequest(),
      listener: NativeAdListener(
        onAdLoaded: (loadedAd) {
          if (!mounted || loadedAd != _ad) {
            loadedAd.dispose();
            return;
          }
          setState(() => _loaded = true);
        },
        onAdFailedToLoad: (failedAd, error) {
          failedAd.dispose();
          if (mounted && failedAd == _ad) {
            setState(() {
              _ad = null;
              _loaded = false;
            });
          }
        },
      ),
      nativeTemplateStyle: NativeTemplateStyle(
        templateType: TemplateType.small,
        cornerRadius: 14,
      ),
    );
    _ad = ad;
    ad.load();
  }

  void _disposeAd() {
    final ad = _ad;
    _ad = null;
    _loaded = false;
    _activeAdUnitId = null;
    ad?.dispose();
  }

  @override
  void dispose() {
    _disposeAd();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ad = _ad;
    if (!_loaded || ad == null) {
      return const SizedBox.shrink();
    }
    return Semantics(
      label: 'إعلان مدمج',
      child: Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(8, 6, 8, 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('إعلان', style: Theme.of(context).textTheme.labelSmall),
              const SizedBox(height: 4),
              ConstrainedBox(
                constraints: const BoxConstraints(
                  minWidth: 320,
                  minHeight: 90,
                  maxHeight: 200,
                ),
                child: AdWidget(ad: ad),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class InterstitialFrequencyPolicy {
  const InterstitialFrequencyPolicy({
    this.actionsPerAd = 3,
    this.minimumInterval = const Duration(minutes: 4),
  });

  final int actionsPerAd;
  final Duration minimumInterval;

  bool canShow({
    required int meaningfulActions,
    required DateTime now,
    required DateTime? lastShownAt,
  }) {
    if (meaningfulActions < actionsPerAd) {
      return false;
    }
    if (lastShownAt == null) {
      return true;
    }
    return now.difference(lastShownAt) >= minimumInterval;
  }
}

class FreePlanInterstitialCoordinator {
  FreePlanInterstitialCoordinator({
    required AppConfig config,
    InterstitialFrequencyPolicy policy = const InterstitialFrequencyPolicy(),
  }) : _config = config,
       _policy = policy;

  final AppConfig _config;
  final InterstitialFrequencyPolicy _policy;
  InterstitialAd? _ad;
  bool _loading = false;
  int _meaningfulActions = 0;
  DateTime? _lastShownAt;

  Future<void> recordMeaningfulAction({required bool enabled}) async {
    if (!enabled || !(Platform.isAndroid || Platform.isIOS)) {
      return;
    }
    _meaningfulActions += 1;
    _loadIfNeeded();

    final now = DateTime.now();
    if (!_policy.canShow(
      meaningfulActions: _meaningfulActions,
      now: now,
      lastShownAt: _lastShownAt,
    )) {
      return;
    }

    final ad = _ad;
    if (ad == null) {
      return;
    }
    _ad = null;
    _meaningfulActions = 0;
    _lastShownAt = now;
    ad.fullScreenContentCallback = FullScreenContentCallback<InterstitialAd>(
      onAdDismissedFullScreenContent: (closedAd) {
        closedAd.dispose();
        _loadIfNeeded();
      },
      onAdFailedToShowFullScreenContent: (failedAd, error) {
        failedAd.dispose();
        _loadIfNeeded();
      },
    );
    await ad.show();
  }

  void preload({required bool enabled}) {
    if (enabled) {
      _loadIfNeeded();
    }
  }

  void _loadIfNeeded() {
    if (_loading || _ad != null || !(Platform.isAndroid || Platform.isIOS)) {
      return;
    }
    final adUnitId = Platform.isAndroid
        ? _config.admobAndroidInterstitialId
        : _config.admobIosInterstitialId;
    if (adUnitId.isEmpty) {
      return;
    }
    _loading = true;
    InterstitialAd.load(
      adUnitId: adUnitId,
      request: const AdRequest(),
      adLoadCallback: InterstitialAdLoadCallback(
        onAdLoaded: (ad) {
          _loading = false;
          _ad = ad;
        },
        onAdFailedToLoad: (error) {
          _loading = false;
        },
      ),
    );
  }

  void dispose() {
    _ad?.dispose();
    _ad = null;
  }
}

final freePlanInterstitialProvider = Provider<FreePlanInterstitialCoordinator>((
  ref,
) {
  final coordinator = FreePlanInterstitialCoordinator(
    config: ref.watch(appConfigProvider),
  );
  ref.onDispose(coordinator.dispose);
  return coordinator;
});

```

---

### File: `lib\features\monetization\monetization_controller.dart`

```dart
import 'dart:async';
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:in_app_purchase/in_app_purchase.dart';

import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'monetization_models.dart';
import 'monetization_repository.dart';
import 'rewarded_ad_gateway.dart';

const _unset = Object();

class MonetizationState {
  const MonetizationState({
    this.loading = true,
    this.storeAvailable = false,
    this.catalog,
    this.status,
    this.products = const <String, ProductDetails>{},
    this.adBusy = false,
    this.purchasingProductId,
    this.message,
    this.error,
  });

  final bool loading;
  final bool storeAvailable;
  final MonetizationCatalog? catalog;
  final MonetizationStatusModel? status;
  final Map<String, ProductDetails> products;
  final bool adBusy;
  final String? purchasingProductId;
  final String? message;
  final String? error;

  MonetizationState copyWith({
    bool? loading,
    bool? storeAvailable,
    Object? catalog = _unset,
    Object? status = _unset,
    Map<String, ProductDetails>? products,
    bool? adBusy,
    Object? purchasingProductId = _unset,
    Object? message = _unset,
    Object? error = _unset,
  }) {
    return MonetizationState(
      loading: loading ?? this.loading,
      storeAvailable: storeAvailable ?? this.storeAvailable,
      catalog: identical(catalog, _unset)
          ? this.catalog
          : catalog as MonetizationCatalog?,
      status: identical(status, _unset)
          ? this.status
          : status as MonetizationStatusModel?,
      products: products ?? this.products,
      adBusy: adBusy ?? this.adBusy,
      purchasingProductId: identical(purchasingProductId, _unset)
          ? this.purchasingProductId
          : purchasingProductId as String?,
      message: identical(message, _unset) ? this.message : message as String?,
      error: identical(error, _unset) ? this.error : error as String?,
    );
  }
}

class MonetizationController extends StateNotifier<MonetizationState> {
  MonetizationController({
    required MonetizationRepository repository,
    required InAppPurchase store,
    required RewardedAdGateway rewardedAdGateway,
    required Future<void> Function() onEntitlementChanged,
  }) : _repository = repository,
       _store = store,
       _rewardedAdGateway = rewardedAdGateway,
       _onEntitlementChanged = onEntitlementChanged,
       super(const MonetizationState()) {
    _purchaseSubscription = _store.purchaseStream.listen(
      _handlePurchaseUpdates,
      onError: _handlePurchaseStreamError,
    );
    unawaited(refresh());
  }

  final MonetizationRepository _repository;
  final InAppPurchase _store;
  final RewardedAdGateway _rewardedAdGateway;
  final Future<void> Function() _onEntitlementChanged;
  late final StreamSubscription<List<PurchaseDetails>> _purchaseSubscription;

  Future<void> refresh() async {
    state = state.copyWith(loading: true, error: null, message: null);
    try {
      final results = await Future.wait<Object>([
        _repository.getCatalog(),
        _repository.getStatus(),
      ]);
      final catalog = results[0] as MonetizationCatalog;
      final status = results[1] as MonetizationStatusModel;
      final storeAvailable = Platform.isAndroid && await _store.isAvailable();
      var products = const <String, ProductDetails>{};
      if (storeAvailable && catalog.storeProductIds.isNotEmpty) {
        final response = await _store.queryProductDetails(
          catalog.storeProductIds,
        );
        products = <String, ProductDetails>{
          for (final product in response.productDetails) product.id: product,
        };
        if (response.error != null) {
          state = state.copyWith(
            message: 'تعذر تحميل بعض أسعار Google Play حاليًا.',
          );
        }
      }
      if (mounted) {
        state = state.copyWith(
          loading: false,
          storeAvailable: storeAvailable,
          catalog: catalog,
          status: status,
          products: products,
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(loading: false, error: error.toString());
      }
    }
  }

  Future<void> showRewardedAd() async {
    final status = state.status;
    if (state.adBusy || status == null || !status.rewardedAd.eligible) {
      return;
    }
    final platform = Platform.isAndroid
        ? 'android'
        : Platform.isIOS
        ? 'ios'
        : null;
    if (platform == null) {
      state = state.copyWith(error: 'الإعلانات متاحة على Android وiOS فقط.');
      return;
    }

    state = state.copyWith(adBusy: true, error: null, message: null);
    try {
      final beforeCount = status.rewardedAd.rewardsUsedToday;
      final session = await _repository.createRewardedAdSession(
        platform: platform,
      );
      final watched = await _rewardedAdGateway.loadAndShow(session);
      if (!watched) {
        state = state.copyWith(
          adBusy: false,
          message: 'لم يكتمل الإعلان، لذلك لم تُضف أي عملات.',
        );
        return;
      }

      if (session.testMode) {
        await _repository.simulateRewardedAd(session: session);
      }
      final verified = await _waitForReward(beforeCount);
      await _onEntitlementChanged();
      if (mounted) {
        state = state.copyWith(
          adBusy: false,
          message: verified
              ? 'تم التحقق من الإعلان وإضافة المكافأة إلى المحفظة.'
              : 'اكتمل الإعلان، والتحقق من Google ما زال قيد المعالجة. حدّث الصفحة بعد قليل.',
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(adBusy: false, error: error.toString());
      }
    }
  }

  Future<void> purchaseProduct(String productId) async {
    if (state.purchasingProductId != null) {
      return;
    }
    if (!Platform.isAndroid) {
      state = state.copyWith(
        error: 'المشتريات في هذه المرحلة مرتبطة بـGoogle Play على Android.',
      );
      return;
    }
    final catalog = state.catalog;
    final product = state.products[productId];
    if (catalog == null || product == null) {
      state = state.copyWith(error: 'المنتج غير متاح في Google Play حاليًا.');
      return;
    }

    state = state.copyWith(
      purchasingProductId: productId,
      error: null,
      message: null,
    );
    final purchaseParam = PurchaseParam(productDetails: product);
    try {
      final started = catalog.isCoinPack(productId)
          ? await _store.buyConsumable(
              purchaseParam: purchaseParam,
              autoConsume: false,
            )
          : await _store.buyNonConsumable(purchaseParam: purchaseParam);
      if (!started && mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: 'لم يبدأ طلب الشراء من Google Play.',
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: error.toString(),
        );
      }
    }
  }

  Future<void> restorePurchases() async {
    if (!Platform.isAndroid || !state.storeAvailable) {
      state = state.copyWith(
        error: 'استعادة المشتريات غير متاحة على هذا الجهاز.',
      );
      return;
    }
    state = state.copyWith(message: 'جارٍ استعادة مشتريات Google Play...');
    try {
      await _store.restorePurchases();
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(error: error.toString());
      }
    }
  }

  Future<bool> _waitForReward(int beforeCount) async {
    for (var attempt = 0; attempt < 7; attempt += 1) {
      final current = await _repository.getStatus();
      if (!mounted) {
        return false;
      }
      state = state.copyWith(status: current);
      if (current.rewardedAd.rewardsUsedToday > beforeCount) {
        return true;
      }
      await Future<void>.delayed(const Duration(seconds: 2));
    }
    return false;
  }

  Future<void> _handlePurchaseUpdates(List<PurchaseDetails> purchases) async {
    for (final purchase in purchases) {
      switch (purchase.status) {
        case PurchaseStatus.pending:
          if (mounted) {
            state = state.copyWith(
              purchasingProductId: purchase.productID,
              message: 'عملية الشراء معلّقة لدى Google Play.',
            );
          }
          break;
        case PurchaseStatus.error:
          if (mounted) {
            state = state.copyWith(
              purchasingProductId: null,
              error: purchase.error?.message ?? 'فشلت عملية الشراء.',
            );
          }
          break;
        case PurchaseStatus.canceled:
          if (mounted) {
            state = state.copyWith(
              purchasingProductId: null,
              message: 'تم إلغاء عملية الشراء.',
            );
          }
          break;
        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          await _verifyAndComplete(purchase);
          break;
      }
    }
  }

  Future<void> _verifyAndComplete(PurchaseDetails purchase) async {
    if (!Platform.isAndroid) {
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: 'التحقق الحالي يدعم مشتريات Google Play فقط.',
        );
      }
      return;
    }
    final purchaseToken = purchase.verificationData.serverVerificationData;
    if (purchaseToken.isEmpty) {
      state = state.copyWith(
        purchasingProductId: null,
        error: 'Google Play لم يرجع رمز تحقق صالحًا.',
      );
      return;
    }

    try {
      final result = await _repository.verifyGooglePlayPurchase(
        productId: purchase.productID,
        purchaseToken: purchaseToken,
      );
      if (!result.entitlementGranted) {
        throw StateError('السيرفر لم يؤكد استحقاق المنتج.');
      }
      if (purchase.pendingCompletePurchase) {
        await _store.completePurchase(purchase);
      }
      await _onEntitlementChanged();
      final updatedStatus = await _repository.getStatus();
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          status: updatedStatus,
          message: result.idempotent
              ? 'تمت استعادة الاستحقاق المسجل سابقًا.'
              : 'تم التحقق من الشراء وتحديث حسابك بنجاح.',
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: error.toString(),
        );
      }
    }
  }

  void _handlePurchaseStreamError(Object error) {
    if (mounted) {
      state = state.copyWith(
        purchasingProductId: null,
        error: error.toString(),
      );
    }
  }

  @override
  void dispose() {
    unawaited(_purchaseSubscription.cancel());
    super.dispose();
  }
}

final inAppPurchaseProvider = Provider<InAppPurchase>((ref) {
  return InAppPurchase.instance;
});

final rewardedAdGatewayProvider = Provider<RewardedAdGateway>((ref) {
  return const GoogleRewardedAdGateway();
});

final monetizationControllerProvider =
    StateNotifierProvider.autoDispose<
      MonetizationController,
      MonetizationState
    >((ref) {
      return MonetizationController(
        repository: ref.watch(monetizationRepositoryProvider),
        store: ref.watch(inAppPurchaseProvider),
        rewardedAdGateway: ref.watch(rewardedAdGatewayProvider),
        onEntitlementChanged: () async {
          ref.invalidate(walletSummaryProvider);
          await ref.read(sessionControllerProvider.notifier).refreshProfile();
        },
      );
    });

```

---

### File: `lib\features\monetization\monetization_models.dart`

```dart
class MonetizationPlan {
  const MonetizationPlan({
    required this.code,
    required this.displayNameAr,
    required this.weeklyPoints,
    required this.weeklyCoins,
    required this.adsEnabled,
    required this.productId,
    required this.historyLimit,
    required this.reportHistoryDays,
    required this.features,
    required this.comparisonMonthlyAllowance,
    required this.maxComparisonStocks,
    required this.priorityLevel,
    required this.badgeCode,
  });

  final String code;
  final String displayNameAr;
  final int weeklyPoints;
  final String weeklyCoins;
  final bool adsEnabled;
  final String? productId;
  final int historyLimit;
  final int reportHistoryDays;
  final List<String> features;
  final int comparisonMonthlyAllowance;
  final int maxComparisonStocks;
  final int priorityLevel;
  final String? badgeCode;

  factory MonetizationPlan.fromJson(Map<String, dynamic> json) {
    return MonetizationPlan(
      code: json['code'] as String,
      displayNameAr: json['display_name_ar'] as String,
      weeklyPoints: json['weekly_points'] as int,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
      productId: json['product_id'] as String?,
      historyLimit: json['history_limit'] as int,
      reportHistoryDays: json['report_history_days'] as int,
      features: _list(
        json['features'],
      ).map((value) => value.toString()).toList(growable: false),
      comparisonMonthlyAllowance:
          json['comparison_monthly_allowance'] as int? ?? 0,
      maxComparisonStocks: json['max_comparison_stocks'] as int? ?? 0,
      priorityLevel: json['priority_level'] as int? ?? 0,
      badgeCode: json['badge_code'] as String?,
    );
  }
}

class CoinPack {
  const CoinPack({
    required this.productId,
    required this.displayNameAr,
    required this.points,
    required this.coins,
  });

  final String productId;
  final String displayNameAr;
  final int points;
  final String coins;

  factory CoinPack.fromJson(Map<String, dynamic> json) {
    return CoinPack(
      productId: json['product_id'] as String,
      displayNameAr: json['display_name_ar'] as String,
      points: json['points'] as int,
      coins: json['coins'] as String,
    );
  }
}

class MonetizationCatalog {
  const MonetizationCatalog({
    required this.plans,
    required this.coinPacks,
    required this.adRewardPoints,
    required this.adRewardCoins,
    required this.adRewardDailyLimit,
    required this.adRewardCooldownSeconds,
  });

  final List<MonetizationPlan> plans;
  final List<CoinPack> coinPacks;
  final int adRewardPoints;
  final String adRewardCoins;
  final int adRewardDailyLimit;
  final int adRewardCooldownSeconds;

  Set<String> get storeProductIds => <String>{
    ...plans.map((plan) => plan.productId).whereType<String>(),
    ...coinPacks.map((pack) => pack.productId),
  };

  bool isCoinPack(String productId) {
    return coinPacks.any((pack) => pack.productId == productId);
  }

  factory MonetizationCatalog.fromJson(Map<String, dynamic> json) {
    return MonetizationCatalog(
      plans: _list(json['plans'])
          .map((value) => MonetizationPlan.fromJson(_map(value)))
          .toList(growable: false),
      coinPacks: _list(
        json['coin_packs'],
      ).map((value) => CoinPack.fromJson(_map(value))).toList(growable: false),
      adRewardPoints: json['ad_reward_points'] as int,
      adRewardCoins: json['ad_reward_coins'] as String,
      adRewardDailyLimit: json['ad_reward_daily_limit'] as int,
      adRewardCooldownSeconds: json['ad_reward_cooldown_seconds'] as int,
    );
  }
}

class RewardedAdEligibilityModel {
  const RewardedAdEligibilityModel({
    required this.eligible,
    required this.reason,
    required this.rewardsUsedToday,
    required this.rewardsRemainingToday,
    required this.nextAvailableAt,
  });

  final bool eligible;
  final String? reason;
  final int rewardsUsedToday;
  final int rewardsRemainingToday;
  final DateTime? nextAvailableAt;

  factory RewardedAdEligibilityModel.fromJson(Map<String, dynamic> json) {
    return RewardedAdEligibilityModel(
      eligible: json['eligible'] as bool,
      reason: json['reason'] as String?,
      rewardsUsedToday: json['rewards_used_today'] as int,
      rewardsRemainingToday: json['rewards_remaining_today'] as int,
      nextAvailableAt: json['next_available_at'] == null
          ? null
          : DateTime.parse(json['next_available_at'] as String),
    );
  }
}

class MonetizationStatusModel {
  const MonetizationStatusModel({
    required this.planCode,
    required this.subscriptionStatus,
    required this.subscriptionExpiresAt,
    required this.weeklyPoints,
    required this.weeklyCoins,
    required this.adsEnabled,
    required this.rewardedAd,
  });

  final String planCode;
  final String subscriptionStatus;
  final DateTime? subscriptionExpiresAt;
  final int weeklyPoints;
  final String weeklyCoins;
  final bool adsEnabled;
  final RewardedAdEligibilityModel rewardedAd;

  factory MonetizationStatusModel.fromJson(Map<String, dynamic> json) {
    return MonetizationStatusModel(
      planCode: json['plan_code'] as String,
      subscriptionStatus: json['subscription_status'] as String,
      subscriptionExpiresAt: json['subscription_expires_at'] == null
          ? null
          : DateTime.parse(json['subscription_expires_at'] as String),
      weeklyPoints: json['weekly_points'] as int,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
      rewardedAd: RewardedAdEligibilityModel.fromJson(
        _map(json['rewarded_ad']),
      ),
    );
  }
}

class RewardedAdSessionModel {
  const RewardedAdSessionModel({
    required this.sessionId,
    required this.adUnitId,
    required this.customData,
    required this.expiresAt,
    required this.testMode,
  });

  final String sessionId;
  final String adUnitId;
  final String customData;
  final DateTime expiresAt;
  final bool testMode;

  factory RewardedAdSessionModel.fromJson(Map<String, dynamic> json) {
    return RewardedAdSessionModel(
      sessionId: json['session_id'] as String,
      adUnitId: json['ad_unit_id'] as String,
      customData: json['custom_data'] as String,
      expiresAt: DateTime.parse(json['expires_at'] as String),
      testMode: json['test_mode'] as bool? ?? false,
    );
  }
}

class RewardedAdSimulationResultModel {
  const RewardedAdSimulationResultModel({
    required this.idempotent,
    required this.balancePoints,
    required this.balanceCoins,
  });

  final bool idempotent;
  final int balancePoints;
  final String balanceCoins;

  factory RewardedAdSimulationResultModel.fromJson(Map<String, dynamic> json) {
    return RewardedAdSimulationResultModel(
      idempotent: json['idempotent'] as bool,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
    );
  }
}

class PurchaseVerificationResultModel {
  const PurchaseVerificationResultModel({
    required this.purchaseId,
    required this.productId,
    required this.productType,
    required this.purchaseState,
    required this.acknowledgementState,
    required this.entitlementGranted,
    required this.idempotent,
    required this.planCode,
    required this.balancePoints,
    required this.balanceCoins,
    required this.subscriptionExpiresAt,
  });

  final String purchaseId;
  final String productId;
  final String productType;
  final String purchaseState;
  final String acknowledgementState;
  final bool entitlementGranted;
  final bool idempotent;
  final String planCode;
  final int balancePoints;
  final String balanceCoins;
  final DateTime? subscriptionExpiresAt;

  factory PurchaseVerificationResultModel.fromJson(Map<String, dynamic> json) {
    return PurchaseVerificationResultModel(
      purchaseId: json['purchase_id'] as String,
      productId: json['product_id'] as String,
      productType: json['product_type'] as String,
      purchaseState: json['purchase_state'] as String,
      acknowledgementState: json['acknowledgement_state'] as String,
      entitlementGranted: json['entitlement_granted'] as bool,
      idempotent: json['idempotent'] as bool,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      subscriptionExpiresAt: json['subscription_expires_at'] == null
          ? null
          : DateTime.parse(json['subscription_expires_at'] as String),
    );
  }
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

List<dynamic> _list(Object? value) {
  return value is List ? value : const <dynamic>[];
}

```

---

### File: `lib\features\monetization\monetization_page.dart`

```dart
import 'package:flutter/material.dart';

import 'monetization_screen.dart';

class MonetizationPage extends StatelessWidget {
  const MonetizationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const MonetizationScreen();
  }
}

```

---

### File: `lib\features\monetization\monetization_repository.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'monetization_models.dart';

class MonetizationRepository {
  const MonetizationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<MonetizationCatalog> getCatalog() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/monetization/catalog',
      );
      return MonetizationCatalog.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MonetizationStatusModel> getStatus() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/monetization/status',
      );
      return MonetizationStatusModel.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<RewardedAdSessionModel> createRewardedAdSession({
    required String platform,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/rewarded-ads/session',
        data: <String, dynamic>{'platform': platform},
      );
      return RewardedAdSessionModel.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<RewardedAdSimulationResultModel> simulateRewardedAd({
    required RewardedAdSessionModel session,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/rewarded-ads/sessions/${session.sessionId}/simulate',
        data: <String, dynamic>{'custom_data': session.customData},
      );
      return RewardedAdSimulationResultModel.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PurchaseVerificationResultModel> verifyGooglePlayPurchase({
    required String productId,
    required String purchaseToken,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/google-play/purchases/verify',
        data: <String, dynamic>{
          'product_id': productId,
          'purchase_token': purchaseToken,
        },
      );
      return PurchaseVerificationResultModel.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _requiredData(Map<String, dynamic>? data) {
    if (data == null) {
      throw StateError('Monetization response is empty.');
    }
    return data;
  }
}

final monetizationRepositoryProvider = Provider<MonetizationRepository>((ref) {
  return MonetizationRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\monetization\monetization_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'monetization_controller.dart';
import 'monetization_models.dart';

class MonetizationScreen extends ConsumerWidget {
  const MonetizationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(monetizationControllerProvider);
    final controller = ref.read(monetizationControllerProvider.notifier);
    final catalog = state.catalog;
    final status = state.status;

    return Scaffold(
      appBar: AppBar(
        title: const Text('الخطط والعملات'),
        actions: [
          IconButton(
            onPressed: state.loading ? null : controller.refresh,
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: state.loading && catalog == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: controller.refresh,
              child: ListView(
                padding: const EdgeInsets.all(18),
                children: [
                  if (state.error case final error?)
                    _NoticeCard(message: _cleanError(error), isError: true),
                  if (state.message case final message?)
                    _NoticeCard(message: message),
                  if (status != null) _CurrentPlanCard(status: status),
                  const SizedBox(height: 18),
                  if (catalog != null && status != null)
                    _RewardedAdCard(
                      catalog: catalog,
                      status: status,
                      busy: state.adBusy,
                      onPressed: controller.showRewardedAd,
                    ),
                  const SizedBox(height: 24),
                  Text(
                    'خطط الاشتراك',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 10),
                  if (catalog != null)
                    for (final plan in catalog.plans)
                      _PlanCard(
                        plan: plan,
                        currentPlanCode: status?.planCode,
                        price: plan.productId == null
                            ? 'مجانية'
                            : state.products[plan.productId]?.price ??
                                  'غير متاح حاليًا',
                        storeAvailable: state.storeAvailable,
                        busy:
                            plan.productId != null &&
                            state.purchasingProductId == plan.productId,
                        onPurchase: plan.productId == null
                            ? null
                            : () => controller.purchaseProduct(plan.productId!),
                      ),
                  const SizedBox(height: 24),
                  Text(
                    'باقات العملات',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'العملات المشتراة تُضاف بعد تحقق السيرفر من Google Play فقط.',
                  ),
                  const SizedBox(height: 10),
                  if (catalog != null)
                    for (final pack in catalog.coinPacks)
                      _CoinPackCard(
                        pack: pack,
                        price:
                            state.products[pack.productId]?.price ??
                            'غير متاح حاليًا',
                        storeAvailable: state.storeAvailable,
                        busy: state.purchasingProductId == pack.productId,
                        onPurchase: () =>
                            controller.purchaseProduct(pack.productId),
                      ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: state.storeAvailable
                        ? controller.restorePurchases
                        : null,
                    icon: const Icon(Icons.restore_rounded),
                    label: const Text('استعادة مشتريات Google Play'),
                  ),
                  const SizedBox(height: 14),
                  const _SecurityNote(),
                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }
}

class _CurrentPlanCard extends StatelessWidget {
  const _CurrentPlanCard({required this.status});

  final MonetizationStatusModel status;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Icon(
                Icons.workspace_premium_rounded,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('خطتك الحالية'),
                  Text(
                    _planName(status.planCode),
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  Text('${status.weeklyCoins} عملة أسبوعيًا'),
                  Text(
                    status.adsEnabled
                        ? 'تتضمن إعلانات اختيارية ومكافآت'
                        : 'بدون إعلانات',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RewardedAdCard extends StatelessWidget {
  const _RewardedAdCard({
    required this.catalog,
    required this.status,
    required this.busy,
    required this.onPressed,
  });

  final MonetizationCatalog catalog;
  final MonetizationStatusModel status;
  final bool busy;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final eligibility = status.rewardedAd;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.ondemand_video_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'شاهد إعلانًا واحصل على ${catalog.adRewardCoins} عملة',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              'المتبقي اليوم: ${eligibility.rewardsRemainingToday} من ${catalog.adRewardDailyLimit}',
            ),
            if (!eligibility.eligible) ...[
              const SizedBox(height: 6),
              Text(
                _eligibilityMessage(eligibility),
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: eligibility.eligible && !busy ? onPressed : null,
              icon: busy
                  ? const SizedBox.square(
                      dimension: 19,
                      child: CircularProgressIndicator(strokeWidth: 2.5),
                    )
                  : const Icon(Icons.play_arrow_rounded),
              label: Text(busy ? 'جارٍ تجهيز الإعلان...' : 'مشاهدة الإعلان'),
            ),
            const SizedBox(height: 8),
            const Text(
              'لا تُضاف المكافأة من الهاتف؛ السيرفر ينتظر تحقق AdMob أولًا.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  const _PlanCard({
    required this.plan,
    required this.currentPlanCode,
    required this.price,
    required this.storeAvailable,
    required this.busy,
    required this.onPurchase,
  });

  final MonetizationPlan plan;
  final String? currentPlanCode;
  final String price;
  final bool storeAvailable;
  final bool busy;
  final VoidCallback? onPurchase;

  @override
  Widget build(BuildContext context) {
    final current = plan.code == currentPlanCode;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    plan.displayNameAr,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                if (current) const Chip(label: Text('الخطة الحالية')),
              ],
            ),
            Text('${plan.weeklyCoins} عملة أسبوعيًا'),
            Text(plan.adsEnabled ? 'مع الإعلانات' : 'بدون إعلانات'),
            Text('سجل التقارير: ${plan.reportHistoryDays} يوم'),
            if (plan.maxComparisonStocks > 0)
              Text('مقارنة حتى ${plan.maxComparisonStocks} أسهم'),
            if (plan.comparisonMonthlyAllowance > 0)
              Text('${plan.comparisonMonthlyAllowance} مقارنة متضمنة شهريًا'),
            if (plan.features.isNotEmpty) ...[
              const SizedBox(height: 12),
              for (final feature in plan.features)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.check_circle_outline_rounded,
                        size: 18,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(feature)),
                    ],
                  ),
                ),
            ],
            const SizedBox(height: 12),
            FilledButton.tonal(
              onPressed:
                  current || onPurchase == null || !storeAvailable || busy
                  ? null
                  : onPurchase,
              child: Text(
                busy
                    ? 'جارٍ فتح Google Play...'
                    : current
                    ? 'مفعّلة'
                    : price,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CoinPackCard extends StatelessWidget {
  const _CoinPackCard({
    required this.pack,
    required this.price,
    required this.storeAvailable,
    required this.busy,
    required this.onPurchase,
  });

  final CoinPack pack;
  final String price;
  final bool storeAvailable;
  final bool busy;
  final VoidCallback onPurchase;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            const CircleAvatar(child: Icon(Icons.monetization_on_rounded)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    pack.displayNameAr,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '$price — ${pack.points} نقطة',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 14),
            busy
                ? const SizedBox.square(
                    dimension: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.5),
                  )
                : FilledButton(
                    onPressed: storeAvailable ? onPurchase : null,
                    child: const Text('شراء'),
                  ),
          ],
        ),
      ),
    );
  }
}

class _NoticeCard extends StatelessWidget {
  const _NoticeCard({required this.message, this.isError = false});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: isError ? Theme.of(context).colorScheme.errorContainer : null,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Text(message, textAlign: TextAlign.center),
      ),
    );
  }
}

class _SecurityNote extends StatelessWidget {
  const _SecurityNote();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.verified_user_outlined,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Text(
                'Google Play وAdMob لا يغيّران رصيدك مباشرة من التطبيق. كل عملية تُراجع على السيرفر، وتُسجل بمعرف فريد لمنع التكرار.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

String _planName(String code) {
  return switch (code) {
    'free' => 'المجانية',
    'basic' => 'الأساسية',
    'advanced' => 'المتقدمة',
    'pro' => 'الاحترافية',
    _ => code,
  };
}

String _eligibilityMessage(RewardedAdEligibilityModel eligibility) {
  return switch (eligibility.reason) {
    'subscription_without_ads' => 'خطتك الحالية بدون إعلانات.',
    'daily_limit_reached' => 'وصلت للحد اليومي لمكافآت الإعلانات.',
    'cooldown_active' => 'انتظر قليلًا قبل مشاهدة إعلان جديد.',
    'verification_disabled' => 'التحقق من الإعلانات غير مفعّل على السيرفر.',
    _ => 'الإعلان غير متاح حاليًا.',
  };
}

String _cleanError(String value) {
  return value
      .replaceFirst('ApiException: ', '')
      .replaceFirst('Bad state: ', '');
}

```

---

### File: `lib\features\monetization\plan_banner_ad.dart`

```dart
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/config/app_config.dart';

class PlanBannerAd extends ConsumerStatefulWidget {
  const PlanBannerAd({required this.enabled, super.key});

  final bool enabled;

  @override
  ConsumerState<PlanBannerAd> createState() => _PlanBannerAdState();
}

class _PlanBannerAdState extends ConsumerState<PlanBannerAd> {
  BannerAd? _bannerAd;
  bool _loading = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (widget.enabled && _bannerAd == null && !_loading) {
      _load();
    }
  }

  @override
  void didUpdateWidget(covariant PlanBannerAd oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!widget.enabled && oldWidget.enabled) {
      _disposeAd();
    } else if (widget.enabled && !oldWidget.enabled) {
      _load();
    }
  }

  Future<void> _load() async {
    if (kIsWeb || (!Platform.isAndroid && !Platform.isIOS)) {
      return;
    }
    _loading = true;
    final config = ref.read(appConfigProvider);
    final adUnitId = Platform.isAndroid
        ? config.admobAndroidBannerId
        : config.admobIosBannerId;
    if (adUnitId.isEmpty) {
      _loading = false;
      return;
    }

    // Keep the always-visible free-plan banner compact. The previous large
    // anchored-adaptive format could reserve up to a much taller slot and
    // crowd the application's navigation and content on smaller phones.
    final banner = BannerAd(
      adUnitId: adUnitId,
      request: const AdRequest(),
      size: AdSize.banner,
      listener: BannerAdListener(
        onAdLoaded: (ad) {
          if (!mounted || !widget.enabled) {
            ad.dispose();
            return;
          }
          setState(() {
            _loading = false;
            _bannerAd = ad as BannerAd;
          });
        },
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          if (mounted) {
            setState(() {
              _loading = false;
              _bannerAd = null;
            });
          }
        },
      ),
    );
    await banner.load();
  }

  void _disposeAd() {
    _bannerAd?.dispose();
    _bannerAd = null;
    _loading = false;
  }

  @override
  void dispose() {
    _disposeAd();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final banner = _bannerAd;
    if (!widget.enabled || banner == null) {
      return const SizedBox.shrink();
    }
    return SafeArea(
      top: false,
      child: ColoredBox(
        color: Theme.of(context).colorScheme.surface,
        child: Center(
          child: Semantics(
            label: 'إعلان بانر',
            child: SizedBox(
              width: banner.size.width.toDouble(),
              height: banner.size.height.toDouble(),
              child: AdWidget(ad: banner),
            ),
          ),
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\monetization\rewarded_ad_gateway.dart`

```dart
import 'dart:async';

import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'monetization_models.dart';

abstract interface class RewardedAdGateway {
  Future<bool> loadAndShow(RewardedAdSessionModel session);
}

class GoogleRewardedAdGateway implements RewardedAdGateway {
  const GoogleRewardedAdGateway();

  @override
  Future<bool> loadAndShow(RewardedAdSessionModel session) {
    final completer = Completer<bool>();
    RewardedAd.load(
      adUnitId: session.adUnitId,
      request: const AdRequest(),
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) async {
          var userEarnedReward = false;
          await ad.setServerSideOptions(
            ServerSideVerificationOptions(customData: session.customData),
          );
          ad.fullScreenContentCallback = FullScreenContentCallback(
            onAdDismissedFullScreenContent: (shownAd) {
              shownAd.dispose();
              if (!completer.isCompleted) {
                completer.complete(userEarnedReward);
              }
            },
            onAdFailedToShowFullScreenContent: (shownAd, error) {
              shownAd.dispose();
              if (!completer.isCompleted) {
                completer.completeError(
                  StateError('تعذر عرض الإعلان: ${error.message}'),
                );
              }
            },
          );
          ad.show(
            onUserEarnedReward: (_, reward) {
              userEarnedReward = true;
            },
          );
        },
        onAdFailedToLoad: (error) {
          if (!completer.isCompleted) {
            completer.completeError(
              StateError('تعذر تحميل الإعلان: ${error.message}'),
            );
          }
        },
      ),
    );
    return completer.future;
  }
}

```

---

### File: `lib\features\notifications\notification_messaging.dart`

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Background/terminated pushes are surfaced by the OS notification tray.
  // A background isolate cannot touch the widget tree, so this handler stays
  // minimal; the inbox is refreshed when the user opens the app.
}

final initialNotificationMessageProvider = FutureProvider<RemoteMessage?>((
  ref,
) {
  return FirebaseMessaging.instance.getInitialMessage();
});

final openedNotificationMessageProvider = StreamProvider<RemoteMessage>((ref) {
  return FirebaseMessaging.onMessageOpenedApp;
});

final foregroundNotificationMessageProvider = StreamProvider<RemoteMessage>((
  ref,
) {
  return FirebaseMessaging.onMessage;
});

```

---

### File: `lib\features\notifications\notification_messaging_shell.dart`

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'notification_messaging.dart';

/// Sits above the router so foreground pushes render as in-app banners and a
/// tapped push (cold start, background, or foreground) opens the inbox.
class NotificationMessagingShell extends ConsumerStatefulWidget {
  const NotificationMessagingShell({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<NotificationMessagingShell> createState() =>
      _NotificationMessagingShellState();
}

class _NotificationMessagingShellState
    extends ConsumerState<NotificationMessagingShell> {
  void _openInbox() {
    if (!mounted) {
      return;
    }
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.push('/notifications');
      }
    });
  }

  void _showForegroundBanner(RemoteMessage message) {
    if (!mounted) {
      return;
    }
    final messenger = ScaffoldMessenger.of(context);
    final title = message.notification?.title ?? 'إشعار جديد';
    final body = message.notification?.body;
    messenger
      ..hideCurrentMaterialBanner()
      ..showMaterialBanner(
        MaterialBanner(
          leading: const Icon(Icons.notifications_active_outlined),
          content: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(title, style: Theme.of(context).textTheme.titleSmall),
              if (body != null && body.isNotEmpty)
                Text(body, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                messenger.hideCurrentMaterialBanner();
                _openInbox();
              },
              child: const Text('فتح'),
            ),
            TextButton(
              onPressed: messenger.hideCurrentMaterialBanner,
              child: const Text('إغلاق'),
            ),
          ],
        ),
      );
    Future<void>.delayed(const Duration(seconds: 6), () {
      if (mounted) {
        messenger.hideCurrentMaterialBanner();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<AsyncValue<RemoteMessage?>>(initialNotificationMessageProvider, (
      previous,
      next,
    ) {
      if (next.valueOrNull != null) {
        _openInbox();
      }
    });
    ref.listen<AsyncValue<RemoteMessage>>(openedNotificationMessageProvider, (
      previous,
      next,
    ) {
      if (next.valueOrNull != null) {
        _openInbox();
      }
    });
    ref.listen<AsyncValue<RemoteMessage>>(
      foregroundNotificationMessageProvider,
      (previous, next) {
        final message = next.valueOrNull;
        if (message != null) {
          _showForegroundBanner(message);
        }
      },
    );
    return widget.child;
  }
}

```

---

### File: `lib\features\notifications\notification_models.dart`

```dart
class AppNotification {
  const AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.category,
    required this.data,
    required this.readAt,
    required this.sentAt,
  });

  final String id;
  final String title;
  final String body;
  final String category;
  final Map<String, dynamic> data;
  final DateTime? readAt;
  final DateTime sentAt;

  bool get isUnread => readAt == null;

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      category: json['category'] as String,
      data: _map(json['data']),
      readAt: json['read_at'] == null
          ? null
          : DateTime.parse(json['read_at'] as String),
      sentAt: DateTime.parse(json['sent_at'] as String),
    );
  }
}

class NotificationPage {
  const NotificationPage({
    required this.items,
    required this.total,
    required this.unreadCount,
    required this.limit,
    required this.offset,
  });

  final List<AppNotification> items;
  final int total;
  final int unreadCount;
  final int limit;
  final int offset;

  factory NotificationPage.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return NotificationPage(
      items: rawItems
          .map((item) => AppNotification.fromJson(_map(item)))
          .toList(growable: false),
      total: json['total'] as int? ?? 0,
      unreadCount: json['unread_count'] as int? ?? 0,
      limit: json['limit'] as int? ?? 20,
      offset: json['offset'] as int? ?? 0,
    );
  }
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

```

---

### File: `lib\features\notifications\notification_providers.dart`

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/session_controller.dart';
import 'notification_models.dart';
import 'notification_repository.dart';

final notificationInboxProvider = FutureProvider.autoDispose<NotificationPage>((
  ref,
) {
  return ref.watch(notificationRepositoryProvider).listNotifications();
});

final pushRegistrationProvider = FutureProvider<void>((ref) async {
  final session = ref.watch(sessionControllerProvider);
  if (session.status != SessionStatus.authenticated) {
    return;
  }
  try {
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp();
    }
    final messaging = FirebaseMessaging.instance;
    await messaging.requestPermission();
    final token = await messaging.getToken();
    if (token == null || token.length < 20) {
      return;
    }
    final platform = kIsWeb
        ? 'web'
        : defaultTargetPlatform == TargetPlatform.iOS
        ? 'ios'
        : 'android';
    await ref
        .read(notificationRepositoryProvider)
        .registerDevice(token: token, platform: platform);
  } on Object {
    // Push remains optional until Firebase project files are configured.
  }
});

```

---

### File: `lib\features\notifications\notification_repository.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'notification_models.dart';

class NotificationRepository {
  const NotificationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<NotificationPage> listNotifications({
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/notifications',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return NotificationPage.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> markRead(String notificationId) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/notifications/$notificationId/read',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> markAllRead() async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/notifications/read-all',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> registerDevice({
    required String token,
    required String platform,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/notifications/devices',
        data: <String, dynamic>{'token': token, 'platform': platform},
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Notification response is empty.');
    }
    return value;
  }
}

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\notifications\notification_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/ui/app_notice.dart';
import 'notification_models.dart';
import 'notification_providers.dart';
import 'notification_repository.dart';

class NotificationScreen extends ConsumerStatefulWidget {
  const NotificationScreen({super.key});

  @override
  ConsumerState<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends ConsumerState<NotificationScreen> {
  bool _unreadOnly = false;

  Future<void> _refresh() async {
    ref.invalidate(notificationInboxProvider);
    await ref.read(notificationInboxProvider.future);
  }

  Future<void> _markAllRead() async {
    try {
      await ref.read(notificationRepositoryProvider).markAllRead();
      ref.invalidate(notificationInboxProvider);
      if (mounted) {
        AppNotice.show(
          context,
          title: 'تم تحديث الإشعارات',
          message: 'تم تعليم كل الإشعارات كمقروءة.',
          tone: AppNoticeTone.success,
        );
      }
    } on Object {
      if (mounted) {
        AppNotice.show(
          context,
          title: 'تعذر التحديث',
          message: 'لم نتمكن من تعليم الإشعارات كمقروءة الآن.',
          tone: AppNoticeTone.error,
        );
      }
    }
  }

  Future<void> _markRead(AppNotification item) async {
    if (!item.isUnread) {
      return;
    }
    try {
      await ref.read(notificationRepositoryProvider).markRead(item.id);
      ref.invalidate(notificationInboxProvider);
    } on Object {
      if (mounted) {
        AppNotice.show(
          context,
          message: 'تعذر تحديث حالة الإشعار.',
          tone: AppNoticeTone.error,
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final inbox = ref.watch(notificationInboxProvider);
    final unreadCount = inbox.asData?.value.unreadCount;
    return Scaffold(
      appBar: AppBar(
        title: const Text('الإشعارات'),
        actions: [
          IconButton(
            tooltip: 'تعليم الكل كمقروء',
            onPressed: unreadCount == null || unreadCount == 0
                ? null
                : _markAllRead,
            icon: const Icon(Icons.done_all_rounded),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: inbox.when(
          loading: () => const _NotificationLoading(),
          error: (error, stackTrace) => ListView(
            padding: const EdgeInsets.all(24),
            children: [
              const SizedBox(height: 90),
              Icon(
                Icons.cloud_off_rounded,
                size: 62,
                color: Theme.of(context).colorScheme.outline,
              ),
              const SizedBox(height: 16),
              Text(
                'تعذر تحميل الإشعارات',
                textAlign: TextAlign.center,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              Text(
                'اسحب الشاشة لأسفل أو حاول مرة أخرى.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 18),
              OutlinedButton.icon(
                onPressed: () => ref.invalidate(notificationInboxProvider),
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
          data: (page) {
            final items = _unreadOnly
                ? page.items.where((item) => item.isUnread).toList()
                : page.items;
            return CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 8),
                  sliver: SliverToBoxAdapter(
                    child: _NotificationSummary(
                      total: page.total,
                      unread: page.unreadCount,
                      unreadOnly: _unreadOnly,
                      onFilterChanged: (value) {
                        setState(() => _unreadOnly = value);
                      },
                    ),
                  ),
                ),
                if (items.isEmpty)
                  SliverFillRemaining(
                    hasScrollBody: false,
                    child: _EmptyNotifications(unreadOnly: _unreadOnly),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    sliver: SliverList.separated(
                      itemCount: items.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) => _NotificationCard(
                        item: items[index],
                        onRead: () => _markRead(items[index]),
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _NotificationSummary extends StatelessWidget {
  const _NotificationSummary({
    required this.total,
    required this.unread,
    required this.unreadOnly,
    required this.onFilterChanged,
  });

  final int total;
  final int unread;
  final bool unreadOnly;
  final ValueChanged<bool> onFilterChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            theme.colorScheme.primaryContainer,
            theme.colorScheme.surfaceContainerLowest,
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Icon(
                  Icons.notifications_active_rounded,
                  color: theme.colorScheme.onPrimary,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      unread == 0
                          ? 'كل شيء تحت السيطرة'
                          : 'لديك $unread إشعار غير مقروء',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      'إجمالي الإشعارات: $total',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 10,
            children: [
              ChoiceChip(
                label: const Text('الكل'),
                selected: !unreadOnly,
                onSelected: (_) => onFilterChanged(false),
              ),
              ChoiceChip(
                label: Text('غير المقروء ($unread)'),
                selected: unreadOnly,
                onSelected: (_) => onFilterChanged(true),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({required this.item, required this.onRead});

  final AppNotification item;
  final VoidCallback onRead;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final visual = _categoryVisual(item.category, theme.colorScheme);
    return Material(
      color: item.isUnread
          ? theme.colorScheme.primaryContainer.withValues(alpha: 0.28)
          : theme.colorScheme.surfaceContainerLowest,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: item.isUnread ? onRead : null,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: item.isUnread
                  ? theme.colorScheme.primary.withValues(alpha: 0.28)
                  : theme.colorScheme.outlineVariant,
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: visual.background,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(visual.icon, color: visual.foreground),
              ),
              const SizedBox(width: 13),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item.title,
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: item.isUnread
                                  ? FontWeight.w800
                                  : FontWeight.w600,
                            ),
                          ),
                        ),
                        if (item.isUnread)
                          Container(
                            width: 9,
                            height: 9,
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary,
                              shape: BoxShape.circle,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 7),
                    Text(
                      item.body,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.55,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Icon(
                          Icons.schedule_rounded,
                          size: 16,
                          color: theme.colorScheme.outline,
                        ),
                        const SizedBox(width: 5),
                        Text(
                          _relativeTime(item.sentAt),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.outline,
                          ),
                        ),
                        if (item.isUnread) ...[
                          const Spacer(),
                          Text(
                            'اضغط للتعليم كمقروء',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.primary,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyNotifications extends StatelessWidget {
  const _EmptyNotifications({required this.unreadOnly});

  final bool unreadOnly;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              unreadOnly
                  ? Icons.mark_email_read_rounded
                  : Icons.notifications_none_rounded,
              size: 68,
              color: theme.colorScheme.outline,
            ),
            const SizedBox(height: 16),
            Text(
              unreadOnly
                  ? 'لا توجد إشعارات غير مقروءة'
                  : 'لا توجد إشعارات حتى الآن',
              textAlign: TextAlign.center,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              unreadOnly
                  ? 'قرأت كل الإشعارات الحالية.'
                  : 'ستظهر هنا التنبيهات والتحديثات المهمة.',
              textAlign: TextAlign.center,
              style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotificationLoading extends StatelessWidget {
  const _NotificationLoading();

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 5,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, __) => Container(
        height: 112,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainer,
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }
}

_CategoryVisual _categoryVisual(String category, ColorScheme colors) {
  final normalized = category.toLowerCase();
  if (normalized.contains('reward') || normalized.contains('wallet')) {
    return const _CategoryVisual(
      icon: Icons.workspace_premium_rounded,
      background: Color(0xFFFFF1C7),
      foreground: Color(0xFF805B00),
    );
  }
  if (normalized.contains('report') || normalized.contains('analysis')) {
    return _CategoryVisual(
      icon: Icons.analytics_rounded,
      background: colors.primaryContainer,
      foreground: colors.onPrimaryContainer,
    );
  }
  if (normalized.contains('community')) {
    return const _CategoryVisual(
      icon: Icons.forum_rounded,
      background: Color(0xFFE9E4FF),
      foreground: Color(0xFF4F378B),
    );
  }
  return _CategoryVisual(
    icon: Icons.notifications_rounded,
    background: colors.surfaceContainerHighest,
    foreground: colors.onSurfaceVariant,
  );
}

String _relativeTime(DateTime value) {
  final difference = DateTime.now().difference(value.toLocal());
  if (difference.isNegative || difference.inMinutes < 1) {
    return 'الآن';
  }
  if (difference.inMinutes < 60) {
    return 'منذ ${difference.inMinutes} دقيقة';
  }
  if (difference.inHours < 24) {
    return 'منذ ${difference.inHours} ساعة';
  }
  if (difference.inDays < 7) {
    return 'منذ ${difference.inDays} يوم';
  }
  return '${value.toLocal().day}/${value.toLocal().month}/${value.toLocal().year}';
}

class _CategoryVisual {
  const _CategoryVisual({
    required this.icon,
    required this.background,
    required this.foreground,
  });

  final IconData icon;
  final Color background;
  final Color foreground;
}

```

---

### File: `lib\features\onboarding\onboarding_controller.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class OnboardingController extends StateNotifier<AsyncValue<bool>> {
  OnboardingController() : super(const AsyncValue.loading()) {
    load();
  }

  static const _completedKey = 'onboarding_completed';

  Future<void> load() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final preferences = await SharedPreferences.getInstance();
      return preferences.getBool(_completedKey) ?? false;
    });
  }

  Future<void> complete() async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setBool(_completedKey, true);
    state = const AsyncValue.data(true);
  }
}

final onboardingControllerProvider =
    StateNotifierProvider<OnboardingController, AsyncValue<bool>>((ref) {
      return OnboardingController();
    });

```

---

### File: `lib\features\onboarding\onboarding_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'onboarding_controller.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _controller = PageController();
  int _page = 0;

  static const _items = <({IconData icon, String title, String body})>[
    (
      icon: Icons.insights_rounded,
      title: 'تحليل واضح بدل الضوضاء',
      body: 'اعرض القرار والدرجة والمخاطرة وخطة الحركة في تقرير عربي منظم.',
    ),
    (
      icon: Icons.calendar_month_rounded,
      title: 'أفضل الفرص للجلسة القادمة',
      body:
          'تقرير يومي ثابت بعد الإغلاق، مبني على قواعد رقمية وليس وعودًا بالربح.',
    ),
    (
      icon: Icons.account_balance_wallet_rounded,
      title: 'رصيدك محمي على السيرفر',
      body: 'لا يحدث الخصم إلا بعد نجاح العملية، ولا يتكرر بسبب ضعف الإنترنت.',
    ),
  ];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _next() async {
    if (_page < _items.length - 1) {
      await _controller.nextPage(
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOut,
      );
      return;
    }
    await ref.read(onboardingControllerProvider.notifier).complete();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 20),
          child: Column(
            children: [
              Align(
                alignment: AlignmentDirectional.centerEnd,
                child: TextButton(
                  onPressed: () => ref
                      .read(onboardingControllerProvider.notifier)
                      .complete(),
                  child: const Text('تخطي'),
                ),
              ),
              Expanded(
                child: PageView.builder(
                  controller: _controller,
                  itemCount: _items.length,
                  onPageChanged: (value) => setState(() => _page = value),
                  itemBuilder: (context, index) {
                    final item = _items[index];
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 132,
                          height: 132,
                          decoration: BoxDecoration(
                            color: Theme.of(
                              context,
                            ).colorScheme.primaryContainer,
                            borderRadius: BorderRadius.circular(42),
                          ),
                          child: Icon(
                            item.icon,
                            size: 66,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                        const SizedBox(height: 36),
                        Text(
                          item.title,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall
                              ?.copyWith(fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          item.body,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyLarge
                              ?.copyWith(
                                height: 1.7,
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                        ),
                      ],
                    );
                  },
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  _items.length,
                  (index) => AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: index == _page ? 28 : 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      color: index == _page
                          ? Theme.of(context).colorScheme.primary
                          : Theme.of(context).colorScheme.outlineVariant,
                      borderRadius: BorderRadius.circular(99),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _next,
                child: Text(
                  _page == _items.length - 1 ? 'ابدأ الآن' : 'التالي',
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\performance\performance_admin_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import 'performance_models.dart';
import 'performance_providers.dart';
import 'performance_repository.dart';
import 'performance_widgets.dart';

class PerformanceAdminScreen extends ConsumerStatefulWidget {
  const PerformanceAdminScreen({super.key});

  @override
  ConsumerState<PerformanceAdminScreen> createState() =>
      _PerformanceAdminScreenState();
}

class _PerformanceAdminScreenState
    extends ConsumerState<PerformanceAdminScreen> {
  bool _busy = false;

  @override
  Widget build(BuildContext context) {
    final delayed = ref.watch(delayedPerformanceProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('عمليات الإدارة'),
        actions: [
          IconButton(
            onPressed: () => context.push('/admin/historical-replays'),
            icon: const Icon(Icons.science_outlined),
            tooltip: 'اختبار المحركات التاريخي',
          ),
          IconButton(
            onPressed: () => context.push('/admin/wallet-credit'),
            icon: const Icon(Icons.add_card_rounded),
            tooltip: 'إضافة عملات للمستخدمين',
          ),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            final refreshed = ref.refresh(delayedPerformanceProvider.future);
            await refreshed;
          },
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'عمليات الإدارة',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      FilledButton.icon(
                        onPressed: () =>
                            context.push('/admin/historical-replays'),
                        icon: const Icon(Icons.science_outlined),
                        label: const Text('اختبار المحركات التاريخي'),
                      ),
                      const SizedBox(height: 8),
                      FilledButton.icon(
                        onPressed: () => context.push('/admin/wallet-credit'),
                        icon: const Icon(Icons.add_card_rounded),
                        label: const Text('إضافة عملات للمستخدمين'),
                      ),
                      const SizedBox(height: 8),
                      FilledButton.icon(
                        onPressed: _busy ? null : _evaluateDue,
                        icon: const Icon(Icons.playlist_add_check_rounded),
                        label: const Text('تقييم التقارير المستحقة'),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _busy ? null : () => _export(7),
                              child: const Text('نسخ CSV لـ7 جلسات'),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _busy ? null : () => _export(30),
                              child: const Text('نسخ CSV لـ30 جلسة'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'التقارير المتأخرة أو الناقصة',
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 10),
              delayed.when(
                loading: () => const PerformanceLoading(),
                error: (error, __) => PerformanceFailure(
                  message: 'تعذر تحميل قائمة التأخير. ${_errorMessage(error)}',
                  retry: () => ref.invalidate(delayedPerformanceProvider),
                ),
                data: (items) => items.isEmpty
                    ? const Card(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Text(
                            'لا توجد تقارير متأخرة حاليًا.',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : Column(
                        children: items
                            .map(
                              (item) => _DelayedCard(
                                item: item,
                                busy: _busy,
                                retry: () => _retry(item.reportId),
                              ),
                            )
                            .toList(growable: false),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _evaluateDue() async {
    await _run(() async {
      final result = await ref
          .read(performanceRepositoryProvider)
          .evaluateDue(limit: 50);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'تم فحص ${result['scanned_reports'] ?? 0} تقرير؛ '
            '${result['completed_reports'] ?? 0} اكتمل.',
          ),
        ),
      );
    });
  }

  Future<void> _retry(String reportId) async {
    await _run(() async {
      await ref.read(performanceRepositoryProvider).retryReport(reportId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تمت إعادة محاولة التقرير.')),
        );
      }
    });
  }

  Future<void> _export(int window) async {
    await _run(() async {
      final csv = await ref
          .read(performanceRepositoryProvider)
          .exportCsv(window);
      await Clipboard.setData(ClipboardData(text: csv));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تم نسخ CSV لآخر $window جلسة.')),
        );
      }
    });
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      await action();
      ref.invalidate(delayedPerformanceProvider);
      ref.invalidate(performanceSummaryProvider);
      ref.invalidate(performanceReportsProvider);
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}

class _DelayedCard extends StatelessWidget {
  const _DelayedCard({
    required this.item,
    required this.busy,
    required this.retry,
  });

  final PerformanceDelayedItem item;
  final bool busy;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    final date = formatPerformanceDate(item.targetSessionDate);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              date,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            Text(
              '${item.evaluatedItems}/${item.totalItems} مكتملة • '
              '${item.pendingItems} معلقة • ${item.failedItems} فاشلة',
            ),
            if (item.reasons.isNotEmpty)
              Text('الأسباب: ${item.reasons.join('، ')}'),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: busy ? null : retry,
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('إعادة المحاولة'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () =>
                        context.push('/performance/reports/${item.reportId}'),
                    icon: const Icon(Icons.visibility_outlined),
                    label: const Text('عرض وتصحيح'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

String _errorMessage(Object error) {
  return error is ApiException ? error.message : 'حاول مرة أخرى.';
}

```

---

### File: `lib\features\performance\performance_models.dart`

```dart
class PerformanceBestWorst {
  const PerformanceBestWorst({
    required this.reportId,
    required this.targetSessionDate,
    required this.ticker,
    required this.rank,
    required this.returnBp,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final String ticker;
  final int rank;
  final int returnBp;

  factory PerformanceBestWorst.fromJson(Map<String, dynamic> json) {
    return PerformanceBestWorst(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      ticker: json['ticker'] as String,
      rank: json['rank'] as int,
      returnBp: json['return_bp'] as int,
    );
  }
}

class PerformanceSession {
  const PerformanceSession({
    required this.reportId,
    required this.targetSessionDate,
    required this.evaluationStatus,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.dataCompletenessPct,
    required this.averageReturnBp,
    required this.positiveCount,
    required this.negativeCount,
    required this.directionAccuracyPct,
    required this.targetOneHitRatePct,
    required this.stopLossHitRatePct,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final String evaluationStatus;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final double dataCompletenessPct;
  final int? averageReturnBp;
  final int positiveCount;
  final int negativeCount;
  final double? directionAccuracyPct;
  final double? targetOneHitRatePct;
  final double? stopLossHitRatePct;

  factory PerformanceSession.fromJson(Map<String, dynamic> json) {
    return PerformanceSession(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      evaluationStatus: json['evaluation_status'] as String,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      dataCompletenessPct: (json['data_completeness_pct'] as num? ?? 0)
          .toDouble(),
      averageReturnBp: json['average_return_bp'] as int?,
      positiveCount: json['positive_count'] as int? ?? 0,
      negativeCount: json['negative_count'] as int? ?? 0,
      directionAccuracyPct: _double(json['direction_accuracy_pct']),
      targetOneHitRatePct: _double(json['target_one_hit_rate_pct']),
      stopLossHitRatePct: _double(json['stop_loss_hit_rate_pct']),
    );
  }
}

class PerformanceRank {
  const PerformanceRank({
    required this.rank,
    required this.evaluatedItems,
    required this.averageReturnBp,
    required this.medianReturnBp,
    required this.positiveRatePct,
    required this.directionAccuracyPct,
    required this.targetOneHitRatePct,
    required this.stopLossHitRatePct,
  });

  final int rank;
  final int evaluatedItems;
  final int? averageReturnBp;
  final int? medianReturnBp;
  final double? positiveRatePct;
  final double? directionAccuracyPct;
  final double? targetOneHitRatePct;
  final double? stopLossHitRatePct;

  factory PerformanceRank.fromJson(Map<String, dynamic> json) {
    return PerformanceRank(
      rank: json['rank'] as int,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      averageReturnBp: json['average_return_bp'] as int?,
      medianReturnBp: json['median_return_bp'] as int?,
      positiveRatePct: _double(json['positive_rate_pct']),
      directionAccuracyPct: _double(json['direction_accuracy_pct']),
      targetOneHitRatePct: _double(json['target_one_hit_rate_pct']),
      stopLossHitRatePct: _double(json['stop_loss_hit_rate_pct']),
    );
  }
}

class PerformanceSummary {
  const PerformanceSummary({
    required this.windowSessions,
    required this.sessionsFound,
    required this.completeSessions,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.dataCompletenessPct,
    required this.positiveCount,
    required this.negativeCount,
    required this.flatCount,
    required this.averageReturnBp,
    required this.medianReturnBp,
    required this.positiveRatePct,
    required this.directionAccuracyPct,
    required this.targetOneHitRatePct,
    required this.targetTwoHitRatePct,
    required this.stopLossHitRatePct,
    required this.bestOutcome,
    required this.worstOutcome,
    required this.ranks,
    required this.sessions,
    required this.benchmark,
    required this.negativeResultsRetained,
  });

  final int windowSessions;
  final int sessionsFound;
  final int completeSessions;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final double dataCompletenessPct;
  final int positiveCount;
  final int negativeCount;
  final int flatCount;
  final int? averageReturnBp;
  final int? medianReturnBp;
  final double? positiveRatePct;
  final double? directionAccuracyPct;
  final double? targetOneHitRatePct;
  final double? targetTwoHitRatePct;
  final double? stopLossHitRatePct;
  final PerformanceBestWorst? bestOutcome;
  final PerformanceBestWorst? worstOutcome;
  final List<PerformanceRank> ranks;
  final List<PerformanceSession> sessions;
  final Map<String, dynamic> benchmark;
  final bool negativeResultsRetained;

  factory PerformanceSummary.fromJson(Map<String, dynamic> json) {
    return PerformanceSummary(
      windowSessions: json['window_sessions'] as int,
      sessionsFound: json['sessions_found'] as int? ?? 0,
      completeSessions: json['complete_sessions'] as int? ?? 0,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      dataCompletenessPct: (json['data_completeness_pct'] as num? ?? 0)
          .toDouble(),
      positiveCount: json['positive_count'] as int? ?? 0,
      negativeCount: json['negative_count'] as int? ?? 0,
      flatCount: json['flat_count'] as int? ?? 0,
      averageReturnBp: json['average_return_bp'] as int?,
      medianReturnBp: json['median_return_bp'] as int?,
      positiveRatePct: _double(json['positive_rate_pct']),
      directionAccuracyPct: _double(json['direction_accuracy_pct']),
      targetOneHitRatePct: _double(json['target_one_hit_rate_pct']),
      targetTwoHitRatePct: _double(json['target_two_hit_rate_pct']),
      stopLossHitRatePct: _double(json['stop_loss_hit_rate_pct']),
      bestOutcome: json['best_outcome'] == null
          ? null
          : PerformanceBestWorst.fromJson(_map(json['best_outcome'])),
      worstOutcome: json['worst_outcome'] == null
          ? null
          : PerformanceBestWorst.fromJson(_map(json['worst_outcome'])),
      ranks: _list(json['ranks'])
          .map((item) => PerformanceRank.fromJson(_map(item)))
          .toList(growable: false),
      sessions: _list(json['sessions'])
          .map((item) => PerformanceSession.fromJson(_map(item)))
          .toList(growable: false),
      benchmark: _map(json['benchmark']),
      negativeResultsRetained:
          json['negative_results_retained'] as bool? ?? true,
    );
  }
}

class PerformanceReportListItem {
  const PerformanceReportListItem({
    required this.reportId,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.evaluationStatus,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.dataCompletenessPct,
    required this.averageReturnBp,
    required this.positiveCount,
    required this.negativeCount,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final String evaluationStatus;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final double dataCompletenessPct;
  final int? averageReturnBp;
  final int positiveCount;
  final int negativeCount;

  factory PerformanceReportListItem.fromJson(Map<String, dynamic> json) {
    return PerformanceReportListItem(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      evaluationStatus: json['evaluation_status'] as String,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      dataCompletenessPct: (json['data_completeness_pct'] as num? ?? 0)
          .toDouble(),
      averageReturnBp: json['average_return_bp'] as int?,
      positiveCount: json['positive_count'] as int? ?? 0,
      negativeCount: json['negative_count'] as int? ?? 0,
    );
  }
}

class PerformanceReportPage {
  const PerformanceReportPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<PerformanceReportListItem> items;
  final int total;
  final int limit;
  final int offset;

  factory PerformanceReportPage.fromJson(Map<String, dynamic> json) {
    return PerformanceReportPage(
      items: _list(json['items'])
          .map((item) => PerformanceReportListItem.fromJson(_map(item)))
          .toList(growable: false),
      total: json['total'] as int? ?? 0,
      limit: json['limit'] as int? ?? 0,
      offset: json['offset'] as int? ?? 0,
    );
  }
}

class PerformanceOutcome {
  const PerformanceOutcome({
    required this.id,
    required this.ticker,
    required this.rank,
    required this.status,
    required this.expectedDirection,
    required this.priceAtAnalysis,
    required this.sessionOpen,
    required this.sessionHigh,
    required this.sessionLow,
    required this.sessionClose,
    required this.returnBp,
    required this.maxUpsideBp,
    required this.maxDrawdownBp,
    required this.directionCorrect,
    required this.targetOne,
    required this.targetTwo,
    required this.stopLoss,
    required this.targetOneHit,
    required this.targetTwoHit,
    required this.stopLossHit,
    required this.provider,
    required this.dataAsOf,
    required this.evaluatedAt,
    required this.evaluatorVersion,
    required this.evidence,
    required this.correctionCount,
  });

  final String id;
  final String ticker;
  final int rank;
  final String status;
  final String expectedDirection;
  final double priceAtAnalysis;
  final double? sessionOpen;
  final double? sessionHigh;
  final double? sessionLow;
  final double? sessionClose;
  final int? returnBp;
  final int? maxUpsideBp;
  final int? maxDrawdownBp;
  final bool? directionCorrect;
  final double? targetOne;
  final double? targetTwo;
  final double? stopLoss;
  final bool? targetOneHit;
  final bool? targetTwoHit;
  final bool? stopLossHit;
  final String? provider;
  final DateTime? dataAsOf;
  final DateTime? evaluatedAt;
  final String evaluatorVersion;
  final Map<String, dynamic> evidence;
  final int correctionCount;

  bool get isComplete => status == 'complete';

  factory PerformanceOutcome.fromJson(Map<String, dynamic> json) {
    return PerformanceOutcome(
      id: json['id'] as String,
      ticker: json['ticker'] as String,
      rank: json['rank'] as int,
      status: json['status'] as String,
      expectedDirection: json['expected_direction'] as String,
      priceAtAnalysis: (json['price_at_analysis'] as num).toDouble(),
      sessionOpen: _double(json['session_open']),
      sessionHigh: _double(json['session_high']),
      sessionLow: _double(json['session_low']),
      sessionClose: _double(json['session_close']),
      returnBp: json['return_bp'] as int?,
      maxUpsideBp: json['max_upside_bp'] as int?,
      maxDrawdownBp: json['max_drawdown_bp'] as int?,
      directionCorrect: json['direction_correct'] as bool?,
      targetOne: _double(json['target_one']),
      targetTwo: _double(json['target_two']),
      stopLoss: _double(json['stop_loss']),
      targetOneHit: json['target_one_hit'] as bool?,
      targetTwoHit: json['target_two_hit'] as bool?,
      stopLossHit: json['stop_loss_hit'] as bool?,
      provider: json['provider'] as String?,
      dataAsOf: _date(json['data_as_of']),
      evaluatedAt: _date(json['evaluated_at']),
      evaluatorVersion: json['evaluator_version'] as String,
      evidence: _map(json['evidence']),
      correctionCount: json['correction_count'] as int? ?? 0,
    );
  }
}

class PerformanceRevision {
  const PerformanceRevision({
    required this.id,
    required this.revisionNumber,
    required this.reason,
    required this.beforePayload,
    required this.afterPayload,
    required this.createdAt,
  });

  final String id;
  final int revisionNumber;
  final String reason;
  final Map<String, dynamic> beforePayload;
  final Map<String, dynamic> afterPayload;
  final DateTime createdAt;

  factory PerformanceRevision.fromJson(Map<String, dynamic> json) {
    return PerformanceRevision(
      id: json['id'] as String,
      revisionNumber: json['revision_number'] as int,
      reason: json['reason'] as String,
      beforePayload: _map(json['before_payload']),
      afterPayload: _map(json['after_payload']),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class PerformanceReportDetail {
  const PerformanceReportDetail({
    required this.reportId,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.evaluationStatus,
    required this.session,
    required this.outcomes,
    required this.revisions,
    required this.negativeResultsRetained,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final String evaluationStatus;
  final PerformanceSession session;
  final List<PerformanceOutcome> outcomes;
  final List<PerformanceRevision> revisions;
  final bool negativeResultsRetained;

  factory PerformanceReportDetail.fromJson(Map<String, dynamic> json) {
    return PerformanceReportDetail(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      evaluationStatus: json['evaluation_status'] as String,
      session: PerformanceSession.fromJson(_map(json['session'])),
      outcomes: _list(json['outcomes'])
          .map((item) => PerformanceOutcome.fromJson(_map(item)))
          .toList(growable: false),
      revisions: _list(json['revisions'])
          .map((item) => PerformanceRevision.fromJson(_map(item)))
          .toList(growable: false),
      negativeResultsRetained:
          json['negative_results_retained'] as bool? ?? true,
    );
  }
}

class PerformanceDelayedItem {
  const PerformanceDelayedItem({
    required this.reportId,
    required this.targetSessionDate,
    required this.evaluationId,
    required this.evaluationStatus,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.lastAttemptAt,
    required this.reasons,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final String? evaluationId;
  final String evaluationStatus;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final DateTime? lastAttemptAt;
  final List<String> reasons;

  factory PerformanceDelayedItem.fromJson(Map<String, dynamic> json) {
    return PerformanceDelayedItem(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      evaluationId: json['evaluation_id'] as String?,
      evaluationStatus: json['evaluation_status'] as String,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      lastAttemptAt: _date(json['last_attempt_at']),
      reasons: _list(json['reasons']).map((item) => '$item').toList(),
    );
  }
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return <String, dynamic>{};
}

List<dynamic> _list(Object? value) {
  return value is List ? value : const <dynamic>[];
}

double? _double(Object? value) {
  return value is num ? value.toDouble() : null;
}

DateTime? _date(Object? value) {
  return value is String ? DateTime.parse(value) : null;
}

```

---

### File: `lib\features\performance\performance_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'performance_models.dart';
import 'performance_repository.dart';

final performanceWindowProvider = StateProvider<int>((ref) => 7);

final performanceSummaryProvider =
    FutureProvider.autoDispose<PerformanceSummary>((ref) {
      final window = ref.watch(performanceWindowProvider);
      return ref.watch(performanceRepositoryProvider).summary(window);
    });

final performanceReportsProvider =
    FutureProvider.autoDispose<PerformanceReportPage>((ref) {
      return ref.watch(performanceRepositoryProvider).reports();
    });

final performanceReportDetailProvider = FutureProvider.autoDispose
    .family<PerformanceReportDetail, String>((ref, reportId) {
      return ref.watch(performanceRepositoryProvider).reportDetail(reportId);
    });

final delayedPerformanceProvider =
    FutureProvider.autoDispose<List<PerformanceDelayedItem>>((ref) {
      return ref.watch(performanceRepositoryProvider).delayed();
    });

```

---

### File: `lib\features\performance\performance_report_screen.dart`

```dart
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../auth/session_controller.dart';
import 'performance_models.dart';
import 'performance_providers.dart';
import 'performance_repository.dart';
import 'performance_widgets.dart';

class PerformanceReportScreen extends ConsumerWidget {
  const PerformanceReportScreen({required this.reportId, super.key});

  final String reportId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detail = ref.watch(performanceReportDetailProvider(reportId));
    return Scaffold(
      appBar: AppBar(title: const Text('نتائج التقرير')),
      body: SafeArea(
        child: detail.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, __) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              PerformanceFailure(
                message: 'تعذر تحميل نتائج التقرير.',
                retry: () =>
                    ref.invalidate(performanceReportDetailProvider(reportId)),
              ),
            ],
          ),
          data: (value) => _DetailBody(detail: value),
        ),
      ),
    );
  }
}

class _DetailBody extends ConsumerWidget {
  const _DetailBody({required this.detail});

  final PerformanceReportDetail detail;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final date = formatPerformanceDate(detail.targetSessionDate);
    final isAdmin =
        ref.watch(sessionControllerProvider).profile?.isAdmin == true;
    return RefreshIndicator(
      onRefresh: () async {
        final refreshed = ref.refresh(
          performanceReportDetailProvider(detail.reportId).future,
        );
        await refreshed;
      },
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        children: [
          const PerformanceNotice(),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    date,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: performanceProgress(
                      detail.session.dataCompletenessPct,
                    ),
                    minHeight: 9,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${detail.session.dataCompletenessPct.toStringAsFixed(1)}% مكتملة • '
                    '${detail.session.evaluatedItems}/${detail.session.totalItems} نتيجة',
                  ),
                  Text(
                    'حالة التقييم: '
                    '${performanceStatusLabel(detail.evaluationStatus)}',
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (detail.outcomes.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Text(
                  'لا توجد نتائج أسهم مسجلة لهذه الجلسة حتى الآن.',
                  textAlign: TextAlign.center,
                ),
              ),
            )
          else
            for (final outcome in detail.outcomes)
              _OutcomeCard(
                outcome: outcome,
                canCorrect: isAdmin && outcome.isComplete,
                onCorrect: () => _showCorrection(context, ref, outcome),
              ),
          if (detail.revisions.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'سجل التصحيحات',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 8),
            for (final revision in detail.revisions)
              Card(
                child: ListTile(
                  leading: CircleAvatar(
                    child: Text('${revision.revisionNumber}'),
                  ),
                  title: Text(revision.reason),
                  subtitle: Text(
                    formatPerformanceDate(
                      revision.createdAt,
                      includeTime: true,
                    ),
                  ),
                ),
              ),
          ],
        ],
      ),
    );
  }

  Future<void> _showCorrection(
    BuildContext context,
    WidgetRef ref,
    PerformanceOutcome outcome,
  ) async {
    final result = await showDialog<_CorrectionData>(
      context: context,
      builder: (context) => _CorrectionDialog(outcome: outcome),
    );
    if (result == null || !context.mounted) return;
    try {
      await ref
          .read(performanceRepositoryProvider)
          .correctOutcome(
            outcomeId: outcome.id,
            reason: result.reason,
            sessionOpen: result.open,
            sessionHigh: result.high,
            sessionLow: result.low,
            sessionClose: result.close,
            provider: result.provider,
            dataFingerprint: result.fingerprint,
            dataAsOf: result.dataAsOf,
          );
      ref.invalidate(performanceReportDetailProvider(detail.reportId));
      ref.invalidate(performanceSummaryProvider);
      ref.invalidate(performanceReportsProvider);
      ref.invalidate(delayedPerformanceProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم حفظ التصحيح في سجل تدقيق جديد.')),
        );
      }
    } on ApiException catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    }
  }
}

class _OutcomeCard extends StatelessWidget {
  const _OutcomeCard({
    required this.outcome,
    required this.canCorrect,
    required this.onCorrect,
  });

  final PerformanceOutcome outcome;
  final bool canCorrect;
  final VoidCallback onCorrect;

  @override
  Widget build(BuildContext context) {
    final result = formatBasisPoints(outcome.returnBp);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${outcome.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    outcome.ticker,
                    textDirection: ui.TextDirection.ltr,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Chip(
                  label: Text(
                    outcome.isComplete
                        ? result
                        : performanceStatusLabel(outcome.status),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            if (outcome.isComplete) ...[
              Text(
                'سعر التحليل: ${outcome.priceAtAnalysis.toStringAsFixed(2)}',
              ),
              Text(
                'الإغلاق: ${outcome.sessionClose?.toStringAsFixed(2) ?? '-'}',
              ),
              Text('أقصى صعود: ${formatBasisPoints(outcome.maxUpsideBp)}'),
              Text('أقصى هبوط: ${formatBasisPoints(outcome.maxDrawdownBp)}'),
              Text(
                'الاتجاه: ${outcome.directionCorrect == true ? 'تحقق' : 'لم يتحقق'}',
              ),
              Text('الهدف الأول: ${_flag(outcome.targetOneHit)}'),
              Text('الهدف الثاني: ${_flag(outcome.targetTwoHit)}'),
              Text('وقف الخسارة: ${_flag(outcome.stopLossHit)}'),
            ] else
              Text(
                'السبب: ${outcome.evidence['reason'] ?? 'البيانات غير مكتملة'}',
              ),
            if (outcome.correctionCount > 0)
              Text('عدد التصحيحات المدققة: ${outcome.correctionCount}'),
            if (canCorrect) ...[
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: onCorrect,
                icon: const Icon(Icons.edit_note_rounded),
                label: const Text('تصحيح بيانات الجلسة مع سجل تدقيق'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _CorrectionDialog extends StatefulWidget {
  const _CorrectionDialog({required this.outcome});

  final PerformanceOutcome outcome;

  @override
  State<_CorrectionDialog> createState() => _CorrectionDialogState();
}

class _CorrectionDialogState extends State<_CorrectionDialog> {
  late final TextEditingController _reason;
  late final TextEditingController _open;
  late final TextEditingController _high;
  late final TextEditingController _low;
  late final TextEditingController _close;
  late final TextEditingController _provider;
  late final TextEditingController _fingerprint;
  String? _validationError;

  @override
  void initState() {
    super.initState();
    _reason = TextEditingController();
    _open = TextEditingController(text: '${widget.outcome.sessionOpen ?? ''}');
    _high = TextEditingController(text: '${widget.outcome.sessionHigh ?? ''}');
    _low = TextEditingController(text: '${widget.outcome.sessionLow ?? ''}');
    _close = TextEditingController(
      text: '${widget.outcome.sessionClose ?? ''}',
    );
    _provider = TextEditingController(
      text: widget.outcome.provider ?? 'manual',
    );
    _fingerprint = TextEditingController(
      text: '${widget.outcome.evidence['data_fingerprint'] ?? ''}',
    );
  }

  @override
  void dispose() {
    for (final controller in [
      _reason,
      _open,
      _high,
      _low,
      _close,
      _provider,
      _fingerprint,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('تصحيح ${widget.outcome.ticker}'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _field(_reason, 'سبب التصحيح'),
            _number(_open, 'الافتتاح'),
            _number(_high, 'الأعلى'),
            _number(_low, 'الأدنى'),
            _number(_close, 'الإغلاق'),
            _field(_provider, 'المزود'),
            _field(_fingerprint, 'بصمة البيانات'),
            if (_validationError != null)
              Text(
                _validationError!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
                textAlign: TextAlign.center,
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        FilledButton(onPressed: _submit, child: const Text('حفظ التصحيح')),
      ],
    );
  }

  Widget _field(TextEditingController controller, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextField(
        controller: controller,
        decoration: InputDecoration(labelText: label),
      ),
    );
  }

  Widget _number(TextEditingController controller, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextField(
        controller: controller,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label),
      ),
    );
  }

  void _submit() {
    final values = [
      double.tryParse(_open.text.trim()),
      double.tryParse(_high.text.trim()),
      double.tryParse(_low.text.trim()),
      double.tryParse(_close.text.trim()),
    ];
    if (_reason.text.trim().length < 8) {
      _showValidation('سبب التصحيح يجب ألا يقل عن 8 أحرف.');
      return;
    }
    if (_provider.text.trim().length < 2) {
      _showValidation('اسم مزود البيانات غير صالح.');
      return;
    }
    if (_fingerprint.text.trim().length < 4) {
      _showValidation('بصمة البيانات يجب ألا تقل عن 4 أحرف.');
      return;
    }
    if (values.any((value) => value == null || value <= 0)) {
      _showValidation('أدخل أسعارًا موجبة وصحيحة لكل حقول الجلسة.');
      return;
    }

    final open = values[0]!;
    final high = values[1]!;
    final low = values[2]!;
    final close = values[3]!;
    if (high < open || high < close || high < low) {
      _showValidation('سعر الأعلى يجب أن يكون أكبر من باقي أسعار الجلسة.');
      return;
    }
    if (low > open || low > close || low > high) {
      _showValidation('سعر الأدنى يجب أن يكون أقل من باقي أسعار الجلسة.');
      return;
    }

    Navigator.pop(
      context,
      _CorrectionData(
        reason: _reason.text.trim(),
        open: open,
        high: high,
        low: low,
        close: close,
        provider: _provider.text.trim(),
        fingerprint: _fingerprint.text.trim(),
        dataAsOf: widget.outcome.dataAsOf ?? DateTime.now().toUtc(),
      ),
    );
  }

  void _showValidation(String message) {
    setState(() => _validationError = message);
  }
}

class _CorrectionData {
  const _CorrectionData({
    required this.reason,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.provider,
    required this.fingerprint,
    required this.dataAsOf,
  });

  final String reason;
  final double open;
  final double high;
  final double low;
  final double close;
  final String provider;
  final String fingerprint;
  final DateTime dataAsOf;
}

String _flag(bool? value) {
  if (value == null) return 'غير محدد';
  return value ? 'تحقق' : 'لم يتحقق';
}

```

---

### File: `lib\features\performance\performance_repository.dart`

```dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'performance_models.dart';

class PerformanceRepository {
  const PerformanceRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<PerformanceSummary> summary(int window) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/performance/summary',
        queryParameters: <String, dynamic>{'window': window},
      );
      return PerformanceSummary.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PerformanceReportPage> reports({
    int limit = 30,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/performance/reports',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return PerformanceReportPage.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PerformanceReportDetail> reportDetail(String reportId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/performance/reports/$reportId',
      );
      return PerformanceReportDetail.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<PerformanceDelayedItem>> delayed() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/performance/ledger-delayed',
        queryParameters: const <String, dynamic>{'limit': 100},
      );
      final payload = _required(response.data);
      return _list(payload['items'])
          .map((item) => PerformanceDelayedItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> evaluateDue({int limit = 20}) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/performance/evaluate-due',
        data: <String, dynamic>{'limit': limit},
      );
      return _required(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> retryReport(String reportId) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/performance/evaluations/$reportId/retry',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<String> exportCsv(int window) async {
    try {
      final response = await _apiClient.dio.get<String>(
        '/admin/operations/performance/export.csv',
        queryParameters: <String, dynamic>{'window': window},
        options: Options(responseType: ResponseType.plain),
      );
      return response.data ?? '';
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> correctOutcome({
    required String outcomeId,
    required String reason,
    required double sessionOpen,
    required double sessionHigh,
    required double sessionLow,
    required double sessionClose,
    required String provider,
    required String dataFingerprint,
    required DateTime dataAsOf,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/performance/outcomes/$outcomeId/corrections',
        data: <String, dynamic>{
          'reason': reason.trim(),
          'session_open': sessionOpen,
          'session_high': sessionHigh,
          'session_low': sessionLow,
          'session_close': sessionClose,
          'provider': provider.trim(),
          'data_fingerprint': dataFingerprint.trim(),
          'data_as_of': dataAsOf.toUtc().toIso8601String(),
        },
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Performance response is empty.');
    }
    return value;
  }

  List<dynamic> _list(Object? value) => value is List ? value : const [];

  Map<String, dynamic> _map(Object? value) => value is Map<String, dynamic>
      ? value
      : value is Map
      ? Map<String, dynamic>.from(value)
      : <String, dynamic>{};
}

final performanceRepositoryProvider = Provider<PerformanceRepository>((ref) {
  return PerformanceRepository(ref.watch(apiClientProvider));
});

```

---

### File: `lib\features\performance\performance_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'performance_models.dart';
import 'performance_providers.dart';
import 'performance_widgets.dart';

class PerformanceScreen extends ConsumerWidget {
  const PerformanceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final window = ref.watch(performanceWindowProvider);
    final summary = ref.watch(performanceSummaryProvider);
    final reports = ref.watch(performanceReportsProvider);

    Future<void> refresh() async {
      await Future.wait([
        ref.refresh(performanceSummaryProvider.future),
        ref.refresh(performanceReportsProvider.future),
      ]);
    }

    return Scaffold(
      appBar: AppBar(title: const Text('سجل الأداء الفعلي')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: refresh,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              const PerformanceNotice(),
              const SizedBox(height: 14),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: SegmentedButton<int>(
                  showSelectedIcon: false,
                  segments: const [
                    ButtonSegment(value: 7, label: Text('آخر 7 جلسات')),
                    ButtonSegment(value: 30, label: Text('آخر 30 جلسة')),
                  ],
                  selected: <int>{window},
                  onSelectionChanged: (selection) {
                    ref.read(performanceWindowProvider.notifier).state =
                        selection.single;
                  },
                ),
              ),
              const SizedBox(height: 16),
              summary.when(
                loading: () => const PerformanceLoading(),
                error: (_, __) => PerformanceFailure(
                  message: 'تعذر تحميل إحصاءات الأداء.',
                  retry: () => ref.invalidate(performanceSummaryProvider),
                ),
                data: (value) => _SummarySection(summary: value),
              ),
              const SizedBox(height: 20),
              Text(
                'سجل الجلسات',
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 10),
              reports.when(
                loading: () => const PerformanceLoading(),
                error: (_, __) => PerformanceFailure(
                  message: 'تعذر تحميل سجل التقارير.',
                  retry: () => ref.invalidate(performanceReportsProvider),
                ),
                data: (page) => page.items.isEmpty
                    ? const Card(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Text(
                            'لا توجد جلسات قابلة للقياس حتى الآن.',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : Column(
                        children: page.items
                            .map((item) => _ReportCard(item: item))
                            .toList(growable: false),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SummarySection extends StatelessWidget {
  const _SummarySection({required this.summary});

  final PerformanceSummary summary;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'جودة البيانات',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 10),
                LinearProgressIndicator(
                  value: performanceProgress(summary.dataCompletenessPct),
                  minHeight: 10,
                  borderRadius: BorderRadius.circular(20),
                ),
                const SizedBox(height: 8),
                Text(
                  '${summary.dataCompletenessPct.toStringAsFixed(1)}% مكتملة • '
                  '${summary.completeSessions}/${summary.sessionsFound} جلسة مكتملة',
                ),
                if (summary.pendingItems > 0 || summary.failedItems > 0)
                  Text(
                    '${summary.pendingItems} تنتظر البيانات • '
                    '${summary.failedItems} فشلت في التقييم',
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (summary.evaluatedItems == 0)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(18),
              child: Text(
                'لم تكتمل أي نتيجة فعلية في المدة المختارة بعد. ستظهر المقاييس فور توفر بيانات إغلاق الجلسات.',
                textAlign: TextAlign.center,
              ),
            ),
          )
        else ...[
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              PerformanceMetric(
                label: 'متوسط الحركة',
                value: formatBasisPoints(summary.averageReturnBp),
              ),
              PerformanceMetric(
                label: 'وسيط الحركة',
                value: formatBasisPoints(summary.medianReturnBp),
              ),
              PerformanceMetric(
                label: 'الأسهم الصاعدة',
                value: '${summary.positiveCount}',
              ),
              PerformanceMetric(
                label: 'الأسهم الهابطة',
                value: '${summary.negativeCount}',
              ),
              PerformanceMetric(
                label: 'نسبة الصعود',
                value: formatPercent(summary.positiveRatePct),
              ),
              PerformanceMetric(
                label: 'دقة الاتجاه',
                value: formatPercent(summary.directionAccuracyPct),
              ),
              PerformanceMetric(
                label: 'تحقق الهدف الأول',
                value: formatPercent(summary.targetOneHitRatePct),
              ),
              PerformanceMetric(
                label: 'لمس وقف الخسارة',
                value: formatPercent(summary.stopLossHitRatePct),
              ),
            ],
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, constraints) {
              final cards = [
                Expanded(
                  child: PerformanceExtreme(
                    title: 'أفضل نتيجة',
                    item: summary.bestOutcome,
                  ),
                ),
                Expanded(
                  child: PerformanceExtreme(
                    title: 'أسوأ نتيجة',
                    item: summary.worstOutcome,
                  ),
                ),
              ];
              if (constraints.maxWidth >= 360) {
                return Row(
                  children: [
                    cards.first,
                    const SizedBox(width: 10),
                    cards.last,
                  ],
                );
              }
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  PerformanceExtreme(
                    title: 'أفضل نتيجة',
                    item: summary.bestOutcome,
                  ),
                  PerformanceExtreme(
                    title: 'أسوأ نتيجة',
                    item: summary.worstOutcome,
                  ),
                ],
              );
            },
          ),
          const SizedBox(height: 18),
          Text(
            'أداء المراكز من 1 إلى 10',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          Card(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('المركز')),
                  DataColumn(label: Text('النتائج')),
                  DataColumn(label: Text('المتوسط')),
                  DataColumn(label: Text('الصعود')),
                  DataColumn(label: Text('دقة الاتجاه')),
                ],
                rows: summary.ranks
                    .map(
                      (rank) => DataRow(
                        cells: [
                          DataCell(Text('${rank.rank}')),
                          DataCell(Text('${rank.evaluatedItems}')),
                          DataCell(
                            Text(formatBasisPoints(rank.averageReturnBp)),
                          ),
                          DataCell(Text(formatPercent(rank.positiveRatePct))),
                          DataCell(
                            Text(formatPercent(rank.directionAccuracyPct)),
                          ),
                        ],
                      ),
                    )
                    .toList(growable: false),
              ),
            ),
          ),
        ],
        if (summary.benchmark['status'] != 'available')
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'المقارنة مع EGX30 غير متاحة بعد، لذلك لا يتم عرض مقارنة تقديرية غير موثقة.',
              ),
            ),
          ),
      ],
    );
  }
}

class _ReportCard extends StatelessWidget {
  const _ReportCard({required this.item});

  final PerformanceReportListItem item;

  @override
  Widget build(BuildContext context) {
    final date = formatPerformanceDate(item.targetSessionDate);
    final status = performanceStatusLabel(item.evaluationStatus);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        onTap: () => context.push('/performance/reports/${item.reportId}'),
        isThreeLine: true,
        leading: CircleAvatar(child: Text('${item.evaluatedItems}')),
        title: Text(date, maxLines: 2, overflow: TextOverflow.ellipsis),
        subtitle: Text(
          '$status • ${item.dataCompletenessPct.toStringAsFixed(0)}% مكتملة\n'
          'متوسط ${formatBasisPoints(item.averageReturnBp)} • '
          '${item.positiveCount} صاعدة / ${item.negativeCount} هابطة',
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: const Icon(Icons.chevron_left_rounded),
      ),
    );
  }
}

```

---

### File: `lib\features\performance\performance_widgets.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart' show DateFormat;

import 'performance_models.dart';

String formatBasisPoints(int? value) {
  if (value == null) return '-';
  final percent = value / 100;
  return '${percent > 0 ? '+' : ''}${percent.toStringAsFixed(2)}%';
}

String formatPercent(double? value) {
  return value == null ? '-' : '${value.toStringAsFixed(1)}%';
}

String formatPerformanceDate(DateTime value, {bool includeTime = false}) {
  final local = value.toLocal();
  try {
    return DateFormat(
      includeTime ? 'd MMM yyyy – HH:mm' : 'EEEE d MMMM yyyy',
      'ar',
    ).format(local);
  } on Object {
    final day = local.day.toString().padLeft(2, '0');
    final month = local.month.toString().padLeft(2, '0');
    final year = local.year.toString();
    if (!includeTime) return '$day/$month/$year';
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');
    return '$day/$month/$year – $hour:$minute';
  }
}

double performanceProgress(double percent) {
  return (percent.clamp(0, 100) / 100).toDouble();
}

String performanceStatusLabel(String status) {
  return switch (status) {
    'complete' => 'مكتمل',
    'partial' => 'مكتمل جزئيًا',
    'pending' || 'pending_data' => 'بانتظار البيانات',
    'running' => 'جارٍ التقييم',
    'failed' => 'تعذر التقييم',
    'not_started' => 'لم يبدأ التقييم',
    'empty_report' => 'التقرير بلا نتائج',
    _ => status.trim().isEmpty ? 'غير محدد' : status,
  };
}

class PerformanceNotice extends StatelessWidget {
  const PerformanceNotice({super.key});

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.fact_check_outlined),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                'يعرض السجل النتائج الفعلية كما حدثت، بما فيها النتائج السلبية والبيانات الناقصة. الأداء السابق لا يضمن نتائج مستقبلية.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class PerformanceMetric extends StatelessWidget {
  const PerformanceMetric({
    required this.label,
    required this.value,
    super.key,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 156,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 6),
              Text(
                value,
                textDirection: TextDirection.ltr,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class PerformanceExtreme extends StatelessWidget {
  const PerformanceExtreme({
    required this.title,
    required this.item,
    super.key,
  });

  final String title;
  final PerformanceBestWorst? item;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title),
            const SizedBox(height: 6),
            Text(
              item?.ticker ?? '-',
              textDirection: TextDirection.ltr,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            Text(item == null ? '-' : formatBasisPoints(item!.returnBp)),
          ],
        ),
      ),
    );
  }
}

class PerformanceLoading extends StatelessWidget {
  const PerformanceLoading({super.key});

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class PerformanceFailure extends StatelessWidget {
  const PerformanceFailure({
    required this.message,
    required this.retry,
    super.key,
  });

  final String message;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: retry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\profile\profile_edit_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../../core/config/app_config.dart';
import '../../core/network/api_client.dart';
import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';

final avatarOptionsProvider = FutureProvider.autoDispose<List<AvatarOption>>((
  ref,
) {
  return ref.watch(backendRepositoryProvider).getAvatarOptions();
});

class ProfileEditScreen extends ConsumerStatefulWidget {
  const ProfileEditScreen({super.key});

  @override
  ConsumerState<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends ConsumerState<ProfileEditScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late String _avatarKey;
  bool _saving = false;
  bool _deleting = false;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(sessionControllerProvider).profile;
    _nameController = TextEditingController(text: profile?.displayName ?? '');
    _avatarKey = profile?.avatarKey ?? avatarKeys.first;
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _saving) {
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(sessionControllerProvider.notifier)
          .updateProfile(
            displayName: _nameController.text,
            avatarKey: _avatarKey,
          );
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('تم تحديث الملف الشخصي.')));
      Navigator.of(context).pop();
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  Future<void> _deleteAccount() async {
    if (_deleting) {
      return;
    }
    final passwordController = TextEditingController();
    final password = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('حذف الحساب نهائيًا'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'سيتم إلغاء جلساتك وإخفاء البريد والاسم، ولن تتمكن من استعادة الحساب. إذا كان لديك اشتراك مدفوع عبر Google Play، فحذف الحساب لا يلغي التجديد التلقائي؛ ألغِ الاشتراك من Google Play أولًا لتجنب أي تجديد لاحق. أدخل كلمة المرور للتأكيد.',
            ),
            const SizedBox(height: 16),
            TextField(
              controller: passwordController,
              obscureText: true,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'كلمة المرور الحالية',
                prefixIcon: Icon(Icons.lock_outline_rounded),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(dialogContext).colorScheme.error,
            ),
            onPressed: () {
              final value = passwordController.text;
              if (value.isNotEmpty) {
                Navigator.pop(dialogContext, value);
              }
            },
            child: const Text('تأكيد الحذف'),
          ),
        ],
      ),
    );
    passwordController.dispose();
    if (password == null || !mounted) {
      return;
    }

    setState(() => _deleting = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.delete<Map<String, dynamic>>(
        '/profile/me',
        data: <String, dynamic>{'password': password},
      );
      await ref.read(sessionControllerProvider.notifier).logout();
    } on Object catch (error) {
      if (mounted) {
        final message = ref.read(apiClientProvider).mapError(error).message;
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(message)));
      }
    } finally {
      if (mounted) {
        setState(() => _deleting = false);
      }
    }
  }

  Future<void> _copyLegalUrl(String path) async {
    final baseUrl = ref
        .read(appConfigProvider)
        .apiBaseUrl
        .replaceFirst(RegExp(r'/+$'), '');
    await Clipboard.setData(ClipboardData(text: '$baseUrl$path'));
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('تم نسخ الرابط.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final avatars = ref.watch(avatarOptionsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('تعديل الملف الشخصي')),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Center(
                child: CircleAvatar(
                  radius: 52,
                  backgroundImage: AssetImage(avatarAssetPath(_avatarKey)),
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _nameController,
                maxLength: 60,
                decoration: const InputDecoration(
                  labelText: 'الاسم الظاهر',
                  prefixIcon: Icon(Icons.badge_outlined),
                ),
                validator: (value) {
                  final cleaned = value?.trim() ?? '';
                  return cleaned.length < 2 ? 'الاسم قصير جدًا.' : null;
                },
              ),
              const SizedBox(height: 18),
              Text(
                'اختر الصورة الرمزية',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 12),
              avatars.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stackTrace) => Column(
                  children: [
                    const Text('تعذر تحميل قائمة الصور من الخادم.'),
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: () => ref.invalidate(avatarOptionsProvider),
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
                data: (options) => GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                  ),
                  itemCount: options.length,
                  itemBuilder: (context, index) {
                    final option = options[index];
                    final selected = option.key == _avatarKey;
                    return InkWell(
                      borderRadius: BorderRadius.circular(22),
                      onTap: () => setState(() => _avatarKey = option.key),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 180),
                        padding: const EdgeInsets.all(5),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(
                            width: selected ? 3 : 1,
                            color: selected
                                ? Theme.of(context).colorScheme.primary
                                : Theme.of(context).colorScheme.outlineVariant,
                          ),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(17),
                          child: Image.asset(
                            avatarAssetPath(option.key),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _saving ? null : _save,
                icon: _saving
                    ? const SizedBox.square(
                        dimension: 20,
                        child: CircularProgressIndicator(strokeWidth: 2.5),
                      )
                    : const Icon(Icons.save_outlined),
                label: const Text('حفظ التعديلات'),
              ),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'الخصوصية والحساب',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'الصفحات القانونية منشورة على خادم التطبيق ويمكن استخدام روابطها في Google Play.',
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton.icon(
                        onPressed: () => _copyLegalUrl('/privacy'),
                        icon: const Icon(Icons.copy_rounded),
                        label: const Text('نسخ رابط سياسة الخصوصية'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () => _copyLegalUrl('/delete-account'),
                        icon: const Icon(Icons.copy_rounded),
                        label: const Text('نسخ رابط حذف الحساب'),
                      ),
                      const Divider(height: 28),
                      FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: Theme.of(context).colorScheme.error,
                        ),
                        onPressed: _deleting ? null : _deleteAccount,
                        icon: _deleting
                            ? const SizedBox.square(
                                dimension: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                ),
                              )
                            : const Icon(Icons.delete_forever_outlined),
                        label: const Text('حذف الحساب نهائيًا'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\reports\market_report_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'report_providers.dart';

class MarketReportScreen extends ConsumerStatefulWidget {
  const MarketReportScreen({required this.reportId, this.preview, super.key});

  final String reportId;
  final MarketReportPreview? preview;

  @override
  ConsumerState<MarketReportScreen> createState() => _MarketReportScreenState();
}

class _MarketReportScreenState extends ConsumerState<MarketReportScreen> {
  MarketReport? _report;
  bool _loading = false;
  bool _locked = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _locked = widget.preview?.unlocked == false;
    if (!_locked) {
      _loadReport();
    }
  }

  Future<void> _loadReport() async {
    if (_loading) {
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final report = await ref
          .read(backendRepositoryProvider)
          .getMarketReport(widget.reportId);
      if (mounted) {
        setState(() {
          _report = report;
          _locked = false;
        });
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() {
          _locked = error.statusCode == 402;
          _error = error.statusCode == 402 ? null : error.message;
        });
      }
    } on Object {
      if (mounted) {
        setState(
          () => _error = 'تعذر عرض التقرير. حدّث التطبيق وحاول مرة أخرى.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _unlock() async {
    if (_loading) {
      return;
    }
    final cost = widget.preview?.unlockCostCoins ?? '1.00';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('فتح تقرير أفضل 10'),
        content: Text(
          'سيتم خصم $cost عملة مرة واحدة فقط. بعد الفتح سيظل التقرير متاحًا لهذا الحساب دون خصم متكرر.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('فتح التقرير'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final execution = await ref
          .read(backendRepositoryProvider)
          .unlockMarketReport(widget.reportId);
      if (!mounted) {
        return;
      }
      setState(() {
        _report = execution.report;
        _locked = false;
      });
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
        ref.invalidate(walletSummaryProvider);
        ref.invalidate(latestReportPreviewProvider);
      } on Object {
        // The purchased report must remain visible if the optional balance refresh fails.
      }
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            execution.chargedPoints == 0
                ? 'التقرير كان مفتوحًا بالفعل ولم يحدث خصم جديد.'
                : 'تم فتح التقرير وخصم ${execution.chargedCoins} عملة.',
          ),
        ),
      );
      if (execution.chargedPoints > 0) {
        await ref
            .read(freePlanInterstitialProvider)
            .recordMeaningfulAction(
              enabled:
                  ref.read(sessionControllerProvider).profile?.adsEnabled ==
                  true,
            );
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } on Object {
      if (mounted) {
        setState(() => _error = 'تعذر فتح التقرير حاليًا. حاول مرة أخرى.');
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('تقرير أفضل 10')),
      body: SafeArea(child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading && _report == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_locked) {
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  const Icon(Icons.lock_outline_rounded, size: 52),
                  const SizedBox(height: 16),
                  Text(
                    'أسماء الأسهم وتفاصيلها محمية حتى فتح التقرير.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'التكلفة: ${widget.preview?.unlockCostCoins ?? '1.00'} عملة',
                  ),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: _loading ? null : _unlock,
                    icon: const Icon(Icons.lock_open_rounded),
                    label: const Text('فتح التقرير'),
                  ),
                ],
              ),
            ),
          ),
          const FreePlanNativeAd(),
          if (_error != null) _ErrorCard(message: _error!, retry: _unlock),
        ],
      );
    }

    final report = _report;
    if (report == null) {
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _ErrorCard(
            message: _error ?? 'تعذر تحميل التقرير.',
            retry: _loadReport,
          ),
        ],
      );
    }

    return _ReportTabs(report: report);
  }
}

class _ReportTabGroup {
  const _ReportTabGroup({
    required this.label,
    required this.icon,
    required this.items,
    required this.isExtended,
  });

  final String label;
  final IconData icon;
  final List<MarketReportItem> items;
  final bool isExtended;
}

List<_ReportTabGroup> _buildReportTabGroups(MarketReport report) {
  final topTen = report.items.where((item) => item.rank <= 10).toList();
  final allItems = [...topTen, ...report.extendedItems];
  final groups = <_ReportTabGroup>[
    _ReportTabGroup(
      label: 'أفضل 10',
      icon: Icons.stars_rounded,
      items: topTen,
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'نخبة متوازن',
      icon: Icons.verified_rounded,
      items: _byTier(allItems, 'elite', profile: 'balanced'),
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'نخبة هجومي',
      icon: Icons.rocket_launch_rounded,
      items: _byTier(allItems, 'elite', profile: 'aggressive'),
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'شراء بجودة أعلى',
      icon: Icons.auto_awesome_rounded,
      items: _byTier(allItems, 'conditional_buy_high_quality'),
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'شراء مشروط',
      icon: Icons.shopping_bag_rounded,
      items: _byTier(allItems, 'conditional_buy'),
      isExtended: true,
    ),
    _ReportTabGroup(
      label: 'مراقبة',
      icon: Icons.visibility_rounded,
      items: _byTier(allItems, 'watch'),
      isExtended: true,
    ),
  ];
  return groups.where((group) => group.items.isNotEmpty).toList();
}

List<MarketReportItem> _byTier(
  List<MarketReportItem> items,
  String tier, {
  String? profile,
}) {
  return items.where((item) {
    final itemTier = _text(item.payload['opportunity_tier']);
    if (itemTier != tier) {
      return false;
    }
    if (profile != null && _text(item.payload['elite_profile']) != profile) {
      return false;
    }
    return true;
  }).toList();
}

class _ReportTabs extends StatelessWidget {
  const _ReportTabs({required this.report});

  final MarketReport report;

  @override
  Widget build(BuildContext context) {
    final groups = _buildReportTabGroups(report);
    return DefaultTabController(
      length: groups.length,
      child: Column(
        children: [
          Flexible(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'الجلسة المستهدفة',
                            style: Theme.of(context).textTheme.labelLarge,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _formatArabicDate(report.targetSessionDate),
                            style: Theme.of(context).textTheme.titleLarge
                                ?.copyWith(fontWeight: FontWeight.w900),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'الترتيب ناتج عن التحليل الآلي ولا يمثل ضمانًا للربح.',
                          ),
                        ],
                      ),
                    ),
                  ),
                  _MarketSummaryCard(summary: report.marketSummary),
                  const FreePlanNativeAd(),
                ],
              ),
            ),
          ),
          Material(
            color: Theme.of(context).colorScheme.surface,
            child: TabBar(
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              tabs: [
                for (final group in groups)
                  Tab(
                    text: group.label == 'أفضل 10'
                        ? group.label
                        : '${group.label} (${group.items.length})',
                    icon: Icon(group.icon),
                  ),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              children: [
                for (final group in groups)
                  ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      for (final item in group.items)
                        if (group.isExtended)
                          _SafeExtendedItemCard(
                            key: ValueKey('ext-${item.ticker}'),
                            item: item,
                          )
                        else
                          _SafeReportItemCard(
                            key: ValueKey('top-${item.ticker}'),
                            item: item,
                          ),
                    ],
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MarketSummaryCard extends StatelessWidget {
  const _MarketSummaryCard({required this.summary});

  final Map<String, dynamic> summary;

  @override
  Widget build(BuildContext context) {
    final analyzed = _integer(summary['analyzed_count']);
    final eligible = _integer(summary['eligible_count']);
    final failed = _integer(summary['failed_count']);
    final averageScore = _number(summary['average_top_score']);
    final signals = _map(summary['signals']);
    final buyCount = _integer(signals['BUY']);
    final watchCount = _integer(signals['WATCH']);
    final title = _text(summary['title']);
    final disclaimer = _text(summary['disclaimer']);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'ملخص السوق',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            if (title.isNotEmpty) ...[const SizedBox(height: 6), Text(title)],
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _MetricChip(label: 'تم تحليلها', value: '$analyzed'),
                _MetricChip(label: 'مؤهلة', value: '$eligible'),
                _MetricChip(label: 'تعذر تحليلها', value: '$failed'),
                _MetricChip(
                  label: 'متوسط الدرجة',
                  value: averageScore.toStringAsFixed(1),
                ),
                _MetricChip(label: 'شراء', value: '$buyCount'),
                _MetricChip(label: 'مراقبة', value: '$watchCount'),
              ],
            ),
            if (disclaimer.isNotEmpty) ...[
              const SizedBox(height: 14),
              Text(disclaimer, style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }
}

class _SafeReportItemCard extends StatelessWidget {
  const _SafeReportItemCard({required this.item, super.key});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    try {
      return _ReportItemCard(item: item);
    } on Object {
      return Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: ListTile(
          leading: CircleAvatar(child: Text('${item.rank}')),
          title: Text(item.ticker, textDirection: TextDirection.ltr),
          subtitle: const Text('تعذر عرض بعض تفاصيل هذا السهم.'),
        ),
      );
    }
  }
}

class _ReportItemCard extends StatelessWidget {
  const _ReportItemCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    final payload = item.payload;
    final analysis = _map(payload['analysis']);
    final tradePlan = _map(analysis['trade_plan']);
    final engines = _map(analysis['engines']);
    final technical = _map(_map(engines['technical'])['details']);
    final risk = _map(_map(engines['risk'])['details']);

    final decision = _text(payload['decision']).isNotEmpty
        ? _text(payload['decision'])
        : _signalLabel(_text(payload['signal']));
    final confidence = _number(payload['confidence']);
    final price = _number(payload['price_at_analysis']);
    final entry = _number(tradePlan['entry']);
    final stop = _number(tradePlan['stop_loss']);
    final target1 = _number(tradePlan['target_1']);
    final target2 = _number(tradePlan['target_2']);
    final rewardRisk = _number(tradePlan['reward_risk_1']);
    final explanation = _text(payload['explanation']);
    final trend = _trendLabel(_text(technical['trend']));
    final rsi = _number(technical['rsi']);
    final volumeRatio = _number(technical['volume_ratio']);
    final riskLevel = _riskLabel(_text(risk['risk_level']));
    final reasons = _collectReasons(engines);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${item.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(decision.isEmpty ? 'مراقبة' : decision),
                    ],
                  ),
                ),
                Chip(label: Text('${item.score.toStringAsFixed(1)} / 100')),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _MetricChip(
                  label: 'الثقة',
                  value: '${confidence.toStringAsFixed(1)}%',
                ),
                _MetricChip(label: 'السعر', value: _price(price)),
                _MetricChip(label: 'الاتجاه', value: trend),
                _MetricChip(label: 'المخاطرة', value: riskLevel),
              ],
            ),
            if (entry > 0 || stop > 0 || target1 > 0) ...[
              const SizedBox(height: 14),
              Text(
                'خطة التداول',
                style: Theme.of(
                  context,
                ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              _ValueRow(label: 'الدخول', value: _price(entry)),
              _ValueRow(label: 'وقف الخسارة', value: _price(stop)),
              _ValueRow(label: 'الهدف الأول', value: _price(target1)),
              _ValueRow(label: 'الهدف الثاني', value: _price(target2)),
              _ValueRow(
                label: 'العائد مقابل المخاطرة',
                value: rewardRisk > 0
                    ? '${rewardRisk.toStringAsFixed(1)} : 1'
                    : '—',
              ),
            ],
            if (rsi > 0 || volumeRatio > 0) ...[
              const Divider(height: 24),
              _ValueRow(
                label: 'مؤشر RSI',
                value: rsi > 0 ? rsi.toStringAsFixed(1) : '—',
              ),
              _ValueRow(
                label: 'نسبة الحجم',
                value: volumeRatio > 0 ? volumeRatio.toStringAsFixed(2) : '—',
              ),
            ],
            if (reasons.isNotEmpty) ...[
              const Divider(height: 24),
              Text(
                'أسباب الاختيار',
                style: Theme.of(
                  context,
                ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 6),
              for (final reason in reasons.take(5))
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text('• ${_reasonLabel(reason)}'),
                ),
            ],
            if (explanation.isNotEmpty) ...[
              const Divider(height: 24),
              Text(explanation),
            ],
          ],
        ),
      ),
    );
  }
}

class _SafeExtendedItemCard extends StatelessWidget {
  const _SafeExtendedItemCard({required this.item, super.key});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    try {
      return _ExtendedItemCard(item: item);
    } on Object {
      return Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: ListTile(
          leading: CircleAvatar(child: Text('${item.rank}')),
          title: Text(item.ticker, textDirection: TextDirection.ltr),
          subtitle: const Text('تعذر عرض بعض تفاصيل هذا السهم.'),
        ),
      );
    }
  }
}

class _ExtendedItemCard extends StatelessWidget {
  const _ExtendedItemCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    final payload = item.payload;
    final tier = _text(payload['opportunity_tier']);
    final decision = _text(payload['decision']).isNotEmpty
        ? _text(payload['decision'])
        : _signalLabel(_text(payload['signal']));
    final price = _number(payload['price_at_analysis']);
    final plan = _map(payload['trade_plan']);
    final entry = _number(plan['entry']);
    final stop = _number(plan['stop_loss']);
    final target1 = _number(plan['target_1']);
    final target2 = _number(plan['target_2']);
    final rewardRisk = _number(plan['reward_risk_1']);
    final explanation = _text(payload['explanation']);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${item.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(decision.isEmpty ? 'مراقبة' : decision),
                    ],
                  ),
                ),
                Chip(label: Text('${item.score.toStringAsFixed(1)} / 100')),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (tier.isNotEmpty)
                  _MetricChip(label: 'الدرجة', value: _tierLabel(tier)),
                _MetricChip(label: 'السعر', value: _price(price)),
              ],
            ),
            if (entry > 0 || stop > 0 || target1 > 0) ...[
              const SizedBox(height: 14),
              Text(
                'خطة التداول',
                style: Theme.of(
                  context,
                ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              _ValueRow(label: 'الدخول', value: _price(entry)),
              _ValueRow(label: 'وقف الخسارة', value: _price(stop)),
              _ValueRow(label: 'الهدف الأول', value: _price(target1)),
              _ValueRow(label: 'الهدف الثاني', value: _price(target2)),
              _ValueRow(
                label: 'العائد مقابل المخاطرة',
                value: rewardRisk > 0
                    ? '${rewardRisk.toStringAsFixed(1)} : 1'
                    : '—',
              ),
            ],
            if (explanation.isNotEmpty) ...[
              const Divider(height: 24),
              Text(explanation),
            ],
          ],
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Chip(label: Text('$label: $value'));
  }
}

class _ValueRow extends StatelessWidget {
  const _ValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Expanded(child: Text(label)),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message, required this.retry});

  final String message;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: retry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

String _formatArabicDate(DateTime value) {
  const weekdays = <String>[
    'الاثنين',
    'الثلاثاء',
    'الأربعاء',
    'الخميس',
    'الجمعة',
    'السبت',
    'الأحد',
  ];
  const months = <String>[
    'يناير',
    'فبراير',
    'مارس',
    'أبريل',
    'مايو',
    'يونيو',
    'يوليو',
    'أغسطس',
    'سبتمبر',
    'أكتوبر',
    'نوفمبر',
    'ديسمبر',
  ];
  final local = value.toLocal();
  return '${weekdays[local.weekday - 1]} ${local.day} ${months[local.month - 1]} ${local.year}';
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

String _text(Object? value) => value is String ? value.trim() : '';

double _number(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse('$value') ?? 0;
}

int _integer(Object? value) => _number(value).round();

String _price(double value) => value > 0 ? value.toStringAsFixed(2) : '—';

String _signalLabel(String value) {
  return switch (value.toUpperCase()) {
    'BUY' => 'فرصة شراء مشروطة',
    'WATCH' => 'للمراقبة',
    'AVOID' => 'تجنب حاليًا',
    _ => value,
  };
}

String _tierLabel(String tier) {
  return switch (tier) {
    'elite' => 'نخبة',
    'elite_balanced' => 'نخبة متوازن',
    'elite_aggressive' => 'نخبة هجومي',
    'conditional_buy_high_quality' => 'شراء بجودة أعلى',
    'conditional_buy' => 'شراء مشروط',
    'watch' => 'مراقبة',
    _ => tier,
  };
}

String _trendLabel(String value) {
  return switch (value.toLowerCase()) {
    'uptrend' || 'bullish' || 'weak_bullish' => 'صاعد',
    'downtrend' || 'bearish' || 'weak_bearish' => 'هابط',
    'sideways' || 'neutral' => 'عرضي',
    _ => value.isEmpty ? 'غير محدد' : value,
  };
}

String _riskLabel(String value) {
  return switch (value.toLowerCase()) {
    'low' => 'منخفضة',
    'medium' => 'متوسطة',
    'high' => 'مرتفعة',
    _ => value.isEmpty ? 'غير محددة' : value,
  };
}

List<String> _collectReasons(Map<String, dynamic> engines) {
  final result = <String>[];
  for (final value in engines.values) {
    final engine = _map(value);
    final reasons = engine['reasons'];
    if (reasons is List) {
      result.addAll(
        reasons.whereType<String>().where((reason) => reason.trim().isNotEmpty),
      );
    }
  }
  return result;
}

String _reasonLabel(String reason) {
  const labels = <String, String>{
    'Price above SMA20': 'السعر أعلى من متوسط 20 جلسة',
    'Price above SMA50': 'السعر أعلى من متوسط 50 جلسة',
    'SMA20 above SMA50': 'متوسط 20 أعلى من متوسط 50',
    'Long-term trend positive': 'الاتجاه طويل الأجل إيجابي',
    'MACD bullish': 'مؤشر MACD إيجابي',
    'Timeframe alignment: bullish': 'الأطر الزمنية متوافقة على اتجاه صاعد',
  };
  return labels[reason] ?? reason;
}

```

---

### File: `lib\features\reports\report_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

final latestReportPreviewProvider =
    FutureProvider.autoDispose<MarketReportPreview?>((ref) {
      return ref.watch(backendRepositoryProvider).getLatestReportPreview();
    });

```

---

### File: `lib\features\reports\reports_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/models.dart';
import 'report_providers.dart';

class ReportsScreen extends ConsumerWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final preview = ref.watch(latestReportPreviewProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('تقارير السوق')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(latestReportPreviewProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              'أحدث التقارير التحليلية للبورصة المصرية',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            preview.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stackTrace) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Icon(Icons.error_outline_rounded),
                      const SizedBox(height: 12),
                      Text('تعذر تحميل التقارير.'),
                      TextButton(
                        onPressed: () =>
                            ref.invalidate(latestReportPreviewProvider),
                        child: const Text('إعادة المحاولة'),
                      ),
                    ],
                  ),
                ),
              ),
              data: (report) => report == null
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(40),
                        child: Text('لا توجد تقارير متاحة حاليًا.'),
                      ),
                    )
                  : _ReportPreviewCard(report: report),
            ),
            const SizedBox(height: 24),
            const Text(
              'ملاحظة: يتم إصدار تقارير السوق بشكل دوري بناءً على مسح شامل لجميع الأسهم.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _ReportPreviewCard extends StatelessWidget {
  const _ReportPreviewCard({required this.report});

  final MarketReportPreview report;

  @override
  Widget build(BuildContext context) {
    final target = report.targetSessionDate;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_graph_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'تقرير جلسة ${target.day}/${target.month}/${target.year}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                Chip(label: Text('${report.itemCount} فرص مؤهلة')),
                Chip(
                  label: Text(
                    report.unlocked
                        ? 'مفتوح بالفعل'
                        : '${report.unlockCostCoins} عملة للفتح',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text('المقدمة مجانية ولا تعرض أسماء الأسهم قبل فتح التقرير.'),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: () =>
                  context.push('/reports/${report.reportId}', extra: report),
              icon: Icon(
                report.unlocked
                    ? Icons.visibility_rounded
                    : Icons.lock_open_rounded,
              ),
              label: Text(report.unlocked ? 'عرض التقرير' : 'فتح التقرير'),
            ),
          ],
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\wallet\wallet_history_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';

class WalletHistoryScreen extends ConsumerStatefulWidget {
  const WalletHistoryScreen({super.key});

  @override
  ConsumerState<WalletHistoryScreen> createState() =>
      _WalletHistoryScreenState();
}

class _WalletHistoryScreenState extends ConsumerState<WalletHistoryScreen> {
  static const _pageSize = 20;
  final List<WalletEntryModel> _items = [];
  int _total = 0;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load(reset: true);
  }

  Future<void> _load({required bool reset}) async {
    if (_loading) {
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
      if (reset) {
        _items.clear();
      }
    });
    try {
      final page = await ref
          .read(backendRepositoryProvider)
          .getWalletHistory(
            limit: _pageSize,
            offset: reset ? 0 : _items.length,
          );
      if (!mounted) {
        return;
      }
      setState(() {
        _total = page.total;
        _items.addAll(page.items);
      });
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } on Object {
      if (mounted) {
        setState(
          () =>
              _error = 'تعذر عرض سجل المحفظة. حاول مرة أخرى بعد تحديث التطبيق.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('سجل المحفظة')),
      body: RefreshIndicator(
        onRefresh: () => _load(reset: true),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_items.isEmpty && _loading)
              const Padding(
                padding: EdgeInsets.all(48),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_items.isEmpty && _error != null)
              _MessageCard(
                icon: Icons.cloud_off_outlined,
                message: _error!,
                buttonLabel: 'إعادة المحاولة',
                onPressed: () => _load(reset: true),
              )
            else if (_items.isEmpty)
              const _MessageCard(
                icon: Icons.receipt_long_outlined,
                message: 'لا توجد عمليات في المحفظة حتى الآن.',
              )
            else ...[
              Text(
                'إجمالي العمليات: $_total',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              for (final entry in _items) _WalletEntryCard(entry: entry),
              if (_error != null)
                _MessageCard(
                  icon: Icons.error_outline,
                  message: _error!,
                  buttonLabel: 'إعادة المحاولة',
                  onPressed: () => _load(reset: false),
                ),
              if (_items.length < _total)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: OutlinedButton.icon(
                    onPressed: _loading ? null : () => _load(reset: false),
                    icon: _loading
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.expand_more_rounded),
                    label: const Text('تحميل المزيد'),
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class _WalletEntryCard extends StatelessWidget {
  const _WalletEntryCard({required this.entry});

  final WalletEntryModel entry;

  @override
  Widget build(BuildContext context) {
    final positive = entry.amountPoints >= 0;
    final amount = '${positive ? '+' : ''}${entry.amountCoins} عملة';
    final date = _formatArabicDateTime(entry.createdAt);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: CircleAvatar(
          child: Icon(positive ? Icons.add_rounded : Icons.remove_rounded),
        ),
        title: Text(_entryLabel(entry)),
        subtitle: Text('$date\nالحالة: ${_statusLabel(entry.status)}'),
        isThreeLine: true,
        trailing: Text(
          amount,
          textDirection: TextDirection.ltr,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w800,
            color: positive
                ? Colors.green.shade700
                : Theme.of(context).colorScheme.error,
          ),
        ),
      ),
    );
  }

  String _entryLabel(WalletEntryModel entry) {
    switch (entry.entryType) {
      case 'welcome_bonus':
        return 'رصيد ترحيبي';
      case 'weekly_plan_grant':
        return 'توزيع الخطة الأسبوعي';
      case 'stock_analysis_debit':
        return 'تحليل سهم';
      case 'market_report_debit':
        return 'فتح تقرير أفضل 10';
      case 'community_submission_hold':
        return 'حجز مراجعة مناقشة';
      case 'community_submission_refund':
        return 'استرداد مراجعة مناقشة';
      case 'prediction_reward':
        return 'مكافأة توقع';
      case 'rewarded_ad_credit':
      case 'rewarded_ad':
        return 'مكافأة إعلان';
      case 'coin_purchase':
        return 'شراء عملات';
    }
    switch (entry.referenceType) {
      case 'stock_analysis':
        return 'تحليل سهم';
      case 'market_report':
        return 'فتح تقرير أفضل 10';
      case 'weekly_grant':
      case 'subscription':
        return 'توزيع الخطة الأسبوعي';
      case 'discussion':
        return 'عملية مناقشة';
      case 'billing_purchase':
        return 'عملية شراء';
      default:
        return 'عملية بالمحفظة';
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'confirmed':
        return 'مكتملة';
      case 'held':
        return 'محجوزة مؤقتًا';
      case 'released':
        return 'تم ردها';
      case 'pending':
        return 'قيد التنفيذ';
      case 'failed':
        return 'لم تكتمل';
      default:
        return 'مسجلة';
    }
  }
}

String _formatArabicDateTime(DateTime value) {
  const months = <String>[
    'يناير',
    'فبراير',
    'مارس',
    'أبريل',
    'مايو',
    'يونيو',
    'يوليو',
    'أغسطس',
    'سبتمبر',
    'أكتوبر',
    'نوفمبر',
    'ديسمبر',
  ];
  final local = value.toLocal();
  final hour12 = local.hour % 12 == 0 ? 12 : local.hour % 12;
  final minute = local.minute.toString().padLeft(2, '0');
  final period = local.hour < 12 ? 'ص' : 'م';
  return '${local.day} ${months[local.month - 1]} ${local.year}، '
      '$hour12:$minute $period';
}

class _MessageCard extends StatelessWidget {
  const _MessageCard({
    required this.icon,
    required this.message,
    this.buttonLabel,
    this.onPressed,
  });

  final IconData icon;
  final String message;
  final String? buttonLabel;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(icon, size: 42),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            if (buttonLabel != null) ...[
              const SizedBox(height: 12),
              OutlinedButton(onPressed: onPressed, child: Text(buttonLabel!)),
            ],
          ],
        ),
      ),
    );
  }
}

```

---

### File: `lib\features\wallet\wallet_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

final walletSummaryProvider = FutureProvider.autoDispose<WalletSummary>((ref) {
  return ref.watch(backendRepositoryProvider).getWallet();
});

```

---

### File: `lib\widgets\structured_data_card.dart`

```dart
import 'package:flutter/material.dart';

class StructuredDataCard extends StatelessWidget {
  const StructuredDataCard({
    required this.title,
    required this.data,
    this.initiallyExpanded = true,
    super.key,
  });

  final String title;
  final Map<String, dynamic> data;
  final bool initiallyExpanded;

  @override
  Widget build(BuildContext context) {
    if (_isInternalTitle(title)) {
      return const SizedBox.shrink();
    }

    final visibleData = _visibleMap(data);
    if (visibleData.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [_ReadableMap(data: visibleData)],
      ),
    );
  }
}

class _ReadableMap extends StatelessWidget {
  const _ReadableMap({required this.data, this.depth = 0});

  final Map<String, dynamic> data;
  final int depth;

  @override
  Widget build(BuildContext context) {
    final entries = _visibleMap(data).entries.toList(growable: false);
    if (entries.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var index = 0; index < entries.length; index++) ...[
          _ReadableEntry(
            label: _labelFor(entries[index].key),
            value: entries[index].value,
            depth: depth,
          ),
          if (index != entries.length - 1) const Divider(height: 18),
        ],
      ],
    );
  }
}

class _ReadableEntry extends StatelessWidget {
  const _ReadableEntry({
    required this.label,
    required this.value,
    required this.depth,
  });

  final String label;
  final dynamic value;
  final int depth;

  @override
  Widget build(BuildContext context) {
    final currentValue = value;
    if (currentValue is Map<Object?, Object?>) {
      final nested = _visibleMap({
        for (final entry in currentValue.entries)
          entry.key.toString(): entry.value,
      });
      if (nested.isEmpty) {
        return const SizedBox.shrink();
      }
      return ExpansionTile(
        tilePadding: EdgeInsets.zero,
        childrenPadding: const EdgeInsetsDirectional.only(start: 12, bottom: 8),
        initiallyExpanded: depth == 0,
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        children: [_ReadableMap(data: nested, depth: depth + 1)],
      );
    }

    if (currentValue is List<Object?>) {
      if (currentValue.isEmpty) {
        return _ValueRow(label: label, value: 'لا يوجد');
      }
      final readable = currentValue
          .where((item) => item is! Map<Object?, Object?>)
          .map(_formatValue)
          .where((item) => item.isNotEmpty)
          .toList(growable: false);
      if (readable.isEmpty) {
        return const SizedBox.shrink();
      }
      return _ValueRow(label: label, value: readable.join('، '));
    }

    return _ValueRow(label: label, value: _formatValue(currentValue));
  }
}

class _ValueRow extends StatelessWidget {
  const _ValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 4,
          child: Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(flex: 5, child: Text(value, textAlign: TextAlign.end)),
      ],
    );
  }
}

bool _isInternalTitle(String title) {
  final normalized = title.trim().toLowerCase();
  return normalized.contains('البيانات التقنية الخام') ||
      normalized.contains('raw data') ||
      normalized.contains('json');
}

Map<String, dynamic> _visibleMap(Map<String, dynamic> data) {
  return {
    for (final entry in data.entries)
      if (!_hiddenKeys.contains(entry.key) && entry.value != null)
        entry.key: entry.value,
  };
}

const _hiddenKeys = <String>{
  'fingerprint',
  'source_text_sha256',
  'cache_key',
  'version',
  'attempts',
  'attempted_at',
  'actor_type',
  'provider_message_id',
  'request_id',
  'trace_id',
  'debug',
  'diagnostics',
};

const _labels = <String, String>{
  'stage': 'مرحلة الفحص',
  'passed': 'اجتاز الفحص',
  'reason_codes': 'أسباب المراجعة',
  'checks': 'فحوص المحتوى',
  'external_link': 'رابط خارجي',
  'phone_number': 'رقم هاتف',
  'contact_details': 'بيانات تواصل',
  'advertisement': 'محتوى إعلاني',
  'profit_guarantee': 'ضمان ربح',
  'abusive_content': 'محتوى مسيء',
  'review_stage': 'حالة المراجعة',
  'ai': 'مراجعة الذكاء الاصطناعي',
  'status': 'الحالة',
  'error_code': 'سبب التعذر',
  'review': 'قرار المراجعة',
  'decision': 'القرار',
  'reason_code': 'سبب القرار',
  'details': 'التفاصيل',
  'reviewed_at': 'وقت المراجعة',
  'ticker': 'رمز السهم',
  'direction': 'الاتجاه المتوقع',
  'target_price': 'السعر المستهدف',
  'period_type': 'مدة التوقع',
  'deadline': 'الموعد المستهدف',
  'claims': 'نقاط التوقع',
  'specificity': 'وضوح التوقع',
  'frozen_at': 'وقت تثبيت التوقع',
  'source_session_date': 'جلسة البيانات',
  'target_session_date': 'الجلسة المستهدفة',
  'analyzed_count': 'الأسهم التي تم تحليلها',
  'eligible_count': 'الأسهم المؤهلة',
  'failed_count': 'الأسهم التي تعذر تحليلها',
  'average_top_score': 'متوسط تقييم الأفضل',
  'signals': 'توزيع القرارات',
  'disclaimer': 'تنبيه مهم',
  'price_at_analysis': 'السعر وقت التحليل',
  'score': 'الدرجة',
  'signal': 'الإشارة',
  'expected_direction': 'الاتجاه المتوقع',
  'confidence': 'الثقة',
  'qualified': 'اجتاز شروط التأهيل',
  'liquidity': 'السيولة',
  'average_turnover_egp_20d': 'متوسط قيمة التداول 20 يوم',
  'nonzero_volume_ratio_20d': 'استمرارية التداول 20 يوم',
  'market_data': 'بيانات السوق',
  'provider': 'مصدر البيانات',
  'data_as_of': 'البيانات حتى',
  'candle_count': 'عدد الشموع',
  'explanation': 'شرح النتيجة',
  'explanation_source': 'مصدر الشرح',
  'analysis': 'تفاصيل التحليل',
  'entry': 'سعر الدخول',
  'stop_loss': 'وقف الخسارة',
  'target_1': 'الهدف الأول',
  'target_2': 'الهدف الثاني',
};

String _labelFor(String key) {
  final translated = _labels[key];
  if (translated != null) {
    return translated;
  }
  final normalized = key.replaceAll('_', ' ').trim();
  if (normalized.isEmpty) {
    return 'تفصيل';
  }
  return normalized[0].toUpperCase() + normalized.substring(1);
}

String _formatValue(dynamic value) {
  if (value == null) {
    return 'لا يوجد';
  }
  if (value is bool) {
    return value ? 'نعم' : 'لا';
  }
  if (value is num) {
    return value.toString();
  }
  final text = value.toString().trim();
  if (text.isEmpty) {
    return 'لا يوجد';
  }
  return switch (text.toLowerCase()) {
    'published' => 'منشور',
    'pending_review' => 'قيد المراجعة',
    'awaiting_ai_retry' => 'بانتظار إعادة المراجعة',
    'complete' => 'مكتمل',
    'completed' => 'مكتمل',
    'failed' => 'تعذر مؤقتًا',
    'provider_unavailable' => 'خدمة الذكاء الاصطناعي غير متاحة مؤقتًا',
    'buy' => 'شراء مشروط',
    'watch' => 'مراقبة',
    'avoid' => 'تجنب',
    'up' => 'صعود',
    'down' => 'هبوط',
    'neutral' => 'محايد',
    'ai' => 'ذكاء اصطناعي',
    'deterministic' => 'المحركات الحسابية',
    _ => text,
  };
}

```

---

### File: `test\api_client_test.dart`

```dart
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';

class _MockTokenStore extends Mock implements TokenStore {}

class _CallbackAdapter implements HttpClientAdapter {
  _CallbackAdapter(this.callback);

  final Future<ResponseBody> Function(RequestOptions options) callback;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<dynamic>? cancelFuture,
  ) {
    return callback(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _jsonBody(Map<String, dynamic> payload, int statusCode) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: <String, List<String>>{
      Headers.contentTypeHeader: <String>[Headers.jsonContentType],
    },
  );
}

void main() {
  group('ApiClient', () {
    test(
      'shares one refresh request across concurrent 401 responses',
      () async {
        final tokenStore = _MockTokenStore();
        var accessToken = 'old-access';
        var refreshToken = 'refresh-one';
        when(tokenStore.readAccessToken).thenAnswer((_) async => accessToken);
        when(tokenStore.readRefreshToken).thenAnswer((_) async => refreshToken);
        when(
          () => tokenStore.save(
            accessToken: any(named: 'accessToken'),
            refreshToken: any(named: 'refreshToken'),
          ),
        ).thenAnswer((invocation) async {
          accessToken = invocation.namedArguments[#accessToken] as String;
          refreshToken = invocation.namedArguments[#refreshToken] as String;
        });

        var refreshCalls = 0;
        final refreshDio = Dio(
          BaseOptions(baseUrl: 'https://example.test/api/v1'),
        );
        refreshDio.httpClientAdapter = _CallbackAdapter((options) async {
          refreshCalls += 1;
          await Future<void>.delayed(const Duration(milliseconds: 25));
          return _jsonBody(<String, dynamic>{
            'access_token': 'new-access',
            'refresh_token': 'refresh-two',
          }, 200);
        });

        final mainDio = Dio(
          BaseOptions(baseUrl: 'https://example.test/api/v1'),
        );
        mainDio.httpClientAdapter = _CallbackAdapter((options) async {
          final authorization = options.headers['Authorization'];
          if (authorization == 'Bearer new-access') {
            return _jsonBody(<String, dynamic>{'ok': true}, 200);
          }
          return _jsonBody(<String, dynamic>{'detail': 'expired'}, 401);
        });

        final client = ApiClient(
          baseUrl: 'https://example.test',
          tokenStore: tokenStore,
          dio: mainDio,
          refreshDio: refreshDio,
        );

        final responses = await Future.wait([
          client.dio.get<Map<String, dynamic>>('/protected'),
          client.dio.get<Map<String, dynamic>>('/protected'),
        ]);

        expect(responses, hasLength(2));
        expect(
          responses.every((response) => response.data?['ok'] == true),
          isTrue,
        );
        expect(refreshCalls, 1);
        expect(accessToken, 'new-access');
        expect(refreshToken, 'refresh-two');
        verify(
          () => tokenStore.save(
            accessToken: 'new-access',
            refreshToken: 'refresh-two',
          ),
        ).called(1);
      },
    );

    test('anonymous request does not read or attach an access token', () async {
      final tokenStore = _MockTokenStore();
      final mainDio = Dio(BaseOptions(baseUrl: 'https://example.test/api/v1'));
      Object? authorization;
      mainDio.httpClientAdapter = _CallbackAdapter((options) async {
        authorization = options.headers['Authorization'];
        return _jsonBody(<String, dynamic>{'ok': true}, 200);
      });

      final client = ApiClient(
        baseUrl: 'https://example.test',
        tokenStore: tokenStore,
        dio: mainDio,
      );
      await client.dio.get<Map<String, dynamic>>(
        '/public',
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );

      expect(authorization, isNull);
      verifyNever(tokenStore.readAccessToken);
    });
  });
}

```

---

### File: `test\app_observability_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/observability/app_observability.dart';

void main() {
  test('trace sample rate is clamped safely', () {
    expect(AppObservability.parseSampleRate('0.25'), 0.25);
    expect(AppObservability.parseSampleRate('-1'), 0.0);
    expect(AppObservability.parseSampleRate('2'), 1.0);
    expect(AppObservability.parseSampleRate('invalid'), 0.0);
  });

  testWidgets('fallback error widget is Arabic and accessible', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AppObservability.buildErrorWidget(
          FlutterErrorDetails(exception: StateError('test')),
        ),
      ),
    );

    expect(find.textContaining('حدث خطأ غير متوقع'), findsOneWidget);
    final semanticsFinder = find.byWidgetPredicate(
      (widget) =>
          widget is Semantics &&
          widget.properties.liveRegion == true &&
          widget.properties.label?.contains('حدث خطأ غير متوقع') == true,
    );
    expect(semanticsFinder, findsOneWidget);
  });
}

```

---

### File: `test\community_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/community_models.dart';

Map<String, dynamic> _discussionJson({
  String status = 'published',
  String? rejectionCode,
}) {
  return <String, dynamic>{
    'id': 'discussion-1',
    'ticker': 'COMI',
    'title': 'توقع حركة سهم البنك التجاري الدولي',
    'content':
        'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
    'period_type': 'next_session',
    'status': status,
    'moderation_result': <String, dynamic>{'source': 'ai'},
    'frozen_prediction': <String, dynamic>{
      'direction': 'up',
      'target_price': 145.0,
    },
    'rejection_code': rejectionCode,
    'created_at': '2026-07-26T00:15:00+03:00',
    'reviewed_at': '2026-07-26T00:16:00+03:00',
    'published_at': status == 'published' ? '2026-07-26T00:16:00+03:00' : null,
    'author': <String, dynamic>{
      'user_id': 'user-1',
      'display_name': 'مستخدم تجريبي',
      'avatar_key': 'avatar_03',
    },
  };
}

void main() {
  test('parses community discussion pagination and labels', () {
    final page = CommunityDiscussionPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[_discussionJson()],
      'total': 21,
      'limit': 20,
      'offset': 0,
    });

    expect(page.total, 21);
    expect(page.hasMore, isTrue);
    expect(page.items.single.ticker, 'COMI');
    expect(page.items.single.periodLabel, 'الجلسة القادمة');
    expect(page.items.single.statusLabel, 'منشورة');
    expect(page.items.single.frozenPrediction['direction'], 'up');
  });

  test('rejected and hidden discussions are eligible for appeal', () {
    final rejected = CommunityDiscussion.fromJson(
      _discussionJson(status: 'rejected', rejectionCode: 'off_topic'),
    );
    final hidden = CommunityDiscussion.fromJson(
      _discussionJson(status: 'hidden'),
    );

    expect(rejected.canAppeal, isTrue);
    expect(rejected.statusLabel, 'مرفوضة');
    expect(hidden.canAppeal, isTrue);
    expect(hidden.statusLabel, 'مخفية');
  });

  test('parses discussion submission wallet state', () {
    final result = CommunityDiscussionSubmission.fromJson(<String, dynamic>{
      'discussion': _discussionJson(status: 'pending_review'),
      'held_points': 50,
      'held_coins': '0.50',
      'balance_points': 250,
      'balance_coins': '2.50',
      'idempotent': false,
    });

    expect(result.discussion.status, 'pending_review');
    expect(result.heldPoints, 50);
    expect(result.balanceCoins, '2.50');
    expect(result.idempotent, isFalse);
  });

  test('parses appeals and resolution metadata', () {
    final page = CommunityAppealPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'appeal-1',
          'discussion_id': 'discussion-1',
          'user_id': 'user-1',
          'source_status': 'rejected',
          'message':
              'أطلب مراجعة القرار لأن المناقشة مرتبطة مباشرة بحركة السهم.',
          'status': 'accepted',
          'created_at': '2026-07-26T00:20:00+03:00',
          'resolved_at': '2026-07-26T00:25:00+03:00',
          'resolution_reason_code': null,
          'resolution_details': <String, dynamic>{'republished': true},
        },
      ],
      'total': 1,
      'limit': 20,
      'offset': 0,
    });

    expect(page.items.single.statusLabel, 'مقبول');
    expect(page.items.single.resolutionDetails['republished'], isTrue);
  });
}

```

---

### File: `test\community_repository_test.dart`

```dart
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/api_exception.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';
import 'package:sahmi_kasban_mobile/features/community/community_repository.dart';

class _MockTokenStore extends Mock implements TokenStore {}

class _CallbackAdapter implements HttpClientAdapter {
  _CallbackAdapter(this.callback);

  final Future<ResponseBody> Function(RequestOptions options) callback;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<dynamic>? cancelFuture,
  ) {
    return callback(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _jsonBody(
  Object payload,
  int statusCode, {
  Map<String, List<String>> headers = const <String, List<String>>{},
}) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: <String, List<String>>{
      Headers.contentTypeHeader: <String>[Headers.jsonContentType],
      ...headers,
    },
  );
}

Map<String, dynamic> _discussionJson() {
  return <String, dynamic>{
    'id': 'discussion-1',
    'ticker': 'COMI',
    'title': 'توقع حركة سهم البنك التجاري الدولي',
    'content':
        'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
    'period_type': 'next_session',
    'status': 'published',
    'moderation_result': <String, dynamic>{},
    'frozen_prediction': <String, dynamic>{'direction': 'up'},
    'rejection_code': null,
    'created_at': '2026-07-26T00:15:00+03:00',
    'reviewed_at': '2026-07-26T00:16:00+03:00',
    'published_at': '2026-07-26T00:16:00+03:00',
    'author': <String, dynamic>{
      'user_id': 'user-1',
      'display_name': 'مستخدم تجريبي',
      'avatar_key': 'avatar_03',
    },
  };
}

CommunityRepository _repository(
  _MockTokenStore tokenStore,
  Future<ResponseBody> Function(RequestOptions options) callback,
) {
  when(tokenStore.readAccessToken).thenAnswer((_) async => 'access-token');
  final dio = Dio(BaseOptions(baseUrl: 'https://example.test/api/v1'));
  dio.httpClientAdapter = _CallbackAdapter(callback);
  return CommunityRepository(
    ApiClient(
      baseUrl: 'https://example.test',
      tokenStore: tokenStore,
      dio: dio,
    ),
  );
}

void main() {
  test('loads filtered community page with pagination', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(options.path, '/community/discussions');
      expect(options.queryParameters['ticker'], 'COMI');
      expect(options.queryParameters['limit'], 10);
      expect(options.queryParameters['offset'], 20);
      return _jsonBody(<String, dynamic>{
        'items': <Map<String, dynamic>>[_discussionJson()],
        'total': 21,
        'limit': 10,
        'offset': 20,
      }, 200);
    });

    final page = await repository.listDiscussions(
      ticker: 'comi',
      limit: 10,
      offset: 20,
    );

    expect(page.items.single.ticker, 'COMI');
    expect(page.total, 21);
    expect(page.hasMore, isFalse);
  });

  test('maps 429 response and Retry-After header', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      return _jsonBody(
        <String, dynamic>{'detail': 'Submission rate limit exceeded'},
        429,
        headers: <String, List<String>>{
          'retry-after': <String>['45'],
        },
      );
    });

    try {
      await repository.submitDiscussion(
        submissionKey: 'submission-key-123',
        ticker: 'COMI',
        title: 'توقع حركة سهم البنك التجاري الدولي',
        content:
            'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
        periodType: 'next_session',
      );
      fail('Expected an ApiException.');
    } on ApiException catch (error) {
      expect(error.statusCode, 429);
      expect(error.retryAfterSeconds, 45);
      expect(error.message, 'Submission rate limit exceeded');
    }
  });

  test('extracts FastAPI validation messages from 422 response', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      return _jsonBody(<String, dynamic>{
        'detail': <Map<String, dynamic>>[
          <String, dynamic>{'msg': 'String should have at least 20 characters'},
        ],
      }, 422);
    });

    try {
      await repository.submitAppeal(
        discussionId: 'discussion-1',
        message: 'قصير',
      );
      fail('Expected an ApiException.');
    } on ApiException catch (error) {
      expect(error.statusCode, 422);
      expect(error.message, 'String should have at least 20 characters');
    }
  });
}

```

---

### File: `test\community_widgets_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/community_create_screen.dart';
import 'package:sahmi_kasban_mobile/features/community/community_feed_tab.dart';
import 'package:sahmi_kasban_mobile/features/community/community_models.dart';

CommunityDiscussion _discussion() {
  return CommunityDiscussion.fromJson(<String, dynamic>{
    'id': 'discussion-1',
    'ticker': 'COMI',
    'title': 'توقع حركة سهم البنك التجاري الدولي',
    'content':
        'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
    'period_type': 'next_session',
    'status': 'published',
    'moderation_result': <String, dynamic>{},
    'frozen_prediction': <String, dynamic>{'direction': 'up'},
    'rejection_code': null,
    'created_at': '2026-07-26T00:15:00+03:00',
    'reviewed_at': '2026-07-26T00:16:00+03:00',
    'published_at': '2026-07-26T00:16:00+03:00',
    'author': <String, dynamic>{
      'user_id': 'user-1',
      'display_name': 'مستخدم تجريبي',
      'avatar_key': 'avatar_03',
    },
  });
}

void main() {
  testWidgets('community discussion card renders Arabic summary and ticker', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CommunityDiscussionCard(
            discussion: _discussion(),
            showStatus: true,
          ),
        ),
      ),
    );

    expect(find.text('مستخدم تجريبي'), findsOneWidget);
    expect(find.text('COMI'), findsOneWidget);
    expect(find.text('الجلسة القادمة'), findsOneWidget);
    expect(find.text('منشورة'), findsOneWidget);
  });

  testWidgets('discussion creation screen explains wallet hold', (
    tester,
  ) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: CommunityCreateScreen())),
    );

    expect(find.text('إنشاء مناقشة'), findsOneWidget);
    expect(find.textContaining('حجز 0.5 عملة مؤقتًا'), findsOneWidget);
    expect(find.text('اختر السهم'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -700));
    await tester.pumpAndSettle();

    expect(find.text('إرسال للمراجعة'), findsOneWidget);
  });
}

```

---

### File: `test\domain_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';

void main() {
  group('TokenPair', () {
    test('parses the backend token response', () {
      final tokens = TokenPair.fromJson(<String, dynamic>{
        'access_token': 'access',
        'refresh_token': 'refresh',
        'expires_in': 900,
      });

      expect(tokens.accessToken, 'access');
      expect(tokens.refreshToken, 'refresh');
      expect(tokens.expiresIn, 900);
    });
  });

  group('MarketReportPreview', () {
    test('parses dates, cost, and market summary', () {
      final preview = MarketReportPreview.fromJson(<String, dynamic>{
        'report_id': '76bf2df9-aadb-45fb-b1fb-22e97fb2c9e8',
        'source_session_date': '2026-07-23',
        'target_session_date': '2026-07-26',
        'generated_at': '2026-07-23T17:05:00+03:00',
        'status': 'complete',
        'item_count': 10,
        'unlocked': false,
        'unlock_cost_points': 100,
        'unlock_cost_coins': '1.00',
        'market_summary': <String, dynamic>{'eligible_count': 26},
      });

      expect(preview.itemCount, 10);
      expect(preview.unlockCostPoints, 100);
      expect(preview.targetSessionDate.day, 26);
      expect(preview.marketSummary['eligible_count'], 26);
    });
  });

  test('RegistrationResult keeps the free weekly grant default', () {
    final result = RegistrationResult.fromJson(<String, dynamic>{
      'user_id': '02140ff6-c9a2-45ef-892f-bd8b5713dd9d',
      'email': 'user@example.com',
      'requires_email_verification': true,
    });

    expect(result.requiresEmailVerification, isTrue);
    expect(result.weeklyPointsGranted, 300);
  });
}

```

---

### File: `test\historical_replay_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/admin/historical_replay_models.dart';

void main() {
  test('parses account replay progress and download availability', () {
    final job = HistoricalReplayJob.fromJson(<String, dynamic>{
      'id': 'job-1',
      'engine_version': 'core-v2',
      'status': 'partial',
      'start_date': '2026-06-01',
      'end_date': '2026-06-30',
      'horizon_sessions': 5,
      'parallelism': 5,
      'total_tickers': 155,
      'processed_tickers': 155,
      'successful_tickers': 150,
      'failed_tickers': 5,
      'total_rows': 3200,
      'evaluated_rows': 2900,
      'pending_rows': 300,
      'progress_pct': 100,
      'download_ready': true,
      'created_at': '2026-07-29T18:00:00Z',
      'completed_at': '2026-07-29T19:00:00Z',
      'tickers': <Map<String, dynamic>>[
        <String, dynamic>{
          'ticker': 'COMI',
          'status': 'complete',
          'provider': 'tradingview',
          'rows_written': 22,
          'evaluated_rows': 20,
          'pending_rows': 2,
          'failed_rows': 0,
        },
      ],
    });

    expect(job.parallelism, 5);
    expect(job.downloadReady, isTrue);
    expect(job.progressPct, 100);
    expect(job.tickers.single.ticker, 'COMI');
    expect(job.tickers.single.pendingRows, 2);
  });
}

```

---

### File: `test\labs_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/labs/labs_models.dart';

void main() {
  group('LabsBacktestResult', () {
    test('parses a full response payload', () {
      final result = LabsBacktestResult.fromJson({
        'params': {
          'start_date': '2026-07-07',
          'end_date': '2026-07-28',
          'rank': 3,
          'exit_mode': 'target_2',
          'track_interval_minutes': 10,
          'source_interval': '5m',
        },
        'summary': {
          'reports_scanned': 3,
          'trades': 3,
          'hits': 2,
          'misses': 1,
          'skipped': 1,
          'hit_rate_pct': 66.67,
          'avg_return_pct': 1.9,
          'median_return_pct': 2.1,
          'avg_hit_return_pct': 5.4,
          'avg_miss_return_pct': -3.6,
          'median_minutes_to_hit': 35.0,
          'best_return_pct': 7.1,
          'worst_return_pct': -3.6,
          'cumulative_return_pct': 5.7,
        },
        'sessions': [
          {
            'target_session_date': '2026-07-28',
            'report_id': 'r-1',
            'rank': 3,
            'ticker': 'HRHO',
            'score': 81.5,
            'price_at_analysis': 12.4,
            'targets': [13.0, 14.2],
            'stop_loss': 11.8,
            'session_open': 12.5,
            'exit_price': 14.2,
            'exit_reason': 'target',
            'hit': true,
            'minutes_to_exit': 40,
            'return_pct': 13.6,
            'tracked': [
              {'time': '10:05', 'price': 12.6, 'high': 12.7, 'low': 12.5},
              {'time': '10:15', 'price': 13.2, 'high': 14.2, 'low': 13.0},
            ],
          },
          {
            'target_session_date': '2026-07-27',
            'report_id': 'r-1',
            'rank': 3,
            'ticker': 'HRHO',
            'score': 81.5,
            'price_at_analysis': null,
            'targets': <Object>[],
            'stop_loss': null,
            'session_open': null,
            'exit_price': null,
            'exit_reason': 'skipped',
            'hit': false,
            'minutes_to_exit': null,
            'return_pct': null,
            'tracked': <Object>[],
          },
        ],
        'meta': {'requested_by': 'user-1'},
      });

      expect(result.params.rank, 3);
      expect(result.params.exitMode, 'target_2');
      expect(result.params.trackIntervalMinutes, 10);
      expect(result.summary.hits, 2);
      expect(result.summary.hitRatePct, closeTo(66.67, 0.001));
      expect(result.summary.medianMinutesToHit, 35.0);
      expect(result.sessions, hasLength(2));

      final trade = result.sessions.first;
      expect(trade.ticker, 'HRHO');
      expect(trade.hit, isTrue);
      expect(trade.exitReason, 'target');
      expect(trade.minutesToExit, 40);
      expect(trade.returnPct, closeTo(13.6, 0.001));
      expect(trade.tracked, hasLength(2));
      expect(trade.tracked.first.time, '10:05');
      expect(trade.targets, [13.0, 14.2]);

      final skipped = result.sessions[1];
      expect(skipped.hit, isFalse);
      expect(skipped.exitReason, 'skipped');
      expect(skipped.returnPct, isNull);
      expect(skipped.tracked, isEmpty);
    });

    test('handles missing optional fields gracefully', () {
      final result = LabsBacktestResult.fromJson({
        'params': {
          'start_date': '2026-07-07',
          'end_date': '2026-07-28',
          'rank': null,
          'exit_mode': 'highest',
        },
        'summary': {'trades': 0},
        'sessions': null,
        'meta': <Object>{},
      });

      expect(result.params.rank, isNull);
      expect(result.params.exitMode, 'highest');
      expect(result.summary.trades, 0);
      expect(result.summary.hitRatePct, 0);
      expect(result.sessions, isEmpty);
    });
  });

  group('LabsBacktestQuery', () {
    test('value equality drives provider identity', () {
      final a = LabsBacktestQuery(
        startDate: DateTime(2026, 7, 7),
        endDate: DateTime(2026, 7, 28),
        rank: 1,
        exitMode: 'target_2',
      );
      final b = LabsBacktestQuery(
        startDate: DateTime(2026, 7, 7),
        endDate: DateTime(2026, 7, 28),
        rank: 1,
        exitMode: 'target_2',
      );
      final c = LabsBacktestQuery(
        startDate: DateTime(2026, 7, 7),
        endDate: DateTime(2026, 7, 28),
        rank: 2,
        exitMode: 'target_2',
      );

      expect(a, b);
      expect(a.hashCode, b.hashCode);
      expect(a == c, isFalse);
    });
  });

  group('LabsBacktestJob', () {
    test('parses a queued job without a result', () {
      final job = LabsBacktestJob.fromJson({
        'id': 'job-1',
        'status': 'queued',
        'start_date': '2026-07-07',
        'end_date': '2026-07-28',
        'rank': null,
        'exit_mode': 'target_2',
        'created_at': '2026-08-01T10:00:00Z',
      });

      expect(job.id, 'job-1');
      expect(job.status, 'queued');
      expect(job.isActive, isTrue);
      expect(job.summary, isNull);
      expect(job.sessions, isEmpty);
      expect(job.errorMessage, isNull);
    });

    test('parses a completed job with summary and sessions', () {
      final job = LabsBacktestJob.fromJson({
        'id': 'job-2',
        'status': 'complete',
        'start_date': '2026-07-07',
        'end_date': '2026-07-28',
        'rank': 2,
        'exit_mode': 'highest',
        'params': {
          'start_date': '2026-07-07',
          'end_date': '2026-07-28',
          'rank': 2,
          'exit_mode': 'highest',
          'track_interval_minutes': 10,
          'source_interval': '5m',
        },
        'summary': {
          'reports_scanned': 1,
          'trades': 1,
          'hits': 1,
          'misses': 0,
          'skipped': 0,
          'hit_rate_pct': 100.0,
        },
        'sessions': [
          {
            'target_session_date': '2026-07-28',
            'report_id': 'r-1',
            'rank': 2,
            'ticker': 'COMI',
            'score': 80.0,
            'price_at_analysis': 12.4,
            'targets': [13.0],
            'stop_loss': 11.8,
            'session_open': 12.5,
            'exit_price': 13.0,
            'exit_reason': 'target',
            'hit': true,
            'minutes_to_exit': 40,
            'return_pct': 4.0,
            'tracked': <Object>[],
          },
        ],
        'error_message': null,
        'started_at': '2026-08-01T10:00:00Z',
        'completed_at': '2026-08-01T10:02:00Z',
        'created_at': '2026-08-01T10:00:00Z',
      });

      expect(job.status, 'complete');
      expect(job.isActive, isFalse);
      expect(job.params?.exitMode, 'highest');
      expect(job.summary?.trades, 1);
      expect(job.summary?.hitRatePct, closeTo(100.0, 0.001));
      expect(job.sessions, hasLength(1));
      expect(job.sessions.first.ticker, 'COMI');
      expect(job.sessions.first.hit, isTrue);
      expect(job.completedAt, isNotNull);
    });

    test('parses a failed job with an error message', () {
      final job = LabsBacktestJob.fromJson({
        'id': 'job-3',
        'status': 'failed',
        'start_date': '2026-07-07',
        'end_date': '2026-07-28',
        'rank': null,
        'exit_mode': 'target_2',
        'error_message': 'نطاق أكبر من المسموح',
        'created_at': '2026-08-01T10:00:00Z',
      });

      expect(job.status, 'failed');
      expect(job.isActive, isFalse);
      expect(job.errorMessage, 'نطاق أكبر من المسموح');
    });
  });
}

```

---

### File: `test\market_report_screen_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/data/backend_repository.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';
import 'package:sahmi_kasban_mobile/features/reports/market_report_screen.dart';

class _MockBackendRepository extends Mock implements BackendRepository {}

void main() {
  testWidgets('Top 10 report renders Arabic cards without intl locale setup', (
    tester,
  ) async {
    final repository = _MockBackendRepository();
    final report = MarketReport(
      reportId: 'report-1',
      sourceSessionDate: DateTime.utc(2026, 7, 28),
      targetSessionDate: DateTime.utc(2026, 7, 29),
      generatedAt: DateTime.utc(2026, 7, 28, 17),
      marketSummary: const <String, dynamic>{
        'title': 'الأسهم الأعلى تقييمًا للجلسة القادمة',
        'analyzed_count': 180,
        'eligible_count': 24,
        'failed_count': 2,
        'average_top_score': 81.5,
        'signals': <String, dynamic>{'BUY': 7, 'WATCH': 3},
        'disclaimer': 'تحليل آلي وليس توصية استثمارية.',
      },
      items: <MarketReportItem>[
        MarketReportItem(
          ticker: 'COMI',
          rank: 1,
          score: 88.4,
          payload: const <String, dynamic>{
            'decision': 'فرصة قوية',
            'confidence': 91.2,
            'price_at_analysis': 82.5,
            'explanation': 'الاتجاه والسيولة يدعمان المراقبة الإيجابية.',
            'analysis': <String, dynamic>{
              'trade_plan': <String, dynamic>{
                'entry': 82.5,
                'stop_loss': 79.0,
                'target_1': 89.5,
                'target_2': 94.0,
                'reward_risk_1': 2.0,
              },
              'engines': <String, dynamic>{
                'technical': <String, dynamic>{
                  'details': <String, dynamic>{
                    'trend': 'uptrend',
                    'rsi': 61.0,
                    'volume_ratio': 1.4,
                  },
                  'reasons': <String>['Price above SMA20'],
                },
                'risk': <String, dynamic>{
                  'details': <String, dynamic>{'risk_level': 'low'},
                  'reasons': <String>[],
                },
              },
            },
          },
        ),
      ],
      extendedItems: <MarketReportItem>[],
    );
    when(
      () => repository.getMarketReport('report-1'),
    ).thenAnswer((_) async => report);

    await tester.pumpWidget(
      ProviderScope(
        overrides: <Override>[
          backendRepositoryProvider.overrideWithValue(repository),
        ],
        child: const MaterialApp(
          home: MarketReportScreen(reportId: 'report-1'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('الأربعاء 29 يوليو 2026'), findsOneWidget);
    expect(find.text('ملخص السوق'), findsOneWidget);
    expect(find.text('COMI'), findsOneWidget);
    expect(find.text('خطة التداول'), findsOneWidget);
    expect(find.textContaining('السعر أعلى من متوسط 20 جلسة'), findsOneWidget);
    expect(find.textContaining('{'), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Grade tabs render extended stocks beyond top 10', (
    tester,
  ) async {
    final repository = _MockBackendRepository();
    final report = MarketReport(
      reportId: 'report-2',
      sourceSessionDate: DateTime.utc(2026, 7, 28),
      targetSessionDate: DateTime.utc(2026, 7, 29),
      generatedAt: DateTime.utc(2026, 7, 28, 17),
      marketSummary: const <String, dynamic>{'eligible_count': 3},
      items: <MarketReportItem>[
        MarketReportItem(
          ticker: 'COMI',
          rank: 1,
          score: 88.4,
          payload: const <String, dynamic>{
            'decision': 'فرصة قوية',
            'signal': 'BUY',
            'opportunity_tier': 'conditional_buy',
            'elite_profile': 'none',
          },
        ),
      ],
      extendedItems: <MarketReportItem>[
        MarketReportItem(
          ticker: 'EXT1',
          rank: 11,
          score: 74.5,
          payload: const <String, dynamic>{
            'decision': 'شراء مشروط',
            'signal': 'BUY',
            'opportunity_tier': 'conditional_buy',
            'elite_profile': 'none',
            'price_at_analysis': 22.5,
            'trade_plan': <String, dynamic>{
              'entry': 22.5,
              'stop_loss': 21.0,
              'target_1': 24.5,
              'target_2': 26.0,
              'reward_risk_1': 1.8,
            },
            'explanation': 'فرصة قوية بشروط المخاطر.',
          },
        ),
      ],
    );
    when(
      () => repository.getMarketReport('report-2'),
    ).thenAnswer((_) async => report);

    await tester.pumpWidget(
      ProviderScope(
        overrides: <Override>[
          backendRepositoryProvider.overrideWithValue(repository),
        ],
        child: const MaterialApp(
          home: MarketReportScreen(reportId: 'report-2'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('شراء مشروط (2)'), findsOneWidget);
    expect(find.text('EXT1'), findsNothing);

    await tester.tap(find.text('شراء مشروط (2)'));
    await tester.pumpAndSettle();

    expect(find.text('EXT1'), findsOneWidget);
    expect(find.text('الهدف الأول'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

```

---

### File: `test\monetization_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/monetization/monetization_models.dart';

void main() {
  test('catalog exposes only server-defined store product IDs', () {
    final catalog = MonetizationCatalog.fromJson(<String, dynamic>{
      'plans': <Map<String, dynamic>>[
        <String, dynamic>{
          'code': 'free',
          'display_name_ar': 'المجانية',
          'weekly_points': 300,
          'weekly_coins': '3.00',
          'ads_enabled': true,
          'product_id': null,
          'history_limit': 20,
          'report_history_days': 1,
          'badge_code': null,
        },
        <String, dynamic>{
          'code': 'basic',
          'display_name_ar': 'الأساسية',
          'weekly_points': 1000,
          'weekly_coins': '10.00',
          'ads_enabled': false,
          'product_id': 'sahmi_basic_monthly',
          'history_limit': 100,
          'report_history_days': 30,
          'badge_code': 'basic',
        },
      ],
      'coin_packs': <Map<String, dynamic>>[
        <String, dynamic>{
          'product_id': 'sahmi_coins_5',
          'display_name_ar': '5 عملات',
          'points': 500,
          'coins': '5.00',
        },
      ],
      'ad_reward_points': 75,
      'ad_reward_coins': '0.75',
      'ad_reward_daily_limit': 4,
      'ad_reward_cooldown_seconds': 900,
    });

    expect(catalog.storeProductIds, <String>{
      'sahmi_basic_monthly',
      'sahmi_coins_5',
    });
    expect(catalog.isCoinPack('sahmi_coins_5'), isTrue);
    expect(catalog.isCoinPack('sahmi_basic_monthly'), isFalse);
    expect(catalog.adRewardPoints, 75);
  });

  test('rewarded session distinguishes development SSV simulation', () {
    final session = RewardedAdSessionModel.fromJson(<String, dynamic>{
      'session_id': '4f6c5633-e3af-4f30-a8dd-a0e6fb38ecb4',
      'ad_unit_id': 'ca-app-pub-test/rewarded',
      'custom_data': 'server-issued-random-value',
      'expires_at': '2026-07-25T19:00:00Z',
      'test_mode': true,
    });

    expect(session.testMode, isTrue);
    expect(session.customData, 'server-issued-random-value');
    expect(session.expiresAt.isUtc, isTrue);
  });

  test('purchase verification result keeps server entitlement decision', () {
    final result = PurchaseVerificationResultModel.fromJson(<String, dynamic>{
      'purchase_id': '28f87fb5-081b-4a13-8f30-c24bdbd73752',
      'product_id': 'sahmi_coins_5',
      'product_type': 'coins',
      'purchase_state': 'purchased',
      'acknowledgement_state': 'acknowledged',
      'entitlement_granted': true,
      'idempotent': false,
      'plan_code': 'free',
      'balance_points': 800,
      'balance_coins': '8.00',
      'subscription_expires_at': null,
    });

    expect(result.entitlementGranted, isTrue);
    expect(result.idempotent, isFalse);
    expect(result.balancePoints, 800);
  });
}

```

---

### File: `test\monetization_plan_features_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/monetization/monetization_models.dart';

void main() {
  test('MonetizationPlan parses comparison limits and feature list', () {
    final plan = MonetizationPlan.fromJson(<String, dynamic>{
      'code': 'advanced',
      'display_name_ar': 'المتقدمة',
      'weekly_points': 6000,
      'weekly_coins': '60.00',
      'ads_enabled': false,
      'product_id': 'sahmi_advanced_monthly',
      'history_limit': 1000,
      'report_history_days': 365,
      'features': <String>[
        '60 عملة أسبوعيًا',
        'مقارنة حتى 3 أسهم 12 مرة شهريًا',
      ],
      'comparison_monthly_allowance': 12,
      'max_comparison_stocks': 3,
      'priority_level': 2,
      'badge_code': 'advanced',
    });

    expect(plan.features, hasLength(2));
    expect(plan.comparisonMonthlyAllowance, 12);
    expect(plan.maxComparisonStocks, 3);
    expect(plan.priorityLevel, 2);
  });
}

```

---

### File: `test\performance_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/performance/performance_models.dart';

void main() {
  test('parses transparent performance summary with negative results', () {
    final summary = PerformanceSummary.fromJson(<String, dynamic>{
      'window_sessions': 7,
      'sessions_found': 3,
      'complete_sessions': 2,
      'total_items': 30,
      'evaluated_items': 27,
      'pending_items': 2,
      'failed_items': 1,
      'data_completeness_pct': 90.0,
      'positive_count': 12,
      'negative_count': 14,
      'flat_count': 1,
      'average_return_bp': -25,
      'median_return_bp': -10,
      'positive_rate_pct': 44.44,
      'direction_accuracy_pct': 48.15,
      'target_one_hit_rate_pct': 20.0,
      'target_two_hit_rate_pct': 5.0,
      'stop_loss_hit_rate_pct': 30.0,
      'best_outcome': <String, dynamic>{
        'report_id': 'r1',
        'target_session_date': '2026-07-20',
        'ticker': 'COMI',
        'rank': 1,
        'return_bp': 450,
      },
      'worst_outcome': <String, dynamic>{
        'report_id': 'r2',
        'target_session_date': '2026-07-21',
        'ticker': 'SWDY',
        'rank': 4,
        'return_bp': -700,
      },
      'ranks': <Map<String, dynamic>>[
        <String, dynamic>{
          'rank': 1,
          'evaluated_items': 3,
          'average_return_bp': 100,
          'median_return_bp': 80,
          'positive_rate_pct': 66.67,
          'direction_accuracy_pct': 66.67,
          'target_one_hit_rate_pct': 33.33,
          'stop_loss_hit_rate_pct': 0.0,
        },
      ],
      'sessions': <Map<String, dynamic>>[],
      'benchmark': <String, dynamic>{'status': 'not_available'},
      'negative_results_retained': true,
    });

    expect(summary.negativeCount, 14);
    expect(summary.averageReturnBp, -25);
    expect(summary.worstOutcome?.returnBp, -700);
    expect(summary.dataCompletenessPct, 90);
    expect(summary.negativeResultsRetained, isTrue);
  });

  test('parses pending outcome and audited revision', () {
    final detail = PerformanceReportDetail.fromJson(<String, dynamic>{
      'report_id': 'r1',
      'target_session_date': '2026-07-20',
      'generated_at': '2026-07-19T15:00:00Z',
      'evaluation_status': 'partial',
      'session': <String, dynamic>{
        'report_id': 'r1',
        'target_session_date': '2026-07-20',
        'evaluation_status': 'partial',
        'total_items': 2,
        'evaluated_items': 1,
        'pending_items': 1,
        'failed_items': 0,
        'data_completeness_pct': 50.0,
        'average_return_bp': -200,
        'positive_count': 0,
        'negative_count': 1,
        'direction_accuracy_pct': 0.0,
        'target_one_hit_rate_pct': 0.0,
        'stop_loss_hit_rate_pct': 0.0,
      },
      'outcomes': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'o1',
          'ticker': 'COMI',
          'rank': 1,
          'status': 'pending_data',
          'expected_direction': 'up',
          'price_at_analysis': 100.0,
          'session_open': null,
          'session_high': null,
          'session_low': null,
          'session_close': null,
          'return_bp': null,
          'max_upside_bp': null,
          'max_drawdown_bp': null,
          'direction_correct': null,
          'target_one': 105.0,
          'target_two': 110.0,
          'stop_loss': 95.0,
          'target_one_hit': null,
          'target_two_hit': null,
          'stop_loss_hit': null,
          'provider': null,
          'data_as_of': null,
          'evaluated_at': null,
          'evaluator_version': 'report-performance-v1',
          'evidence': <String, dynamic>{
            'reason': 'target_session_candle_missing',
          },
          'correction_count': 1,
        },
      ],
      'revisions': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'rev1',
          'revision_number': 1,
          'reason': 'Official correction',
          'before_payload': <String, dynamic>{'status': 'pending_data'},
          'after_payload': <String, dynamic>{'status': 'complete'},
          'created_at': '2026-07-21T15:10:00Z',
        },
      ],
      'negative_results_retained': true,
    });

    expect(detail.outcomes.single.isComplete, isFalse);
    expect(
      detail.outcomes.single.evidence['reason'],
      'target_session_candle_missing',
    );
    expect(detail.revisions.single.revisionNumber, 1);
  });
}

```

---

### File: `test\performance_presentation_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/performance/performance_widgets.dart';

void main() {
  test(
    'performance date formatting never crashes without locale bootstrap',
    () {
      final value = formatPerformanceDate(
        DateTime(2026, 7, 29, 13, 45),
        includeTime: true,
      );

      expect(value, isNotEmpty);
      expect(value, contains('2026'));
    },
  );

  test('performance progress is clamped to the indicator range', () {
    expect(performanceProgress(-5), 0);
    expect(performanceProgress(50), 0.5);
    expect(performanceProgress(125), 1);
  });

  test('performance statuses are presented in Arabic', () {
    expect(performanceStatusLabel('complete'), 'مكتمل');
    expect(performanceStatusLabel('pending_data'), 'بانتظار البيانات');
    expect(performanceStatusLabel('not_started'), 'لم يبدأ التقييم');
  });
}

```

---

### File: `test\phase4_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';

void main() {
  test('parses paginated wallet history', () {
    final page = WalletHistoryPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'transaction_id': 'txn-1',
          'entry_type': 'debit',
          'amount_points': -50,
          'amount_coins': '-0.50',
          'status': 'confirmed',
          'reference_type': 'stock_analysis',
          'reference_id': 'analysis-1',
          'details': <String, dynamic>{'ticker': 'COMI'},
          'created_at': '2026-07-25T17:00:00Z',
          'confirmed_at': '2026-07-25T17:00:01Z',
        },
      ],
      'total': 21,
      'limit': 20,
      'offset': 0,
    });

    expect(page.total, 21);
    expect(page.items.single.amountPoints, -50);
    expect(page.items.single.details['ticker'], 'COMI');
  });

  test('parses paid analysis result and cached billing state', () {
    final result = StockAnalysisResult.fromJson(<String, dynamic>{
      'analysis_id': 'analysis-1',
      'ticker': 'COMI',
      'cached': true,
      'market_snapshot_cached': true,
      'charged_points': 0,
      'charged_coins': '0.00',
      'balance_points': 250,
      'balance_coins': '2.50',
      'data_as_of': '2026-07-25T14:00:00Z',
      'payload': <String, dynamic>{'decision': 'WATCH'},
    });

    expect(result.cached, isTrue);
    expect(result.chargedPoints, 0);
    expect(result.payload['decision'], 'WATCH');
  });

  test('parses unlocked Top 10 report and ranked items', () {
    final report = MarketReport.fromJson(<String, dynamic>{
      'report_id': 'report-1',
      'source_session_date': '2026-07-24',
      'target_session_date': '2026-07-26',
      'generated_at': '2026-07-24T17:00:00+03:00',
      'market_summary': <String, dynamic>{'eligible_count': 34},
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'ticker': 'COMI',
          'rank': 1,
          'score': 87.35,
          'payload': <String, dynamic>{'reason': 'momentum'},
        },
      ],
    });

    expect(report.items.single.rank, 1);
    expect(report.items.single.score, closeTo(87.35, 0.001));
    expect(report.marketSummary['eligible_count'], 34);
  });

  test('avatar options use generated WebP assets', () {
    final option = AvatarOption.fromJson(<String, dynamic>{
      'key': 'avatar_12',
      'asset_path': 'assets/avatars/avatar_12.webp',
    });

    expect(option.key, 'avatar_12');
    expect(option.assetPath, endsWith('.webp'));
  });
}

```

---

### File: `test\phase8_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/admin/admin_models.dart';
import 'package:sahmi_kasban_mobile/features/notifications/notification_models.dart';

void main() {
  test('parses admin overview metrics', () {
    final overview = AdminOverview.fromJson(<String, dynamic>{
      'users_total': 10,
      'users_active': 8,
      'users_suspended': 2,
      'discussions_pending': 3,
      'discussions_published': 7,
      'discussions_hidden': 1,
      'open_reports': 2,
      'open_appeals': 1,
      'verified_predictions': 4,
      'wallet_points_total': 1200,
      'notifications_today': 5,
    });
    expect(overview.usersTotal, 10);
    expect(overview.openReports, 2);
  });

  test('renders administrator audit codes as Arabic text', () {
    final item = AdminAuditItem.fromJson(<String, dynamic>{
      'action': 'admin_wallet_credit',
      'reason_code': 'admin_credit',
      'details': <String, dynamic>{
        'amount_coins': 5,
        'balance_before_points': 100,
        'balance_after_points': 600,
        'request_id': 'hidden-request-id',
      },
      'created_at': '2026-07-29T17:00:00Z',
    });

    expect(item.action, 'إضافة عملات لمستخدم');
    expect(item.reasonCode, 'إضافة رصيد بواسطة الإدارة');
    expect(item.details.toString(), contains('العملات المضافة: 5'));
    expect(item.details.toString(), contains('الرصيد قبل العملية: 100'));
    expect(item.details.toString(), isNot(contains('request_id')));
    expect(item.details.toString(), isNot(contains('{')));
  });

  test('parses notification unread state', () {
    final page = NotificationPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'n1',
          'title': 'تنبيه',
          'body': 'تم نشر التقرير.',
          'category': 'report',
          'data': <String, dynamic>{},
          'read_at': null,
          'sent_at': '2026-07-26T12:00:00Z',
        },
      ],
      'total': 1,
      'unread_count': 1,
      'limit': 20,
      'offset': 0,
    });
    expect(page.items.single.isUnread, isTrue);
    expect(page.unreadCount, 1);
  });
}

```

---

### File: `test\prediction_models_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_models.dart';

Map<String, dynamic> _verificationJson() {
  return <String, dynamic>{
    'id': 'verification-1',
    'discussion_id': 'discussion-1',
    'score_bp': 8750,
    'score_percent': 87.5,
    'strength': 'very_strong',
    'reward_points': 200,
    'reward_coins': '2.00',
    'evidence': <String, dynamic>{
      'explanation': <String, dynamic>{
        'source': 'ai',
        'reason': 'تحقق الاتجاه والهدف خلال الفترة المحددة.',
      },
    },
    'verified_at': '2026-07-27T17:05:00+03:00',
  };
}

void main() {
  test('parses verified prediction status and Arabic labels', () {
    final status = PredictionVerificationStatus.fromJson(<String, dynamic>{
      'discussion_id': 'discussion-1',
      'state': 'verified',
      'eligible_at': '2026-07-27T17:00:00+03:00',
      'verification': _verificationJson(),
    });

    expect(status.isVerified, isTrue);
    expect(status.verification?.strengthLabel, 'قوية جدًا');
    expect(status.verification?.rewardCoins, '2.00');
    expect(
      status.verification?.explanation,
      'تحقق الاتجاه والهدف خلال الفترة المحددة.',
    );
  });

  test('parses waiting and eligible verification states', () {
    final waiting = PredictionVerificationStatus.fromJson(<String, dynamic>{
      'discussion_id': 'discussion-2',
      'state': 'waiting',
      'eligible_at': '2026-07-30T17:00:00+03:00',
      'verification': null,
    });
    final eligible = PredictionVerificationStatus.fromJson(<String, dynamic>{
      'discussion_id': 'discussion-3',
      'state': 'eligible',
      'eligible_at': '2026-07-26T17:00:00+03:00',
      'verification': null,
    });

    expect(waiting.isWaiting, isTrue);
    expect(waiting.eligibleAt, isNotNull);
    expect(eligible.isEligible, isTrue);
  });

  test('parses verification submission wallet result', () {
    final submission =
        PredictionVerificationSubmission.fromJson(<String, dynamic>{
          'verification': _verificationJson(),
          'balance_points': 500,
          'balance_coins': '5.00',
          'idempotent': false,
        });

    expect(submission.verification.scorePercent, 87.5);
    expect(submission.balancePoints, 500);
    expect(submission.idempotent, isFalse);
  });

  test('parses personal prediction statistics', () {
    final stats = PredictionStats.fromJson(<String, dynamic>{
      'verified_predictions': 8,
      'accepted_predictions': 6,
      'accuracy_percent': 75.0,
      'average_score_percent': 68.25,
      'total_reward_points': 650,
      'total_reward_coins': '6.50',
    });

    expect(stats.verifiedPredictions, 8);
    expect(stats.accuracyPercent, 75.0);
    expect(stats.totalRewardCoins, '6.50');
  });
}

```

---

### File: `test\prediction_repository_test.dart`

```dart
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/api_exception.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_repository.dart';

class _MockTokenStore extends Mock implements TokenStore {}

class _CallbackAdapter implements HttpClientAdapter {
  _CallbackAdapter(this.callback);

  final Future<ResponseBody> Function(RequestOptions options) callback;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<dynamic>? cancelFuture,
  ) {
    return callback(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _jsonBody(Object payload, int statusCode) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: <String, List<String>>{
      Headers.contentTypeHeader: <String>[Headers.jsonContentType],
    },
  );
}

Map<String, dynamic> _verificationJson() {
  return <String, dynamic>{
    'id': 'verification-1',
    'discussion_id': 'discussion-1',
    'score_bp': 9000,
    'score_percent': 90.0,
    'strength': 'very_strong',
    'reward_points': 200,
    'reward_coins': '2.00',
    'evidence': <String, dynamic>{
      'explanation': <String, dynamic>{'reason': 'تحقق الاتجاه والهدف.'},
    },
    'verified_at': '2026-07-27T17:05:00+03:00',
  };
}

PredictionRepository _repository(
  _MockTokenStore tokenStore,
  Future<ResponseBody> Function(RequestOptions options) callback,
) {
  when(tokenStore.readAccessToken).thenAnswer((_) async => 'access-token');
  final dio = Dio(BaseOptions(baseUrl: 'https://example.test/api/v1'));
  dio.httpClientAdapter = _CallbackAdapter(callback);
  return PredictionRepository(
    ApiClient(
      baseUrl: 'https://example.test',
      tokenStore: tokenStore,
      dio: dio,
    ),
  );
}

void main() {
  test('loads verification eligibility status', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(options.path, '/community/discussions/discussion-1/verification');
      expect(options.method, 'GET');
      return _jsonBody(<String, dynamic>{
        'discussion_id': 'discussion-1',
        'state': 'eligible',
        'eligible_at': '2026-07-27T17:00:00+03:00',
        'verification': null,
      }, 200);
    });

    final status = await repository.getVerificationStatus('discussion-1');

    expect(status.isEligible, isTrue);
    expect(status.verification, isNull);
  });

  test(
    'submits verification and parses exactly-once reward response',
    () async {
      final tokenStore = _MockTokenStore();
      final repository = _repository(tokenStore, (options) async {
        expect(
          options.path,
          '/community/discussions/discussion-1/verification',
        );
        expect(options.method, 'POST');
        return _jsonBody(<String, dynamic>{
          'verification': _verificationJson(),
          'balance_points': 500,
          'balance_coins': '5.00',
          'idempotent': false,
        }, 200);
      });

      final result = await repository.verifyPrediction('discussion-1');

      expect(result.verification.rewardPoints, 200);
      expect(result.balanceCoins, '5.00');
      expect(result.idempotent, isFalse);
    },
  );

  test('loads personal prediction statistics', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(options.path, '/community/predictions/stats/mine');
      return _jsonBody(<String, dynamic>{
        'verified_predictions': 3,
        'accepted_predictions': 2,
        'accuracy_percent': 66.67,
        'average_score_percent': 71.25,
        'total_reward_points': 250,
        'total_reward_coins': '2.50',
      }, 200);
    });

    final stats = await repository.getMyStats();

    expect(stats.verifiedPredictions, 3);
    expect(stats.accuracyPercent, 66.67);
    expect(stats.totalRewardPoints, 250);
  });

  test('maps unfinished-period conflict from the backend', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      return _jsonBody(<String, dynamic>{
        'detail': 'لم تنتهِ فترة التوقع بعد.',
      }, 409);
    });

    try {
      await repository.verifyPrediction('discussion-1');
      fail('Expected an ApiException.');
    } on ApiException catch (error) {
      expect(error.statusCode, 409);
      expect(error.message, 'لم تنتهِ فترة التوقع بعد.');
    }
  });
}

```

---

### File: `test\prediction_widgets_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_models.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_providers.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_verification_card.dart';

void main() {
  testWidgets('eligible prediction shows verification action', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          predictionVerificationStatusProvider.overrideWith((ref, id) async {
            return PredictionVerificationStatus(
              discussionId: id,
              state: 'eligible',
              eligibleAt: DateTime(2026, 7, 26, 17),
              verification: null,
            );
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PredictionVerificationCard(
              discussionId: 'discussion-eligible',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('تحقق من صحة توقعي'), findsOneWidget);
    expect(find.textContaining('انتهت فترة التوقع'), findsOneWidget);
  });

  testWidgets('waiting prediction shows eligibility date without action', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          predictionVerificationStatusProvider.overrideWith((ref, id) async {
            return PredictionVerificationStatus(
              discussionId: id,
              state: 'waiting',
              eligibleAt: DateTime(2026, 7, 30, 17),
              verification: null,
            );
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PredictionVerificationCard(
              discussionId: 'discussion-waiting',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('تحقق من صحة توقعي'), findsNothing);
    expect(find.textContaining('لم يصبح جاهزًا'), findsOneWidget);
    expect(find.textContaining('30/07/2026'), findsOneWidget);
  });

  testWidgets('verified prediction displays score reward and explanation', (
    tester,
  ) async {
    final verification = PredictionVerification(
      id: 'verification-1',
      discussionId: 'discussion-verified',
      scoreBp: 8750,
      scorePercent: 87.5,
      strength: 'very_strong',
      rewardPoints: 200,
      rewardCoins: '2.00',
      evidence: const <String, dynamic>{
        'explanation': <String, dynamic>{
          'reason': 'تحقق الاتجاه والهدف خلال الفترة المحددة.',
        },
      },
      verifiedAt: DateTime(2026, 7, 27, 17, 5),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          predictionVerificationStatusProvider.overrideWith((ref, id) async {
            return PredictionVerificationStatus(
              discussionId: id,
              state: 'verified',
              eligibleAt: DateTime(2026, 7, 27, 17),
              verification: verification,
            );
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PredictionVerificationCard(
              discussionId: 'discussion-verified',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('قوية جدًا'), findsOneWidget);
    expect(find.textContaining('87.50%'), findsOneWidget);
    expect(find.textContaining('2.00 عملة'), findsOneWidget);
    expect(
      find.text('تحقق الاتجاه والهدف خلال الفترة المحددة.'),
      findsOneWidget,
    );
  });
}

```

---

### File: `test\stock_comparison_and_ads_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/market/stock_comparison_models.dart';
import 'package:sahmi_kasban_mobile/features/monetization/free_plan_ads.dart';

void main() {
  group('InterstitialFrequencyPolicy', () {
    const policy = InterstitialFrequencyPolicy(
      actionsPerAd: 3,
      minimumInterval: Duration(minutes: 4),
    );
    final now = DateTime(2026, 7, 29, 8);

    test('requires enough meaningful actions', () {
      expect(
        policy.canShow(meaningfulActions: 2, now: now, lastShownAt: null),
        isFalse,
      );
      expect(
        policy.canShow(meaningfulActions: 3, now: now, lastShownAt: null),
        isTrue,
      );
    });

    test('enforces the minimum interval after an impression', () {
      expect(
        policy.canShow(
          meaningfulActions: 3,
          now: now,
          lastShownAt: now.subtract(const Duration(minutes: 3)),
        ),
        isFalse,
      );
      expect(
        policy.canShow(
          meaningfulActions: 3,
          now: now,
          lastShownAt: now.subtract(const Duration(minutes: 4)),
        ),
        isTrue,
      );
    });
  });

  test('StockComparisonResult parses costs, ranking, and skipped stocks', () {
    final result = StockComparisonResult.fromJson(<String, dynamic>{
      'comparison_id': 'comparison-id',
      'request_key': 'comparison_test_001',
      'tickers': <String>['COMI', 'DSCW'],
      'best_ticker': 'COMI',
      'summary': 'COMI حصل على أعلى تقييم مقارن.',
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'rank': 1,
          'ticker': 'COMI',
          'analysis_id': 'analysis-id',
          'data_as_of': '2026-07-28T12:00:00Z',
          'signal': 'BUY',
          'final_score': 82.5,
          'confidence': 77,
          'comparison_score': 80.1,
          'trend': 'bullish',
          'rsi': 58.2,
          'average_volume_20': 1200000,
          'risk_level': 'medium',
          'risk_score': 71,
          'entry': 75.1,
          'stop_loss': 71.8,
          'target_1': 80.4,
          'target_2': 84.2,
          'reward_risk_1': 1.6,
        },
      ],
      'failed_items': <Map<String, dynamic>>[
        <String, dynamic>{
          'ticker': 'DSCW',
          'code': 'market_data_unavailable',
          'message': 'بيانات السوق غير متاحة لهذا السهم حاليًا.',
          'retryable': true,
        },
      ],
      'included_allowance': false,
      'comparison_charged_points': 50,
      'comparison_charged_coins': '0.50',
      'analysis_charged_points': 50,
      'analysis_charged_coins': '0.50',
      'allowance_used': 0,
      'allowance_remaining': 0,
      'idempotent': false,
      'balance_points': 900,
      'balance_coins': '9.00',
      'disclaimer': 'ليست توصية شراء أو بيع.',
    });

    expect(result.bestTicker, 'COMI');
    expect(result.comparisonChargedPoints, 50);
    expect(result.analysisChargedPoints, 50);
    expect(result.balanceCoins, '9.00');
    expect(result.items.single.rank, 1);
    expect(result.items.single.comparisonScore, 80.1);
    expect(result.failedItems.single.ticker, 'DSCW');
    expect(result.failedItems.single.retryable, isTrue);
  });
}

```

---

### File: `test\token_store_test.dart`

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    FlutterSecureStorage.setMockInitialValues(<String, String>{});
  });

  test('stores reads and clears the rotating token pair', () async {
    const storage = FlutterSecureStorage();
    final store = TokenStore(storage);

    expect(await store.read(), isNull);

    await store.save(accessToken: 'access-one', refreshToken: 'refresh-one');
    final saved = await store.read();

    expect(saved, isNotNull);
    expect(saved!.accessToken, 'access-one');
    expect(saved.refreshToken, 'refresh-one');
    expect(await store.readAccessToken(), 'access-one');
    expect(await store.readRefreshToken(), 'refresh-one');

    await store.save(accessToken: 'access-two', refreshToken: 'refresh-two');
    expect((await store.read())!.refreshToken, 'refresh-two');

    await store.clear();
    expect(await store.read(), isNull);
  });
}

```

---

### File: `test\wallet_history_screen_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/data/backend_repository.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';
import 'package:sahmi_kasban_mobile/features/wallet/wallet_history_screen.dart';

class _MockBackendRepository extends Mock implements BackendRepository {}

void main() {
  testWidgets('wallet history renders Arabic-safe dates without intl setup', (
    tester,
  ) async {
    final repository = _MockBackendRepository();
    when(() => repository.getWalletHistory(limit: 20, offset: 0)).thenAnswer(
      (_) async => WalletHistoryPage(
        total: 1,
        limit: 20,
        offset: 0,
        items: <WalletEntryModel>[
          WalletEntryModel(
            transactionId: 'weekly:test:2026-07-27',
            entryType: 'weekly_plan_grant',
            amountPoints: 300,
            amountCoins: '3.00',
            status: 'confirmed',
            referenceType: 'subscription',
            referenceId: 'subscription-id',
            details: const <String, dynamic>{},
            createdAt: DateTime.utc(2026, 7, 28, 20, 15),
            confirmedAt: DateTime.utc(2026, 7, 28, 20, 15),
          ),
        ],
      ),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: <Override>[
          backendRepositoryProvider.overrideWithValue(repository),
        ],
        child: const MaterialApp(home: WalletHistoryScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('توزيع الخطة الأسبوعي'), findsOneWidget);
    expect(find.textContaining('الحالة: مكتملة'), findsOneWidget);
    expect(find.textContaining('+3.00 عملة'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

```

---

### File: `test\widget_smoke_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/avatar_assets.dart';
import 'package:sahmi_kasban_mobile/widgets/structured_data_card.dart';

void main() {
  test('generated avatar registry is complete and deterministic', () {
    expect(avatarKeys, hasLength(12));
    expect(avatarKeys.toSet(), hasLength(12));
    expect(avatarAssetPath('avatar_01'), 'assets/avatars/avatar_01.webp');
    expect(avatarAssetPath('unsupported'), 'assets/avatars/avatar_01.webp');
  });

  testWidgets('structured data card renders and expands JSON payload', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: StructuredDataCard(
            title: 'تفاصيل التحليل',
            data: <String, dynamic>{'ticker': 'COMI', 'score': 87.5},
          ),
        ),
      ),
    );

    expect(find.text('تفاصيل التحليل'), findsOneWidget);
    expect(find.textContaining('COMI'), findsOneWidget);
    expect(find.textContaining('87.5'), findsOneWidget);
  });
}

```

---

### File: `test\workmanager_manifest_test.dart`

```dart
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Android manifest disables eager WorkManager startup', () {
    final manifest = File(
      'android/app/src/main/AndroidManifest.xml',
    ).readAsStringSync();

    expect(
      manifest,
      contains('xmlns:tools="http://schemas.android.com/tools"'),
    );
    expect(manifest, contains('androidx.startup.InitializationProvider'));
    expect(manifest, contains('androidx.work.WorkManagerInitializer'));
    expect(manifest, contains('tools:node="remove"'));
  });
}

```

---

### File: `test\core\config\app_config_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/config/app_config.dart';

AppConfig buildConfig({
  String environment = 'production',
  String apiBaseUrl = 'https://api.sahmikasban.example',
  String releasePlatform = 'android',
  String androidPublisher = '1234567890123456',
  String iosPublisher = '1234567890123456',
}) {
  return AppConfig(
    apiBaseUrl: apiBaseUrl,
    appEnvironment: environment,
    releasePlatform: releasePlatform,
    admobAndroidBannerId: 'ca-app-pub-$androidPublisher/1000000001',
    admobIosBannerId: 'ca-app-pub-$iosPublisher/1000000002',
    admobAndroidNativeId: 'ca-app-pub-$androidPublisher/1000000003',
    admobIosNativeId: 'ca-app-pub-$iosPublisher/1000000004',
    admobAndroidInterstitialId: 'ca-app-pub-$androidPublisher/1000000005',
    admobIosInterstitialId: 'ca-app-pub-$iosPublisher/1000000006',
  );
}

void main() {
  test(
    'production Android accepts live Android IDs with iOS test defaults',
    () {
      final config = buildConfig(iosPublisher: AppConfig.googleTestPublisherId);

      expect(config.validateForRuntime, returnsNormally);
    },
  );

  test('production iOS accepts live iOS IDs with Android test defaults', () {
    final config = buildConfig(
      releasePlatform: 'ios',
      androidPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, returnsNormally);
  });

  test('production config rejects an insecure API URL', () {
    final config = buildConfig(apiBaseUrl: 'http://api.example.com');

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production Android rejects Google test Android ad units', () {
    final config = buildConfig(
      androidPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production iOS rejects Google test iOS ad units', () {
    final config = buildConfig(
      releasePlatform: 'ios',
      iosPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production rejects an unknown release platform', () {
    final config = buildConfig(releasePlatform: 'web');

    expect(config.validateForRuntime, throwsStateError);
  });

  test('staging config keeps test integrations available', () {
    final config = buildConfig(
      environment: 'staging',
      apiBaseUrl: 'http://10.0.2.2:8000',
      androidPublisher: AppConfig.googleTestPublisherId,
      iosPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, returnsNormally);
  });
}

```

---

### File: `test\features\market\stock_analysis_report_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';
import 'package:sahmi_kasban_mobile/features/market/stock_analysis_report.dart';

void main() {
  testWidgets('renders Arabic analysis cards without raw payloads', (
    tester,
  ) async {
    final analysis = StockAnalysisResult(
      analysisId: 'analysis-1',
      ticker: 'DSCW',
      cached: false,
      marketSnapshotCached: false,
      chargedPoints: 50,
      chargedCoins: '0.50',
      balancePoints: 250,
      balanceCoins: '2.50',
      dataAsOf: DateTime.utc(2026, 7, 28, 7),
      payload: {
        'market_data': {
          'provider': 'tradingview',
          'interval': '1d',
          'period': '1y',
          'candle_count': 300,
        },
        'analysis': {
          'signal': 'BUY',
          'final_score': 82.11,
          'confidence': 84.73,
          'trade_plan': {
            'entry': 1.97,
            'stop_loss': 1.8778,
            'target_1': 2.1545,
            'target_2': 2.2929,
            'reward_risk_1': 2.0,
            'reward_risk_2': 3.5,
          },
          'engines': {
            'technical': {
              'score': 99.0,
              'confidence': 94.3,
              'details': {'trend': 'uptrend', 'close': 1.97, 'rsi': 67.52},
            },
            'risk': {
              'score': 83.79,
              'confidence': 88.0,
              'details': {'risk_level': 'low', 'total_risk_pct': 16.21},
            },
            'scenario': {
              'score': 69.45,
              'confidence': 75.0,
              'details': {
                'bullish': {'probability_pct': 52.22, 'target': 2.2929},
                'base': {'probability_pct': 34.44, 'target': 2.1545},
                'bearish': {'probability_pct': 13.33, 'target': 1.8778},
              },
            },
          },
          'warnings': <String>[],
        },
        'explanation': 'نتيجة المحركات: شراء مشروط.',
        'disclaimer': 'هذا تحليل آلي لدعم القرار وليس توصية شراء أو بيع.',
      },
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: StockAnalysisReport(analysis: analysis),
          ),
        ),
      ),
    );

    expect(tester.takeException(), isNull);
    expect(find.text('القرار الآلي: شراء مشروط'), findsOneWidget);
    expect(find.text('خطة التداول الافتراضية'), findsOneWidget);
    expect(find.text('الملخص الفني'), findsOneWidget);
    expect(find.text('السيناريوهات المحتملة'), findsOneWidget);
    expect(find.text('البيانات التقنية الخام'), findsNothing);
  });
}

```

---


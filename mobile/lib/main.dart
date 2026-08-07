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

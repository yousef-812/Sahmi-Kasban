import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'app/app.dart';
import 'core/observability/app_observability.dart';

Future<void> _initializeServices() async {
  await MobileAds.instance.initialize();
  try {
    await Firebase.initializeApp();
  } on Object {
    // Firebase remains optional until platform project files are configured.
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppObservability.bootstrap(
    initializeServices: _initializeServices,
    app: const ProviderScope(child: SahmiKasbanApp()),
  );
}

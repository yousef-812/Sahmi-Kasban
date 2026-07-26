import 'dart:ui' as ui;

import 'package:flutter/foundation.dart';
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

    await SentryFlutter.init(
      (options) {
        options.dsn = dsn;
        options.environment = environment;
        if (release.trim().isNotEmpty) {
          options.release = release;
        }
        options.tracesSampleRate = tracesSampleRate;
        options.sendDefaultPii = false;
        options.attachScreenshot = false;
        options.enableAutoSessionTracking = true;
      },
      appRunner: appRunner,
    );
  }

  @visibleForTesting
  static Widget buildErrorWidget(FlutterErrorDetails details) {
    return const Directionality(
      textDirection: TextDirection.rtl,
      child: ColoredBox(
        color: Color(0xFFF7F2EA),
        child: Center(
          child: Semantics(
            liveRegion: true,
            label: 'حدث خطأ غير متوقع. حاول فتح الشاشة مرة أخرى.',
            child: Padding(
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

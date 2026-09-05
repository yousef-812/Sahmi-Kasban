import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/config/app_config.dart';
import '../features/auth/session_controller.dart';
import '../features/monetization/ad_frequency_gate.dart';
import '../features/monetization/app_open_ad_manager.dart';
import '../features/monetization/free_plan_ads.dart';
import '../features/monetization/monetization_repository.dart';
import '../features/notifications/notification_messaging_shell.dart';
import 'app_theme_provider.dart';
import 'router.dart';
import 'theme.dart';

class SahmiKasbanApp extends ConsumerStatefulWidget {
  const SahmiKasbanApp({super.key});

  @override
  ConsumerState<SahmiKasbanApp> createState() => _SahmiKasbanAppState();
}

class _SahmiKasbanAppState extends ConsumerState<SahmiKasbanApp> {
  late final AppOpenAdManager _appOpenAdManager;

  @override
  void initState() {
    super.initState();
    _appOpenAdManager = AppOpenAdManager(
      config: ref.read(appConfigProvider),
      gate: ref.read(adFrequencyGateProvider),
      repository: ref.read(monetizationRepositoryProvider),
      isEnabled: () =>
          ref.read(sessionControllerProvider).profile?.adsEnabled == true,
      isSafeRoute: () {
        final location = ref
            .read(appRouterProvider)
            .routerDelegate
            .currentConfiguration
            .uri
            .toString();
        const unsafe = [
          '/login',
          '/register',
          '/verify-email',
          '/forgot-password',
          '/reset-password',
          '/splash',
          '/onboarding',
        ];
        return !unsafe.any(location.startsWith);
      },
    );
    _appOpenAdManager.start();
  }

  @override
  void dispose() {
    _appOpenAdManager.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp.router(
      title: 'سهمي كسبان',
      debugShowCheckedModeBanner: false,
      theme: SahmiTheme.light(),
      darkTheme: SahmiTheme.dark(),
      themeMode: themeMode,
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

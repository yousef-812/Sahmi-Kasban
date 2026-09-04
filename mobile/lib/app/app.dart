import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../features/monetization/free_plan_ads.dart';
import '../features/notifications/notification_messaging_shell.dart';
import 'app_theme_provider.dart';
import 'router.dart';
import 'theme.dart';

class SahmiKasbanApp extends ConsumerWidget {
  const SahmiKasbanApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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

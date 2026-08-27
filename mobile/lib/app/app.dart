import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/theme/terminal_theme.dart';
import '../core/theme/theme_controller.dart';
import '../features/monetization/free_plan_ads.dart';
import '../features/notifications/notification_messaging_shell.dart';
import 'router.dart';
import 'theme.dart';

class SahmiKasbanApp extends ConsumerWidget {
  const SahmiKasbanApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeControllerProvider);

    return MaterialApp.router(
      title: 'سهمي كسبان',
      debugShowCheckedModeBanner: false,
      theme: SahmiTheme.light(),
      darkTheme: SahmiTheme.dark(),
      themeMode: themeMode.toMaterialThemeMode(),
      routerConfig: router,
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;
        return Directionality(
          textDirection: TextDirection.rtl,
          child: TerminalTheme(
            data: isDark ? defaultDark() : defaultLight(),
            child: NotificationMessagingShell(
              child: FreePlanAdShell(
                child: child ?? const SizedBox.shrink(),
              ),
            ),
          ),
        );
      },
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/observability/app_observability.dart';
import '../domain/models.dart';
import '../features/admin/admin_dashboard_screen.dart';
import '../features/admin/admin_wallet_credit_screen.dart';
import '../features/admin/historical_replay_control_screen.dart';
import '../features/auth/account_recovery_screens.dart';
import '../features/auth/auth_screens.dart';
import '../features/auth/biometric_prompt_screen.dart';
import '../features/auth/session_controller.dart';
import '../features/bootstrap/splash_screen.dart';
import '../features/community/community_create_screen.dart';
import '../features/community/community_detail_screen.dart';
import '../features/community/my_discussions_screen.dart';
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
import '../features/pulse/pulse_screen.dart';
import '../features/analyze/quick_analyze_screen.dart';
import '../features/reports/market_report_screen.dart';
import '../features/reports/reports_screen.dart';
import '../features/wallet/wallet_history_screen.dart';
import '../features/watchlist/watchlist_screen.dart';
import 'terminal_shell.dart';

class _RouterRefreshNotifier extends ChangeNotifier {
  void refresh() => notifyListeners();
}

/// صفحة انتقال سلسة بين شاشات التطبيق لراحة بصرية أفضل.
/// تجمع بين انزلاق خفيف من اليمين (اتجاه RTL) وبهتان ناعم.
CustomTransitionPage<void> _sahmiPage({
  required String childKey,
  required Widget child,
}) {
  return CustomTransitionPage<void>(
    key: ValueKey(childKey),
    child: child,
    transitionDuration: const Duration(milliseconds: 260),
    reverseTransitionDuration: const Duration(milliseconds: 200),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      final curved = CurvedAnimation(
        parent: animation,
        curve: Curves.easeOutCubic,
        reverseCurve: Curves.easeInCubic,
      );
      return FadeTransition(
        opacity: curved,
        child: SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0.06, 0),
            end: Offset.zero,
          ).animate(curved),
          child: child,
        ),
      );
    },
  );
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
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'splash', child: const SplashScreen()),
      ),
      GoRoute(
        path: '/onboarding',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'onboarding', child: const OnboardingScreen()),
      ),
      GoRoute(
        path: '/login',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'login', child: const LoginScreen()),
      ),
      GoRoute(
        path: '/register',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'register', child: const RegisterScreen()),
      ),
      GoRoute(
        path: '/verify-email',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'verify', child: VerifyEmailScreen(email: state.uri.queryParameters['email'])),
      ),
      GoRoute(
        path: '/forgot-password',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'forgot', child: const ForgotPasswordScreen()),
      ),
      GoRoute(
        path: '/reset-password',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'reset', child: ResetPasswordScreen(email: state.uri.queryParameters['email'])),
      ),
      GoRoute(
        path: '/biometric-prompt',
        pageBuilder: (context, state) {
          final extra = state.extra as Map<String, String>? ?? {};
          return _sahmiPage(
            childKey: 'biometric',
            child: BiometricPromptScreen(
              accessToken: extra['accessToken'] ?? '',
              refreshToken: extra['refreshToken'] ?? '',
              onComplete: () => context.go('/pulse'),
            ),
          );
        },
      ),
      ShellRoute(
        builder: (context, state, child) => TerminalShell(child: child),
        routes: [
          GoRoute(
            path: '/pulse',
            builder: (context, state) => const PulseScreen(),
          ),
          GoRoute(
            path: '/home',
            builder: (context, state) => const PulseScreen(),
          ),
          GoRoute(
            path: '/watch',
            builder: (context, state) => const WatchlistScreen(),
          ),
          GoRoute(
            path: '/analyze',
            builder: (context, state) => const QuickAnalyzeScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/stocks',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'stocks', child: const StocksScreen()),
      ),
      GoRoute(
        path: '/stocks/:ticker',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'stocks-${state.pathParameters['ticker']}',
          child: StockDetailScreen(ticker: state.pathParameters['ticker']!),
        ),
      ),
      GoRoute(
        path: '/reports',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'reports', child: const ReportsScreen()),
      ),
      GoRoute(
        path: '/market/compare',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'compare', child: const StockComparisonScreen()),
      ),
      GoRoute(
        path: '/market/analyze/:ticker',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'analyze-${state.pathParameters['ticker']}',
          child: StockAnalysisScreen(ticker: state.pathParameters['ticker']!),
        ),
      ),
      GoRoute(
        path: '/profile/edit',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'profile', child: const ProfileEditScreen()),
      ),
      GoRoute(
        path: '/wallet/history',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'wallet', child: const WalletHistoryScreen()),
      ),
      GoRoute(
        path: '/monetization',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'monetization', child: const MonetizationPage()),
      ),
      GoRoute(
        path: '/notifications',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'notifications', child: const NotificationScreen()),
      ),
      GoRoute(
        path: '/performance',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'performance', child: const PerformanceScreen()),
      ),
      GoRoute(
        path: '/performance/reports/:reportId',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'perf-report-${state.pathParameters['reportId']}',
          child: PerformanceReportScreen(
            reportId: state.pathParameters['reportId']!,
          ),
        ),
      ),
      GoRoute(
        path: '/admin',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'admin', child: const AdminDashboardScreen()),
      ),
      GoRoute(
        path: '/admin/performance',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'admin-perf',
          child: const PerformanceAdminScreen(),
        ),
      ),
      GoRoute(
        path: '/admin/wallet-credit',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'admin-wallet',
          child: const AdminWalletCreditScreen(),
        ),
      ),
      GoRoute(
        path: '/admin/historical-replays',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'admin-replays',
          child: const HistoricalReplayControlScreen(),
        ),
      ),
      GoRoute(
        path: '/community/new',
        pageBuilder: (context, state) =>
            _sahmiPage(childKey: 'community-new', child: const CommunityCreateScreen()),
      ),
      GoRoute(
        path: '/community/mine',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'community-mine',
          child: const MyDiscussionsScreen(),
        ),
      ),
      GoRoute(
        path: '/community/:discussionId',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'community-${state.pathParameters['discussionId']}',
          child: CommunityDetailScreen(
            discussionId: state.pathParameters['discussionId']!,
          ),
        ),
      ),
      GoRoute(
        path: '/reports/:reportId',
        pageBuilder: (context, state) => _sahmiPage(
          childKey: 'report-${state.pathParameters['reportId']}',
          child: MarketReportScreen(
            reportId: state.pathParameters['reportId']!,
            preview: state.extra is MarketReportPreview
                ? state.extra! as MarketReportPreview
                : null,
          ),
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

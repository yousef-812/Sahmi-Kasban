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
        builder: (context, state) => ResetPasswordScreen(
          email: state.uri.queryParameters['email'],
        ),
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
        builder: (context, state) => StockDetailScreen(
          ticker: state.pathParameters['ticker']!,
        ),
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
        builder: (context, state) => StockAnalysisScreen(
          ticker: state.pathParameters['ticker']!,
        ),
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

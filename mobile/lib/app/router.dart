import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../domain/models.dart';
import '../features/admin/admin_dashboard_screen.dart';
import '../features/auth/account_recovery_screens.dart';
import '../features/auth/auth_screens.dart';
import '../features/auth/session_controller.dart';
import '../features/bootstrap/splash_screen.dart';
import '../features/community/community_create_screen.dart';
import '../features/community/community_detail_screen.dart';
import '../features/community/my_discussions_screen.dart';
import '../features/home/dashboard_screen.dart';
import '../features/monetization/monetization_page.dart';
import '../features/notifications/notification_screen.dart';
import '../features/onboarding/onboarding_controller.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/profile/profile_edit_screen.dart';
import '../features/reports/market_report_screen.dart';
import '../features/wallet/wallet_history_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final onboarding = ref.watch(onboardingControllerProvider);
  final session = ref.watch(sessionControllerProvider);

  return GoRouter(
    initialLocation: '/splash',
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
          initialToken: state.uri.queryParameters['token'],
          email: state.uri.queryParameters['email'],
        ),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const DashboardScreen(),
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
        path: '/admin',
        builder: (context, state) => const AdminDashboardScreen(),
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
      if (location == '/admin' && session.profile?.isAdmin != true) {
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

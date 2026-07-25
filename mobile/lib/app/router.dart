import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/auth_screens.dart';
import '../features/auth/session_controller.dart';
import '../features/bootstrap/splash_screen.dart';
import '../features/home/dashboard_screen.dart';
import '../features/onboarding/onboarding_controller.dart';
import '../features/onboarding/onboarding_screen.dart';

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
        path: '/home',
        builder: (context, state) => const DashboardScreen(),
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
      final authRoute = location == '/login' || location == '/register';
      if (!authenticated) {
        return authRoute ? null : '/login';
      }
      if (authRoute || location == '/splash' || location == '/onboarding') {
        return '/home';
      }
      return null;
    },
  );
});

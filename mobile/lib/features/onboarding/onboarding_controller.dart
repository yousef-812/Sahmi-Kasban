import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class OnboardingController extends StateNotifier<AsyncValue<bool>> {
  OnboardingController() : super(const AsyncValue.loading()) {
    load();
  }

  static const _completedKey = 'onboarding_completed';

  Future<void> load() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final preferences = await SharedPreferences.getInstance();
      return preferences.getBool(_completedKey) ?? false;
    });
  }

  Future<void> complete() async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setBool(_completedKey, true);
    state = const AsyncValue.data(true);
  }
}

final onboardingControllerProvider =
    StateNotifierProvider<OnboardingController, AsyncValue<bool>>((ref) {
      return OnboardingController();
    });

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/demo_mode.dart';
import '../../core/network/api_exception.dart';
import '../../core/network/token_store.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';

enum SessionStatus { loading, unauthenticated, authenticated }

class SessionState {
  const SessionState({required this.status, this.profile, this.errorMessage});
  const SessionState.loading() : this(status: SessionStatus.loading);
  const SessionState.unauthenticated({String? errorMessage})
    : this(status: SessionStatus.unauthenticated, errorMessage: errorMessage);
  const SessionState.authenticated(UserProfile profile)
    : this(status: SessionStatus.authenticated, profile: profile);

  final SessionStatus status;
  final UserProfile? profile;
  final String? errorMessage;
}

class SessionController extends StateNotifier<SessionState> {
  SessionController({
    required BackendRepository repository,
    required TokenStore tokenStore,
  }) : _repository = repository,
       _tokenStore = tokenStore,
       super(const SessionState.loading()) {
    restore();
  }

  final BackendRepository _repository;
  final TokenStore _tokenStore;

  Future<void> restore() async {
    if (DemoMode.enabled) {
      loginAsDemo();
      return;
    }

    state = const SessionState.loading();
    try {
      final tokens = await _tokenStore.read();
      if (tokens == null) {
        state = const SessionState.unauthenticated();
        return;
      }

      final profile = await _repository.getProfile();
      state = SessionState.authenticated(profile);
    } on ApiException catch (error) {
      if (error.statusCode == 401) {
        await _clearTokensSafely();
      }
      state = SessionState.unauthenticated(errorMessage: error.message);
    } on Object {
      await _clearTokensSafely();
      state = const SessionState.unauthenticated(
        errorMessage: 'تعذر استعادة الجلسة السابقة. سجل الدخول مرة أخرى.',
      );
    }
  }

  Future<void> _clearTokensSafely() async {
    try {
      await _tokenStore.clear();
    } on Object {
      // Corrupted or restored encrypted storage must not prevent app startup.
    }
  }

  Future<void> login({required String email, required String password}) async {
    state = const SessionState.loading();
    try {
      await _repository.login(email: email, password: password);
      final profile = await _repository.getProfile();
      state = SessionState.authenticated(profile);
    } on ApiException catch (error) {
      state = SessionState.unauthenticated(errorMessage: error.message);
      rethrow;
    }
  }

  void loginAsDemo() {
    state = const SessionState.authenticated(
      UserProfile(
        id: 'demo-user',
        email: 'demo@sahmi-kasban.local',
        displayName: 'مستخدم تجريبي',
        avatarKey: 'avatar_1',
        emailVerified: true,
        planCode: 'free',
        balancePoints: 300,
        balanceCoins: '3.00',
        weeklyCoins: '3.00',
        adsEnabled: true,
      ),
    );
  }

  Future<RegistrationResult> register({
    required String email,
    required String password,
    required String displayName,
    String? referralCode,
  }) {
    return _repository.register(
      email: email,
      password: password,
      displayName: displayName,
      referralCode: referralCode,
    );
  }

  Future<void> refreshProfile() async {
    if (state.status != SessionStatus.authenticated) {
      return;
    }
    final profile = await _repository.getProfile();
    state = SessionState.authenticated(profile);
  }

  Future<UserProfile> updateProfile({
    required String displayName,
    required String avatarKey,
  }) async {
    final profile = await _repository.updateProfile(
      displayName: displayName,
      avatarKey: avatarKey,
    );
    state = SessionState.authenticated(profile);
    return profile;
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const SessionState.unauthenticated();
  }
}

final sessionControllerProvider =
    StateNotifierProvider<SessionController, SessionState>((ref) {
      return SessionController(
        repository: ref.watch(backendRepositoryProvider),
        tokenStore: ref.watch(tokenStoreProvider),
      );
    });

import 'package:flutter_riverpod/flutter_riverpod.dart';

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
  })  : _repository = repository,
        _tokenStore = tokenStore,
        super(const SessionState.loading()) {
    restore();
  }

  final BackendRepository _repository;
  final TokenStore _tokenStore;

  Future<void> restore() async {
    state = const SessionState.loading();
    final tokens = await _tokenStore.read();
    if (tokens == null) {
      state = const SessionState.unauthenticated();
      return;
    }
    try {
      final profile = await _repository.getProfile();
      state = SessionState.authenticated(profile);
    } on ApiException catch (error) {
      if (error.statusCode == 401) {
        await _tokenStore.clear();
      }
      state = SessionState.unauthenticated(errorMessage: error.message);
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

  Future<RegistrationResult> register({
    required String email,
    required String password,
    required String displayName,
  }) {
    return _repository.register(
      email: email,
      password: password,
      displayName: displayName,
    );
  }

  Future<void> refreshProfile() async {
    if (state.status != SessionStatus.authenticated) {
      return;
    }
    final profile = await _repository.getProfile();
    state = SessionState.authenticated(profile);
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

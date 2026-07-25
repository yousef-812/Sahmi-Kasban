import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/network/api_client.dart';
import '../core/network/api_exception.dart';
import '../core/network/token_store.dart';
import '../domain/models.dart';

class BackendRepository {
  BackendRepository({
    required ApiClient apiClient,
    required TokenStore tokenStore,
  })  : _apiClient = apiClient,
        _tokenStore = tokenStore;

  final ApiClient _apiClient;
  final TokenStore _tokenStore;

  Future<RegistrationResult> register({
    required String email,
    required String password,
    required String displayName,
    String avatarKey = 'avatar_01',
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/auth/register',
        data: <String, dynamic>{
          'email': email.trim(),
          'password': password,
          'display_name': displayName.trim(),
          'avatar_key': avatarKey,
        },
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );
      return RegistrationResult.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<TokenPair> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/auth/login',
        data: <String, dynamic>{
          'email': email.trim(),
          'password': password,
        },
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );
      final tokens = TokenPair.fromJson(_requiredData(response));
      await _tokenStore.save(
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      );
      return tokens;
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> logout() async {
    final refreshToken = await _tokenStore.readRefreshToken();
    try {
      if (refreshToken != null) {
        await _apiClient.dio.post<Map<String, dynamic>>(
          '/auth/logout',
          data: <String, dynamic>{'refresh_token': refreshToken},
        );
      }
    } on Object {
      // Local logout must still complete if the network is unavailable.
    } finally {
      await _tokenStore.clear();
    }
  }

  Future<UserProfile> getProfile() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/profile/me',
      );
      return UserProfile.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<WalletSummary> getWallet() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>('/wallet');
      return WalletSummary.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketReportPreview?> getLatestReportPreview() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/reports/latest/preview',
      );
      return MarketReportPreview.fromJson(_requiredData(response));
    } on DioException catch (error) {
      if (error.response?.statusCode == 404) {
        return null;
      }
      throw _apiClient.mapError(error);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _requiredData(Response<Map<String, dynamic>> response) {
    final data = response.data;
    if (data == null) {
      throw const ApiException(message: 'استجابة الخادم فارغة.');
    }
    return data;
  }
}

final backendRepositoryProvider = Provider<BackendRepository>((ref) {
  return BackendRepository(
    apiClient: ref.watch(apiClientProvider),
    tokenStore: ref.watch(tokenStoreProvider),
  );
});

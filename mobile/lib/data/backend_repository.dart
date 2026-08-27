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
  }) : _apiClient = apiClient,
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

  Future<String> verifyEmail({required String email, required String code}) {
    return _anonymousMessage(
      path: '/auth/verify-email',
      data: <String, dynamic>{'email': email.trim(), 'code': code.trim()},
    );
  }

  Future<String> resendVerification(String email) {
    return _anonymousMessage(
      path: '/auth/resend-verification',
      data: <String, dynamic>{'email': email.trim()},
    );
  }

  Future<String> forgotPassword(String email) {
    return _anonymousMessage(
      path: '/auth/forgot-password',
      data: <String, dynamic>{'email': email.trim()},
    );
  }

  Future<String> resetPassword({
    required String email,
    required String code,
    required String newPassword,
  }) {
    return _anonymousMessage(
      path: '/auth/reset-password',
      data: <String, dynamic>{
        'email': email.trim(),
        'code': code.trim(),
        'new_password': newPassword,
      },
    );
  }

  Future<TokenPair> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/auth/login',
        data: <String, dynamic>{'email': email.trim(), 'password': password},
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

  Future<List<AvatarOption>> getAvatarOptions() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/profile/avatars',
      );
      final payload = _requiredData(response);
      final rawItems = payload['avatars'];
      if (rawItems is! List) {
        throw const ApiException(message: 'قائمة الصور الرمزية غير صالحة.');
      }
      return rawItems
          .map((item) => AvatarOption.fromJson(_requiredMap(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<UserProfile> updateProfile({
    required String displayName,
    required String avatarKey,
  }) async {
    try {
      final response = await _apiClient.dio.patch<Map<String, dynamic>>(
        '/profile/me',
        data: <String, dynamic>{
          'display_name': displayName.trim(),
          'avatar_key': avatarKey,
        },
      );
      return UserProfile.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<WalletSummary> getWallet() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/wallet',
      );
      return WalletSummary.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<WalletHistoryPage> getWalletHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/wallet/history',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return WalletHistoryPage.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<MarketInstrument>> searchInstruments(
    String query, {
    int limit = 30,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/instruments',
        queryParameters: <String, dynamic>{
          'query': query.trim().toUpperCase(),
          'limit': limit,
        },
      );
      final payload = _requiredData(response);
      final rawItems = payload['items'];
      if (rawItems is! List) {
        throw const ApiException(message: 'قائمة الأسهم غير صالحة.');
      }
      return rawItems
          .map((item) => MarketInstrument.fromJson(_requiredMap(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<StockAnalysisResult> analyzeStock(String ticker) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/stocks/${ticker.trim().toUpperCase()}/analysis',
        data: const <String, dynamic>{'language': 'ar'},
      );
      return StockAnalysisResult.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<StockAnalysisResult?> getLatestOwnedStockAnalysis(
    String ticker,
  ) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/stocks/${ticker.trim().toUpperCase()}/analysis/latest',
      );
      return StockAnalysisResult.fromJson(_requiredData(response));
    } on DioException catch (error) {
      if (error.response?.statusCode == 404) {
        return null;
      }
      throw _apiClient.mapError(error);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<AnalysisHistoryResponse> getAnalysisHistory({int limit = 10}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/analysis-history',
        queryParameters: <String, dynamic>{'limit': limit},
      );
      return AnalysisHistoryResponse.fromJson(_requiredData(response));
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

  Future<MarketReport> getMarketReport(String reportId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/reports/$reportId',
      );
      return MarketReport.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketQuotesSnapshot> getMarketQuotes() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/quotes',
      );
      return MarketQuotesSnapshot.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketQuote> getMarketQuote(
    String ticker, {
    bool forceRefresh = false,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/quotes/${ticker.trim().toUpperCase()}',
        queryParameters: <String, dynamic>{
          if (forceRefresh) 'force_refresh': 'true',
        },
      );
      return MarketQuote.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MarketReportUnlockResult> unlockMarketReport(String reportId) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/market/reports/$reportId/unlock',
      );
      return MarketReportUnlockResult.fromJson(_requiredData(response));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<String> _anonymousMessage({
    required String path,
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        path,
        data: data,
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );
      return (_requiredData(response)['message'] as String?) ??
          'تم تنفيذ الطلب.';
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

Map<String, dynamic> _requiredData(Response<Map<String, dynamic>> response) {
  final data = response.data;
  if (data == null) {
    throw const ApiException(message: 'استجابة الخادم غير صالحة.');
  }
  return data;
}

Map<String, dynamic> _requiredMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return value.map((key, item) => MapEntry(key.toString(), item));
  }
  throw const ApiException(message: 'صيغة البيانات غير صالحة.');
}

final backendRepositoryProvider = Provider<BackendRepository>((ref) {
  return BackendRepository(
    apiClient: ref.watch(apiClientProvider),
    tokenStore: ref.watch(tokenStoreProvider),
  );
});

import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';
import 'api_exception.dart';
import 'token_store.dart';

class ApiClient {
  ApiClient({
    required String baseUrl,
    required TokenStore tokenStore,
    Dio? dio,
    Dio? refreshDio,
  }) : _tokenStore = tokenStore,
       _dio = dio ?? Dio(BaseOptions(baseUrl: '$baseUrl/api/v1')),
       _refreshDio =
           refreshDio ?? Dio(BaseOptions(baseUrl: '$baseUrl/api/v1')) {
    _dio.interceptors.add(
      InterceptorsWrapper(onRequest: _onRequest, onError: _onError),
    );
  }

  final TokenStore _tokenStore;
  final Dio _dio;
  final Dio _refreshDio;
  Future<String?>? _refreshFuture;

  Dio get dio => _dio;

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (options.extra['anonymous'] == true) {
      handler.next(options);
      return;
    }
    final accessToken = await _tokenStore.readAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  Future<void> _onError(
    DioException error,
    ErrorInterceptorHandler handler,
  ) async {
    final request = error.requestOptions;
    final shouldRefresh =
        error.response?.statusCode == 401 &&
        request.extra['anonymous'] != true &&
        request.extra['retried'] != true &&
        !request.path.endsWith('/auth/refresh');
    if (!shouldRefresh) {
      handler.next(error);
      return;
    }

    final accessToken = await _refreshAccessToken();
    if (accessToken == null) {
      handler.next(error);
      return;
    }

    request.extra['retried'] = true;
    request.headers['Authorization'] = 'Bearer $accessToken';
    try {
      final response = await _dio.fetch<Object?>(request);
      handler.resolve(response);
    } on DioException catch (retryError) {
      handler.next(retryError);
    }
  }

  Future<String?> _refreshAccessToken() {
    final activeRefresh = _refreshFuture;
    if (activeRefresh != null) {
      return activeRefresh;
    }
    final refresh = _performRefresh();
    _refreshFuture = refresh;
    return refresh.whenComplete(() => _refreshFuture = null);
  }

  Future<String?> _performRefresh() async {
    final refreshToken = await _tokenStore.readRefreshToken();
    if (refreshToken == null) {
      return null;
    }
    try {
      final response = await _refreshDio.post<Map<String, dynamic>>(
        '/auth/refresh',
        data: <String, dynamic>{'refresh_token': refreshToken},
      );
      final data = response.data;
      final accessToken = data?['access_token'] as String?;
      final rotatedRefreshToken = data?['refresh_token'] as String?;
      if (accessToken == null || rotatedRefreshToken == null) {
        await _tokenStore.clear();
        return null;
      }
      await _tokenStore.save(
        accessToken: accessToken,
        refreshToken: rotatedRefreshToken,
      );
      return accessToken;
    } on DioException {
      await _tokenStore.clear();
      return null;
    }
  }

  ApiException mapError(Object error) {
    if (error is ApiException) {
      return error;
    }
    if (error is DioException) {
      final response = error.response;
      final payload = response?.data;
      return ApiException(
        message: _extractMessage(payload),
        statusCode: response?.statusCode,
        payload: payload,
        retryAfterSeconds: _parseRetryAfter(response?.headers),
      );
    }
    return ApiException(message: error.toString());
  }

  String _extractMessage(Object? payload) {
    const fallback = 'تعذر الاتصال بالخادم. حاول مرة أخرى.';
    if (payload is! Map) {
      return fallback;
    }
    final detail = payload['detail'];
    if (detail is String && detail.trim().isNotEmpty) {
      return detail.trim();
    }
    if (detail is List) {
      final messages = detail
          .map((item) {
            if (item is Map) {
              final message = item['msg'];
              if (message is String && message.trim().isNotEmpty) {
                return message.trim();
              }
            }
            return null;
          })
          .whereType<String>()
          .toList(growable: false);
      if (messages.isNotEmpty) {
        return messages.join('\n');
      }
    }
    return fallback;
  }

  int? _parseRetryAfter(Headers? headers) {
    if (headers == null) {
      return null;
    }
    return int.tryParse(headers.value('retry-after') ?? '');
  }
}

final apiClientProvider = Provider<ApiClient>((ref) {
  final config = ref.watch(appConfigProvider);
  final tokenStore = ref.watch(tokenStoreProvider);
  return ApiClient(baseUrl: config.apiBaseUrl, tokenStore: tokenStore);
});

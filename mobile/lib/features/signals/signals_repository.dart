import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'signals_models.dart';

class SignalsRepository {
  const SignalsRepository(this._apiClient);

  final ApiClient _apiClient;

  /// `GET /signals` — إشارات المتصل (ومشاركة المصدر التلقائي) مع فلاتر اختيارية.
  Future<ApiList<Signal>> list({
    String? state,
    String? ticker,
    bool mine = false,
  }) async {
    try {
      final parameters = <String, dynamic>{'mine': mine};
      if (state != null && state.isNotEmpty) {
        parameters['state'] = state;
      }
      if (ticker != null && ticker.isNotEmpty) {
        parameters['ticker'] = ticker;
      }
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/signals',
        queryParameters: parameters,
      );
      return ApiList.fromJson(
        _required(response.data),
        (Object? item) => Signal.fromJson(_map(item)),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /signals/{id}` — إشارة واحدة مع سجل أحداثها (أو 404).
  Future<Signal> detail(String signalId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/signals/$signalId',
      );
      return Signal.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /alerts` — صندوق تنبيهات المتصل.
  Future<ApiList<AlertItem>> alerts({
    int limit = 50,
    bool unreadOnly = false,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/alerts',
        queryParameters: <String, dynamic>{
          'limit': limit,
          'unreadOnly': unreadOnly,
        },
      );
      return ApiList.fromJson(
        _required(response.data),
        (Object? item) => AlertItem.fromJson(_map(item)),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `POST /alerts/{id}/read` — تعليم تنبيه واحد كمقروء.
  Future<AlertItem> markAlertRead(String alertId) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/alerts/$alertId/read',
      );
      return AlertItem.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `POST /alerts/read-all` — تعليم كل التنبيهات كمقروءة، يرجع عدد المُحدَّث.
  Future<int> markAllAlertsRead() async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/alerts/read-all',
      );
      return _required(response.data)['updated'] as int? ?? 0;
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Signals response is empty.');
    }
    return value;
  }

  Map<String, dynamic> _map(Object? value) => value is Map<String, dynamic>
      ? value
      : value is Map
      ? Map<String, dynamic>.from(value)
      : <String, dynamic>{};
}

final signalsRepositoryProvider = Provider<SignalsRepository>((ref) {
  return SignalsRepository(ref.watch(apiClientProvider));
});

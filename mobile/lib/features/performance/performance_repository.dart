import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'performance_models.dart';

class PerformanceRepository {
  const PerformanceRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<PerformanceSummary> summary(int window) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/performance/summary',
        queryParameters: <String, dynamic>{'window': window},
      );
      return PerformanceSummary.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PerformanceReportPage> reports({
    int limit = 30,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/performance/reports',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return PerformanceReportPage.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PerformanceReportDetail> reportDetail(String reportId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/performance/reports/$reportId',
      );
      return PerformanceReportDetail.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<PerformanceDelayedItem>> delayed() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/performance/delayed',
        queryParameters: const <String, dynamic>{'limit': 100},
      );
      final payload = _required(response.data);
      return _list(payload['items'])
          .map((item) => PerformanceDelayedItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> evaluateDue({int limit = 20}) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/performance/evaluate-due',
        data: <String, dynamic>{'limit': limit},
      );
      return _required(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> retryReport(String reportId) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/performance/evaluations/$reportId/retry',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<String> exportCsv(int window) async {
    try {
      final response = await _apiClient.dio.get<String>(
        '/admin/operations/performance/export.csv',
        queryParameters: <String, dynamic>{'window': window},
        options: Options(responseType: ResponseType.plain),
      );
      return response.data ?? '';
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> correctOutcome({
    required String outcomeId,
    required String reason,
    required double sessionOpen,
    required double sessionHigh,
    required double sessionLow,
    required double sessionClose,
    required String provider,
    required String dataFingerprint,
    required DateTime dataAsOf,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/performance/outcomes/$outcomeId/corrections',
        data: <String, dynamic>{
          'reason': reason.trim(),
          'session_open': sessionOpen,
          'session_high': sessionHigh,
          'session_low': sessionLow,
          'session_close': sessionClose,
          'provider': provider.trim(),
          'data_fingerprint': dataFingerprint.trim(),
          'data_as_of': dataAsOf.toUtc().toIso8601String(),
        },
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Performance response is empty.');
    }
    return value;
  }

  List<dynamic> _list(Object? value) => value is List ? value : const [];

  Map<String, dynamic> _map(Object? value) => value is Map<String, dynamic>
      ? value
      : value is Map
      ? Map<String, dynamic>.from(value)
      : <String, dynamic>{};
}

final performanceRepositoryProvider = Provider<PerformanceRepository>((ref) {
  return PerformanceRepository(ref.watch(apiClientProvider));
});

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'labs_models.dart';

class LabsRepository {
  const LabsRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<LabsBacktestJob> createBacktestJob(LabsBacktestQuery query) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/labs/backtest-jobs',
        data: <String, dynamic>{
          'start_date': _formatDate(query.startDate),
          'end_date': _formatDate(query.endDate),
          if (query.rank != null) 'rank': query.rank,
          'exit_mode': query.exitMode,
        },
        options: Options(receiveTimeout: const Duration(seconds: 30)),
      );
      return LabsBacktestJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<LabsBacktestJob> backtestJob(String jobId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/labs/backtest-jobs/$jobId',
      );
      return LabsBacktestJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> deleteBacktestJob(String jobId) async {
    try {
      await _apiClient.dio.delete<void>('/labs/backtest-jobs/$jobId');
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<LabsBacktestJob>> backtestJobs({int limit = 50}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/labs/backtest-jobs',
        queryParameters: <String, dynamic>{'limit': limit},
      );
      final rawItems = _required(response.data)['items'];
      if (rawItems is! List) {
        return const <LabsBacktestJob>[];
      }
      return rawItems
          .whereType<Map<String, dynamic>>()
          .map(LabsBacktestJob.fromJson)
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  String _formatDate(DateTime value) {
    final month = value.month.toString().padLeft(2, '0');
    final day = value.day.toString().padLeft(2, '0');
    return '${value.year}-$month-$day';
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Labs response is empty.');
    }
    return value;
  }
}

final labsRepositoryProvider = Provider<LabsRepository>((ref) {
  return LabsRepository(ref.watch(apiClientProvider));
});

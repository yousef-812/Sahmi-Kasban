import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'labs_models.dart';

class LabsRepository {
  const LabsRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<LabsBacktestResult> dailyReportBacktest(
    LabsBacktestQuery query,
  ) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/labs/daily-report-backtest',
        queryParameters: <String, dynamic>{
          'start_date': _formatDate(query.startDate),
          'end_date': _formatDate(query.endDate),
          if (query.rank != null) 'rank': query.rank,
          'exit_mode': query.exitMode,
        },
        options: Options(receiveTimeout: const Duration(seconds: 120)),
      );
      return LabsBacktestResult.fromJson(_required(response.data));
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

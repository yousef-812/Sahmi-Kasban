import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'admin_models.dart';
import 'historical_replay_models.dart';

class AdminRepository {
  const AdminRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<AdminOverview> overview() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/overview',
      );
      return AdminOverview.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<OperationalSetting>> settings() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/settings',
      );
      return _list(_required(response.data)['items'])
          .map((item) => OperationalSetting.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> updateSetting(String key, Object value) async {
    try {
      await _apiClient.dio.put<Map<String, dynamic>>(
        '/admin/operations/settings/$key',
        data: <String, dynamic>{'value': value},
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<ServiceHealth>> providers({bool probe = false}) async {
    try {
      final response = probe
          ? await _apiClient.dio.post<Map<String, dynamic>>(
              '/admin/operations/providers/probe',
            )
          : await _apiClient.dio.get<Map<String, dynamic>>(
              '/admin/operations/providers',
            );
      return _list(_required(response.data)['items'])
          .map((item) => ServiceHealth.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AdminUserItem>> users() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/users',
        queryParameters: const <String, dynamic>{'limit': 100},
      );
      return _list(_required(response.data)['items'])
          .map((item) => AdminUserItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> creditUserCoins({
    required String userId,
    required int amountCoins,
    required String reason,
    required String requestId,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/users/$userId/wallet-credit',
        data: <String, dynamic>{
          'amount_coins': amountCoins,
          'reason': reason.trim(),
          'request_id': requestId,
        },
      );
      return _required(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<HistoricalReplayJob>> historicalReplayJobs() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs',
        queryParameters: const <String, dynamic>{'limit': 50},
      );
      return _list(_required(response.data)['items'])
          .map((item) => HistoricalReplayJob.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> createHistoricalReplay({
    required DateTime startDate,
    required DateTime endDate,
    required int horizonSessions,
  }) async {
    try {
      final requestKey = 'replay_${DateTime.now().microsecondsSinceEpoch}';
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs',
        data: <String, dynamic>{
          'request_key': requestKey,
          'start_date': _dateOnly(startDate),
          'end_date': _dateOnly(endDate),
          'horizon_sessions': horizonSessions,
          'min_train_size': 200,
          'neutral_band_pct': 1.0,
        },
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<HistoricalReplayJob>> createHistoricalReplayBatch({
    required List<HistoricalReplayWindow> windows,
    required int horizonSessions,
  }) async {
    if (windows.length < 2) {
      throw const FormatException('أضف فترتين على الأقل لتشغيل دفعة.');
    }
    try {
      final requestKeyPrefix =
          'replay_batch_${DateTime.now().microsecondsSinceEpoch}';
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/batches',
        data: <String, dynamic>{
          'request_key_prefix': requestKeyPrefix,
          'windows': windows.map((window) => window.toJson()).toList(),
          'horizon_sessions': horizonSessions,
          'min_train_size': 200,
          'neutral_band_pct': 1.0,
        },
      );
      return _list(_required(response.data)['items'])
          .map((item) => HistoricalReplayJob.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> historicalReplayJob(String jobId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs/$jobId',
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<HistoricalReplayJob> pauseHistoricalReplay(String jobId) {
    return _controlHistoricalReplay(jobId, 'pause');
  }

  Future<HistoricalReplayJob> resumeHistoricalReplay(String jobId) {
    return _controlHistoricalReplay(jobId, 'resume');
  }

  Future<HistoricalReplayJob> cancelHistoricalReplay(String jobId) {
    return _controlHistoricalReplay(jobId, 'cancel');
  }

  Future<HistoricalReplayJob> _controlHistoricalReplay(
    String jobId,
    String action,
  ) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/historical-replays/jobs/$jobId/$action',
      );
      return HistoricalReplayJob.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<({Uint8List bytes, String filename})> downloadHistoricalReplay(
    String jobId,
  ) async {
    try {
      final response = await _apiClient.dio.get<List<int>>(
        '/admin/operations/historical-replays/jobs/$jobId/export.csv',
        options: Options(responseType: ResponseType.bytes),
      );
      final data = response.data;
      if (data == null || data.isEmpty) {
        throw const FormatException('ملف الاختبار فارغ.');
      }
      final disposition = response.headers.value('content-disposition') ?? '';
      final filename =
          RegExp('filename="?([^";]+)').firstMatch(disposition)?.group(1) ??
          'sahmi-engine-replay-$jobId.csv';
      return (bytes: Uint8List.fromList(data), filename: filename);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AdminAuditItem>> audit() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/operations/audit',
        queryParameters: const <String, dynamic>{'limit': 100},
      );
      return _list(_required(response.data)['items'])
          .map((item) => AdminAuditItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<AdminDiscussionItem>> discussions({
    String status = 'pending_review',
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/admin/community/discussions',
        queryParameters: <String, dynamic>{
          'discussion_status': status,
          'limit': 100,
        },
      );
      return _list(_required(response.data)['items'])
          .map((item) => AdminDiscussionItem.fromJson(_map(item)))
          .toList(growable: false);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> moderateDiscussion({
    required String discussionId,
    required String action,
    String? reasonCode,
    Map<String, dynamic>? prediction,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/community/discussions/$discussionId/action',
        data: <String, dynamic>{
          'action': action,
          if (reasonCode != null) 'reason_code': reasonCode,
          'details': 'Flutter administration dashboard',
          if (prediction != null) 'prediction': prediction,
        },
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> setUserBlocked(AdminUserItem user, bool blocked) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/community/users/${user.id}/${blocked ? 'block' : 'unblock'}',
        data: const <String, dynamic>{
          'reason_code': 'manual_admin_action',
          'details': 'Flutter administration dashboard',
        },
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> broadcast({
    required String title,
    required String body,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/admin/operations/notifications/broadcast',
        data: <String, dynamic>{
          'title': title,
          'body': body,
          'category': 'announcement',
          'audience': 'active',
        },
      );
      return _required(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  String _dateOnly(DateTime value) {
    return '${value.year.toString().padLeft(4, '0')}-'
        '${value.month.toString().padLeft(2, '0')}-'
        '${value.day.toString().padLeft(2, '0')}';
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) throw const FormatException('Admin response is empty.');
    return value;
  }

  List<dynamic> _list(Object? value) => value is List ? value : const [];
  Map<String, dynamic> _map(Object? value) => value is Map<String, dynamic>
      ? value
      : value is Map
      ? Map<String, dynamic>.from(value)
      : <String, dynamic>{};
}

final adminRepositoryProvider = Provider<AdminRepository>((ref) {
  return AdminRepository(ref.watch(apiClientProvider));
});

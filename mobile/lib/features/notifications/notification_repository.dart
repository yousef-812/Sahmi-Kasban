import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'notification_models.dart';

class NotificationRepository {
  const NotificationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<NotificationPage> listNotifications({
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/notifications',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return NotificationPage.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> markRead(String notificationId) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/notifications/$notificationId/read',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> markAllRead() async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/notifications/read-all',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> registerDevice({
    required String token,
    required String platform,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/notifications/devices',
        data: <String, dynamic>{'token': token, 'platform': platform},
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Notification response is empty.');
    }
    return value;
  }
}

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.watch(apiClientProvider));
});

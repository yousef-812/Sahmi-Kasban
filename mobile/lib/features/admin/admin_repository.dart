import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'admin_models.dart';

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

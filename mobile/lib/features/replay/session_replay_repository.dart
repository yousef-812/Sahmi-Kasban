import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'session_replay_models.dart';

class SessionReplayRepository {
  const SessionReplayRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<SessionReplay> fetch({
    required String ticker,
    required String interval,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/session-replay',
        queryParameters: <String, dynamic>{
          'ticker': ticker.trim().toUpperCase(),
          'interval': interval,
        },
      );
      final data = response.data;
      if (data == null) {
        throw const FormatException('Session replay response is empty.');
      }
      return SessionReplay.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

final sessionReplayRepositoryProvider =
    Provider<SessionReplayRepository>((ref) {
  return SessionReplayRepository(ref.watch(apiClientProvider));
});

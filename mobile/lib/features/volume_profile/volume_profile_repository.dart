import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'volume_profile_models.dart';

class VolumeProfileRepository {
  const VolumeProfileRepository(this._apiClient);

  final ApiClient _apiClient;

  /// `GET /stocks/{ticker}/volume-profile?days=N` — POC/منطقة القيمة (WP-30).
  Future<StockVolumeProfileSnapshot> volumeProfile(
    String ticker, {
    int days = 250,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/stocks/$ticker/volume-profile',
        queryParameters: <String, dynamic>{'days': days},
      );
      final data = response.data;
      if (data == null) {
        throw const FormatException('Volume profile response is empty.');
      }
      return StockVolumeProfileSnapshot.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

final volumeProfileRepositoryProvider = Provider<VolumeProfileRepository>((ref) {
  return VolumeProfileRepository(ref.watch(apiClientProvider));
});

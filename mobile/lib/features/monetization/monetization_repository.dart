import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'monetization_models.dart';

class MonetizationRepository {
  const MonetizationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<MonetizationCatalog> getCatalog() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/monetization/catalog',
      );
      return MonetizationCatalog.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<MonetizationStatusModel> getStatus() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/monetization/status',
      );
      return MonetizationStatusModel.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<RewardedAdSessionModel> createRewardedAdSession({
    required String platform,
    String adFormat = 'rewarded',
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/rewarded-ads/session',
        data: <String, dynamic>{'platform': platform, 'ad_format': adFormat},
      );
      return RewardedAdSessionModel.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<RewardedAdSimulationResultModel> claimRewardedAdSession({
    required RewardedAdSessionModel session,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/rewarded-ads/sessions/${session.sessionId}/claim',
        data: <String, dynamic>{'custom_data': session.customData},
      );
      return RewardedAdSimulationResultModel.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<RewardedAdSimulationResultModel> simulateRewardedAd({
    required RewardedAdSessionModel session,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/rewarded-ads/sessions/${session.sessionId}/simulate',
        data: <String, dynamic>{'custom_data': session.customData},
      );
      return RewardedAdSimulationResultModel.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PurchaseVerificationResultModel> verifyGooglePlayPurchase({
    required String productId,
    required String purchaseToken,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/monetization/google-play/purchases/verify',
        data: <String, dynamic>{
          'product_id': productId,
          'purchase_token': purchaseToken,
        },
      );
      return PurchaseVerificationResultModel.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> recordAdTelemetry({
    required String adType,
    required String eventType,
    String? adUnitId,
    String platform = 'android',
    String? errorMessage,
  }) async {
    try {
      await _apiClient.dio.post<void>(
        '/monetization/ads/telemetry',
        data: <String, dynamic>{
          'ad_type': adType,
          'event_type': eventType,
          if (adUnitId != null) 'ad_unit_id': adUnitId,
          'platform': platform,
          if (errorMessage != null) 'error_message': errorMessage,
        },
      );
    } on Object {
      // Telemetry is non-blocking
    }
  }

  Map<String, dynamic> _requiredData(Map<String, dynamic>? data) {
    if (data == null) {
      throw StateError('Monetization response is empty.');
    }
    return data;
  }
}

final monetizationRepositoryProvider = Provider<MonetizationRepository>((ref) {
  return MonetizationRepository(ref.watch(apiClientProvider));
});

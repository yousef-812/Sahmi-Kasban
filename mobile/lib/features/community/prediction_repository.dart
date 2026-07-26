import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'prediction_models.dart';

class PredictionRepository {
  const PredictionRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<PredictionVerificationStatus> getVerificationStatus(
    String discussionId,
  ) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions/$discussionId/verification',
      );
      return PredictionVerificationStatus.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PredictionVerificationSubmission> verifyPrediction(
    String discussionId,
  ) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/verification',
      );
      return PredictionVerificationSubmission.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<PredictionStats> getMyStats() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/predictions/stats/mine',
      );
      return PredictionStats.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _requiredData(Map<String, dynamic>? data) {
    if (data == null) {
      throw const FormatException('Prediction response is empty.');
    }
    return data;
  }
}

final predictionRepositoryProvider = Provider<PredictionRepository>((ref) {
  return PredictionRepository(ref.watch(apiClientProvider));
});

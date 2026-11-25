import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'market_models.dart';

class MarketRepository {
  const MarketRepository(this._apiClient);

  final ApiClient _apiClient;

  /// `GET /market/breadth` — اتساع السوق.
  Future<MarketBreadthSnapshot> breadth() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/breadth',
      );
      final data = response.data;
      if (data == null) {
        throw const FormatException('Market breadth response is empty.');
      }
      return MarketBreadthSnapshot.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /market/global` — السياق العالمي (مؤشرات/عملات/سلع).
  Future<GlobalMarketSnapshot> global() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/global',
      );
      final data = response.data;
      if (data == null) {
        throw const FormatException('Global market response is empty.');
      }
      return GlobalMarketSnapshot.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /market/status` — حالة السوق (مفتوح/مغلق/الجلسة التالية).
  Future<MarketStatusSnapshot> status() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/status',
      );
      final data = response.data;
      if (data == null) {
        throw const FormatException('Market status response is empty.');
      }
      return MarketStatusSnapshot.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

final marketRepositoryProvider = Provider<MarketRepository>((ref) {
  return MarketRepository(ref.watch(apiClientProvider));
});
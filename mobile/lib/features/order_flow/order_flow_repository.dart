import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'order_flow_models.dart';

class OrderFlowRepository {
  const OrderFlowRepository(this._apiClient);

  final ApiClient _apiClient;

  /// `GET /market/orderbook/{ticker}` — دفتر الأوامر (يتطلب مصادقة).
  Future<OrderBookSnapshot> orderBook(String ticker) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/orderbook/$ticker',
      );
      return OrderBookSnapshot.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /market/trades/{ticker}?limit=N` — آخر الصفقات المنفّذة.
  Future<RecentTradesSnapshot> recentTrades(String ticker, {int limit = 200}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/trades/$ticker',
        queryParameters: <String, dynamic>{'limit': limit},
      );
      return RecentTradesSnapshot.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /market/bulk-trades?ticker=X&value_threshold=Y` — كشف «الحيتان»
  /// من الدوران اليومي (إشارة بديلة موثّقة).
  Future<WhaleDetectionSnapshot> bulkTrades(
    String ticker, {
    double? valueThreshold,
  }) async {
    try {
      final parameters = <String, dynamic>{'ticker': ticker};
      if (valueThreshold != null) {
        parameters['value_threshold'] = valueThreshold;
      }
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/bulk-trades',
        queryParameters: parameters,
      );
      return WhaleDetectionSnapshot.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /market/depth/{ticker}?levels=N` — ملخّص عمق السوق المُجمَّع.
  Future<MarketDepthSnapshot> depth(String ticker, {int levels = 10}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/depth/$ticker',
        queryParameters: <String, dynamic>{'levels': levels},
      );
      return MarketDepthSnapshot.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  /// `GET /market/top-of-book/{ticker}` — أفضل bid/ask لحظي بدون أحجام (WP-27).
  Future<TopOfBookQuote> topOfBook(String ticker) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/market/top-of-book/$ticker',
      );
      return TopOfBookQuote.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Order flow response is empty.');
    }
    return value;
  }
}

final orderFlowRepositoryProvider = Provider<OrderFlowRepository>((ref) {
  return OrderFlowRepository(ref.watch(apiClientProvider));
});

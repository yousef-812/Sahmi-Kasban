import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'stock_flow_models.dart';

class StockFlowRepository {
  const StockFlowRepository(this._apiClient);

  final ApiClient _apiClient;

  /// `GET /stocks/{ticker}/flow?days=N` — ضغط الشراء/البيع من OHLCV (WP-29).
  Future<StockFlowSnapshot> stockFlow(String ticker, {int days = 90}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/stocks/$ticker/flow',
        queryParameters: <String, dynamic>{'days': days},
      );
      final data = response.data;
      if (data == null) {
        throw const FormatException('Stock flow response is empty.');
      }
      return StockFlowSnapshot.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

final stockFlowRepositoryProvider = Provider<StockFlowRepository>((ref) {
  return StockFlowRepository(ref.watch(apiClientProvider));
});

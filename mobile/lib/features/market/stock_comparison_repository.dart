import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import '../../core/network/api_exception.dart';
import 'stock_comparison_models.dart';

class StockComparisonRepository {
  const StockComparisonRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<StockComparisonResult> compare({
    required String requestKey,
    required List<String> tickers,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/market/comparisons',
        data: <String, dynamic>{
          'request_key': requestKey,
          'tickers': tickers,
          'language': 'ar',
        },
      );
      final data = response.data;
      if (data == null) {
        throw const ApiException(message: 'استجابة المقارنة غير صالحة.');
      }
      return StockComparisonResult.fromJson(data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }
}

final stockComparisonRepositoryProvider = Provider<StockComparisonRepository>((
  ref,
) {
  return StockComparisonRepository(ref.watch(apiClientProvider));
});

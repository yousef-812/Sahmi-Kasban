import '../../core/network/api_client.dart';
import 'news_models.dart';

class NewsRepository {
  const NewsRepository(this._apiClient);
  final ApiClient _apiClient;

  Future<List<StockNewsArticle>> getStockNews(
    String ticker, {
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/stocks/${ticker.trim().toUpperCase()}/news',
        queryParameters: {'limit': limit, 'offset': offset},
      );
      return NewsListResponse.fromJson(response.data!).items;
    } on Object catch (e) {
      throw _apiClient.mapError(e);
    }
  }

  Future<List<StockNewsArticle>> getLatestNews({
    int limit = 30,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/news',
        queryParameters: {'limit': limit, 'offset': offset},
      );
      return NewsListResponse.fromJson(response.data!).items;
    } on Object catch (e) {
      throw _apiClient.mapError(e);
    }
  }
}

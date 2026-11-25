import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'sentiment_models.dart';

class SentimentRepository {
  const SentimentRepository(this._apiClient);

  final ApiClient _apiClient;

  /// `GET /stocks/{ticker}/sentiment?days=N` — معنويات أخبار السهم (عامة، بلا مصادقة).
  Future<SymbolSentiment> symbolSentiment(String ticker, {int days = 7}) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/stocks/$ticker/sentiment',
        queryParameters: <String, dynamic>{'days': days},
      );
      return SymbolSentiment.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Sentiment response is empty.');
    }
    return value;
  }
}

final sentimentRepositoryProvider = Provider<SentimentRepository>((ref) {
  return SentimentRepository(ref.watch(apiClientProvider));
});

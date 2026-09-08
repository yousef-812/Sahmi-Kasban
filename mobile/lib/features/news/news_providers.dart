import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'news_models.dart';
import 'news_repository.dart';

final newsRepositoryProvider = Provider<NewsRepository>((ref) {
  return NewsRepository(ref.watch(apiClientProvider));
});

/// أخبار سهم معين
final stockNewsProvider =
    FutureProvider.autoDispose.family<List<StockNewsArticle>, String>((ref, ticker) {
  return ref.watch(newsRepositoryProvider).getStockNews(ticker);
});

/// آخر الأخبار العامة
final latestNewsProvider =
    FutureProvider.autoDispose<List<StockNewsArticle>>((ref) {
  return ref.watch(newsRepositoryProvider).getLatestNews();
});

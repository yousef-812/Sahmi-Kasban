import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'news_models.dart';
import 'news_repository.dart';

final newsRepositoryProvider = Provider<NewsRepository>((ref) {
  return NewsRepository(ref.watch(apiClientProvider));
});

/// المزود الخاص بكلمة البحث في صفحة الأخبار
final newsSearchQueryProvider = StateProvider.autoDispose<String>((ref) => '');

/// أخبار سهم معين
final stockNewsProvider =
    FutureProvider.autoDispose.family<List<StockNewsArticle>, String>((ref, ticker) {
  return ref.watch(newsRepositoryProvider).getStockNews(ticker);
});

/// آخر الأخبار العامة مع البحث
final latestNewsProvider =
    FutureProvider.autoDispose<List<StockNewsArticle>>((ref) {
  final query = ref.watch(newsSearchQueryProvider);
  return ref.watch(newsRepositoryProvider).getLatestNews(query: query);
});

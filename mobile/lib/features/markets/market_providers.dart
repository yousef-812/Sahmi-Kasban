import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'market_models.dart';
import 'market_repository.dart';

/// اتساع السوق (عام).
final marketBreadthProvider = FutureProvider.autoDispose<MarketBreadthSnapshot>((ref) {
  return ref.watch(marketRepositoryProvider).breadth();
});

/// السياق العالمي (مؤشرات/عملات/سلع).
final globalMarketProvider = FutureProvider.autoDispose<GlobalMarketSnapshot>((ref) {
  return ref.watch(marketRepositoryProvider).global();
});

/// حالة السوق (مفتوح/مغلق/الجلسة التالية).
final marketStatusProvider = FutureProvider.autoDispose<MarketStatusSnapshot>((ref) {
  return ref.watch(marketRepositoryProvider).status();
});
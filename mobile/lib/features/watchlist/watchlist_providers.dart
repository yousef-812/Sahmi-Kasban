import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

/// قائمة المتابعة (GET /watchlist).
final watchlistProvider = FutureProvider.autoDispose<WatchlistSnapshot>((ref) {
  return ref.watch(backendRepositoryProvider).getWatchlist();
});

/// إضافة للمتابعة (POST /watchlist).
final addToWatchlistProvider =
    FutureProvider.autoDispose.family<WatchlistSnapshot, String>((ref, ticker) {
      return ref.watch(backendRepositoryProvider).addToWatchlist(ticker);
    });

/// إزالة من المتابعة (DELETE /watchlist/{ticker}).
final removeFromWatchlistProvider =
    FutureProvider.autoDispose.family<WatchlistSnapshot, String>((ref, ticker) {
      return ref.watch(backendRepositoryProvider).removeFromWatchlist(ticker);
    });

/// تحديث إشارة المتابعة (POST /watchlist/refresh/{ticker}).
final refreshWatchlistSignalProvider =
    FutureProvider.autoDispose.family<WatchlistSnapshot, String>((ref, ticker) {
      return ref.watch(backendRepositoryProvider).refreshWatchlistSignal(ticker);
    });
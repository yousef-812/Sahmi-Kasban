import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

/// Real-time live EGX market quotes streamed via WebSocket from backend broadcaster.
final marketQuotesProvider = StreamProvider.autoDispose<MarketQuotesSnapshot>((
  ref,
) {
  final repository = ref.watch(backendRepositoryProvider);
  return repository.streamMarketQuotes();
});

/// Single stock quote used by the stock detail screen.
/// Automatically updates in real-time when the live stream broadcasts changes for this ticker.
class StockQuoteNotifier
    extends AutoDisposeFamilyAsyncNotifier<MarketQuote, String> {
  @override
  Future<MarketQuote> build(String arg) async {
    // 1. Listen to real-time market stream for live updates
    ref.listen<AsyncValue<MarketQuotesSnapshot>>(marketQuotesProvider, (
      _,
      next,
    ) {
      final snapshot = next.valueOrNull;
      if (snapshot != null) {
        final normalizedTicker = arg.trim().toUpperCase();
        for (final item in snapshot.items) {
          if (item.ticker.toUpperCase() == normalizedTicker) {
            state = AsyncValue.data(item);
            break;
          }
        }
      }
    });

    // 2. Check if already present in stream cache
    final currentSnapshot = ref.read(marketQuotesProvider).valueOrNull;
    if (currentSnapshot != null) {
      final normalizedTicker = arg.trim().toUpperCase();
      for (final item in currentSnapshot.items) {
        if (item.ticker.toUpperCase() == normalizedTicker) {
          return item;
        }
      }
    }

    // 3. Fallback to initial server fetch
    return ref.watch(backendRepositoryProvider).getMarketQuote(arg);
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
      () => ref
          .watch(backendRepositoryProvider)
          .getMarketQuote(arg, forceRefresh: true),
    );
  }
}

final stockQuoteProvider =
    AutoDisposeAsyncNotifierProviderFamily<
      StockQuoteNotifier,
      MarketQuote,
      String
    >(StockQuoteNotifier.new);

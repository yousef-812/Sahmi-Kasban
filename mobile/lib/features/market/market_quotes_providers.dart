import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

const marketQuotesPollInterval = Duration(seconds: 5);

/// Live EGX market quotes, refreshed periodically while the home/stock
/// screens are visible using the backend-side cached scanner response.
final marketQuotesProvider =
    StreamProvider.autoDispose<MarketQuotesSnapshot>((ref) {
      final repository = ref.watch(backendRepositoryProvider);
      return Stream.periodic(
        marketQuotesPollInterval,
        (_) => (),
      ).asyncMap(
        (_) => repository.getMarketQuotes(),
      );
    });

/// Single stock quote used by the stock detail screen. Falls back to a
/// one-shot fetch and re-runs when the reference ticker changes.
class StockQuoteNotifier extends AutoDisposeFamilyAsyncNotifier<MarketQuote, String> {
  @override
  Future<MarketQuote> build(String arg) {
    return ref.watch(backendRepositoryProvider).getMarketQuote(arg);
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
      () => ref.watch(backendRepositoryProvider).getMarketQuote(
            arg,
            forceRefresh: true,
          ),
    );
  }
}

final stockQuoteProvider =
    AutoDisposeAsyncNotifierProviderFamily<StockQuoteNotifier, MarketQuote, String>(
      StockQuoteNotifier.new,
    );
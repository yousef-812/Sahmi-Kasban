import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models.dart';
import 'watchlist_repository.dart';

/// Provider لقائمة المراقبة الكاملة.
final watchlistProvider =
    AsyncNotifierProvider<WatchlistNotifier, WatchlistResponse>(
      WatchlistNotifier.new,
    );

/// Notifier لإدارة حالة قائمة المراقبة.
class WatchlistNotifier extends AsyncNotifier<WatchlistResponse> {
  late final WatchlistRepository _repo = ref.read(watchlistRepositoryProvider);

  @override
  Future<WatchlistResponse> build() async {
    return _repo.list();
  }

  Future<void> add(String ticker) async {
    try {
      await _repo.add(ticker);
      ref.invalidateSelf();
    } catch (e, st) {
      state = AsyncError(e, st);
      rethrow;
    }
  }

  Future<void> remove(String ticker) async {
    try {
      await _repo.remove(ticker);
      ref.invalidateSelf();
    } catch (e, st) {
      state = AsyncError(e, st);
      rethrow;
    }
  }

  Future<void> refreshSignal(String ticker) async {
    final current = state.value;
    if (current == null) return;

    try {
      final updated = await _repo.refreshSignal(ticker);
      final updatedItems = current.items.map((item) {
        return item.ticker == ticker ? updated : item;
      }).toList();
      state = AsyncData(
        WatchlistResponse(
          items: updatedItems,
          count: current.count,
          maxItems: current.maxItems,
        ),
      );
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }

  Future<void> refreshAll() async {
    final current = state.value;
    if (current == null) return;

    for (final item in current.items) {
      await refreshSignal(item.ticker);
    }
  }
}

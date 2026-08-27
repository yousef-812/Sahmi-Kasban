import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../domain/models.dart';

/// Repository للتعامل مع Watchlist API.
class WatchlistRepository {
  WatchlistRepository(this._api);

  final ApiClient _api;

  Future<WatchlistResponse> list() async {
    final response = await _api.get('/watchlist');
    return WatchlistResponse.fromJson(response);
  }

  Future<WatchlistItem> add(String ticker) async {
    final response = await _api.post('/watchlist', body: {'ticker': ticker});
    return WatchlistItem.fromJson(response);
  }

  Future<WatchlistResponse> bulkAdd(List<String> tickers) async {
    final response = await _api.post(
      '/watchlist/bulk',
      body: {'tickers': tickers},
    );
    return WatchlistResponse.fromJson(response);
  }

  Future<void> remove(String ticker) async {
    await _api.delete('/watchlist/$ticker');
  }

  Future<WatchlistItem> refreshSignal(String ticker) async {
    final response = await _api.post('/watchlist/$ticker/refresh');
    return WatchlistItem.fromJson(response);
  }
}

/// Provider للـ Repository.
final watchlistRepositoryProvider = Provider<WatchlistRepository>((ref) {
  final api = ref.watch(apiClientProvider);
  return WatchlistRepository(api);
});

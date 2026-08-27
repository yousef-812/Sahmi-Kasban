import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../domain/models.dart';

/// Repository للتعامل مع Watchlist API.
class WatchlistRepository {
  WatchlistRepository(this._api);

  final ApiClient _api;

  Future<WatchlistResponse> list() async {
    try {
      final response = await _api.dio.get<Map<String, dynamic>>('/watchlist');
      return WatchlistResponse.fromJson(response.data ?? <String, dynamic>{});
    } on Object catch (e) {
      throw _api.mapError(e);
    }
  }

  Future<WatchlistItem> add(String ticker) async {
    try {
      final response = await _api.dio.post<Map<String, dynamic>>(
        '/watchlist',
        data: {'ticker': ticker},
      );
      return WatchlistItem.fromJson(response.data ?? <String, dynamic>{});
    } on Object catch (e) {
      throw _api.mapError(e);
    }
  }

  Future<WatchlistResponse> bulkAdd(List<String> tickers) async {
    try {
      final response = await _api.dio.post<Map<String, dynamic>>(
        '/watchlist/bulk',
        data: {'tickers': tickers},
      );
      return WatchlistResponse.fromJson(response.data ?? <String, dynamic>{});
    } on Object catch (e) {
      throw _api.mapError(e);
    }
  }

  Future<void> remove(String ticker) async {
    try {
      await _api.dio.delete<void>('/watchlist/$ticker');
    } on Object catch (e) {
      throw _api.mapError(e);
    }
  }

  Future<WatchlistItem> refreshSignal(String ticker) async {
    try {
      final response = await _api.dio.post<Map<String, dynamic>>(
        '/watchlist/$ticker/refresh',
      );
      return WatchlistItem.fromJson(response.data ?? <String, dynamic>{});
    } on Object catch (e) {
      throw _api.mapError(e);
    }
  }
}

/// Provider للـ Repository.
final watchlistRepositoryProvider = Provider<WatchlistRepository>((ref) {
  final api = ref.watch(apiClientProvider);
  return WatchlistRepository(api);
});

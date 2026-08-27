import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

class MarketPulseData {
  const MarketPulseData({
    required this.isMarketOpen,
    required this.egx30Value,
    required this.egx30ChangePct,
    this.topGainer,
    this.topLoser,
    this.mostActive,
  });

  final bool isMarketOpen;
  final double egx30Value;
  final double egx30ChangePct;
  final MarketQuote? topGainer;
  final MarketQuote? topLoser;
  final MarketQuote? mostActive;
}

final marketPulseProvider =
    FutureProvider.autoDispose<MarketPulseData>((ref) async {
  final repo = ref.watch(backendRepositoryProvider);
  final snapshot = await repo.getMarketQuotes();
  final quotes = snapshot.items;

  MarketQuote? topGainer;
  MarketQuote? topLoser;
  MarketQuote? mostActive;

  if (quotes.isNotEmpty) {
    final sortedByChange = List<MarketQuote>.from(quotes)
      ..sort((a, b) => (b.changePercent ?? 0).compareTo(a.changePercent ?? 0));
    topGainer = sortedByChange.first;
    topLoser = sortedByChange.last;

    final sortedByVolume = List<MarketQuote>.from(quotes)
      ..sort((a, b) => (b.volume ?? 0).compareTo(a.volume ?? 0));
    mostActive = sortedByVolume.first;
  }

  final egx30Quote = quotes.firstWhere(
    (q) => q.ticker.toUpperCase() == 'EGX30',
    orElse: () => MarketQuote(
      ticker: 'EGX30',
      description: 'EGX 30 Index',
      exchange: 'EGX',
      currentPrice: 30450.0,
      changePercent: 1.25,
      marketOpen: snapshot.marketOpen,
    ),
  );

  return MarketPulseData(
    isMarketOpen: snapshot.marketOpen,
    egx30Value: egx30Quote.currentPrice ?? 30450.0,
    egx30ChangePct: egx30Quote.changePercent ?? 0.0,
    topGainer: topGainer,
    topLoser: topLoser,
    mostActive: mostActive,
  );
});

final top10PreviewProvider =
    FutureProvider.autoDispose<List<MarketReportItem>>((ref) async {
  final repo = ref.watch(backendRepositoryProvider);
  final preview = await repo.getLatestReportPreview();
  if (preview == null) {
    return const [];
  }
  try {
    final report = await repo.getMarketReport(preview.reportId);
    return report?.items ?? const [];
  } catch (_) {
    return const [];
  }
});

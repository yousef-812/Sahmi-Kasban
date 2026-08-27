import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme.dart';
import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'market_quotes_providers.dart';
import 'stock_quote_card.dart';

class StocksScreen extends ConsumerStatefulWidget {
  const StocksScreen({super.key});

  @override
  ConsumerState<StocksScreen> createState() => _StocksScreenState();
}

class _StocksScreenState extends ConsumerState<StocksScreen> {
  String _query = '';
  bool _showFallers = false;
  bool _showOnlyActive = false;

  @override
  Widget build(BuildContext context) {
    final snapshot = ref.watch(marketQuotesProvider).valueOrNull;
    final items = _visibleItems(snapshot);

    final header = snapshot == null
        ? null
        : QuoteSessionHeader(snapshot: snapshot);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(marketQuotesProvider);
        await ref.read(marketQuotesProvider.future);
      },
      child: Column(
        children: [
          if (header != null) header,
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
            child: TextField(
              textDirection: TextDirection.ltr,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search_rounded),
                hintText: 'بحث برمز السهم أو الاسم — COMI',
                isDense: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(14)),
                ),
              ),
              onChanged: (value) =>
                  setState(() => _query = value.trim().toUpperCase()),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
            child: Wrap(
              spacing: 8,
              runSpacing: 4,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                FilterChip(
                  label: const Text('الأكثر هبوطًا'),
                  selected: _showFallers,
                  onSelected: (value) => setState(() => _showFallers = value),
                ),
                FilterChip(
                  label: const Text('المتداولة فقط'),
                  selected: _showOnlyActive,
                  onSelected: (value) =>
                      setState(() => _showOnlyActive = value),
                ),
              ],
            ),
          ),
          Expanded(
            child: ref
                .watch(marketQuotesProvider)
                .when(
                  loading: () =>
                      const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => _ErrorView(
                    error: error,
                    onRetry: () => ref.invalidate(marketQuotesProvider),
                  ),
                  data: (_) => _buildGrid(context, items),
                ),
          ),
        ],
      ),
    );
  }

  List<MarketQuote> _visibleItems(MarketQuotesSnapshot? snapshot) {
    if (snapshot == null) {
      return const [];
    }
    final items = snapshot.items
        .where((quote) {
          if (_query.isNotEmpty) {
            final match =
                quote.ticker.contains(_query) ||
                quote.description.contains(_query);
            if (!match) {
              return false;
            }
          }
          if (_showOnlyActive && quote.currentPrice == null) {
            return false;
          }
          return true;
        })
        .toList(growable: false);

    items.sort((a, b) {
      if (_showFallers) {
        final aChange = a.changePercent ?? 0;
        final bChange = b.changePercent ?? 0;
        return aChange.compareTo(bChange);
      }
      return a.ticker.compareTo(b.ticker);
    });
    return items;
  }

  Widget _buildGrid(BuildContext context, List<MarketQuote> items) {
    if (items.isEmpty) {
      return ListView(
        padding: const EdgeInsets.all(24),
        children: const [
          Icon(Icons.search_off_rounded, size: 48),
          SizedBox(height: 12),
          Text(
            'لا توجد أسهم مطابقة للبحث الحالي.',
            textAlign: TextAlign.center,
          ),
        ],
      );
    }
    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 220,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.92,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final quote = items[index];
        return StockQuoteCard(
          quote: quote,
          onTap: () => context.push('/stocks/${quote.ticker}'),
        );
      },
    );
  }
}

class QuoteSessionHeader extends StatelessWidget {
  const QuoteSessionHeader({super.key, required this.snapshot});

  final MarketQuotesSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final open = snapshot.marketOpen;
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: open
              ? [
                  Theme.of(context).colorScheme.primaryContainer,
                  Theme.of(context).colorScheme.primary.withValues(alpha: 0.4),
                ]
              : [
                  Theme.of(context).colorScheme.surfaceContainerHigh,
                  Theme.of(context).colorScheme.surfaceContainerLow,
                ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(
            open
                ? Icons.show_chart_rounded
                : Icons.pause_circle_outline_rounded,
            size: 34,
            color: open
                ? SahmiBrand.neonBull
                : Theme.of(context).colorScheme.onSurface,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  open ? 'السوق مفتوح الآن' : 'السوق مغلق',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  _subtitle(context, open),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          if (snapshot.items.isNotEmpty)
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${snapshot.items.length} سهم',
                  style: Theme.of(
                    context,
                  ).textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 2),
                Text(
                  'تحديث كل ${marketQuotesPollInterval.inSeconds} ث',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  String _subtitle(BuildContext context, bool open) {
    final next = snapshot.nextSessionOpen;
    if (next == null) {
      return open ? 'التداول جارٍ' : 'سيُفتح السوق قريبًا';
    }
    if (open) {
      final now = DateTime.now();
      final diff = next.difference(now);
      if (diff.isNegative) {
        return 'سيغلق السوق في نهاية الجلسة.';
      }
      final minutes = diff.inMinutes.remainder(60);
      final hours = diff.inHours;
      return 'باقي على إغلاق السوق '
          '${hours > 0 ? '$hours س ' : ''}$minutes د';
    }
    return 'باقي على فتح السوق '
        '${_untilOpen(next)}';
  }

  String _untilOpen(DateTime next) {
    final now = DateTime.now();
    final diff = next.difference(now);
    if (diff.isNegative) {
      return 'قريبًا';
    }
    final minutes = diff.inMinutes.remainder(60);
    final hours = diff.inHours;
    return '${hours > 0 ? '$hours س ' : ''}$minutes د';
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 48),
            const SizedBox(height: 12),
            Text(
              error is ApiException
                  ? (error as ApiException).message
                  : 'تعذر تحميل أسعار السوق.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

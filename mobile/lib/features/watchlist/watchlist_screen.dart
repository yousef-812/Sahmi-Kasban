import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'watchlist_providers.dart';

/// شاشة قائمة المتابعة — تعرض العناصر من `GET /watchlist` مع خيارات
/// إضافة/حذف/تحديث الإشارة + فتح صفحة السهم (WP-34).
class WatchlistScreen extends ConsumerStatefulWidget {
  const WatchlistScreen({super.key});

  static const routeName = '/watchlist';

  @override
  ConsumerState<WatchlistScreen> createState() => _WatchlistScreenState();
}

class _WatchlistScreenState extends ConsumerState<WatchlistScreen> {
  final TextEditingController _tickerController = TextEditingController();

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(watchlistProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('قائمة المتابعة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(watchlistProvider),
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => _ErrorView(
          error: error,
          onRetry: () => ref.invalidate(watchlistProvider),
        ),
        data: (snapshot) {
          if (snapshot.items.isEmpty) {
            return _EmptyWatchlist(
              onAdd: _showAddTickerDialog,
              maxItems: snapshot.maxItems,
            );
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(watchlistProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: snapshot.items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (_, index) =>
                  _WatchlistTile(item: snapshot.items[index]),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddTickerDialog,
        icon: const Icon(Icons.add_rounded),
        label: const Text('إضافة'),
      ),
    );
  }

  void _showAddTickerDialog() {
    _tickerController.clear();
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('إضافة لقائمة المتابعة'),
        content: TextField(
          controller: _tickerController,
          decoration: const InputDecoration(
            labelText: 'رمز السهم (مثال: COMI)',
            hintText: 'COMI',
          ),
          textCapitalization: TextCapitalization.characters,
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () {
              final ticker = _tickerController.text.trim().toUpperCase();
              if (ticker.isEmpty) return;
              Navigator.pop(dialogContext);
              _addTicker(ticker);
            },
            child: const Text('إضافة'),
          ),
        ],
      ),
    );
  }

  Future<void> _addTicker(String ticker) async {
    final result = await ref.read(addToWatchlistProvider(ticker).future);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            result.items.any((i) => i.ticker == ticker)
                ? 'تمت إضافة $ticker'
                : 'فشل إضافة $ticker',
          ),
        ),
      );
      ref.invalidate(watchlistProvider);
    }
  }
}

class _WatchlistTile extends ConsumerWidget {
  const _WatchlistTile({required this.item});

  final WatchlistItem item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final changeColor = item.lastChangePct == null
        ? muted
        : item.lastChangePct! > 0
            ? Colors.green.shade700
            : theme.colorScheme.error;

    return Dismissible(
      key: ValueKey(item.ticker),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        color: theme.colorScheme.error,
        child: const Icon(Icons.delete_rounded, color: Colors.white),
      ),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => _deleteTicker(context, ref, item.ticker),
      child: Card(
        child: InkWell(
          onTap: () => context.push('/market/analyze/${item.ticker}'),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.ticker,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Wrap(
                        spacing: 12,
                        runSpacing: 2,
                        children: [
                          if (item.lastSignal != null)
                            _SignalChip(label: item.lastSignal!),
                          if (item.lastScore != null)
                            _InfoChip(
                                label: 'تقييم',
                                value: item.lastScore!.toStringAsFixed(0)),
                          if (item.lastPrice != null)
                            _InfoChip(
                                label: 'سعر',
                                value: item.lastPrice!.toStringAsFixed(2)),
                          if (item.lastChangePct != null)
                            _InfoChip(
                              label: 'تغير',
                              value:
                                  '${item.lastChangePct! > 0 ? '+' : ''}${item.lastChangePct!.toStringAsFixed(2)}%',
                              color: changeColor,
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                PopupMenuButton<String>(
                  onSelected: (value) {
                    switch (value) {
                      case 'refresh':
                        _refreshSignal(context, ref, item.ticker);
                        break;
                      case 'delete':
                        _deleteTicker(context, ref, item.ticker);
                        break;
                      case 'details':
                        context.push('/market/analyze/${item.ticker}');
                        break;
                    }
                  },
                  itemBuilder: (_) => [
                    const PopupMenuItem(
                      value: 'details',
                      child: ListTile(
                        leading: Icon(Icons.open_in_new_rounded),
                        title: Text('فتح صفحة السهم'),
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'refresh',
                      child: ListTile(
                        leading: Icon(Icons.refresh_rounded),
                        title: Text('تحديث الإشارة'),
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'delete',
                      child: ListTile(
                        leading: Icon(Icons.delete_rounded, color: Colors.red),
                        title: Text('حذف من المتابعة'),
                      ),
                    ),
                  ],
                  icon: Icon(Icons.more_vert_rounded, color: muted),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _refreshSignal(BuildContext context, WidgetRef ref, String ticker) async {
    await ref.read(refreshWatchlistSignalProvider(ticker).future);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('تم تحديث إشارة $ticker')),
      );
      ref.invalidate(watchlistProvider);
    }
  }

  Future<void> _deleteTicker(BuildContext context, WidgetRef ref, String ticker) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('حذف من المتابعة'),
        content: Text('هل تريد حذف $ticker من قائمة المتابعة؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ref.read(removeFromWatchlistProvider(ticker).future);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تم حذف $ticker')),
        );
        ref.invalidate(watchlistProvider);
      }
    }
  }
}

class _SignalChip extends StatelessWidget {
  const _SignalChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = switch (label) {
      'buy' => Colors.green.shade700,
      'sell' => theme.colorScheme.error,
      _ => theme.colorScheme.onSurfaceVariant,
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: theme.textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.label, required this.value, this.color});

  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label: ',
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: theme.textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.w700,
            color: color,
          ),
        ),
      ],
    );
  }
}

class _EmptyWatchlist extends StatelessWidget {
  const _EmptyWatchlist({
    required this.onAdd,
    required this.maxItems,
  });

  final VoidCallback onAdd;
  final int maxItems;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.bookmark_border_rounded, size: 64, color: muted),
            const SizedBox(height: 16),
            Text(
              'قائمة المتابعة فارغة',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 8),
            Text(
              'أضف أسهمًا لمتابعتها وتلقي إشاراتها',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(color: muted),
            ),
            const SizedBox(height: 4),
            Text(
              'الحد الأقصى: $maxItems سهم',
              style: theme.textTheme.labelSmall?.copyWith(color: muted),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add_rounded),
              label: const Text('إضافة سهم'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: 12),
            Text(
              error is ApiException
                  ? (error as ApiException).message
                  : 'تعذر تحميل قائمة المتابعة.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
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
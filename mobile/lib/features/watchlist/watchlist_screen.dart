import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/terminal_theme.dart';
import '../../core/widgets/terminal_skeleton.dart';
import '../../domain/models.dart';
import 'watchlist_providers.dart';

/// شاشة قائمة المراقبة — قلب محطة التداول.
/// تعرض الإشارات الحية مع ألوان نيون وأرقام mono.
class WatchlistScreen extends ConsumerWidget {
  const WatchlistScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = TerminalTheme.of(context);
    final watchlistAsync = ref.watch(watchlistProvider);

    return Scaffold(
      backgroundColor: theme.bgBase,
      appBar: AppBar(
        backgroundColor: theme.bgBase,
        elevation: 0,
        leading: const SizedBox.shrink(),
        title: Row(
          children: [
            Icon(Icons.visibility_rounded, color: theme.signalGold, size: 24),
            const SizedBox(width: 10),
            Text(
              'قائمة المراقبة',
              style: theme.titleSmall.copyWith(
                color: theme.textPrimary,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () => _showAddDialog(context, ref),
            icon: Icon(Icons.add_rounded, color: theme.signalGold),
            tooltip: 'إضافة سهم',
          ),
        ],
      ),
      body: watchlistAsync.when(
        data: (response) => response.items.isEmpty
            ? _EmptyState(
                theme: theme,
                onAdd: () => _showAddDialog(context, ref),
              )
            : RefreshIndicator(
                color: theme.signalGold,
                onRefresh: () async {
                  await ref.read(watchlistProvider.notifier).refreshAll();
                },
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  itemCount: response.items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = response.items[index];
                    return _WatchlistTile(
                      item: item,
                      rank: index + 1,
                      onTap: () => context.push('/stocks/${item.ticker}'),
                      onRefresh: () => ref
                          .read(watchlistProvider.notifier)
                          .refreshSignal(item.ticker),
                      onRemove: () => ref
                          .read(watchlistProvider.notifier)
                          .remove(item.ticker),
                    );
                  },
                ),
              ),
        loading: () => const Padding(
          padding: EdgeInsets.all(16),
          child: WatchlistSkeleton(),
        ),
        error: (e, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline, color: theme.bearRed, size: 48),
              const SizedBox(height: 12),
              Text(
                'تعذر تحميل القائمة',
                style: theme.monoMedium.copyWith(color: theme.textPrimary),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => ref.invalidate(watchlistProvider),
                child: Text(
                  'إعادة المحاولة',
                  style: TextStyle(color: theme.signalGold),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showAddDialog(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (context) => const _AddToWatchlistDialog(),
    );
  }
}

/// بلاطة عنصر في قائمة المراقبة.
class _WatchlistTile extends StatelessWidget {
  const _WatchlistTile({
    required this.item,
    required this.rank,
    required this.onTap,
    required this.onRefresh,
    required this.onRemove,
  });

  final WatchlistItem item;
  final int rank;
  final VoidCallback onTap;
  final Future<void> Function() onRefresh;
  final Future<void> Function() onRemove;

  @override
  Widget build(BuildContext context) {
    final theme = TerminalTheme.of(context);
    final signal = item.lastSignal ?? '—';
    final (signalColor, signalBg) = _signalColors(signal, theme);

    return Dismissible(
      key: ValueKey(item.ticker),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        decoration: BoxDecoration(
          color: theme.bearRed.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(Icons.delete_outline, color: theme.bearRed, size: 24),
      ),
      confirmDismiss: (_) async {
        await onRemove();
        return false;
      },
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: theme.bgSurface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: theme.border),
          ),
          child: Row(
            children: [
              SizedBox(
                width: 28,
                child: Text(
                  '#$rank',
                  style: theme.monoSmall.copyWith(
                    color: theme.textSecondary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.ticker,
                      style: theme.monoMedium.copyWith(
                        color: theme.textPrimary,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    if (item.lastCheckedAt != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        _formatTimeAgo(item.lastCheckedAt!),
                        style: theme.monoTiny.copyWith(
                          color: theme.textTertiary,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (item.lastPrice != null) ...[
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      item.lastPrice!.toStringAsFixed(2),
                      style: theme.monoMedium.copyWith(
                        color: theme.textPrimary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    if (item.lastChangePct != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        '${item.lastChangePct! >= 0 ? '+' : ''}${item.lastChangePct!.toStringAsFixed(2)}%',
                        style: theme.monoTiny.copyWith(
                          color: item.lastChangePct! >= 0
                              ? theme.bullGreen
                              : theme.bearRed,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(width: 12),
              ],
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: signalBg,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: signalColor.withValues(alpha: 0.4)),
                ),
                child: Text(
                  _signalLabel(signal),
                  style: theme.monoTiny.copyWith(
                    color: signalColor,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.5,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                onPressed: onRefresh,
                icon: Icon(
                  Icons.refresh_rounded,
                  color: theme.textSecondary,
                  size: 20,
                ),
                tooltip: 'تحديث الإشارة',
                visualDensity: VisualDensity.compact,
              ),
            ],
          ),
        ),
      ),
    );
  }

  (Color, Color) _signalColors(String signal, TerminalThemeData theme) {
    return switch (signal.toUpperCase()) {
      'BUY' => (theme.bullGreen, theme.bullGreen.withValues(alpha: 0.12)),
      'AVOID' => (theme.bearRed, theme.bearRed.withValues(alpha: 0.12)),
      _ => (theme.textSecondary, theme.bgElevated),
    };
  }

  String _signalLabel(String signal) {
    return switch (signal.toUpperCase()) {
      'BUY' => 'شراء',
      'AVOID' => 'تجنب',
      _ => 'مراقبة',
    };
  }

  String _formatTimeAgo(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 1) return 'الآن';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} د';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} س';
    return 'منذ ${diff.inDays} ي';
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.theme, required this.onAdd});
  final TerminalThemeData theme;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.visibility_off_rounded,
              color: theme.textTertiary,
              size: 64,
            ),
            const SizedBox(height: 20),
            Text(
              'قائمة المراقبة فارغة',
              style: theme.monoLarge.copyWith(
                color: theme.textPrimary,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'أضف أسهمًا لمتابعتها لحظيًا\nمع إشارات BUY/WATCH/AVOID حية',
              textAlign: TextAlign.center,
              style: theme.monoSmall.copyWith(
                color: theme.textSecondary,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add_rounded),
              label: const Text('أضف أول سهم'),
              style: FilledButton.styleFrom(
                backgroundColor: theme.signalGold,
                foregroundColor: theme.bgBase,
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AddToWatchlistDialog extends ConsumerStatefulWidget {
  const _AddToWatchlistDialog();

  @override
  ConsumerState<_AddToWatchlistDialog> createState() =>
      _AddToWatchlistDialogState();
}

class _AddToWatchlistDialogState extends ConsumerState<_AddToWatchlistDialog> {
  final _controller = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final ticker = _controller.text.trim().toUpperCase();
    if (ticker.isEmpty) {
      setState(() => _error = 'أدخل رمز السهم');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      await ref.read(watchlistProvider.notifier).add(ticker);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      setState(() {
        _error = e.toString().contains('already')
            ? 'السهم موجود بالفعل في القائمة'
            : 'تعذر إضافة السهم';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = TerminalTheme.of(context);
    return AlertDialog(
      backgroundColor: theme.bgSurface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      title: Text(
        'إضافة سهم للمراقبة',
        style: theme.titleSmall.copyWith(color: theme.textPrimary),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _controller,
            textCapitalization: TextCapitalization.characters,
            style: theme.monoMedium.copyWith(color: theme.textPrimary),
            decoration: InputDecoration(
              hintText: 'COMI',
              hintStyle: theme.monoMedium.copyWith(color: theme.textTertiary),
              filled: true,
              fillColor: theme.bgBase,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: theme.border),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: theme.border),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: theme.signalGold, width: 2),
              ),
              errorText: _error,
            ),
            onSubmitted: (_) => _submit(),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: _loading ? null : () => Navigator.of(context).pop(),
          child: Text('إلغاء', style: TextStyle(color: theme.textSecondary)),
        ),
        FilledButton(
          onPressed: _loading ? null : _submit,
          style: FilledButton.styleFrom(
            backgroundColor: theme.signalGold,
            foregroundColor: theme.bgBase,
          ),
          child: _loading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('إضافة'),
        ),
      ],
    );
  }
}

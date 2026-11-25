import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import 'signals_models.dart';
import 'signals_providers.dart';
import 'signals_screen.dart' show signalStateColor, signalStateLabels;

/// بطاقة إشارات السهم داخل صفحته (WP-32) — تعرض إشارات الرمز من
/// `GET /signals?ticker=` (حالة/دخول/وقف/أهداف/P&L) + زر يفتح شاشة الإشارات.
class StockSignalsCard extends ConsumerWidget {
  const StockSignalsCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final filter = SignalsFilter(ticker: ticker);
    final state = ref.watch(signalsListProvider(filter));
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.notifications_active_rounded,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'إشارات السهم',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => context.push('/signals'),
                  child: const Text('الكل'),
                ),
              ],
            ),
            const SizedBox(height: 4),
            state.when(
              loading: () => const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Center(
                  child: SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.5),
                  ),
                ),
              ),
              error: (error, stackTrace) => _SignalsError(
                error: error,
                onRetry: () => ref.invalidate(signalsListProvider(filter)),
              ),
              data: (page) {
                if (page.items.isEmpty) {
                  return _Note(
                    message: 'لا توجد إشارات لهذا السهم حاليًا.',
                  );
                }
                final signals = [...page.items]
                  ..sort((a, b) => b.openedAt.compareTo(a.openedAt));
                return Column(
                  children: [
                    for (final signal in signals.take(3)) ...[
                      _SignalRow(signal: signal),
                      if (signal != signals.last) const Divider(height: 12),
                    ],
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _SignalRow extends StatelessWidget {
  const _SignalRow({required this.signal});

  final Signal signal;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final directionColor = signal.isLong
        ? Colors.green.shade700
        : theme.colorScheme.error;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: directionColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: directionColor.withValues(alpha: 0.35)),
              ),
              child: Text(
                signal.isLong ? 'شراء' : 'بيع',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: directionColor,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            const SizedBox(width: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: signalStateColor(signal.state).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                signalStateLabels[signal.state] ?? signal.state,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: signalStateColor(signal.state),
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            const Spacer(),
            if (signal.pnlPct != null)
              Text(
                '${signal.pnlPct! > 0 ? '+' : ''}${signal.pnlPct!.toStringAsFixed(1)}%',
                textDirection: TextDirection.ltr,
                style: theme.textTheme.labelMedium?.copyWith(
                  color: signal.pnlPct! > 0
                      ? Colors.green.shade700
                      : signal.pnlPct! < 0
                          ? theme.colorScheme.error
                          : muted,
                  fontWeight: FontWeight.w800,
                ),
              ),
          ],
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 12,
          runSpacing: 2,
          children: [
            _Level(label: 'دخول', value: signal.entry),
            _Level(label: 'وقف', value: signal.stop),
            _Level(label: 'هدف 1', value: signal.t1),
            if (signal.t2 != null) _Level(label: 'هدف 2', value: signal.t2!),
            if (signal.t3 != null) _Level(label: 'هدف 3', value: signal.t3!),
          ],
        ),
      ],
    );
  }
}

class _Level extends StatelessWidget {
  const _Level({required this.label, required this.value});

  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(color: muted),
        ),
        const SizedBox(width: 3),
        Text(
          value.toStringAsFixed(2),
          textDirection: TextDirection.ltr,
          style: theme.textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

class _SignalsError extends StatelessWidget {
  const _SignalsError({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 18,
              color: theme.colorScheme.error,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                error is ApiException
                    ? (error as ApiException).message
                    : 'تعذر تحميل إشارات السهم.',
                style: theme.textTheme.bodySmall,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        OutlinedButton.icon(
          onPressed: onRetry,
          icon: const Icon(Icons.refresh_rounded, size: 16),
          label: const Text('إعادة المحاولة'),
          style: OutlinedButton.styleFrom(visualDensity: VisualDensity.compact),
        ),
      ],
    );
  }
}

class _Note extends StatelessWidget {
  const _Note({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: muted.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.info_outline_rounded, size: 18, color: muted),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: theme.textTheme.bodySmall?.copyWith(color: muted),
            ),
          ),
        ],
      ),
    );
  }
}

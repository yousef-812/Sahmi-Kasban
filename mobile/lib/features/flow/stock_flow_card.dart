import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'stock_flow_models.dart';
import 'stock_flow_providers.dart';

/// بطاقة ضغط الشراء/البيع من OHLCV (CLV×الحجم) — WP-29.
///
/// تقدير للضغط بين المشترين/البائعين من الشموم، **لا أوامر فعلية**
/// (لا يوجد دفتر عمق مجاني لـ EGX). تُظهر حكم التراكم/التوزيع وحصة كل طرف
/// ومؤشرات MFI/OBV/A-D.
class StockFlowCard extends ConsumerWidget {
  const StockFlowCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(stockFlowProvider(ticker));
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
                  Icons.swap_vert_circle_rounded,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  'ضغط الشراء والبيع',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              'محسوب من شموم OHLCV (CLV×الحجم) — تقدير لا أوامر فعلية.',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 10),
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
              error: (error, stackTrace) => _FlowError(
                error: error,
                onRetry: () => ref.invalidate(stockFlowProvider(ticker)),
              ),
              data: (snapshot) => _FlowData(snapshot: snapshot),
            ),
          ],
        ),
      ),
    );
  }
}

class _FlowData extends StatelessWidget {
  const _FlowData({required this.snapshot});

  final StockFlowSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (!snapshot.available ||
        snapshot.buySharePct == null ||
        snapshot.sellSharePct == null) {
      return _FlowNote(
        message: snapshot.reason ?? 'بيانات ضغط الشراء/البيع غير متاحة حاليًا.',
      );
    }
    final buyShare = snapshot.buySharePct!;
    final sellShare = snapshot.sellSharePct!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _VerdictBadge(verdict: snapshot.verdict),
            const Spacer(),
            Text(
              'نافذة ${snapshot.windowDays} جلسة',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Text(
              'شراء ${buyShare.toStringAsFixed(1)}%',
              style: theme.textTheme.labelMedium?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: Row(
                  children: [
                    Expanded(
                      flex: buyShare.round().clamp(1, 99),
                      child: Container(
                        height: 10,
                        color: theme.colorScheme.primary.withValues(alpha: 0.75),
                      ),
                    ),
                    Expanded(
                      flex: sellShare.round().clamp(1, 99),
                      child: Container(
                        height: 10,
                        color: theme.colorScheme.error.withValues(alpha: 0.75),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${sellShare.toStringAsFixed(1)}% بيع',
              style: theme.textTheme.labelMedium?.copyWith(
                color: theme.colorScheme.error,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 14,
          runSpacing: 4,
          children: [
            _MetricChip(
              label: 'MFI(14)',
              value: snapshot.mfi14?.toStringAsFixed(1) ?? '-',
            ),
            _MetricChip(
              label: 'اتجاه A/D',
              value: _trendLabel(snapshot.adTrend),
            ),
            _MetricChip(
              label: 'اتجاه OBV',
              value: _trendLabel(snapshot.obvTrend),
            ),
            if (snapshot.netVolume != null)
              _MetricChip(
                label: 'صافي الحجم',
                value: _formatVolume(snapshot.netVolume!),
              ),
          ],
        ),
      ],
    );
  }

  String _trendLabel(int trend) {
    if (trend > 0) return 'تراكم';
    if (trend < 0) return 'توزيع';
    return 'محايد';
  }

  String _formatVolume(double value) {
    final sign = value < 0 ? '-' : '';
    final magnitude = value.abs();
    if (magnitude >= 1_000_000) {
      return '$sign${(magnitude / 1_000_000).toStringAsFixed(2)} م';
    }
    if (magnitude >= 1_000) {
      return '$sign${(magnitude / 1_000).toStringAsFixed(1)} أ';
    }
    return '$sign${magnitude.toStringAsFixed(0)}';
  }
}

class _VerdictBadge extends StatelessWidget {
  const _VerdictBadge({required this.verdict});

  final String verdict;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (label, color) = switch (verdict) {
      'accumulate' => ('تراكم', theme.colorScheme.primary),
      'distribute' => ('توزيع', theme.colorScheme.error),
      _ => ('محيد', theme.colorScheme.onSurfaceVariant),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Text(
        label,
        style: theme.textTheme.labelMedium?.copyWith(
          color: color,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

class _FlowError extends StatelessWidget {
  const _FlowError({required this.error, required this.onRetry});

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
                    : 'تعذر تحميل ضغط الشراء/البيع.',
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

class _FlowNote extends StatelessWidget {
  const _FlowNote({required this.message});

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

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'order_flow_models.dart';
import 'order_flow_providers.dart';

/// بطاقة أفضل سعر bid/ask لحظي (بدون أحجام) — WP-27.
///
/// تُغذّى من اشتراك TradingView WS عبر `GET /market/top-of-book/{ticker}`؛
/// تعرض أفضل سعرَي شراء/بيع مع انتشار السعر (spread) ونقطة المنتصف.
/// عند غياب bid/ask تعرض حالة «غير متاح» صادقة بدل أصفار مختلقة.
class TopOfBookCard extends ConsumerWidget {
  const TopOfBookCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(topOfBookProvider(ticker));
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
                  Icons.currency_exchange_rounded,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  'أفضل سعر (bid/ask)',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              'أفضل سعرَي شراء/بيع لحظي بدون أحجام — من اشتراك TradingView WS.',
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
              error: (error, stackTrace) => _TopOfBookError(
                error: error,
                onRetry: () => ref.invalidate(topOfBookProvider(ticker)),
              ),
              data: (quote) => _TopOfBookData(quote: quote),
            ),
          ],
        ),
      ),
    );
  }
}

class _TopOfBookData extends StatelessWidget {
  const _TopOfBookData({required this.quote});

  final TopOfBookQuote quote;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (!quote.available || quote.bid == null || quote.ask == null) {
      return _TopOfBookNote(
        message: quote.reason ?? 'بيانات bid/ask غير متاحة حاليًا من المصدر.',
      );
    }
    final muted = theme.colorScheme.onSurfaceVariant;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: _SideBox(
                label: 'شراء (Bid)',
                value: quote.bid!,
                color: theme.colorScheme.primary,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _SideBox(
                label: 'بيع (Ask)',
                value: quote.ask!,
                color: theme.colorScheme.error,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 14,
          runSpacing: 4,
          children: [
            _MetricChip(
              label: 'الانتشار',
              value: '${quote.spread?.toStringAsFixed(3) ?? '-'} ج.م',
            ),
            _MetricChip(
              label: 'الانتشار (نقطة)',
              value: quote.spreadBp?.toStringAsFixed(2) ?? '-',
            ),
            _MetricChip(
              label: 'المنتصف',
              value: quote.midPrice?.toStringAsFixed(3) ?? '-',
            ),
          ],
        ),
        if (quote.asOf != null) ...[
          const SizedBox(height: 6),
          Text(
            'آخر تحديث: ${_formatTime(quote.asOf!)}',
            style: theme.textTheme.labelSmall?.copyWith(color: muted),
          ),
        ],
      ],
    );
  }
}

class _SideBox extends StatelessWidget {
  const _SideBox({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(color: color),
          ),
          const SizedBox(height: 2),
          Text(
            value.toStringAsFixed(3),
            textDirection: TextDirection.ltr,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
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

class _TopOfBookError extends StatelessWidget {
  const _TopOfBookError({required this.error, required this.onRetry});

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
                    : 'تعذر تحميل بيانات bid/ask.',
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

class _TopOfBookNote extends StatelessWidget {
  const _TopOfBookNote({required this.message});

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

String _formatTime(DateTime value) {
  final local = value.toLocal();
  return '${_padTwo(local.hour)}:${_padTwo(local.minute)}:${_padTwo(local.second)}';
}

String _padTwo(int number) => number.toString().padLeft(2, '0');

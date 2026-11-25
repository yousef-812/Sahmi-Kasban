import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../scanner/scanner_models.dart';
import '../scanner/scanner_providers.dart';

/// بطاقة لوحة المؤشرات الفنية للسهم (WP-28) — من لقطة الماسح الفني.
///
/// تُحمّل عبر `GET /scanner/technical/{symbol}` (تُحسب عند الغياب) وتعرض
/// RSI/MACD/ADX/ATR%/MFI/Stoch/BB/حجم نسبي/المتوسطات + شارة التقييم.
class StockIndicatorsCard extends ConsumerWidget {
  const StockIndicatorsCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(scannerTechnicalSymbolProvider(ticker));
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
                  Icons.analytics_rounded,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  'المؤشرات الفنية',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              'لقطة الماسح الفني (1D) — تُحسب من الشموم المخزّنة.',
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
              error: (error, stackTrace) => _IndicatorsError(
                error: error,
                onRetry: () =>
                    ref.invalidate(scannerTechnicalSymbolProvider(ticker)),
              ),
              data: (item) => _IndicatorsData(item: item),
            ),
          ],
        ),
      ),
    );
  }
}

class _IndicatorsData extends StatelessWidget {
  const _IndicatorsData({required this.item});

  final ScannerTechnicalItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final metrics = <(String, String, Color?)>[
      ('RSI(14)', _fmt(item.rsi14, digits: 1), _rsiColor(item.rsi14)),
      (
        'MACD',
        '${_fmt(item.macd, digits: 2)} / ${_fmt(item.macdSignal, digits: 2)}',
        _signColor(item.macdHistogram),
      ),
      ('ADX(14)', _fmt(item.adx14, digits: 1), null),
      ('ATR%', _fmt(item.atrPercent, digits: 2), null),
      ('MFI(14)', _fmt(item.mfi14, digits: 1), _rsiColor(item.mfi14)),
      (
        'Stoch',
        '${_fmt(item.stochasticK, digits: 1)} / ${_fmt(item.stochasticD, digits: 1)}',
        null,
      ),
      ('BB', _fmt(item.bbPosition, digits: 2), _bbColor(item.bbPosition)),
      ('حجم نسبي', _fmt(item.relativeVolume20, digits: 2), _signColor((item.relativeVolume20 ?? 1) - 1)),
      (
        'SMA20',
        '${_fmt(item.sma20, digits: 2)} (${_fmtSigned(item.priceVsSma20)}%)',
        _signColor(item.priceVsSma20),
      ),
      (
        'SMA50',
        '${_fmt(item.sma50, digits: 2)} (${_fmtSigned(item.priceVsSma50)}%)',
        _signColor(item.priceVsSma50),
      ),
      (
        'SMA200',
        '${_fmt(item.sma200, digits: 2)} (${_fmtSigned(item.priceVsSma200)}%)',
        _signColor(item.priceVsSma200),
      ),
      ('EMA20/50', '${_fmt(item.ema20, digits: 2)} / ${_fmt(item.ema50, digits: 2)}', null),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _RatingBadge(rating: item.technicalRating ?? item.rating),
            const SizedBox(width: 8),
            if (item.technicalScore != null)
              Text(
                'التقييم ${item.technicalScore!.toStringAsFixed(0)}/100',
                style: theme.textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
            const Spacer(),
            Text(
              '${item.candlesUsed} شمعة',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        GridView.count(
          crossAxisCount: 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          childAspectRatio: 1.55,
          children: [
            for (final (label, value, color) in metrics)
              _MetricTile(label: label, value: value, color: color),
          ],
        ),
      ],
    );
  }

  static String _fmt(double? value, {int digits = 2}) {
    return value?.toStringAsFixed(digits) ?? '-';
  }

  static String _fmtSigned(double? value) {
    if (value == null) return '-';
    final text = value.toStringAsFixed(1);
    return value > 0 ? '+$text' : text;
  }

  static Color? _signColor(double? value) {
    if (value == null) return null;
    if (value > 0) return Colors.green.shade700;
    if (value < 0) return Colors.red.shade700;
    return null;
  }

  static Color? _rsiColor(double? value) {
    if (value == null) return null;
    if (value >= 70) return Colors.red.shade700;
    if (value <= 30) return Colors.green.shade700;
    return null;
  }

  static Color? _bbColor(double? value) {
    if (value == null) return null;
    if (value >= 1.0) return Colors.red.shade700;
    if (value <= 0.0) return Colors.green.shade700;
    return null;
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({required this.label, required this.value, this.color});

  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: muted.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.labelSmall?.copyWith(color: muted),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textDirection: TextDirection.ltr,
            style: theme.textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _RatingBadge extends StatelessWidget {
  const _RatingBadge({required this.rating});

  final String? rating;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (label, color) = switch (rating) {
      'buy' => ('شراء', Colors.green.shade700),
      'sell' => ('بيع', theme.colorScheme.error),
      _ => ('محايد', theme.colorScheme.onSurfaceVariant),
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

class _IndicatorsError extends StatelessWidget {
  const _IndicatorsError({required this.error, required this.onRetry});

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
                    : 'تعذر تحميل المؤشرات الفنية.',
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

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'stock_fundamentals_providers.dart';

/// بطاقة الأساسيات والأرباح (WP-31) — تجمع تحليل الاستثمار + أقرب إعلان أرباح.
///
/// المعطيات من `GET /stocks/{ticker}/investment` (PE/PB/توزيعات/ROE/سوق/EPS
/// + تقييم وترشيح) و`GET /market/earnings-calendar` (الأرباح القادمة).
/// لا backend جديد — مجرد عرض لمسارين موجودين.
class StockFundamentalsCard extends ConsumerWidget {
  const StockFundamentalsCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final investment = ref.watch(stockInvestmentProvider(ticker));
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
                  Icons.account_balance_rounded,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  'الأساسيات والأرباح',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            investment.when(
              loading: () => const _Loading(),
              error: (error, stackTrace) => _Error(
                error: error,
                onRetry: () => ref.invalidate(stockInvestmentProvider(ticker)),
              ),
              data: (analysis) => _InvestmentSection(analysis: analysis),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 10),
              child: Divider(height: 1),
            ),
            _EarningsSection(ticker: ticker),
          ],
        ),
      ),
    );
  }
}

class _InvestmentSection extends StatelessWidget {
  const _InvestmentSection({required this.analysis});

  final StockInvestmentAnalysis analysis;

  @override
  Widget build(BuildContext context) {
    final metrics = <(String, String)>[
      ('PE', _fmt(analysis.peRatio)),
      ('PB', _fmt(analysis.pbRatio)),
      ('توزيعات', analysis.dividendYieldPct != null ? '${_fmt(analysis.dividendYieldPct)}%' : '-'),
      ('ROE', analysis.roePct != null ? '${_fmt(analysis.roePct)}%' : '-'),
      ('السوق', _formatCap(analysis.marketCap)),
      ('EPS', _fmt(analysis.eps)),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 6,
          children: [
            if (analysis.recommendation != null)
              _Badge(label: analysis.recommendation!, positive: true),
            if (analysis.valuationStatus != null)
              _Badge(label: analysis.valuationStatus!, positive: null),
            _Badge(
              label: _categoryLabel(analysis.investmentCategory),
              positive: null,
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
          childAspectRatio: 1.6,
          children: [
            for (final (label, value) in metrics)
              _MetricTile(label: label, value: value),
          ],
        ),
      ],
    );
  }

  static String _fmt(double? value) => value?.toStringAsFixed(2) ?? '-';

  static String _formatCap(double? value) {
    if (value == null) return '-';
    if (value >= 1e9) return '${(value / 1e9).toStringAsFixed(2)} مليار';
    if (value >= 1e6) return '${(value / 1e6).toStringAsFixed(1)} مليون';
    return value.toStringAsFixed(0);
  }

  static String _categoryLabel(String category) {
    return switch (category) {
      'growth' => 'نمو',
      'value' => 'قيمة',
      'income' => 'دخل',
      'speculative' => 'مضاربة',
      'defensive' => 'دفاعي',
      _ => 'متوازن',
    };
  }
}

class _EarningsSection extends ConsumerWidget {
  const _EarningsSection({required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(earningsCalendarProvider(ticker));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'الأرباح القادمة',
          style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 6),
        state.when(
          loading: () => const _Loading(),
          error: (error, stackTrace) => _Error(
            error: error,
            onRetry: () => ref.invalidate(earningsCalendarProvider(ticker)),
          ),
          data: (calendar) {
            if (!calendar.available || calendar.items.isEmpty) {
              return const _Note(
                message: 'لا تتوفر بيانات أرباح قادمة حاليًا — لا يُخترع أي تاريخ.',
              );
            }
            final event = calendar.items.first;
            return _EarningsEventTile(event: event);
          },
        ),
      ],
    );
  }
}

class _EarningsEventTile extends StatelessWidget {
  const _EarningsEventTile({required this.event});

  final EarningsEvent event;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final date =
        '${event.eventDate.year}/${event.eventDate.month.toString().padLeft(2, '0')}/${event.eventDate.day.toString().padLeft(2, '0')}';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: muted.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.event_rounded, size: 18, color: theme.colorScheme.primary),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'إعلان الأرباح — $date',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (event.period != null || event.estimateEps != null)
                  Text(
                    [
                      if (event.period != null) 'الفترة: ${event.period}',
                      if (event.estimateEps != null)
                        'التقدير: EPS ${event.estimateEps!.toStringAsFixed(2)}',
                    ].join(' • '),
                    style: theme.textTheme.labelSmall?.copyWith(color: muted),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  const _Badge({required this.label, required this.positive});

  final String label;

  /// `null` = لون محايد.
  final bool? positive;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = positive == null
        ? theme.colorScheme.onSurfaceVariant
        : positive!
            ? Colors.green.shade700
            : theme.colorScheme.error;
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

class _MetricTile extends StatelessWidget {
  const _MetricTile({required this.label, required this.value});

  final String label;
  final String value;

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
            ),
          ),
        ],
      ),
    );
  }
}

class _Loading extends StatelessWidget {
  const _Loading();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 12),
      child: Center(
        child: SizedBox(
          width: 22,
          height: 22,
          child: CircularProgressIndicator(strokeWidth: 2.5),
        ),
      ),
    );
  }
}

class _Error extends StatelessWidget {
  const _Error({required this.error, required this.onRetry});

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
                    : 'تعذر تحميل البيانات.',
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

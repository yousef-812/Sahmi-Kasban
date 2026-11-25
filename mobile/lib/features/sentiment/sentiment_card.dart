import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'sentiment_models.dart';
import 'sentiment_providers.dart';

/// بطاقة معنويات الأخبار لصفحة تفاصيل السهم (WP-17).
///
/// تعرض مؤشرًا بصريًا للدرجة [-1..1] مع تغطية الأخبار، وتعاملًا صادقًا
/// لحالة `insufficient` كقيمة ناقصة وليست خطأ.
class StockSentimentCard extends ConsumerWidget {
  const StockSentimentCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(stockSentimentProvider(ticker));
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: state.when(
          loading: () => const _SentimentLoading(),
          error: (error, stackTrace) => _SentimentErrorView(
            error: error,
            onRetry: () => ref.invalidate(stockSentimentProvider(ticker)),
          ),
          data: (sentiment) => _SentimentBody(sentiment: sentiment),
        ),
      ),
    );
  }
}

class _SentimentLoading extends StatelessWidget {
  const _SentimentLoading();

  @override
  Widget build(BuildContext context) {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _SentimentHeader(),
        SizedBox(height: 16),
        Center(
          child: Padding(
            padding: EdgeInsets.symmetric(vertical: 12),
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(strokeWidth: 2.5),
            ),
          ),
        ),
        _SentimentDisclaimer(),
      ],
    );
  }
}

class _SentimentErrorView extends StatelessWidget {
  const _SentimentErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SentimentHeader(),
        const SizedBox(height: 12),
        Row(
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 20,
              color: theme.colorScheme.error,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                error is ApiException
                    ? (error as ApiException).message
                    : 'تعذر تحميل معنويات الأخبار.',
                style: theme.textTheme.bodyMedium,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: OutlinedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh_rounded, size: 18),
            label: const Text('إعادة المحاولة'),
          ),
        ),
        const SizedBox(height: 4),
        const _SentimentDisclaimer(),
      ],
    );
  }
}

class _SentimentBody extends StatelessWidget {
  const _SentimentBody({required this.sentiment});

  final SymbolSentiment sentiment;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final verdict = _sentimentVerdict(sentiment.score);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SentimentHeader(),
        const SizedBox(height: 14),
        if (sentiment.isInsufficient) ...[
          _InsufficientBanner(windowDays: sentiment.windowDays),
          const SizedBox(height: 12),
          _CoverageRow(sentiment: sentiment),
        ] else ...[
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                _formatScore(sentiment.score),
                textDirection: TextDirection.ltr,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w900,
                  color: verdict.color,
                ),
              ),
              const SizedBox(width: 8),
              Padding(
                padding: const EdgeInsets.only(bottom: 3),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: verdict.color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    verdict.label,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: verdict.color,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _SentimentGauge(score: sentiment.score, color: verdict.color),
          const SizedBox(height: 12),
          _CoverageRow(sentiment: sentiment),
        ],
        const SizedBox(height: 12),
        const _SentimentDisclaimer(),
      ],
    );
  }
}

class _SentimentHeader extends StatelessWidget {
  const _SentimentHeader();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Icon(Icons.newspaper_rounded, size: 20, color: theme.colorScheme.primary),
        const SizedBox(width: 8),
        Text(
          'معنويات الأخبار',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }
}

/// شريط الدرجة [-1..1] مع مؤشر للموقع وسمين السلبي/المحايد/الإيجابي.
class _SentimentGauge extends StatelessWidget {
  const _SentimentGauge({required this.score, required this.color});

  final double score;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final clamped = score.clamp(-1.0, 1.0);
    // ازاحة المؤشر: -1 يسار / 0 وسط / 1 يمين.
    final position = (clamped + 1) / 2;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          height: 10,
          child: LayoutBuilder(
            builder: (context, constraints) {
              final markerX = position * constraints.maxWidth;
              return Stack(
                clipBehavior: Clip.none,
                children: [
                  Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(6),
                      gradient: LinearGradient(
                        colors: [
                          Colors.red.shade400,
                          Colors.orange.shade200,
                          Colors.green.shade400,
                        ],
                      ),
                    ),
                  ),
                  Positioned(
                    left: (markerX - 7).clamp(
                      0.0,
                      (constraints.maxWidth - 14).clamp(0.0, double.infinity),
                    ),
                    top: -3,
                    child: Container(
                      width: 14,
                      height: 16,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surface,
                        shape: BoxShape.circle,
                        border: Border.all(color: color, width: 3),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 6),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'سلبي',
              style: theme.textTheme.labelSmall?.copyWith(
                color: Colors.red.shade400,
                fontWeight: FontWeight.w700,
              ),
            ),
            Text(
              'محايد',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w700,
              ),
            ),
            Text(
              'إيجابي',
              style: theme.textTheme.labelSmall?.copyWith(
                color: Colors.green.shade400,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _CoverageRow extends StatelessWidget {
  const _CoverageRow({required this.sentiment});

  final SymbolSentiment sentiment;

  @override
  Widget build(BuildContext context) {
    final coverage = _coverageInfo(sentiment.coverage);
    return Wrap(
      spacing: 16,
      runSpacing: 6,
      children: [
        _MetaChip(
          icon: Icons.article_outlined,
          label: 'عدد الأخبار',
          value: '${sentiment.sampleSize}',
        ),
        _MetaChip(
          icon: coverage.icon,
          label: 'التغطية',
          value: coverage.label,
          valueColor: coverage.color,
        ),
        _MetaChip(
          icon: Icons.date_range_outlined,
          label: 'النافذة',
          value: '${sentiment.windowDays} يوم',
        ),
      ],
    );
  }
}

class _MetaChip extends StatelessWidget {
  const _MetaChip({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
  });

  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 15, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(width: 4),
        Text(
          '$label: ',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w800,
            color: valueColor ?? theme.colorScheme.onSurface,
          ),
        ),
      ],
    );
  }
}

/// حالة «لا توجد أخبار كافية» — ناقص صادق وليس خطأ.
class _InsufficientBanner extends StatelessWidget {
  const _InsufficientBanner({required this.windowDays});

  final int windowDays;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final surfaceVariant = theme.colorScheme.onSurfaceVariant;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: surfaceVariant.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline_rounded, size: 20, color: surfaceVariant),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'لا توجد أخبار كافية',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'لم تُجمع أخبار كافية عن هذا السهم خلال آخر $windowDays يومًا '
                  'لحساب درجة معنويات ذات مصداقية.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: surfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SentimentDisclaimer extends StatelessWidget {
  const _SentimentDisclaimer();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Text(
      'تنبيه: هذه الدرجة مؤشر لغوي (lexicon) محسوب من كلمات الأخبار '
      'إرشاديًا — وليس تحليل نموذج ذكي، ولا يُعد توصية استثمارية.',
      style: theme.textTheme.labelSmall?.copyWith(
        color: theme.colorScheme.onSurfaceVariant,
      ),
    );
  }
}

class _SentimentVerdict {
  const _SentimentVerdict(this.label, this.color);

  final String label;
  final Color color;
}

_SentimentVerdict _sentimentVerdict(double score) {
  if (score >= 0.15) {
    return const _SentimentVerdict('إيجابي', Color(0xFF008955));
  }
  if (score <= -0.15) {
    return const _SentimentVerdict('سلبي', Color(0xFFDC2626));
  }
  return const _SentimentVerdict('محايد', Color(0xFF6B7280));
}

class _CoverageInfo {
  const _CoverageInfo(this.label, this.color, this.icon);

  final String label;
  final Color color;
  final IconData icon;
}

_CoverageInfo _coverageInfo(String coverage) {
  return switch (coverage) {
    'normal' => _CoverageInfo('طبيعية', Color(0xFF008955), Icons.check_circle_outline),
    'low' => _CoverageInfo('منخفضة', Color(0xFFD97706), Icons.error_outline),
    _ => _CoverageInfo('غير كافية', Color(0xFF6B7280), Icons.remove_circle_outline),
  };
}

String _formatScore(double score) {
  final clamped = score.clamp(-1.0, 1.0);
  final sign = clamped > 0 ? '+' : '';
  return '$sign${clamped.toStringAsFixed(2)}';
}

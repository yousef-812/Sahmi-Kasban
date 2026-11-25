import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import 'order_flow_models.dart';
import 'order_flow_providers.dart';

/// قسم تدفق الأوامر ونشاط الحيتان في صفحة تفاصيل السهم (WP-19).
///
/// بطاقة قابلة للطي تُحمّل بياناتها عند الفتح فقط. تعرض:
/// - كشف «الحيتان» (إشارة الدوران اليومي الاستثنائي) عند توفره.
/// - دفتر الأوامر/العمق والصفقات مع حالة «غير متاح» صادقة عند غياب المصدر
///   (لا تُختلق صفوف وهمية).
class StockOrderFlowSection extends ConsumerStatefulWidget {
  const StockOrderFlowSection({super.key, required this.ticker});

  final String ticker;

  @override
  ConsumerState<StockOrderFlowSection> createState() =>
      _StockOrderFlowSectionState();
}

class _StockOrderFlowSectionState extends ConsumerState<StockOrderFlowSection> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: ExpansionTile(
        leading: Icon(Icons.waves_rounded, color: theme.colorScheme.primary),
        title: Text(
          'تدفق الأوامر ونشاط الحيتان',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w800,
          ),
        ),
        subtitle: Text(
          'كشف الدوران الاستثنائي وعمق السوق',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        initiallyExpanded: false,
        onExpansionChanged: (expanded) => setState(() => _expanded = expanded),
        children: _expanded ? _buildSections() : const <Widget>[],
      ),
    );
  }

  List<Widget> _buildSections() {
    return <Widget>[
      _WhaleSection(ticker: widget.ticker),
      const Divider(height: 1),
      _DepthSection(ticker: widget.ticker),
      const Divider(height: 1),
      _TradesSection(ticker: widget.ticker),
      const SizedBox(height: 8),
    ];
  }
}

/// ── كشف «الحيتان» ─────────────────────────────────────────────
class _WhaleSection extends ConsumerWidget {
  const _WhaleSection({required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(whaleActivityProvider(ticker));
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.pets_rounded, size: 18),
              const SizedBox(width: 6),
              Text(
                'نشاط الحيتان (إشارة بديلة)',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'دوران يومي استثنائي محسوب من إغلاقات الجلسات — لا يعادل صفقات فردية.',
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 10),
          state.when(
            loading: () => const _SectionLoading(),
            error: (error, stackTrace) => _SectionError(
              error: error,
              onRetry: () => ref.invalidate(whaleActivityProvider(ticker)),
            ),
            data: (snapshot) => _WhaleData(snapshot: snapshot),
          ),
        ],
      ),
    );
  }
}

class _WhaleData extends StatelessWidget {
  const _WhaleData({required this.snapshot});

  final WhaleDetectionSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (!snapshot.available || snapshot.items.isEmpty) {
      return _UnavailableNote(
        message: snapshot.available
            ? 'لا توجد جلسات بدوران استثنائي حاليًا لهذا السهم.'
            : 'كشف نشاط الحيتان غير متاح حاليًا لهذا السهم.',
      );
    }
    final threshold = snapshot.threshold;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (threshold != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              'العتبة المستخدمة: ${_formatEgp(threshold)} ج.م',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        ...snapshot.items.map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: _WhaleSessionTile(item: item),
          ),
        ),
      ],
    );
  }
}

class _WhaleSessionTile extends StatelessWidget {
  const _WhaleSessionTile({required this.item});

  final WhaleActivityItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.onSurface.withValues(alpha: 0.04),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                item.sessionDate ?? '—',
                textDirection: TextDirection.ltr,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
              const Spacer(),
              if (item.isSharpActivity)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.amber.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: Colors.amber.shade700.withValues(alpha: 0.5),
                    ),
                  ),
                  child: Text(
                    'نشاط حاد',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: Colors.amber.shade900,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 16,
            runSpacing: 4,
            children: [
              _Metric(
                label: 'الإغلاق',
                value: item.close.toStringAsFixed(2),
              ),
              _Metric(label: 'الحجم', value: _formatVolume(item.volume)),
              _Metric(
                label: 'الدوران',
                value: '${_formatEgp(item.turnoverEgp)} ج.م',
              ),
              if (item.turnoverRatio != null)
                _Metric(
                  label: 'نسبة الدوران',
                  value: '×${item.turnoverRatio!.toStringAsFixed(1)}',
                  highlight: item.isSharpActivity,
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({
    required this.label,
    required this.value,
    this.highlight = false,
  });

  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label: ',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w800,
            color: highlight ? Colors.amber.shade900 : null,
          ),
        ),
      ],
    );
  }
}

/// ── عمق السوق + دفتر الأوامر ──────────────────────────────────
class _DepthSection extends ConsumerWidget {
  const _DepthSection({required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final depthState = ref.watch(marketDepthProvider(ticker));
    final bookState = ref.watch(orderBookProvider(ticker));
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.stacked_bar_chart_rounded, size: 18),
              const SizedBox(width: 6),
              Text(
                'عمق السوق ودفتر الأوامر',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          depthState.when(
            loading: () => const _SectionLoading(),
            error: (error, stackTrace) => _SectionError(
              error: error,
              onRetry: () => ref.invalidate(marketDepthProvider(ticker)),
            ),
            data: (depth) => _DepthData(depth: depth),
          ),
          const SizedBox(height: 8),
          bookState.when(
            loading: () => const _SectionLoading(),
            error: (error, stackTrace) => _SectionError(
              error: error,
              onRetry: () => ref.invalidate(orderBookProvider(ticker)),
            ),
            data: (book) => _OrderBookData(book: book, ticker: ticker),
          ),
        ],
      ),
    );
  }
}

class _DepthData extends StatelessWidget {
  const _DepthData({required this.depth});

  final MarketDepthSnapshot depth;

  @override
  Widget build(BuildContext context) {
    if (!depth.available) {
      return const _UnavailableNote(
        message:
            'ملخّص عمق السوق غير متاح — مصدر البيانات الحالي لا يوفّر بيانات عمق حقيقية.',
      );
    }
    return Wrap(
      spacing: 16,
      runSpacing: 4,
      children: [
        if (depth.spread != null)
          _Metric(label: 'الفارق (Spread)', value: depth.spread!.toStringAsFixed(2)),
        if (depth.midPrice != null)
          _Metric(label: 'السعر الوسطي', value: depth.midPrice!.toStringAsFixed(2)),
        _Metric(
          label: 'إجمالي عروض الشراء',
          value: _formatVolume(depth.totalBidVolume),
        ),
        _Metric(
          label: 'إجمالي عروض البيع',
          value: _formatVolume(depth.totalAskVolume),
        ),
        _Metric(label: 'عدد المستويات', value: '${depth.levels}'),
      ],
    );
  }
}

class _OrderBookData extends StatelessWidget {
  const _OrderBookData({required this.book, required this.ticker});

  final OrderBookSnapshot book;
  final String ticker;

  @override
  Widget build(BuildContext context) {
    if (!book.available || (book.bids.isEmpty && book.asks.isEmpty)) {
      return const _UnavailableNote(
        message:
            'دفتر الأوامر غير متاح — مصدر البيانات الحالي لا يوفّر بيانات bid/ask حقيقية، '
            'ولذلك لا تُعرض أي صفوف.',
      );
    }
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'دليل الأوامر (أعلى 5 مستويات)',
              style: theme.textTheme.labelMedium?.copyWith(fontWeight: FontWeight.w800),
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: () => context.push('/market/dom/$ticker'),
              icon: const Icon(Icons.layers_rounded, size: 16),
              label: const Text('شاشة DOM الكاملة'),
              style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
            ),
          ],
        ),
        const SizedBox(height: 8),
        _BookSide(title: 'عروض الشراء (Bids)', levels: book.bids, isBid: true),
        const SizedBox(height: 8),
        _BookSide(title: 'عروض البيع (Asks)', levels: book.asks, isBid: false),
      ],
    );
  }
}

class _BookSide extends StatelessWidget {
  const _BookSide({
    required this.title,
    required this.levels,
    required this.isBid,
  });

  final String title;
  final List<OrderBookLevel> levels;
  final bool isBid;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = isBid ? const Color(0xFF008955) : const Color(0xFFDC2626);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.w800,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        ...levels.take(5).map(
          (level) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              children: [
                Text(
                  level.price.toStringAsFixed(2),
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: color,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  _formatVolume(level.size),
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// ── آخر الصفقات ───────────────────────────────────────────────
class _TradesSection extends ConsumerWidget {
  const _TradesSection({required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(recentTradesProvider(ticker));
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.swap_vert_rounded, size: 18),
              const SizedBox(width: 6),
              Text(
                'آخر الصفقات',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          state.when(
            loading: () => const _SectionLoading(),
            error: (error, stackTrace) => _SectionError(
              error: error,
              onRetry: () => ref.invalidate(recentTradesProvider(ticker)),
            ),
            data: (snapshot) => _TradesData(snapshot: snapshot),
          ),
        ],
      ),
    );
  }
}

class _TradesData extends StatelessWidget {
  const _TradesData({required this.snapshot});

  final RecentTradesSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (!snapshot.available || snapshot.items.isEmpty) {
      return const _UnavailableNote(
        message:
            'بيانات الصفقات اللحظية غير متاحة — مصدر البيانات الحالي لا يوفّر time & sales حقيقيًا.',
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ...snapshot.items.take(10).map(
          (trade) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              children: [
                Text(
                  trade.price.toStringAsFixed(2),
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  _formatVolume(trade.size),
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.bodySmall,
                ),
                const SizedBox(width: 12),
                Text(
                  '${_formatEgp(trade.turnoverEgp)} ج.م',
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// ── عناصر مشتركة ──────────────────────────────────────────────
class _SectionLoading extends StatelessWidget {
  const _SectionLoading();

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

class _SectionError extends StatelessWidget {
  const _SectionError({required this.error, required this.onRetry});

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
          style: OutlinedButton.styleFrom(
            visualDensity: VisualDensity.compact,
          ),
        ),
      ],
    );
  }
}

/// حالة «غير متاح» صادقة — تُشرح بأن مصدر البيانات لا يوفّر بيانات حقيقية.
class _UnavailableNote extends StatelessWidget {
  const _UnavailableNote({required this.message});

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
        crossAxisAlignment: CrossAxisAlignment.start,
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

String _formatVolume(double value) {
  if (value >= 1000000) {
    return '${(value / 1000000).toStringAsFixed(2)}M';
  }
  if (value >= 1000) {
    return '${(value / 1000).toStringAsFixed(1)}K';
  }
  return value.toStringAsFixed(0);
}

String _formatEgp(double value) {
  if (value >= 1000000) {
    return '${(value / 1000000).toStringAsFixed(2)} مليون';
  }
  if (value >= 1000) {
    return '${(value / 1000).toStringAsFixed(1)} ألف';
  }
  return value.toStringAsFixed(0);
}

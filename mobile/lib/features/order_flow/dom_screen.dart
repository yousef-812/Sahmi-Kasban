import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'order_flow_models.dart';
import 'order_flow_providers.dart';

/// شاشة DOM (Depth of Market / Ladder) كاملة — WP-35.
///
/// تعرض سلّم الأوامر من `GET /market/orderbook/{ticker}`:
/// - العروض (Bids) على اليسار (أخضر)، الأعلى سعرًا أولًا.
/// - الطلبات (Asks) على اليمين (أحمر)، الأقل سعرًا أولًا.
/// - أحجام تراكمية + نسبة عدم التوازن (imbalance) + السبريد.
/// عند `available:false` تُعرض رسالة صادقة «يتطلب مزوّد بيانات عمق».
/// تعمل فعليًا لحظة تفعيل `MARKET_DATA_DEPTH_PROVIDER`.
class DOMScreen extends ConsumerWidget {
  const DOMScreen({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(orderBookProvider(ticker));

    return Scaffold(
      appBar: AppBar(
        title: Text('DOM - $ticker'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(orderBookProvider(ticker)),
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => _ErrorView(
          error: error,
          onRetry: () => ref.invalidate(orderBookProvider(ticker)),
        ),
        data: (snapshot) {
          if (!snapshot.available || snapshot.bids.isEmpty && snapshot.asks.isEmpty) {
            return _UnavailableView(
              message: 'يتطلب مزوّد بيانات عمق حقيقي.',
            );
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(orderBookProvider(ticker).future),
            child: _DOMLadder(snapshot: snapshot),
          );
        },
      ),
    );
  }
}

class _DOMLadder extends StatelessWidget {
  const _DOMLadder({required this.snapshot});

  final OrderBookSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bids = [...snapshot.bids]
      ..sort((a, b) => b.price.compareTo(a.price)); // أعلى سعر أولًا
    final asks = [...snapshot.asks]
      ..sort((a, b) => a.price.compareTo(b.price)); // أقل سعر أولًا

    // أحجام تراكمية
    final bidCumulatives = <OrderBookLevel, double>{};
    double bidCum = 0;
    for (final level in bids) {
      bidCum += level.size;
      bidCumulatives[level] = bidCum;
    }
    final askCumulatives = <OrderBookLevel, double>{};
    double askCum = 0;
    for (final level in asks) {
      askCum += level.size;
      askCumulatives[level] = askCum;
    }

    // إحصائيات
    final bestBid = bids.isNotEmpty ? bids.first.price : null;
    final bestAsk = asks.isNotEmpty ? asks.first.price : null;
    final spread = (bestBid != null && bestAsk != null) ? bestAsk - bestBid : null;
    final midPrice = (bestBid != null && bestAsk != null) ? (bestBid + bestAsk) / 2 : null;
    final totalBidVolume = bids.fold(0.0, (sum, l) => sum + l.size);
    final totalAskVolume = asks.fold(0.0, (sum, l) => sum + l.size);
    final imbalance = totalBidVolume + totalAskVolume > 0
        ? (totalBidVolume - totalAskVolume) / (totalBidVolume + totalAskVolume)
        : 0.0;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── الرأس: أفضل الأسعار + إحصائيات ──────────────────────
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: 'أفضل شراء',
                  value: bestBid?.toStringAsFixed(2) ?? '—',
                  color: Colors.green.shade700,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _StatCard(
                  label: 'أفضل بيع',
                  value: bestAsk?.toStringAsFixed(2) ?? '—',
                  color: Colors.red.shade700,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _StatCard(
                  label: 'السبريد',
                  value: spread != null ? spread.toStringAsFixed(2) : '—',
                  color: Colors.blue.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: 'سعر المنتصف',
                  value: midPrice?.toStringAsFixed(2) ?? '—',
                  color: Colors.purple.shade700,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _StatCard(
                  label: 'عدم التوازن',
                  value: '${(imbalance * 100).toStringAsFixed(1)}%',
                  color: imbalance > 0
                      ? Colors.green.shade700
                      : imbalance < 0
                          ? Colors.red.shade700
                          : Colors.grey.shade700,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _StatCard(
                  label: 'آخر تحديث',
                  value: snapshot.asOf != null
                      ? '${snapshot.asOf!.hour.toString().padLeft(2, '0')}:${snapshot.asOf!.minute.toString().padLeft(2, '0')}:${snapshot.asOf!.second.toString().padLeft(2, '0')}'
                      : '—',
                  color: Colors.grey.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // ── السلّم: العروض (Bids) ──────────────────────────────
          if (bids.isNotEmpty) ...[
            _SectionHeader(title: 'العروض (Bids)', color: Colors.green.shade700),
            const SizedBox(height: 4),
            for (final level in bids)
              _DOMRow(
                price: level.price,
                size: level.size,
                cumulative: bidCumulatives[level] ?? 0,
                isBid: true,
                totalVolume: totalBidVolume,
              ),
          ],

          // فاصل المنتصف
          Container(
            height: 2,
            color: theme.dividerColor,
            margin: const EdgeInsets.symmetric(vertical: 8),
          ),

          // ── السلّم: الطلبات (Asks) ─────────────────────────────
          if (asks.isNotEmpty) ...[
            _SectionHeader(title: 'الطلبات (Asks)', color: Colors.red.shade700),
            const SizedBox(height: 4),
            for (final level in asks)
              _DOMRow(
                price: level.price,
                size: level.size,
                cumulative: askCumulatives[level] ?? 0,
                isBid: false,
                totalVolume: totalAskVolume,
              ),
          ],
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({required this.label, required this.value, required this.color});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Column(
        children: [
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: theme.textTheme.titleSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, required this.color});

  final String title;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Container(
          width: 4,
          height: 20,
          color: color,
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: theme.textTheme.titleSmall?.copyWith(
            color: color,
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }
}

class _DOMRow extends StatelessWidget {
  const _DOMRow({
    required this.price,
    required this.size,
    required this.cumulative,
    required this.isBid,
    required this.totalVolume,
  });

  final double price;
  final double size;
  final double cumulative;
  final bool isBid;
  final double totalVolume;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = isBid ? Colors.green.shade700 : Colors.red.shade700;
    final bgColor = isBid
        ? Colors.green.shade700.withValues(alpha: 0.08)
        : Colors.red.shade700.withValues(alpha: 0.08);
    final progress = totalVolume > 0 ? (cumulative / totalVolume).clamp(0.0, 1.0) : 0.0;

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 1.5),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          // السعر
          SizedBox(
            width: 80,
            child: Text(
              price.toStringAsFixed(2),
              textDirection: TextDirection.ltr,
              textAlign: isBid ? TextAlign.right : TextAlign.left,
              style: theme.textTheme.labelMedium?.copyWith(
                color: color,
                fontWeight: FontWeight.w800,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
            ),
          ),
          const SizedBox(width: 12),
          // الحجم + التراكمي
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'حجم: ',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    Text(
                      _formatVolume(size),
                      textDirection: TextDirection.ltr,
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'تراكمي: ',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    Text(
                      _formatVolume(cumulative),
                      textDirection: TextDirection.ltr,
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                // شريط التقدم التراكمي
                ClipRRect(
                  borderRadius: BorderRadius.circular(2),
                  child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 4,
                    backgroundColor: color.withValues(alpha: 0.2),
                    valueColor: AlwaysStoppedAnimation(color),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatVolume(double v) {
    if (v >= 1_000_000) return '${(v / 1_000_000).toStringAsFixed(2)} م';
    if (v >= 1_000) return '${(v / 1_000).toStringAsFixed(1)} أ';
    return v.toStringAsFixed(0);
  }
}

class _UnavailableView extends StatelessWidget {
  const _UnavailableView({required this.message});

  final String message;

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
            Icon(Icons.layers_outlined, size: 64, color: muted),
            const SizedBox(height: 16),
            Text(
              'شاشة DOM غير متاحة',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(color: muted),
            ),
            const SizedBox(height: 4),
            Text(
              'عند تفعيل مزوّد عمق السوق (MARKET_DATA_DEPTH_PROVIDER)، ستظهر هنا العروض والطلبات الحقيقية مع أحجام تراكمية.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodySmall?.copyWith(color: muted),
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
                  : 'تعذر تحميل دفتر الأوامر.',
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
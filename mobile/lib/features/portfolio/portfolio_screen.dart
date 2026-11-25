import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'portfolio_providers.dart';

/// شاشة تحليلات المحفظة — ارتباط/تنويع/قطاعات + قائمة المتابعة كتعرض (WP-34).
class PortfolioScreen extends ConsumerWidget {
  const PortfolioScreen({super.key});

  static const routeName = '/portfolio';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(portfolioAnalyticsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('تحليلات المحفظة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(portfolioAnalyticsProvider),
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => _ErrorView(
          error: error,
          onRetry: () => ref.invalidate(portfolioAnalyticsProvider),
        ),
        data: (snapshot) => RefreshIndicator(
          onRefresh: () => ref.refresh(portfolioAnalyticsProvider.future),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── تنبيهات ─────────────────────────────────────
                if (snapshot.warnings.isNotEmpty) ...[
                  _WarningBanner(warnings: snapshot.warnings),
                  const SizedBox(height: 16),
                ],
                // ── الملخص ──────────────────────────────────────
                _SummaryRow(
                  positions: snapshot.positionCount,
                  herfindahl: snapshot.diversification.herfindahl,
                  effectivePositions: snapshot.diversification.effectivePositions,
                  concentrationFlag: snapshot.diversification.concentrationFlag,
                ),
                const SizedBox(height: 16),
                // ── المراكز ──────────────────────────────────────
                if (snapshot.positions.isNotEmpty) ...[
                  Text(
                    'المراكز المفتوحة (${snapshot.positionCount})',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: snapshot.positions.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (_, index) =>
                        _PositionTile(position: snapshot.positions[index]),
                  ),
                  const SizedBox(height: 16),
                ],
                // ── التعرض القطاعي ────────────────────────────────
                if (snapshot.sectorExposure.isNotEmpty) ...[
                  Text(
                    'التعرض القطاعي',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  _SectorExposureChart(exposure: snapshot.sectorExposure),
                  const SizedBox(height: 16),
                ],
                // ── مصفوفة الارتباط ──────────────────────────────
                if (snapshot.correlation.tickers.isNotEmpty) ...[
                  Text(
                    'مصفوفة الارتباط (${snapshot.correlation.lookbackSessions} جلسة)',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  _CorrelationMatrix(
                    tickers: snapshot.correlation.tickers,
                    matrix: snapshot.correlation.matrix,
                  ),
                  const SizedBox(height: 16),
                ],
                // ── قائمة المتابعة كتعرض ──────────────────────────
                if (snapshot.watchlist.tickers.isNotEmpty) ...[
                  Text(
                    'قائمة المتابعة (${snapshot.watchlist.count})',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: snapshot.watchlist.tickers
                        .map((t) => Chip(
                              label: Text(t),
                              backgroundColor: theme.colorScheme.primaryContainer,
                            ))
                        .toList(),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _WarningBanner extends StatelessWidget {
  const _WarningBanner({required this.warnings});

  final List<String> warnings;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, size: 18, color: Colors.amber.shade800),
              const SizedBox(width: 8),
              Text(
                'تنبيهات',
                style: theme.textTheme.labelLarge?.copyWith(
                  color: Colors.amber.shade800,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          for (final w in warnings)
            Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Text(
                '• $w',
                style: theme.textTheme.bodySmall?.copyWith(color: Colors.amber.shade800),
              ),
            ),
        ],
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({
    required this.positions,
    required this.herfindahl,
    required this.effectivePositions,
    required this.concentrationFlag,
  });

  final int positions;
  final double herfindahl;
  final double effectivePositions;
  final bool concentrationFlag;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            label: 'مراكز',
            value: positions.toString(),
            color: theme.colorScheme.primary,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            label: 'HHI',
            value: herfindahl.toStringAsFixed(3),
            color: concentrationFlag ? theme.colorScheme.error : Colors.green.shade700,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            label: 'مراكز فعالة',
            value: effectivePositions.toStringAsFixed(1),
            color: Colors.blue.shade700,
          ),
        ),
      ],
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

class _PositionTile extends StatelessWidget {
  const _PositionTile({required this.position});

  final PortfolioPosition position;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final isLong = position.direction == 'long';
    final dirColor = isLong ? Colors.green.shade700 : theme.colorScheme.error;
    final pnlColor = position.unrealizedPct == null
        ? muted
        : position.unrealizedPct! > 0
            ? Colors.green.shade700
            : theme.colorScheme.error;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: dirColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    isLong ? 'شراء' : 'بيع',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: dirColor,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    position.ticker,
                    style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
                  ),
                ),
                if (position.unrealizedPct != null)
                  Text(
                    '${position.unrealizedPct! > 0 ? '+' : ''}${position.unrealizedPct!.toStringAsFixed(1)}%',
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: pnlColor,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 12,
              runSpacing: 4,
              children: [
                _Level(label: 'دخول', value: position.entry.toStringAsFixed(2)),
                _Level(label: 'وقف', value: position.stop.toStringAsFixed(2)),
                if (position.currentPrice != null)
                  _Level(label: 'حالي', value: position.currentPrice!.toStringAsFixed(2)),
                _Level(label: 'وزن', value: '${(position.weight * 100).toStringAsFixed(1)}%'),
                if (position.sector != null)
                  _Level(label: 'قطاع', value: position.sector!),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Level extends StatelessWidget {
  const _Level({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label: ',
          style: theme.textTheme.labelSmall?.copyWith(color: muted),
        ),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: theme.textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w700),
        ),
      ],
    );
  }
}

class _SectorExposureChart extends StatelessWidget {
  const _SectorExposureChart({required this.exposure});

  final Map<String, double> exposure;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final total = exposure.values.fold(0.0, (a, b) => a + b);
    if (total == 0) return const SizedBox.shrink();

    final sorted = exposure.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Column(
      children: [
        for (final entry in sorted)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              children: [
                Expanded(
                  flex: 2,
                  child: Text(
                    entry.key,
                    style: theme.textTheme.bodySmall,
                  ),
                ),
                Expanded(
                  flex: 3,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: entry.value / total,
                      minHeight: 8,
                      backgroundColor: muted.withValues(alpha: 0.2),
                      valueColor: AlwaysStoppedAnimation(theme.colorScheme.primary),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                SizedBox(
                  width: 50,
                  child: Text(
                    '${(entry.value / total * 100).toStringAsFixed(1)}%',
                    textAlign: TextAlign.end,
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.labelSmall?.copyWith(color: muted),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _CorrelationMatrix extends StatelessWidget {
  const _CorrelationMatrix({
    required this.tickers,
    required this.matrix,
  });

  final List<String> tickers;
  final Map<String, Map<String, double?>> matrix;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (tickers.isEmpty) return const SizedBox.shrink();

    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.04),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          // Header
          Row(
            children: [
              const SizedBox(width: 50),
              for (final t in tickers)
                Expanded(
                  child: Center(
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(
                        t,
                        style: theme.textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w700),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ),
            ],
          ),
          // Rows
          for (final rowTicker in tickers)
            Container(
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(color: theme.dividerColor.withValues(alpha: 0.2)),
                ),
              ),
              child: Row(
                children: [
                  SizedBox(
                    width: 50,
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(8),
                        child: Text(
                          rowTicker,
                          style: theme.textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w700),
                        ),
                      ),
                    ),
                  ),
                  for (final colTicker in tickers)
                    Expanded(
                      child: Center(
                        child: Padding(
                          padding: const EdgeInsets.all(6),
                          child: _CorrelationCell(
                            value: matrix[rowTicker]?[colTicker],
                            isDiagonal: rowTicker == colTicker,
                          ),
                        ),
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

class _CorrelationCell extends StatelessWidget {
  const _CorrelationCell({required this.value, required this.isDiagonal});

  final double? value;
  final bool isDiagonal;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (isDiagonal) {
      return Text(
        '1.00',
        textDirection: TextDirection.ltr,
        style: theme.textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w700),
      );
    }
    if (value == null) {
      return Text(
        '—',
        style: theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
      );
    }
    final v = value!;
    Color color;
    if (v >= 0.7) {
      color = Colors.red.shade700;
    } else if (v >= 0.4) {
      color = Colors.orange.shade700;
    } else if (v >= 0.1) {
      color = Colors.amber.shade700;
    } else if (v >= -0.1) {
      color = theme.colorScheme.onSurfaceVariant;
    } else if (v >= -0.4) {
      color = Colors.lightBlue.shade700;
    } else {
      color = Colors.blue.shade700;
    }

    return Text(
      v.toStringAsFixed(2),
      textDirection: TextDirection.ltr,
      style: theme.textTheme.labelSmall?.copyWith(color: color, fontWeight: FontWeight.w700),
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
                  : 'تعذر تحميل تحليلات المحفظة.',
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
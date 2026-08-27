import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/theme/terminal_theme.dart';
import '../../domain/models.dart';
import 'pulse_providers.dart';

/// شاشة PULSE — نبض السوق ومحطة المتداول الرئيسية.
/// مصممة للوصول للمعلومة في أقل من 3 ثواني.
class PulseScreen extends ConsumerWidget {
  const PulseScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = TerminalTheme.of(context);
    final top10Async = ref.watch(top10PreviewProvider);

    return Scaffold(
      backgroundColor: theme.bgBase,
      appBar: _TerminalAppBar(theme: theme),
      body: RefreshIndicator(
        color: theme.signalGold,
        onRefresh: () async {
          ref.invalidate(top10PreviewProvider);
          ref.invalidate(marketPulseProvider);
        },
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          children: [
            _MarketStatusSection(theme: theme),
            const SizedBox(height: 16),
            _QuickStatsRow(theme: theme),
            const SizedBox(height: 16),
            _LastAnalysisCard(theme: theme),
            const SizedBox(height: 16),
            _Top10PreviewSection(theme: theme, async: top10Async),
            const SizedBox(height: 80), // مساحة للـ FAB
          ],
        ),
      ),
      floatingActionButton: _QuickAnalyzeFAB(theme: theme),
    );
  }
}

/// شريط علوي يعرض حالة الاتصال ووقت السوق
class _TerminalAppBar extends StatelessWidget implements PreferredSizeWidget {
  const _TerminalAppBar({required this.theme});
  final TerminalThemeData theme;

  @override
  Size get preferredSize => const Size.fromHeight(56);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: theme.bgBase,
        border: Border(bottom: BorderSide(color: theme.border, width: 1)),
      ),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              // شعار التطبيق
              Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: theme.signalGold,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Icon(
                      Icons.show_chart_rounded,
                      color: Color(0xFF0A0E1A),
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'سهمي كسبان',
                        style: theme.titleSmall.copyWith(
                          color: theme.textPrimary,
                          letterSpacing: 0.5,
                        ),
                      ),
                      Text(
                        'TRADING TERMINAL',
                        style: theme.monoTiny.copyWith(
                          color: theme.signalGold,
                          letterSpacing: 1.5,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const Spacer(),
              // مؤشر السوق مفتوح/مغلق
              _MarketStatusChip(theme: theme),
            ],
          ),
        ),
      ),
    );
  }
}

class _MarketStatusChip extends ConsumerWidget {
  const _MarketStatusChip({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pulse = ref.watch(marketPulseProvider);
    return pulse.when(
      data: (data) {
        final isOpen = data.isMarketOpen;
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: isOpen
                ? theme.bullGreen.withValues(alpha: 0.12)
                : theme.bearRed.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isOpen ? theme.bullGreen : theme.bearRed,
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: isOpen ? theme.bullGreen : theme.bearRed,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                isOpen ? 'السوق مفتوح' : 'السوق مغلق',
                style: theme.monoTiny.copyWith(
                  color: isOpen ? theme.bullGreen : theme.bearRed,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        );
      },
      loading: () => const SizedBox(width: 80, height: 24),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}

/// قسم حالة المؤشر الرئيسي (EGX30)
class _MarketStatusSection extends ConsumerWidget {
  const _MarketStatusSection({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pulse = ref.watch(marketPulseProvider);
    return pulse.when(
      data: (data) => Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: theme.bgSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: theme.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'EGX30',
                  style: theme.monoSmall.copyWith(
                    color: theme.textSecondary,
                    letterSpacing: 1.2,
                  ),
                ),
                const Spacer(),
                Text(
                  data.egx30ChangePct >= 0 ? '▲' : '▼',
                  style: theme.monoLarge.copyWith(
                    color: data.egx30ChangePct >= 0
                        ? theme.bullGreen
                        : theme.bearRed,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  data.egx30Value.toStringAsFixed(0),
                  style: theme.monoHuge.copyWith(
                    color: theme.textPrimary,
                    fontWeight: FontWeight.w900,
                    height: 1,
                  ),
                ),
                const SizedBox(width: 12),
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    '${data.egx30ChangePct >= 0 ? '+' : ''}${data.egx30ChangePct.toStringAsFixed(2)}%',
                    style: theme.monoMedium.copyWith(
                      color: data.egx30ChangePct >= 0
                          ? theme.bullGreen
                          : theme.bearRed,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // شريط التقدم البصري
            _TrendBar(value: data.egx30ChangePct, theme: theme),
          ],
        ),
      ),
      loading: () => _PulseSkeleton(theme: theme),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}

class _TrendBar extends StatelessWidget {
  const _TrendBar({required this.value, required this.theme});
  final double value;
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context) {
    final isPositive = value >= 0;
    final intensity = (value.abs() / 3.0).clamp(0.1, 1.0);
    return Container(
      height: 4,
      decoration: BoxDecoration(
        color: theme.bgBase,
        borderRadius: BorderRadius.circular(2),
      ),
      child: FractionallySizedBox(
        alignment: isPositive ? Alignment.centerLeft : Alignment.centerRight,
        widthFactor: intensity,
        child: Container(
          decoration: BoxDecoration(
            color: isPositive ? theme.bullGreen : theme.bearRed,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
      ),
    );
  }
}

/// صف الإحصائيات السريعة
class _QuickStatsRow extends ConsumerWidget {
  const _QuickStatsRow({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pulse = ref.watch(marketPulseProvider);
    return pulse.when(
      data: (data) => Row(
        children: [
          Expanded(
            child: _QuickStatTile(
              theme: theme,
              label: 'أعلى رابح',
              ticker: data.topGainer?.ticker ?? '—',
              value: data.topGainer?.changePercent ?? 0,
              isPositive: true,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _QuickStatTile(
              theme: theme,
              label: 'أكبر خاسر',
              ticker: data.topLoser?.ticker ?? '—',
              value: data.topLoser?.changePercent ?? 0,
              isPositive: false,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _QuickStatTile(
              theme: theme,
              label: 'الأكثر تداولاً',
              ticker: data.mostActive?.ticker ?? '—',
              value: (data.mostActive?.volume ?? 0) / 1000000.0,
              isPositive: true,
              suffix: 'M',
            ),
          ),
        ],
      ),
      loading: () => const SizedBox(height: 80),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}

class _QuickStatTile extends StatelessWidget {
  const _QuickStatTile({
    required this.theme,
    required this.label,
    required this.ticker,
    required this.value,
    required this.isPositive,
    this.suffix = '%',
  });
  final TerminalThemeData theme;
  final String label;
  final String ticker;
  final double value;
  final bool isPositive;
  final String suffix;

  @override
  Widget build(BuildContext context) {
    final color = isPositive ? theme.bullGreen : theme.bearRed;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.bgSurface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: theme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.monoTiny.copyWith(color: theme.textSecondary),
          ),
          const SizedBox(height: 6),
          Text(
            ticker,
            style: theme.monoMedium.copyWith(
              color: theme.textPrimary,
              fontWeight: FontWeight.w800,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            '${isPositive ? '+' : ''}${value.toStringAsFixed(2)}$suffix',
            style: theme.monoSmall.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

/// بطاقة آخر تحليل قام به المستخدم — one-tap لإعادة فتحه
class _LastAnalysisCard extends ConsumerWidget {
  const _LastAnalysisCard({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    const lastTicker = 'COMI';
    const lastSignal = 'BUY';
    const lastScore = 78.5;
    const lastDate = 'منذ 3 ساعات';

    return InkWell(
      onTap: () => context.push('/stocks/$lastTicker'),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: theme.bgSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: theme.signalGold.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: theme.signalGold.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: theme.signalGold.withValues(alpha: 0.4),
                ),
              ),
              child: const Icon(
                Icons.history_rounded,
                color: Color(0xFFFFB800),
                size: 24,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'آخر تحليل',
                    style: theme.monoTiny.copyWith(color: theme.textSecondary),
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      Text(
                        lastTicker,
                        style: theme.titleSmall.copyWith(
                          color: theme.textPrimary,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(width: 8),
                      _SignalBadge(signal: lastSignal, theme: theme),
                      const SizedBox(width: 8),
                      Text(
                        lastScore.toStringAsFixed(0),
                        style: theme.monoSmall.copyWith(
                          color: theme.signalGold,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                  Text(
                    lastDate,
                    style: theme.monoTiny.copyWith(color: theme.textSecondary),
                  ),
                ],
              ),
            ),
            Icon(Icons.chevron_left, color: theme.textSecondary, size: 22),
          ],
        ),
      ),
    );
  }
}

class _SignalBadge extends StatelessWidget {
  const _SignalBadge({required this.signal, required this.theme});
  final String signal;
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context) {
    final (color, label) = switch (signal) {
      'BUY' => (theme.bullGreen, 'شراء'),
      'AVOID' => (theme.bearRed, 'تجنب'),
      _ => (theme.textSecondary, 'مراقبة'),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        label,
        style: theme.monoTiny.copyWith(
          color: color,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}

/// قسم معاينة تقرير أفضل 10
class _Top10PreviewSection extends StatelessWidget {
  const _Top10PreviewSection({required this.theme, required this.async});
  final TerminalThemeData theme;
  final AsyncValue<List<MarketReportItem>> async;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.bgSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: theme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.leaderboard_rounded,
                color: theme.signalGold,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'تقرير اليوم — أفضل 10',
                style: theme.titleSmall.copyWith(
                  color: theme.textPrimary,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const Spacer(),
              Text(
                '50 نقطة',
                style: theme.monoTiny.copyWith(color: theme.signalGold),
              ),
            ],
          ),
          const SizedBox(height: 14),
          async.when(
            data: (items) => _Top10List(theme: theme, items: items),
            loading: () => const _Top10Skeleton(),
            error: (_, __) => Text(
              'تعذر تحميل التقرير',
              style: theme.monoSmall.copyWith(color: theme.bearRed),
            ),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: () => context.push('/reports'),
              style: FilledButton.styleFrom(
                backgroundColor: theme.signalGold,
                foregroundColor: const Color(0xFF0A0E1A),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'افتح التقرير الكامل ←',
                style: theme.monoSmall.copyWith(
                  color: const Color(0xFF0A0E1A),
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Top10List extends StatelessWidget {
  const _Top10List({required this.theme, required this.items});
  final TerminalThemeData theme;
  final List<MarketReportItem> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return Text(
        'لا توجد بيانات تقرير حية حاليًا',
        style: theme.monoSmall.copyWith(color: theme.textSecondary),
      );
    }
    final displayItems = items.take(3).toList();
    return Column(
      children: [
        for (int i = 0; i < displayItems.length; i++) ...[
          _Top10Row(
            theme: theme,
            rank: i + 1,
            ticker: displayItems[i].ticker,
            score: displayItems[i].score,
            signal: (displayItems[i].payload['signal'] as String?) ?? 'WATCH',
          ),
          if (i < displayItems.length - 1)
            Divider(height: 20, color: theme.border),
        ],
        if (items.length > 3)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              '+ ${items.length - 3} أسهم أخرى',
              style: theme.monoTiny.copyWith(color: theme.textSecondary),
            ),
          ),
      ],
    );
  }
}

class _Top10Row extends StatelessWidget {
  const _Top10Row({
    required this.theme,
    required this.rank,
    required this.ticker,
    required this.score,
    required this.signal,
  });
  final TerminalThemeData theme;
  final int rank;
  final String ticker;
  final double score;
  final String signal;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 24,
          child: Text(
            '#$rank',
            style: theme.monoSmall.copyWith(
              color: theme.signalGold,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            ticker,
            style: theme.monoMedium.copyWith(
              color: theme.textPrimary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        _SignalBadge(signal: signal, theme: theme),
        const SizedBox(width: 12),
        SizedBox(
          width: 40,
          child: Text(
            score.toStringAsFixed(0),
            textAlign: TextAlign.right,
            style: theme.monoMedium.copyWith(
              color: theme.textPrimary,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
      ],
    );
  }
}

/// FAB للتحليل السريع
class _QuickAnalyzeFAB extends StatelessWidget {
  const _QuickAnalyzeFAB({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      onPressed: () => context.push('/stocks'),
      backgroundColor: theme.signalGold,
      foregroundColor: const Color(0xFF0A0E1A),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      icon: const Icon(Icons.bolt_rounded, size: 22),
      label: Text(
        'تحليل سريع',
        style: theme.monoSmall.copyWith(
          color: const Color(0xFF0A0E1A),
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}

// Skeleton loaders
class _PulseSkeleton extends StatelessWidget {
  const _PulseSkeleton({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 120,
      decoration: BoxDecoration(
        color: theme.bgSurface,
        borderRadius: BorderRadius.circular(12),
      ),
    );
  }
}

class _Top10Skeleton extends StatelessWidget {
  const _Top10Skeleton();

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        SizedBox(height: 24, child: _SkeletonLine()),
        SizedBox(height: 16),
        SizedBox(height: 24, child: _SkeletonLine()),
        SizedBox(height: 16),
        SizedBox(height: 24, child: _SkeletonLine()),
      ],
    );
  }
}

class _SkeletonLine extends StatelessWidget {
  const _SkeletonLine();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }
}

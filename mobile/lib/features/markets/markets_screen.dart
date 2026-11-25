import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'market_models.dart';
import 'market_providers.dart';

/// شاشة الأسواق بثلاثة تبويبات: عالمي / اتساع / حالة السوق (WP-33).
class MarketsScreen extends ConsumerWidget {
  const MarketsScreen({super.key});

  static const routeName = '/markets';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الأسواق'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'عالمي'),
              Tab(text: 'اتساع'),
              Tab(text: 'حالة السوق'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            _GlobalTab(),
            _BreadthTab(),
            _StatusTab(),
          ],
        ),
      ),
    );
  }
}

class _GlobalTab extends ConsumerWidget {
  const _GlobalTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(globalMarketProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => _ErrorView(
        error: error,
        onRetry: () => ref.invalidate(globalMarketProvider),
      ),
      data: (snapshot) {
        if (!snapshot.available) {
          return _EmptyView(
            message: snapshot.error ?? 'لا تتوفر بيانات الأسواق العالمية حاليًا.',
          );
        }
        return RefreshIndicator(
          onRefresh: () => ref.refresh(globalMarketProvider.future),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _GlobalSection(
                title: 'المؤشرات',
                items: snapshot.indices,
                emptyMessage: 'لا توجد مؤشرات.',
              ),
              const SizedBox(height: 16),
              _GlobalSection(
                title: 'أزواج العملات',
                items: snapshot.fx,
                emptyMessage: 'لا توجد أزواج عملات.',
              ),
              const SizedBox(height: 16),
              _GlobalSection(
                title: 'السلع',
                items: snapshot.commodities,
                emptyMessage: 'لا توجد سلع.',
              ),
            ],
          ),
        );
      },
    );
  }
}

class _GlobalSection extends StatelessWidget {
  const _GlobalSection({
    required this.title,
    required this.items,
    required this.emptyMessage,
  });

  final String title;
  final List<GlobalMarketItem> items;
  final String emptyMessage;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (items.isEmpty) {
      return _EmptyCard(message: emptyMessage);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: items.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (_, index) => _GlobalItemTile(item: items[index]),
        ),
      ],
    );
  }
}

class _GlobalItemTile extends StatelessWidget {
  const _GlobalItemTile({required this.item});

  final GlobalMarketItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final changeColor = item.changePct == null
        ? muted
        : item.changePct! > 0
            ? Colors.green.shade700
            : theme.colorScheme.error;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.nameAr,
                    style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    item.name,
                    style: theme.textTheme.labelSmall?.copyWith(color: muted),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  item.value.toStringAsFixed(2),
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                if (item.changePct != null)
                  Text(
                    '${item.changePct! > 0 ? '+' : ''}${item.changePct!.toStringAsFixed(2)}%',
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: changeColor,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _BreadthTab extends ConsumerWidget {
  const _BreadthTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(marketBreadthProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => _ErrorView(
        error: error,
        onRetry: () => ref.invalidate(marketBreadthProvider),
      ),
      data: (snapshot) {
        if (!snapshot.available) {
          return _EmptyView(
            message: snapshot.reason ?? 'لا تتوفر بيانات اتساع السوق حاليًا.',
          );
        }
        return RefreshIndicator(
          onRefresh: () => ref.refresh(marketBreadthProvider.future),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    _StatCard(
                      label: 'صاعد',
                      value: snapshot.advancers.toString(),
                      color: Colors.green.shade700,
                    ),
                    const SizedBox(width: 8),
                    _StatCard(
                      label: 'هابط',
                      value: snapshot.decliners.toString(),
                      color: Colors.red.shade700,
                    ),
                    const SizedBox(width: 8),
                    _StatCard(
                      label: 'ثابت',
                      value: snapshot.unchanged.toString(),
                      color: Colors.blueGrey,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (snapshot.advanceDeclineRatio != null)
                  _StatCard(
                    label: 'نسبة الصاعد/الهابط (AD)',
                    value: snapshot.advanceDeclineRatio!.toStringAsFixed(2),
                    color: Colors.blue.shade700,
                    wide: true,
                  ),
                const SizedBox(height: 16),
                Text(
                  'أداء القطاعات',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 8),
                if (snapshot.sectorPerformance.isEmpty)
                  _EmptyCard(message: 'لا توجد بيانات قطاعية.')
                else
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: snapshot.sectorPerformance.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (_, index) =>
                        _SectorTile(sector: snapshot.sectorPerformance[index]),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _SectorTile extends StatelessWidget {
  const _SectorTile({required this.sector});

  final SectorPerformance sector;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    final changeColor = sector.avgChangePct > 0
        ? Colors.green.shade700
        : sector.avgChangePct < 0
            ? theme.colorScheme.error
            : muted;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Text(
                sector.sector,
                style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
            ),
            const SizedBox(width: 12),
            Text(
              '${sector.symbols} رمز',
              style: theme.textTheme.labelSmall?.copyWith(color: muted),
            ),
            const SizedBox(width: 8),
            Text(
              '${sector.avgChangePct > 0 ? '+' : ''}${sector.avgChangePct.toStringAsFixed(2)}%',
              textDirection: TextDirection.ltr,
              style: theme.textTheme.labelMedium?.copyWith(
                color: changeColor,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusTab extends ConsumerWidget {
  const _StatusTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(marketStatusProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => _ErrorView(
        error: error,
        onRetry: () => ref.invalidate(marketStatusProvider),
      ),
      data: (snapshot) {
        return RefreshIndicator(
          onRefresh: () => ref.refresh(marketStatusProvider.future),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _StatusCard(
                  title: snapshot.isOpen ? 'السوق مفتوح' : 'السوق مغلق',
                  isOpen: snapshot.isOpen,
                ),
                const SizedBox(height: 16),
                _StatusRow(label: 'الجلسة', value: '${snapshot.session.opensAt} – ${snapshot.session.closesAt}'),
                _StatusRow(label: 'المنطقة الزمنية', value: snapshot.timezone),
                _StatusRow(label: 'التاريخ', value: snapshot.date),
                _StatusRow(label: 'اليوم', value: _dayAr(snapshot.day)),
                if (snapshot.nextOpen != null)
                  _StatusRow(label: 'الافتتاح القادم', value: snapshot.nextOpen!),
                if (snapshot.nextClose != null)
                  _StatusRow(label: 'الإغلاق القادم', value: snapshot.nextClose!),
                _StatusRow(label: 'يوم تداول', value: snapshot.isTradingDay ? 'نعم' : 'لا'),
              ],
            ),
          ),
        );
      },
    );
  }

  String _dayAr(String day) {
    return switch (day.toLowerCase()) {
      'monday' => 'الإثنين',
      'tuesday' => 'الثلاثاء',
      'wednesday' => 'الأربعاء',
      'thursday' => 'الخميس',
      'friday' => 'الجمعة',
      'saturday' => 'السبت',
      'sunday' => 'الأحد',
      _ => day,
    };
  }
}

class _StatusCard extends StatelessWidget {
  const _StatusCard({required this.title, required this.isOpen});

  final String title;
  final bool isOpen;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = isOpen ? Colors.green.shade700 : theme.colorScheme.error;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Row(
        children: [
          Icon(
            isOpen ? Icons.check_circle_rounded : Icons.cancel_rounded,
            size: 28,
            color: color,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: theme.textTheme.titleMedium?.copyWith(
                color: color,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusRow extends StatelessWidget {
  const _StatusRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(color: muted),
          ),
          const Spacer(),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: theme.textTheme.labelMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.label,
    required this.value,
    required this.color,
    this.wide = false,
  });

  final String label;
  final String value;
  final Color color;
  final bool wide;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      flex: wide ? 2 : 1,
      child: Container(
        padding: const EdgeInsets.all(14),
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
              style: theme.textTheme.titleMedium?.copyWith(
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
      ),
    );
  }
}

class _EmptyView extends StatelessWidget {
  const _EmptyView({required this.message});

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
            Icon(Icons.info_outline_rounded, size: 48, color: muted),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(color: muted),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  const _EmptyCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
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
                  : 'تعذر تحميل البيانات.',
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
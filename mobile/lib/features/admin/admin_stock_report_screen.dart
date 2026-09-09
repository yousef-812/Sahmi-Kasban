import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'admin_repository.dart';

class AdminStockReportScreen extends ConsumerWidget {
  const AdminStockReportScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('تقرير الأسهم الإداري'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'مقومة بأقل من قيمتها'),
              Tab(text: 'نازلة 10%'),
              Tab(text: 'فرص ارتداد'),
            ],
          ),
        ),
        body: const _StockReportBody(),
      ),
    );
  }
}

class StockReportTab extends ConsumerStatefulWidget {
  const StockReportTab({super.key});

  @override
  ConsumerState<StockReportTab> createState() => _StockReportTabState();
}

class _StockReportTabState extends ConsumerState<StockReportTab> {
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final repo = ref.read(adminRepositoryProvider);
      final result = await repo.fetchStockReport();
      if (mounted) {
        setState(() {
          _data = result;
          _loading = false;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.message;
        });
      }
    } on Object catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (_loading && _data == null) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null && _data == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.error_outline_rounded,
                size: 48,
                color: theme.colorScheme.error,
              ),
              const SizedBox(height: 12),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyLarge,
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _load,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      );
    }

    final undervalued = _mapsList(_data?['undervalued']);
    final dropped = _mapsList(_data?['dropped']);
    final bounceCandidates = _mapsList(_data?['bounce_candidates']);

    return DefaultTabController(
      length: 3,
      child: Column(
        children: [
          Material(
            color: theme.colorScheme.surface,
            child: TabBar(
              tabs: const [
                Tab(text: 'مقومة بأقل من قيمتها'),
                Tab(text: 'نازلة 10%'),
                Tab(text: 'فرص ارتداد'),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              children: [
                _StockList(
                  items: undervalued,
                  type: _StockValueType.undervalued,
                  onRefresh: _load,
                ),
                _StockList(
                  items: dropped,
                  type: _StockValueType.dropped,
                  onRefresh: _load,
                ),
                _StockList(
                  items: bounceCandidates,
                  type: _StockValueType.bounce,
                  onRefresh: _load,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StockReportBody extends ConsumerStatefulWidget {
  const _StockReportBody();

  @override
  ConsumerState<_StockReportBody> createState() => _StockReportBodyState();
}

class _StockReportBodyState extends ConsumerState<_StockReportBody> {
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final repo = ref.read(adminRepositoryProvider);
      final result = await repo.fetchStockReport();
      if (mounted) {
        setState(() {
          _data = result;
          _loading = false;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.message;
        });
      }
    } on Object catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _data == null) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!),
            const SizedBox(height: 12),
            FilledButton(onPressed: _load, child: const Text('إعادة المحاولة')),
          ],
        ),
      );
    }

    final undervalued = _mapsList(_data?['undervalued']);
    final dropped = _mapsList(_data?['dropped']);
    final bounceCandidates = _mapsList(_data?['bounce_candidates']);

    return TabBarView(
      children: [
        _StockList(
          items: undervalued,
          type: _StockValueType.undervalued,
          onRefresh: _load,
        ),
        _StockList(
          items: dropped,
          type: _StockValueType.dropped,
          onRefresh: _load,
        ),
        _StockList(
          items: bounceCandidates,
          type: _StockValueType.bounce,
          onRefresh: _load,
        ),
      ],
    );
  }
}

enum _StockValueType {
  undervalued,
  dropped,
  bounce;

  String get label => switch (this) {
    undervalued => 'مقومة بأقل من قيمتها',
    dropped => 'نازلة أكثر من 10%',
    bounce => 'فرصة ارتداد',
  };

  String get emptyLabel => switch (this) {
    undervalued => 'لا توجد أسهم مقومة بأقل من قيمتها حالياً.',
    dropped => 'لا توجد أسهم نازلة أكثر من 10% هذا الشهر.',
    bounce => 'لا توجد فرص ارتداد حالياً.',
  };

  IconData get icon => switch (this) {
    undervalued => Icons.trending_down_rounded,
    dropped => Icons.arrow_downward_rounded,
    bounce => Icons.trending_up_rounded,
  };

  Color get color => switch (this) {
    undervalued => Colors.green,
    dropped => Colors.red,
    bounce => Colors.blue,
  };
}

class _StockList extends StatelessWidget {
  const _StockList({
    required this.items,
    required this.type,
    required this.onRefresh,
  });

  final List<Map<String, dynamic>> items;
  final _StockValueType type;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      child: items.isEmpty
          ? ListView(
              children: [
                SizedBox(
                  height: MediaQuery.of(context).size.height * 0.4,
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(type.icon, size: 48, color: Colors.grey),
                        const SizedBox(height: 12),
                        Text(
                          type.emptyLabel,
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            )
          : ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) => _StockCard(
                item: items[index],
                type: type,
              ),
            ),
    );
  }
}

class _StockCard extends StatelessWidget {
  const _StockCard({required this.item, required this.type});

  final Map<String, dynamic> item;
  final _StockValueType type;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final ticker = item['ticker'] as String? ?? '';
    final companyName = item['company_name'] as String? ?? '';
    final currentPrice = (item['current_price'] as num?)?.toDouble() ?? 0;
    final fairValue = (item['fair_value'] as num?)?.toDouble();
    final marginOfSafety = (item['margin_of_safety_pct'] as num?)?.toDouble();
    final investmentScore = (item['investment_score'] as num?)?.toDouble();
    final priceChange = (item['price_change_pct'] as num?)?.toDouble();
    final expectedRecovery =
        (item['expected_recovery_pct'] as num?)?.toDouble();
    final peRatio = (item['pe_ratio'] as num?)?.toDouble();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: type.color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(
                      color: type.color.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Text(
                    ticker,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: type.color,
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    companyName,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _MetricChip(
                  label: 'السعر الحالي',
                  value: '${currentPrice.toStringAsFixed(2)} ج.م',
                  color: Colors.black87,
                ),
                if (fairValue != null) ...[
                  const SizedBox(width: 8),
                  _MetricChip(
                    label: 'القيمة العادلة',
                    value: '${fairValue.toStringAsFixed(2)} ج.م',
                    color: Colors.green,
                  ),
                ],
                if (priceChange != null) ...[
                  const SizedBox(width: 8),
                  _MetricChip(
                    label: 'التغيير الشهري',
                    value:
                        '${priceChange >= 0 ? '+' : ''}${priceChange.toStringAsFixed(1)}%',
                    color: priceChange >= 0 ? Colors.green : Colors.red,
                  ),
                ],
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: [
                if (marginOfSafety != null)
                  _InfoChip(
                    icon: Icons.shield_outlined,
                    label:
                        'هامش الأمان: ${marginOfSafety >= 0 ? '+' : ''}${marginOfSafety.toStringAsFixed(1)}%',
                    color: marginOfSafety >= 0 ? Colors.green : Colors.orange,
                  ),
                if (investmentScore != null)
                  _InfoChip(
                    icon: Icons.star_outline_rounded,
                    label: 'التقييم: ${investmentScore.toStringAsFixed(0)}/100',
                    color: investmentScore >= 70
                        ? Colors.green
                        : investmentScore >= 50
                            ? Colors.orange
                            : Colors.red,
                  ),
                if (peRatio != null)
                  _InfoChip(
                    icon: Icons.analytics_outlined,
                    label: 'P/E: ${peRatio.toStringAsFixed(1)}x',
                    color: Colors.blueGrey,
                  ),
                if (expectedRecovery != null)
                  _InfoChip(
                    icon: Icons.rocket_launch_outlined,
                    label:
                        'الارتداد المتوقع: +${expectedRecovery.toStringAsFixed(0)}%',
                    color: Colors.blue,
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.06),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: color.withValues(alpha: 0.15)),
        ),
        child: Column(
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: color.withValues(alpha: 0.7),
              ),
            ),
            const SizedBox(height: 2),
            Text(
              value,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  final IconData icon;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 3),
          Text(
            label,
            style: TextStyle(fontSize: 11, color: color),
          ),
        ],
      ),
    );
  }
}

List<Map<String, dynamic>> _mapsList(Object? value) {
  if (value is! List) return <Map<String, dynamic>>[];
  return value
      .map(
        (item) => item is Map<String, dynamic>
            ? item
            : item is Map
                ? Map<String, dynamic>.from(item)
                : <String, dynamic>{},
      )
      .toList(growable: false);
}

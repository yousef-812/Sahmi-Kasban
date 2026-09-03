import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'report_providers.dart';

class MarketReportScreen extends ConsumerStatefulWidget {
  const MarketReportScreen({required this.reportId, this.preview, super.key});

  final String reportId;
  final MarketReportPreview? preview;

  @override
  ConsumerState<MarketReportScreen> createState() => _MarketReportScreenState();
}

class _MarketReportScreenState extends ConsumerState<MarketReportScreen> {
  MarketReport? _report;
  bool _loading = false;
  bool _locked = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _locked = widget.preview?.unlocked == false;
    if (!_locked) {
      _loadReport();
    }
  }

  Future<void> _loadReport() async {
    if (_loading) {
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final report = await ref
          .read(backendRepositoryProvider)
          .getMarketReport(widget.reportId);
      if (mounted) {
        setState(() {
          _report = report;
          _locked = false;
        });
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() {
          _locked = error.statusCode == 402;
          _error = error.statusCode == 402 ? null : error.message;
        });
      }
    } on Object {
      if (mounted) {
        setState(
          () => _error = 'تعذر عرض التقرير. حدّث التطبيق وحاول مرة أخرى.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _unlock() async {
    if (_loading) {
      return;
    }
    final cost = widget.preview?.unlockCostCoins ?? '1.00';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('فتح تقرير أفضل 10'),
        content: Text(
          'سيتم خصم $cost عملة مرة واحدة فقط. بعد الفتح سيظل التقرير متاحًا لهذا الحساب دون خصم متكرر.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('فتح التقرير'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final execution = await ref
          .read(backendRepositoryProvider)
          .unlockMarketReport(widget.reportId);
      if (!mounted) {
        return;
      }
      setState(() {
        _report = execution.report;
        _locked = false;
      });
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
        ref.invalidate(walletSummaryProvider);
        ref.invalidate(latestReportPreviewProvider);
      } on Object {
        // The purchased report must remain visible if the optional balance refresh fails.
      }
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            execution.chargedPoints == 0
                ? 'التقرير كان مفتوحًا بالفعل ولم يحدث خصم جديد.'
                : 'تم فتح التقرير وخصم ${execution.chargedCoins} عملة.',
          ),
        ),
      );
      if (execution.chargedPoints > 0) {
        await ref
            .read(freePlanInterstitialProvider)
            .recordMeaningfulAction(
              enabled:
                  ref.read(sessionControllerProvider).profile?.adsEnabled ==
                  true,
            );
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } on Object {
      if (mounted) {
        setState(() => _error = 'تعذر فتح التقرير حاليًا. حاول مرة أخرى.');
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isInvestment =
        _report?.reportType == 'investment' ||
        widget.preview?.reportType == 'investment';
    return Scaffold(
      appBar: AppBar(
        title: Text(
          isInvestment ? 'تقرير الاستثمار والقيمة العادلة' : 'تقرير أفضل 10',
        ),
      ),
      body: SafeArea(child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading && _report == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_locked) {
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.lock_rounded, size: 48),
                  const SizedBox(height: 16),
                  Text(
                    'تقرير جلسة ${_formatArabicDate(widget.preview?.targetSessionDate ?? DateTime.now())}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'يحتوي التقرير على ${widget.preview?.itemCount ?? 10} فرص استثمارية وتحليلية مرتبة ومفصلة.',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: _loading ? null : _unlock,
                    icon: const Icon(Icons.lock_open_rounded),
                    label: Text(
                      'فتح التقرير (${widget.preview?.unlockCostCoins ?? '1.00'} عملة)',
                    ),
                  ),
                ],
              ),
            ),
          ),
          const FreePlanNativeAd(),
          if (_error != null) _ErrorCard(message: _error!, retry: _unlock),
        ],
      );
    }

    final report = _report;
    if (report == null) {
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _ErrorCard(
            message: _error ?? 'تعذر تحميل التقرير.',
            retry: _loadReport,
          ),
        ],
      );
    }

    if (report.reportType == 'investment') {
      return _InvestmentReportView(report: report);
    }

    return _ReportTabs(report: report);
  }
}

class _ReportTabGroup {
  const _ReportTabGroup({
    required this.label,
    required this.icon,
    required this.items,
    required this.isExtended,
  });

  final String label;
  final IconData icon;
  final List<MarketReportItem> items;
  final bool isExtended;
}

List<_ReportTabGroup> _buildReportTabGroups(MarketReport report) {
  final topTen = report.items.where((item) => item.rank <= 10).toList();
  final allItems = [...topTen, ...report.extendedItems];
  final groups = <_ReportTabGroup>[
    _ReportTabGroup(
      label: 'أفضل 10',
      icon: Icons.stars_rounded,
      items: topTen,
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'نخبة متوازن',
      icon: Icons.verified_rounded,
      items: _byTier(allItems, 'elite', profile: 'balanced'),
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'نخبة هجومي',
      icon: Icons.rocket_launch_rounded,
      items: _byTier(allItems, 'elite', profile: 'aggressive'),
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'شراء بجودة أعلى',
      icon: Icons.auto_awesome_rounded,
      items: _byTier(allItems, 'conditional_buy_high_quality'),
      isExtended: false,
    ),
    _ReportTabGroup(
      label: 'شراء مشروط',
      icon: Icons.shopping_bag_rounded,
      items: _byTier(allItems, 'conditional_buy'),
      isExtended: true,
    ),
    _ReportTabGroup(
      label: 'مراقبة',
      icon: Icons.visibility_rounded,
      items: _byTier(allItems, 'watch'),
      isExtended: true,
    ),
  ];
  return groups.where((group) => group.items.isNotEmpty).toList();
}

List<MarketReportItem> _byTier(
  List<MarketReportItem> items,
  String tier, {
  String? profile,
}) {
  return items.where((item) {
    final itemTier = _text(item.payload['opportunity_tier']);
    if (itemTier != tier) {
      return false;
    }
    if (profile != null && _text(item.payload['elite_profile']) != profile) {
      return false;
    }
    return true;
  }).toList();
}

class _ReportTabs extends StatelessWidget {
  const _ReportTabs({required this.report});

  final MarketReport report;

  @override
  Widget build(BuildContext context) {
    final groups = _buildReportTabGroups(report);
    return DefaultTabController(
      length: groups.length,
      child: Column(
        children: [
          Flexible(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'الجلسة المستهدفة',
                            style: Theme.of(context).textTheme.labelLarge,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _formatArabicDate(report.targetSessionDate),
                            style: Theme.of(context).textTheme.titleLarge
                                ?.copyWith(fontWeight: FontWeight.w900),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'الترتيب ناتج عن التحليل الآلي ولا يمثل ضمانًا للربح.',
                          ),
                        ],
                      ),
                    ),
                  ),
                  _MarketSummaryCard(summary: report.marketSummary),
                  const FreePlanNativeAd(),
                ],
              ),
            ),
          ),
          Material(
            color: Theme.of(context).colorScheme.surface,
            child: TabBar(
              isScrollable: true,
              tabAlignment: TabAlignment.start,
              tabs: [
                for (final group in groups)
                  Tab(
                    text: group.label == 'أفضل 10'
                        ? group.label
                        : '${group.label} (${group.items.length})',
                    icon: Icon(group.icon),
                  ),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              children: [
                for (final group in groups)
                  ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      for (final item in group.items)
                        if (group.isExtended)
                          _SafeExtendedItemCard(
                            key: ValueKey('ext-${item.ticker}'),
                            item: item,
                          )
                        else
                          _SafeReportItemCard(
                            key: ValueKey('top-${item.ticker}'),
                            item: item,
                          ),
                    ],
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MarketSummaryCard extends StatelessWidget {
  const _MarketSummaryCard({required this.summary});

  final Map<String, dynamic> summary;

  @override
  Widget build(BuildContext context) {
    final analyzed = _integer(summary['analyzed_count']);
    final eligible = _integer(summary['eligible_count']);
    final failed = _integer(summary['failed_count']);
    final averageScore = _number(summary['average_top_score']);
    final signals = _map(summary['signals']);
    final buyCount = _integer(signals['BUY']);
    final watchCount = _integer(signals['WATCH']);
    final title = _text(summary['title']);
    final disclaimer = _text(summary['disclaimer']);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'ملخص السوق',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            if (title.isNotEmpty) ...[const SizedBox(height: 6), Text(title)],
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _MetricChip(label: 'تم تحليلها', value: '$analyzed'),
                _MetricChip(label: 'مؤهلة', value: '$eligible'),
                _MetricChip(label: 'تعذر تحليلها', value: '$failed'),
                _MetricChip(
                  label: 'متوسط الدرجة',
                  value: averageScore.toStringAsFixed(1),
                ),
                _MetricChip(label: 'شراء', value: '$buyCount'),
                _MetricChip(label: 'مراقبة', value: '$watchCount'),
              ],
            ),
            if (disclaimer.isNotEmpty) ...[
              const SizedBox(height: 14),
              Text(disclaimer, style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }
}

class _SafeReportItemCard extends StatelessWidget {
  const _SafeReportItemCard({required this.item, super.key});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    try {
      return _ReportItemCard(item: item);
    } on Object {
      return Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: ListTile(
          leading: CircleAvatar(child: Text('${item.rank}')),
          title: Text(item.ticker, textDirection: TextDirection.ltr),
          subtitle: const Text('تعذر عرض بعض تفاصيل هذا السهم.'),
          trailing: OutlinedButton.icon(
            onPressed: () => context.push('/stocks/${item.ticker}'),
            icon: const Icon(Icons.show_chart_rounded, size: 16),
            label: const Text('معلومات السهم'),
          ),
        ),
      );
    }
  }
}

class _ReportItemCard extends StatelessWidget {
  const _ReportItemCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    final payload = item.payload;
    final analysis = _map(payload['analysis']);
    final tradePlan = _map(analysis['trade_plan']);
    final engines = _map(analysis['engines']);
    final technical = _map(_map(engines['technical'])['details']);
    final risk = _map(_map(engines['risk'])['details']);

    final decision = _text(payload['decision']).isNotEmpty
        ? _text(payload['decision'])
        : _signalLabel(_text(payload['signal']));
    final confidence = _number(payload['confidence']);
    final price = _number(payload['price_at_analysis']);
    final entry = _number(tradePlan['entry']);
    final stop = _number(tradePlan['stop_loss']);
    final target1 = _number(tradePlan['target_1']);
    final target2 = _number(tradePlan['target_2']);
    final rewardRisk = _number(tradePlan['reward_risk_1']);
    final explanation = _text(payload['explanation']);
    final trend = _trendLabel(_text(technical['trend']));
    final rsi = _number(technical['rsi']);
    final volumeRatio = _number(technical['volume_ratio']);
    final riskLevel = _riskLabel(_text(risk['risk_level']));
    final reasons = _collectReasons(engines);

    final sectorQuality = _map(payload['sector_quality']);
    final marketData = _map(payload['market_data']);
    final sectorName = _text(sectorQuality['sector_name']).isNotEmpty
        ? _text(sectorQuality['sector_name'])
        : _text(marketData['sector']);
    final qualityLabel = _text(sectorQuality['quality_label']).isNotEmpty
        ? _text(sectorQuality['quality_label'])
        : (item.score >= 75
              ? 'متفوق على قطاع $sectorName'
              : (item.score >= 50
                    ? 'متوافق مع قطاع $sectorName'
                    : 'أقل من متوسط قطاع $sectorName'));

    final sectorTrendAr = _text(sectorQuality['sector_trend_ar']).isNotEmpty
        ? _text(sectorQuality['sector_trend_ar'])
        : 'صاعد 📈';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${item.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(decision.isEmpty ? 'مراقبة' : decision),
                    ],
                  ),
                ),
                Chip(label: Text('${item.score.toStringAsFixed(1)} / 100')),
              ],
            ),
            const SizedBox(height: 10),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: OutlinedButton.icon(
                onPressed: () => context.push('/stocks/${item.ticker}'),
                icon: const Icon(Icons.show_chart_rounded, size: 18),
                label: const Text('معلومات السهم'),
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _MetricChip(
                  label: 'الثقة',
                  value: '${confidence.toStringAsFixed(1)}%',
                ),
                _MetricChip(label: 'السعر', value: _price(price)),
                _MetricChip(label: 'الاتجاه', value: trend),
                _MetricChip(label: 'المخاطرة', value: riskLevel),
                if (sectorName.isNotEmpty)
                  _MetricChip(label: 'القطاع', value: sectorName),
                _MetricChip(label: 'اتجاه القطاع', value: sectorTrendAr),
              ],
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Theme.of(
                  context,
                ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: Theme.of(
                    context,
                  ).colorScheme.outlineVariant.withValues(alpha: 0.5),
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.pie_chart_outline_rounded,
                    size: 18,
                    color: Colors.amber,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'جودة السهم مقابل القطاع',
                          style: Theme.of(context).textTheme.labelSmall
                              ?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Theme.of(context).colorScheme.outline,
                              ),
                        ),
                        Text(
                          qualityLabel,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            if (entry > 0 || stop > 0 || target1 > 0) ...[
              const SizedBox(height: 14),
              Text(
                'خطة التداول',
                style: Theme.of(
                  context,
                ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              _ValueRow(label: 'الدخول', value: _price(entry)),
              _ValueRow(label: 'وقف الخسارة', value: _price(stop)),
              _ValueRow(label: 'الهدف الأول', value: _price(target1)),
              _ValueRow(label: 'الهدف الثاني', value: _price(target2)),
              _ValueRow(
                label: 'العائد مقابل المخاطرة',
                value: rewardRisk > 0
                    ? '${rewardRisk.toStringAsFixed(1)} : 1'
                    : '—',
              ),
            ],
            if (rsi > 0 || volumeRatio > 0) ...[
              const Divider(height: 24),
              _ValueRow(
                label: 'مؤشر RSI',
                value: rsi > 0 ? rsi.toStringAsFixed(1) : '—',
              ),
              _ValueRow(
                label: 'نسبة الحجم',
                value: volumeRatio > 0 ? volumeRatio.toStringAsFixed(2) : '—',
              ),
            ],
            if (reasons.isNotEmpty) ...[
              const Divider(height: 24),
              Text(
                'أسباب الاختيار',
                style: Theme.of(
                  context,
                ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 6),
              for (final reason in reasons.take(5))
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text('• ${_reasonLabel(reason)}'),
                ),
            ],
            if (explanation.isNotEmpty) ...[
              const Divider(height: 24),
              Text(explanation),
            ],
          ],
        ),
      ),
    );
  }
}

class _SafeExtendedItemCard extends StatelessWidget {
  const _SafeExtendedItemCard({required this.item, super.key});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    try {
      return _ExtendedItemCard(item: item);
    } on Object {
      return Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: ListTile(
          leading: CircleAvatar(child: Text('${item.rank}')),
          title: Text(item.ticker, textDirection: TextDirection.ltr),
          subtitle: const Text('تعذر عرض بعض تفاصيل هذا السهم.'),
          trailing: OutlinedButton.icon(
            onPressed: () => context.push('/stocks/${item.ticker}'),
            icon: const Icon(Icons.show_chart_rounded, size: 16),
            label: const Text('معلومات السهم'),
          ),
        ),
      );
    }
  }
}

class _ExtendedItemCard extends StatelessWidget {
  const _ExtendedItemCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    final payload = item.payload;
    final tier = _text(payload['opportunity_tier']);
    final decision = _text(payload['decision']).isNotEmpty
        ? _text(payload['decision'])
        : _signalLabel(_text(payload['signal']));
    final price = _number(payload['price_at_analysis']);
    final plan = _map(payload['trade_plan']);
    final entry = _number(plan['entry']);
    final stop = _number(plan['stop_loss']);
    final target1 = _number(plan['target_1']);
    final target2 = _number(plan['target_2']);
    final rewardRisk = _number(plan['reward_risk_1']);
    final explanation = _text(payload['explanation']);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${item.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(decision.isEmpty ? 'مراقبة' : decision),
                    ],
                  ),
                ),
                Chip(label: Text('${item.score.toStringAsFixed(1)} / 100')),
              ],
            ),
            const SizedBox(height: 10),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: OutlinedButton.icon(
                onPressed: () => context.push('/stocks/${item.ticker}'),
                icon: const Icon(Icons.show_chart_rounded, size: 18),
                label: const Text('معلومات السهم'),
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (tier.isNotEmpty)
                  _MetricChip(label: 'الدرجة', value: _tierLabel(tier)),
                _MetricChip(label: 'السعر', value: _price(price)),
              ],
            ),
            if (entry > 0 || stop > 0 || target1 > 0) ...[
              const SizedBox(height: 14),
              Text(
                'خطة التداول',
                style: Theme.of(
                  context,
                ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              _ValueRow(label: 'الدخول', value: _price(entry)),
              _ValueRow(label: 'وقف الخسارة', value: _price(stop)),
              _ValueRow(label: 'الهدف الأول', value: _price(target1)),
              _ValueRow(label: 'الهدف الثاني', value: _price(target2)),
              _ValueRow(
                label: 'العائد مقابل المخاطرة',
                value: rewardRisk > 0
                    ? '${rewardRisk.toStringAsFixed(1)} : 1'
                    : '—',
              ),
            ],
            if (explanation.isNotEmpty) ...[
              const Divider(height: 24),
              Text(explanation),
            ],
          ],
        ),
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
    return Chip(label: Text('$label: $value'));
  }
}

class _ValueRow extends StatelessWidget {
  const _ValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Expanded(child: Text(label)),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message, required this.retry});

  final String message;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: retry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

String _formatArabicDate(DateTime value) {
  const weekdays = <String>[
    'الاثنين',
    'الثلاثاء',
    'الأربعاء',
    'الخميس',
    'الجمعة',
    'السبت',
    'الأحد',
  ];
  const months = <String>[
    'يناير',
    'فبراير',
    'مارس',
    'أبريل',
    'مايو',
    'يونيو',
    'يوليو',
    'أغسطس',
    'سبتمبر',
    'أكتوبر',
    'نوفمبر',
    'ديسمبر',
  ];
  final local = value.toLocal();
  return '${weekdays[local.weekday - 1]} ${local.day} ${months[local.month - 1]} ${local.year}';
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

String _text(Object? value) => value is String ? value.trim() : '';

double _number(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse('$value') ?? 0;
}

List<dynamic> _list(Object? value) => value is List ? value : const <dynamic>[];

int _integer(Object? value) => _number(value).round();

String _price(double value) => value > 0 ? value.toStringAsFixed(2) : '—';

String _signalLabel(String value) {
  return switch (value.toUpperCase()) {
    'BUY' => 'فرصة شراء مشروطة',
    'WATCH' => 'للمراقبة',
    'AVOID' => 'تجنب حاليًا',
    _ => value,
  };
}

String _tierLabel(String tier) {
  return switch (tier) {
    'elite' => 'نخبة',
    'elite_balanced' => 'نخبة متوازن',
    'elite_aggressive' => 'نخبة هجومي',
    'conditional_buy_high_quality' => 'شراء بجودة أعلى',
    'conditional_buy' => 'شراء مشروط',
    'watch' => 'مراقبة',
    _ => tier,
  };
}

String _trendLabel(String value) {
  return switch (value.toLowerCase()) {
    'uptrend' || 'bullish' || 'weak_bullish' => 'صاعد',
    'downtrend' || 'bearish' || 'weak_bearish' => 'هابط',
    'sideways' || 'neutral' => 'عرضي',
    _ => value.isEmpty ? 'غير محدد' : value,
  };
}

String _riskLabel(String value) {
  return switch (value.toLowerCase()) {
    'low' => 'منخفضة',
    'medium' => 'متوسطة',
    'high' => 'مرتفعة',
    _ => value.isEmpty ? 'غير محددة' : value,
  };
}

List<String> _collectReasons(Map<String, dynamic> engines) {
  final result = <String>[];
  for (final value in engines.values) {
    final engine = _map(value);
    final reasons = engine['reasons'];
    if (reasons is List) {
      result.addAll(
        reasons.whereType<String>().where((reason) => reason.trim().isNotEmpty),
      );
    }
  }
  return result;
}

String _reasonLabel(String reason) {
  const labels = <String, String>{
    'Price above SMA20': 'السعر أعلى من متوسط 20 جلسة',
    'Price above SMA50': 'السعر أعلى من متوسط 50 جلسة',
    'SMA20 above SMA50': 'متوسط 20 أعلى من متوسط 50',
    'Long-term trend positive': 'الاتجاه طويل الأجل إيجابي',
    'MACD bullish': 'مؤشر MACD إيجابي',
    'Timeframe alignment: bullish': 'الأطر الزمنية متوافقة على اتجاه صاعد',
  };
  return labels[reason] ?? reason;
}

class _InvestmentReportView extends StatelessWidget {
  const _InvestmentReportView({required this.report});

  final MarketReport report;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _InvestmentSummaryCard(summary: report.marketSummary),
        const SizedBox(height: 12),
        Text(
          'أفضل الشركات المؤهلة استثمارياً (${report.items.length})',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
        const SizedBox(height: 10),
        for (final item in report.items)
          Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: _InvestmentStockCard(item: item),
          ),
        const FreePlanNativeAd(),
        const SizedBox(height: 24),
      ],
    );
  }
}

class _InvestmentSummaryCard extends StatelessWidget {
  const _InvestmentSummaryCard({required this.summary});

  final Map<String, dynamic> summary;

  @override
  Widget build(BuildContext context) {
    final title = _text(summary['title']);
    final description = _text(summary['description']);
    final horizon = _text(summary['horizon']);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.account_balance_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title.isEmpty ? 'تقرير الاستثمار والقيمة العادلة' : title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
              ],
            ),
            if (description.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(description, style: Theme.of(context).textTheme.bodySmall),
            ],
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _MetricChip(
                  label: 'الأفق الزمني',
                  value: horizon.isEmpty ? '6 - 36 شهراً' : horizon,
                ),
                const _MetricChip(
                  label: 'المصدر',
                  value: 'TradingView المالية',
                ),
                const _MetricChip(
                  label: 'نوع التحليل',
                  value: 'قيمة مالية وأرباح',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InvestmentStockCard extends StatelessWidget {
  const _InvestmentStockCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    final payload = item.payload;
    final ticker = item.ticker;
    final rawCompanyName = _text(payload['company_name']);
    final companyName = rawCompanyName.isEmpty ? ticker : rawCompanyName;
    final sector = _text(payload['sector']);
    final currentPrice = _number(payload['current_price']);
    final fairValue = payload['fair_value'] != null
        ? _number(payload['fair_value'])
        : null;
    final marginOfSafety = payload['margin_of_safety_pct'] != null
        ? _number(payload['margin_of_safety_pct'])
        : null;
    final peRatio = payload['pe_ratio'] != null
        ? _number(payload['pe_ratio'])
        : null;
    final divYield = payload['dividend_yield_pct'] != null
        ? _number(payload['dividend_yield_pct'])
        : null;
    final roe = payload['roe_pct'] != null ? _number(payload['roe_pct']) : null;
    final category = _text(payload['investment_category']);
    final strengths = _list(payload['strengths']);

    final (categoryLabel, categoryColor, categoryIcon) = switch (category) {
      'dividend' => ('سهم توزيعات كاش', Colors.teal, Icons.payments_rounded),
      'growth' => ('سهم نمو واعد', Colors.blue, Icons.trending_up_rounded),
      'value' => ('سهم قيمة وهامش أمان', Colors.purple, Icons.security_rounded),
      _ => ('سهم متوازن', Colors.indigo, Icons.balance_rounded),
    };

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 18,
                  backgroundColor: Theme.of(
                    context,
                  ).colorScheme.primaryContainer,
                  child: Text(
                    '#${item.rank}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ticker,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(
                        companyName,
                        style: Theme.of(context).textTheme.bodySmall,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${item.score.toStringAsFixed(1)} / 100',
                    style: const TextStyle(
                      fontWeight: FontWeight.w900,
                      color: Colors.green,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(
                  avatar: Icon(categoryIcon, size: 16, color: categoryColor),
                  label: Text(
                    categoryLabel,
                    style: TextStyle(
                      color: categoryColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  backgroundColor: categoryColor.withValues(alpha: 0.1),
                ),
                if (sector.isNotEmpty) Chip(label: Text(sector)),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(
                  context,
                ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: Theme.of(context).dividerColor.withValues(alpha: 0.2),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      const Text(
                        'السعر الحالي',
                        style: TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${currentPrice.toStringAsFixed(2)} ج',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                    ],
                  ),
                  if (fairValue != null)
                    Column(
                      children: [
                        const Text(
                          'القيمة العادلة',
                          style: TextStyle(fontSize: 11, color: Colors.grey),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${fairValue.toStringAsFixed(2)} ج',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                            color: Colors.blue,
                          ),
                        ),
                      ],
                    ),
                  if (marginOfSafety != null)
                    Column(
                      children: [
                        const Text(
                          'هامش الأمان',
                          style: TextStyle(fontSize: 11, color: Colors.grey),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${marginOfSafety >= 0 ? '+' : ''}${marginOfSafety.toStringAsFixed(1)}%',
                          style: TextStyle(
                            fontWeight: FontWeight.w900,
                            fontSize: 15,
                            color: marginOfSafety >= 0
                                ? Colors.green
                                : Colors.red,
                          ),
                        ),
                      ],
                    ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                if (peRatio != null)
                  Expanded(
                    child: _InvestmentMetricTile(
                      label: 'مكرر الربحية',
                      value: '${peRatio.toStringAsFixed(1)}x',
                    ),
                  ),
                if (divYield != null)
                  Expanded(
                    child: _InvestmentMetricTile(
                      label: 'عائد التوزيعات',
                      value: '${divYield.toStringAsFixed(1)}%',
                      highlight: divYield >= 7.0,
                    ),
                  ),
                if (roe != null)
                  Expanded(
                    child: _InvestmentMetricTile(
                      label: 'عائد حقوق الملكية',
                      value: '${roe.toStringAsFixed(1)}%',
                    ),
                  ),
              ],
            ),
            if (strengths.isNotEmpty) ...[
              const SizedBox(height: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final s in strengths.take(2))
                    Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.check_circle_rounded,
                            size: 15,
                            color: Colors.green,
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              _text(s),
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ],
            const SizedBox(height: 12),
            FilledButton.tonalIcon(
              onPressed: () => context.push('/stocks/$ticker'),
              icon: const Icon(Icons.show_chart_rounded, size: 18),
              label: const Text('معلومات وتحليل السهم'),
            ),
          ],
        ),
      ),
    );
  }
}

class _InvestmentMetricTile extends StatelessWidget {
  const _InvestmentMetricTile({
    required this.label,
    required this.value,
    this.highlight = false,
  });

  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 3),
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
      decoration: BoxDecoration(
        color: highlight
            ? Colors.green.withValues(alpha: 0.1)
            : Theme.of(
                context,
              ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 10, color: Colors.grey),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 13,
              color: highlight ? Colors.green : null,
            ),
          ),
        ],
      ),
    );
  }
}

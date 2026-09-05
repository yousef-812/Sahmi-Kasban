import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'stock_analysis_report.dart';

class StockAnalysisTab extends ConsumerStatefulWidget {
  const StockAnalysisTab({super.key});

  @override
  ConsumerState<StockAnalysisTab> createState() => _StockAnalysisTabState();
}

class _StockAnalysisTabState extends ConsumerState<StockAnalysisTab> {
  final _queryController = TextEditingController();
  Timer? _searchDebounce;
  int _searchRevision = 0;
  List<MarketInstrument> _results = const [];
  MarketInstrument? _selected;
  StockAnalysisResult? _analysis;
  StockInvestmentAnalysis? _investmentAnalysis;
  bool _searching = false;
  bool _loadingSaved = false;
  bool _analyzing = false;
  bool _analyzingInvestment = false;
  String? _error;

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _queryController.dispose();
    super.dispose();
  }

  void _onQueryChanged(String value) {
    _searchDebounce?.cancel();
    final normalizedQuery = value.trim().toUpperCase();
    final revision = ++_searchRevision;
    setState(() {
      _selected = null;
      _results = const [];
      _error = null;
      _analysis = null;
      _investmentAnalysis = null;
      _loadingSaved = false;
      _searching = normalizedQuery.isNotEmpty;
    });
    if (normalizedQuery.isEmpty) {
      return;
    }
    _searchDebounce = Timer(
      const Duration(milliseconds: 350),
      () => _search(query: normalizedQuery, revision: revision),
    );
  }

  Future<void> _search({String? query, int? revision}) async {
    _searchDebounce?.cancel();
    final normalizedQuery = (query ?? _queryController.text)
        .trim()
        .toUpperCase();
    final requestRevision = revision ?? ++_searchRevision;
    if (normalizedQuery.isEmpty) {
      if (mounted) {
        setState(() {
          _results = const [];
          _selected = null;
          _analysis = null;
          _searching = false;
          _error = 'اكتب رمز السهم أو اسم الشركة أولًا.';
        });
      }
      return;
    }
    if (mounted) {
      setState(() {
        _searching = true;
        _error = null;
        _analysis = null;
      });
    }
    try {
      final results = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(normalizedQuery);
      if (!mounted || requestRevision != _searchRevision) {
        return;
      }
      MarketInstrument? exactMatch;
      for (final instrument in results) {
        if (instrument.ticker == normalizedQuery) {
          exactMatch = instrument;
          break;
        }
      }
      exactMatch ??= results.length == 1 ? results.first : null;
      setState(() {
        _results = results;
        _selected = exactMatch;
        _error = results.isEmpty
            ? 'لم نعثر على سهم مصري مطابق في كتالوج السوق.'
            : null;
      });
      if (exactMatch != null) {
        unawaited(_loadSavedAnalysis(exactMatch, requestRevision));
      }
    } on ApiException catch (error) {
      if (mounted && requestRevision == _searchRevision) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted && requestRevision == _searchRevision) {
        setState(() => _searching = false);
      }
    }
  }

  void _selectInstrument(MarketInstrument instrument) {
    final revision = ++_searchRevision;
    setState(() {
      _selected = instrument;
      _analysis = null;
      _investmentAnalysis = null;
      _error = null;
    });
    unawaited(_loadSavedAnalysis(instrument, revision));
  }

  Future<void> _loadSavedAnalysis(
    MarketInstrument instrument,
    int revision,
  ) async {
    if (mounted) {
      setState(() => _loadingSaved = true);
    }
    try {
      final saved = await ref
          .read(backendRepositoryProvider)
          .getLatestOwnedStockAnalysis(instrument.ticker);
      if (!mounted || revision != _searchRevision) {
        return;
      }
      if (_selected?.ticker == instrument.ticker) {
        setState(() => _analysis = saved);
      }
    } on ApiException {
      // A saved analysis is optional; the user can still request a fresh one.
    } finally {
      if (mounted && revision == _searchRevision) {
        setState(() => _loadingSaved = false);
      }
    }
  }

  Future<void> _analyze() async {
    final instrument = _selected;
    if (instrument == null || _analyzing) {
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('تحليل ${instrument.ticker}'),
        content: const Text(
          'تكلفة التحليل بالبيانات الجديدة 0.5 عملة. التحليل المحفوظ لنفس الحساب ونفس بيانات السوق يُعرض دون خصم جديد.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('متابعة'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    setState(() {
      _analyzing = true;
      _error = null;
    });
    try {
      final analysis = await ref
          .read(backendRepositoryProvider)
          .analyzeStock(instrument.ticker);
      if (mounted) {
        setState(() => _analysis = analysis);
      }
      ref.invalidate(walletSummaryProvider);
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      } on Object {
        // The completed analysis must remain visible even if the optional
        // profile refresh fails. Wallet data will retry through its provider.
      }
      if (mounted) {
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
    } finally {
      if (mounted) {
        setState(() => _analyzing = false);
      }
    }
  }

  Future<void> _analyzeInvestment() async {
    final instrument = _selected;
    if (instrument == null || _analyzingInvestment) {
      return;
    }
    setState(() {
      _analyzingInvestment = true;
      _error = null;
    });
    try {
      final inv = await ref
          .read(backendRepositoryProvider)
          .getStockInvestmentAnalysis(instrument.ticker);
      if (mounted) {
        setState(() => _investmentAnalysis = inv);
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
    } catch (_) {
      if (mounted) {
        setState(
          () => _error = 'تعذر إجراء التحليل الاستثماري لهذا السهم حالياً.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _analyzingInvestment = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'تحليل سهم من البورصة المصرية',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 8),
                const Text(
                  'اكتب رمز السهم أو اسم الشركة، وستظهر النتائج تلقائيًا.',
                ),
                const SizedBox(height: 18),
                TextField(
                  controller: _queryController,
                  textDirection: TextDirection.ltr,
                  textCapitalization: TextCapitalization.characters,
                  decoration: InputDecoration(
                    labelText: 'رمز السهم أو اسم الشركة',
                    hintText: 'COMI',
                    prefixIcon: IconButton(
                      tooltip: 'تحديث البحث',
                      onPressed: _searching ? null : () => _search(),
                      icon: _searching
                          ? const SizedBox.square(
                              dimension: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.search_rounded),
                    ),
                  ),
                  onChanged: _onQueryChanged,
                  onSubmitted: (_) => _search(),
                ),
                if (_results.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    '${_results.length} نتيجة',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 4),
                  for (final instrument in _results)
                    Builder(
                      builder: (context) {
                        final selected = _selected?.ticker == instrument.ticker;
                        return Card(
                          color: selected
                              ? Theme.of(context).colorScheme.secondaryContainer
                              : null,
                          child: ListTile(
                            onTap: () => _selectInstrument(instrument),
                            leading: Icon(
                              selected
                                  ? Icons.radio_button_checked_rounded
                                  : Icons.radio_button_unchecked_rounded,
                            ),
                            title: Text(
                              instrument.ticker,
                              textDirection: TextDirection.ltr,
                            ),
                            subtitle: Text(
                              instrument.description.isEmpty
                                  ? '${instrument.exchange} — ${instrument.providerSymbol}'
                                  : '${instrument.description} • ${instrument.exchange}',
                              textDirection: instrument.description.isEmpty
                                  ? TextDirection.ltr
                                  : TextDirection.rtl,
                            ),
                          ),
                        );
                      },
                    ),
                ],
                if (_loadingSaved) ...[
                  const SizedBox(height: 10),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox.square(
                        dimension: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      SizedBox(width: 8),
                      Text('جاري البحث عن آخر تحليل محفوظ للحساب...'),
                    ],
                  ),
                ],
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 8),
                Text(
                  _selected == null
                      ? 'اختر سهمًا من نتائج البحث أولاً للبدء في التحليل أو المقارنة:'
                      : 'خيارات التحليل والمقارنة لـ (${_selected!.ticker}):',
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.icon(
                        onPressed:
                            _selected == null ||
                                _analyzing ||
                                _analyzingInvestment
                            ? null
                            : () {
                                setState(() => _investmentAnalysis = null);
                                _analyze();
                              },
                        icon: _analyzing
                            ? const SizedBox.square(
                                dimension: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.bolt_rounded),
                        label: const Text('تحليل كسهم مضاربة'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: FilledButton.tonalIcon(
                        onPressed:
                            _selected == null ||
                                _analyzing ||
                                _analyzingInvestment
                            ? null
                            : () {
                                setState(() => _analysis = null);
                                _analyzeInvestment();
                              },
                        icon: _analyzingInvestment
                            ? const SizedBox.square(
                                dimension: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.account_balance_rounded),
                        label: const Text('تحليل كسهم استثماري'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _analyzing || _analyzingInvestment
                            ? null
                            : () => context.push('/market/compare?mode=swing'),
                        icon: const Icon(Icons.compare_arrows_rounded),
                        label: const Text('مقارنة أسهم مضاربة'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _analyzing || _analyzingInvestment
                            ? null
                            : () => context.push(
                                '/market/compare?mode=investment',
                              ),
                        icon: const Icon(Icons.analytics_outlined),
                        label: const Text('مقارنة أسهم استثمارية'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        const FreePlanNativeAd(),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Card(
            color: Theme.of(context).colorScheme.errorContainer,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(_error!, textAlign: TextAlign.center),
            ),
          ),
        ],
        if (_analysis case final analysis?) ...[
          const SizedBox(height: 16),
          StockAnalysisReport(analysis: analysis),
          const SizedBox(height: 12),
          FilledButton.tonalIcon(
            onPressed: () => context.push('/stocks/${analysis.ticker}'),
            icon: const Icon(Icons.candlestick_chart_rounded, size: 20),
            label: const Text(
              'معلومات وشارت السهم',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
        if (_investmentAnalysis case final inv?) ...[
          const SizedBox(height: 16),
          _StockInvestmentAnalysisView(analysis: inv),
        ],
      ],
    );
  }
}

class _StockInvestmentAnalysisView extends StatelessWidget {
  const _StockInvestmentAnalysisView({required this.analysis});

  final StockInvestmentAnalysis analysis;

  static String _formatLargeAmount(double? value) {
    if (value == null || value == 0) return '—';
    if (value >= 1e9) {
      return '${(value / 1e9).toStringAsFixed(2)} مليار ج.م';
    }
    if (value >= 1e6) {
      return '${(value / 1e6).toStringAsFixed(2)} مليون ج.م';
    }
    return '${value.toStringAsFixed(2)} ج.م';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isValue = analysis.investmentCategory == 'value';
    final isDividend = analysis.investmentCategory == 'dividend';
    final (categoryTitle, categoryColor, categoryIcon) = isValue
        ? ('سهم قيمة وهامش أمان', Colors.purple, Icons.security_rounded)
        : isDividend
        ? ('سهم توزيعات نقدية كاش', Colors.teal, Icons.payments_rounded)
        : ('سهم نمو وأرباح واعدة', Colors.blue, Icons.trending_up_rounded);

    final margin = analysis.marginOfSafetyPct;
    final isPositiveMargin = margin != null && margin > 0;
    final targetPrice = analysis.expectedTargetPrice ?? analysis.fairValue;
    final timeframe = analysis.expectedTimeframe ?? '6 - 12 شهراً';
    final expectedReturn = analysis.expectedReturnPct ?? margin;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 1. بطاقة القرار والتوصية الاستثمارية
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            analysis.ticker,
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.w900,
                            ),
                            textDirection: TextDirection.ltr,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${analysis.companyName} • ${analysis.sector}',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: categoryColor.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: categoryColor.withValues(alpha: 0.4),
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(categoryIcon, size: 14, color: categoryColor),
                          const SizedBox(width: 4),
                          Text(
                            categoryTitle,
                            style: TextStyle(
                              color: categoryColor,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Column(
                        children: [
                          Text(
                            'التقييم الاستثماري',
                            style: theme.textTheme.bodySmall,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${analysis.investmentScore.toStringAsFixed(1)} / 100',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w900,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        height: 36,
                        width: 1,
                        color: theme.dividerColor,
                      ),
                      Column(
                        children: [
                          Text(
                            'السعر الحالي',
                            style: theme.textTheme.bodySmall,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${analysis.currentPrice.toStringAsFixed(2)} ج.م',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        height: 36,
                        width: 1,
                        color: theme.dividerColor,
                      ),
                      Column(
                        children: [
                          Text(
                            'التوصية الاستثمارية',
                            style: theme.textTheme.bodySmall,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            analysis.recommendation ?? 'شراء استثماري',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: analysis.investmentScore >= 65
                                  ? Colors.green
                                  : Colors.orange,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                if (analysis.valuationStatus != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: isPositiveMargin
                          ? Colors.green.withValues(alpha: 0.1)
                          : Colors.orange.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isPositiveMargin
                            ? Colors.green.withValues(alpha: 0.3)
                            : Colors.orange.withValues(alpha: 0.3),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          isPositiveMargin
                              ? Icons.check_circle_outline_rounded
                              : Icons.info_outline_rounded,
                          size: 18,
                          color: isPositiveMargin
                              ? Colors.green
                              : Colors.orange,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            analysis.valuationStatus!,
                            style: TextStyle(
                              color: isPositiveMargin
                                  ? Colors.green.shade800
                                  : Colors.orange.shade900,
                              fontWeight: FontWeight.w600,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // 2. بطاقة السعر المستهدف والأفق الزمني والقيمة العادلة
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.flag_rounded,
                      color: theme.colorScheme.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'القيمة المتوقعة والأفق الزمني',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.green.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: Colors.green.withValues(alpha: 0.25),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'القيمة المتوقعة (المستهدف)',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: Colors.green.shade800,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              targetPrice != null
                                  ? '${targetPrice.toStringAsFixed(2)} ج.م'
                                  : '—',
                              style: theme.textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.w900,
                                color: Colors.green.shade800,
                              ),
                            ),
                            if (expectedReturn != null) ...[
                              const SizedBox(height: 2),
                              Text(
                                '${expectedReturn >= 0 ? '+' : ''}${expectedReturn.toStringAsFixed(1)}% عائد متوقع',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: expectedReturn >= 0
                                      ? Colors.green.shade700
                                      : Colors.red,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.schedule_rounded, size: 14),
                                const SizedBox(width: 4),
                                Text(
                                  'المدة المتوقعة',
                                  style: theme.textTheme.bodySmall?.copyWith(
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              timeframe,
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: theme.colorScheme.primary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'استثمار استراتيجي',
                              style: theme.textTheme.bodySmall?.copyWith(
                                fontSize: 11,
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                if (margin != null) ...[
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'هامش الأمان الحالي: ${margin >= 0 ? '+' : ''}${margin.toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: isPositiveMargin ? Colors.green : Colors.red,
                        ),
                      ),
                      Text(
                        isPositiveMargin
                            ? 'أقل من القيمة العادلة'
                            : 'أعلى من القيمة العادلة',
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  LinearProgressIndicator(
                    value: isPositiveMargin
                        ? (margin / 100.0).clamp(0.0, 1.0)
                        : 0.1,
                    color: isPositiveMargin ? Colors.green : Colors.orange,
                    backgroundColor: theme.colorScheme.surfaceContainerHighest,
                    minHeight: 6,
                    borderRadius: BorderRadius.circular(3),
                  ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // 3. شبكة المؤشرات المالية والأساسية الكاملة
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.query_stats_rounded,
                      color: theme.colorScheme.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'المؤشرات المالية والأساسية',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _InvestmentMetricChip(
                      label: 'مكرر الربحية P/E',
                      value: analysis.peRatio != null
                          ? '${analysis.peRatio!.toStringAsFixed(1)}x'
                          : '—',
                      isPositive:
                          analysis.peRatio != null && analysis.peRatio! <= 10,
                    ),
                    _InvestmentMetricChip(
                      label: 'مضاعف القيمة الدفترية P/B',
                      value: analysis.pbRatio != null
                          ? '${analysis.pbRatio!.toStringAsFixed(1)}x'
                          : '—',
                    ),
                    _InvestmentMetricChip(
                      label: 'عائد التوزيعات النقدية',
                      value: analysis.dividendYieldPct != null
                          ? '${analysis.dividendYieldPct!.toStringAsFixed(1)}%'
                          : '—',
                      isPositive: (analysis.dividendYieldPct ?? 0) >= 5,
                      isHighlight: (analysis.dividendYieldPct ?? 0) >= 7,
                    ),
                    _InvestmentMetricChip(
                      label: 'العائد على حقوق الملكية ROE',
                      value: analysis.roePct != null
                          ? '${analysis.roePct!.toStringAsFixed(1)}%'
                          : '—',
                      isPositive: (analysis.roePct ?? 0) >= 15,
                    ),
                    _InvestmentMetricChip(
                      label: 'ربحية السهم (EPS)',
                      value: analysis.eps != null
                          ? '${analysis.eps!.toStringAsFixed(2)} ج.م'
                          : '—',
                    ),
                    _InvestmentMetricChip(
                      label: 'القيمة السوقية',
                      value: _formatLargeAmount(analysis.marketCap),
                    ),
                    _InvestmentMetricChip(
                      label: 'صافي الأرباح السنوية',
                      value: _formatLargeAmount(analysis.netIncome),
                      isPositive: (analysis.netIncome ?? 0) > 0,
                    ),
                    _InvestmentMetricChip(
                      label: 'إجمالي الديون',
                      value: _formatLargeAmount(analysis.totalDebt),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // 4. نقاط القوة الاستثمارية والمحفزات
        if (analysis.strengths.isNotEmpty) ...[
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.check_circle_rounded,
                        color: Colors.green,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'نقاط القوة والمحفزات الاستثمارية',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  for (final s in analysis.strengths)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.check_rounded,
                            size: 16,
                            color: Colors.green,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              s,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                height: 1.3,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
        ],

        // 5. المخاطر وجوانب الحذر
        if (analysis.risks.isNotEmpty) ...[
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.warning_amber_rounded,
                        color: Colors.orange,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'المخاطر والتحديات الواجب متابعتها',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  for (final r in analysis.risks)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.arrow_left_rounded,
                            size: 18,
                            color: Colors.orange,
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              r,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                height: 1.3,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
        ],

        // 6. إرشادات وخطة الاستثمار للمستثمر
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline_rounded,
                      color: theme.colorScheme.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'إرشادات استراتيجية الاستثمار',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  '• أسلوب الدخول المقترح: الشراء المتدرج على دفعات سعرية (DCA) لتقليل متوسط تكلفة الشراء.\n'
                  '• أفق الاحتفاظ: ينصح بالاحتفاظ طوال الأفق الزمني المستهدف ($timeframe) لجني ثمار النمو أو التوزيعات.\n'
                  '• إعادة استثمار الأرباح: تدوير التوزيعات النقدية يسهم في تعظيم العائد التراكمي للمحفظة على المدى الطويل.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    height: 1.6,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 14),

        // 7. زر معلومات وشارت السهم
        FilledButton.tonalIcon(
          onPressed: () => context.push('/stocks/${analysis.ticker}'),
          icon: const Icon(Icons.candlestick_chart_rounded, size: 20),
          label: const Text(
            'معلومات وشارت السهم',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 16),
      ],
    );
  }
}

class _InvestmentMetricChip extends StatelessWidget {
  const _InvestmentMetricChip({
    required this.label,
    required this.value,
    this.isHighlight = false,
    this.isPositive = false,
  });

  final String label;
  final String value;
  final bool isHighlight;
  final bool isPositive;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isHighlight
            ? theme.colorScheme.primaryContainer.withValues(alpha: 0.5)
            : theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(10),
        border: isHighlight
            ? Border.all(
                color: theme.colorScheme.primary.withValues(alpha: 0.4),
              )
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              fontSize: 11,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: isPositive ? Colors.green.shade700 : null,
            ),
            textDirection: TextDirection.ltr,
          ),
        ],
      ),
    );
  }
}

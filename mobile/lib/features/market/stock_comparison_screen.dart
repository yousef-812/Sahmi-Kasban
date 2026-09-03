import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'stock_comparison_models.dart';
import 'stock_comparison_repository.dart';

class StockComparisonScreen extends ConsumerStatefulWidget {
  const StockComparisonScreen({super.key, this.initialMode});

  final String? initialMode;

  @override
  ConsumerState<StockComparisonScreen> createState() =>
      _StockComparisonScreenState();
}

class _StockComparisonScreenState extends ConsumerState<StockComparisonScreen> {
  final _queryController = TextEditingController();
  late String _mode;
  Timer? _debounce;
  int _searchRevision = 0;
  List<MarketInstrument> _results = const [];
  final List<MarketInstrument> _selected = [];
  bool _searching = false;
  bool _comparing = false;
  bool _comparingInvestment = false;
  String? _error;
  String? _requestKey;
  StockComparisonResult? _result;
  StockInvestmentComparisonResult? _investmentResult;

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode == 'investment' ? 'investment' : 'swing';
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _queryController.dispose();
    super.dispose();
  }

  int get _maxStocks {
    final plan =
        ref.read(sessionControllerProvider).profile?.planCode ?? 'free';
    return switch (plan) {
      'basic' => 2,
      'advanced' => 3,
      'pro' => 5,
      _ => 3,
    };
  }

  void _onQueryChanged(String value) {
    _debounce?.cancel();
    final query = value.trim().toUpperCase();
    final revision = ++_searchRevision;
    setState(() {
      _results = const [];
      _error = null;
      _searching = query.isNotEmpty;
    });
    if (query.isEmpty) {
      return;
    }
    _debounce = Timer(
      const Duration(milliseconds: 350),
      () => _search(query, revision),
    );
  }

  Future<void> _search(String query, int revision) async {
    try {
      final items = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(query, limit: 20);
      if (!mounted || revision != _searchRevision) {
        return;
      }
      final selectedTickers = _selected.map((item) => item.ticker).toSet();
      setState(() {
        _results = items
            .where((item) => !selectedTickers.contains(item.ticker))
            .toList(growable: false);
        _error = items.isEmpty ? 'لم نعثر على سهم مطابق.' : null;
      });
    } on ApiException catch (error) {
      if (mounted && revision == _searchRevision) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted && revision == _searchRevision) {
        setState(() => _searching = false);
      }
    }
  }

  void _select(MarketInstrument instrument) {
    if (_selected.length >= _maxStocks) {
      setState(() => _error = 'خطتك تسمح بمقارنة حتى $_maxStocks أسهم.');
      return;
    }
    setState(() {
      _selected.add(instrument);
      _results = const [];
      _queryController.clear();
      _error = null;
      _result = null;
      _requestKey = null;
    });
  }

  void _remove(MarketInstrument instrument) {
    setState(() {
      _selected.removeWhere((item) => item.ticker == instrument.ticker);
      _result = null;
      _requestKey = null;
      _error = null;
    });
  }

  String _newRequestKey() {
    final random = Random.secure();
    final suffix = List<int>.generate(
      12,
      (_) => random.nextInt(36),
    ).map((value) => value.toRadixString(36)).join();
    return 'comparison_${DateTime.now().microsecondsSinceEpoch}_$suffix';
  }

  Future<void> _compare() async {
    if (_selected.length < 2 || _comparing) {
      return;
    }
    final profile = ref.read(sessionControllerProvider).profile;
    final planCode = profile?.planCode ?? 'free';
    final paidAllowance = planCode != 'free';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تأكيد مقارنة الأسهم'),
        content: Text(
          paidAllowance
              ? 'ستُستخدم المقارنات الشهرية المتضمنة في خطتك أولًا. أي سهم لا تملك تحليله الحالي قد يكلف 0.5 عملة.'
              : 'تكلفة المقارنة 0.5 عملة، بالإضافة إلى 0.5 عملة لكل سهم لا تملك تحليله الحالي. الأسهم المحللة والمحفوظة لا تُخصم مرة أخرى.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('ابدأ المقارنة'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }

    final requestKey = _requestKey ?? _newRequestKey();
    _requestKey = requestKey;
    setState(() {
      _comparing = true;
      _error = null;
    });
    try {
      final result = await ref
          .read(stockComparisonRepositoryProvider)
          .compare(
            requestKey: requestKey,
            tickers: _selected
                .map((item) => item.ticker)
                .toList(growable: false),
          );
      if (!mounted) {
        return;
      }
      setState(() => _result = result);
      ref.invalidate(walletSummaryProvider);
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      } on Object {
        // The comparison remains visible if the optional wallet refresh fails.
      }
      if (!mounted) {
        return;
      }
      await ref
          .read(freePlanInterstitialProvider)
          .recordMeaningfulAction(enabled: profile?.adsEnabled == true);
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _comparing = false);
      }
    }
  }

  Future<void> _compareInvestment() async {
    if (_selected.length < 2 || _comparingInvestment) {
      return;
    }
    setState(() {
      _comparingInvestment = true;
      _error = null;
    });
    try {
      final res = await ref
          .read(backendRepositoryProvider)
          .compareStocksInvestment(
            _selected.map((item) => item.ticker).toList(),
          );
      if (!mounted) return;
      setState(() => _investmentResult = res);
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } catch (_) {
      if (mounted) {
        setState(() => _error = 'تعذر مقارنة الأسهم استثمارياً حالياً.');
      }
    } finally {
      if (mounted) {
        setState(() => _comparingInvestment = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final planCode =
        ref.watch(sessionControllerProvider).profile?.planCode ?? 'free';
    final isLoading = _mode == 'swing' ? _comparing : _comparingInvestment;

    return Scaffold(
      appBar: AppBar(title: const Text('مقارنة الأسهم')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'swing',
                  icon: Icon(Icons.bolt_rounded),
                  label: Text('مقارنة المضاربة'),
                ),
                ButtonSegment(
                  value: 'investment',
                  icon: Icon(Icons.account_balance_rounded),
                  label: Text('مقارنة الاستثمار'),
                ),
              ],
              selected: {_mode},
              onSelectionChanged: (set) {
                setState(() {
                  _mode = set.first;
                  _error = null;
                });
              },
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'اختر من سهمين إلى $_maxStocks أسهم',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _mode == 'swing'
                          ? (planCode == 'free'
                                ? 'المقارنة الفنية تكلف 0.5 عملة، والتحليلات المحفوظة لا تُخصم مرة أخرى.'
                                : 'يتم استخدام المقارنات الشهرية المتضمنة في خطتك قبل الخصم.')
                          : 'مقارنة استثمارية شاملة للقيمة العادلة، مكررات الربحية، وعوائد التوزيعات.',
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _queryController,
                      textDirection: TextDirection.ltr,
                      textCapitalization: TextCapitalization.characters,
                      decoration: InputDecoration(
                        labelText: 'ابحث بالرمز أو اسم الشركة',
                        hintText: 'COMI',
                        prefixIcon: _searching
                            ? const Padding(
                                padding: EdgeInsets.all(14),
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.search_rounded),
                      ),
                      onChanged: _onQueryChanged,
                    ),
                    if (_results.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      for (final instrument in _results.take(8))
                        ListTile(
                          title: Text(
                            instrument.ticker,
                            textDirection: TextDirection.ltr,
                          ),
                          subtitle: Text(
                            instrument.description.isEmpty
                                ? instrument.exchange
                                : instrument.description,
                            textDirection: instrument.description.isEmpty
                                ? TextDirection.ltr
                                : TextDirection.rtl,
                          ),
                          trailing: const Icon(
                            Icons.add_circle_outline_rounded,
                          ),
                          onTap: () => _select(instrument),
                        ),
                    ],
                  ],
                ),
              ),
            ),
            if (_selected.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final instrument in _selected)
                    InputChip(
                      label: Text(instrument.ticker),
                      onDeleted: isLoading ? null : () => _remove(instrument),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: _selected.length < 2 || isLoading
                    ? null
                    : () {
                        if (_mode == 'swing') {
                          _compare();
                        } else {
                          _compareInvestment();
                        }
                      },
                icon: isLoading
                    ? const SizedBox.square(
                        dimension: 20,
                        child: CircularProgressIndicator(strokeWidth: 2.5),
                      )
                    : Icon(
                        _mode == 'swing'
                            ? Icons.compare_arrows_rounded
                            : Icons.analytics_outlined,
                      ),
                label: Text(
                  isLoading
                      ? 'جاري تحليل المقارنة...'
                      : (_mode == 'swing'
                            ? 'قارن الأسهم للمضاربة'
                            : 'قارن الأسهم للاستثمار والقيمة'),
                ),
              ),
            ],
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
            const SizedBox(height: 12),
            const FreePlanNativeAd(),
            if (_mode == 'swing' && _result != null)
              _ComparisonResultView(result: _result!),
            if (_mode == 'investment' && _investmentResult != null)
              _InvestmentComparisonResultView(result: _investmentResult!),
          ],
        ),
      ),
    );
  }
}

class _ComparisonResultView extends StatelessWidget {
  const _ComparisonResultView({required this.result});

  final StockComparisonResult result;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'الأفضل في المقارنة: ${result.bestTicker}',
                  textDirection: TextDirection.rtl,
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 8),
                Text(result.summary),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    Chip(
                      label: Text(
                        result.includedAllowance
                            ? 'المقارنة متضمنة في الخطة'
                            : 'تكلفة المقارنة: ${result.comparisonChargedCoins} عملة',
                      ),
                    ),
                    Chip(
                      label: Text(
                        'تكلفة التحليلات الجديدة: ${result.analysisChargedCoins} عملة',
                      ),
                    ),
                    Chip(label: Text('الرصيد: ${result.balanceCoins} عملة')),
                    if (result.includedAllowance)
                      Chip(
                        label: Text(
                          'المتبقي هذا الشهر: ${result.allowanceRemaining}',
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
        for (final item in result.items) _ComparisonItemCard(item: item),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              result.disclaimer,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ),
      ],
    );
  }
}

class _ComparisonItemCard extends StatelessWidget {
  const _ComparisonItemCard({required this.item});

  final StockComparisonItem item;

  @override
  Widget build(BuildContext context) {
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
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    item.ticker,
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Chip(
                  label: Text(
                    '${item.comparisonScore.toStringAsFixed(1)} / 100',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text(_signal(item.signal))),
                Chip(
                  label: Text('الثقة ${item.confidence.toStringAsFixed(1)}%'),
                ),
                Chip(label: Text('الاتجاه ${_trend(item.trend)}')),
                Chip(label: Text('المخاطرة ${_risk(item.riskLevel)}')),
              ],
            ),
            const Divider(height: 24),
            _ValueRow(label: 'الدخول', value: _price(item.entry)),
            _ValueRow(label: 'وقف الخسارة', value: _price(item.stopLoss)),
            _ValueRow(label: 'الهدف الأول', value: _price(item.target1)),
            _ValueRow(label: 'الهدف الثاني', value: _price(item.target2)),
            _ValueRow(
              label: 'العائد مقابل المخاطرة',
              value: item.rewardRisk1 > 0
                  ? '${item.rewardRisk1.toStringAsFixed(1)} : 1'
                  : '—',
            ),
            _ValueRow(
              label: 'RSI',
              value: item.rsi > 0 ? item.rsi.toStringAsFixed(1) : '—',
            ),
          ],
        ),
      ),
    );
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

String _price(double value) => value > 0 ? value.toStringAsFixed(2) : '—';

String _signal(String value) {
  return switch (value.toUpperCase()) {
    'BUY' => 'شراء مشروط',
    'AVOID' => 'تجنب حاليًا',
    _ => 'مراقبة',
  };
}

String _trend(String value) {
  return switch (value.toLowerCase()) {
    'uptrend' || 'bullish' || 'weak_bullish' => 'صاعد',
    'downtrend' || 'bearish' || 'weak_bearish' => 'هابط',
    _ => 'عرضي',
  };
}

String _risk(String value) {
  return switch (value.toLowerCase()) {
    'low' => 'منخفضة',
    'high' => 'مرتفعة',
    _ => 'متوسطة',
  };
}

class _InvestmentComparisonResultView extends StatelessWidget {
  const _InvestmentComparisonResultView({required this.result});

  final StockInvestmentComparisonResult result;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 16),
        Card(
          color: theme.colorScheme.primaryContainer,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.stars_rounded,
                      color: theme.colorScheme.onPrimaryContainer,
                      size: 24,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'أفضل خيار استثماري: ${result.bestTicker}',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.onPrimaryContainer,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  result.summary,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        for (var i = 0; i < result.items.length; i++) ...[
          _InvestmentStockComparisonCard(
            item: result.items[i],
            rank: i + 1,
            isBest: result.items[i].ticker == result.bestTicker,
          ),
          const SizedBox(height: 10),
        ],
      ],
    );
  }
}

class _InvestmentStockComparisonCard extends StatelessWidget {
  const _InvestmentStockComparisonCard({
    required this.item,
    required this.rank,
    required this.isBest,
  });

  final StockInvestmentAnalysis item;
  final int rank;
  final bool isBest;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isValue = item.investmentCategory == 'value';
    final isDividend = item.investmentCategory == 'dividend';
    final categoryText = isValue
        ? '🛡️ سهم قيمة'
        : isDividend
        ? '💰 توزيعات كاش'
        : '💎 نمو واعد';

    final margin = item.marginOfSafetyPct;
    final isPositiveMargin = margin != null && margin > 0;

    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: isBest
            ? BorderSide(color: theme.colorScheme.primary, width: 2)
            : BorderSide.none,
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: isBest
                      ? theme.colorScheme.primary
                      : theme.colorScheme.surfaceContainerHighest,
                  foregroundColor: isBest
                      ? theme.colorScheme.onPrimary
                      : theme.colorScheme.onSurfaceVariant,
                  child: Text(
                    '$rank',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            item.ticker,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                            textDirection: TextDirection.ltr,
                          ),
                          if (isBest) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: theme.colorScheme.primary,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'الخيار الأفضل',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      Text(
                        '${item.companyName} • ${item.sector}',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                Chip(
                  label: Text(
                    categoryText,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      Text('التقييم', style: theme.textTheme.bodySmall),
                      const SizedBox(height: 2),
                      Text(
                        '${item.investmentScore.toStringAsFixed(1)} / 100',
                        style: TextStyle(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      Text('هامش الأمان', style: theme.textTheme.bodySmall),
                      const SizedBox(height: 2),
                      Text(
                        margin != null
                            ? '${isPositiveMargin ? '+' : ''}${margin.toStringAsFixed(1)}%'
                            : '—',
                        style: TextStyle(
                          color: isPositiveMargin ? Colors.green : Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                        textDirection: TextDirection.ltr,
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      Text('السعر الحالي', style: theme.textTheme.bodySmall),
                      const SizedBox(height: 2),
                      Text(
                        '${item.currentPrice.toStringAsFixed(2)} ج.م',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            // صندوق القيمة المستهدفة والمدة المتوقعة
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.withValues(alpha: 0.25)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.flag_rounded, size: 16, color: Colors.green),
                      const SizedBox(width: 4),
                      Text(
                        'المستهدف: ${item.expectedTargetPrice != null ? "${item.expectedTargetPrice!.toStringAsFixed(2)} ج.م" : (item.fairValue != null ? "${item.fairValue!.toStringAsFixed(2)} ج.م" : "—")}',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade800,
                        ),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      const Icon(Icons.schedule_rounded, size: 14, color: Colors.green),
                      const SizedBox(width: 4),
                      Text(
                        item.expectedTimeframe ?? '6 - 12 شهراً',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Colors.green.shade800,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                if (item.fairValue != null)
                  _InvChip(
                    label: 'القيمة العادلة',
                    value: '${item.fairValue!.toStringAsFixed(2)} ج.م',
                  ),
                if (item.peRatio != null)
                  _InvChip(
                    label: 'مكرر P/E',
                    value: '${item.peRatio!.toStringAsFixed(1)}x',
                    isPositive: item.peRatio! <= 10,
                  ),
                if (item.pbRatio != null)
                  _InvChip(
                    label: 'مضاعف P/B',
                    value: '${item.pbRatio!.toStringAsFixed(1)}x',
                  ),
                if (item.dividendYieldPct != null)
                  _InvChip(
                    label: 'عائد توزيعات',
                    value: '${item.dividendYieldPct!.toStringAsFixed(1)}%',
                    isPositive: item.dividendYieldPct! > 5,
                  ),
                if (item.roePct != null)
                  _InvChip(
                    label: 'عائد ROE',
                    value: '${item.roePct!.toStringAsFixed(1)}%',
                    isPositive: item.roePct! > 15,
                  ),
                if (item.eps != null)
                  _InvChip(
                    label: 'ربحية السهم EPS',
                    value: '${item.eps!.toStringAsFixed(2)} ج.م',
                  ),
              ],
            ),
            if (item.strengths.isNotEmpty) ...[
              const SizedBox(height: 10),
              for (final s in item.strengths.take(2))
                Padding(
                  padding: const EdgeInsets.only(bottom: 2),
                  child: Row(
                    children: [
                      const Icon(Icons.check, size: 14, color: Colors.green),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          s,
                          style: theme.textTheme.bodySmall?.copyWith(
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
            const SizedBox(height: 12),
            FilledButton.tonalIcon(
              onPressed: () => context.push('/stocks/${item.ticker}'),
              icon: const Icon(Icons.candlestick_chart_rounded, size: 18),
              label: const Text(
                'معلومات وشارت السهم',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InvChip extends StatelessWidget {
  const _InvChip({
    required this.label,
    required this.value,
    this.isPositive = false,
  });

  final String label;
  final String value;
  final bool isPositive;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: isPositive ? Colors.green : null,
        ),
      ),
    );
  }
}

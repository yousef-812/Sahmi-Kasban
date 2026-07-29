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
  bool _searching = false;
  bool _loadingSaved = false;
  bool _analyzing = false;
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
        await ref.read(freePlanInterstitialProvider).recordMeaningfulAction(
          enabled:
              ref.read(sessionControllerProvider).profile?.adsEnabled == true,
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
                              '${instrument.exchange} — ${instrument.providerSymbol}',
                              textDirection: TextDirection.ltr,
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
                FilledButton.icon(
                  onPressed: _selected == null || _analyzing ? null : _analyze,
                  icon: _analyzing
                      ? const SizedBox.square(
                          dimension: 20,
                          child: CircularProgressIndicator(strokeWidth: 2.5),
                        )
                      : const Icon(Icons.auto_graph_rounded),
                  label: const Text('تحليل السهم — 0.5 عملة'),
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed: _analyzing
                      ? null
                      : () => context.push('/market/compare'),
                  icon: const Icon(Icons.compare_arrows_rounded),
                  label: const Text('مقارنة سهمين أو أكثر'),
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
        ],
      ],
    );
  }
}

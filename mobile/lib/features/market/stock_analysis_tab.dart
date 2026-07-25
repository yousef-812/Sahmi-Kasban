import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../../widgets/structured_data_card.dart';
import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';

class StockAnalysisTab extends ConsumerStatefulWidget {
  const StockAnalysisTab({super.key});

  @override
  ConsumerState<StockAnalysisTab> createState() => _StockAnalysisTabState();
}

class _StockAnalysisTabState extends ConsumerState<StockAnalysisTab> {
  final _queryController = TextEditingController();
  List<MarketInstrument> _results = const [];
  MarketInstrument? _selected;
  StockAnalysisResult? _analysis;
  bool _searching = false;
  bool _analyzing = false;
  String? _error;

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    if (_searching) {
      return;
    }
    setState(() {
      _searching = true;
      _error = null;
      _analysis = null;
    });
    try {
      final results = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(_queryController.text);
      if (mounted) {
        setState(() => _results = results);
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _searching = false);
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
          'تكلفة التحليل الجديد 0.5 عملة. لن يتم الخصم إلا بعد نجاح التحليل، وإعادة نفس التحليل المخزن لا تخصم مرة أخرى.',
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
      _analysis = null;
    });
    try {
      final analysis = await ref
          .read(backendRepositoryProvider)
          .analyzeStock(instrument.ticker);
      await ref.read(sessionControllerProvider.notifier).refreshProfile();
      ref.invalidate(walletSummaryProvider);
      if (mounted) {
        setState(() => _analysis = analysis);
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
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'ابحث بالرمز، اختر السهم الصحيح، ثم ابدأ التحليل المدفوع.',
                ),
                const SizedBox(height: 18),
                TextField(
                  controller: _queryController,
                  textDirection: TextDirection.ltr,
                  textCapitalization: TextCapitalization.characters,
                  decoration: InputDecoration(
                    labelText: 'رمز السهم',
                    hintText: 'COMI',
                    prefixIcon: const Icon(Icons.search_rounded),
                    suffixIcon: IconButton(
                      onPressed: _searching ? null : _search,
                      icon: _searching
                          ? const SizedBox.square(
                              dimension: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.arrow_forward_rounded),
                    ),
                  ),
                  onSubmitted: (_) => _search(),
                ),
                if (_results.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  for (final instrument in _results)
                    Builder(
                      builder: (context) {
                        final selected = _selected?.ticker == instrument.ticker;
                        return Card(
                          color: selected
                              ? Theme.of(context).colorScheme.secondaryContainer
                              : null,
                          child: ListTile(
                            onTap: () => setState(() => _selected = instrument),
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
              ],
            ),
          ),
        ),
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
          _AnalysisHeader(analysis: analysis),
          StructuredDataCard(
            title: 'تفاصيل التحليل',
            data: analysis.payload,
          ),
        ],
      ],
    );
  }
}

class _AnalysisHeader extends StatelessWidget {
  const _AnalysisHeader({required this.analysis});

  final StockAnalysisResult analysis;

  @override
  Widget build(BuildContext context) {
    final timestamp = DateFormat('d MMM yyyy، h:mm a', 'ar')
        .format(analysis.dataAsOf.toLocal());
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              analysis.ticker,
              textDirection: TextDirection.ltr,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
            ),
            const SizedBox(height: 8),
            Text('البيانات حتى: $timestamp'),
            Text(
              analysis.cached
                  ? 'تم استخدام تحليل مخزن — لا يوجد خصم جديد.'
                  : 'تم خصم ${analysis.chargedCoins} عملة بعد نجاح التحليل.',
            ),
            Text('الرصيد بعد العملية: ${analysis.balanceCoins} عملة'),
          ],
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import '../watchlist/watchlist_providers.dart';
import 'stock_analysis_report.dart';

class StockAnalysisScreen extends ConsumerStatefulWidget {
  const StockAnalysisScreen({super.key, required this.ticker});

  final String ticker;

  @override
  ConsumerState<StockAnalysisScreen> createState() =>
      _StockAnalysisScreenState();
}

class _StockAnalysisScreenState extends ConsumerState<StockAnalysisScreen> {
  StockAnalysisResult? _analysis;
  bool _loadingSaved = false;
  bool _analyzing = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    Future<void>.microtask(_loadSavedAnalysis);
  }

  Future<void> _addToWatchlist(BuildContext context) async {
    try {
      await ref.read(watchlistProvider.notifier).add(widget.ticker);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تمت إضافة ${widget.ticker} لـ قائمة المراقبة'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e.toString().contains('already')
                  ? 'السهم موجود بالفعل في قائمة المراقبة'
                  : 'تعذر إضافة السهم للمراقبة',
            ),
          ),
        );
      }
    }
  }

  Future<void> _loadSavedAnalysis() async {
    if (!mounted) {
      return;
    }
    setState(() => _loadingSaved = true);
    try {
      final saved = await ref
          .read(backendRepositoryProvider)
          .getLatestOwnedStockAnalysis(widget.ticker);
      if (mounted && saved != null) {
        setState(() => _analysis = saved);
      }
    } on ApiException {
      // A saved analysis is optional; the user can still request a fresh one.
    } finally {
      if (mounted) {
        setState(() => _loadingSaved = false);
      }
    }
  }

  Future<void> _analyze() async {
    if (_analyzing) {
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('تحليل ${widget.ticker}'),
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
          .analyzeStock(widget.ticker);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('تحليل ${widget.ticker}'),
        actions: [
          IconButton(
            onPressed: () => _addToWatchlist(context),
            icon: const Icon(Icons.visibility_rounded),
            tooltip: 'أضف للمراقبة',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadSavedAnalysis,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'تحليل ${widget.ticker}',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'التقرير أدناه مبني على البيانات الفنية والكمية للسهم.',
                    ),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed: _analyzing ? null : _analyze,
                      icon: _analyzing
                          ? const SizedBox.square(
                              dimension: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                              ),
                            )
                          : const Icon(Icons.auto_graph_rounded),
                      label: const Text('تحليل بالبيانات الجديدة — 0.5 عملة'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            if (_loadingSaved) ...[
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
              const SizedBox(height: 12),
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
            if (_analysis case final analysis?) ...[
              const SizedBox(height: 16),
              StockAnalysisReport(analysis: analysis),
            ],
          ],
        ),
      ),
    );
  }
}

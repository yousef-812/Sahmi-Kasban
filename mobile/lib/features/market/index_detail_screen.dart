import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../rating/rating_prompt_manager.dart';
import '../wallet/wallet_providers.dart';
import 'market_quotes_providers.dart';
import 'stock_analysis_report.dart';
import 'stock_detail_screen.dart' show TradingViewWidget;
import 'stock_quote_card.dart';

const Map<String, String> _indexTradingViewSymbols = {
  'EGX30': 'EGX:EGX30',
  'EGX70': 'EGX:EGX70EWI',
  'EGX100': 'EGX:EGX100EWI',
};

class IndexDetailScreen extends ConsumerStatefulWidget {
  const IndexDetailScreen({super.key, required this.ticker});

  final String ticker;

  @override
  ConsumerState<IndexDetailScreen> createState() => _IndexDetailScreenState();
}

class _IndexDetailScreenState extends ConsumerState<IndexDetailScreen> {
  StockAnalysisResult? _analysis;
  bool _loadingSaved = false;
  bool _analyzing = false;
  String? _error;

  String get _ticker => widget.ticker.trim().toUpperCase();

  String get _tradingViewSymbol =>
      _indexTradingViewSymbols[_ticker] ?? 'EGX:$_ticker';

  @override
  void initState() {
    super.initState();
    Future<void>.microtask(_loadSavedAnalysis);
  }

  Future<void> _loadSavedAnalysis() async {
    if (!mounted) {
      return;
    }
    setState(() => _loadingSaved = true);
    try {
      final saved = await ref
          .read(backendRepositoryProvider)
          .getLatestOwnedIndexAnalysis(_ticker);
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
        title: Text('تحليل المؤشر $_ticker'),
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
          .analyzeMarketIndex(_ticker);
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
        if (mounted) {
          await ref
              .read(ratingPromptManagerProvider)
              .recordCompletedAnalysis(context);
        }
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
    final quoteState = ref.watch(marketIndexQuoteProvider(_ticker));
    return Scaffold(
      appBar: AppBar(
        title: Text(_ticker, textDirection: TextDirection.ltr),
      ),
      body: quoteState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => _ErrorView(
          error: error,
          onRetry: () => ref.invalidate(marketIndexQuoteProvider(_ticker)),
        ),
        data: (quote) => RefreshIndicator(
          onRefresh: _loadSavedAnalysis,
          child: ListView(
            padding: const EdgeInsets.symmetric(vertical: 12),
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: _Header(quote: quote),
              ),
              const SizedBox(height: 12),
              _StatsRow(quote: quote),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        'الرسم البياني اللحظي',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: TradingViewWidget(symbol: _tradingViewSymbol),
              ),
              const SizedBox(height: 16),
              Card(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'التحليل الفني للمؤشر',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'تقرير مبني على بيانات المؤشر الفنية والكمية من محرك التحليل.',
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
                        label: const Text(
                          'تحليل بالبيانات الجديدة — 0.5 عملة',
                        ),
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
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: StockAnalysisReport(analysis: analysis),
                ),
              ],
              const SizedBox(height: 8),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: FreePlanNativeAd(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.quote});

  final MarketQuote quote;

  @override
  Widget build(BuildContext context) {
    final isUp = (quote.changePercent ?? 0) > 0;
    final isDown = (quote.changePercent ?? 0) < 0;
    final accent = isUp
        ? Colors.green
        : isDown
        ? Colors.redAccent
        : Theme.of(context).colorScheme.primary;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    quote.description.isEmpty
                        ? quote.ticker
                        : quote.description,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Theme.of(
                      context,
                    ).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    quote.ticker,
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.2,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  formatPrice(quote.currentPrice),
                  textDirection: TextDirection.ltr,
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.w900,
                    color: accent,
                  ),
                ),
                const SizedBox(width: 12),
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    formatChangePercent(quote.changePercent),
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: changeColor(context, quote.changePercent),
                    ),
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

class _StatsRow extends StatelessWidget {
  const _StatsRow({required this.quote});

  final MarketQuote quote;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          _Stat(
            label: 'الفتح',
            value: formatPrice(quote.openPrice),
            color: Theme.of(context).colorScheme.onSurface,
          ),
          _Stat(
            label: 'سعر الإغلاق',
            value: formatPrice(quote.currentPrice),
            color: Theme.of(context).colorScheme.onSurface,
          ),
          _Stat(
            label: 'الأعلى',
            value: formatPrice(quote.sessionHigh ?? quote.week52High),
            color: Colors.green,
          ),
          _Stat(
            label: 'الأدنى',
            value: formatPrice(quote.sessionLow ?? quote.week52Low),
            color: Colors.redAccent,
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value, required this.color});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            textDirection: TextDirection.ltr,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w800,
              color: color,
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
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 48),
            const SizedBox(height: 12),
            Text(
              error is ApiException
                  ? (error as ApiException).message
                  : 'تعذر تحميل بيانات المؤشر.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
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
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'market_quotes_providers.dart';
import 'stock_quote_card.dart';

class StockDetailScreen extends ConsumerWidget {
  const StockDetailScreen({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final quoteState = ref.watch(stockQuoteProvider(ticker));
    return Scaffold(
      appBar: AppBar(
        title: Text(
          ticker,
          textDirection: TextDirection.ltr,
        ),
        actions: [
          IconButton(
            tooltip: 'تحديث',
            onPressed: quoteState.isLoading
                ? null
                : () => ref
                      .read(stockQuoteProvider(ticker).notifier)
                      .refresh(),
            icon: quoteState.isLoading
                ? const SizedBox.square(
                    dimension: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: quoteState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => _ErrorView(
          error: error,
          onRetry: () => ref.invalidate(stockQuoteProvider(ticker)),
        ),
        data: (quote) => _DetailContent(quote: quote, ticker: ticker),
      ),
    );
  }
}

class _DetailContent extends ConsumerWidget {
  const _DetailContent({required this.quote, required this.ticker});

  final MarketQuote quote;
  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _Header(quote: quote),
        ),
        const SizedBox(height: 12),
        const SizedBox(height: 8),
        _StatsRow(quote: quote),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _QuickActions(ticker: ticker, quote: quote),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'الرسم البياني اللحظي',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        const SizedBox(height: 8),
        TradingViewWidget(symbol: ticker),
        const SizedBox(height: 8),
      ],
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
                    quote.description.isEmpty ? quote.ticker : quote.description,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                if (quote.sector != null)
                  Chip(
                    label: Text(quote.sector!),
                    labelStyle: Theme.of(
                      context,
                    ).textTheme.labelSmall,
                    visualDensity: VisualDensity.compact,
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
                const Spacer(),
                if (quote.volume != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'الحجم',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(
                              context,
                            ).colorScheme.onSurfaceVariant,
                          ),
                        ),
                        Text(
                          _formatVolume(quote.volume),
                          textDirection: TextDirection.ltr,
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
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
            value: formatPrice(quote.previousClose),
            color: Theme.of(context).colorScheme.onSurface,
          ),
          _Stat(
            label: 'الأعلى',
            value: quote.marketOpen
                ? formatPrice(quote.sessionHigh)
                : formatPrice(quote.week52High),
            color: Colors.green,
          ),
          _Stat(
            label: 'الأدنى',
            value: quote.marketOpen
                ? formatPrice(quote.sessionLow)
                : formatPrice(quote.week52Low),
            color: Colors.redAccent,
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({
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

class _QuickActions extends ConsumerWidget {
  const _QuickActions({required this.ticker, required this.quote});

  final String ticker;
  final MarketQuote quote;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Row(
      children: [
        Expanded(
          child: FilledButton.icon(
            onPressed: () => context.push('/market/analyze/${quote.ticker}'),
            icon: const Icon(Icons.auto_graph_rounded),
            label: const Text('تحليل'),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () => context.push('/market/compare'),
            icon: const Icon(Icons.compare_arrows_rounded),
            label: const Text('مقارنة'),
          ),
        ),
      ],
    );
  }
}

class TradingViewWidget extends StatefulWidget {
  const TradingViewWidget({super.key, required this.symbol});

  final String symbol;
  final bool dark = false;

  @override
  State<TradingViewWidget> createState() => _TradingViewWidgetState();
}

class _TradingViewWidgetState extends State<TradingViewWidget> {
  late final WebViewController _controller;
  late final String _html;

  @override
  void initState() {
    super.initState();
    _html = _buildHtml();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFFFFFFF));
  }

  String _buildHtml() {
    final symbol = widget.symbol.toUpperCase();
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  html, body {
    margin: 0; padding: 0; height: 100%; background: #ffffff;
    font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  #tv { width: 100%; height: 100%; }
  body.loading #tv { visibility: hidden; }
  .center { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; }
  .spinner { width: 28px; height: 28px; border: 3px solid #e0e0e0; border-top-color: #1f6feb; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body class="loading">
<div class="center"><div class="spinner"></div></div>
<div id="tv"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
  new TradingView.widget({
    "container_id": "tv",
    "autosize": true,
    "width": "100%",
    "height": "100%",
    "symbol": "EGX:$symbol",
    "interval": "D",
    "timezone": "Africa/Cairo",
    "theme": "light",
    "style": "1",
    "locale": "ar_AE",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "hide_top_toolbar": false,
    "studies": ["Volume@tv-basicstudies"],
    "details": true,
    "hotlist": true,
    "calendar": false,
    "support_host": "https://www.tradingview.com"
  });
  function ready() {
    document.body.classList.remove('loading');
  }
  setTimeout(ready, 1200);
</script>
</body>
</html>
''';
  }

  @override
  void didUpdateWidget(covariant TradingViewWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.symbol != widget.symbol) {
      _html = _buildHtml();
      _controller
        ..loadHtmlString(_html)
        ..reload();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 420,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            const Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: Color(0xFFF7F7F7),
                ),
                child: Center(child: CircularProgressIndicator()),
              ),
            ),
            Positioned.fill(
              child: WebViewWidget(
                controller: _controller..loadHtmlString(_html),
              ),
            ),
          ],
        ),
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
                  : 'تعذر تحميل بيانات السهم.',
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

String _formatVolume(double? value) {
  if (value == null) {
    return '—';
  }
  if (value >= 1000000) {
    return '${(value / 1000000).toStringAsFixed(2)}M';
  }
  if (value >= 1000) {
    return '${(value / 1000).toStringAsFixed(1)}K';
  }
  return value.toStringAsFixed(0);
}
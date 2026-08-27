import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../app/theme.dart';
import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'market_quotes_providers.dart';
import 'stock_quote_card.dart';

class StockDetailScreen extends ConsumerStatefulWidget {
  const StockDetailScreen({super.key, required this.ticker});

  final String ticker;

  @override
  ConsumerState<StockDetailScreen> createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends ConsumerState<StockDetailScreen> {
  bool _fullscreenOpen = false;
  bool _autoFullscreen = false;
  bool _rotationCheckScheduled = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_rotationCheckScheduled) {
      return;
    }
    _rotationCheckScheduled = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _rotationCheckScheduled = false;
      if (!mounted) {
        return;
      }
      final orientation = MediaQuery.orientationOf(context);
      if (orientation == Orientation.landscape && !_fullscreenOpen) {
        _openFullscreenChart(auto: true);
      } else if (orientation == Orientation.portrait && _autoFullscreen) {
        _autoFullscreen = false;
        Navigator.of(context).pop();
        _fullscreenOpen = false;
      }
    });
  }

  Future<void> _openFullscreenChart({bool auto = false}) async {
    if (_fullscreenOpen) {
      return;
    }
    _fullscreenOpen = true;
    _autoFullscreen = auto;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => Scaffold(
          backgroundColor: Theme.of(
            context,
          ).colorScheme.surfaceContainerLowest,
          body: SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) => TradingViewWidget(
                symbol: widget.ticker,
                height: constraints.maxHeight,
              ),
            ),
          ),
        ),
      ),
    );
    _fullscreenOpen = false;
    _autoFullscreen = false;
  }

  @override
  Widget build(BuildContext context) {
    final quoteState = ref.watch(stockQuoteProvider(widget.ticker));
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.ticker, textDirection: TextDirection.ltr),
        actions: [
          IconButton(
            tooltip: 'تحديث',
            onPressed: quoteState.isLoading
                ? null
                : () => ref
                      .read(stockQuoteProvider(widget.ticker).notifier)
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
          onRetry: () => ref.invalidate(stockQuoteProvider(widget.ticker)),
        ),
        data: (quote) => _DetailContent(
          quote: quote,
          ticker: widget.ticker,
          onOpenFullscreen: _openFullscreenChart,
        ),
      ),
    );
  }
}

class _DetailContent extends ConsumerWidget {
  const _DetailContent({
    required this.quote,
    required this.ticker,
    required this.onOpenFullscreen,
  });

  final MarketQuote quote;
  final String ticker;
  final VoidCallback onOpenFullscreen;

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
        _StatsRow(quote: quote),
        const SizedBox(height: 8),
        _AnnualRange(quote: quote),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _QuickActions(ticker: ticker, quote: quote),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  'الرسم البياني اللحظي',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              IconButton(
                tooltip: 'ملء الشاشة',
                onPressed: onOpenFullscreen,
                icon: const Icon(Icons.fullscreen_rounded),
                color: Theme.of(context).colorScheme.primary,
              ),
            ],
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
        ? SahmiBrand.neonBull
        : isDown
        ? SahmiBrand.alertRed
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
                if (quote.sector != null)
                  Chip(
                    label: Text(quote.sector!),
                    labelStyle: Theme.of(context).textTheme.labelSmall,
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
                          style: Theme.of(context).textTheme.bodySmall
                              ?.copyWith(
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                        ),
                        Text(
                          _formatVolume(quote.volume),
                          textDirection: TextDirection.ltr,
                          style: Theme.of(context).textTheme.titleSmall
                              ?.copyWith(fontWeight: FontWeight.w700),
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
            value: formatPrice(quote.currentPrice),
            color: Theme.of(context).colorScheme.onSurface,
          ),
          _Stat(
            label: 'الأعلى',
            value: formatPrice(quote.sessionHigh ?? quote.week52High),
            color: SahmiBrand.neonBull,
          ),
          _Stat(
            label: 'الأدنى',
            value: formatPrice(quote.sessionLow ?? quote.week52Low),
            color: SahmiBrand.alertRed,
          ),
        ],
      ),
    );
  }
}

class _AnnualRange extends StatelessWidget {
  const _AnnualRange({required this.quote});

  final MarketQuote quote;

  @override
  Widget build(BuildContext context) {
    final hasHigh = quote.week52High != null;
    final hasLow = quote.week52Low != null;
    if (!hasHigh && !hasLow) {
      return const SizedBox.shrink();
    }
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'النطاق السنوي (52 أسبوع)',
              style: Theme.of(
                context,
              ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _Stat(
                  label: 'أعلى سعر سنوي',
                  value: formatPrice(quote.week52High),
                  color: SahmiBrand.neonBull,
                ),
                _Stat(
                  label: 'أدنى سعر سنوي',
                  value: formatPrice(quote.week52Low),
                  color: SahmiBrand.alertRed,
                ),
              ],
            ),
          ],
        ),
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
  const TradingViewWidget({super.key, required this.symbol, this.height = 420});

  final String symbol;
  final double height;

  @override
  State<TradingViewWidget> createState() => _TradingViewWidgetState();
}

class _TradingViewWidgetState extends State<TradingViewWidget> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(
        Theme.of(context).brightness == Brightness.dark
            ? const Color(0xFF0A0E1A)
            : const Color(0xFFFFFFFF),
      )
      ..loadHtmlString(_buildHtml());
  }

  bool get _isDark => Theme.of(context).brightness == Brightness.dark;

  String _buildHtml() {
    final symbol = widget.symbol.toUpperCase();
    final chartTheme = _isDark ? 'dark' : 'light';
    final bg = _isDark ? '#0a0e1a' : '#ffffff';
    final toolbarBg = _isDark ? '#141824' : '#f1f3f6';
    final spinnerBorder = _isDark ? '#2a3040' : '#e0e0e0';
    final spinnerAccent = _isDark ? '#00e676' : '#1f6feb';
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  html, body {
    margin: 0; padding: 0; height: 100%; background: $bg;
    font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  #tv { width: 100%; height: 100%; }
  body.loading #tv { visibility: hidden; }
  .center { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; }
  .spinner { width: 28px; height: 28px; border: 3px solid $spinnerBorder; border-top-color: $spinnerAccent; border-radius: 50%; animation: spin 0.8s linear infinite; }
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
    "theme": "$chartTheme",
    "style": "1",
    "locale": "ar_AE",
    "toolbar_bg": "$toolbarBg",
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
      _controller
        ..loadHtmlString(_buildHtml())
        ..reload();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: widget.height,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: _isDark
                      ? const Color(0xFF0A0E1A)
                      : const Color(0xFFF7F7F7),
                ),
                child: const Center(child: CircularProgressIndicator()),
              ),
            ),
            Positioned.fill(
              child: WebViewWidget(controller: _controller),
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

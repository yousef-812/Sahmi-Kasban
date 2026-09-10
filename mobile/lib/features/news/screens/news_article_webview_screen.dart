import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_windows/webview_windows.dart' as win_wv;

/// يعرض مقال الخبر داخل التطبيق عبر WebView بدلاً من فتح متصفح خارجي.
class NewsArticleWebviewScreen extends StatefulWidget {
  const NewsArticleWebviewScreen({
    super.key,
    required this.title,
    required this.url,
  });

  final String title;
  final String url;

  @override
  State<NewsArticleWebviewScreen> createState() =>
      _NewsArticleWebviewScreenState();
}

class _NewsArticleWebviewScreenState extends State<NewsArticleWebviewScreen> {
  WebViewController? _mobileController;
  win_wv.WebviewController? _winController;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initWebView();
  }

  Future<void> _initWebView() async {
    if (kIsWeb) return;
    if (defaultTargetPlatform == TargetPlatform.windows) {
      try {
        final controller = win_wv.WebviewController();
        await controller.initialize();
        controller.url.listen((url) {
          if (!mounted) return;
          setState(() => _loading = false);
        });
        if (mounted) {
          setState(() {
            _winController = controller;
          });
          await controller.setBackgroundColor(
            Theme.of(context).colorScheme.surface,
          );
          await controller.loadUrl(widget.url);
        }
      } catch (e) {
        debugPrint('News WebView Windows init error: $e');
        if (mounted) setState(() => _error = 'تعذّر فتح المقال داخل التطبيق');
      }
    } else if (defaultTargetPlatform == TargetPlatform.android ||
        defaultTargetPlatform == TargetPlatform.iOS) {
      try {
        final controller = WebViewController()
          ..setJavaScriptMode(JavaScriptMode.unrestricted)
          ..setNavigationDelegate(
            NavigationDelegate(
              onPageStarted: (_) => setState(() => _loading = true),
              onPageFinished: (_) => setState(() => _loading = false),
              onWebResourceError: (error) {
                if (mounted) {
                  setState(() {
                    _error = 'تعذّر تحميل المقال — تحقق من اتصالك وحاول مجدداً';
                  });
                }
              },
            ),
          );
        await controller.loadRequest(Uri.parse(widget.url));
        if (mounted) {
          setState(() {
            _mobileController = controller;
          });
        }
      } catch (e) {
        debugPrint('News WebView mobile init error: $e');
        if (mounted) setState(() => _error = 'تعذّر فتح المقال داخل التطبيق');
      }
    } else {
      if (mounted) setState(() => _error = 'المتصفح غير مدعوم على هذا الجهاز');
    }
  }

  @override
  void dispose() {
    _winController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'إعادة تحميل الصفحة',
            onPressed: () {
              setState(() => _error = null);
              final url = widget.url;
              final mobile = _mobileController;
              final win = _winController;
              if (mobile != null) {
                mobile.loadRequest(Uri.parse(url));
              } else if (win != null && win.value.isInitialized) {
                win.loadUrl(url);
              } else {
                _initWebView();
              }
            },
          ),
        ],
      ),
      backgroundColor: colorScheme.surface,
      body: Stack(
        children: [
          if (_winController != null && _winController!.value.isInitialized)
            Positioned.fill(child: win_wv.Webview(_winController!)),
          if (_mobileController != null)
            Positioned.fill(child: WebViewWidget(controller: _mobileController!)),
          if (_loading && _mobileController == null && _winController == null)
            const Center(child: CircularProgressIndicator()),
          if (_loading && _error == null)
            Positioned(
              top: 12,
              right: 12,
              child: SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: colorScheme.primary,
                ),
              ),
            ),
          if (_error != null)
            Positioned.fill(
              child: ColoredBox(
                color: colorScheme.surface,
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.web_asset_off_rounded,
                          size: 56,
                          color: colorScheme.error,
                        ),
                        const SizedBox(height: 14),
                        Text(
                          _error!,
                          style: theme.textTheme.bodyMedium,
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
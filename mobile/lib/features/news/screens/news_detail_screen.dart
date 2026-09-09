import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';

import '../news_models.dart';
import '../news_providers.dart';

class NewsDetailScreen extends ConsumerStatefulWidget {
  const NewsDetailScreen({super.key, required this.article});

  final StockNewsArticle article;

  @override
  ConsumerState<NewsDetailScreen> createState() => _NewsDetailScreenState();
}

class _NewsDetailScreenState extends ConsumerState<NewsDetailScreen> {
  Future<void> _shareArticle() async {
    final article = widget.article;
    final text = [
      article.title,
      '',
      'المصدر: ${article.sourceName}',
      article.url,
    ].join('\n');
    // ignore: deprecated_member_use
    await Share.share(text, subject: article.title);
  }

  String _timeAgo(DateTime dt) {
    final diff = DateTime.now().toUtc().difference(dt.toUtc());
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final article = widget.article;

    // المحتوى الكامل يُجلب دائماً من الـ API (مش في القوائم عشان خفة الحجم)
    final detailAsync = ref.watch(newsArticleDetailProvider(article.id));
    final detail = detailAsync.value;
    final content = detail?.content.isNotEmpty == true
        ? detail!.content.trim()
        : (article.content.isNotEmpty ? article.content.trim() : '');
    final hasContent = content.isNotEmpty;
    final isLoadingContent = detailAsync.isLoading;
    final contentFailed = detailAsync.hasError;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          article.sourceName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_rounded),
            tooltip: 'مشاركة الخبر',
            onPressed: _shareArticle,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // شارات المصدر والتاريخ
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    article.sourceName,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  _timeAgo(article.publishedAt),
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
                const Spacer(),
                if (article.sentiment != null && article.sentiment!.isNotEmpty)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: article.sentiment == 'bullish'
                          ? Colors.green.withValues(alpha: 0.15)
                          : (article.sentiment == 'bearish'
                              ? Colors.red.withValues(alpha: 0.15)
                              : Colors.grey.withValues(alpha: 0.15)),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      article.sentiment == 'bullish'
                          ? 'إيجابي'
                          : (article.sentiment == 'bearish' ? 'سلبي' : 'محايد'),
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: article.sentiment == 'bullish'
                            ? Colors.green.shade700
                            : (article.sentiment == 'bearish'
                                ? Colors.red.shade700
                                : Colors.grey.shade700),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 14),

            // عنوان الخبر الرئيسي
            Text(
              article.title,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                height: 1.4,
              ),
            ),

            // شارات التيكرات المرتبطة إن وجدت
            if (article.tickers.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 6,
                children: article.tickers.map((t) {
                  return ActionChip(
                    avatar: const Icon(Icons.show_chart_rounded, size: 14),
                    label: Text(t),
                    onPressed: () => context.push('/stocks/$t'),
                  );
                }).toList(),
              ),
            ],
            const SizedBox(height: 16),

            // صورة الخبر إن وجدت
            if (article.imageUrl != null) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.network(
                  article.imageUrl!,
                  width: double.infinity,
                  height: 220,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // حالة تحميل المحتوى الكامل
            if (isLoadingContent) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: colorScheme.outlineVariant.withValues(alpha: 0.3),
                  ),
                ),
                child: Column(
                  children: [
                    const CircularProgressIndicator(),
                    const SizedBox(height: 12),
                    Text(
                      'جارٍ تحميل المحتوى الكامل للخبر...',
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // فشل تحميل المحتوى — مع إعادة المحاولة
            if (contentFailed && !isLoadingContent && !hasContent) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: colorScheme.errorContainer.withValues(alpha: 0.25),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline_rounded, color: colorScheme.error),
                    const SizedBox(width: 10),
                    const Expanded(child: Text('تعذّر تحميل المحتوى الكامل')),
                    TextButton(
                      onPressed: () =>
                          ref.invalidate(newsArticleDetailProvider(article.id)),
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // المحتوى الكامل للخبر (ناتيف داخل التطبيق)
            if (hasContent) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: colorScheme.outlineVariant.withValues(alpha: 0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.article_outlined,
                          size: 20,
                          color: colorScheme.primary,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'الخبر كاملاً',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      content,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.7,
                        color: colorScheme.onSurface,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ] else if (article.summary.isNotEmpty) ...[
              // ملخص الخبر كبديل إذا لم يتوفر المحتوى الكامل
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color:
                      colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: colorScheme.outlineVariant.withValues(alpha: 0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.article_outlined,
                          size: 20,
                          color: colorScheme.primary,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'تفاصيل وملخص الخبر',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      article.summary,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.6,
                        color: colorScheme.onSurface,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _shareArticle,
                    icon: const Icon(Icons.share_rounded, size: 18),
                    label: const Text('مشاركة الخبر مع مصدره'),
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
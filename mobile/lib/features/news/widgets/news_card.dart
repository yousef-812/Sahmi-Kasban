import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../news_models.dart';

class NewsCard extends StatelessWidget {
  const NewsCard({super.key, required this.article, this.compact = false});

  final StockNewsArticle article;
  final bool compact;

  Color _sentimentColor(BuildContext context) {
    return switch (article.sentiment) {
      'bullish' => const Color(0xFF00C875),
      'bearish' => Colors.redAccent,
      _ => Colors.grey,
    };
  }

  String _sentimentLabel() {
    return switch (article.sentiment) {
      'bullish' => 'إيجابي',
      'bearish' => 'سلبي',
      'neutral' => 'محايد',
      _ => '',
    };
  }

  String _timeAgo(DateTime dt) {
    final diff = DateTime.now().toUtc().difference(dt.toUtc());
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }

  Future<void> _openUrl() async {
    final uri = Uri.tryParse(article.url);
    if (uri != null && await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: colorScheme.outline.withValues(alpha: 0.15)),
      ),
      elevation: 0,
      child: InkWell(
        onTap: _openUrl,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: EdgeInsets.all(compact ? 12 : 14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // صورة الخبر
              if (article.imageUrl != null && !compact) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.network(
                    article.imageUrl!,
                    width: 76,
                    height: 76,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) =>
                        _FallbackNewsImage(sourceKey: article.sourceKey),
                  ),
                ),
                const SizedBox(width: 12),
              ],
              // المحتوى
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // عنوان الخبر
                    Text(
                      article.title,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        height: 1.4,
                      ),
                      maxLines: compact ? 2 : 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 6),
                    // ملخص (فقط في الوضع الكامل)
                    if (!compact && article.summary.isNotEmpty) ...[
                      Text(
                        article.summary,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurface.withValues(alpha: 0.65),
                          height: 1.4,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 8),
                    ],
                    // Footer: مصدر + وقت + sentiment
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        Text(
                          article.sourceName,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: colorScheme.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          '·',
                          style: TextStyle(color: colorScheme.outline),
                        ),
                        Text(
                          _timeAgo(article.publishedAt),
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: colorScheme.onSurface.withValues(alpha: 0.5),
                          ),
                        ),
                        if (article.sentiment != null &&
                            article.sentiment!.isNotEmpty) ...[
                          Text(
                            '·',
                            style: TextStyle(color: colorScheme.outline),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color:
                                  _sentimentColor(context).withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              _sentimentLabel(),
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: _sentimentColor(context),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              // سهم للفتح
              const SizedBox(width: 6),
              Icon(
                Icons.open_in_new_rounded,
                size: 16,
                color: colorScheme.outline.withValues(alpha: 0.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FallbackNewsImage extends StatelessWidget {
  const _FallbackNewsImage({required this.sourceKey});
  final String sourceKey;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 76,
      height: 76,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Icon(Icons.newspaper_rounded, size: 32, color: Colors.grey),
    );
  }
}

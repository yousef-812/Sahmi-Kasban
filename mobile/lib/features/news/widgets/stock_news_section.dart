import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/session_controller.dart';
import '../news_providers.dart';
import 'news_card.dart';

/// سكشن الأخبار المختصر في صفحة تفاصيل السهم (آخر 3 أخبار) — للأدمن فقط
class StockNewsSection extends ConsumerWidget {
  const StockNewsSection({super.key, required this.ticker});
  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isAdmin =
        ref.watch(sessionControllerProvider).profile?.isAdmin == true;
    if (!isAdmin) return const SizedBox.shrink();

    final newsAsync = ref.watch(stockNewsProvider(ticker));
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return newsAsync.when(
      loading: () => const Padding(
        padding: EdgeInsets.all(16),
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (_, __) => const SizedBox.shrink(),
      data: (articles) {
        if (articles.isEmpty) return const SizedBox.shrink();

        final preview = articles.take(3).toList();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // رأس السكشن
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Row(
                children: [
                  Icon(Icons.newspaper_rounded,
                      size: 20, color: colorScheme.primary),
                  const SizedBox(width: 8),
                  Text(
                    'أخبار السهم',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () =>
                        context.push('/stocks/$ticker/news'),
                    child: const Text('عرض الكل'),
                  ),
                ],
              ),
            ),
            // الأخبار المختصرة
            ...preview.map(
              (article) => NewsCard(article: article, compact: true),
            ),
            const SizedBox(height: 8),
          ],
        );
      },
    );
  }
}

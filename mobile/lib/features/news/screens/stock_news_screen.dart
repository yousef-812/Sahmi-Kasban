import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../news_providers.dart';
import '../widgets/news_card.dart';

/// شاشة الأخبار الكاملة لسهم معين
class StockNewsScreen extends ConsumerWidget {
  const StockNewsScreen({super.key, required this.ticker});
  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final newsAsync = ref.watch(stockNewsProvider(ticker));

    return Scaffold(
      appBar: AppBar(
        title: Text('أخبار $ticker'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.invalidate(stockNewsProvider(ticker)),
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: newsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.grey),
              const SizedBox(height: 12),
              Text('تعذّر تحميل الأخبار',
                  style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => ref.invalidate(stockNewsProvider(ticker)),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
        data: (articles) {
          if (articles.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.newspaper_outlined,
                      size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text(
                    'لا توجد أخبار لهذا السهم حالياً',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'سيتم تحديث الأخبار تلقائياً كل 15 دقيقة',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(stockNewsProvider(ticker)),
            child: ListView.builder(
              padding: const EdgeInsets.only(top: 8, bottom: 24),
              itemCount: articles.length,
              itemBuilder: (context, index) =>
                  NewsCard(article: articles[index]),
            ),
          );
        },
      ),
    );
  }
}

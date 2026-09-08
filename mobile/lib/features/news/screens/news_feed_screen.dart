import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../news_providers.dart';
import '../widgets/news_card.dart';

/// تاب الأخبار العامة مع البحث في الـ Dashboard
class NewsFeedScreen extends ConsumerStatefulWidget {
  const NewsFeedScreen({super.key});

  @override
  ConsumerState<NewsFeedScreen> createState() => _NewsFeedScreenState();
}

class _NewsFeedScreenState extends ConsumerState<NewsFeedScreen> {
  late final TextEditingController _searchController;
  Timer? _debounceTimer;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String text) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 350), () {
      if (mounted) {
        ref.read(newsSearchQueryProvider.notifier).state = text.trim();
      }
    });
  }

  void _clearSearch() {
    _searchController.clear();
    _debounceTimer?.cancel();
    ref.read(newsSearchQueryProvider.notifier).state = '';
  }

  @override
  Widget build(BuildContext context) {
    final activeQuery = ref.watch(newsSearchQueryProvider);
    final newsAsync = ref.watch(latestNewsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      body: Column(
        children: [
          // شريط البحث برمز السهم واسم الشركة
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: TextField(
              controller: _searchController,
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: 'ابحث بـ رمز السهم (COMI)، اسم الشركة، أو العنوان...',
                hintStyle: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.7),
                ),
                prefixIcon: Icon(
                  Icons.search_rounded,
                  color: theme.colorScheme.primary,
                ),
                suffixIcon: activeQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear_rounded),
                        onPressed: _clearSearch,
                      )
                    : null,
                filled: true,
                fillColor: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide.none,
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(
                    color: theme.colorScheme.outlineVariant.withValues(alpha: 0.3),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(
                    color: theme.colorScheme.primary,
                    width: 1.5,
                  ),
                ),
              ),
            ),
          ),

          // شريط تفاصيل تصفية البحث إذا تم إدخال استعلام
          if (activeQuery.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  Chip(
                    avatar: const Icon(Icons.filter_list_rounded, size: 16),
                    label: Text('نتائج البحث عن: $activeQuery'),
                    onDeleted: _clearSearch,
                    deleteIcon: const Icon(Icons.cancel_rounded, size: 16),
                    backgroundColor: theme.colorScheme.primaryContainer.withValues(alpha: 0.4),
                  ),
                ],
              ),
            ),

          // قائمة الأخبار أو حالات التحميل/الخطأ
          Expanded(
            child: newsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline_rounded, size: 48, color: Colors.grey),
                    const SizedBox(height: 12),
                    Text(
                      'تعذّر تحميل الأخبار',
                      style: theme.textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () => ref.invalidate(latestNewsProvider),
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
              ),
              data: (articles) {
                if (articles.isEmpty) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            activeQuery.isNotEmpty
                                ? Icons.search_off_rounded
                                : Icons.newspaper_outlined,
                            size: 64,
                            color: Colors.grey,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            activeQuery.isNotEmpty
                                ? 'لا توجد أخبار مطابقة لـ "$activeQuery"'
                                : 'لا توجد أخبار حالياً',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            activeQuery.isNotEmpty
                                ? 'جرّب البحث باسم شركة أخرى أو تيكر السهم مثل: COMI، TMGH، فوري'
                                : 'يتم تحديث الأخبار تلقائياً كل 15 دقيقة',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: Colors.grey,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: () async => ref.invalidate(latestNewsProvider),
                  child: ListView.builder(
                    padding: const EdgeInsets.only(top: 4, bottom: 24),
                    itemCount: articles.length,
                    itemBuilder: (context, index) =>
                        NewsCard(article: articles[index]),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

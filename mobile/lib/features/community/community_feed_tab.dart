import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/avatar_assets.dart';
import 'community_models.dart';
import 'community_providers.dart';

class CommunityFeedTab extends ConsumerStatefulWidget {
  const CommunityFeedTab({super.key});

  @override
  ConsumerState<CommunityFeedTab> createState() => _CommunityFeedTabState();
}

class _CommunityFeedTabState extends ConsumerState<CommunityFeedTab> {
  final _tickerController = TextEditingController();

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  Future<void> _refresh() async {
    ref.invalidate(communityFeedProvider);
    await ref.read(communityFeedProvider.future);
  }

  void _applyTickerFilter() {
    final value = _tickerController.text.trim().toUpperCase();
    ref.read(communityTickerFilterProvider.notifier).state = value.isEmpty
        ? null
        : value;
  }

  void _clearTickerFilter() {
    _tickerController.clear();
    ref.read(communityTickerFilterProvider.notifier).state = null;
  }

  @override
  Widget build(BuildContext context) {
    final feed = ref.watch(communityFeedProvider);
    final activeTicker = ref.watch(communityTickerFilterProvider);

    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: () => context.push('/community/new'),
                  icon: const Icon(Icons.add_comment_outlined),
                  label: const Text('إنشاء مناقشة'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/community/mine'),
                  icon: const Icon(Icons.forum_outlined),
                  label: const Text('مناقشاتي'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _tickerController,
            textCapitalization: TextCapitalization.characters,
            textInputAction: TextInputAction.search,
            decoration: InputDecoration(
              labelText: 'فلترة برمز السهم',
              hintText: 'مثال: COMI',
              prefixIcon: const Icon(Icons.search_rounded),
              suffixIcon: activeTicker == null
                  ? IconButton(
                      onPressed: _applyTickerFilter,
                      icon: const Icon(Icons.tune_rounded),
                      tooltip: 'تطبيق الفلتر',
                    )
                  : IconButton(
                      onPressed: _clearTickerFilter,
                      icon: const Icon(Icons.close_rounded),
                      tooltip: 'إلغاء الفلتر',
                    ),
            ),
            onSubmitted: (_) => _applyTickerFilter(),
          ),
          if (activeTicker != null) ...[
            const SizedBox(height: 10),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Chip(label: Text('السهم: $activeTicker')),
            ),
          ],
          const SizedBox(height: 14),
          feed.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(36),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (error, stackTrace) => _CommunityErrorCard(
              message: 'تعذر تحميل مناقشات المجتمع.',
              onRetry: () => ref.invalidate(communityFeedProvider),
            ),
            data: (page) {
              if (page.items.isEmpty) {
                return const _EmptyCommunityCard();
              }
              return Column(
                children: [
                  for (final discussion in page.items) ...[
                    CommunityDiscussionCard(discussion: discussion),
                    const SizedBox(height: 12),
                  ],
                  if (page.hasMore)
                    const Padding(
                      padding: EdgeInsets.only(top: 4),
                      child: Text(
                        'توجد مناقشات إضافية وسيتم تحميلها في تحديث لاحق للصفحة.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class CommunityDiscussionCard extends StatelessWidget {
  const CommunityDiscussionCard({
    required this.discussion,
    this.showStatus = false,
    super.key,
  });

  final CommunityDiscussion discussion;
  final bool showStatus;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/community/${discussion.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundImage: AssetImage(
                      avatarAssetPath(discussion.author.avatarKey),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          discussion.author.displayName,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        Text(
                          _formatDate(
                            discussion.publishedAt ?? discussion.createdAt,
                          ),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                  Chip(label: Text(discussion.ticker)),
                ],
              ),
              const SizedBox(height: 14),
              Text(
                discussion.title,
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              Text(
                discussion.content,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  Chip(label: Text(discussion.periodLabel)),
                  if (showStatus) Chip(label: Text(discussion.statusLabel)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyCommunityCard extends StatelessWidget {
  const _EmptyCommunityCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(28),
        child: Column(
          children: [
            Icon(Icons.forum_outlined, size: 44),
            SizedBox(height: 12),
            Text(
              'لا توجد مناقشات منشورة تطابق الفلتر الحالي.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _CommunityErrorCard extends StatelessWidget {
  const _CommunityErrorCard({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: onRetry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

String _formatDate(DateTime value) {
  final local = value.toLocal();
  String two(int number) => number.toString().padLeft(2, '0');
  return '${two(local.day)}/${two(local.month)}/${local.year} '
      '${two(local.hour)}:${two(local.minute)}';
}

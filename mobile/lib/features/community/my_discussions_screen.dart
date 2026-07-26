import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'community_feed_tab.dart';
import 'community_models.dart';
import 'community_providers.dart';
import 'prediction_models.dart';
import 'prediction_providers.dart';
import 'prediction_verification_card.dart';

class MyDiscussionsScreen extends ConsumerWidget {
  const MyDiscussionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مناقشاتي'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'المناقشات'),
              Tab(text: 'الاستئنافات'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [_MyDiscussionList(), _MyAppealList()],
        ),
      ),
    );
  }
}

class _MyDiscussionList extends ConsumerWidget {
  const _MyDiscussionList();

  Future<void> _refresh(WidgetRef ref) async {
    ref.invalidate(myDiscussionsProvider);
    ref.invalidate(myPredictionStatsProvider);
    await Future.wait([
      ref.read(myDiscussionsProvider.future),
      ref.read(myPredictionStatsProvider.future),
    ]);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final discussions = ref.watch(myDiscussionsProvider);
    return RefreshIndicator(
      onRefresh: () => _refresh(ref),
      child: discussions.when(
        loading: () => const _LoadingList(),
        error: (error, stackTrace) => _ErrorList(
          message: 'تعذر تحميل مناقشاتك.',
          onRetry: () => ref.invalidate(myDiscussionsProvider),
        ),
        data: (page) {
          if (page.items.isEmpty) {
            return ListView(
              padding: const EdgeInsets.all(16),
              children: const [
                _PredictionStatsSection(),
                SizedBox(height: 60),
                Icon(Icons.forum_outlined, size: 52),
                SizedBox(height: 14),
                Text(
                  'لم ترسل أي مناقشة حتى الآن.',
                  textAlign: TextAlign.center,
                ),
              ],
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const _PredictionStatsSection(),
              const SizedBox(height: 14),
              for (final discussion in page.items) ...[
                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    CommunityDiscussionCard(
                      discussion: discussion,
                      showStatus: true,
                    ),
                    if (discussion.status == 'rejected' &&
                        discussion.rejectionCode != null)
                      Padding(
                        padding: const EdgeInsetsDirectional.only(
                          start: 16,
                          end: 16,
                          top: 6,
                        ),
                        child: Text(
                          'سبب الرفض: ${discussion.rejectionCode}',
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                    if (discussion.status == 'published') ...[
                      const SizedBox(height: 8),
                      PredictionVerificationCard(
                        discussionId: discussion.id,
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 12),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _PredictionStatsSection extends ConsumerWidget {
  const _PredictionStatsSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stats = ref.watch(myPredictionStatsProvider);
    return stats.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(18),
          child: LinearProgressIndicator(),
        ),
      ),
      error: (error, stackTrace) => Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              const Expanded(child: Text('تعذر تحميل إحصاءات التوقعات.')),
              TextButton(
                onPressed: () => ref.invalidate(myPredictionStatsProvider),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
      data: (value) => _PredictionStatsCard(stats: value),
    );
  }
}

class _PredictionStatsCard extends StatelessWidget {
  const _PredictionStatsCard({required this.stats});

  final PredictionStats stats;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'أداء توقعاتي',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text('تم التحقق: ${stats.verifiedPredictions}')),
                Chip(
                  label: Text(
                    'نسبة القبول: ${stats.accuracyPercent.toStringAsFixed(1)}%',
                  ),
                ),
                Chip(
                  label: Text(
                    'متوسط الدرجة: '
                    '${stats.averageScorePercent.toStringAsFixed(1)}%',
                  ),
                ),
                Chip(
                  label: Text('إجمالي المكافآت: ${stats.totalRewardCoins} عملة'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MyAppealList extends ConsumerWidget {
  const _MyAppealList();

  Future<void> _refresh(WidgetRef ref) async {
    ref.invalidate(myAppealsProvider);
    await ref.read(myAppealsProvider.future);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appeals = ref.watch(myAppealsProvider);
    return RefreshIndicator(
      onRefresh: () => _refresh(ref),
      child: appeals.when(
        loading: () => const _LoadingList(),
        error: (error, stackTrace) => _ErrorList(
          message: 'تعذر تحميل الاستئنافات.',
          onRetry: () => ref.invalidate(myAppealsProvider),
        ),
        data: (page) {
          if (page.items.isEmpty) {
            return const _EmptyList(
              icon: Icons.gavel_outlined,
              message: 'لا توجد استئنافات مسجلة.',
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: page.items.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) =>
                _AppealCard(appeal: page.items[index]),
          );
        },
      ),
    );
  }
}

class _AppealCard extends StatelessWidget {
  const _AppealCard({required this.appeal});

  final CommunityAppeal appeal;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'استئناف مناقشة',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Chip(label: Text(appeal.statusLabel)),
              ],
            ),
            const SizedBox(height: 8),
            Text('الحالة الأصلية: ${_sourceStatusLabel(appeal.sourceStatus)}'),
            const SizedBox(height: 10),
            Text(appeal.message),
            if (appeal.resolutionReasonCode != null) ...[
              const SizedBox(height: 10),
              Text('سبب القرار: ${appeal.resolutionReasonCode}'),
            ],
            if (appeal.resolutionDetails.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                appeal.resolutionDetails.toString(),
                textDirection: TextDirection.ltr,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _LoadingList extends StatelessWidget {
  const _LoadingList();

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: const [
        SizedBox(height: 220),
        Center(child: CircularProgressIndicator()),
      ],
    );
  }
}

class _EmptyList extends StatelessWidget {
  const _EmptyList({required this.icon, required this.message});

  final IconData icon;
  final String message;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SizedBox(height: 100),
        Icon(icon, size: 52),
        const SizedBox(height: 14),
        Text(message, textAlign: TextAlign.center),
      ],
    );
  }
}

class _ErrorList extends StatelessWidget {
  const _ErrorList({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SizedBox(height: 80),
        Text(message, textAlign: TextAlign.center),
        const SizedBox(height: 14),
        Center(
          child: OutlinedButton(
            onPressed: onRetry,
            child: const Text('إعادة المحاولة'),
          ),
        ),
      ],
    );
  }
}

String _sourceStatusLabel(String status) {
  return switch (status) {
    'rejected' => 'مرفوضة',
    'hidden' => 'مخفية',
    _ => status,
  };
}

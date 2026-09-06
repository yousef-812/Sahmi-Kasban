import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/avatar_assets.dart';
import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import '../monetization/free_plan_ads.dart';
import '../auth/session_controller.dart';
import 'community_models.dart';
import 'community_providers.dart';
import 'community_repository.dart';
import 'screens/user_profile_screen.dart';

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

    return Stack(
      children: [
        RefreshIndicator(
          onRefresh: _refresh,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: Theme.of(context)
                      .colorScheme
                      .primaryContainer
                      .withValues(alpha: 0.35),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: Theme.of(context)
                        .colorScheme
                        .primary
                        .withValues(alpha: 0.2),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.tips_and_updates_outlined,
                      color: Theme.of(context).colorScheme.primary,
                      size: 22,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'المناقشات والتوقعات مجانية بالكامل. شارك توقعك مع مجتمع المتداولين لتوثيق دقة تحليلاتك.',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
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
                      icon: const Icon(Icons.history_edu_rounded),
                      label: const Text('مناقشاتي'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Card(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  child: Row(
                    children: [
                      const Icon(Icons.search_rounded),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextField(
                          controller: _tickerController,
                          textCapitalization: TextCapitalization.characters,
                          decoration: const InputDecoration(
                            hintText: 'تصفية حسب سهم (مثال: COMI)',
                            border: InputBorder.none,
                            enabledBorder: InputBorder.none,
                            focusedBorder: InputBorder.none,
                          ),
                          onSubmitted: (_) => _applyTickerFilter(),
                        ),
                      ),
                      if (activeTicker != null)
                        IconButton(
                          icon: const Icon(Icons.close_rounded),
                          onPressed: _clearTickerFilter,
                        )
                      else
                        IconButton(
                          icon: const Icon(Icons.arrow_forward_rounded),
                          onPressed: _applyTickerFilter,
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              feed.when(
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (error, stack) => _CommunityErrorCard(
                  message: error.toString(),
                  onRetry: _refresh,
                ),
                data: (data) {
                  final discussions = data.items;
                  if (discussions.isEmpty) {
                    return const _EmptyCommunityCard();
                  }

                  return Column(
                    children: [
                      for (final item in discussions)
                        CommunityDiscussionCard(discussion: item),
                      const SizedBox(height: 12),
                      const FreePlanNativeAd(),
                      const SizedBox(height: 12),
                      if (data.hasMore)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8),
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
        ),
        const _DraggableTelegramBall(),
      ],
    );
  }
}

final _registeredFeedViewIds = <String>{};

class CommunityDiscussionCard extends ConsumerStatefulWidget {
  const CommunityDiscussionCard({
    required this.discussion,
    this.showStatus = false,
    super.key,
  });

  final CommunityDiscussion discussion;
  final bool showStatus;

  @override
  ConsumerState<CommunityDiscussionCard> createState() =>
      _CommunityDiscussionCardState();
}

class _CommunityDiscussionCardState
    extends ConsumerState<CommunityDiscussionCard> {
  @override
  void initState() {
    super.initState();
    _registerImpression();
  }

  @override
  void didUpdateWidget(covariant CommunityDiscussionCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    _registerImpression();
  }

  void _registerImpression() {
    final id = widget.discussion.id;
    if (!_registeredFeedViewIds.contains(id)) {
      _registeredFeedViewIds.add(id);
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(communityRepositoryProvider).registerViews([id]);
      });
    }
  }

  Future<void> _toggleReaction(String reactionType) async {
    try {
      await ref.read(communityRepositoryProvider).toggleReaction(
        discussionId: widget.discussion.id,
        reactionType: reactionType,
      );
      ref.invalidate(communityFeedProvider);
      ref.invalidate(myDiscussionsProvider);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final discussion = widget.discussion;
    final currentUserId = ref.watch(sessionControllerProvider).profile?.id;
    final isAuthor =
        currentUserId != null && discussion.author.userId == currentUserId;

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/community/${discussion.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (discussion.isPinned)
                Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.amber.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.amber.withValues(alpha: 0.4)),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.push_pin_rounded, color: Colors.amber, size: 14),
                      SizedBox(width: 6),
                      Text(
                        'منشور مثبت ومميز',
                        style: TextStyle(
                          color: Colors.amber,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              Row(
                children: [
                  GestureDetector(
                    onTap: () {
                      Navigator.of(context).push(
                        UserProfileScreen.route(
                          userId: discussion.author.userId,
                          initialDisplayName: discussion.author.displayName,
                          initialAvatarKey: discussion.author.avatarKey,
                        ),
                      );
                    },
                    child: CircleAvatar(
                      backgroundImage: AssetImage(
                        avatarAssetPath(discussion.author.avatarKey),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: InkWell(
                      onTap: () {
                        Navigator.of(context).push(
                          UserProfileScreen.route(
                            userId: discussion.author.userId,
                            initialDisplayName: discussion.author.displayName,
                            initialAvatarKey: discussion.author.avatarKey,
                          ),
                        );
                      },
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            discussion.author.displayName,
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Text(
                                '${discussion.author.predictionsCount} توقع',
                                style: const TextStyle(fontSize: 10, color: Colors.grey),
                              ),
                              const SizedBox(width: 6),
                              Text(
                                'نجاح: ${discussion.author.successRate.toStringAsFixed(0)}%',
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Colors.green,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(width: 6),
                              Text(
                                _formatDate(
                                  discussion.publishedAt ?? discussion.createdAt,
                                ),
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  if (!isAuthor)
                    TextButton(
                      onPressed: () async {
                        try {
                          await ref.read(communityRepositoryProvider).toggleFollow(discussion.author.userId);
                          ref.invalidate(communityFeedProvider);
                        } catch (_) {}
                      },
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        discussion.author.isFollowing ? 'متابَع' : '+ متابعة',
                        style: TextStyle(
                          fontSize: 12,
                          color: discussion.author.isFollowing ? Colors.grey : Theme.of(context).colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  const SizedBox(width: 4),
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
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Chip(label: Text(discussion.periodLabel)),
                  if (widget.showStatus)
                    Chip(label: Text(discussion.statusLabel)),
                  if (isAuthor)
                    Chip(
                      avatar: const Icon(
                        Icons.remove_red_eye_outlined,
                        size: 14,
                      ),
                      label: Text('${discussion.viewsCount} مشاهدة'),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: discussion.userReaction == 'agree'
                        ? FilledButton(
                            onPressed: () => _toggleReaction('agree'),
                            style: FilledButton.styleFrom(
                              visualDensity: VisualDensity.compact,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 4,
                              ),
                            ),
                            child: Text('متفق (${discussion.agreeCount})'),
                          )
                        : OutlinedButton(
                            onPressed: () => _toggleReaction('agree'),
                            style: OutlinedButton.styleFrom(
                              visualDensity: VisualDensity.compact,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 4,
                              ),
                            ),
                            child: Text('متفق (${discussion.agreeCount})'),
                          ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: discussion.userReaction == 'disagree'
                        ? FilledButton(
                            onPressed: () => _toggleReaction('disagree'),
                            style: FilledButton.styleFrom(
                              visualDensity: VisualDensity.compact,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 4,
                              ),
                            ),
                            child: Text('غير متفق (${discussion.disagreeCount})'),
                          )
                        : OutlinedButton(
                            onPressed: () => _toggleReaction('disagree'),
                            style: OutlinedButton.styleFrom(
                              visualDensity: VisualDensity.compact,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 4,
                              ),
                            ),
                            child: Text('غير متفق (${discussion.disagreeCount})'),
                          ),
                  ),
                ],
              ),
              if (isAuthor && !discussion.isPinned && discussion.status == 'published') ...[
                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: () async {
                    try {
                      await ref.read(communityRepositoryProvider).pinDiscussion(discussion.id);
                      ref.invalidate(communityFeedProvider);
                      if (context.mounted) {
                        AppNotice.show(
                          context,
                          title: 'تم التثبيت',
                          message: 'تم تثبيت وإبراز المنشور بنجاح في أعلى المجتمع.',
                          tone: AppNoticeTone.success,
                        );
                      }
                    } on ApiException catch (e) {
                      if (context.mounted) {
                        AppNotice.show(
                          context,
                          title: 'تعذر التثبيت',
                          message: e.message,
                          tone: AppNoticeTone.error,
                        );
                      }
                    } catch (_) {
                      if (context.mounted) {
                        AppNotice.show(
                          context,
                          title: 'تعذر التثبيت',
                          message: 'عذراً، انتهت المهلة. لا يمكن تثبيت أو ترقية المنشور بعد بدء الجلسة التجارية للتوقع.',
                          tone: AppNoticeTone.error,
                        );
                      }
                    }
                  },
                  style: OutlinedButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    foregroundColor: Colors.amber,
                    side: const BorderSide(color: Colors.amber),
                  ),
                  icon: const Icon(Icons.push_pin_outlined, size: 14),
                  label: const Text(
                    'تثبيت وإبراز المنشور',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
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

class _DraggableTelegramBall extends StatefulWidget {
  const _DraggableTelegramBall();

  @override
  State<_DraggableTelegramBall> createState() => _DraggableTelegramBallState();
}

class _DraggableTelegramBallState extends State<_DraggableTelegramBall> {
  double? _top;
  double? _left;

  Future<void> _openTelegramGroup() async {
    final uri = Uri.parse('https://t.me/sahmikasban');
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    } on Object {
      // Fallback open attempt
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    _top ??= size.height * 0.55;
    _left ??= size.width - 70;

    return Positioned(
      top: _top,
      left: _left,
      child: GestureDetector(
        onPanUpdate: (details) {
          setState(() {
            _top = (_top! + details.delta.dy).clamp(60.0, size.height - 140.0);
            _left = (_left! + details.delta.dx).clamp(10.0, size.width - 64.0);
          });
        },
        child: Tooltip(
          message: 'انضم لجروب التليجرام',
          child: Material(
            elevation: 8,
            shadowColor: const Color(0xFF0088CC).withOpacity(0.5),
            shape: const CircleBorder(),
            clipBehavior: Clip.antiAlias,
            child: InkWell(
              onTap: _openTelegramGroup,
              child: Container(
                width: 54,
                height: 54,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [Color(0xFF2AABEE), Color(0xFF229ED9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: const Center(
                  child: Icon(
                    Icons.send_rounded,
                    color: Colors.white,
                    size: 26,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../community_models.dart';
import '../community_providers.dart';
import '../community_repository.dart';
import '../widgets/coin_tipping_dialog.dart';
import '../../core/avatar_assets.dart';

final userDiscussionsProvider =
    FutureProvider.family<List<CommunityDiscussion>, String>((ref, userId) async {
  final repository = ref.watch(communityRepositoryProvider);
  final page = await repository.listDiscussions(limit: 50);
  return page.items.where((item) => item.author.userId == userId).toList();
});

class UserProfileScreen extends ConsumerStatefulWidget {
  const UserProfileScreen({
    super.key,
    required this.userId,
    this.initialDisplayName,
    this.initialAvatarKey,
  });

  final String userId;
  final String? initialDisplayName;
  final String? initialAvatarKey;

  static Route<void> route({
    required String userId,
    String? initialDisplayName,
    String? initialAvatarKey,
  }) {
    return MaterialPageRoute<void>(
      builder: (_) => UserProfileScreen(
        userId: userId,
        initialDisplayName: initialDisplayName,
        initialAvatarKey: initialAvatarKey,
      ),
    );
  }

  @override
  ConsumerState<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends ConsumerState<UserProfileScreen> {
  bool _isTogglingFollow = false;

  Future<void> _handleFollowToggle(UserPublicProfile profile) async {
    if (_isTogglingFollow) return;

    setState(() {
      _isTogglingFollow = true;
    });

    try {
      final repo = ref.read(communityRepositoryProvider);
      await repo.toggleFollow(profile.userId);
      ref.invalidate(userPublicProfileProvider(widget.userId));
      ref.invalidate(communityFeedProvider);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('حدث خطأ أثناء الحديث: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isTogglingFollow = false;
        });
      }
    }
  }

  void _showTippingInfoDialog(UserPublicProfile profile) {
    String reason = '';
    if (!profile.isFollowing) {
      reason = 'يجب متابعة المحلل أولاً لإمكانية إهداء العملات.';
    } else if (!profile.canReceiveTips) {
      reason = 'المحلل لم يفعل استقبال هدايا العملات في حسابه بعد.';
    } else {
      reason = 'يجب أن يكون لديك 10 مناقشات منشورين على الأقل لإهداء العملات.';
    }

    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text(
          'شروط إهداء العملات',
          textAlign: TextAlign.center,
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              reason,
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 12),
            const Text(
              'شروط الإهداء:\n'
              '1. متابعة المحلل.\n'
              '2. وجود 10 مناقشات في حسابك.\n'
              '3. استيفاء المحلل لشرط الأهلية (20+ توقع بنسبة نجاح > 70%).',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final profileAsync = ref.watch(userPublicProfileProvider(widget.userId));
    final discussionsAsync = ref.watch(userDiscussionsProvider(widget.userId));

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.initialDisplayName ?? 'الملف الشخصي'),
        centerTitle: true,
      ),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 12),
              Text('حدث خطأ في تحميل البيانات: $err'),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () => ref.refresh(userPublicProfileProvider(widget.userId)),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
        data: (profile) {
          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(userPublicProfileProvider(widget.userId));
              ref.invalidate(userDiscussionsProvider(widget.userId));
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // User Header Card
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          CircleAvatar(
                            radius: 40,
                            backgroundColor: theme.colorScheme.primaryContainer,
                            backgroundImage:
                                AssetImage(avatarAssetPath(profile.avatarKey)),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            profile.displayName,
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'محلل في مجتمع سهمي كسبان',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: Colors.grey,
                            ),
                          ),
                          if (profile.bio != null && profile.bio!.isNotEmpty) ...[
                            const SizedBox(height: 10),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: theme.colorScheme.surfaceContainerHighest,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                profile.bio!,
                                textAlign: TextAlign.center,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ),
                          ],
                          const SizedBox(height: 20),

                          // Profile Metrics Grid
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              InkWell(
                                onTap: () => context.push(
                                  '/community/users/${profile.userId}/followers',
                                ),
                                borderRadius: BorderRadius.circular(8),
                                child: _MetricTile(
                                  label: 'المتابعون',
                                  value: '${profile.followersCount}',
                                  icon: Icons.group,
                                ),
                              ),
                              InkWell(
                                onTap: () => context.push(
                                  '/community/users/${profile.userId}/following',
                                ),
                                borderRadius: BorderRadius.circular(8),
                                child: _MetricTile(
                                  label: 'يتابع',
                                  value: '${profile.followingCount}',
                                  icon: Icons.person_add_alt_1,
                                ),
                              ),
                              _MetricTile(
                                label: 'التوقعات',
                                value: '${profile.predictionsCount}',
                                icon: Icons.analytics,
                              ),
                              _MetricTile(
                                label: 'نسبة النجاح',
                                value: '${profile.successRate.toStringAsFixed(0)}%',
                                icon: Icons.verified,
                                isAccent: true,
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),

                          // Action Buttons
                          Row(
                            children: [
                              // Follow / Unfollow Button
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: _isTogglingFollow
                                      ? null
                                      : () => _handleFollowToggle(profile),
                                  icon: _isTogglingFollow
                                      ? const SizedBox(
                                          width: 16,
                                          height: 16,
                                          child: CircularProgressIndicator(strokeWidth: 2),
                                        )
                                      : Icon(
                                          profile.isFollowing
                                              ? Icons.check_circle_outline
                                              : Icons.person_add_outlined,
                                        ),
                                  label: Text(
                                    profile.isFollowing ? 'متابَع' : 'متابعة',
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  style: ElevatedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                    backgroundColor: profile.isFollowing
                                        ? theme.colorScheme.surfaceContainerHighest
                                        : theme.colorScheme.primary,
                                    foregroundColor: profile.isFollowing
                                        ? theme.colorScheme.onSurfaceVariant
                                        : theme.colorScheme.onPrimary,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),

                              // Gift Coins Button
                              Expanded(
                                child: OutlinedButton.icon(
                                  onPressed: profile.canSendTip
                                      ? () async {
                                          final tipped = await CoinTippingDialog.show(context, profile);
                                          if (tipped == true) {
                                            ref.invalidate(userPublicProfileProvider(widget.userId));
                                          }
                                        }
                                      : () => _showTippingInfoDialog(profile),
                                  icon: Icon(
                                    Icons.monetization_on_outlined,
                                    color: profile.canSendTip ? Colors.amber : Colors.grey,
                                  ),
                                  label: Text(
                                    'إهداء عملات',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: profile.canSendTip
                                          ? theme.colorScheme.primary
                                          : Colors.grey,
                                    ),
                                  ),
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                    side: BorderSide(
                                      color: profile.canSendTip
                                          ? theme.colorScheme.primary
                                          : Colors.grey.shade400,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Discussions Section Header
                  Align(
                    alignment: Alignment.centerRight,
                    child: Text(
                      'توقعات ومناقشات المحلل',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Discussions List
                  discussionsAsync.when(
                    loading: () => const Padding(
                      padding: EdgeInsets.all(24),
                      child: CircularProgressIndicator(),
                    ),
                    error: (err, _) => Padding(
                      padding: const EdgeInsets.all(16),
                      child: Text('عفواً، تعذر جلب المناقشات: $err'),
                    ),
                    data: (discussions) {
                      if (discussions.isEmpty) {
                        return Card(
                          margin: const EdgeInsets.symmetric(vertical: 8),
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Center(
                              child: Column(
                                children: const [
                                  Icon(Icons.forum_outlined, size: 40, color: Colors.grey),
                                  SizedBox(height: 8),
                                  Text(
                                    'لم ينشر هذا المحلل أي مناقشات بعد.',
                                    style: TextStyle(color: Colors.grey),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        );
                      }

                      return ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: discussions.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final item = discussions[index];
                          return Card(
                            elevation: 1,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(16),
                              title: Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: theme.colorScheme.primaryContainer,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      item.ticker,
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: theme.colorScheme.onPrimaryContainer,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      item.title,
                                      style: const TextStyle(fontWeight: FontWeight.bold),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 8),
                                child: Text(
                                  item.content,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(color: Colors.grey.shade700),
                                ),
                              ),
                              onTap: () {
                                context.push('/community/${item.id}');
                              },
                            ),
                          );
                        },
                      );
                    },
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({
    required this.label,
    required this.value,
    required this.icon,
    this.isAccent = false,
  });

  final String label;
  final String value;
  final IconData icon;
  final bool isAccent;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      children: [
        Icon(
          icon,
          size: 20,
          color: isAccent ? Colors.green : theme.colorScheme.primary,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: isAccent ? Colors.green : null,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }
}

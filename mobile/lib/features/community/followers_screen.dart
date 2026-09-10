import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../auth/session_controller.dart';
import 'community_models.dart';
import 'community_providers.dart';
import 'community_repository.dart';
import 'screens/user_profile_screen.dart';

enum FollowListMode { followers, following }

class FollowersScreen extends ConsumerWidget {
  const FollowersScreen({
    super.key,
    required this.userId,
    required this.mode,
  });

  final String userId;
  final FollowListMode mode;

  bool get _isFollowers => mode == FollowListMode.followers;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final listAsync = ref.watch(
      _isFollowers ? followersProvider(userId) : followingProvider(userId),
    );
    final currentUserId = ref.watch(sessionControllerProvider).profile?.id;

    return Scaffold(
      appBar: AppBar(
        title: Text(_isFollowers ? 'المتابعون' : 'المتابَعون'),
        centerTitle: true,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(
            _isFollowers ? followersProvider(userId) : followingProvider(userId),
          );
        },
        child: listAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => ListView(
            padding: const EdgeInsets.all(24),
            children: [
              const SizedBox(height: 80),
              const Icon(Icons.error_outline, size: 40, color: Colors.grey),
              const SizedBox(height: 12),
              Text(
                'تعذر تحميل القائمة: $error',
                textAlign: TextAlign.center,
              ),
            ],
          ),
          data: (page) {
            if (page.items.isEmpty) {
              return ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  const SizedBox(height: 100),
                  Icon(
                    _isFollowers
                        ? Icons.group_outlined
                        : Icons.person_add_alt_1_outlined,
                    size: 52,
                    color: Colors.grey,
                  ),
                  const SizedBox(height: 14),
                  Text(
                    _isFollowers
                        ? 'لا يوجد متابعون بعد.'
                        : 'لا يتابع أحدًا بعد.',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: page.items.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final item = page.items[index];
                final isSelf = item.userId == currentUserId;
                return _FollowUserTile(
                  item: item,
                  isSelf: isSelf,
                  mode: mode,
                  onFollowChanged: () {
                    ref.invalidate(
                      _isFollowers
                          ? followersProvider(userId)
                          : followingProvider(userId),
                    );
                    ref.invalidate(userPublicProfileProvider(userId));
                  },
                );
              },
            );
          },
        ),
      ),
    );
  }
}

class _FollowUserTile extends ConsumerWidget {
  const _FollowUserTile({
    required this.item,
    required this.isSelf,
    required this.mode,
    required this.onFollowChanged,
  });

  final UserFollowItem item;
  final bool isSelf;
  final FollowListMode mode;
  final VoidCallback onFollowChanged;

  String get _buttonLabel {
    if (item.isFollowing) return 'متابَع';
    return mode == FollowListMode.followers ? 'رد متابعة' : 'متابعة';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    return InkWell(
      onTap: () {
        Navigator.of(context).push(
          UserProfileScreen.route(
            userId: item.userId,
            initialDisplayName: item.displayName,
            initialAvatarKey: item.avatarKey,
          ),
        );
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        child: Row(
          children: [
            CircleAvatar(
              backgroundImage: AssetImage(avatarAssetPath(item.avatarKey)),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                item.displayName,
                style: TextStyle(
                  fontWeight: FontWeight.w700,
                  color: colorScheme.onSurface,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (!isSelf) ...[
              const SizedBox(width: 8),
              _busyButton(context, ref),
            ],
          ],
        ),
      ),
    );
  }

  Widget _busyButton(BuildContext context, WidgetRef ref) {
    return FollowButton(
      isFollowing: item.isFollowing,
      label: _buttonLabel,
      onPressed: () async {
        try {
          await ref.read(communityRepositoryProvider).toggleFollow(item.userId);
          onFollowChanged();
        } on Object catch (error) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('حدث خطأ أثناء التحديث: $error')),
            );
          }
        }
      },
    );
  }
}

class FollowButton extends StatefulWidget {
  const FollowButton({
    super.key,
    required this.isFollowing,
    required this.label,
    required this.onPressed,
  });

  final bool isFollowing;
  final String label;
  final Future<void> Function() onPressed;

  @override
  State<FollowButton> createState() => _FollowButtonState();
}

class _FollowButtonState extends State<FollowButton> {
  bool _busy = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return _busy
        ? const SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(strokeWidth: 2),
          )
        : widget.isFollowing
        ? OutlinedButton(
            onPressed: () async {
              setState(() => _busy = true);
              try {
                await widget.onPressed();
              } finally {
                if (mounted) setState(() => _busy = false);
              }
            },
            style: OutlinedButton.styleFrom(
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            ),
            child: Text(widget.label),
          )
        : FilledButton(
            onPressed: () async {
              setState(() => _busy = true);
              try {
                await widget.onPressed();
              } finally {
                if (mounted) setState(() => _busy = false);
              }
            },
            style: FilledButton.styleFrom(
              visualDensity: VisualDensity.compact,
              backgroundColor: theme.colorScheme.primary,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            ),
            child: Text(widget.label),
          );
  }
}
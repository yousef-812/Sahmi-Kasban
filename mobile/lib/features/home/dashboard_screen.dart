import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_theme_provider.dart';
import '../../core/avatar_assets.dart';
import '../../domain/models.dart';
import '../../core/network/api_client.dart';
import '../../core/network/api_exception.dart';
import '../app_version/version_check_manager.dart';
import '../auth/session_controller.dart';
import '../community/community_feed_tab.dart';
import '../community/community_models.dart';
import '../community/community_providers.dart';
import '../community/community_repository.dart';
import '../market/stock_analysis_tab.dart';
import '../market/stocks_screen.dart';
import '../news/screens/news_feed_screen.dart';
import '../notifications/notification_providers.dart';
import '../reports/reports_screen.dart';

final dashboardTabProvider = StateProvider<int>((ref) => 0);

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future<void>.microtask(() {
      if (mounted) {
        ref.read(versionCheckManagerProvider).checkAndShowPrompt(context);
      }
    });
  }

  static const _navItems = <(String, IconData, String)>[
    ('stocks', Icons.home_rounded, 'الرئيسية'),
    ('reports', Icons.assessment_outlined, 'التقارير'),
    ('news', Icons.newspaper_rounded, 'الأخبار'),
    ('analyze', Icons.query_stats_outlined, 'تحليل سهم'),
    ('community', Icons.forum_outlined, 'المجتمع'),
    ('profile', Icons.person_outline_rounded, 'الملف الشخصي'),
  ];

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(sessionControllerProvider).profile;
    final selectedIndex = ref.watch(dashboardTabProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(_navItems[selectedIndex].$3),
        actions: [
          if (profile?.isAdmin == true)
            IconButton(
              onPressed: () => context.push('/admin'),
              icon: const Icon(Icons.admin_panel_settings_outlined),
              tooltip: 'الإدارة',
            ),
          IconButton(
            onPressed: () => context.push('/ai-copilot'),
            icon: const Icon(Icons.auto_awesome_rounded),
            tooltip: 'مساعد الذكاء الاصطناعي',
          ),
          IconButton(
            onPressed: () => context.push('/performance'),
            icon: const Icon(Icons.assessment_outlined),
            tooltip: 'سجل الأداء',
          ),
          IconButton(
            onPressed: () => context.push('/notifications'),
            icon: Badge(
              isLabelVisible:
                  ref
                      .watch(notificationInboxProvider)
                      .valueOrNull
                      ?.unreadCount !=
                  0,
              label: Text(
                '${ref.watch(notificationInboxProvider).valueOrNull?.unreadCount ?? 0}',
              ),
              child: const Icon(Icons.notifications_outlined),
            ),
            tooltip: 'الإشعارات',
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            _DrawerHeader(profile: profile),
            const Divider(),
            ListTile(
              leading: const Icon(
                Icons.auto_awesome_rounded,
                color: Colors.purpleAccent,
              ),
              title: const Text('مساعد السهم الذكي (AI)'),
              subtitle: const Text('استفسار مباشر عن أي سهم'),
              onTap: () {
                context.push('/ai-copilot');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(
                Icons.forum_rounded,
                color: Color(0xFF0088CC),
              ),
              title: const Text('غرفة الدردشة المباشرة (شات الجلسة)'),
              subtitle: const Text('دردشة الجلسة المشروطة بـ 40 صوتًا'),
              onTap: () {
                context.push('/trading-chat');
                Navigator.pop(context);
              },
            ),
            const Divider(),
            for (var item in _navItems)
              ListTile(
                leading: Icon(item.$2),
                title: Text(item.$3),
                selected: selectedIndex == _navItems.indexOf(item),
                onTap: () {
                  ref.read(dashboardTabProvider.notifier).state =
                      _navItems.indexOf(item);
                  Navigator.pop(context);
                },
              ),
            const Divider(),
            ListTile(
              leading: const Icon(
                Icons.card_giftcard_rounded,
                color: Colors.orangeAccent,
              ),
              title: const Text('دعوة الأصدقاء'),
              subtitle: const Text('احصل على 10 عملات لك ولصديقك'),
              onTap: () {
                context.push('/referrals');
                Navigator.pop(context);
              },
            ),
            if (profile?.isAdmin == true) ...[
              const Divider(),
              ListTile(
                leading: const Icon(Icons.admin_panel_settings_outlined),
                title: const Text('لوحة الإدارة'),
                onTap: () {
                  context.push('/admin');
                  Navigator.pop(context);
                },
              ),
            ],
          ],
        ),
      ),
      body: Stack(
        children: [
          _buildBody(selectedIndex),
          const _DraggableTradingRoomBall(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: (index) {
          ref.read(dashboardTabProvider.notifier).state = index;
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'الرئيسية',
          ),
          NavigationDestination(
            icon: Icon(Icons.assessment_outlined),
            selectedIcon: Icon(Icons.assessment_rounded),
            label: 'التقارير',
          ),
          NavigationDestination(
            icon: Icon(Icons.newspaper_outlined),
            selectedIcon: Icon(Icons.newspaper_rounded),
            label: 'الأخبار',
          ),
          NavigationDestination(
            icon: Icon(Icons.query_stats_outlined),
            selectedIcon: Icon(Icons.query_stats_rounded),
            label: 'تحليل سهم',
          ),
          NavigationDestination(
            icon: Icon(Icons.forum_outlined),
            selectedIcon: Icon(Icons.forum_rounded),
            label: 'المجتمع',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'الملف الشخصي',
          ),
        ],
      ),
    );
  }

  Widget _buildBody(int selectedIndex) {
    switch (selectedIndex) {
      case 0:
        return const StocksScreen();
      case 1:
        return const ReportsScreen();
      case 2:
        return const NewsFeedScreen();
      case 3:
        return const StockAnalysisTab();
      case 4:
        return const CommunityFeedTab();
      case 5:
        return const ProfileTab();
      default:
        return const StocksScreen();
    }
  }
}

class _DrawerHeader extends StatelessWidget {
  const _DrawerHeader({required this.profile});
  final UserProfile? profile;

  @override
  Widget build(BuildContext context) {
    return UserAccountsDrawerHeader(
      currentAccountPicture: CircleAvatar(
        backgroundImage: AssetImage(
          avatarAssetPath(profile?.avatarKey ?? avatarKeys.first),
        ),
      ),
      accountName: Text(profile?.displayName ?? 'مستخدم'),
      accountEmail: Text(profile?.email ?? ''),
    );
  }
}

class ProfileTab extends ConsumerWidget {
  const ProfileTab({super.key});

  static const _statusLabels = <String, String>{
    'published': 'منشور',
    'pending': 'قيد المراجعة',
    'rejected': 'مرفوض',
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(sessionControllerProvider).profile;
    if (profile == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final publicProfileAsync = ref.watch(userPublicProfileProvider(profile.id));
    final discussionsAsync = ref.watch(myDiscussionsProvider);
    final theme = Theme.of(context);
    final publicProfile = publicProfileAsync.valueOrNull;

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(userPublicProfileProvider(profile.id));
        ref.invalidate(myDiscussionsProvider);
      },
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(22),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 48,
                    backgroundImage: AssetImage(
                      avatarAssetPath(profile.avatarKey),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    profile.displayName,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    profile.email,
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.bodyMedium,
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
                  const SizedBox(height: 12),
                  Text('الخطة: ${profile.planCode}'),
                  Text('الرصيد: ${profile.balanceCoins} عملة'),
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () => context.push('/wallet'),
                          icon: const Icon(Icons.account_balance_wallet_rounded),
                          label: const Text('المحفظة'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => context.push('/profile/edit'),
                          icon: const Icon(Icons.edit_outlined),
                          label: const Text('تعديل الملف'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    onPressed: () =>
                        ref.read(sessionControllerProvider.notifier).logout(),
                    icon: const Icon(Icons.logout_rounded),
                    label: const Text('تسجيل الخروج'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Stats
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _ProfileStat(
                    label: 'المتابعون',
                    value: '${publicProfile?.followersCount ?? 0}',
                    icon: Icons.group,
                    valueColor: theme.colorScheme.primary,
                    onTap: () => context.push(
                      '/community/users/${profile.id}/followers',
                    ),
                  ),
                  _ProfileStat(
                    label: 'يتابع',
                    value: '${publicProfile?.followingCount ?? 0}',
                    icon: Icons.person_add_alt_1,
                    valueColor: theme.colorScheme.primary,
                    onTap: () => context.push(
                      '/community/users/${profile.id}/following',
                    ),
                  ),
                  _ProfileStat(
                    label: 'التوقعات',
                    value: '${publicProfile?.predictionsCount ?? 0}',
                    icon: Icons.analytics,
                    valueColor: theme.colorScheme.primary,
                  ),
                  _ProfileStat(
                    label: 'نسبة النجاح',
                    value:
                        '${(publicProfile?.successRate ?? 0).toStringAsFixed(0)}%',
                    icon: Icons.verified,
                    valueColor: Colors.green,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // My discussions
          Align(
            alignment: Alignment.centerRight,
            child: Text(
              'مناقشاتي',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          discussionsAsync.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(24),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (err, _) => Padding(
              padding: const EdgeInsets.all(16),
              child: Text('عفواً، تعذر جلب المناقشات: $err'),
            ),
            data: (discussions) {
              if (discussions.items.isEmpty) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: const [
                        Icon(
                          Icons.forum_outlined,
                          size: 40,
                          color: Colors.grey,
                        ),
                        SizedBox(height: 8),
                        Text(
                          'لم تنشر أي مناقشات بعد.',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                );
              }
              return Column(
                children: [
                  for (final discussion in discussions.items) ...[
                    _MyDiscussionCard(
                      discussion: discussion,
                      statusLabel: _statusLabels[discussion.status] ??
                          discussion.status,
                      onDelete: () =>
                          _confirmDelete(context, ref, discussion, profile.id),
                    ),
                    const SizedBox(height: 10),
                  ],
                ],
              );
            },
          ),
          const SizedBox(height: 16),

          const _ThemeSettingsCard(),
          const SizedBox(height: 16),
          const _DeveloperFeedbackCard(),
        ],
      ),
    );
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    CommunityDiscussion discussion,
    String userId,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('حذف المناقشة'),
        content: const Text('هل أنت متأكد من حذف هذه المناقشة؟ لا يمكن التراجع.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
    if (confirmed != true || !context.mounted) return;

    try {
      await ref.read(communityRepositoryProvider).deleteDiscussion(discussion.id);
      ref.invalidate(myDiscussionsProvider);
      ref.invalidate(communityFeedProvider);
      ref.invalidate(userPublicProfileProvider(userId));
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم حذف المناقشة بنجاح.')),
        );
      }
    } on Object catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('حدث خطأ أثناء الحذف: $error')),
        );
      }
    }
  }
}

class _MyDiscussionCard extends StatelessWidget {
  const _MyDiscussionCard({
    required this.discussion,
    required this.statusLabel,
    required this.onDelete,
  });

  final CommunityDiscussion discussion;
  final String statusLabel;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPublished = discussion.status == 'published';
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                discussion.ticker,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                discussion.title,
                style: const TextStyle(fontWeight: FontWeight.bold),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: isPublished
                      ? Colors.green.withValues(alpha: 0.15)
                      : Colors.orange.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  statusLabel,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: isPublished ? Colors.green : Colors.orange,
                  ),
                ),
              ),
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 6),
          child: Text(
            discussion.content,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(color: Colors.grey.shade700),
          ),
        ),
        trailing: IconButton(
          onPressed: onDelete,
          icon: const Icon(Icons.delete_outline),
          tooltip: 'حذف المناقشة',
        ),
        onTap: () => context.push('/community/${discussion.id}'),
      ),
    );
  }
}

class _ProfileStat extends StatelessWidget {
  const _ProfileStat({
    required this.label,
    required this.value,
    required this.icon,
    required this.valueColor,
    this.onTap,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color valueColor;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final tile = Column(
      children: [
        Icon(icon, size: 20, color: valueColor),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: valueColor,
          ),
        ),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
      ],
    );
    if (onTap == null) return tile;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: tile,
    );
  }
}

class _ThemeSettingsCard extends ConsumerWidget {
  const _ThemeSettingsCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.palette_outlined, color: Colors.teal),
                const SizedBox(width: 10),
                Text(
                  'مظهر التطبيق',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              'الوضع الداكن هو الوضع الأساسي لتجربة قراءة مريحة للمؤشرات والأسهم.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: SegmentedButton<ThemeMode>(
                segments: const [
                  ButtonSegment<ThemeMode>(
                    value: ThemeMode.dark,
                    label: Text('داكن'),
                    icon: Icon(Icons.dark_mode_rounded),
                  ),
                  ButtonSegment<ThemeMode>(
                    value: ThemeMode.light,
                    label: Text('فاتح'),
                    icon: Icon(Icons.light_mode_rounded),
                  ),
                  ButtonSegment<ThemeMode>(
                    value: ThemeMode.system,
                    label: Text('تلقائي'),
                    icon: Icon(Icons.settings_suggest_rounded),
                  ),
                ],
                selected: {themeMode},
                onSelectionChanged: (Set<ThemeMode> newSelection) {
                  ref
                      .read(themeModeProvider.notifier)
                      .setThemeMode(newSelection.first);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DeveloperFeedbackCard extends ConsumerStatefulWidget {
  const _DeveloperFeedbackCard();

  @override
  ConsumerState<_DeveloperFeedbackCard> createState() =>
      __DeveloperFeedbackCardState();
}

class __DeveloperFeedbackCardState
    extends ConsumerState<_DeveloperFeedbackCard> {
  final _messageController = TextEditingController();
  bool _sending = false;

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _submitFeedback() async {
    final message = _messageController.text.trim();
    if (message.length < 5) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('يرجى كتابة ملاحظة واضحة لا تقل عن 5 أحرف.'),
        ),
      );
      return;
    }

    setState(() => _sending = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.post<Map<String, dynamic>>(
        '/user/feedback',
        data: {'message': message},
      );
      _messageController.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('شكراً لك! تم إرسال ملاحظتك للمطورين بنجاح.'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.message)),
        );
      }
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.toString())),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _sending = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.feedback_outlined, color: Colors.amber),
                const SizedBox(width: 10),
                Text(
                  'إرسال ملاحظة للمطورين',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              'أفكارك واقتراحاتك تهمنا مستقبلاً لتطوير التطبيق وتحسين تجربة الاستخدام.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _messageController,
              minLines: 3,
              maxLines: 6,
              maxLength: 4000,
              decoration: const InputDecoration(
                hintText: 'اكتب اقتراحك، استفسارك أو مشكلتك هنا...',
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _sending ? null : _submitFeedback,
                icon: _sending
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.send_rounded),
                label: const Text('إرسال للمطورين'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DraggableTradingRoomBall extends StatefulWidget {
  const _DraggableTradingRoomBall();

  @override
  State<_DraggableTradingRoomBall> createState() =>
      _DraggableTradingRoomBallState();
}

class _DraggableTradingRoomBallState extends State<_DraggableTradingRoomBall> {
  double? _top;
  double? _left;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    _top ??= size.height * 0.65;
    _left ??= size.width - 72;

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
          message: 'شات الجلسة المباشرة (40 صوتًا)',
          child: Material(
            elevation: 10,
            shadowColor: const Color(0xFF0088CC).withValues(alpha: 0.5),
            shape: const CircleBorder(),
            clipBehavior: Clip.antiAlias,
            child: InkWell(
              onTap: () => context.push('/trading-chat'),
              child: Container(
                width: 58,
                height: 58,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [Color(0xFF0088CC), Color(0xFF0288D1)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.forum_rounded,
                      color: Colors.white,
                      size: 20,
                    ),
                    SizedBox(height: 2),
                    Text(
                      'شات الجلسة',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 8,
                        fontWeight: FontWeight.w900,
                        height: 1.0,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}


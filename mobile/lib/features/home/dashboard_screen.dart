import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_theme_provider.dart';
import '../../core/avatar_assets.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../community/community_feed_tab.dart';
import '../market/stock_analysis_tab.dart';
import '../market/stocks_screen.dart';
import '../notifications/notification_providers.dart';
import '../reports/reports_screen.dart';
import '../wallet/wallet_providers.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _selectedIndex = 0;

  static const _navItems = <(String, IconData, String)>[
    ('stocks', Icons.home_rounded, 'الرئيسية'),
    ('reports', Icons.assessment_outlined, 'التقارير'),
    ('analyze', Icons.query_stats_outlined, 'تحليل سهم'),
    ('community', Icons.forum_outlined, 'المجتمع'),
    ('wallet', Icons.account_balance_wallet_outlined, 'المحفظة'),
    ('profile', Icons.person_outline_rounded, 'حسابي'),
  ];

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(sessionControllerProvider).profile;

    return Scaffold(
      appBar: AppBar(
        title: Text(_navItems[_selectedIndex].$3),
        actions: [
          if (profile?.isAdmin == true)
            IconButton(
              onPressed: () => context.push('/admin'),
              icon: const Icon(Icons.admin_panel_settings_outlined),
              tooltip: 'الإدارة',
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
            for (var item in _navItems)
              ListTile(
                leading: Icon(item.$2),
                title: Text(item.$3),
                selected: _selectedIndex == _navItems.indexOf(item),
                onTap: () {
                  setState(() => _selectedIndex = _navItems.indexOf(item));
                  Navigator.pop(context);
                },
              ),
            const Divider(),
            ListTile(
              leading: const Icon(
                Icons.card_giftcard_rounded,
                color: Colors.orangeAccent,
              ),
              title: const Text('دعوة الأصدقاء 🎁'),
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
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return const StocksScreen();
      case 1:
        return const ReportsScreen();
      case 2:
        return const StockAnalysisTab();
      case 3:
        return const CommunityFeedTab();
      case 4:
        return const WalletTab();
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

class WalletTab extends ConsumerWidget {
  const WalletTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wallet = ref.watch(walletSummaryProvider);
    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(walletSummaryProvider),
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(22),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'الرصيد الحالي',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  wallet.when(
                    loading: () =>
                        const Center(child: CircularProgressIndicator()),
                    error: (error, stackTrace) => Text('تعذر تحميل المحفظة.'),
                    data: (summary) => Text(
                      '${summary.balanceCoins} عملة',
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.w900,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  wallet.when(
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                    data: (summary) => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('الخطة: ${summary.planCode}'),
                        Text('التوزيع الأسبوعي: ${summary.weeklyCoins} عملة'),
                        Text(
                          summary.adsEnabled
                              ? 'الإعلانات مفعلة'
                              : 'الخطة بدون إعلانات',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  OutlinedButton.icon(
                    onPressed: () => context.push('/wallet/history'),
                    icon: const Icon(Icons.receipt_long_outlined),
                    label: const Text('عرض سجل العمليات'),
                  ),
                  const SizedBox(height: 10),
                  FilledButton.icon(
                    onPressed: () => context.push('/monetization'),
                    icon: const Icon(Icons.workspace_premium_outlined),
                    label: const Text('الخطط وشراء العملات'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ProfileTab extends ConsumerWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(sessionControllerProvider).profile;
    final themeMode = ref.watch(themeModeProvider);

    return ListView(
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
                    avatarAssetPath(profile?.avatarKey ?? avatarKeys.first),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  profile?.displayName ?? '',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                Text(
                  profile?.email ?? '',
                  textDirection: TextDirection.ltr,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 8),
                Text('الخطة: ${profile?.planCode ?? '-'}'),
                Text('الرصيد: ${profile?.balanceCoins ?? '0'} عملة'),
                const SizedBox(height: 20),
                FilledButton.icon(
                  onPressed: () => context.push('/profile/edit'),
                  icon: const Icon(Icons.edit_outlined),
                  label: const Text('تعديل الاسم والصورة'),
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
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.palette_outlined, color: Colors.teal),
                    const SizedBox(width: 10),
                    Text(
                      'مظهر التطبيق 🎨',
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
        ),
      ],
    );
  }
}

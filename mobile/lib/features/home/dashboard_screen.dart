import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/avatar_assets.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../community/community_feed_tab.dart';
import '../market/stock_analysis_tab.dart';
import '../monetization/free_plan_ads.dart';
import '../notifications/notification_providers.dart';
import '../reports/report_providers.dart';
import '../wallet/wallet_providers.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _index = 0;

  static const _titles = <String>[
    'الرئيسية',
    'تحليل سهم',
    'المجتمع',
    'المحفظة',
    'حسابي',
  ];

  @override
  Widget build(BuildContext context) {
    ref.watch(pushRegistrationProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_index]),
        actions: [
          if (ref.watch(sessionControllerProvider).profile?.isAdmin == true)
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
      body: IndexedStack(
        index: _index,
        children: const [
          _HomeTab(),
          StockAnalysisTab(),
          CommunityFeedTab(),
          _WalletTab(),
          _ProfileTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) => setState(() => _index = value),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'الرئيسية',
          ),
          NavigationDestination(
            icon: Icon(Icons.query_stats_outlined),
            selectedIcon: Icon(Icons.query_stats_rounded),
            label: 'تحليل',
          ),
          NavigationDestination(
            icon: Icon(Icons.forum_outlined),
            selectedIcon: Icon(Icons.forum_rounded),
            label: 'المجتمع',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_balance_wallet_outlined),
            selectedIcon: Icon(Icons.account_balance_wallet_rounded),
            label: 'المحفظة',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'حسابي',
          ),
        ],
      ),
    );
  }
}

class _HomeTab extends ConsumerWidget {
  const _HomeTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionControllerProvider);
    final preview = ref.watch(latestReportPreviewProvider);
    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(latestReportPreviewProvider);
        ref.invalidate(walletSummaryProvider);
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      },
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'أهلًا ${session.profile?.displayName ?? ''}',
            style: Theme.of(
              context,
            ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          Text(
            'الأسهم الأعلى تقييمًا وفق التحليل الآلي للجلسة القادمة',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 22),
          preview.when(
            loading: () => const _LoadingCard(),
            error: (error, stackTrace) => _ErrorCard(
              message: 'تعذر تحميل تقرير السوق.',
              onRetry: () => ref.invalidate(latestReportPreviewProvider),
            ),
            data: (report) => report == null
                ? const _EmptyReportCard()
                : _ReportPreviewCard(report: report),
          ),
          const SizedBox(height: 16),
          const FreePlanNativeAd(),
          const SizedBox(height: 16),
          const _DisclaimerCard(),
        ],
      ),
    );
  }
}

class _ReportPreviewCard extends StatelessWidget {
  const _ReportPreviewCard({required this.report});

  final MarketReportPreview report;

  @override
  Widget build(BuildContext context) {
    final target = report.targetSessionDate;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_graph_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'تقرير جلسة ${target.day}/${target.month}/${target.year}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                Chip(label: Text('${report.itemCount} فرص مؤهلة')),
                Chip(
                  label: Text(
                    report.unlocked
                        ? 'مفتوح بالفعل'
                        : '${report.unlockCostCoins} عملة للفتح',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text('المقدمة مجانية ولا تعرض أسماء الأسهم قبل فتح التقرير.'),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: () =>
                  context.push('/reports/${report.reportId}', extra: report),
              icon: Icon(
                report.unlocked
                    ? Icons.visibility_rounded
                    : Icons.lock_open_rounded,
              ),
              label: Text(report.unlocked ? 'عرض التقرير' : 'فتح التقرير'),
            ),
          ],
        ),
      ),
    );
  }
}

class _WalletTab extends ConsumerWidget {
  const _WalletTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wallet = ref.watch(walletSummaryProvider);
    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(walletSummaryProvider),
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const FreePlanNativeAd(),
          const SizedBox(height: 12),
          wallet.when(
            loading: () => const _LoadingCard(),
            error: (error, stackTrace) => _ErrorCard(
              message: 'تعذر تحميل المحفظة.',
              onRetry: () => ref.invalidate(walletSummaryProvider),
            ),
            data: (summary) => Card(
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
                    Text(
                      '${summary.balanceCoins} عملة',
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.w900,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    const SizedBox(height: 14),
                    Text('الخطة: ${summary.planCode}'),
                    Text('التوزيع الأسبوعي: ${summary.weeklyCoins} عملة'),
                    Text(
                      summary.adsEnabled
                          ? 'الإعلانات مفعلة'
                          : 'الخطة بدون إعلانات',
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
          ),
        ],
      ),
    );
  }
}

class _ProfileTab extends ConsumerWidget {
  const _ProfileTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(sessionControllerProvider).profile;
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const FreePlanNativeAd(),
        const SizedBox(height: 12),
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
      ],
    );
  }
}

class _EmptyReportCard extends StatelessWidget {
  const _EmptyReportCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.event_busy_rounded, size: 42),
            SizedBox(height: 14),
            Text(
              'لا يوجد تقرير جاهز حاليًا. سيظهر التقرير بعد اكتمال مسح جلسة التداول.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _LoadingCard extends StatelessWidget {
  const _LoadingCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message, required this.onRetry});

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
            const SizedBox(height: 14),
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

class _DisclaimerCard extends StatelessWidget {
  const _DisclaimerCard();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.info_outline_rounded,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Text(
                'التحليلات آلية وأداة لدعم القرار وليست ضمانًا للربح أو توصية شخصية بالشراء والبيع.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

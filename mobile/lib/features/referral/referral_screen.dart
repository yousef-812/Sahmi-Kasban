import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../../core/ui/app_notice.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';

final referralStatsProvider = FutureProvider.autoDispose<ReferralStats>((
  ref,
) async {
  final repository = ref.watch(backendRepositoryProvider);
  return repository.getReferralStats();
});

class ReferralScreen extends ConsumerWidget {
  const ReferralScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statsAsync = ref.watch(referralStatsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('دعوة الأصدقاء 🎁')),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(referralStatsProvider),
        child: statsAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline_rounded,
                  size: 48,
                  color: Colors.red,
                ),
                const SizedBox(height: 12),
                Text(
                  'تعذر تحميل بيانات الإحالات.',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: () => ref.invalidate(referralStatsProvider),
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('إعادة المحاولة'),
                ),
              ],
            ),
          ),
          data: (stats) => SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildHeroBanner(context),
                const SizedBox(height: 20),
                _buildReferralCodeCard(context, stats),
                const SizedBox(height: 20),
                _buildStatsOverviewCard(context, stats),
                const SizedBox(height: 24),
                Text(
                  'الأصدقاء الذين انضموا (${stats.totalReferredCount})',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                if (stats.referredUsers.isEmpty)
                  _buildEmptyState(context)
                else
                  ...stats.referredUsers.map(
                    (user) => _buildReferredUserTile(context, user),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeroBanner(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(
        context,
      ).colorScheme.primaryContainer.withValues(alpha: 0.4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Theme.of(
                  context,
                ).colorScheme.primary.withValues(alpha: 0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.card_giftcard_rounded,
                size: 40,
                color: Colors.amber,
              ),
            ),
            const SizedBox(height: 14),
            Text(
              'ادعُ أصدقاءك واكسب 10 عملات!',
              textAlign: TextAlign.center,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'احصل أنت وصديقك على 10 عملات مجانية (1,000 نقطة) فور إتمام صديقك لتأكيد بريده الإلكتروني على تطبيق سهمي كسبان.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReferralCodeCard(BuildContext context, ReferralStats stats) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'كود الدعوة الخاص بك',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                color: Theme.of(context).colorScheme.outline,
              ),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Theme.of(context).colorScheme.outlineVariant,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      stats.referralCode,
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(
                            fontWeight: FontWeight.w900,
                            letterSpacing: 2,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                    ),
                  ),
                  IconButton.filledTonal(
                    onPressed: () {
                      Clipboard.setData(
                        ClipboardData(text: stats.referralCode),
                      );
                      AppNotice.show(
                        context,
                        title: 'تم النسخ',
                        message:
                            'تم نسخ كود الدعوة إلى الحافظة: ${stats.referralCode}',
                        tone: AppNoticeTone.success,
                      );
                    },
                    icon: const Icon(Icons.copy_rounded),
                    tooltip: 'نسخ الكود',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () {
                final shareText =
                    'حمّل تطبيق سهمي كسبان لتحليل الأسهم واستخدم كود الدعوة الخاص بي [${stats.referralCode}] للحصول على 10 عملات مجانية!\n\nرابط التحميل من متجر بلاي:\n${stats.playStoreUrl}';
                Clipboard.setData(ClipboardData(text: shareText));
                AppNotice.show(
                  context,
                  title: 'تم نسخ رابط الدعوة',
                  message:
                      'تم نسخ نص ورابط الدعوة إلى الحافظة جاهزاً للمشاركة مع أصدقائك!',
                  tone: AppNoticeTone.success,
                );
              },
              icon: const Icon(Icons.share_rounded),
              label: const Text('مشاركة رابط وكود الدعوة'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsOverviewCard(BuildContext context, ReferralStats stats) {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            title: 'إجمالي الأصدقاء',
            value: '${stats.totalReferredCount}',
            icon: Icons.people_outline_rounded,
            iconColor: Colors.blueAccent,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatCard(
            title: 'أرباح الإحالات',
            value: '${stats.totalEarnedCoins} عملة',
            icon: Icons.monetization_on_outlined,
            iconColor: Colors.amber,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerLowest,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
      ),
      child: const Padding(
        padding: EdgeInsets.symmetric(vertical: 32, horizontal: 16),
        child: Column(
          children: [
            Icon(
              Icons.person_add_disabled_outlined,
              size: 48,
              color: Colors.grey,
            ),
            SizedBox(height: 12),
            Text(
              'لم تقم بدعوة أصدقاء بعد',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            SizedBox(height: 6),
            Text(
              'شارك كودك الخاص الآن واحصل على 10 عملات لكل صديق يسجل ويؤكد حسابه!',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReferredUserTile(BuildContext context, ReferredUserItem user) {
    final isVerified = user.status == 'verified';
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: CircleAvatar(
          backgroundImage: AssetImage(avatarAssetPath(user.avatarKey)),
        ),
        title: Text(
          user.displayName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text('انضم في: ${user.joinedAt}'),
        trailing: Chip(
          avatar: Icon(
            isVerified
                ? Icons.check_circle_rounded
                : Icons.hourglass_top_rounded,
            size: 16,
            color: isVerified ? Colors.green : Colors.orange,
          ),
          label: Text(
            isVerified ? '+${user.earnedCoins} عملة' : 'قيد التأكيد',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isVerified ? Colors.green : Colors.orange,
            ),
          ),
          backgroundColor: isVerified
              ? Colors.green.withValues(alpha: 0.1)
              : Colors.orange.withValues(alpha: 0.1),
          side: BorderSide.none,
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.iconColor,
  });

  final String title;
  final String value;
  final IconData icon;
  final Color iconColor;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: iconColor, size: 28),
            const SizedBox(height: 10),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.outline,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}

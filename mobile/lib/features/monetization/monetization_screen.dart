import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'monetization_controller.dart';
import 'monetization_models.dart';

class MonetizationScreen extends ConsumerWidget {
  const MonetizationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(monetizationControllerProvider);
    final controller = ref.read(monetizationControllerProvider.notifier);
    final catalog = state.catalog;
    final status = state.status;

    return Scaffold(
      appBar: AppBar(
        title: const Text('الخطط والعملات'),
        actions: [
          IconButton(
            onPressed: state.loading ? null : controller.refresh,
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: state.loading && catalog == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: controller.refresh,
              child: ListView(
                padding: const EdgeInsets.all(18),
                children: [
                  if (state.error case final error?)
                    _NoticeCard(message: _cleanError(error), isError: true),
                  if (state.message case final message?)
                    _NoticeCard(message: message),
                  if (status != null) _CurrentPlanCard(status: status),
                  const SizedBox(height: 18),
                  if (catalog != null && status != null)
                    _RewardedAdCard(
                      catalog: catalog,
                      status: status,
                      busy: state.adBusy,
                      onPressed: controller.showRewardedAd,
                    ),
                  const SizedBox(height: 24),
                  Text(
                    'خطط الاشتراك',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 10),
                  if (catalog != null)
                    for (final plan in catalog.plans)
                      _PlanCard(
                        plan: plan,
                        currentPlanCode: status?.planCode,
                        price: plan.productId == null
                            ? 'مجانية'
                            : state.products[plan.productId]?.price ??
                                  'غير متاح حاليًا',
                        storeAvailable: state.storeAvailable,
                        busy: state.purchasingProductId == plan.productId,
                        onPurchase: plan.productId == null
                            ? null
                            : () => controller.purchaseProduct(plan.productId!),
                      ),
                  const SizedBox(height: 24),
                  Text(
                    'باقات العملات',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'العملات المشتراة تُضاف بعد تحقق السيرفر من Google Play فقط.',
                  ),
                  const SizedBox(height: 10),
                  if (catalog != null)
                    for (final pack in catalog.coinPacks)
                      _CoinPackCard(
                        pack: pack,
                        price:
                            state.products[pack.productId]?.price ??
                            'غير متاح حاليًا',
                        storeAvailable: state.storeAvailable,
                        busy: state.purchasingProductId == pack.productId,
                        onPurchase: () =>
                            controller.purchaseProduct(pack.productId),
                      ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: state.storeAvailable
                        ? controller.restorePurchases
                        : null,
                    icon: const Icon(Icons.restore_rounded),
                    label: const Text('استعادة مشتريات Google Play'),
                  ),
                  const SizedBox(height: 14),
                  const _SecurityNote(),
                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }
}

class _CurrentPlanCard extends StatelessWidget {
  const _CurrentPlanCard({required this.status});

  final MonetizationStatusModel status;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Icon(
                Icons.workspace_premium_rounded,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('خطتك الحالية'),
                  Text(
                    _planName(status.planCode),
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  Text('${status.weeklyCoins} عملة أسبوعيًا'),
                  Text(
                    status.adsEnabled
                        ? 'تتضمن إعلانات اختيارية ومكافآت'
                        : 'بدون إعلانات',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RewardedAdCard extends StatelessWidget {
  const _RewardedAdCard({
    required this.catalog,
    required this.status,
    required this.busy,
    required this.onPressed,
  });

  final MonetizationCatalog catalog;
  final MonetizationStatusModel status;
  final bool busy;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final eligibility = status.rewardedAd;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.ondemand_video_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'شاهد إعلانًا واحصل على ${catalog.adRewardCoins} عملة',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              'المتبقي اليوم: ${eligibility.rewardsRemainingToday} من ${catalog.adRewardDailyLimit}',
            ),
            if (!eligibility.eligible) ...[
              const SizedBox(height: 6),
              Text(
                _eligibilityMessage(eligibility),
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: eligibility.eligible && !busy ? onPressed : null,
              icon: busy
                  ? const SizedBox.square(
                      dimension: 19,
                      child: CircularProgressIndicator(strokeWidth: 2.5),
                    )
                  : const Icon(Icons.play_arrow_rounded),
              label: Text(busy ? 'جارٍ تجهيز الإعلان...' : 'مشاهدة الإعلان'),
            ),
            const SizedBox(height: 8),
            const Text(
              'لا تُضاف المكافأة من الهاتف؛ السيرفر ينتظر تحقق AdMob أولًا.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  const _PlanCard({
    required this.plan,
    required this.currentPlanCode,
    required this.price,
    required this.storeAvailable,
    required this.busy,
    required this.onPurchase,
  });

  final MonetizationPlan plan;
  final String? currentPlanCode;
  final String price;
  final bool storeAvailable;
  final bool busy;
  final VoidCallback? onPurchase;

  @override
  Widget build(BuildContext context) {
    final current = plan.code == currentPlanCode;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    plan.displayNameAr,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                if (current) const Chip(label: Text('الخطة الحالية')),
              ],
            ),
            Text('${plan.weeklyCoins} عملة أسبوعيًا'),
            Text(plan.adsEnabled ? 'مع الإعلانات' : 'بدون إعلانات'),
            Text('سجل التقارير: ${plan.reportHistoryDays} يوم'),
            const SizedBox(height: 12),
            FilledButton.tonal(
              onPressed:
                  current || onPurchase == null || !storeAvailable || busy
                  ? null
                  : onPurchase,
              child: Text(
                busy
                    ? 'جارٍ فتح Google Play...'
                    : current
                    ? 'مفعّلة'
                    : price,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CoinPackCard extends StatelessWidget {
  const _CoinPackCard({
    required this.pack,
    required this.price,
    required this.storeAvailable,
    required this.busy,
    required this.onPurchase,
  });

  final CoinPack pack;
  final String price;
  final bool storeAvailable;
  final bool busy;
  final VoidCallback onPurchase;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: const CircleAvatar(child: Icon(Icons.monetization_on_rounded)),
        title: Text(
          pack.displayNameAr,
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        subtitle: Text('$price — ${pack.points} نقطة'),
        trailing: busy
            ? const SizedBox.square(
                dimension: 22,
                child: CircularProgressIndicator(strokeWidth: 2.5),
              )
            : FilledButton(
                onPressed: storeAvailable ? onPurchase : null,
                child: const Text('شراء'),
              ),
      ),
    );
  }
}

class _NoticeCard extends StatelessWidget {
  const _NoticeCard({required this.message, this.isError = false});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: isError ? Theme.of(context).colorScheme.errorContainer : null,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Text(message, textAlign: TextAlign.center),
      ),
    );
  }
}

class _SecurityNote extends StatelessWidget {
  const _SecurityNote();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.verified_user_outlined,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Text(
                'Google Play وAdMob لا يغيّران رصيدك مباشرة من التطبيق. كل عملية تُراجع على السيرفر، وتُسجل بمعرف فريد لمنع التكرار.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

String _planName(String code) {
  return switch (code) {
    'free' => 'المجانية',
    'basic' => 'الأساسية',
    'advanced' => 'المتقدمة',
    'pro' => 'الاحترافية',
    _ => code,
  };
}

String _eligibilityMessage(RewardedAdEligibilityModel eligibility) {
  return switch (eligibility.reason) {
    'subscription_without_ads' => 'خطتك الحالية بدون إعلانات.',
    'daily_limit_reached' => 'وصلت للحد اليومي لمكافآت الإعلانات.',
    'cooldown_active' => 'انتظر قليلًا قبل مشاهدة إعلان جديد.',
    'verification_disabled' => 'التحقق من الإعلانات غير مفعّل على السيرفر.',
    _ => 'الإعلان غير متاح حاليًا.',
  };
}

String _cleanError(String value) {
  return value
      .replaceFirst('ApiException: ', '')
      .replaceFirst('Bad state: ', '');
}

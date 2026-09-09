import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'wallet_providers.dart';

class WalletScreen extends ConsumerWidget {
  const WalletScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wallet = ref.watch(walletSummaryProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('المحفظة'),
        centerTitle: true,
      ),
      body: RefreshIndicator(
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
                      loading: () => const Center(
                        child: CircularProgressIndicator(),
                      ),
                      error: (error, stackTrace) =>
                          Text('تعذر تحميل المحفظة.'),
                      data: (summary) => Text(
                        '${summary.balanceCoins} عملة',
                        style: Theme.of(context).textTheme.displaySmall
                            ?.copyWith(
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
      ),
    );
  }
}
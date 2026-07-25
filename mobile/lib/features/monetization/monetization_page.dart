import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'monetization_controller.dart';
import 'monetization_screen.dart';
import 'plan_banner_ad.dart';

class MonetizationPage extends ConsumerWidget {
  const MonetizationPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(monetizationControllerProvider);
    final adsEnabled = state.status?.adsEnabled ?? false;
    return Column(
      children: [
        const Expanded(child: MonetizationScreen()),
        PlanBannerAd(enabled: adsEnabled),
      ],
    );
  }
}

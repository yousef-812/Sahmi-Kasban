import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/config/app_config.dart';
import 'monetization_repository.dart';

class BannerAdNotifier extends StateNotifier<BannerAd?> {
  BannerAdNotifier(this._ref) : super(null);

  final Ref _ref;
  bool _loading = false;
  String? _loadedAdUnitId;

  void ensureLoaded({required bool enabled}) {
    if (!enabled || kIsWeb || (!Platform.isAndroid && !Platform.isIOS)) {
      return;
    }

    final config = _ref.read(appConfigProvider);
    final adUnitId = Platform.isAndroid
        ? config.admobAndroidBannerId
        : config.admobIosBannerId;

    if (adUnitId.isEmpty) {
      return;
    }

    if (state != null && _loadedAdUnitId == adUnitId) {
      return;
    }

    if (_loading) {
      return;
    }

    _loading = true;
    final banner = BannerAd(
      adUnitId: adUnitId,
      request: const AdRequest(),
      size: AdSize.banner,
      listener: BannerAdListener(
        onAdLoaded: (ad) {
          _loading = false;
          _loadedAdUnitId = adUnitId;
          state = ad as BannerAd;
          _ref.read(monetizationRepositoryProvider).recordAdTelemetry(
                adType: 'banner',
                eventType: 'impression',
                adUnitId: adUnitId,
              );
        },
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          _loading = false;
          _loadedAdUnitId = null;
          state = null;
          _ref.read(monetizationRepositoryProvider).recordAdTelemetry(
                adType: 'banner',
                eventType: 'failed_to_load',
                adUnitId: adUnitId,
                errorMessage: 'code ${error.code}: ${error.message}',
              );
        },
        onAdClicked: (ad) {
          _ref.read(monetizationRepositoryProvider).recordAdTelemetry(
                adType: 'banner',
                eventType: 'clicked',
                adUnitId: adUnitId,
              );
        },
      ),
    );
    banner.load();
  }

  void disposeCurrent() {
    state?.dispose();
    state = null;
    _loading = false;
    _loadedAdUnitId = null;
  }

  @override
  void dispose() {
    disposeCurrent();
    super.dispose();
  }
}

final bannerAdProvider =
    StateNotifierProvider<BannerAdNotifier, BannerAd?>((ref) {
  return BannerAdNotifier(ref);
});

class PlanBannerAd extends ConsumerWidget {
  const PlanBannerAd({required this.enabled, super.key});

  final bool enabled;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (!enabled || kIsWeb || (!Platform.isAndroid && !Platform.isIOS)) {
      return const SizedBox.shrink();
    }

    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(bannerAdProvider.notifier).ensureLoaded(enabled: true);
    });

    final banner = ref.watch(bannerAdProvider);
    if (banner == null) {
      return const SizedBox.shrink();
    }

    return SafeArea(
      top: false,
      child: ColoredBox(
        color: Theme.of(context).colorScheme.surface,
        child: Center(
          child: Semantics(
            label: 'إعلان بانر',
            child: SizedBox(
              width: banner.size.width.toDouble(),
              height: banner.size.height.toDouble(),
              child: AdWidget(ad: banner),
            ),
          ),
        ),
      ),
    );
  }
}

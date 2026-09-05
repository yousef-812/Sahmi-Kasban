import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/config/app_config.dart';
import '../auth/session_controller.dart';
import 'monetization_repository.dart';

class PlanBannerAd extends ConsumerStatefulWidget {
  const PlanBannerAd({this.enabled = true, this.enabledOverride, super.key});

  final bool enabled;
  final bool? enabledOverride;

  @override
  ConsumerState<PlanBannerAd> createState() => _PlanBannerAdState();
}

class _PlanBannerAdState extends ConsumerState<PlanBannerAd> {
  BannerAd? _bannerAd;
  bool _loading = false;
  String? _loadedAdUnitId;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _syncAd();
    });
  }

  @override
  void didUpdateWidget(covariant PlanBannerAd oldWidget) {
    super.didUpdateWidget(oldWidget);
    _syncAd();
  }

  void _syncAd() {
    final profile = ref.read(sessionControllerProvider).profile;
    final enabled =
        widget.enabledOverride ?? (widget.enabled && (profile?.adsEnabled == true));

    if (!enabled || kIsWeb || (!Platform.isAndroid && !Platform.isIOS)) {
      _disposeAd();
      return;
    }

    final config = ref.read(appConfigProvider);
    final adUnitId = Platform.isAndroid
        ? config.admobAndroidBannerId
        : config.admobIosBannerId;

    if (adUnitId.isEmpty || (_bannerAd != null && _loadedAdUnitId == adUnitId)) {
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
          if (!mounted) {
            ad.dispose();
            return;
          }
          setState(() {
            _loading = false;
            _loadedAdUnitId = adUnitId;
            _bannerAd = ad as BannerAd;
          });
          ref.read(monetizationRepositoryProvider).recordAdTelemetry(
                adType: 'banner',
                eventType: 'impression',
                adUnitId: adUnitId,
              );
        },
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          if (mounted) {
            setState(() {
              _loading = false;
              _loadedAdUnitId = null;
              _bannerAd = null;
            });
            ref.read(monetizationRepositoryProvider).recordAdTelemetry(
                  adType: 'banner',
                  eventType: 'failed_to_load',
                  adUnitId: adUnitId,
                  errorMessage: 'code ${error.code}: ${error.message}',
                );
          }
        },
        onAdClicked: (ad) {
          ref.read(monetizationRepositoryProvider).recordAdTelemetry(
                adType: 'banner',
                eventType: 'clicked',
                adUnitId: adUnitId,
              );
        },
      ),
    );
    banner.load();
  }

  void _disposeAd() {
    _bannerAd?.dispose();
    _bannerAd = null;
    _loading = false;
    _loadedAdUnitId = null;
  }

  @override
  void dispose() {
    _disposeAd();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(sessionControllerProvider).profile;
    final enabled =
        widget.enabledOverride ?? (widget.enabled && (profile?.adsEnabled == true));

    if (!enabled || kIsWeb || (!Platform.isAndroid && !Platform.isIOS)) {
      return const SizedBox.shrink();
    }

    final banner = _bannerAd;
    if (banner == null) {
      if (!_loading) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) _syncAd();
        });
      }
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

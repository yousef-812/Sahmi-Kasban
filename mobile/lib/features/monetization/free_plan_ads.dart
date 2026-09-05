import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/config/app_config.dart';
import '../auth/session_controller.dart';
import 'monetization_repository.dart';
import 'plan_banner_ad.dart';

class FreePlanAdShell extends ConsumerWidget {
  const FreePlanAdShell({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(sessionControllerProvider).profile;
    final enabled = profile?.adsEnabled == true;
    if (enabled) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(freePlanInterstitialProvider).preload(enabled: true);
      });
    }
    return Column(
      children: [
        Expanded(child: child),
        PlanBannerAd(enabled: enabled),
      ],
    );
  }
}

class FreePlanNativeAd extends ConsumerStatefulWidget {
  const FreePlanNativeAd({this.enabledOverride, super.key});

  final bool? enabledOverride;

  @override
  ConsumerState<FreePlanNativeAd> createState() => _FreePlanNativeAdState();
}

class _FreePlanNativeAdState extends ConsumerState<FreePlanNativeAd> {
  NativeAd? _ad;
  bool _loaded = false;
  String? _activeAdUnitId;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncAd();
  }

  @override
  void didUpdateWidget(covariant FreePlanNativeAd oldWidget) {
    super.didUpdateWidget(oldWidget);
    _syncAd();
  }

  void _syncAd() {
    final profile = ref.read(sessionControllerProvider).profile;
    final enabled = widget.enabledOverride ?? profile?.adsEnabled == true;
    if (!enabled || !(Platform.isAndroid || Platform.isIOS)) {
      _disposeAd();
      return;
    }

    final config = ref.read(appConfigProvider);
    final adUnitId = Platform.isAndroid
        ? config.admobAndroidNativeId
        : config.admobIosNativeId;
    if (adUnitId.isEmpty || (_ad != null && _activeAdUnitId == adUnitId)) {
      return;
    }

    _disposeAd();
    _activeAdUnitId = adUnitId;
    final ad = NativeAd(
      adUnitId: adUnitId,
      request: const AdRequest(),
      listener: NativeAdListener(
        onAdLoaded: (loadedAd) {
          if (!mounted || loadedAd != _ad) {
            loadedAd.dispose();
            return;
          }
          setState(() => _loaded = true);
          ref
              .read(monetizationRepositoryProvider)
              .recordAdTelemetry(
                adType: 'native',
                eventType: 'impression',
                adUnitId: adUnitId,
              );
        },
        onAdFailedToLoad: (failedAd, error) {
          failedAd.dispose();
          if (mounted && failedAd == _ad) {
            setState(() {
              _ad = null;
              _loaded = false;
            });
            ref
                .read(monetizationRepositoryProvider)
                .recordAdTelemetry(
                  adType: 'native',
                  eventType: 'failed_to_load',
                  adUnitId: adUnitId,
                  errorMessage: 'code ${error.code}: ${error.message}',
                );
          }
        },
        onAdClicked: (ad) {
          ref
              .read(monetizationRepositoryProvider)
              .recordAdTelemetry(
                adType: 'native',
                eventType: 'clicked',
                adUnitId: adUnitId,
              );
        },
      ),
      nativeTemplateStyle: NativeTemplateStyle(
        templateType: TemplateType.small,
        cornerRadius: 14,
      ),
    );
    _ad = ad;
    ad.load();
  }

  void _disposeAd() {
    final ad = _ad;
    _ad = null;
    _loaded = false;
    _activeAdUnitId = null;
    ad?.dispose();
  }

  @override
  void dispose() {
    _disposeAd();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ad = _ad;
    if (!_loaded || ad == null) {
      return const SizedBox.shrink();
    }
    return Semantics(
      label: 'إعلان مدمج',
      child: Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(8, 6, 8, 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('إعلان', style: Theme.of(context).textTheme.labelSmall),
              const SizedBox(height: 4),
              ConstrainedBox(
                constraints: const BoxConstraints(
                  minWidth: 320,
                  minHeight: 90,
                  maxHeight: 200,
                ),
                child: AdWidget(ad: ad),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class InterstitialFrequencyPolicy {
  const InterstitialFrequencyPolicy({
    this.actionsPerAd = 2,
    this.minimumInterval = const Duration(seconds: 90),
  });

  final int actionsPerAd;
  final Duration minimumInterval;

  bool canShow({
    required int meaningfulActions,
    required DateTime now,
    required DateTime? lastShownAt,
  }) {
    if (meaningfulActions < actionsPerAd) {
      return false;
    }
    if (lastShownAt == null) {
      return true;
    }
    return now.difference(lastShownAt) >= minimumInterval;
  }
}

class FreePlanInterstitialCoordinator {
  FreePlanInterstitialCoordinator({
    required AppConfig config,
    MonetizationRepository? repository,
    InterstitialFrequencyPolicy policy = const InterstitialFrequencyPolicy(),
  }) : _config = config,
       _repository = repository,
       _policy = policy;

  final AppConfig _config;
  final MonetizationRepository? _repository;
  final InterstitialFrequencyPolicy _policy;
  InterstitialAd? _ad;
  bool _loading = false;
  int _meaningfulActions = 0;
  DateTime? _lastShownAt;
  Timer? _retryTimer;

  Future<void> recordMeaningfulAction({required bool enabled}) async {
    if (!enabled || !(Platform.isAndroid || Platform.isIOS)) {
      return;
    }
    _meaningfulActions += 1;
    _loadIfNeeded();

    final now = DateTime.now();
    if (!_policy.canShow(
      meaningfulActions: _meaningfulActions,
      now: now,
      lastShownAt: _lastShownAt,
    )) {
      return;
    }

    final ad = _ad;
    if (ad == null) {
      return;
    }
    _ad = null;
    _meaningfulActions = 0;
    _lastShownAt = now;
    final adUnitId = Platform.isAndroid
        ? _config.admobAndroidInterstitialId
        : _config.admobIosInterstitialId;
    ad.fullScreenContentCallback = FullScreenContentCallback<InterstitialAd>(
      onAdDismissedFullScreenContent: (closedAd) {
        closedAd.dispose();
        _loadIfNeeded();
      },
      onAdFailedToShowFullScreenContent: (failedAd, error) {
        failedAd.dispose();
        _repository?.recordAdTelemetry(
          adType: 'interstitial',
          eventType: 'failed_to_show',
          adUnitId: adUnitId,
          errorMessage: 'code ${error.code}: ${error.message}',
        );
        _loadIfNeeded();
      },
    );
    await ad.show();
  }

  void preload({required bool enabled}) {
    if (enabled) {
      _loadIfNeeded();
    }
  }

  void _loadIfNeeded() {
    if (_loading || _ad != null || !(Platform.isAndroid || Platform.isIOS)) {
      return;
    }
    final adUnitId = Platform.isAndroid
        ? _config.admobAndroidInterstitialId
        : _config.admobIosInterstitialId;
    if (adUnitId.isEmpty) {
      return;
    }
    _loading = true;
    InterstitialAd.load(
      adUnitId: adUnitId,
      request: const AdRequest(),
      adLoadCallback: InterstitialAdLoadCallback(
        onAdLoaded: (ad) {
          _loading = false;
          _ad = ad;
          _repository?.recordAdTelemetry(
            adType: 'interstitial',
            eventType: 'impression',
            adUnitId: adUnitId,
          );
        },
        onAdFailedToLoad: (error) {
          _loading = false;
          _repository?.recordAdTelemetry(
            adType: 'interstitial',
            eventType: 'failed_to_load',
            adUnitId: adUnitId,
            errorMessage: 'code ${error.code}: ${error.message}',
          );
          _retryTimer?.cancel();
          _retryTimer = Timer(const Duration(seconds: 15), () {
            _loadIfNeeded();
          });
        },
      ),
    );
  }

  void dispose() {
    _retryTimer?.cancel();
    _ad?.dispose();
    _ad = null;
  }
}

final freePlanInterstitialProvider = Provider<FreePlanInterstitialCoordinator>((
  ref,
) {
  final coordinator = FreePlanInterstitialCoordinator(
    config: ref.watch(appConfigProvider),
    repository: ref.watch(monetizationRepositoryProvider),
  );
  ref.onDispose(coordinator.dispose);
  return coordinator;
});

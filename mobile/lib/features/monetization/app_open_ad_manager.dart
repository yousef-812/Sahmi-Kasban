import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/config/app_config.dart';
import 'ad_frequency_gate.dart';
import 'monetization_repository.dart';

class AppOpenAdManager with WidgetsBindingObserver {
  AppOpenAdManager({
    required this.config,
    required this.gate,
    required this.isEnabled,
    required this.isSafeRoute,
    this.repository,
    this.minimumBackgroundDuration = const Duration(minutes: 5),
    this.adMaxCacheDuration = const Duration(hours: 4),
  });

  final AppConfig config;
  final AdFrequencyGate gate;
  final bool Function() isEnabled;
  final bool Function() isSafeRoute;
  final MonetizationRepository? repository;
  final Duration minimumBackgroundDuration;
  final Duration adMaxCacheDuration;

  AppOpenAd? _ad;
  DateTime? _adLoadedAt;
  DateTime? _backgroundedAt;
  bool _loading = false;
  bool _isFirstLaunchHandled = false;

  static const _prefsKey = 'sahmi_has_opened_before';

  Future<void> start() async {
    WidgetsBinding.instance.addObserver(this);
    final prefs = await SharedPreferences.getInstance();
    final hasOpenedBefore = prefs.getBool(_prefsKey) ?? false;
    if (!hasOpenedBefore) {
      // First installation: record it and avoid showing ad on first open
      await prefs.setBool(_prefsKey, true);
      _isFirstLaunchHandled = true;
      _loadAd();
      return;
    }
    _isFirstLaunchHandled = true;
    _loadAd();
  }

  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _ad?.dispose();
    _ad = null;
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused) {
      _backgroundedAt = DateTime.now();
    } else if (state == AppLifecycleState.resumed) {
      _maybeShowOnResume();
    }
  }

  void _maybeShowOnResume() {
    if (!_isFirstLaunchHandled || !isEnabled() || !isSafeRoute()) return;

    final backgroundedAt = _backgroundedAt;
    if (backgroundedAt == null) return;
    final wasInBackgroundLongEnough =
        DateTime.now().difference(backgroundedAt) >= minimumBackgroundDuration;
    if (!wasInBackgroundLongEnough) return;

    if (!gate.canShow(DateTime.now())) return;
    _showAdIfAvailable();
  }

  void _loadAd() {
    if (_loading || _hasFreshAd || !(Platform.isAndroid || Platform.isIOS)) return;
    final adUnitId =
        Platform.isAndroid ? config.admobAndroidAppOpenId : config.admobIosAppOpenId;
    if (adUnitId.isEmpty) return;

    _loading = true;
    AppOpenAd.load(
      adUnitId: adUnitId,
      request: const AdRequest(),
      adLoadCallback: AppOpenAdLoadCallback(
        onAdLoaded: (ad) {
          _loading = false;
          _ad = ad;
          _adLoadedAt = DateTime.now();
          repository?.recordAdTelemetry(
            adType: 'app_open',
            eventType: 'loaded',
            adUnitId: adUnitId,
          );
        },
        onAdFailedToLoad: (error) {
          _loading = false;
          repository?.recordAdTelemetry(
            adType: 'app_open',
            eventType: 'failed_to_load',
            adUnitId: adUnitId,
            errorMessage: 'code ${error.code}: ${error.message}',
          );
        },
      ),
    );
  }

  bool get _hasFreshAd {
    final ad = _ad;
    final loadedAt = _adLoadedAt;
    if (ad == null || loadedAt == null) return false;
    return DateTime.now().difference(loadedAt) < adMaxCacheDuration;
  }

  void _showAdIfAvailable() {
    if (!_hasFreshAd) {
      _loadAd();
      return;
    }
    final ad = _ad!;
    final adUnitId =
        Platform.isAndroid ? config.admobAndroidAppOpenId : config.admobIosAppOpenId;
    gate.markShowing();
    ad.fullScreenContentCallback = FullScreenContentCallback(
      onAdImpression: (impressionAd) {
        repository?.recordAdTelemetry(
          adType: 'app_open',
          eventType: 'impression',
          adUnitId: adUnitId,
        );
      },
      onAdDismissedFullScreenContent: (dismissedAd) {
        dismissedAd.dispose();
        _ad = null;
        gate.markDismissed();
        _loadAd();
      },
      onAdFailedToShowFullScreenContent: (failedAd, error) {
        failedAd.dispose();
        _ad = null;
        gate.markDismissed();
        repository?.recordAdTelemetry(
          adType: 'app_open',
          eventType: 'failed_to_show',
          adUnitId: adUnitId,
          errorMessage: 'code ${error.code}: ${error.message}',
        );
        _loadAd();
      },
    );
    ad.show();
  }
}

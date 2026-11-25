import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

/// Session-wide answer to "may this app request ads right now?".
///
/// It is set only from the Google UMP SDK ([ConsentInformation.canRequestAds]),
/// which applies the user's region and any saved consent choice. Every ad
/// load and show checks it, and ad widgets and caches listen to [notifier] so
/// loaded or preloaded ads are disposed when consent is withdrawn.
class AdsConsent {
  AdsConsent._();

  static final ValueNotifier<bool> notifier = ValueNotifier<bool>(false);

  static bool get canRequestAds => notifier.value;
  static set canRequestAds(bool value) => notifier.value = value;

  @visibleForTesting
  static void debugSet(bool value) => canRequestAds = value;
}

/// Thin wrapper over the UMP SDK so the consent flow can be tested.
abstract interface class ConsentGateway {
  /// Completes when the consent info update finished (success or failure).
  Future<void> updateConsentInfo();

  /// Shows the consent form only if the SDK says it is required. Completes
  /// when the form flow is done (success or error).
  Future<void> loadAndShowFormIfRequired();

  Future<bool> canRequestAds();

  Future<bool> isPrivacyOptionsRequired();

  /// Completes when the privacy options form is closed.
  Future<void> showPrivacyOptionsForm();

  /// Starts the Mobile Ads SDK.
  Future<void> startAdsSdk();
}

class SdkConsentGateway implements ConsentGateway {
  const SdkConsentGateway();

  @override
  Future<void> updateConsentInfo() {
    final done = Completer<void>();
    ConsentInformation.instance.requestConsentInfoUpdate(
      ConsentRequestParameters(),
      () {
        if (!done.isCompleted) done.complete();
      },
      (FormError error) {
        debugPrint('UMP consent info update failed: ${error.message}');
        if (!done.isCompleted) done.complete();
      },
    );
    return done.future;
  }

  @override
  Future<void> loadAndShowFormIfRequired() {
    final done = Completer<void>();
    ConsentForm.loadAndShowConsentFormIfRequired((FormError? error) {
      if (error != null) debugPrint('UMP consent form error: ${error.message}');
      if (!done.isCompleted) done.complete();
    });
    return done.future;
  }

  @override
  Future<bool> canRequestAds() => ConsentInformation.instance.canRequestAds();

  @override
  Future<bool> isPrivacyOptionsRequired() async {
    final status = await ConsentInformation.instance
        .getPrivacyOptionsRequirementStatus();
    return status == PrivacyOptionsRequirementStatus.required;
  }

  @override
  Future<void> showPrivacyOptionsForm() {
    final done = Completer<void>();
    ConsentForm.showPrivacyOptionsForm((FormError? error) {
      if (error != null) {
        debugPrint('UMP privacy options error: ${error.message}');
      }
      if (!done.isCompleted) done.complete();
    });
    return done.future;
  }

  @override
  Future<void> startAdsSdk() => MobileAds.instance.initialize();
}

final consentManagerProvider = Provider<ConsentManager>((ref) {
  return ConsentManager();
});

final privacyOptionsRequiredProvider = FutureProvider<bool>((ref) {
  return ref.watch(consentManagerProvider).isPrivacyOptionsRequired();
});

class ConsentManager {
  ConsentManager({
    ConsentGateway gateway = const SdkConsentGateway(),
    this.formTimeout = const Duration(minutes: 10),
  }) : _gateway = gateway;

  final ConsentGateway _gateway;
  final Duration formTimeout;

  static bool _sdkStarted = false;

  @visibleForTesting
  static void debugResetSdkStarted() => _sdkStarted = false;

  Future<void> _startSdkOnce() async {
    if (_sdkStarted) return;
    _sdkStarted = true;
    try {
      await _gateway.startAdsSdk();
    } on Object catch (error) {
      _sdkStarted = false;
      debugPrint('Mobile Ads SDK start failed: $error');
    }
  }

  /// Startup flow: update consent info, show the form only when the SDK
  /// requires it, then ask the SDK whether ads may be requested. The answer
  /// is stored in [AdsConsent]; the ads SDK starts only when allowed. Errors
  /// never grant consent: the SDK's own answer decides, and a failed
  /// first-time check keeps ads off.
  Future<bool> gatherConsent() async {
    try {
      await _gateway.updateConsentInfo();
      await _gateway.loadAndShowFormIfRequired();
    } on Object catch (error) {
      debugPrint('UMP consent flow failed: $error');
    }
    var allowed = false;
    try {
      allowed = await _gateway.canRequestAds();
    } on Object catch (error) {
      debugPrint('UMP canRequestAds failed: $error');
    }
    AdsConsent.canRequestAds = allowed;
    if (allowed) await _startSdkOnce();
    return allowed;
  }

  /// True when the SDK says a privacy-options entry point must be offered.
  /// False on any error or on web.
  Future<bool> isPrivacyOptionsRequired() async {
    if (kIsWeb) return false;
    try {
      return await _gateway.isPrivacyOptionsRequired();
    } on Object catch (error) {
      debugPrint('UMP privacy options status failed: $error');
      return false;
    }
  }

  /// Opens the privacy options form, then re-reads the SDK's answer. A
  /// withdrawal turns [AdsConsent] off (listeners dispose loaded ads); a new
  /// grant starts the SDK if it never started. Never throws.
  Future<void> showPrivacyOptions() async {
    try {
      await _gateway.showPrivacyOptionsForm().timeout(formTimeout);
    } on Object catch (error) {
      debugPrint('UMP privacy options failed: $error');
    }
    try {
      final allowed = await _gateway.canRequestAds();
      if (allowed) await _startSdkOnce();
      AdsConsent.canRequestAds = allowed;
    } on Object catch (error) {
      debugPrint('UMP consent re-check failed: $error');
    }
  }
}

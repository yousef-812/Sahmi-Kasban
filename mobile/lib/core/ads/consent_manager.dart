import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

/// Session-wide answer to "may this app request ads right now?".
///
/// It is set only from the Google UMP SDK ([ConsentInformation.canRequestAds]),
/// which applies the user's region and any saved consent choice. Every ad
/// load in the app checks it, so no ad request is made before consent is
/// settled or after it was refused.
class AdsConsent {
  AdsConsent._();

  static bool canRequestAds = false;

  /// Test hook.
  @visibleForTesting
  static void debugSet(bool value) => canRequestAds = value;
}

final privacyOptionsRequiredProvider = FutureProvider<bool>((ref) {
  return const ConsentManager().isPrivacyOptionsRequired();
});

class ConsentManager {
  const ConsentManager();

  /// Updates consent info, shows the UMP form only when the SDK says it is
  /// required (EEA/UK etc. and not already answered), then asks the SDK
  /// whether ads may be requested. Returns that answer; on any error the
  /// SDK's own answer is still used, so previously saved consent keeps
  /// working and a failed first-time check keeps ads off.
  Future<bool> gatherConsent() async {
    final updated = Completer<void>();
    ConsentInformation.instance.requestConsentInfoUpdate(
      ConsentRequestParameters(),
      () {
        if (!updated.isCompleted) updated.complete();
      },
      (FormError error) {
        debugPrint('UMP consent info update failed: ${error.message}');
        if (!updated.isCompleted) updated.complete();
      },
    );
    await updated.future;

    final formDone = Completer<void>();
    ConsentForm.loadAndShowConsentFormIfRequired((FormError? error) {
      if (error != null) {
        debugPrint('UMP consent form error: ${error.message}');
      }
      if (!formDone.isCompleted) formDone.complete();
    });
    await formDone.future;

    final allowed = await ConsentInformation.instance.canRequestAds();
    AdsConsent.canRequestAds = allowed;
    if (allowed) _sdkStarted = true;
    return allowed;
  }

  /// True when the SDK says a privacy-options entry point must be offered
  /// (for example EEA/UK users). False on any error or unsupported platform.
  Future<bool> isPrivacyOptionsRequired() async {
    if (kIsWeb) return false;
    try {
      final status = await ConsentInformation.instance
          .getPrivacyOptionsRequirementStatus();
      return status == PrivacyOptionsRequirementStatus.required;
    } on Object catch (error) {
      debugPrint('UMP privacy options status failed: $error');
      return false;
    }
  }

  /// Opens the UMP privacy options form, then re-reads the SDK's answer so a
  /// changed choice takes effect for later ad requests. Never throws.
  Future<void> showPrivacyOptions() async {
    final done = Completer<void>();
    try {
      ConsentForm.showPrivacyOptionsForm((FormError? error) {
        if (error != null) {
          debugPrint('UMP privacy options error: ${error.message}');
        }
        if (!done.isCompleted) done.complete();
      });
      await done.future.timeout(const Duration(minutes: 10));
    } on Object catch (error) {
      debugPrint('UMP privacy options failed: $error');
    }
    try {
      final allowed = await ConsentInformation.instance.canRequestAds();
      if (allowed && !AdsConsent.canRequestAds && !_sdkStarted) {
        await MobileAds.instance.initialize();
        _sdkStarted = true;
      }
      AdsConsent.canRequestAds = allowed;
    } on Object catch (error) {
      debugPrint('UMP consent re-check failed: $error');
    }
  }
}

bool _sdkStarted = false;

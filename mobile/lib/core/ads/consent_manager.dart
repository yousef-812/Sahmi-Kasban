import 'dart:async';

import 'package:flutter/foundation.dart';
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
    return allowed;
  }
}

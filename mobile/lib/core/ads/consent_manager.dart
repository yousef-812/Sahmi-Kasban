import 'dart:async';

import 'package:google_mobile_ads/google_mobile_ads.dart';

class ConsentManager {
  const ConsentManager();

  /// Gathers user consent required for GDPR/EEA regions before loading ads.
  /// For non-EEA users (e.g. Egypt), [ConsentInformation] returns [ConsentStatus.notRequired]
  /// or unavailability instantly without displaying any UI form.
  Future<bool> gatherConsent() async {
    final completer = Completer<bool>();

    final params = ConsentRequestParameters();

    ConsentInformation.instance.requestConsentInfoUpdate(
      params,
      () async {
        if (await ConsentInformation.instance.isConsentFormAvailable()) {
          _loadAndShowForm(completer);
        } else {
          completer.complete(true);
        }
      },
      (FormError error) {
        // In case of error updating consent info, proceed gracefully with default ads
        completer.complete(true);
      },
    );

    return completer.future;
  }

  void _loadAndShowForm(Completer<bool> completer) {
    ConsentForm.loadConsentForm(
      (ConsentForm consentForm) async {
        final status = await ConsentInformation.instance.getConsentStatus();
        if (status == ConsentStatus.required) {
          consentForm.show((FormError? formError) {
            _loadAndShowForm(completer);
          });
        } else {
          if (!completer.isCompleted) completer.complete(true);
        }
      },
      (FormError error) {
        if (!completer.isCompleted) completer.complete(true);
      },
    );
  }
}

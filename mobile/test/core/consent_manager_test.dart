import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/ads/consent_manager.dart';

class _Fake implements ConsentGateway {
  _Fake({this.allowed = true, this.required = false, this.failUpdate = false, this.failCanRequest = false});
  bool allowed;
  bool required;
  bool failUpdate;
  bool failCanRequest;
  int starts = 0;
  int forms = 0;
  bool formThrows = false;
  bool allowedAfterForm = true;
  @override
  Future<void> updateConsentInfo() async {
    if (failUpdate) throw StateError('network');
  }
  @override
  Future<void> loadAndShowFormIfRequired() async {}
  @override
  Future<bool> canRequestAds() async {
    if (failCanRequest) throw StateError('sdk');
    return allowed;
  }
  @override
  Future<bool> isPrivacyOptionsRequired() async => required;
  @override
  Future<void> showPrivacyOptionsForm() async {
    forms++;
    if (formThrows) throw StateError('form');
    allowed = allowedAfterForm;
  }
  @override
  Future<void> startAdsSdk() async => starts++;
}

void main() {
  setUp(() {
    AdsConsent.canRequestAds = false;
    ConsentManager.debugResetSdkStarted();
  });

  test('SDK allows: ads on, SDK started once', () async {
    final g = _Fake();
    final m = ConsentManager(gateway: g);
    expect(await m.gatherConsent(), isTrue);
    expect(AdsConsent.canRequestAds, isTrue);
    await m.gatherConsent();
    expect(g.starts, 1);
  });

  test('SDK refuses: ads stay off, SDK not started', () async {
    final g = _Fake(allowed: false);
    expect(await ConsentManager(gateway: g).gatherConsent(), isFalse);
    expect(AdsConsent.canRequestAds, isFalse);
    expect(g.starts, 0);
  });

  test('update error with no saved consent: ads off (no silent grant)', () async {
    final g = _Fake(allowed: false, failUpdate: true);
    expect(await ConsentManager(gateway: g).gatherConsent(), isFalse);
    expect(g.starts, 0);
  });

  test('update error but SDK still says allowed (saved prior consent): ads on', () async {
    final g = _Fake(allowed: true, failUpdate: true);
    expect(await ConsentManager(gateway: g).gatherConsent(), isTrue);
  });

  test('canRequestAds throws: ads off', () async {
    final g = _Fake(failCanRequest: true);
    expect(await ConsentManager(gateway: g).gatherConsent(), isFalse);
    expect(AdsConsent.canRequestAds, isFalse);
  });

  test('privacy options required flag comes from the SDK', () async {
    expect(await ConsentManager(gateway: _Fake(required: true)).isPrivacyOptionsRequired(), isTrue);
    expect(await ConsentManager(gateway: _Fake(required: false)).isPrivacyOptionsRequired(), isFalse);
  });

  test('withdrawal via privacy options turns ads off and notifies listeners', () async {
    final g = _Fake()..allowedAfterForm = false;
    final m = ConsentManager(gateway: g);
    await m.gatherConsent();
    var notified = 0;
    void l() => notified++;
    AdsConsent.notifier.addListener(l);
    await m.showPrivacyOptions();
    AdsConsent.notifier.removeListener(l);
    expect(AdsConsent.canRequestAds, isFalse);
    expect(notified, 1);
  });

  test('grant via privacy options starts SDK if it never started', () async {
    final g = _Fake(allowed: false)..allowedAfterForm = true;
    final m = ConsentManager(gateway: g);
    await m.gatherConsent();
    expect(g.starts, 0);
    await m.showPrivacyOptions();
    expect(AdsConsent.canRequestAds, isTrue);
    expect(g.starts, 1);
  });

  test('form error does not throw and consent is re-read', () async {
    final g = _Fake()..formThrows = true;
    final m = ConsentManager(gateway: g);
    await m.gatherConsent();
    await m.showPrivacyOptions();
    expect(g.forms, 1);
    expect(AdsConsent.canRequestAds, isTrue);
  });
}

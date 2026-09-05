import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Unified frequency gate for all interrupting full-screen ads:
/// Standard Interstitial, App Open, and Rewarded Interstitial.
/// Prevents multiple full-screen ads from bombarding the user in quick succession.
class AdFrequencyGate {
  AdFrequencyGate({this.minimumInterval = const Duration(minutes: 3)});

  final Duration minimumInterval;

  DateTime? _lastShownAt;
  bool _showing = false;

  bool get isAnyAdShowing => _showing;

  bool canShow(DateTime now) {
    if (_showing) return false;
    final last = _lastShownAt;
    if (last == null) return true;
    return now.difference(last) >= minimumInterval;
  }

  void markShowing() {
    _showing = true;
  }

  void markDismissed({DateTime? at}) {
    _showing = false;
    _lastShownAt = at ?? DateTime.now();
  }
}

final adFrequencyGateProvider = Provider<AdFrequencyGate>((ref) {
  return AdFrequencyGate();
});

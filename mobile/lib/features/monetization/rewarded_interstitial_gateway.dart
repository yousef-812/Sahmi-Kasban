import 'dart:async';
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'ad_frequency_gate.dart';
import 'monetization_models.dart';
import 'monetization_repository.dart';

enum RewardedInterstitialResult { earned, dismissedWithoutReward, failed }

abstract interface class RewardedInterstitialGateway {
  Future<RewardedInterstitialResult> loadAndShow();
}

class GoogleRewardedInterstitialGateway implements RewardedInterstitialGateway {
  const GoogleRewardedInterstitialGateway({
    required MonetizationRepository repository,
    required AdFrequencyGate gate,
  }) : _repository = repository,
       _gate = gate;

  final MonetizationRepository _repository;
  final AdFrequencyGate _gate;

  @override
  Future<RewardedInterstitialResult> loadAndShow() async {
    if (!(Platform.isAndroid || Platform.isIOS)) {
      return RewardedInterstitialResult.failed;
    }
    if (!_gate.canShow(DateTime.now())) {
      return RewardedInterstitialResult.failed;
    }

    final RewardedAdSessionModel session;
    try {
      session = await _repository.createRewardedAdSession(
        platform: Platform.isAndroid ? 'android' : 'ios',
        adFormat: 'rewarded_interstitial',
      );
    } on Object {
      return RewardedInterstitialResult.failed;
    }

    final completer = Completer<RewardedInterstitialResult>();
    RewardedInterstitialAd.load(
      adUnitId: session.adUnitId,
      request: const AdRequest(),
      rewardedInterstitialAdLoadCallback: RewardedInterstitialAdLoadCallback(
        onAdLoaded: (ad) async {
          var earned = false;
          _gate.markShowing();
          _repository.recordAdTelemetry(
            adType: 'rewarded_interstitial',
            eventType: 'loaded',
            adUnitId: session.adUnitId,
          );
          await ad.setServerSideOptions(
            ServerSideVerificationOptions(customData: session.customData),
          );
          ad.fullScreenContentCallback = FullScreenContentCallback(
            onAdImpression: (impressionAd) {
              _repository.recordAdTelemetry(
                adType: 'rewarded_interstitial',
                eventType: 'impression',
                adUnitId: session.adUnitId,
              );
            },
            onAdDismissedFullScreenContent: (shownAd) {
              shownAd.dispose();
              _gate.markDismissed();
              if (!completer.isCompleted) {
                completer.complete(
                  earned
                      ? RewardedInterstitialResult.earned
                      : RewardedInterstitialResult.dismissedWithoutReward,
                );
              }
            },
            onAdFailedToShowFullScreenContent: (shownAd, error) {
              shownAd.dispose();
              _gate.markDismissed();
              _repository.recordAdTelemetry(
                adType: 'rewarded_interstitial',
                eventType: 'failed_to_show',
                adUnitId: session.adUnitId,
                errorMessage: 'code ${error.code}: ${error.message}',
              );
              if (!completer.isCompleted) {
                completer.complete(RewardedInterstitialResult.failed);
              }
            },
          );
          ad.show(
            onUserEarnedReward: (_, reward) {
              earned = true;
              _repository.recordAdTelemetry(
                adType: 'rewarded_interstitial',
                eventType: 'reward_granted',
                adUnitId: session.adUnitId,
              );
            },
          );
        },
        onAdFailedToLoad: (error) {
          _repository.recordAdTelemetry(
            adType: 'rewarded_interstitial',
            eventType: 'failed_to_load',
            adUnitId: session.adUnitId,
            errorMessage: 'code ${error.code}: ${error.message}',
          );
          if (!completer.isCompleted) {
            completer.complete(RewardedInterstitialResult.failed);
          }
        },
      ),
    );
    return completer.future;
  }
}

final rewardedInterstitialGatewayProvider =
    Provider<RewardedInterstitialGateway>((ref) {
  return GoogleRewardedInterstitialGateway(
    repository: ref.watch(monetizationRepositoryProvider),
    gate: ref.watch(adFrequencyGateProvider),
  );
});

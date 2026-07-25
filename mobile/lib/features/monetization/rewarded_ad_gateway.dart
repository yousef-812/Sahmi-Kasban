import 'dart:async';

import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'monetization_models.dart';

abstract interface class RewardedAdGateway {
  Future<bool> loadAndShow(RewardedAdSessionModel session);
}

class GoogleRewardedAdGateway implements RewardedAdGateway {
  const GoogleRewardedAdGateway();

  @override
  Future<bool> loadAndShow(RewardedAdSessionModel session) {
    final completer = Completer<bool>();
    RewardedAd.load(
      adUnitId: session.adUnitId,
      request: const AdRequest(),
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) async {
          var userEarnedReward = false;
          await ad.setServerSideOptions(
            ServerSideVerificationOptions(customData: session.customData),
          );
          ad.fullScreenContentCallback = FullScreenContentCallback(
            onAdDismissedFullScreenContent: (shownAd) {
              shownAd.dispose();
              if (!completer.isCompleted) {
                completer.complete(userEarnedReward);
              }
            },
            onAdFailedToShowFullScreenContent: (shownAd, error) {
              shownAd.dispose();
              if (!completer.isCompleted) {
                completer.completeError(
                  StateError('تعذر عرض الإعلان: ${error.message}'),
                );
              }
            },
          );
          ad.show(
            onUserEarnedReward: (_, reward) {
              userEarnedReward = true;
            },
          );
        },
        onAdFailedToLoad: (error) {
          if (!completer.isCompleted) {
            completer.completeError(
              StateError('تعذر تحميل الإعلان: ${error.message}'),
            );
          }
        },
      ),
    );
    return completer.future;
  }
}

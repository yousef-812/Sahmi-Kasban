import 'dart:async';

import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'monetization_models.dart';
import 'monetization_repository.dart';

abstract interface class RewardedAdGateway {
  Future<bool> loadAndShow(RewardedAdSessionModel session);
}

class GoogleRewardedAdGateway implements RewardedAdGateway {
  const GoogleRewardedAdGateway([this._repository]);

  final MonetizationRepository? _repository;

  @override
  Future<bool> loadAndShow(RewardedAdSessionModel session) {
    final completer = Completer<bool>();
    RewardedAd.load(
      adUnitId: session.adUnitId,
      request: const AdRequest(),
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) async {
          var userEarnedReward = false;
          _repository?.recordAdTelemetry(
            adType: 'rewarded',
            eventType: 'loaded',
            adUnitId: session.adUnitId,
          );
          await ad.setServerSideOptions(
            ServerSideVerificationOptions(customData: session.customData),
          );
          ad.fullScreenContentCallback = FullScreenContentCallback(
            onAdImpression: (impressionAd) {
              _repository?.recordAdTelemetry(
                adType: 'rewarded',
                eventType: 'impression',
                adUnitId: session.adUnitId,
              );
            },
            onAdDismissedFullScreenContent: (shownAd) {
              shownAd.dispose();
              if (!completer.isCompleted) {
                completer.complete(userEarnedReward);
              }
            },
            onAdFailedToShowFullScreenContent: (shownAd, error) {
              shownAd.dispose();
              _repository?.recordAdTelemetry(
                adType: 'rewarded',
                eventType: 'failed_to_show',
                adUnitId: session.adUnitId,
                errorMessage: 'code ${error.code}: ${error.message}',
              );
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
              _repository?.recordAdTelemetry(
                adType: 'rewarded',
                eventType: 'reward_granted',
                adUnitId: session.adUnitId,
              );
            },
          );
        },
        onAdFailedToLoad: (error) {
          _repository?.recordAdTelemetry(
            adType: 'rewarded',
            eventType: 'failed_to_load',
            adUnitId: session.adUnitId,
            errorMessage: 'code ${error.code}: ${error.message}',
          );
          if (!completer.isCompleted) {
            final reason = error.code == 3
                ? 'لا يوجد إعلان متوفر حالياً من AdMob (في انتظار تفعيل الوحدات الجديدة واعتماد المتجر).'
                : error.message;
            completer.completeError(
              StateError('تعذر تحميل إعلان الفيديو: $reason'),
            );
          }
        },
      ),
    );
    return completer.future;
  }
}

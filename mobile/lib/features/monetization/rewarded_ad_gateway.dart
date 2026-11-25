import 'dart:async';

import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/ads/consent_manager.dart';
import 'ad_frequency_gate.dart';
import 'monetization_models.dart';
import 'monetization_repository.dart';

abstract interface class RewardedAdGateway {
  Future<bool> loadAndShow(RewardedAdSessionModel session);
}

class GoogleRewardedAdGateway implements RewardedAdGateway {
  const GoogleRewardedAdGateway([this._repository, this._gate]);

  final MonetizationRepository? _repository;
  final AdFrequencyGate? _gate;

  @override
  Future<bool> loadAndShow(RewardedAdSessionModel session) {
    if (!AdsConsent.canRequestAds) {
      return Future<bool>.error(
        StateError('الإعلانات غير متاحة حالياً بسبب إعدادات الموافقة.'),
      );
    }
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
              _gate?.markDismissed();
              if (!completer.isCompleted) {
                completer.complete(userEarnedReward);
              }
            },
            onAdFailedToShowFullScreenContent: (shownAd, error) {
              shownAd.dispose();
              _gate?.markDismissed();
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
          // Re-check right before show: another full-screen format may have
          // started while this ad was loading. Check and mark are synchronous,
          // so no other ad can slip in between.
          if (!AdsConsent.canRequestAds) {
            ad.dispose();
            if (!completer.isCompleted) {
              completer.completeError(
                StateError('الإعلانات غير متاحة حالياً بسبب إعدادات الموافقة.'),
              );
            }
            return;
          }
          if (_gate?.isAnyAdShowing == true) {
            ad.dispose();
            _repository?.recordAdTelemetry(
              adType: 'rewarded',
              eventType: 'failed_to_show',
              adUnitId: session.adUnitId,
              errorMessage: 'another full-screen ad was showing',
            );
            if (!completer.isCompleted) {
              completer.completeError(
                StateError('إعلان آخر معروض الآن، حاول مرة أخرى بعد قليل.'),
              );
            }
            return;
          }
          _gate?.markShowing();
          try {
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
          } on Object catch (error) {
            ad.dispose();
            _gate?.markDismissed();
            if (!completer.isCompleted) {
              completer.completeError(StateError('تعذر عرض الإعلان: $error'));
            }
          }
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

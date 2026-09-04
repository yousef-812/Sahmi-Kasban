import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.admobAndroidBannerId,
    required this.admobIosBannerId,
    required this.admobAndroidNativeId,
    required this.admobIosNativeId,
    required this.admobAndroidInterstitialId,
    required this.admobIosInterstitialId,
    this.appEnvironment = 'development',
    this.releasePlatform = 'android',
  });

  static const String googleTestPublisherId = '3940256099942544';

  final String apiBaseUrl;
  final String admobAndroidBannerId;
  final String admobIosBannerId;
  final String admobAndroidNativeId;
  final String admobIosNativeId;
  final String admobAndroidInterstitialId;
  final String admobIosInterstitialId;
  final String appEnvironment;
  final String releasePlatform;

  bool get isProduction => appEnvironment.trim().toLowerCase() == 'production';

  void validateForRuntime() {
    if (!isProduction) {
      return;
    }
    final uri = Uri.tryParse(apiBaseUrl);
    if (uri == null || uri.scheme != 'https' || uri.host.isEmpty) {
      throw StateError(
        'Production builds require an absolute HTTPS API_BASE_URL.',
      );
    }

    final normalizedPlatform = releasePlatform.trim().toLowerCase();
    final adUnitIds = switch (normalizedPlatform) {
      'android' => <String>[
        admobAndroidBannerId,
        admobAndroidNativeId,
        admobAndroidInterstitialId,
      ],
      'ios' => <String>[
        admobIosBannerId,
        admobIosNativeId,
        admobIosInterstitialId,
      ],
      _ => throw StateError(
        'Production builds require RELEASE_PLATFORM=android or ios.',
      ),
    };
    if (adUnitIds.any(
      (id) => id.trim().isEmpty || id.contains(googleTestPublisherId),
    )) {
      throw StateError(
        'Production builds require non-test AdMob banner, native, and interstitial IDs for the selected release platform.',
      );
    }
  }

  factory AppConfig.fromEnvironment() {
    const configuredUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:8000',
    );
    const environment = String.fromEnvironment(
      'APP_ENV',
      defaultValue: 'development',
    );
    const configuredReleasePlatform = String.fromEnvironment(
      'RELEASE_PLATFORM',
      defaultValue: 'android',
    );
    const androidBannerId = String.fromEnvironment(
      'ADMOB_ANDROID_BANNER_ID',
      defaultValue: 'ca-app-pub-4624889874966809/2715711480',
    );
    const iosBannerId = String.fromEnvironment(
      'ADMOB_IOS_BANNER_ID',
      defaultValue: 'ca-app-pub-3940256099942544/2435281174',
    );
    const androidNativeId = String.fromEnvironment(
      'ADMOB_ANDROID_NATIVE_ID',
      defaultValue: 'ca-app-pub-4624889874966809/3665725872',
    );
    const iosNativeId = String.fromEnvironment(
      'ADMOB_IOS_NATIVE_ID',
      defaultValue: 'ca-app-pub-3940256099942544/3986624511',
    );
    const androidInterstitialId = String.fromEnvironment(
      'ADMOB_ANDROID_INTERSTITIAL_ID',
      defaultValue: 'ca-app-pub-4624889874966809/7776466476',
    );
    const iosInterstitialId = String.fromEnvironment(
      'ADMOB_IOS_INTERSTITIAL_ID',
      defaultValue: 'ca-app-pub-3940256099942544/4411468910',
    );
    const config = AppConfig(
      apiBaseUrl: configuredUrl,
      admobAndroidBannerId: androidBannerId,
      admobIosBannerId: iosBannerId,
      admobAndroidNativeId: androidNativeId,
      admobIosNativeId: iosNativeId,
      admobAndroidInterstitialId: androidInterstitialId,
      admobIosInterstitialId: iosInterstitialId,
      appEnvironment: environment,
      releasePlatform: configuredReleasePlatform,
    );
    config.validateForRuntime();
    return config;
  }
}

final appConfigProvider = Provider<AppConfig>((ref) {
  return AppConfig.fromEnvironment();
});

import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/config/app_config.dart';

AppConfig buildConfig({
  String environment = 'production',
  String apiBaseUrl = 'https://api.sahmikasban.example',
  String releasePlatform = 'android',
  String androidPublisher = '1234567890123456',
  String iosPublisher = '1234567890123456',
}) {
  return AppConfig(
    apiBaseUrl: apiBaseUrl,
    appEnvironment: environment,
    releasePlatform: releasePlatform,
    admobAndroidBannerId: 'ca-app-pub-$androidPublisher/1000000001',
    admobIosBannerId: 'ca-app-pub-$iosPublisher/1000000002',
    admobAndroidNativeId: 'ca-app-pub-$androidPublisher/1000000003',
    admobIosNativeId: 'ca-app-pub-$iosPublisher/1000000004',
    admobAndroidInterstitialId: 'ca-app-pub-$androidPublisher/1000000005',
    admobIosInterstitialId: 'ca-app-pub-$iosPublisher/1000000006',
  );
}

void main() {
  test(
    'production Android accepts live Android IDs with iOS test defaults',
    () {
      final config = buildConfig(iosPublisher: AppConfig.googleTestPublisherId);

      expect(config.validateForRuntime, returnsNormally);
    },
  );

  test('production iOS accepts live iOS IDs with Android test defaults', () {
    final config = buildConfig(
      releasePlatform: 'ios',
      androidPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, returnsNormally);
  });

  test('production config rejects an insecure API URL', () {
    final config = buildConfig(apiBaseUrl: 'http://api.example.com');

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production Android rejects Google test Android ad units', () {
    final config = buildConfig(
      androidPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production iOS rejects Google test iOS ad units', () {
    final config = buildConfig(
      releasePlatform: 'ios',
      iosPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production rejects an unknown release platform', () {
    final config = buildConfig(releasePlatform: 'web');

    expect(config.validateForRuntime, throwsStateError);
  });

  test('staging config keeps test integrations available', () {
    final config = buildConfig(
      environment: 'staging',
      apiBaseUrl: 'http://10.0.2.2:8000',
      androidPublisher: AppConfig.googleTestPublisherId,
      iosPublisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, returnsNormally);
  });
}

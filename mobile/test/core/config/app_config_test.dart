import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/config/app_config.dart';

AppConfig buildConfig({
  String environment = 'production',
  String apiBaseUrl = 'https://api.sahmikasban.example',
  String publisher = '1234567890123456',
}) {
  return AppConfig(
    apiBaseUrl: apiBaseUrl,
    appEnvironment: environment,
    admobAndroidBannerId: 'ca-app-pub-$publisher/1000000001',
    admobIosBannerId: 'ca-app-pub-$publisher/1000000002',
    admobAndroidNativeId: 'ca-app-pub-$publisher/1000000003',
    admobIosNativeId: 'ca-app-pub-$publisher/1000000004',
    admobAndroidInterstitialId: 'ca-app-pub-$publisher/1000000005',
    admobIosInterstitialId: 'ca-app-pub-$publisher/1000000006',
  );
}

void main() {
  test('production config accepts HTTPS and live AdMob IDs', () {
    expect(buildConfig().validateForRuntime, returnsNormally);
  });

  test('production config rejects an insecure API URL', () {
    final config = buildConfig(apiBaseUrl: 'http://api.example.com');

    expect(config.validateForRuntime, throwsStateError);
  });

  test('production config rejects Google test ad units', () {
    final config = buildConfig(publisher: AppConfig.googleTestPublisherId);

    expect(config.validateForRuntime, throwsStateError);
  });

  test('staging config keeps test integrations available', () {
    final config = buildConfig(
      environment: 'staging',
      apiBaseUrl: 'http://10.0.2.2:8000',
      publisher: AppConfig.googleTestPublisherId,
    );

    expect(config.validateForRuntime, returnsNormally);
  });
}

import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.admobAndroidBannerId,
    required this.admobIosBannerId,
  });

  final String apiBaseUrl;
  final String admobAndroidBannerId;
  final String admobIosBannerId;

  factory AppConfig.fromEnvironment() {
    const configuredUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:8000',
    );
    const androidBannerId = String.fromEnvironment(
      'ADMOB_ANDROID_BANNER_ID',
      defaultValue: 'ca-app-pub-3940256099942544/9214589741',
    );
    const iosBannerId = String.fromEnvironment(
      'ADMOB_IOS_BANNER_ID',
      defaultValue: 'ca-app-pub-3940256099942544/2435281174',
    );
    return const AppConfig(
      apiBaseUrl: configuredUrl,
      admobAndroidBannerId: androidBannerId,
      admobIosBannerId: iosBannerId,
    );
  }
}

final appConfigProvider = Provider<AppConfig>((ref) {
  return AppConfig.fromEnvironment();
});

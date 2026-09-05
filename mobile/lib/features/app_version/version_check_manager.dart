import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/network/api_client.dart';

const int currentAppVersionCode = 28;

class AppVersionInfo {
  const AppVersionInfo({
    required this.latestVersion,
    required this.latestVersionCode,
    required this.minRequiredVersionCode,
    required this.playStoreUrl,
    required this.titleAr,
    required this.messageAr,
    required this.forceUpdate,
  });

  final String latestVersion;
  final int latestVersionCode;
  final int minRequiredVersionCode;
  final String playStoreUrl;
  final String titleAr;
  final String messageAr;
  final bool forceUpdate;

  factory AppVersionInfo.fromJson(Map<String, dynamic> json) {
    return AppVersionInfo(
      latestVersion: (json['latest_version'] as String?) ?? '1.0.1+28',
      latestVersionCode: (json['latest_version_code'] as num?)?.toInt() ?? 28,
      minRequiredVersionCode:
          (json['min_required_version_code'] as num?)?.toInt() ?? 1,
      playStoreUrl: (json['play_store_url'] as String?) ??
          'https://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile',
      titleAr: (json['title_ar'] as String?) ?? 'يتوفر تحديث جديد للتطبيق',
      messageAr: (json['message_ar'] as String?) ??
          'يتوفر إصدار أحدث للتطبيق يحتوي على تحسينات هامة وميزات جديدة. يرجى التحديث الآن للحصول على أفضل تجربة.',
      forceUpdate: (json['force_update'] as bool?) ?? false,
    );
  }
}

class VersionCheckManager {
  VersionCheckManager(this._apiClient);

  final ApiClient _apiClient;

  Future<AppVersionInfo?> checkVersion() async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>('/app/version');
      if (response.data != null) {
        return AppVersionInfo.fromJson(response.data!);
      }
    } on Object {
      // Fail gracefully on version check network errors
    }
    return null;
  }

  Future<void> checkAndShowPrompt(BuildContext context) async {
    final versionInfo = await checkVersion();
    if (versionInfo == null || !context.mounted) {
      return;
    }

    final isOutdated = versionInfo.latestVersionCode > currentAppVersionCode;
    final isForceUpdate = versionInfo.forceUpdate ||
        currentAppVersionCode < versionInfo.minRequiredVersionCode;

    if (isOutdated || isForceUpdate) {
      showDialog<void>(
        context: context,
        barrierDismissible: !isForceUpdate,
        builder: (dialogContext) {
          return PopScope(
            canPop: !isForceUpdate,
            child: AlertDialog(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              title: Row(
                children: [
                  const Icon(Icons.system_update_rounded, color: Colors.amber),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      versionInfo.titleAr,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              content: Text(
                versionInfo.messageAr,
                style: const TextStyle(height: 1.4),
              ),
              actions: [
                if (!isForceUpdate)
                  TextButton(
                    onPressed: () => Navigator.of(dialogContext).pop(),
                    child: const Text('لاحقاً'),
                  ),
                FilledButton.icon(
                  onPressed: () async {
                    final uri = Uri.parse(versionInfo.playStoreUrl);
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                    }
                  },
                  icon: const Icon(Icons.open_in_new_rounded),
                  label: const Text('تحديث الآن'),
                ),
              ],
            ),
          );
        },
      );
    }
  }
}

final versionCheckManagerProvider = Provider<VersionCheckManager>((ref) {
  return VersionCheckManager(ref.watch(apiClientProvider));
});

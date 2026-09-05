import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

const String _keyAnalysisCount = 'rating_analysis_count';
const String _keyNextTargetCount = 'rating_next_target_count';
const String _keyHasRatedOrRefused = 'rating_has_rated_or_refused';

const String playStoreUrl =
    'https://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile';

class RatingPromptManager {
  RatingPromptManager();

  /// Call this when an analysis is completed successfully.
  Future<void> recordCompletedAnalysis(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();

    final bool hasRatedOrRefused =
        prefs.getBool(_keyHasRatedOrRefused) ?? false;
    if (hasRatedOrRefused) {
      return;
    }

    final int currentCount = (prefs.getInt(_keyAnalysisCount) ?? 0) + 1;
    await prefs.setInt(_keyAnalysisCount, currentCount);

    final int targetCount = prefs.getInt(_keyNextTargetCount) ?? 3;

    if (currentCount >= targetCount && context.mounted) {
      await showRatingBottomSheet(context);
    }
  }

  Future<void> showRatingBottomSheet(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    if (!context.mounted) return;

    await showModalBottomSheet<void>(
      context: context,
      isDismissible: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (sheetContext) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 48,
                height: 5,
                margin: const EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(
                  color: Colors.grey[600],
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              const Icon(Icons.star_rounded, size: 56, color: Colors.amber),
              const SizedBox(height: 12),
              Text(
                'ما رأيك في تطبيق سهمي كسبان؟',
                style: Theme.of(sheetContext).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                'تقييمك يساعدنا على تقديم ميزات جديدة وتحسين جودة التحليلات الذكية باستمرار.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey, height: 1.4),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () async {
                    Navigator.of(sheetContext).pop();
                    await prefs.setBool(_keyHasRatedOrRefused, true);
                    final uri = Uri.parse(playStoreUrl);
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(uri,
                          mode: LaunchMode.externalApplication);
                    }
                  },
                  icon: const Icon(Icons.star_rate_rounded),
                  label: const Text('تقييم الآن ⭐⭐⭐⭐⭐'),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () async {
                        Navigator.of(sheetContext).pop();
                        final int count = prefs.getInt(_keyAnalysisCount) ?? 3;
                        await prefs.setInt(_keyNextTargetCount, count + 20);
                      },
                      child: const Text('تذكيري لاحقاً'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextButton(
                      onPressed: () async {
                        Navigator.of(sheetContext).pop();
                        await prefs.setBool(_keyHasRatedOrRefused, true);
                      },
                      child: const Text('لا شكراً'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
            ],
          ),
        );
      },
    );
  }
}

final ratingPromptManagerProvider = Provider<RatingPromptManager>((ref) {
  return RatingPromptManager();
});

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

class ReferralGateDialog extends StatelessWidget {
  const ReferralGateDialog({
    super.key,
    required this.currentCount,
    required this.requiredCount,
    required this.referralCode,
  });

  final int currentCount;
  final int requiredCount;
  final String referralCode;

  static Future<void> show(
    BuildContext context, {
    required int currentCount,
    required int requiredCount,
    required String referralCode,
  }) {
    return showDialog<void>(
      context: context,
      builder: (_) => ReferralGateDialog(
        currentCount: currentCount,
        requiredCount: requiredCount,
        referralCode: referralCode,
      ),
    );
  }

  void _copyCode(BuildContext context) {
    Clipboard.setData(ClipboardData(text: referralCode));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم نسخ كود الإحالة بنجاح')),
    );
  }

  void _shareWhatsApp(BuildContext context) {
    final text = Uri.encodeComponent(
      'حمل تطبيق سهمي كسبان واستخدم كود الدعوة الخاص بي: $referralCode للحصول على 10 عملات مجانية!\nhttps://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile',
    );
    launchUrl(
      Uri.parse('https://wa.me/?text=$text'),
      mode: LaunchMode.externalApplication,
    );
  }

  void _shareTelegram(BuildContext context) {
    final text = Uri.encodeComponent(
      'حمل تطبيق سهمي كسبان واستخدم كود الدعوة الخاص بي: $referralCode للحصول على 10 عملات مجانية!',
    );
    final url = Uri.encodeComponent(
      'https://play.google.com/store/apps/details?id=com.sahmikasban.sahmi_kasban_mobile',
    );
    launchUrl(
      Uri.parse('https://t.me/share/url?url=$url&text=$text'),
      mode: LaunchMode.externalApplication,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final progress = (currentCount / requiredCount).clamp(0.0, 1.0);

    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Column(
        children: const [
          Icon(
            Icons.lock_outlined,
            size: 44,
            color: Colors.amber,
          ),
          SizedBox(height: 8),
          Text(
            'تفعيل المساعد الذكي المباشر',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'ميزة المساعد الذكي تقتصر على الأعضاء المساهمين في نمو مجتمع التطبيق.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),

            // Progress Indicator
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'تقدم الدعوات:',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '$currentCount / $requiredCount دعوات',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: progress,
                    minHeight: 8,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Referral Code Box
            InkWell(
              onTap: () => _copyCode(context),
              borderRadius: BorderRadius.circular(10),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  border: Border.all(color: theme.colorScheme.primary),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      referralCode,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const Icon(Icons.copy, size: 20),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Share Buttons Row
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _shareWhatsApp(context),
                    icon: const Icon(Icons.send_rounded, color: Colors.green),
                    label: const Text('واتساب'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _shareTelegram(context),
                    icon: const Icon(Icons.telegram, color: Colors.blue),
                    label: const Text('تليجرام'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('إغلاق'),
        ),
      ],
    );
  }
}

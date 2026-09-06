import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class BrandedAnalysisCardDialog extends StatelessWidget {
  const BrandedAnalysisCardDialog({
    required this.ticker,
    required this.signal,
    required this.score,
    required this.confidence,
    required this.explanation,
    super.key,
  });

  final String ticker;
  final String signal;
  final double? score;
  final double? confidence;
  final String explanation;

  static const String signatureText = '''
--------------------------------------------------
تم استخراج هذا التحليل عبر تطبيق سهمي كسبان (Sahmi Kasban)
حمل تطبيق سهمي كسبان من علي متجر بلاي
--------------------------------------------------''';

  String _buildCopyableText() {
    final cleanExplanation = explanation
        .replaceAll(RegExp(r'[#*`_]'), '')
        .trim();
    final scoreStr = score != null ? '${score!.toStringAsFixed(1)}/100' : 'غير متوفر';
    final confStr = confidence != null ? '${confidence!.toStringAsFixed(0)}%' : 'غير متوفر';

    return '''
تقرير تحليل سهم: $ticker
القرار الآلي: $signal
تقييم الجودة: $scoreStr
نسبة الثقة: $confStr

ملخص التحليل:
$cleanExplanation

$signatureText''';
  }

  void _copyToClipboard(BuildContext context) {
    final text = _buildCopyableText();
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم نسخ التحليل مع رابط التطبيق بنجاح'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreVal = score != null ? score!.toStringAsFixed(1) : '-';

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 450),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0F172A),
              Color(0xFF1E293B),
            ],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header Brand Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.amber.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.amber, width: 1),
                    ),
                    child: const Text(
                      'سهمي كسبان | SAHMI KASBAN',
                      style: TextStyle(
                        color: Colors.amber,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Ticker and Signal Row
              Row(
                children: [
                  Text(
                    ticker,
                    textDirection: TextDirection.ltr,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      signal,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Metrics Card
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.white12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Column(
                      children: [
                        const Text(
                          'تقييم الجودة',
                          style: TextStyle(color: Colors.white60, fontSize: 11),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '$scoreVal/100',
                          style: const TextStyle(
                            color: Colors.amber,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    Container(height: 24, width: 1, color: Colors.white12),
                    Column(
                      children: [
                        const Text(
                          'نسبة الثقة',
                          style: TextStyle(color: Colors.white60, fontSize: 11),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          confidence != null ? '${confidence!.toStringAsFixed(0)}%' : '-',
                          style: const TextStyle(
                            color: Colors.lightGreenAccent,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Signature Branding Callout Box
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.black38,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.white10),
                ),
                child: Column(
                  children: [
                    const Text(
                      'تم استخراج هذا التحليل عبر تطبيق سهمي كسبان (Sahmi Kasban)',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'حمل تطبيق سهمي كسبان من علي متجر بلاي',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: theme.colorScheme.primaryContainer,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: () => _copyToClipboard(context),
                      icon: const Icon(Icons.content_copy_rounded, size: 18),
                      label: const Text('نسخ التحليل نصياً'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Colors.white30),
                    ),
                    child: const Text('إغلاق'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

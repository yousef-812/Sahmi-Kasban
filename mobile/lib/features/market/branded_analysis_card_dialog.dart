import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class BrandedAnalysisCardDialog extends StatelessWidget {
  const BrandedAnalysisCardDialog({
    required this.ticker,
    required this.signal,
    required this.score,
    required this.confidence,
    required this.explanation,
    this.tradePlan = const {},
    super.key,
  });

  final String ticker;
  final String signal;
  final double? score;
  final double? confidence;
  final String explanation;
  final Map<String, dynamic> tradePlan;

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

    final StringBuffer sb = StringBuffer();
    sb.writeln('تقرير تحليل سهم شامل: $ticker');
    sb.writeln('القرار الآلي: $signal');
    sb.writeln('تقييم الجودة: $scoreStr | نسبة الثقة: $confStr');
    if (tradePlan.isNotEmpty) {
      sb.writeln('--- خطة التداول الافتراضية ---');
      if (tradePlan['entry'] != null) sb.writeln('سعر الدخول: ${tradePlan['entry']}');
      if (tradePlan['target_1'] != null) sb.writeln('الهدف الأول: ${tradePlan['target_1']}');
      if (tradePlan['target_2'] != null) sb.writeln('الهدف الثاني: ${tradePlan['target_2']}');
      if (tradePlan['stop_loss'] != null) sb.writeln('وقف الخسارة: ${tradePlan['stop_loss']}');
    }
    sb.writeln('\nملخص التحليل الفني:');
    sb.writeln(cleanExplanation);
    sb.writeln('\n$signatureText');
    return sb.toString();
  }

  void _copyToClipboard(BuildContext context) {
    final text = _buildCopyableText();
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم نسخ التحليل كاملاً مع بيانات التداول بنجاح'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreVal = score != null ? score!.toStringAsFixed(1) : '-';
    final confVal = confidence != null ? '${confidence!.toStringAsFixed(0)}%' : '-';
    final cleanExplanation = explanation.replaceAll(RegExp(r'[#*`_]'), '').trim();

    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 680),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0F172A),
              Color(0xFF1E293B),
              Color(0xFF0F172A),
            ],
          ),
          border: Border.all(color: Colors.amber.withValues(alpha: 0.3), width: 1.5),
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
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                    decoration: BoxDecoration(
                      color: Colors.amber.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.amber, width: 1.2),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.show_chart_rounded, color: Colors.amber, size: 18),
                        SizedBox(width: 6),
                        Text(
                          'سهمي كسبان | SAHMI KASBAN',
                          style: TextStyle(
                            color: Colors.amber,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 18),

              // Main Header: Ticker & Recommendation Signal
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.04),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white12),
                ),
                child: Row(
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          ticker,
                          textDirection: TextDirection.ltr,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 34,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'تحليل شامل ومفصل للسهم',
                          style: TextStyle(color: Colors.white60, fontSize: 12),
                        ),
                      ],
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            theme.colorScheme.primary,
                            theme.colorScheme.primary.withValues(alpha: 0.8),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: [
                          BoxShadow(
                            color: theme.colorScheme.primary.withValues(alpha: 0.4),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          const Text(
                            'القرار الآلي',
                            style: TextStyle(color: Colors.white70, fontSize: 10),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            signal,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w900,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              // Key Indicators & Scores Row
              Row(
                children: [
                  Expanded(
                    child: _InfoTile(
                      label: 'تقييم الجودة',
                      value: '$scoreVal/100',
                      color: Colors.amber,
                      icon: Icons.workspace_premium_rounded,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _InfoTile(
                      label: 'نسبة الثقة',
                      value: confVal,
                      color: Colors.lightGreenAccent,
                      icon: Icons.verified_user_rounded,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              // Trade Plan Grid Section (if available)
              if (tradePlan.isNotEmpty) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.black26,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.alt_route_rounded, color: Colors.cyanAccent, size: 18),
                          SizedBox(width: 6),
                          Text(
                            'خطة التداول الأهداف والمخاطر',
                            style: TextStyle(
                              color: Colors.cyanAccent,
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          if (tradePlan['entry'] != null)
                            Expanded(
                              child: _PlanCell(
                                label: 'سعر الدخول',
                                value: '${tradePlan['entry']}',
                                color: Colors.white,
                              ),
                            ),
                          if (tradePlan['stop_loss'] != null)
                            Expanded(
                              child: _PlanCell(
                                label: 'وقف الخسارة',
                                value: '${tradePlan['stop_loss']}',
                                color: Colors.redAccent,
                              ),
                            ),
                          if (tradePlan['target_1'] != null)
                            Expanded(
                              child: _PlanCell(
                                label: 'الهدف الأول',
                                value: '${tradePlan['target_1']}',
                                color: Colors.greenAccent,
                              ),
                            ),
                          if (tradePlan['target_2'] != null)
                            Expanded(
                              child: _PlanCell(
                                label: 'الهدف الثاني',
                                value: '${tradePlan['target_2']}',
                                color: Colors.green,
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 14),
              ],

              // Full Analysis Summary Box
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.03),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.white12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.notes_rounded, color: Colors.white70, size: 18),
                        SizedBox(width: 6),
                        Text(
                          'ملخص التحليل الفني والمالي',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      cleanExplanation,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 13,
                        height: 1.6,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Signature Branding Callout Box
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.amber.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.amber.withValues(alpha: 0.3)),
                ),
                child: Column(
                  children: [
                    const Text(
                      'تم استخراج هذا التحليل الشامل عبر تطبيق سهمي كسبان (Sahmi Kasban)',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.amber,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'حمل تطبيق سهمي كسبان الآن من متجر بلاي للحصول على تحليلات دقيقة يومياً',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: theme.colorScheme.primaryContainer,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
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
                  const SizedBox(width: 10),
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

class _InfoTile extends StatelessWidget {
  const _InfoTile({
    required this.label,
    required this.value,
    required this.color,
    required this.icon,
  });

  final String label;
  final String value;
  final Color color;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(color: Colors.white60, fontSize: 11),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  color: color,
                  fontSize: 16,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PlanCell extends StatelessWidget {
  const _PlanCell({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white60, fontSize: 10),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: TextStyle(
            color: color,
            fontSize: 13,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

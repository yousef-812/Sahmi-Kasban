import 'package:flutter/material.dart';

class StructuredDataCard extends StatelessWidget {
  const StructuredDataCard({
    required this.title,
    required this.data,
    this.initiallyExpanded = true,
    super.key,
  });

  final String title;
  final Map<String, dynamic> data;
  final bool initiallyExpanded;

  @override
  Widget build(BuildContext context) {
    if (title.contains('البيانات التقنية الخام')) {
      return const SizedBox.shrink();
    }
    final rows = _friendlyRows(data);
    if (rows.isEmpty) {
      return const SizedBox.shrink();
    }
    return Card(
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        leading: const Icon(Icons.fact_check_outlined),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [
          for (final row in rows)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 4,
                    child: Text(
                      row.label,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 5,
                    child: Text(
                      row.value,
                      textAlign: TextAlign.end,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _FriendlyRow {
  const _FriendlyRow(this.label, this.value);

  final String label;
  final String value;
}

const _hiddenKeys = <String>{
  'fingerprint',
  'content_fingerprint',
  'submission_key',
  'reason_codes',
  'checks',
  'attempted_at',
  'attempts',
  'version',
  'engines',
  'analysis',
  'market_data',
};

const _labels = <String, String>{
  'title': 'العنوان',
  'decision': 'القرار',
  'signal': 'الإشارة',
  'score': 'الدرجة',
  'final_score': 'الدرجة النهائية',
  'confidence': 'الثقة',
  'price_at_analysis': 'السعر وقت التحليل',
  'expected_direction': 'الاتجاه المتوقع',
  'qualified': 'اجتاز شروط التأهيل',
  'explanation': 'التفسير',
  'disclaimer': 'تنبيه',
  'source_session_date': 'جلسة البيانات',
  'target_session_date': 'الجلسة المستهدفة',
  'analyzed_count': 'الأسهم التي تم تحليلها',
  'eligible_count': 'الأسهم المؤهلة',
  'failed_count': 'الأسهم المتعذر تحليلها',
  'average_top_score': 'متوسط درجة أفضل الأسهم',
  'rules': 'فحص قواعد النشر',
  'passed': 'اجتاز الفحص',
  'stage': 'مرحلة الفحص',
  'review_stage': 'حالة المراجعة',
  'ai': 'مراجعة الذكاء الاصطناعي',
  'status': 'الحالة',
  'error_code': 'سبب التعذر',
  'direction': 'الاتجاه',
  'target': 'الهدف',
  'target_price': 'السعر المستهدف',
  'stop_loss': 'وقف الخسارة',
  'entry': 'الدخول',
  'period': 'المدة',
  'period_type': 'المدة',
  'summary': 'الملخص',
  'reason': 'السبب',
};

List<_FriendlyRow> _friendlyRows(Map<String, dynamic> source) {
  final rows = <_FriendlyRow>[];
  void visit(Map<String, dynamic> data, {String? parent}) {
    for (final entry in data.entries) {
      if (_hiddenKeys.contains(entry.key) || rows.length >= 14) {
        continue;
      }
      final value = entry.value;
      final label = _labels[entry.key] ?? parent ?? _humanize(entry.key);
      if (value is Map) {
        visit(Map<String, dynamic>.from(value), parent: label);
      } else if (value is List) {
        final visible = value
            .where((item) => item is String || item is num || item is bool)
            .map(_formatValue)
            .where((item) => item.isNotEmpty)
            .take(4)
            .toList(growable: false);
        if (visible.isNotEmpty) {
          rows.add(_FriendlyRow(label, visible.join('، ')));
        }
      } else {
        final formatted = _formatValue(value);
        if (formatted.isNotEmpty) {
          rows.add(_FriendlyRow(label, formatted));
        }
      }
    }
  }

  visit(source);
  return rows;
}

String _humanize(String key) {
  return key.replaceAll('_', ' ').trim();
}

String _formatValue(Object? value) {
  if (value == null) {
    return '';
  }
  if (value is bool) {
    return value ? 'نعم' : 'لا';
  }
  if (value is num) {
    return value is double ? value.toStringAsFixed(2) : value.toString();
  }
  final raw = value.toString().trim();
  const statuses = <String, String>{
    'BUY': 'شراء مشروط',
    'WATCH': 'مراقبة',
    'AVOID': 'تجنب',
    'up': 'صعود',
    'down': 'هبوط',
    'pending_review': 'قيد المراجعة',
    'awaiting_ai_retry': 'بانتظار إعادة مراجعة الذكاء الاصطناعي',
    'failed': 'متعذرة مؤقتًا',
    'provider_unavailable': 'مزود الذكاء الاصطناعي غير متاح',
    'rules': 'فحص القواعد',
  };
  return statuses[raw] ?? raw;
}

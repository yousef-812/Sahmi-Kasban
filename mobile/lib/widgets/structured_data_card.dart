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
    final visible = data.entries
        .where((entry) => !_hiddenKeys.contains(entry.key))
        .toList(growable: false);
    if (visible.isEmpty) {
      return const SizedBox.shrink();
    }
    return Card(
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [
          for (final entry in visible)
            _ReadableEntry(label: _label(entry.key), value: entry.value),
        ],
      ),
    );
  }
}

class _ReadableEntry extends StatelessWidget {
  const _ReadableEntry({required this.label, required this.value});

  final String label;
  final Object? value;

  @override
  Widget build(BuildContext context) {
    if (value is Map) {
      final map = Map<String, dynamic>.from(value! as Map);
      final entries = map.entries
          .where((entry) => !_hiddenKeys.contains(entry.key))
          .toList(growable: false);
      if (entries.isEmpty) {
        return const SizedBox.shrink();
      }
      return Container(
        width: double.infinity,
        margin: const EdgeInsets.only(top: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(label, style: const TextStyle(fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            for (final entry in entries)
              _ReadableEntry(label: _label(entry.key), value: entry.value),
          ],
        ),
      );
    }
    if (value is List) {
      final items = (value! as List)
          .map(_displayValue)
          .where((item) => item.isNotEmpty)
          .toList(growable: false);
      if (items.isEmpty) {
        return const SizedBox.shrink();
      }
      return _ValueRow(label: label, value: items.join('، '));
    }
    return _ValueRow(label: label, value: _displayValue(value));
  }
}

class _ValueRow extends StatelessWidget {
  const _ValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    if (value.isEmpty) {
      return const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: Text(label)),
          const SizedBox(width: 12),
          Flexible(
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}

const _hiddenKeys = <String>{
  'fingerprint',
  'content_fingerprint',
  'submission_key',
  'provider_message_id',
  'raw',
};

String _label(String key) => _labels[key] ?? key.replaceAll('_', ' ');

String _displayValue(Object? value) {
  if (value == null) {
    return 'غير متاح';
  }
  if (value is bool) {
    return value ? 'نعم' : 'لا';
  }
  final text = value.toString().trim();
  return _valueLabels[text] ?? text;
}

const _labels = <String, String>{
  'rules': 'فحص القواعد',
  'stage': 'المرحلة',
  'passed': 'النتيجة',
  'reason_codes': 'أسباب القرار',
  'checks': 'الفحوصات',
  'external_link': 'رابط خارجي',
  'phone_number': 'رقم هاتف',
  'contact_details': 'بيانات تواصل',
  'advertisement': 'إعلان',
  'profit_guarantee': 'ضمان أرباح',
  'abusive_content': 'محتوى مسيء',
  'review_stage': 'حالة المراجعة',
  'ai': 'مراجعة الذكاء الاصطناعي',
  'status': 'الحالة',
  'error_code': 'سبب التعطل',
  'attempts': 'عدد المحاولات',
  'attempted_at': 'آخر محاولة',
  'direction': 'الاتجاه المتوقع',
  'target': 'السعر المستهدف',
  'stop_loss': 'وقف الخسارة',
  'confidence': 'الثقة',
  'period_type': 'الفترة',
  'price_at_submission': 'السعر وقت النشر',
  'source': 'المصدر',
  'explanation': 'التفسير',
  'score': 'الدرجة',
  'reward_points': 'المكافأة',
};

const _valueLabels = <String, String>{
  'deterministic_rules': 'فحص آلي ثابت',
  'awaiting_ai_retry': 'في انتظار إعادة مراجعة الذكاء الاصطناعي',
  'provider_unavailable': 'مزود الذكاء الاصطناعي غير متاح مؤقتًا',
  'failed': 'تعذر التنفيذ',
  'passed': 'اجتاز الفحص',
  'published': 'منشورة',
  'pending_review': 'قيد المراجعة',
  'rejected': 'مرفوضة',
  'next_session': 'الجلسة القادمة',
  'week': 'أسبوع',
  'month': 'شهر',
  'up': 'صعود',
  'down': 'هبوط',
  'flat': 'ثبات',
};

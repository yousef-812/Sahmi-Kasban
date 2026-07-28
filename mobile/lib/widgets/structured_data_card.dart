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
    return Card(
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [
          if (data.isEmpty)
            const Padding(
              padding: EdgeInsets.all(12),
              child: Text('لا توجد تفاصيل إضافية.'),
            )
          else
            _ReadableMap(data: data),
        ],
      ),
    );
  }
}

class _ReadableMap extends StatelessWidget {
  const _ReadableMap({required this.data, this.depth = 0});

  final Map<String, dynamic> data;
  final int depth;

  @override
  Widget build(BuildContext context) {
    final entries = data.entries
        .where((entry) => !_hiddenKeys.contains(entry.key))
        .toList(growable: false);
    if (entries.isEmpty) {
      return const Text('لا توجد تفاصيل إضافية.');
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var index = 0; index < entries.length; index++) ...[
          _ReadableEntry(
            label: _labelFor(entries[index].key),
            value: entries[index].value,
            depth: depth,
          ),
          if (index != entries.length - 1) const Divider(height: 18),
        ],
      ],
    );
  }
}

class _ReadableEntry extends StatelessWidget {
  const _ReadableEntry({
    required this.label,
    required this.value,
    required this.depth,
  });

  final String label;
  final dynamic value;
  final int depth;

  @override
  Widget build(BuildContext context) {
    if (value is Map) {
      final nested = value.map<String, dynamic>(
        (key, item) => MapEntry(key.toString(), item),
      );
      return ExpansionTile(
        tilePadding: EdgeInsets.zero,
        childrenPadding: const EdgeInsetsDirectional.only(start: 12, bottom: 8),
        initiallyExpanded: depth == 0,
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        children: [_ReadableMap(data: nested, depth: depth + 1)],
      );
    }
    if (value is List) {
      if (value.isEmpty) {
        return _ValueRow(label: label, value: 'لا يوجد');
      }
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          for (final item in value)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(top: 7),
                    child: Icon(Icons.circle, size: 6),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _ReadableValue(value: item, depth: depth + 1),
                  ),
                ],
              ),
            ),
        ],
      );
    }
    return _ValueRow(label: label, value: _formatValue(value));
  }
}

class _ReadableValue extends StatelessWidget {
  const _ReadableValue({required this.value, required this.depth});

  final dynamic value;
  final int depth;

  @override
  Widget build(BuildContext context) {
    if (value is Map) {
      return _ReadableMap(
        data: value.map<String, dynamic>(
          (key, item) => MapEntry(key.toString(), item),
        ),
        depth: depth,
      );
    }
    if (value is List) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [for (final item in value) Text('• ${_formatValue(item)}')],
      );
    }
    return Text(_formatValue(value));
  }
}

class _ValueRow extends StatelessWidget {
  const _ValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 4,
          child: Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(flex: 5, child: Text(value, textAlign: TextAlign.end)),
      ],
    );
  }
}

const _hiddenKeys = <String>{
  'fingerprint',
  'source_text_sha256',
  'cache_key',
  'version',
};

const _labels = <String, String>{
  'stage': 'مرحلة الفحص',
  'passed': 'اجتاز الفحص',
  'reason_codes': 'أسباب المراجعة',
  'checks': 'فحوص المحتوى',
  'external_link': 'رابط خارجي',
  'phone_number': 'رقم هاتف',
  'contact_details': 'بيانات تواصل',
  'advertisement': 'محتوى إعلاني',
  'profit_guarantee': 'ضمان ربح',
  'abusive_content': 'محتوى مسيء',
  'review_stage': 'حالة المراجعة',
  'ai': 'مراجعة الذكاء الاصطناعي',
  'status': 'الحالة',
  'error_code': 'سبب التعذر',
  'attempts': 'عدد المحاولات',
  'attempted_at': 'وقت آخر محاولة',
  'review': 'قرار المراجعة',
  'actor_type': 'جهة المراجعة',
  'decision': 'القرار',
  'reason_code': 'سبب القرار',
  'details': 'التفاصيل',
  'reviewed_at': 'وقت المراجعة',
  'ticker': 'رمز السهم',
  'direction': 'الاتجاه المتوقع',
  'target_price': 'السعر المستهدف',
  'period_type': 'مدة التوقع',
  'deadline': 'الموعد المستهدف',
  'claims': 'نقاط التوقع',
  'specificity': 'وضوح التوقع',
  'frozen_at': 'وقت تثبيت التوقع',
  'source_session_date': 'جلسة البيانات',
  'target_session_date': 'الجلسة المستهدفة',
  'analyzed_count': 'الأسهم التي تم تحليلها',
  'eligible_count': 'الأسهم المؤهلة',
  'failed_count': 'الأسهم التي تعذر تحليلها',
  'average_top_score': 'متوسط تقييم الأفضل',
  'signals': 'توزيع القرارات',
  'disclaimer': 'تنبيه مهم',
  'price_at_analysis': 'السعر وقت التحليل',
  'score': 'الدرجة',
  'signal': 'الإشارة',
  'expected_direction': 'الاتجاه المتوقع',
  'confidence': 'الثقة',
  'qualified': 'اجتاز شروط التأهيل',
  'liquidity': 'السيولة',
  'average_turnover_egp_20d': 'متوسط قيمة التداول 20 يوم',
  'nonzero_volume_ratio_20d': 'استمرارية التداول 20 يوم',
  'market_data': 'بيانات السوق',
  'provider': 'مصدر البيانات',
  'data_as_of': 'البيانات حتى',
  'candle_count': 'عدد الشموع',
  'explanation': 'شرح النتيجة',
  'explanation_source': 'مصدر الشرح',
  'analysis': 'تفاصيل التحليل',
  'entry': 'سعر الدخول',
  'stop_loss': 'وقف الخسارة',
  'target_1': 'الهدف الأول',
  'target_2': 'الهدف الثاني',
};

String _labelFor(String key) {
  final translated = _labels[key];
  if (translated != null) {
    return translated;
  }
  final normalized = key.replaceAll('_', ' ').trim();
  if (normalized.isEmpty) {
    return 'تفصيل';
  }
  return normalized[0].toUpperCase() + normalized.substring(1);
}

String _formatValue(dynamic value) {
  if (value == null) {
    return 'غير محدد';
  }
  if (value is bool) {
    return value ? 'نعم' : 'لا';
  }
  if (value is num) {
    return value is double ? value.toStringAsFixed(2) : value.toString();
  }
  final text = value.toString().trim();
  const translations = <String, String>{
    'true': 'نعم',
    'false': 'لا',
    'rules': 'فحص القواعد',
    'completed': 'مكتملة',
    'awaiting_ai': 'في انتظار المراجعة الذكية',
    'awaiting_ai_retry': 'تعذرت المراجعة الذكية وسيتم إعادة المحاولة',
    'failed': 'تعذرت المحاولة',
    'provider_unavailable': 'مزود الذكاء الاصطناعي غير متاح مؤقتًا',
    'approved': 'مقبول',
    'rejected': 'مرفوض',
    'published': 'منشور',
    'up': 'صعود',
    'down': 'هبوط',
    'neutral': 'حركة عرضية',
    'next_session': 'الجلسة القادمة',
    'week': 'أسبوع',
    'month': 'شهر',
    'BUY': 'شراء مشروط',
    'WATCH': 'مراقبة',
    'AVOID': 'تجنب',
    'ai': 'الذكاء الاصطناعي',
    'deterministic': 'المحرك التحليلي',
  };
  return translations[text] ?? (text.isEmpty ? 'غير محدد' : text);
}

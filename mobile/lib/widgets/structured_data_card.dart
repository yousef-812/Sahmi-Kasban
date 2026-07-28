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
    if (_isInternalTitle(title)) {
      return const SizedBox.shrink();
    }

    final visibleData = _visibleMap(data);
    if (visibleData.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: ExpansionTile(
        initiallyExpanded: initiallyExpanded,
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        children: [_ReadableMap(data: visibleData)],
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
    final entries = _visibleMap(data).entries.toList(growable: false);
    if (entries.isEmpty) {
      return const SizedBox.shrink();
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
    final currentValue = value;
    if (currentValue is Map<Object?, Object?>) {
      final nested = _visibleMap({
        for (final entry in currentValue.entries)
          entry.key.toString(): entry.value,
      });
      if (nested.isEmpty) {
        return const SizedBox.shrink();
      }
      return ExpansionTile(
        tilePadding: EdgeInsets.zero,
        childrenPadding: const EdgeInsetsDirectional.only(start: 12, bottom: 8),
        initiallyExpanded: depth == 0,
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        children: [_ReadableMap(data: nested, depth: depth + 1)],
      );
    }

    if (currentValue is List<Object?>) {
      if (currentValue.isEmpty) {
        return _ValueRow(label: label, value: 'لا يوجد');
      }
      final readable = currentValue
          .where((item) => item is! Map<Object?, Object?>)
          .map(_formatValue)
          .where((item) => item.isNotEmpty)
          .toList(growable: false);
      if (readable.isEmpty) {
        return const SizedBox.shrink();
      }
      return _ValueRow(label: label, value: readable.join('، '));
    }

    return _ValueRow(label: label, value: _formatValue(currentValue));
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
          child: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        ),
        const SizedBox(width: 12),
        Expanded(flex: 5, child: Text(value, textAlign: TextAlign.end)),
      ],
    );
  }
}

bool _isInternalTitle(String title) {
  final normalized = title.trim().toLowerCase();
  return normalized.contains('البيانات التقنية الخام') ||
      normalized.contains('raw data') ||
      normalized.contains('json');
}

Map<String, dynamic> _visibleMap(Map<String, dynamic> data) {
  return {
    for (final entry in data.entries)
      if (!_hiddenKeys.contains(entry.key) && entry.value != null)
        entry.key: entry.value,
  };
}

const _hiddenKeys = <String>{
  'fingerprint',
  'source_text_sha256',
  'cache_key',
  'version',
  'attempts',
  'attempted_at',
  'actor_type',
  'provider_message_id',
  'request_id',
  'trace_id',
  'debug',
  'diagnostics',
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
  'review': 'قرار المراجعة',
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
    return 'لا يوجد';
  }
  if (value is bool) {
    return value ? 'نعم' : 'لا';
  }
  if (value is num) {
    return value.toString();
  }
  final text = value.toString().trim();
  if (text.isEmpty) {
    return 'لا يوجد';
  }
  return switch (text.toLowerCase()) {
    'published' => 'منشور',
    'pending_review' => 'قيد المراجعة',
    'awaiting_ai_retry' => 'بانتظار إعادة المراجعة',
    'complete' => 'مكتمل',
    'completed' => 'مكتمل',
    'failed' => 'تعذر مؤقتًا',
    'provider_unavailable' => 'خدمة الذكاء الاصطناعي غير متاحة مؤقتًا',
    'buy' => 'شراء مشروط',
    'watch' => 'مراقبة',
    'avoid' => 'تجنب',
    'up' => 'صعود',
    'down' => 'هبوط',
    'neutral' => 'محايد',
    'ai' => 'ذكاء اصطناعي',
    'deterministic' => 'المحركات الحسابية',
    _ => text,
  };
}

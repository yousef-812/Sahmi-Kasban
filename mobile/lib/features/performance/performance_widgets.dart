import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'performance_models.dart';

String formatBasisPoints(int? value) {
  if (value == null) return '-';
  final percent = value / 100;
  return '${percent > 0 ? '+' : ''}${percent.toStringAsFixed(2)}%';
}

String formatPercent(double? value) {
  return value == null ? '-' : '${value.toStringAsFixed(1)}%';
}

String formatPerformanceDate(DateTime value, {bool includeTime = false}) {
  final local = value.toLocal();
  try {
    return DateFormat(
      includeTime ? 'd MMM yyyy – HH:mm' : 'EEEE d MMMM yyyy',
      'ar',
    ).format(local);
  } on Object {
    final day = local.day.toString().padLeft(2, '0');
    final month = local.month.toString().padLeft(2, '0');
    final year = local.year.toString();
    if (!includeTime) return '$day/$month/$year';
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');
    return '$day/$month/$year – $hour:$minute';
  }
}

double performanceProgress(double percent) {
  return (percent.clamp(0, 100) / 100).toDouble();
}

String performanceStatusLabel(String status) {
  return switch (status) {
    'complete' => 'مكتمل',
    'partial' => 'مكتمل جزئيًا',
    'pending' || 'pending_data' => 'بانتظار البيانات',
    'running' => 'جارٍ التقييم',
    'failed' => 'تعذر التقييم',
    'not_started' => 'لم يبدأ التقييم',
    'empty_report' => 'التقرير بلا نتائج',
    _ => status.trim().isEmpty ? 'غير محدد' : status,
  };
}

class PerformanceNotice extends StatelessWidget {
  const PerformanceNotice({super.key});

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.fact_check_outlined),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                'يعرض السجل النتائج الفعلية كما حدثت، بما فيها النتائج السلبية والبيانات الناقصة. الأداء السابق لا يضمن نتائج مستقبلية.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class PerformanceMetric extends StatelessWidget {
  const PerformanceMetric({
    required this.label,
    required this.value,
    super.key,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 156,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 6),
              Text(
                value,
                textDirection: TextDirection.ltr,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class PerformanceExtreme extends StatelessWidget {
  const PerformanceExtreme({
    required this.title,
    required this.item,
    super.key,
  });

  final String title;
  final PerformanceBestWorst? item;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title),
            const SizedBox(height: 6),
            Text(
              item?.ticker ?? '-',
              textDirection: TextDirection.ltr,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            Text(item == null ? '-' : formatBasisPoints(item!.returnBp)),
          ],
        ),
      ),
    );
  }
}

class PerformanceLoading extends StatelessWidget {
  const PerformanceLoading({super.key});

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class PerformanceFailure extends StatelessWidget {
  const PerformanceFailure({
    required this.message,
    required this.retry,
    super.key,
  });

  final String message;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 10),
            OutlinedButton(
              onPressed: retry,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

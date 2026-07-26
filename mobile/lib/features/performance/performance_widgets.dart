import 'package:flutter/material.dart';

import 'performance_models.dart';

String formatBasisPoints(int? value) {
  if (value == null) return '-';
  final percent = value / 100;
  return '${percent > 0 ? '+' : ''}${percent.toStringAsFixed(2)}%';
}

String formatPercent(double? value) {
  return value == null ? '-' : '${value.toStringAsFixed(1)}%';
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

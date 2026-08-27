import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/models.dart';
import 'report_providers.dart';

class ReportsScreen extends ConsumerWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final preview = ref.watch(latestReportPreviewProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('تقارير السوق')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(latestReportPreviewProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              'أحدث التقارير التحليلية للبورصة المصرية',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            preview.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stackTrace) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Icon(Icons.error_outline_rounded),
                      const SizedBox(height: 12),
                      Text('تعذر تحميل التقارير.'),
                      TextButton(
                        onPressed: () =>
                            ref.invalidate(latestReportPreviewProvider),
                        child: const Text('إعادة المحاولة'),
                      ),
                    ],
                  ),
                ),
              ),
              data: (report) => report == null
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(40),
                        child: Text('لا توجد تقارير متاحة حاليًا.'),
                      ),
                    )
                  : _ReportPreviewCard(report: report),
            ),
            const SizedBox(height: 24),
            const Text(
              'ملاحظة: يتم إصدار تقارير السوق بشكل دوري بناءً على مسح شامل لجميع الأسهم.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _ReportPreviewCard extends StatelessWidget {
  const _ReportPreviewCard({required this.report});

  final MarketReportPreview report;

  @override
  Widget build(BuildContext context) {
    final target = report.targetSessionDate;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_graph_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'تقرير جلسة ${target.day}/${target.month}/${target.year}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                Chip(label: Text('${report.itemCount} فرص مؤهلة')),
                Chip(
                  label: Text(
                    report.unlocked
                        ? 'مفتوح بالفعل'
                        : '${report.unlockCostCoins} عملة للفتح',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text('المقدمة مجانية ولا تعرض أسماء الأسهم قبل فتح التقرير.'),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: () =>
                  context.push('/reports/${report.reportId}', extra: report),
              icon: Icon(
                report.unlocked
                    ? Icons.visibility_rounded
                    : Icons.lock_open_rounded,
              ),
              label: Text(report.unlocked ? 'عرض التقرير' : 'فتح التقرير'),
            ),
          ],
        ),
      ),
    );
  }
}

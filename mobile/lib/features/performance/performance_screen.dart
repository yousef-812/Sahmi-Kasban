import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'performance_models.dart';
import 'performance_providers.dart';
import 'performance_widgets.dart';

class PerformanceScreen extends ConsumerWidget {
  const PerformanceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final window = ref.watch(performanceWindowProvider);
    final summary = ref.watch(performanceSummaryProvider);
    final reports = ref.watch(performanceReportsProvider);

    Future<void> refresh() async {
      await Future.wait([
        ref.refresh(performanceSummaryProvider.future),
        ref.refresh(performanceReportsProvider.future),
      ]);
    }

    return Scaffold(
      appBar: AppBar(title: const Text('سجل الأداء الفعلي')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: refresh,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              const PerformanceNotice(),
              const SizedBox(height: 14),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: SegmentedButton<int>(
                  showSelectedIcon: false,
                  segments: const [
                    ButtonSegment(value: 7, label: Text('آخر 7 جلسات')),
                    ButtonSegment(value: 30, label: Text('آخر 30 جلسة')),
                  ],
                  selected: <int>{window},
                  onSelectionChanged: (selection) {
                    ref.read(performanceWindowProvider.notifier).state =
                        selection.single;
                  },
                ),
              ),
              const SizedBox(height: 16),
              summary.when(
                loading: () => const PerformanceLoading(),
                error: (_, __) => PerformanceFailure(
                  message: 'تعذر تحميل إحصاءات الأداء.',
                  retry: () => ref.invalidate(performanceSummaryProvider),
                ),
                data: (value) => _SummarySection(summary: value),
              ),
              const SizedBox(height: 20),
              Text(
                'سجل الجلسات',
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 10),
              reports.when(
                loading: () => const PerformanceLoading(),
                error: (_, __) => PerformanceFailure(
                  message: 'تعذر تحميل سجل التقارير.',
                  retry: () => ref.invalidate(performanceReportsProvider),
                ),
                data: (page) => page.items.isEmpty
                    ? const Card(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Text(
                            'لا توجد جلسات قابلة للقياس حتى الآن.',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : Column(
                        children: page.items
                            .map((item) => _ReportCard(item: item))
                            .toList(growable: false),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SummarySection extends StatelessWidget {
  const _SummarySection({required this.summary});

  final PerformanceSummary summary;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'جودة البيانات',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 10),
                LinearProgressIndicator(
                  value: performanceProgress(summary.dataCompletenessPct),
                  minHeight: 10,
                  borderRadius: BorderRadius.circular(20),
                ),
                const SizedBox(height: 8),
                Text(
                  '${summary.dataCompletenessPct.toStringAsFixed(1)}% مكتملة • '
                  '${summary.completeSessions}/${summary.sessionsFound} جلسة مكتملة',
                ),
                if (summary.pendingItems > 0 || summary.failedItems > 0)
                  Text(
                    '${summary.pendingItems} تنتظر البيانات • '
                    '${summary.failedItems} فشلت في التقييم',
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        if (summary.evaluatedItems == 0)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(18),
              child: Text(
                'لم تكتمل أي نتيجة فعلية في المدة المختارة بعد. ستظهر المقاييس فور توفر بيانات إغلاق الجلسات.',
                textAlign: TextAlign.center,
              ),
            ),
          )
        else ...[
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              PerformanceMetric(
                label: 'متوسط الحركة',
                value: formatBasisPoints(summary.averageReturnBp),
              ),
              PerformanceMetric(
                label: 'وسيط الحركة',
                value: formatBasisPoints(summary.medianReturnBp),
              ),
              PerformanceMetric(
                label: 'الأسهم الصاعدة',
                value: '${summary.positiveCount}',
              ),
              PerformanceMetric(
                label: 'الأسهم الهابطة',
                value: '${summary.negativeCount}',
              ),
              PerformanceMetric(
                label: 'نسبة الصعود',
                value: formatPercent(summary.positiveRatePct),
              ),
              PerformanceMetric(
                label: 'دقة الاتجاه',
                value: formatPercent(summary.directionAccuracyPct),
              ),
              PerformanceMetric(
                label: 'تحقق الهدف الأول',
                value: formatPercent(summary.targetOneHitRatePct),
              ),
              PerformanceMetric(
                label: 'لمس وقف الخسارة',
                value: formatPercent(summary.stopLossHitRatePct),
              ),
            ],
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, constraints) {
              final cards = [
                Expanded(
                  child: PerformanceExtreme(
                    title: 'أفضل نتيجة',
                    item: summary.bestOutcome,
                  ),
                ),
                Expanded(
                  child: PerformanceExtreme(
                    title: 'أسوأ نتيجة',
                    item: summary.worstOutcome,
                  ),
                ),
              ];
              if (constraints.maxWidth >= 360) {
                return Row(
                  children: [cards.first, const SizedBox(width: 10), cards.last],
                );
              }
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  PerformanceExtreme(
                    title: 'أفضل نتيجة',
                    item: summary.bestOutcome,
                  ),
                  PerformanceExtreme(
                    title: 'أسوأ نتيجة',
                    item: summary.worstOutcome,
                  ),
                ],
              );
            },
          ),
          const SizedBox(height: 18),
          Text(
            'أداء المراكز من 1 إلى 10',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          Card(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('المركز')),
                  DataColumn(label: Text('النتائج')),
                  DataColumn(label: Text('المتوسط')),
                  DataColumn(label: Text('الصعود')),
                  DataColumn(label: Text('دقة الاتجاه')),
                ],
                rows: summary.ranks
                    .map(
                      (rank) => DataRow(
                        cells: [
                          DataCell(Text('${rank.rank}')),
                          DataCell(Text('${rank.evaluatedItems}')),
                          DataCell(
                            Text(formatBasisPoints(rank.averageReturnBp)),
                          ),
                          DataCell(Text(formatPercent(rank.positiveRatePct))),
                          DataCell(
                            Text(formatPercent(rank.directionAccuracyPct)),
                          ),
                        ],
                      ),
                    )
                    .toList(growable: false),
              ),
            ),
          ),
        ],
        if (summary.benchmark['status'] != 'available')
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'المقارنة مع EGX30 غير متاحة بعد، لذلك لا يتم عرض مقارنة تقديرية غير موثقة.',
              ),
            ),
          ),
      ],
    );
  }
}

class _ReportCard extends StatelessWidget {
  const _ReportCard({required this.item});

  final PerformanceReportListItem item;

  @override
  Widget build(BuildContext context) {
    final date = formatPerformanceDate(item.targetSessionDate);
    final status = performanceStatusLabel(item.evaluationStatus);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        onTap: () => context.push('/performance/reports/${item.reportId}'),
        isThreeLine: true,
        leading: CircleAvatar(child: Text('${item.evaluatedItems}')),
        title: Text(date, maxLines: 2, overflow: TextOverflow.ellipsis),
        subtitle: Text(
          '$status • ${item.dataCompletenessPct.toStringAsFixed(0)}% مكتملة\n'
          'متوسط ${formatBasisPoints(item.averageReturnBp)} • '
          '${item.positiveCount} صاعدة / ${item.negativeCount} هابطة',
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: const Icon(Icons.chevron_left_rounded),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import 'performance_models.dart';
import 'performance_providers.dart';
import 'performance_repository.dart';
import 'performance_widgets.dart';

class PerformanceAdminScreen extends ConsumerStatefulWidget {
  const PerformanceAdminScreen({super.key});

  @override
  ConsumerState<PerformanceAdminScreen> createState() =>
      _PerformanceAdminScreenState();
}

class _PerformanceAdminScreenState
    extends ConsumerState<PerformanceAdminScreen> {
  bool _busy = false;

  @override
  Widget build(BuildContext context) {
    final delayed = ref.watch(delayedPerformanceProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('تشغيل سجل الأداء')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async => ref.invalidate(delayedPerformanceProvider),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'عمليات الإدارة',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 12),
                      FilledButton.icon(
                        onPressed: _busy ? null : _evaluateDue,
                        icon: const Icon(Icons.playlist_add_check_rounded),
                        label: const Text('تقييم التقارير المستحقة'),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _busy ? null : () => _export(7),
                              child: const Text('نسخ CSV لـ7 جلسات'),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _busy ? null : () => _export(30),
                              child: const Text('نسخ CSV لـ30 جلسة'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'التقارير المتأخرة أو الناقصة',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 10),
              delayed.when(
                loading: () => const PerformanceLoading(),
                error: (_, __) => PerformanceFailure(
                  message: 'تعذر تحميل قائمة التأخير.',
                  retry: () => ref.invalidate(delayedPerformanceProvider),
                ),
                data: (items) => items.isEmpty
                    ? const Card(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Text(
                            'لا توجد تقارير متأخرة حاليًا.',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : Column(
                        children: items
                            .map(
                              (item) => _DelayedCard(
                                item: item,
                                busy: _busy,
                                retry: () => _retry(item.reportId),
                              ),
                            )
                            .toList(growable: false),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _evaluateDue() async {
    await _run(() async {
      final result = await ref
          .read(performanceRepositoryProvider)
          .evaluateDue(limit: 50);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'تم فحص ${result['scanned_reports'] ?? 0} تقرير؛ '
            '${result['completed_reports'] ?? 0} اكتمل.',
          ),
        ),
      );
    });
  }

  Future<void> _retry(String reportId) async {
    await _run(() async {
      await ref.read(performanceRepositoryProvider).retryReport(reportId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تمت إعادة محاولة التقرير.')),
        );
      }
    });
  }

  Future<void> _export(int window) async {
    await _run(() async {
      final csv = await ref
          .read(performanceRepositoryProvider)
          .exportCsv(window);
      await Clipboard.setData(ClipboardData(text: csv));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تم نسخ CSV لآخر $window جلسة.')),
        );
      }
    });
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      await action();
      ref.invalidate(delayedPerformanceProvider);
      ref.invalidate(performanceSummaryProvider);
      ref.invalidate(performanceReportsProvider);
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(error.message)),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}

class _DelayedCard extends StatelessWidget {
  const _DelayedCard({
    required this.item,
    required this.busy,
    required this.retry,
  });

  final PerformanceDelayedItem item;
  final bool busy;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    final date = DateFormat(
      'd MMMM yyyy',
      'ar',
    ).format(item.targetSessionDate);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              date,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w900,
              ),
            ),
            Text(
              '${item.evaluatedItems}/${item.totalItems} مكتملة • '
              '${item.pendingItems} معلقة • ${item.failedItems} فاشلة',
            ),
            if (item.reasons.isNotEmpty)
              Text('الأسباب: ${item.reasons.join('، ')}'),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: busy ? null : retry,
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('إعادة المحاولة'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => context.push(
                      '/performance/reports/${item.reportId}',
                    ),
                    icon: const Icon(Icons.visibility_outlined),
                    label: const Text('عرض وتصحيح'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

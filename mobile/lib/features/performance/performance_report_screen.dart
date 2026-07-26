import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import '../auth/session_controller.dart';
import 'performance_models.dart';
import 'performance_providers.dart';
import 'performance_repository.dart';
import 'performance_widgets.dart';

class PerformanceReportScreen extends ConsumerWidget {
  const PerformanceReportScreen({required this.reportId, super.key});

  final String reportId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detail = ref.watch(performanceReportDetailProvider(reportId));
    return Scaffold(
      appBar: AppBar(title: const Text('نتائج التقرير')),
      body: SafeArea(
        child: detail.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, __) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              PerformanceFailure(
                message: 'تعذر تحميل نتائج التقرير.',
                retry: () =>
                    ref.invalidate(performanceReportDetailProvider(reportId)),
              ),
            ],
          ),
          data: (value) => _DetailBody(detail: value),
        ),
      ),
    );
  }
}

class _DetailBody extends ConsumerWidget {
  const _DetailBody({required this.detail});

  final PerformanceReportDetail detail;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final date = DateFormat(
      'EEEE d MMMM yyyy',
      'ar',
    ).format(detail.targetSessionDate);
    final isAdmin =
        ref.watch(sessionControllerProvider).profile?.isAdmin == true;
    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(performanceReportDetailProvider(detail.reportId));
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const PerformanceNotice(),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    date,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: detail.session.dataCompletenessPct / 100,
                    minHeight: 9,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${detail.session.dataCompletenessPct.toStringAsFixed(1)}% مكتملة • '
                    '${detail.session.evaluatedItems}/${detail.session.totalItems} نتيجة',
                  ),
                  Text('حالة التقييم: ${detail.evaluationStatus}'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          for (final outcome in detail.outcomes)
            _OutcomeCard(
              outcome: outcome,
              canCorrect: isAdmin,
              onCorrect: () => _showCorrection(context, ref, outcome),
            ),
          if (detail.revisions.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'سجل التصحيحات',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 8),
            for (final revision in detail.revisions)
              Card(
                child: ListTile(
                  leading: CircleAvatar(
                    child: Text('${revision.revisionNumber}'),
                  ),
                  title: Text(revision.reason),
                  subtitle: Text(
                    DateFormat(
                      'd MMM yyyy – HH:mm',
                      'ar',
                    ).format(revision.createdAt.toLocal()),
                  ),
                ),
              ),
          ],
        ],
      ),
    );
  }

  Future<void> _showCorrection(
    BuildContext context,
    WidgetRef ref,
    PerformanceOutcome outcome,
  ) async {
    final result = await showDialog<_CorrectionData>(
      context: context,
      builder: (context) => _CorrectionDialog(outcome: outcome),
    );
    if (result == null || !context.mounted) return;
    try {
      await ref
          .read(performanceRepositoryProvider)
          .correctOutcome(
            outcomeId: outcome.id,
            reason: result.reason,
            sessionOpen: result.open,
            sessionHigh: result.high,
            sessionLow: result.low,
            sessionClose: result.close,
            provider: result.provider,
            dataFingerprint: result.fingerprint,
            dataAsOf: result.dataAsOf,
          );
      ref.invalidate(performanceReportDetailProvider(detail.reportId));
      ref.invalidate(performanceSummaryProvider);
      ref.invalidate(performanceReportsProvider);
      ref.invalidate(delayedPerformanceProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم حفظ التصحيح في سجل تدقيق جديد.')),
        );
      }
    } on ApiException catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    }
  }
}

class _OutcomeCard extends StatelessWidget {
  const _OutcomeCard({
    required this.outcome,
    required this.canCorrect,
    required this.onCorrect,
  });

  final PerformanceOutcome outcome;
  final bool canCorrect;
  final VoidCallback onCorrect;

  @override
  Widget build(BuildContext context) {
    final result = formatBasisPoints(outcome.returnBp);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${outcome.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    outcome.ticker,
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Chip(label: Text(outcome.isComplete ? result : outcome.status)),
              ],
            ),
            const SizedBox(height: 10),
            if (outcome.isComplete) ...[
              Text(
                'سعر التحليل: ${outcome.priceAtAnalysis.toStringAsFixed(2)}',
              ),
              Text(
                'الإغلاق: ${outcome.sessionClose?.toStringAsFixed(2) ?? '-'}',
              ),
              Text('أقصى صعود: ${formatBasisPoints(outcome.maxUpsideBp)}'),
              Text('أقصى هبوط: ${formatBasisPoints(outcome.maxDrawdownBp)}'),
              Text(
                'الاتجاه: ${outcome.directionCorrect == true ? 'تحقق' : 'لم يتحقق'}',
              ),
              Text('الهدف الأول: ${_flag(outcome.targetOneHit)}'),
              Text('الهدف الثاني: ${_flag(outcome.targetTwoHit)}'),
              Text('وقف الخسارة: ${_flag(outcome.stopLossHit)}'),
            ] else
              Text(
                'السبب: ${outcome.evidence['reason'] ?? 'البيانات غير مكتملة'}',
              ),
            if (outcome.correctionCount > 0)
              Text('عدد التصحيحات المدققة: ${outcome.correctionCount}'),
            if (canCorrect) ...[
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: onCorrect,
                icon: const Icon(Icons.edit_note_rounded),
                label: const Text('تصحيح بيانات الجلسة مع سجل تدقيق'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _CorrectionDialog extends StatefulWidget {
  const _CorrectionDialog({required this.outcome});

  final PerformanceOutcome outcome;

  @override
  State<_CorrectionDialog> createState() => _CorrectionDialogState();
}

class _CorrectionDialogState extends State<_CorrectionDialog> {
  late final TextEditingController _reason;
  late final TextEditingController _open;
  late final TextEditingController _high;
  late final TextEditingController _low;
  late final TextEditingController _close;
  late final TextEditingController _provider;
  late final TextEditingController _fingerprint;

  @override
  void initState() {
    super.initState();
    _reason = TextEditingController();
    _open = TextEditingController(text: '${widget.outcome.sessionOpen ?? ''}');
    _high = TextEditingController(text: '${widget.outcome.sessionHigh ?? ''}');
    _low = TextEditingController(text: '${widget.outcome.sessionLow ?? ''}');
    _close = TextEditingController(
      text: '${widget.outcome.sessionClose ?? ''}',
    );
    _provider = TextEditingController(
      text: widget.outcome.provider ?? 'manual',
    );
    _fingerprint = TextEditingController();
  }

  @override
  void dispose() {
    for (final controller in [
      _reason,
      _open,
      _high,
      _low,
      _close,
      _provider,
      _fingerprint,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('تصحيح ${widget.outcome.ticker}'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _field(_reason, 'سبب التصحيح'),
            _number(_open, 'الافتتاح'),
            _number(_high, 'الأعلى'),
            _number(_low, 'الأدنى'),
            _number(_close, 'الإغلاق'),
            _field(_provider, 'المزود'),
            _field(_fingerprint, 'بصمة البيانات'),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        FilledButton(onPressed: _submit, child: const Text('حفظ التصحيح')),
      ],
    );
  }

  Widget _field(TextEditingController controller, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextField(
        controller: controller,
        decoration: InputDecoration(labelText: label),
      ),
    );
  }

  Widget _number(TextEditingController controller, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextField(
        controller: controller,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label),
      ),
    );
  }

  void _submit() {
    final values = [
      double.tryParse(_open.text),
      double.tryParse(_high.text),
      double.tryParse(_low.text),
      double.tryParse(_close.text),
    ];
    if (_reason.text.trim().length < 8 ||
        _fingerprint.text.trim().length < 4 ||
        values.any((value) => value == null || value <= 0)) {
      return;
    }
    Navigator.pop(
      context,
      _CorrectionData(
        reason: _reason.text.trim(),
        open: values[0]!,
        high: values[1]!,
        low: values[2]!,
        close: values[3]!,
        provider: _provider.text.trim(),
        fingerprint: _fingerprint.text.trim(),
        dataAsOf: DateTime.now().toUtc(),
      ),
    );
  }
}

class _CorrectionData {
  const _CorrectionData({
    required this.reason,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.provider,
    required this.fingerprint,
    required this.dataAsOf,
  });

  final String reason;
  final double open;
  final double high;
  final double low;
  final double close;
  final String provider;
  final String fingerprint;
  final DateTime dataAsOf;
}

String _flag(bool? value) {
  if (value == null) return 'غير محدد';
  return value ? 'تحقق' : 'لم يتحقق';
}

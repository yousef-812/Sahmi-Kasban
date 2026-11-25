import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'signals_models.dart';
import 'signals_providers.dart';
import 'signals_screen.dart';

class SignalDetailScreen extends ConsumerWidget {
  const SignalDetailScreen({super.key, required this.signalId});

  final String signalId;

  Future<void> _refresh(WidgetRef ref) async {
    ref.invalidate(signalDetailProvider(signalId));
    try {
      await ref.read(signalDetailProvider(signalId).future);
    } on Object catch (error) {
      debugPrint('signal detail refresh failed: $error');
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailState = ref.watch(signalDetailProvider(signalId));
    return Scaffold(
      appBar: AppBar(title: const Text('تفاصيل الإشارة')),
      body: detailState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => _SignalDetailErrorView(
          error: error,
          onRetry: () => ref.invalidate(signalDetailProvider(signalId)),
        ),
        data: (detail) => RefreshIndicator(
          onRefresh: () => _refresh(ref),
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
            children: [
              _headerCard(context, detail),
              const SizedBox(height: 12),
              _levelsCard(context, detail),
              const SizedBox(height: 12),
              _infoCard(context, detail),
              const SizedBox(height: 12),
              _timelineCard(context, detail),
            ],
          ),
        ),
      ),
    );
  }

  Widget _headerCard(BuildContext context, Signal detail) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Text(
                  detail.ticker,
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(width: 10),
                _DetailChip(
                  label: detail.isLong ? 'شراء' : 'بيع',
                  color: detail.isLong
                      ? Colors.green.shade700
                      : Colors.red.shade700,
                ),
                const SizedBox(width: 8),
                _DetailChip(
                  label: signalStateLabels[detail.state] ?? detail.state,
                  color: signalStateColor(detail.state),
                ),
                const Spacer(),
                Text(
                  _formatSigned(detail.pnlPct, suffix: '%'),
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w900,
                    color: _signedColor(detail.pnlPct),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              detail.isLong
                  ? 'إشارة شراء (Long) — الهدف صعود السعر'
                  : 'إشارة بيع (Short) — الهدف هبوط السعر',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _levelsCard(BuildContext context, Signal detail) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'مستويات التداول',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: _DetailField(
                    label: 'الدخول',
                    value: _formatNumber(detail.entry),
                  ),
                ),
                Expanded(
                  child: _DetailField(
                    label: 'الوقف',
                    value: _formatNumber(detail.stop),
                  ),
                ),
                Expanded(
                  child: _DetailField(
                    label: 'هدف 1',
                    value: _formatNumber(detail.t1),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: _DetailField(
                    label: 'هدف 2',
                    value: _formatNumber(detail.t2),
                  ),
                ),
                Expanded(
                  child: _DetailField(
                    label: 'هدف 3',
                    value: _formatNumber(detail.t3),
                  ),
                ),
                Expanded(
                  child: _DetailField(
                    label: 'وقف متحرك',
                    value: _formatNumber(detail.trailingStop),
                    color: detail.trailingStop == null
                        ? null
                        : Colors.amber.shade800,
                  ),
                ),
              ],
            ),
            if (detail.activationHigh != null) ...[
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _DetailField(
                      label: 'أقصى تفعيل (activation_high)',
                      value: _formatNumber(detail.activationHigh),
                      color: Colors.blue.shade700,
                    ),
                  ),
                  const Expanded(child: SizedBox.shrink()),
                  const Expanded(child: SizedBox.shrink()),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _infoCard(BuildContext context, Signal detail) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'بيانات الإشارة',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: _DetailField(
                    label: 'المصدر',
                    value: detail.source == 'manual' ? 'يدوي' : detail.source,
                  ),
                ),
                Expanded(
                  child: _DetailField(
                    label: 'المالك',
                    value: detail.userId != null ? 'إشارتك' : 'مشتركة',
                  ),
                ),
                Expanded(
                  child: _DetailField(
                    label: 'الربح/الخسارة',
                    value: _formatSigned(detail.pnlPct, suffix: '%'),
                    color: _signedColor(detail.pnlPct),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            _DetailField(
              label: 'تاريخ الفتح',
              value: _formatDateTime(detail.openedAt),
              alignment: AlignmentDirectional.centerStart,
            ),
            const SizedBox(height: 8),
            _DetailField(
              label: 'آخر تحديث',
              value: _formatDateTime(detail.updatedAt),
              alignment: AlignmentDirectional.centerStart,
            ),
            const SizedBox(height: 8),
            _DetailField(
              label: 'تاريخ الإغلاق',
              value: detail.closedAt == null
                  ? '—'
                  : _formatDateTime(detail.closedAt!),
              alignment: AlignmentDirectional.centerStart,
            ),
            if (detail.refReportId != null) ...[
              const SizedBox(height: 8),
              _DetailField(
                label: 'تقرير مرجعي',
                value: detail.refReportId!,
                alignment: AlignmentDirectional.centerStart,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _timelineCard(BuildContext context, Signal detail) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'سجل الأحداث',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 4),
            if (detail.events.isEmpty)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: Text(
                  'لا توجد أحداث مسجلة لهذه الإشارة.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              )
            else
              for (var index = 0; index < detail.events.length; index++)
                _TimelineTile(
                  event: detail.events[index],
                  isLast: index == detail.events.length - 1,
                ),
          ],
        ),
      ),
    );
  }
}

class _TimelineTile extends StatelessWidget {
  const _TimelineTile({required this.event, required this.isLast});

  final SignalEvent event;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: event.event == 'opened'
                    ? Colors.blue.shade700
                    : signalStateColor(event.event),
                shape: BoxShape.circle,
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 46,
                color: theme.colorScheme.outlineVariant,
              ),
          ],
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        _eventLabel(event.event),
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    if (event.price != null)
                      Text(
                        _formatNumber(event.price),
                        textDirection: TextDirection.ltr,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: Colors.blue.shade700,
                        ),
                      ),
                  ],
                ),
                if (event.note != null && event.note!.trim().isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Text(
                      event.note!.trim(),
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                const SizedBox(height: 2),
                Text(
                  _formatDateTime(event.createdAt),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _DetailField extends StatelessWidget {
  const _DetailField({
    required this.label,
    required this.value,
    this.color,
    this.alignment = AlignmentDirectional.center,
  });

  final String label;
  final String value;
  final Color? color;
  final AlignmentGeometry alignment;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 2),
        Align(
          alignment: alignment,
          child: Text(
            value,
            textDirection: TextDirection.ltr,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
        ),
      ],
    );
  }
}

class _DetailChip extends StatelessWidget {
  const _DetailChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

class _SignalDetailErrorView extends StatelessWidget {
  const _SignalDetailErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final notFound =
        error is ApiException && (error as ApiException).statusCode == 404;
    final message = notFound
        ? 'الإشارة غير موجودة أو لم تعد متاحة.'
        : error is ApiException
        ? (error as ApiException).message
        : 'تعذر تحميل تفاصيل الإشارة.';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              notFound ? Icons.search_off_rounded : Icons.cloud_off_rounded,
              size: 48,
            ),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            if (!notFound) ...[
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

String _eventLabel(String event) {
  if (event == 'opened') return 'فتح الإشارة';
  return signalStateLabels[event] ?? event;
}

Color? _signedColor(double? value) {
  if (value == null) return null;
  if (value > 0) return Colors.green.shade700;
  if (value < 0) return Colors.red.shade700;
  return null;
}

String _formatNumber(double? value) {
  if (value == null) return '—';
  return value.toStringAsFixed(2);
}

String _formatSigned(double? value, {String suffix = ''}) {
  if (value == null) return '—';
  final sign = value > 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(2)}$suffix';
}

String _formatDateTime(DateTime value) {
  final local = value.toLocal();
  final day = local.day.toString().padLeft(2, '0');
  final month = local.month.toString().padLeft(2, '0');
  final hour = local.hour.toString().padLeft(2, '0');
  final minute = local.minute.toString().padLeft(2, '0');
  return '$day/$month/${local.year} $hour:$minute';
}

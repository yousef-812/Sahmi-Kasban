import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import 'admin_repository.dart';
import 'historical_replay_models.dart';

class HistoricalReplayScreen extends ConsumerStatefulWidget {
  const HistoricalReplayScreen({super.key});

  @override
  ConsumerState<HistoricalReplayScreen> createState() =>
      _HistoricalReplayScreenState();
}

class _HistoricalReplayScreenState
    extends ConsumerState<HistoricalReplayScreen> {
  static const _downloads = MethodChannel('sahmi_kasban/downloads');
  static const _horizons = <int>[1, 3, 5, 10, 20];

  late DateTime _startDate;
  late DateTime _endDate;
  int _horizonSessions = 5;
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<HistoricalReplayJob> _jobs = const [];
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _selectPreviousMonth(notify: false);
    unawaited(_load());
    _pollTimer = Timer.periodic(
      const Duration(seconds: 8),
      (_) => unawaited(_load(silent: true)),
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load({bool silent = false}) async {
    if (!silent && mounted) setState(() => _loading = true);
    try {
      final jobs = await ref.read(adminRepositoryProvider).historicalReplayJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _error = null;
        _loading = false;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error is ApiException ? error.message : error.toString();
        _loading = false;
      });
    }
  }

  void _selectPreviousMonth({bool notify = true}) {
    final today = DateTime.now();
    final firstCurrentMonth = DateTime(today.year, today.month);
    final previousEnd = firstCurrentMonth.subtract(const Duration(days: 1));
    final previousStart = DateTime(previousEnd.year, previousEnd.month);
    if (notify) {
      setState(() {
        _startDate = previousStart;
        _endDate = previousEnd;
      });
    } else {
      _startDate = previousStart;
      _endDate = previousEnd;
    }
  }

  void _selectCurrentMonth() {
    final today = DateTime.now();
    setState(() {
      _startDate = DateTime(today.year, today.month);
      _endDate = DateTime(today.year, today.month, today.day);
    });
  }

  Future<void> _pickStart() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365 * 5)),
      lastDate: DateTime.now(),
      helpText: 'اختر تاريخ بداية الاختبار',
    );
    if (picked == null) return;
    setState(() {
      _startDate = picked;
      if (_endDate.isBefore(picked)) _endDate = picked;
      if (_endDate.difference(_startDate).inDays > 30) {
        _endDate = _startDate.add(const Duration(days: 30));
      }
    });
  }

  Future<void> _pickEnd() async {
    final latest = _startDate.add(const Duration(days: 30));
    final today = DateTime.now();
    final lastDate = latest.isBefore(today) ? latest : today;
    final picked = await showDatePicker(
      context: context,
      initialDate: _endDate.isAfter(lastDate) ? lastDate : _endDate,
      firstDate: _startDate,
      lastDate: lastDate,
      helpText: 'اختر تاريخ نهاية الاختبار',
    );
    if (picked == null) return;
    setState(() => _endDate = picked);
  }

  Future<void> _start() async {
    final days = _endDate.difference(_startDate).inDays + 1;
    if (days < 1 || days > 31) {
      _showMessage('الحد الأقصى لكل تشغيل هو 31 يومًا.');
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref.read(adminRepositoryProvider).createHistoricalReplay(
            startDate: _startDate,
            endDate: _endDate,
            horizonSessions: _horizonSessions,
          );
      if (!mounted) return;
      _showMessage(
        'بدأ الاختبار على السيرفر. يمكنك الخروج من التطبيق والعودة لاحقًا.',
      );
      await _load(silent: true);
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _download(HistoricalReplayJob job) async {
    try {
      final file = await ref
          .read(adminRepositoryProvider)
          .downloadHistoricalReplay(job.id);
      final location = await _downloads.invokeMethod<String>('saveCsv', {
        'filename': file.filename,
        'bytes': file.bytes,
      });
      if (!mounted) return;
      _showMessage(
        location == null
            ? 'تم تنزيل ملف النتائج.'
            : 'تم تنزيل ملف النتائج في: $location',
      );
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    }
  }

  Future<void> _showDetails(HistoricalReplayJob job) async {
    try {
      final detailed = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJob(job.id);
      if (!mounted) return;
      await showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        builder: (context) => DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.75,
          builder: (context, controller) => ListView(
            controller: controller,
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                'تفاصيل الأسهم',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              for (final ticker in detailed.tickers)
                ListTile(
                  dense: true,
                  leading: Icon(_tickerIcon(ticker.status)),
                  title: Text(ticker.ticker),
                  subtitle: Text(
                    '${_statusLabel(ticker.status)} • '
                    '${ticker.rowsWritten} تقرير • '
                    '${ticker.evaluatedRows} مُقيّم • '
                    '${ticker.pendingRows} منتظر',
                  ),
                  trailing: ticker.failedRows > 0
                      ? Text('${ticker.failedRows} فشل')
                      : null,
                ),
            ],
          ),
        ),
      );
    } on Object catch (error) {
      if (!mounted) return;
      _showMessage(error is ApiException ? error.message : error.toString());
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('d MMMM y', 'ar');
    return Scaffold(
      appBar: AppBar(
        title: const Text('اختبار المحركات التاريخي'),
        actions: [
          IconButton(
            onPressed: () => _load(),
            tooltip: 'تحديث',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
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
                      'تشغيل اختبار جديد',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'المحركات ترى فقط البيانات السابقة لكل يوم. '
                      'السيرفر يعالج 5 أسهم بالتوازي ويحفظ التقدم في قاعدة البيانات.',
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        OutlinedButton(
                          onPressed: _selectPreviousMonth,
                          child: const Text('الشهر السابق'),
                        ),
                        OutlinedButton(
                          onPressed: _selectCurrentMonth,
                          child: const Text('الشهر الحالي'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _DateButton(
                            label: 'من',
                            value: dateFormat.format(_startDate),
                            onPressed: _pickStart,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _DateButton(
                            label: 'إلى',
                            value: dateFormat.format(_endDate),
                            onPressed: _pickEnd,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<int>(
                      initialValue: _horizonSessions,
                      decoration: const InputDecoration(
                        labelText: 'مدة تقييم التوقع بعد التحليل',
                        border: OutlineInputBorder(),
                      ),
                      items: [
                        for (final value in _horizons)
                          DropdownMenuItem(
                            value: value,
                            child: Text('$value جلسات تداول'),
                          ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setState(() => _horizonSessions = value);
                        }
                      },
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'الفترة المختارة: '
                      '${_endDate.difference(_startDate).inDays + 1} يوم '
                      '• الحد الأقصى 31 يومًا',
                    ),
                    const SizedBox(height: 12),
                    FilledButton.icon(
                      onPressed: _submitting ? null : _start,
                      icon: _submitting
                          ? const SizedBox.square(
                              dimension: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.play_arrow_rounded),
                      label: const Text('بدء الاختبار على السيرفر'),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'يمكنك الخروج من التطبيق. عند العودة ستجد نسبة التقدم '
                      'وزر التنزيل مربوطين بحساب الأدمن.',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text('اختبارات حسابي', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            if (_loading) const Center(child: CircularProgressIndicator()),
            if (_error != null)
              Card(
                child: ListTile(
                  leading: const Icon(Icons.error_outline),
                  title: const Text('تعذر تحميل الاختبارات'),
                  subtitle: Text(_error!),
                ),
              ),
            if (!_loading && _jobs.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('لم تبدأ أي اختبارات بعد.')),
                ),
              ),
            for (final job in _jobs) _JobCard(
              job: job,
              dateFormat: dateFormat,
              onDownload: job.downloadReady ? () => _download(job) : null,
              onDetails: () => _showDetails(job),
            ),
          ],
        ),
      ),
    );
  }
}

class _DateButton extends StatelessWidget {
  const _DateButton({
    required this.label,
    required this.value,
    required this.onPressed,
  });

  final String label;
  final String value;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      ),
      child: Column(
        children: [
          Text(label),
          const SizedBox(height: 4),
          Text(value, textAlign: TextAlign.center),
        ],
      ),
    );
  }
}

class _JobCard extends StatelessWidget {
  const _JobCard({
    required this.job,
    required this.dateFormat,
    required this.onDetails,
    this.onDownload,
  });

  final HistoricalReplayJob job;
  final DateFormat dateFormat;
  final VoidCallback onDetails;
  final VoidCallback? onDownload;

  @override
  Widget build(BuildContext context) {
    final progress = job.totalTickers == 0 ? null : job.progressPct / 100;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(_jobIcon(job.status)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${dateFormat.format(job.startDate)} — '
                    '${dateFormat.format(job.endDate)}',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(label: Text(_statusLabel(job.status))),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(value: progress),
            const SizedBox(height: 6),
            Text(
              '${job.progressPct.toStringAsFixed(1)}% • '
              '${job.processedTickers}/${job.totalTickers} سهم • '
              '${job.parallelism} أسهم بالتوازي',
            ),
            const SizedBox(height: 4),
            Text(
              '${job.totalRows} تقرير يومي • '
              '${job.evaluatedRows} مُقيّم • '
              '${job.pendingRows} منتظر النتيجة • '
              '${job.failedTickers} سهم متعطل',
            ),
            Text(
              'المحرك ${job.engineVersion} • التقييم بعد '
              '${job.horizonSessions} جلسات',
            ),
            if (job.errorMessage != null) ...[
              const SizedBox(height: 6),
              Text(job.errorMessage!),
            ],
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: onDetails,
                  icon: const Icon(Icons.list_alt_outlined),
                  label: const Text('تفاصيل الأسهم'),
                ),
                if (onDownload != null)
                  FilledButton.icon(
                    onPressed: onDownload,
                    icon: const Icon(Icons.download_outlined),
                    label: const Text('تنزيل CSV'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

String _statusLabel(String value) => switch (value) {
  'pending' => 'في الانتظار',
  'running' => 'جاري التشغيل',
  'complete' => 'مكتمل',
  'partial' => 'مكتمل جزئيًا',
  'failed' => 'فشل',
  _ => value,
};

IconData _jobIcon(String status) => switch (status) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' => Icons.error_outline,
  'running' => Icons.sync,
  _ => Icons.schedule,
};

IconData _tickerIcon(String status) => switch (status) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' => Icons.error_outline,
  'running' => Icons.sync,
  _ => Icons.schedule,
};

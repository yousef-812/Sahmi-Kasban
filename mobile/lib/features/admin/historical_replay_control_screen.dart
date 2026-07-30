import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import 'admin_repository.dart';
import 'historical_replay_models.dart';

class HistoricalReplayControlScreen extends ConsumerStatefulWidget {
  const HistoricalReplayControlScreen({super.key});

  @override
  ConsumerState<HistoricalReplayControlScreen> createState() =>
      _HistoricalReplayControlScreenState();
}

class _HistoricalReplayControlScreenState
    extends ConsumerState<HistoricalReplayControlScreen> {
  static const _downloads = MethodChannel('sahmi_kasban/downloads');
  static const _horizons = <int>[1, 3, 5, 10, 20];

  late DateTime _startDate;
  late DateTime _endDate;
  int _horizonSessions = 5;
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<HistoricalReplayJob> _jobs = const [];
  List<HistoricalReplayWindow> _batchWindows = const [];
  final Set<String> _busyJobs = <String>{};
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _previousMonth(notify: false);
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
      final jobs = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _loading = false;
        _error = null;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = _errorText(error);
      });
    }
  }

  void _previousMonth({bool notify = true}) {
    final firstCurrent = DateTime(DateTime.now().year, DateTime.now().month);
    final end = firstCurrent.subtract(const Duration(days: 1));
    final start = DateTime(end.year, end.month);
    if (notify) {
      setState(() {
        _startDate = start;
        _endDate = end;
      });
    } else {
      _startDate = start;
      _endDate = end;
    }
  }

  void _currentMonth() {
    final now = DateTime.now();
    setState(() {
      _startDate = DateTime(now.year, now.month);
      _endDate = DateTime(now.year, now.month, now.day);
    });
  }

  Future<void> _pickDate({required bool start}) async {
    final today = DateTime.now();
    final latestEnd = _startDate.add(const Duration(days: 30));
    final picked = await showDatePicker(
      context: context,
      initialDate: start
          ? _startDate
          : (_endDate.isAfter(latestEnd) ? latestEnd : _endDate),
      firstDate: start
          ? today.subtract(const Duration(days: 365 * 5))
          : _startDate,
      lastDate: start ? today : (latestEnd.isBefore(today) ? latestEnd : today),
      helpText: start ? 'اختر تاريخ البداية' : 'اختر تاريخ النهاية',
    );
    if (picked == null) return;
    setState(() {
      if (start) {
        _startDate = picked;
        if (_endDate.isBefore(picked)) _endDate = picked;
        if (_endDate.difference(picked).inDays > 30) {
          _endDate = picked.add(const Duration(days: 30));
        }
      } else {
        _endDate = picked;
      }
    });
  }

  bool _validateWindow() {
    final days = _endDate.difference(_startDate).inDays + 1;
    if (days < 1 || days > 31) {
      _message('الحد الأقصى لكل فترة هو 31 يومًا.');
      return false;
    }
    return true;
  }

  Future<void> _startSingle() async {
    if (!_validateWindow()) return;
    await _submit(() async {
      await ref
          .read(adminRepositoryProvider)
          .createHistoricalReplay(
            startDate: _startDate,
            endDate: _endDate,
            horizonSessions: _horizonSessions,
          );
      _message('بدأ الاختبار على Worker منفصل عن مستخدمي التطبيق.');
    });
  }

  void _addWindow() {
    if (!_validateWindow()) return;
    final duplicate = _batchWindows.any(
      (window) =>
          _sameDay(window.startDate, _startDate) &&
          _sameDay(window.endDate, _endDate),
    );
    if (duplicate) {
      _message('الفترة موجودة بالفعل داخل الدفعة.');
      return;
    }
    setState(() {
      _batchWindows = [
        ..._batchWindows,
        HistoricalReplayWindow(startDate: _startDate, endDate: _endDate),
      ];
    });
  }

  Future<void> _startBatch() async {
    if (_batchWindows.length < 2) {
      _message('أضف فترتين على الأقل لتشغيل دفعة.');
      return;
    }
    await _submit(() async {
      final jobs = await ref
          .read(adminRepositoryProvider)
          .createHistoricalReplayBatch(
            windows: _batchWindows,
            horizonSessions: _horizonSessions,
          );
      if (mounted) setState(() => _batchWindows = const []);
      _message(
        'تمت إضافة ${jobs.length} فترات. ستعمل بالترتيب وتشارك Cache البيانات.',
      );
    });
  }

  Future<void> _submit(Future<void> Function() operation) async {
    setState(() => _submitting = true);
    try {
      await operation();
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _control(HistoricalReplayJob job, String action) async {
    if (_busyJobs.contains(job.id)) return;
    if (action == 'cancel') {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('إلغاء الاختبار؟'),
          content: const Text(
            'سيتم الاحتفاظ بالنتائج المكتملة وإيقاف الأسهم المتبقية.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('رجوع'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('إلغاء الاختبار'),
            ),
          ],
        ),
      );
      if (confirmed != true) return;
    }

    setState(() => _busyJobs.add(job.id));
    try {
      final repository = ref.read(adminRepositoryProvider);
      switch (action) {
        case 'pause':
          await repository.pauseHistoricalReplay(job.id);
        case 'resume':
          await repository.resumeHistoricalReplay(job.id);
        case 'cancel':
          await repository.cancelHistoricalReplay(job.id);
      }
      if (mounted) {
        _message(switch (action) {
          'pause' => 'تم طلب الإيقاف بعد الدفعة الحالية.',
          'resume' => 'تم استكمال الاختبار.',
          _ => 'تم إلغاء الاختبار.',
        });
      }
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    } finally {
      if (mounted) setState(() => _busyJobs.remove(job.id));
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
      if (mounted) {
        _message(
          location == null ? 'تم تنزيل النتائج.' : 'تم التنزيل في: $location',
        );
      }
    } on Object catch (error) {
      if (mounted) _message(_errorText(error));
    }
  }

  Future<void> _details(HistoricalReplayJob job) async {
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
              if (detailed.tickers.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('لم تبدأ معالجة الأسهم بعد.')),
                ),
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
      if (mounted) _message(_errorText(error));
    }
  }

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(text)));
  }

  String _errorText(Object error) {
    return error is ApiException ? error.message : error.toString();
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('d MMMM y', 'ar');
    return Scaffold(
      appBar: AppBar(
        title: const Text('اختبار المحركات التاريخي'),
        actions: [
          IconButton(
            onPressed: _load,
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
            _ReplaySetupCard(
              dateFormat: dateFormat,
              startDate: _startDate,
              endDate: _endDate,
              horizonSessions: _horizonSessions,
              horizons: _horizons,
              submitting: _submitting,
              windows: _batchWindows,
              onPreviousMonth: _previousMonth,
              onCurrentMonth: _currentMonth,
              onPickStart: () => _pickDate(start: true),
              onPickEnd: () => _pickDate(start: false),
              onHorizonChanged: (value) =>
                  setState(() => _horizonSessions = value),
              onStartSingle: _startSingle,
              onAddWindow: _addWindow,
              onRemoveWindow: (index) => setState(() {
                _batchWindows = [
                  for (var i = 0; i < _batchWindows.length; i++)
                    if (i != index) _batchWindows[i],
                ];
              }),
              onStartBatch: _startBatch,
            ),
            const SizedBox(height: 16),
            Text(
              'اختبارات حسابي',
              style: Theme.of(context).textTheme.titleLarge,
            ),
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
            for (final job in _jobs)
              _ReplayJobCard(
                job: job,
                dateFormat: dateFormat,
                busy: _busyJobs.contains(job.id),
                onDetails: () => _details(job),
                onDownload: job.downloadReady ? () => _download(job) : null,
                onPause: job.canPause ? () => _control(job, 'pause') : null,
                onResume: job.canResume ? () => _control(job, 'resume') : null,
                onCancel: job.canCancel ? () => _control(job, 'cancel') : null,
              ),
          ],
        ),
      ),
    );
  }
}

class _ReplaySetupCard extends StatelessWidget {
  const _ReplaySetupCard({
    required this.dateFormat,
    required this.startDate,
    required this.endDate,
    required this.horizonSessions,
    required this.horizons,
    required this.submitting,
    required this.windows,
    required this.onPreviousMonth,
    required this.onCurrentMonth,
    required this.onPickStart,
    required this.onPickEnd,
    required this.onHorizonChanged,
    required this.onStartSingle,
    required this.onAddWindow,
    required this.onRemoveWindow,
    required this.onStartBatch,
  });

  final DateFormat dateFormat;
  final DateTime startDate;
  final DateTime endDate;
  final int horizonSessions;
  final List<int> horizons;
  final bool submitting;
  final List<HistoricalReplayWindow> windows;
  final VoidCallback onPreviousMonth;
  final VoidCallback onCurrentMonth;
  final VoidCallback onPickStart;
  final VoidCallback onPickEnd;
  final ValueChanged<int> onHorizonChanged;
  final VoidCallback onStartSingle;
  final VoidCallback onAddWindow;
  final ValueChanged<int> onRemoveWindow;
  final VoidCallback onStartBatch;

  @override
  Widget build(BuildContext context) {
    return Card(
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
              'الاختبارات تعمل على Worker منفصل، لذلك لا تبطئ مستخدمي التطبيق. '
              'يمكن تشغيل فترة واحدة أو إضافة عدة فترات إلى دفعة متسلسلة.',
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              children: [
                OutlinedButton(
                  onPressed: onPreviousMonth,
                  child: const Text('الشهر السابق'),
                ),
                OutlinedButton(
                  onPressed: onCurrentMonth,
                  child: const Text('الشهر الحالي'),
                ),
              ],
            ),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: onPickStart,
                    child: Text('من\n${dateFormat.format(startDate)}'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: onPickEnd,
                    child: Text('إلى\n${dateFormat.format(endDate)}'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<int>(
              initialValue: horizonSessions,
              decoration: const InputDecoration(
                labelText: 'التقييم بعد عدد جلسات',
                border: OutlineInputBorder(),
              ),
              items: [
                for (final value in horizons)
                  DropdownMenuItem(value: value, child: Text('$value جلسات')),
              ],
              onChanged: submitting
                  ? null
                  : (value) {
                      if (value != null) onHorizonChanged(value);
                    },
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton.icon(
                  onPressed: submitting ? null : onStartSingle,
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('تشغيل الفترة'),
                ),
                OutlinedButton.icon(
                  onPressed: submitting ? null : onAddWindow,
                  icon: const Icon(Icons.playlist_add),
                  label: const Text('إضافة للدفعة'),
                ),
              ],
            ),
            if (windows.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('دفعة الفترات (${windows.length})'),
              for (final indexed in windows.indexed)
                ListTile(
                  dense: true,
                  leading: CircleAvatar(child: Text('${indexed.$1 + 1}')),
                  title: Text(
                    '${dateFormat.format(indexed.$2.startDate)} — '
                    '${dateFormat.format(indexed.$2.endDate)}',
                  ),
                  trailing: IconButton(
                    onPressed: submitting
                        ? null
                        : () => onRemoveWindow(indexed.$1),
                    icon: const Icon(Icons.close),
                  ),
                ),
              FilledButton.tonalIcon(
                onPressed: submitting || windows.length < 2
                    ? null
                    : onStartBatch,
                icon: const Icon(Icons.queue_play_next),
                label: Text('تشغيل ${windows.length} فترات بالترتيب'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ReplayJobCard extends StatelessWidget {
  const _ReplayJobCard({
    required this.job,
    required this.dateFormat,
    required this.busy,
    required this.onDetails,
    this.onDownload,
    this.onPause,
    this.onResume,
    this.onCancel,
  });

  final HistoricalReplayJob job;
  final DateFormat dateFormat;
  final bool busy;
  final VoidCallback onDetails;
  final VoidCallback? onDownload;
  final VoidCallback? onPause;
  final VoidCallback? onResume;
  final VoidCallback? onCancel;

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
                Icon(_jobIcon(job.controlState)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${dateFormat.format(job.startDate)} — '
                    '${dateFormat.format(job.endDate)}',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(label: Text(_statusLabel(job.controlState))),
              ],
            ),
            LinearProgressIndicator(value: progress),
            const SizedBox(height: 6),
            Text(
              '${job.progressPct.toStringAsFixed(1)}% • '
              '${job.processedTickers}/${job.totalTickers} سهم',
            ),
            if (job.estimatedSecondsRemaining != null && job.isActive)
              Text(
                'المتبقي تقريبًا ${_durationLabel(job.estimatedSecondsRemaining!)}'
                '${job.throughputTickersPerMinute == null ? '' : ' • ${job.throughputTickersPerMinute!.toStringAsFixed(1)} سهم/دقيقة'}',
              ),
            Text(
              '${job.totalRows} تقرير • ${job.evaluatedRows} مُقيّم • '
              '${job.pendingRows} منتظر • ${job.failedTickers} متعطل',
            ),
            if (job.workerIsolated)
              const Text('Worker منفصل: لا يستهلك موارد واجهة المستخدمين.'),
            if (job.errorMessage != null) Text(job.errorMessage!),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: busy ? null : onDetails,
                  icon: const Icon(Icons.list_alt_outlined),
                  label: const Text('التفاصيل'),
                ),
                if (onPause != null)
                  OutlinedButton.icon(
                    onPressed: busy ? null : onPause,
                    icon: const Icon(Icons.pause),
                    label: const Text('إيقاف مؤقت'),
                  ),
                if (onResume != null)
                  FilledButton.tonalIcon(
                    onPressed: busy ? null : onResume,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('استكمال'),
                  ),
                if (onCancel != null)
                  TextButton.icon(
                    onPressed: busy ? null : onCancel,
                    icon: const Icon(Icons.cancel_outlined),
                    label: const Text('إلغاء'),
                  ),
                if (onDownload != null)
                  FilledButton.icon(
                    onPressed: busy ? null : onDownload,
                    icon: const Icon(Icons.download_outlined),
                    label: const Text('تنزيل CSV'),
                  ),
                if (busy)
                  const SizedBox.square(
                    dimension: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
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
  'paused' => 'متوقف مؤقتًا',
  'cancelled' => 'ملغي',
  'complete' => 'مكتمل',
  'partial' => 'مكتمل جزئيًا',
  'failed' => 'فشل',
  _ => value,
};

IconData _jobIcon(String value) => switch (value) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' || 'cancelled' => Icons.error_outline,
  'running' => Icons.sync,
  'paused' => Icons.pause_circle_outline,
  _ => Icons.schedule,
};

IconData _tickerIcon(String value) => switch (value) {
  'complete' => Icons.check_circle_outline,
  'partial' => Icons.warning_amber_rounded,
  'failed' => Icons.error_outline,
  'running' => Icons.sync,
  _ => Icons.schedule,
};

bool _sameDay(DateTime first, DateTime second) {
  return first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;
}

String _durationLabel(int seconds) {
  final duration = Duration(seconds: seconds.clamp(0, 86400 * 30).toInt());
  if (duration.inHours >= 1) {
    final minutes = duration.inMinutes.remainder(60);
    return minutes == 0
        ? '${duration.inHours} ساعة'
        : '${duration.inHours} ساعة و$minutes دقيقة';
  }
  if (duration.inMinutes >= 1) return '${duration.inMinutes} دقيقة';
  return 'أقل من دقيقة';
}

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;

import '../../core/network/api_exception.dart';
import 'labs_models.dart';
import 'labs_providers.dart';
import 'labs_repository.dart';

class LabsScreen extends ConsumerStatefulWidget {
  const LabsScreen({super.key, this.embedded = false});

  final bool embedded;

  @override
  ConsumerState<LabsScreen> createState() => _LabsScreenState();
}

class _LabsScreenState extends ConsumerState<LabsScreen> {
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 21));
  DateTime _endDate = DateTime.now();
  int? _rank;
  String _exitMode = 'target_2';
  bool _submitting = false;
  String? _activeJobId;
  String? _error;
  List<LabsBacktestJob> _jobs = const [];
  bool _loadingJobs = true;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    unawaited(_load());
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final jobs = await ref
          .read(labsRepositoryProvider)
          .backtestJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _loadingJobs = false;
        _error = null;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loadingJobs = false;
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  Future<void> _pickStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365 * 3)),
      lastDate: _endDate,
      helpText: 'اختر بداية النطاق',
    );
    if (picked != null) {
      setState(() => _startDate = picked);
    }
  }

  Future<void> _pickEndDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _endDate,
      firstDate: _startDate,
      lastDate: DateTime.now(),
      helpText: 'اختر نهاية النطاق',
    );
    if (picked != null) {
      setState(() => _endDate = picked);
    }
  }

  Future<void> _run() async {
    final query = LabsBacktestQuery(
      startDate: _startDate,
      endDate: _endDate,
      rank: _rank,
      exitMode: _exitMode,
    );
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      final job = await ref
          .read(labsRepositoryProvider)
          .createBacktestJob(query);
      if (!mounted) return;
      setState(() {
        _activeJobId = job.id;
        _submitting = false;
      });
      _startPolling();
      await _load();
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  void _startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(
      const Duration(seconds: 6),
      (_) => unawaited(_poll()),
    );
  }

  Future<void> _poll() async {
    final jobId = _activeJobId;
    if (jobId == null) return;
    try {
      final job = await ref.read(labsRepositoryProvider).backtestJob(jobId);
      if (!mounted) return;
      if (job.status == 'complete' || job.status == 'failed') {
        _pollTimer?.cancel();
        setState(() => _activeJobId = null);
      }
      await _load();
    } on Object {
      // Transient polling failures are retried on the next tick.
    }
  }

  Future<void> _openJob(LabsBacktestJob job) async {
    setState(() {
      _activeJobId = job.id;
      _startDate = job.startDate;
      _endDate = job.endDate;
      _rank = job.rank;
      _exitMode = job.exitMode;
    });
    if (job.isActive) {
      _startPolling();
    }
    await _load();
  }

  Future<void> _deleteJob(LabsBacktestJob job) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف المحاكاة'),
        content: const Text(
          'سيتم حذف هذه المحاكاة نهائيًا من قاعدة البيانات. لا يمكن التراجع عن هذا الإجراء.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('حذف نهائي'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }
    try {
      await ref.read(labsRepositoryProvider).deleteBacktestJob(job.id);
      if (!mounted) {
        return;
      }
      if (_activeJobId == job.id) {
        _pollTimer?.cancel();
        setState(() => _activeJobId = null);
      }
      await _load();
    } on Object catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  String _formatDate(DateTime value) {
    try {
      return DateFormat('d MMMM yyyy', 'ar').format(value.toLocal());
    } on Object {
      return '${value.day}/${value.month}/${value.year}';
    }
  }

  Widget _body() {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const _LabsNotice(),
          const SizedBox(height: 14),
          _buildControls(context),
          const SizedBox(height: 16),
          if (_error != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: const Text('تعذر تشغيل المحاكاة'),
                subtitle: Text(_error!),
              ),
            ),
          if (_submitting)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(
                  child: Text('جارٍ إرسال المحاكاة إلى Worker الاختبارات...'),
                ),
              ),
            ),
          if (_activeJobId != null)
            _buildActiveJob(context),
          const SizedBox(height: 8),
          Text(
            'محاولاتي',
            style: Theme.of(
              context,
            ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          if (_loadingJobs)
            const Center(child: CircularProgressIndicator()),
          if (!_loadingJobs && _jobs.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('لم تشغّل أي محاكاة بعد.')),
              ),
            ),
          for (final job in _jobs)
            _JobCard(
              job: job,
              dateFormat: DateFormat('d MMM yyyy', 'ar'),
              active: _activeJobId == job.id,
              onOpen: () => _openJob(job),
              onDelete: () => _deleteJob(job),
            ),
        ],
      ),
    );
  }

  Widget _buildActiveJob(BuildContext context) {
    final jobId = _activeJobId!;
    return FutureBuilder<LabsBacktestJob>(
      future: ref.read(labsBacktestJobProvider(jobId).future),
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          final error = snapshot.error;
          return Card(
            child: ListTile(
              leading: const Icon(Icons.error_outline),
              title: const Text('تعذر تحميل نتيجة المحاكاة'),
              subtitle: Text(error is ApiException ? error.message : '$error'),
            ),
          );
        }
        if (snapshot.hasData) {
          final job = snapshot.data!;
          if (job.status == 'complete' && job.summary != null) {
            return _LabsResults(job: job);
          }
          if (job.status == 'failed') {
            return Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    const Icon(Icons.error_outline, size: 32),
                    const SizedBox(height: 10),
                    Text(
                      job.errorMessage ?? 'فشلت المحاكاة.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          }
        }
        return const Card(
          child: Padding(
            padding: EdgeInsets.all(32),
            child: Column(
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 14),
                Text(
                  'المحاكاة تعمل الآن على Worker الاختبارات... سيظهر الملخص هنا تلقائيًا.',
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final body = _body();
    if (widget.embedded) {
      return body;
    }
    return Scaffold(
      appBar: AppBar(title: const Text('المختببرات')),
      body: SafeArea(child: body),
    );
  }

  Widget _buildControls(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'محاكاة تقرير الـ10 اليومي',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submitting ? null : _pickStartDate,
                    icon: const Icon(Icons.event_outlined),
                    label: Text('من: ${_formatDate(_startDate)}'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submitting ? null : _pickEndDate,
                    icon: const Icon(Icons.event_available_outlined),
                    label: Text('إلى: ${_formatDate(_endDate)}'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<int?>(
              initialValue: _rank,
              decoration: const InputDecoration(
                labelText: 'رتبة السهم في التقرير',
                border: OutlineInputBorder(),
              ),
              items: [
                const DropdownMenuItem<int?>(
                  value: null,
                  child: Text('كل الرتب (1-10)'),
                ),
                for (var rank = 1; rank <= 10; rank++)
                  DropdownMenuItem<int?>(value: rank, child: Text('الرتبة $rank')),
              ],
              onChanged: _submitting
                  ? null
                  : (value) => setState(() => _rank = value),
            ),
            const SizedBox(height: 14),
            SegmentedButton<String>(
              showSelectedIcon: false,
              segments: const [
                ButtonSegment(
                  value: 'target_2',
                  label: Text('الهدف الثاني'),
                ),
                ButtonSegment(
                  value: 'highest',
                  label: Text('أعلى هدف'),
                ),
              ],
              selected: <String>{_exitMode},
              onSelectionChanged: _submitting
                  ? null
                  : (selection) {
                      setState(() => _exitMode = selection.single);
                    },
            ),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: _submitting ? null : _run,
              icon: _submitting
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.play_arrow_rounded),
              label: const Text('تشغيل المحاكاة على Worker الاختبارات'),
            ),
            const SizedBox(height: 8),
            const Text(
              'يمكنك الخروج من الصفحة. عند العودة ستجد النتيجة محفوظة في محاولاتك.',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class _LabsNotice extends StatelessWidget {
  const _LabsNotice();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.science_outlined),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                'محاكاة شراء أسهم تقرير الـ10 اليومي عند افتتاح الجلسة وبيعها عند تحقق الهدف المختار، مع تتبع الأسعار كل 10 دقائق خلال الجلسة. النطاق محدود بآخر 45 يومًا. المحاكاة تعمل على Worker الاختبارات المنفصل، فلا تؤثر على مستخدمي التطبيق.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _JobCard extends StatelessWidget {
  const _JobCard({
    required this.job,
    required this.dateFormat,
    required this.active,
    required this.onOpen,
    required this.onDelete,
  });

  final LabsBacktestJob job;
  final DateFormat dateFormat;
  final bool active;
  final VoidCallback onOpen;
  final VoidCallback onDelete;

  static const _statusLabels = <String, String>{
    'queued': 'في الانتظار',
    'running': 'جاري التشغيل',
    'complete': 'مكتمل',
    'failed': 'فشل',
  };

  @override
  Widget build(BuildContext context) {
    final statusLabel =
        _statusLabels[job.status] ?? job.status;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(
          switch (job.status) {
            'complete' => Icons.check_circle_outline,
            'failed' => Icons.error_outline,
            'running' => Icons.sync,
            _ => Icons.schedule,
          },
        ),
        title: Text(
          '${dateFormat.format(job.startDate)} — '
          '${dateFormat.format(job.endDate)}'
          '${job.rank == null ? '' : ' • الرتبة ${job.rank}'}',
        ),
        subtitle: Text(
          active
              ? 'جاري عرض النتيجة...'
              : '$statusLabel • '
                  '${job.exitMode == 'highest' ? 'أعلى هدف' : 'الهدف الثاني'}',
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              tooltip: 'حذف نهائي',
              visualDensity: VisualDensity.compact,
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline_rounded),
              color: Theme.of(context).colorScheme.error,
            ),
            const Icon(Icons.chevron_left_rounded),
          ],
        ),
        onTap: onOpen,
      ),
    );
  }
}

class _LabsResults extends StatelessWidget {
  const _LabsResults({required this.job});

  final LabsBacktestJob job;

  @override
  Widget build(BuildContext context) {
    final summary = job.summary!;
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
                  'ملخص المحاكاة',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 14),
                _SummaryRow(
                  label: 'نسبة تحقق الهدف',
                  value: '${summary.hitRatePct.toStringAsFixed(1)}%',
                  highlighted: true,
                ),
                const Divider(height: 20),
                _SummaryRow(
                  label: 'متوسط العائد عند النجاح',
                  value: _formatPercent(summary.avgHitReturnPct),
                ),
                _SummaryRow(
                  label: 'متوسط العائد عند الإخفاق',
                  value: _formatPercent(summary.avgMissReturnPct),
                ),
                _SummaryRow(
                  label: 'متوسط العائد الإجمالي',
                  value: _formatPercent(summary.avgReturnPct),
                ),
                _SummaryRow(
                  label: 'الوسيط الزمني لتحقيق الهدف',
                  value: summary.medianMinutesToHit == null
                      ? '-'
                      : '${summary.medianMinutesToHit!.round()} دقيقة',
                ),
                const Divider(height: 20),
                _SummaryRow(
                  label: 'الصفقات المكتملة',
                  value:
                      '${summary.trades} (نجاح ${summary.hits} / إخفاق ${summary.misses})',
                ),
                _SummaryRow(
                  label: 'جلسات تم فحصها',
                  value: '${summary.reportsScanned}',
                ),
                if (summary.skipped > 0)
                  _SummaryRow(
                    label: 'بدون بيانات',
                    value: '${summary.skipped}',
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'تفاصيل الصفقات',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 10),
        if (job.sessions.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Text('لا توجد صفقات ضمن هذا النطاق.', textAlign: TextAlign.center),
            ),
          )
        else
          Column(
            children: job.sessions
                .map((trade) => _TradeCard(trade: trade))
                .toList(growable: false),
          ),
      ],
    );
  }

  String _formatPercent(double? value) {
    if (value == null) return '-';
    final prefix = value > 0 ? '+' : '';
    return '$prefix${value.toStringAsFixed(2)}%';
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({
    required this.label,
    required this.value,
    this.highlighted = false,
  });

  final String label;
  final String value;
  final bool highlighted;

  @override
  Widget build(BuildContext context) {
    final style = highlighted
        ? Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w900,
            color: Theme.of(context).colorScheme.primary,
          )
        : Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w800,
          );
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Text(value, textDirection: TextDirection.ltr, style: style),
        ],
      ),
    );
  }
}

class _TradeCard extends StatelessWidget {
  const _TradeCard({required this.trade});

  final LabsBacktestSession trade;

  static const _exitLabels = <String, String>{
    'target': 'تحقق الهدف',
    'stop': 'وقف الخسارة',
    'close': 'إغلاق الجلسة',
    'skipped': 'بدون بيانات',
  };

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final returnColor = (trade.returnPct ?? 0) >= 0
        ? Colors.green.shade700
        : Colors.red.shade700;
    final isHit = trade.hit;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ExpansionTile(
        shape: const Border(),
        collapsedShape: const Border(),
        leading: CircleAvatar(
          backgroundColor: isHit
              ? colorScheme.primaryContainer
              : colorScheme.surfaceContainerHighest,
          child: Icon(
            isHit ? Icons.check_rounded : Icons.close_rounded,
            color: isHit ? colorScheme.primary : colorScheme.outline,
          ),
        ),
        title: Row(
          children: [
            Text(
              trade.ticker,
              textDirection: TextDirection.ltr,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(width: 8),
            Chip(
              visualDensity: VisualDensity.compact,
              label: Text('الرتبة ${trade.rank}'),
            ),
          ],
        ),
        subtitle: Text(
          'جلسة ${_formatDate(trade.targetSessionDate)} • '
          '${_exitLabels[trade.exitReason] ?? trade.exitReason}'
          '${trade.minutesToExit != null ? ' • بعد ${trade.minutesToExit} دقيقة' : ''}',
        ),
        trailing: Text(
          trade.returnPct == null
              ? '-'
              : '${(trade.returnPct! > 0 ? '+' : '')}${trade.returnPct!.toStringAsFixed(2)}%',
          textDirection: TextDirection.ltr,
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w900,
                color: returnColor,
              ),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _TradeDetailRow(
                  label: 'فتح الجلسة',
                  value: _formatPrice(trade.sessionOpen),
                ),
                _TradeDetailRow(
                  label: 'سعر الخروج',
                  value: _formatPrice(trade.exitPrice),
                ),
                if (trade.priceAtAnalysis != null)
                  _TradeDetailRow(
                    label: 'سعر التحليل',
                    value: _formatPrice(trade.priceAtAnalysis),
                  ),
                _TradeDetailRow(
                  label: 'الأهداف',
                  value: trade.targets.map(_formatPrice).join(' / '),
                ),
                if (trade.stopLoss != null)
                  _TradeDetailRow(
                    label: 'وقف الخسارة',
                    value: _formatPrice(trade.stopLoss),
                  ),
                const SizedBox(height: 8),
                Text(
                  'التتبع كل 10 دقائق',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 6),
                SizedBox(
                  height: 200,
                  child: trade.tracked.isEmpty
                      ? const Center(child: Text('لا توجد نقاط تتبع.'))
                      : _TrackedChart(points: trade.tracked),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime value) {
    try {
      return DateFormat('d MMM yyyy', 'ar').format(value.toLocal());
    } on Object {
      return '${value.day}/${value.month}/${value.year}';
    }
  }

  String _formatPrice(double? value) {
    return value == null ? '-' : value.toStringAsFixed(3);
  }
}

class _TradeDetailRow extends StatelessWidget {
  const _TradeDetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class _TrackedChart extends StatelessWidget {
  const _TrackedChart({required this.points});

  final List<LabsTrackedPoint> points;

  @override
  Widget build(BuildContext context) {
    final prices = points.map((point) => point.price).toList(growable: false);
    final minPrice = prices.reduce((a, b) => a < b ? a : b);
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);
    final range = (maxPrice - minPrice).abs() < 0.0001
        ? 1.0
        : (maxPrice - minPrice);

    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final height = constraints.maxHeight;
        final step = width / (points.length - 1).clamp(1, points.length);
        final line = <Offset>[];
        for (var index = 0; index < points.length; index++) {
          final dx = index * step;
          final dy = height -
              ((points[index].price - minPrice) / range) * (height - 20) -
              10;
          line.add(Offset(dx, dy.toDouble()));
        }
        return CustomPaint(
          size: Size(width, height),
          painter: _TrackedPainter(
            line: line,
            maxPrice: maxPrice,
            minPrice: minPrice,
            firstTime: points.first.time,
            lastTime: points.last.time,
            color: Theme.of(context).colorScheme.primary,
          ),
        );
      },
    );
  }
}

class _TrackedPainter extends CustomPainter {
  const _TrackedPainter({
    required this.line,
    required this.maxPrice,
    required this.minPrice,
    required this.firstTime,
    required this.lastTime,
    required this.color,
  });

  final List<Offset> line;
  final double maxPrice;
  final double minPrice;
  final String firstTime;
  final String lastTime;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = color.withValues(alpha: 0.12)
      ..strokeWidth = 1;
    for (var index = 1; index < 4; index++) {
      final dy = size.height * index / 4;
      canvas.drawLine(Offset(0, dy), Offset(size.width, dy), gridPaint);
    }
    final linePaint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    if (line.length >= 2) {
      final path = Path()..moveTo(line.first.dx, line.first.dy);
      for (final point in line.skip(1)) {
        path.lineTo(point.dx, point.dy);
      }
      canvas.drawPath(path, linePaint);
    } else if (line.isNotEmpty) {
      canvas.drawCircle(line.first, 3, Paint()..color = color);
    }
    final labelPaint = Paint()..color = color.withValues(alpha: 0.75);
    final textStyle = TextStyle(color: labelPaint.color, fontSize: 10);
    _drawText(canvas, '$minPrice', const Offset(4, 2), textStyle);
    _drawText(canvas, '$maxPrice', Offset(4, size.height - 16), textStyle);
    _drawText(
      canvas,
      firstTime,
      Offset(size.width - 30, 2),
      textStyle,
    );
  }

  void _drawText(Canvas canvas, String text, Offset offset, TextStyle style) {
    final textPainter = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(_TrackedPainter oldDelegate) {
    return oldDelegate.line != line || oldDelegate.color != color;
  }
}

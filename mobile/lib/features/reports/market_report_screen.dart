import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'report_providers.dart';

class MarketReportScreen extends ConsumerStatefulWidget {
  const MarketReportScreen({required this.reportId, this.preview, super.key});

  final String reportId;
  final MarketReportPreview? preview;

  @override
  ConsumerState<MarketReportScreen> createState() => _MarketReportScreenState();
}

class _MarketReportScreenState extends ConsumerState<MarketReportScreen> {
  MarketReport? _report;
  bool _loading = false;
  bool _locked = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _locked = widget.preview?.unlocked == false;
    if (!_locked) {
      _loadReport();
    }
  }

  Future<void> _loadReport() async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final report = await ref
          .read(backendRepositoryProvider)
          .getMarketReport(widget.reportId);
      if (mounted) {
        setState(() {
          _report = report;
          _locked = false;
        });
      }
    } on ApiException catch (error) {
      if (mounted) {
        setState(() {
          _locked = error.statusCode == 402;
          _error = error.statusCode == 402 ? null : error.message;
        });
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _unlock() async {
    if (_loading) return;
    final cost = widget.preview?.unlockCostCoins ?? '1';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('فتح تقرير أفضل 10'),
        content: Text(
          'سيتم خصم $cost عملة مرة واحدة فقط. بعد الفتح سيظل التقرير محفوظًا لهذا الحساب.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('فتح التقرير'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final execution = await ref
          .read(backendRepositoryProvider)
          .unlockMarketReport(widget.reportId);
      await ref.read(sessionControllerProvider.notifier).refreshProfile();
      ref.invalidate(walletSummaryProvider);
      ref.invalidate(latestReportPreviewProvider);
      if (!mounted) return;
      setState(() {
        _report = execution.report;
        _locked = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            execution.chargedPoints == 0
                ? 'التقرير كان مفتوحًا بالفعل.'
                : 'تم فتح التقرير وخصم ${execution.chargedCoins} عملة.',
          ),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('تقرير أفضل 10')),
      body: SafeArea(child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading && _report == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_locked) {
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  const Icon(Icons.lock_outline_rounded, size: 52),
                  const SizedBox(height: 16),
                  Text(
                    'أسماء الأسهم وخطط التداول تظهر بعد فتح التقرير.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'التكلفة: ${widget.preview?.unlockCostCoins ?? '1'} عملة',
                  ),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: _loading ? null : _unlock,
                    icon: const Icon(Icons.lock_open_rounded),
                    label: const Text('فتح التقرير'),
                  ),
                ],
              ),
            ),
          ),
          if (_error != null) _ErrorCard(message: _error!, retry: _unlock),
        ],
      );
    }

    final report = _report;
    if (report == null) {
      return ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _ErrorCard(
            message: _error ?? 'تعذر تحميل التقرير.',
            retry: _loadReport,
          ),
        ],
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _ReportHeader(report: report),
        const SizedBox(height: 12),
        _MarketSummaryCard(summary: report.marketSummary),
        const SizedBox(height: 12),
        for (final item in report.items) _ReportItemCard(item: item),
      ],
    );
  }
}

class _ReportHeader extends StatelessWidget {
  const _ReportHeader({required this.report});

  final MarketReport report;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('الجلسة المستهدفة'),
            const SizedBox(height: 4),
            Text(
              _arabicDate(report.targetSessionDate),
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 8),
            const Text('الترتيب ناتج عن التحليل الآلي ولا يمثل ضمانًا للربح.'),
          ],
        ),
      ),
    );
  }
}

class _MarketSummaryCard extends StatelessWidget {
  const _MarketSummaryCard({required this.summary});

  final Map<String, dynamic> summary;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'ملخص مسح السوق',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 12),
            _MetricGrid(
              values: [
                ('الأسهم التي تم فحصها', _integer(summary['analyzed_count'])),
                ('الأسهم المؤهلة', _integer(summary['eligible_count'])),
                ('تعذر فحصها', _integer(summary['failed_count'])),
                ('متوسط أفضل النتائج', _decimal(summary['average_top_score'])),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ReportItemCard extends StatelessWidget {
  const _ReportItemCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
    final payload = item.payload;
    final analysis = _map(payload['analysis']);
    final tradePlan = _map(analysis['trade_plan']);
    final confidence = _decimal(payload['confidence']);
    final decision = _decision(payload['signal']?.toString());
    final explanation = payload['explanation']?.toString().trim() ?? '';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CircleAvatar(child: Text('${item.rank}')),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(decision),
                    ],
                  ),
                ),
                Chip(label: Text('${item.score.toStringAsFixed(1)} / 100')),
              ],
            ),
            const SizedBox(height: 12),
            _MetricGrid(
              values: [
                ('السعر وقت التحليل', _money(payload['price_at_analysis'])),
                ('الثقة', '$confidence%'),
                ('سعر الدخول', _money(tradePlan['entry'])),
                ('وقف الخسارة', _money(tradePlan['stop_loss'])),
                ('الهدف الأول', _money(tradePlan['target_1'])),
                ('الهدف الثاني', _money(tradePlan['target_2'])),
              ],
            ),
            if (explanation.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(explanation),
            ],
          ],
        ),
      ),
    );
  }
}

class _MetricGrid extends StatelessWidget {
  const _MetricGrid({required this.values});

  final List<(String, String)> values;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        for (final value in values)
          SizedBox(
            width: (MediaQuery.sizeOf(context).width - 74) / 2,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerLow,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Column(
                children: [
                  Text(value.$1, textAlign: TextAlign.center),
                  const SizedBox(height: 4),
                  Text(
                    value.$2,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message, required this.retry});

  final String message;
  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(18),
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

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return const <String, dynamic>{};
}

String _integer(Object? value) => value is num ? value.toInt().toString() : '—';

String _decimal(Object? value) => value is num ? value.toStringAsFixed(1) : '—';

String _money(Object? value) =>
    value is num ? '${value.toStringAsFixed(4)} ج.م' : '—';

String _decision(String? signal) => switch (signal?.toUpperCase()) {
  'BUY' => 'فرصة شراء مشروطة',
  'WATCH' => 'للمراقبة',
  'AVOID' => 'يفضل التجنب',
  _ => 'قرار غير متاح',
};

String _arabicDate(DateTime date) {
  const weekdays = <int, String>{
    DateTime.monday: 'الاثنين',
    DateTime.tuesday: 'الثلاثاء',
    DateTime.wednesday: 'الأربعاء',
    DateTime.thursday: 'الخميس',
    DateTime.friday: 'الجمعة',
    DateTime.saturday: 'السبت',
    DateTime.sunday: 'الأحد',
  };
  const months = <int, String>{
    1: 'يناير',
    2: 'فبراير',
    3: 'مارس',
    4: 'أبريل',
    5: 'مايو',
    6: 'يونيو',
    7: 'يوليو',
    8: 'أغسطس',
    9: 'سبتمبر',
    10: 'أكتوبر',
    11: 'نوفمبر',
    12: 'ديسمبر',
  };
  final local = date.toLocal();
  return '${weekdays[local.weekday]} ${local.day} ${months[local.month]} ${local.year}';
}

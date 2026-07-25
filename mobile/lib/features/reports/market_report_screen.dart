import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../../widgets/structured_data_card.dart';
import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'report_providers.dart';

class MarketReportScreen extends ConsumerStatefulWidget {
  const MarketReportScreen({
    required this.reportId,
    this.preview,
    super.key,
  });

  final String reportId;
  final MarketReportPreview? preview;

  @override
  ConsumerState<MarketReportScreen> createState() =>
      _MarketReportScreenState();
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
    if (_loading) {
      return;
    }
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
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _unlock() async {
    if (_loading) {
      return;
    }
    final cost = widget.preview?.unlockCostCoins ?? '1';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('فتح تقرير أفضل 10'),
        content: Text(
          'سيتم خصم $cost عملة مرة واحدة فقط. بعد الفتح سيظل التقرير متاحًا لهذا الحساب دون خصم متكرر.',
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
    if (confirmed != true || !mounted) {
      return;
    }

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
      if (!mounted) {
        return;
      }
      setState(() {
        _report = execution.report;
        _locked = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            execution.chargedPoints == 0
                ? 'التقرير كان مفتوحًا بالفعل ولم يحدث خصم جديد.'
                : 'تم فتح التقرير وخصم ${execution.chargedCoins} عملة.',
          ),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('تقرير أفضل 10')),
      body: SafeArea(
        child: _buildBody(context),
      ),
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
                    'أسماء الأسهم وتفاصيلها محمية حتى فتح التقرير.',
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
    final target = DateFormat('EEEE d MMMM yyyy', 'ar')
        .format(report.targetSessionDate);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'الجلسة المستهدفة',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  target,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'الترتيب ناتج عن التحليل الآلي ولا يمثل ضمانًا للربح.',
                ),
              ],
            ),
          ),
        ),
        StructuredDataCard(
          title: 'ملخص السوق',
          data: report.marketSummary,
        ),
        for (final item in report.items) _ReportItemCard(item: item),
      ],
    );
  }
}

class _ReportItemCard extends StatelessWidget {
  const _ReportItemCard({required this.item});

  final MarketReportItem item;

  @override
  Widget build(BuildContext context) {
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
                  child: Text(
                    item.ticker,
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w900,
                        ),
                  ),
                ),
                Chip(label: Text('${item.score.toStringAsFixed(2)} / 100')),
              ],
            ),
            const SizedBox(height: 10),
            StructuredDataCard(
              title: 'تفاصيل السهم',
              data: item.payload,
            ),
          ],
        ),
      ),
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
            OutlinedButton(onPressed: retry, child: const Text('إعادة المحاولة')),
          ],
        ),
      ),
    );
  }
}

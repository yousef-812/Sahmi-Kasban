import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';

class WalletHistoryScreen extends ConsumerStatefulWidget {
  const WalletHistoryScreen({super.key});

  @override
  ConsumerState<WalletHistoryScreen> createState() =>
      _WalletHistoryScreenState();
}

class _WalletHistoryScreenState extends ConsumerState<WalletHistoryScreen> {
  static const _pageSize = 20;
  final List<WalletEntryModel> _items = [];
  int _total = 0;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load(reset: true);
  }

  Future<void> _load({required bool reset}) async {
    if (_loading) {
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
      if (reset) {
        _items.clear();
      }
    });
    try {
      final page = await ref.read(backendRepositoryProvider).getWalletHistory(
            limit: _pageSize,
            offset: reset ? 0 : _items.length,
          );
      if (!mounted) {
        return;
      }
      setState(() {
        _total = page.total;
        _items.addAll(page.items);
      });
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
      appBar: AppBar(title: const Text('سجل المحفظة')),
      body: RefreshIndicator(
        onRefresh: () => _load(reset: true),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_items.isEmpty && _loading)
              const Padding(
                padding: EdgeInsets.all(48),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_items.isEmpty && _error != null)
              _MessageCard(
                icon: Icons.cloud_off_outlined,
                message: _error!,
                buttonLabel: 'إعادة المحاولة',
                onPressed: () => _load(reset: true),
              )
            else if (_items.isEmpty)
              const _MessageCard(
                icon: Icons.receipt_long_outlined,
                message: 'لا توجد عمليات في المحفظة حتى الآن.',
              )
            else ...[
              Text(
                'إجمالي العمليات: $_total',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              for (final entry in _items) _WalletEntryCard(entry: entry),
              if (_error != null)
                _MessageCard(
                  icon: Icons.error_outline,
                  message: _error!,
                  buttonLabel: 'إعادة المحاولة',
                  onPressed: () => _load(reset: false),
                ),
              if (_items.length < _total)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: OutlinedButton.icon(
                    onPressed: _loading ? null : () => _load(reset: false),
                    icon: _loading
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.expand_more_rounded),
                    label: const Text('تحميل المزيد'),
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class _WalletEntryCard extends StatelessWidget {
  const _WalletEntryCard({required this.entry});

  final WalletEntryModel entry;

  @override
  Widget build(BuildContext context) {
    final positive = entry.amountPoints >= 0;
    final amount = '${positive ? '+' : ''}${entry.amountCoins} عملة';
    final date = DateFormat('d MMM yyyy، h:mm a', 'ar').format(entry.createdAt);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: CircleAvatar(
          child: Icon(
            positive ? Icons.add_rounded : Icons.remove_rounded,
          ),
        ),
        title: Text(_entryLabel(entry)),
        subtitle: Text('$date\nالحالة: ${entry.status}'),
        isThreeLine: true,
        trailing: Text(
          amount,
          textDirection: TextDirection.ltr,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
                color: positive
                    ? Colors.green.shade700
                    : Theme.of(context).colorScheme.error,
              ),
        ),
      ),
    );
  }

  String _entryLabel(WalletEntryModel entry) {
    switch (entry.referenceType) {
      case 'stock_analysis':
        return 'تحليل سهم';
      case 'market_report':
        return 'فتح تقرير أفضل 10';
      case 'weekly_grant':
        return 'توزيع الخطة الأسبوعي';
      default:
        return entry.entryType;
    }
  }
}

class _MessageCard extends StatelessWidget {
  const _MessageCard({
    required this.icon,
    required this.message,
    this.buttonLabel,
    this.onPressed,
  });

  final IconData icon;
  final String message;
  final String? buttonLabel;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(icon, size: 42),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            if (buttonLabel != null) ...[
              const SizedBox(height: 12),
              OutlinedButton(onPressed: onPressed, child: Text(buttonLabel!)),
            ],
          ],
        ),
      ),
    );
  }
}

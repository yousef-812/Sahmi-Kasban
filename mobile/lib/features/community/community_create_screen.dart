import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'community_providers.dart';
import 'community_repository.dart';

class CommunityCreateScreen extends ConsumerStatefulWidget {
  const CommunityCreateScreen({super.key});

  @override
  ConsumerState<CommunityCreateScreen> createState() =>
      _CommunityCreateScreenState();
}

class _CommunityCreateScreenState
    extends ConsumerState<CommunityCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  late final String _submissionKey;
  MarketInstrument? _selectedInstrument;
  String _periodType = 'next_session';
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _submissionKey =
        'discussion-${DateTime.now().microsecondsSinceEpoch.toString()}';
  }

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _selectTicker() async {
    final selected = await showModalBottomSheet<MarketInstrument>(
      context: context,
      isScrollControlled: true,
      builder: (context) => const _TickerPickerSheet(),
    );
    if (selected != null && mounted) {
      setState(() => _selectedInstrument = selected);
    }
  }

  Future<void> _submit() async {
    if (_submitting || !_formKey.currentState!.validate()) {
      return;
    }
    final instrument = _selectedInstrument;
    if (instrument == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('اختر السهم المرتبط بالمناقشة.')),
      );
      return;
    }

    setState(() => _submitting = true);
    try {
      final result = await ref
          .read(communityRepositoryProvider)
          .submitDiscussion(
            submissionKey: _submissionKey,
            ticker: instrument.ticker,
            title: _titleController.text,
            content: _contentController.text,
            periodType: _periodType,
          );
      ref.invalidate(communityFeedProvider);
      ref.invalidate(myDiscussionsProvider);
      ref.invalidate(walletSummaryProvider);
      await ref.read(sessionControllerProvider.notifier).refreshProfile();
      if (!mounted) {
        return;
      }
      final message = switch (result.discussion.status) {
        'published' => 'تم قبول المناقشة ونشرها وتأكيد خصم 0.5 عملة.',
        'rejected' => 'تم رفض المناقشة وإعادة الرصيد كاملًا.',
        _ => 'تم إرسال المناقشة وهي قيد المراجعة مع حجز 0.5 عملة مؤقتًا.',
      };
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
      context.pop();
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      final retry = error.retryAfterSeconds;
      final message = retry == null
          ? error.message
          : '${error.message}\nأعد المحاولة بعد $retry ثانية.';
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('إنشاء مناقشة')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.account_balance_wallet_outlined,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text(
                        'سيتم حجز 0.5 عملة مؤقتًا. عند القبول يتحول الحجز إلى خصم نهائي، وعند الرفض يعود الرصيد كاملًا.',
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _submitting ? null : _selectTicker,
              icon: const Icon(Icons.candlestick_chart_outlined),
              label: Text(
                _selectedInstrument == null
                    ? 'اختر السهم'
                    : 'السهم: ${_selectedInstrument!.ticker}',
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _titleController,
              enabled: !_submitting,
              maxLength: 180,
              decoration: const InputDecoration(
                labelText: 'عنوان المناقشة',
                hintText: 'اكتب عنوانًا واضحًا لا يقل عن 10 أحرف',
              ),
              validator: (value) {
                final cleaned = value?.trim() ?? '';
                if (cleaned.length < 10) {
                  return 'العنوان يجب أن يحتوي على 10 أحرف على الأقل.';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _contentController,
              enabled: !_submitting,
              minLines: 6,
              maxLines: 12,
              maxLength: 5000,
              decoration: const InputDecoration(
                labelText: 'المحتوى والتوقع',
                hintText:
                    'اشرح توقعك وأسبابه من دون روابط أو أرقام هاتف أو ادعاءات ربح مضمون.',
                alignLabelWithHint: true,
              ),
              validator: (value) {
                final cleaned = value?.trim() ?? '';
                if (cleaned.length < 20) {
                  return 'المحتوى يجب أن يحتوي على 20 حرفًا على الأقل.';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _periodType,
              decoration: const InputDecoration(labelText: 'مدة التوقع'),
              items: const [
                DropdownMenuItem(
                  value: 'next_session',
                  child: Text('الجلسة القادمة'),
                ),
                DropdownMenuItem(value: 'week', child: Text('أسبوع')),
                DropdownMenuItem(value: 'month', child: Text('شهر')),
              ],
              onChanged: _submitting
                  ? null
                  : (value) => setState(
                      () => _periodType = value ?? 'next_session',
                    ),
            ),
            const SizedBox(height: 22),
            FilledButton.icon(
              onPressed: _submitting ? null : _submit,
              icon: _submitting
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send_rounded),
              label: Text(_submitting ? 'جارٍ الإرسال والمراجعة...' : 'إرسال للمراجعة'),
            ),
          ],
        ),
      ),
    );
  }
}

class _TickerPickerSheet extends ConsumerStatefulWidget {
  const _TickerPickerSheet();

  @override
  ConsumerState<_TickerPickerSheet> createState() => _TickerPickerSheetState();
}

class _TickerPickerSheetState extends ConsumerState<_TickerPickerSheet> {
  final _searchController = TextEditingController();
  List<MarketInstrument> _items = const [];
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) {
      setState(() => _error = 'اكتب رمز السهم أو جزءًا منه.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(query, limit: 30);
      if (mounted) {
        setState(() => _items = items);
      }
    } on Object catch (error) {
      if (mounted) {
        setState(() => _error = error.toString());
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          20,
          20,
          20,
          20 + MediaQuery.viewInsetsOf(context).bottom,
        ),
        child: SizedBox(
          height: MediaQuery.sizeOf(context).height * 0.65,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'اختيار سهم من EGX',
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: _searchController,
                autofocus: true,
                textCapitalization: TextCapitalization.characters,
                textInputAction: TextInputAction.search,
                decoration: InputDecoration(
                  labelText: 'رمز السهم',
                  hintText: 'COMI',
                  suffixIcon: IconButton(
                    onPressed: _loading ? null : _search,
                    icon: const Icon(Icons.search_rounded),
                  ),
                ),
                onSubmitted: (_) => _search(),
              ),
              if (_error != null) ...[
                const SizedBox(height: 10),
                Text(
                  _error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: 12),
              Expanded(
                child: _loading
                    ? const Center(child: CircularProgressIndicator())
                    : _items.isEmpty
                    ? const Center(child: Text('ابحث لاختيار السهم.'))
                    : ListView.separated(
                        itemCount: _items.length,
                        separatorBuilder: (context, index) => const Divider(),
                        itemBuilder: (context, index) {
                          final item = _items[index];
                          return ListTile(
                            title: Text(item.ticker),
                            subtitle: Text(
                              '${item.exchange} — ${item.providerSymbol}',
                              textDirection: TextDirection.ltr,
                            ),
                            trailing: const Icon(Icons.chevron_left_rounded),
                            onTap: () => Navigator.of(context).pop(item),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

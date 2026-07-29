import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'admin_models.dart';
import 'admin_providers.dart';
import 'admin_repository.dart';

class AdminWalletCreditScreen extends ConsumerStatefulWidget {
  const AdminWalletCreditScreen({super.key});

  @override
  ConsumerState<AdminWalletCreditScreen> createState() =>
      _AdminWalletCreditScreenState();
}

class _AdminWalletCreditScreenState
    extends ConsumerState<AdminWalletCreditScreen> {
  final _search = TextEditingController();
  String? _creditingUserId;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final users = ref.watch(adminUsersProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('إضافة عملات للمستخدمين')),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: TextField(
                controller: _search,
                onChanged: (_) => setState(() {}),
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search_rounded),
                  labelText: 'ابحث بالاسم أو البريد الإلكتروني',
                ),
              ),
            ),
            Expanded(
              child: users.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, __) => _Failure(
                  retry: () => ref.invalidate(adminUsersProvider),
                ),
                data: (items) {
                  final query = _search.text.trim().toLowerCase();
                  final filtered = items
                      .where(
                        (item) =>
                            query.isEmpty ||
                            item.displayName.toLowerCase().contains(query) ||
                            item.email.toLowerCase().contains(query),
                      )
                      .toList(growable: false);
                  if (filtered.isEmpty) {
                    return const Center(child: Text('لا يوجد مستخدم مطابق.'));
                  }
                  return RefreshIndicator(
                    onRefresh: () async {
                      await ref.refresh(adminUsersProvider.future);
                    },
                    child: ListView.separated(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.all(16),
                      itemCount: filtered.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (context, index) {
                        final user = filtered[index];
                        final busy = _creditingUserId == user.id;
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                Text(
                                  user.displayName,
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleMedium
                                      ?.copyWith(fontWeight: FontWeight.w900),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  user.email,
                                  textDirection: TextDirection.ltr,
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  'الخطة: ${user.planCode} • الرصيد: '
                                  '${_coins(user.balancePoints)} عملة',
                                ),
                                const SizedBox(height: 12),
                                FilledButton.icon(
                                  onPressed: busy ? null : () => _credit(user),
                                  icon: busy
                                      ? const SizedBox.square(
                                          dimension: 18,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                          ),
                                        )
                                      : const Icon(Icons.add_card_rounded),
                                  label: const Text('إضافة عملات'),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _credit(AdminUserItem user) async {
    final form = await showDialog<_CreditFormData>(
      context: context,
      builder: (context) => _CreditDialog(user: user),
    );
    if (form == null || !mounted) return;

    setState(() => _creditingUserId = user.id);
    try {
      final result = await ref
          .read(adminRepositoryProvider)
          .creditUserCoins(
            userId: user.id,
            amountCoins: form.amountCoins,
            reason: form.reason,
            requestId:
                'mobile-${DateTime.now().microsecondsSinceEpoch}-${user.id.substring(0, 8)}',
          );
      ref.invalidate(adminUsersProvider);
      ref.invalidate(adminOverviewProvider);
      ref.invalidate(adminAuditProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'تمت إضافة ${form.amountCoins} عملة إلى ${user.displayName}. '
              'الرصيد الجديد: ${result['balance_coins'] ?? '-'} عملة.',
            ),
          ),
        );
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } finally {
      if (mounted) setState(() => _creditingUserId = null);
    }
  }
}

class _CreditDialog extends StatefulWidget {
  const _CreditDialog({required this.user});

  final AdminUserItem user;

  @override
  State<_CreditDialog> createState() => _CreditDialogState();
}

class _CreditDialogState extends State<_CreditDialog> {
  final _amount = TextEditingController();
  final _reason = TextEditingController();
  String? _error;

  @override
  void dispose() {
    _amount.dispose();
    _reason.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('إضافة عملات إلى ${widget.user.displayName}'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'الرصيد الحالي: ${_coins(widget.user.balancePoints)} عملة',
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _amount,
              keyboardType: TextInputType.number,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'عدد العملات',
                prefixIcon: Icon(Icons.monetization_on_outlined),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _reason,
              minLines: 2,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'سبب الإضافة',
                hintText: 'مثال: تعويض عن مشكلة في التقرير',
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 10),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        FilledButton(
          onPressed: _submit,
          child: const Text('تأكيد الإضافة'),
        ),
      ],
    );
  }

  void _submit() {
    final amount = int.tryParse(_amount.text.trim());
    final reason = _reason.text.trim();
    if (amount == null || amount < 1 || amount > 100000) {
      setState(() => _error = 'أدخل عدد عملات صحيحًا من 1 إلى 100000.');
      return;
    }
    if (reason.length < 4) {
      setState(() => _error = 'اكتب سببًا واضحًا لا يقل عن 4 أحرف.');
      return;
    }
    Navigator.pop(
      context,
      _CreditFormData(amountCoins: amount, reason: reason),
    );
  }
}

class _CreditFormData {
  const _CreditFormData({required this.amountCoins, required this.reason});

  final int amountCoins;
  final String reason;
}

class _Failure extends StatelessWidget {
  const _Failure({required this.retry});

  final VoidCallback retry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('تعذر تحميل المستخدمين.'),
            const SizedBox(height: 10),
            OutlinedButton(onPressed: retry, child: const Text('إعادة المحاولة')),
          ],
        ),
      ),
    );
  }
}

String _coins(int points) => (points / 100).toStringAsFixed(2);

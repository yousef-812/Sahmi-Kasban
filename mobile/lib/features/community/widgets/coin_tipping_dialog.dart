import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../community_models.dart';
import '../community_providers.dart';
import '../community_repository.dart';
import '../../auth/session_controller.dart';

class CoinTippingDialog extends ConsumerStatefulWidget {
  const CoinTippingDialog({
    super.key,
    required this.profile,
  });

  final UserPublicProfile profile;

  static Future<bool?> show(BuildContext context, UserPublicProfile profile) {
    return showDialog<bool>(
      context: context,
      builder: (_) => CoinTippingDialog(profile: profile),
    );
  }

  @override
  ConsumerState<CoinTippingDialog> createState() => _CoinTippingDialogState();
}

class _CoinTippingDialogState extends ConsumerState<CoinTippingDialog> {
  int _selectedAmount = 5;
  final _customAmountController = TextEditingController();
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _customAmountController.text = '5';
  }

  @override
  void dispose() {
    _customAmountController.dispose();
    super.dispose();
  }

  Future<void> _submitTip() async {
    final amount = int.tryParse(_customAmountController.text.trim());
    if (amount == null || amount <= 0) {
      setState(() {
        _errorMessage = 'يرجى إدخال عدد صحيح من العملات أكبر من 0';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final repo = ref.read(communityRepositoryProvider);
      await repo.sendCoinTip(
        receiverId: widget.profile.userId,
        amountCoins: amount,
      );

      ref.invalidate(sessionControllerProvider);
      ref.invalidate(communityFeedProvider);

      if (mounted) {
        Navigator.of(context).pop(true);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'تم إهداء $amount عملة بنجاح إلى ${widget.profile.displayName}',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final userCoins = ref.watch(sessionControllerProvider).profile?.balanceCoins ?? '0';

    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Column(
        children: [
          const Icon(
            Icons.monetization_on,
            size: 40,
            color: Colors.amber,
          ),
          const SizedBox(height: 8),
          Text(
            'إهداء عملات إلى ${widget.profile.displayName}',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'رصيدك الحالي: $userCoins عملة',
              style: TextStyle(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            const Text(
              'اختر كمية العملات المراد إهداؤها:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 10),

            // Preset Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [5, 10, 20].map((preset) {
                final isSelected = _selectedAmount == preset;
                return ChoiceChip(
                  label: Text('$preset عملات'),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() {
                        _selectedAmount = preset;
                        _customAmountController.text = '$preset';
                      });
                    }
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            // Custom Amount TextField
            TextField(
              controller: _customAmountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'عدد العملات',
                prefixIcon: Icon(Icons.monetization_on_outlined),
                border: OutlineInputBorder(),
              ),
              onChanged: (val) {
                final parsed = int.tryParse(val);
                if (parsed != null) {
                  setState(() {
                    _selectedAmount = parsed;
                  });
                }
              },
            ),

            if (_errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                _errorMessage!,
                style: const TextStyle(color: Colors.red, fontSize: 13),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isSubmitting ? null : () => Navigator.of(context).pop(false),
          child: const Text('إلغاء'),
        ),
        ElevatedButton.icon(
          onPressed: _isSubmitting ? null : _submitTip,
          icon: _isSubmitting
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.send),
          label: const Text('إرسال الهديّة'),
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.onPrimary,
          ),
        ),
      ],
    );
  }
}

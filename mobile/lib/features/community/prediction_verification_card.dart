import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'community_providers.dart';
import 'prediction_models.dart';
import 'prediction_providers.dart';
import 'prediction_repository.dart';

class PredictionVerificationCard extends ConsumerStatefulWidget {
  const PredictionVerificationCard({required this.discussionId, super.key});

  final String discussionId;

  @override
  ConsumerState<PredictionVerificationCard> createState() =>
      _PredictionVerificationCardState();
}

class _PredictionVerificationCardState
    extends ConsumerState<PredictionVerificationCard> {
  bool _verifying = false;

  Future<void> _verify() async {
    if (_verifying) {
      return;
    }
    setState(() => _verifying = true);
    try {
      final result = await ref
          .read(predictionRepositoryProvider)
          .verifyPrediction(widget.discussionId);
      ref.invalidate(predictionVerificationStatusProvider(widget.discussionId));
      ref.invalidate(myPredictionStatsProvider);
      ref.invalidate(myDiscussionsProvider);
      ref.invalidate(walletSummaryProvider);
      await ref.read(sessionControllerProvider.notifier).refreshProfile();
      if (!mounted) {
        return;
      }
      final reward = result.verification.rewardCoins;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            result.verification.rewardPoints > 0
                ? 'تم تقييم التوقع وإضافة $reward عملة إلى رصيدك.'
                : 'تم تقييم التوقع. لا توجد مكافأة لهذه النتيجة.',
          ),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    } finally {
      if (mounted) {
        setState(() => _verifying = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = ref.watch(
      predictionVerificationStatusProvider(widget.discussionId),
    );
    return status.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(18),
          child: Row(
            children: [
              SizedBox.square(
                dimension: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              SizedBox(width: 12),
              Expanded(child: Text('جاري التحقق من موعد تقييم التوقع...')),
            ],
          ),
        ),
      ),
      error: (error, stackTrace) => Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              const Expanded(child: Text('تعذر تحميل حالة تقييم التوقع.')),
              TextButton(
                onPressed: () => ref.invalidate(
                  predictionVerificationStatusProvider(widget.discussionId),
                ),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
      data: (value) => switch (value.state) {
        'waiting' => _WaitingCard(status: value),
        'eligible' => _EligibleCard(verifying: _verifying, onVerify: _verify),
        'verified' when value.verification != null => _VerificationResultCard(
          verification: value.verification!,
        ),
        _ => const SizedBox.shrink(),
      },
    );
  }
}

class _WaitingCard extends StatelessWidget {
  const _WaitingCard({required this.status});

  final PredictionVerificationStatus status;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.schedule_outlined,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'التوقع لم يصبح جاهزًا للتحقق بعد',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  if (status.eligibleAt != null) ...[
                    const SizedBox(height: 6),
                    Text(
                      'موعد التحقق المتوقع: ${_formatDate(status.eligibleAt!)}',
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EligibleCard extends StatelessWidget {
  const _EligibleCard({required this.verifying, required this.onVerify});

  final bool verifying;
  final VoidCallback onVerify;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.fact_check_outlined,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'انتهت فترة التوقع وأصبحت بياناته جاهزة للمقارنة.',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: verifying ? null : onVerify,
              icon: verifying
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.verified_outlined),
              label: const Text('تحقق من صحة توقعي'),
            ),
          ],
        ),
      ),
    );
  }
}

class _VerificationResultCard extends StatelessWidget {
  const _VerificationResultCard({required this.verification});

  final PredictionVerification verification;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.verified_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'نتيجة تقييم التوقع',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Chip(label: Text(verification.strengthLabel)),
              ],
            ),
            const SizedBox(height: 14),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _MetricChip(
                  label: 'الدرجة',
                  value: '${verification.scorePercent.toStringAsFixed(2)}%',
                ),
                _MetricChip(
                  label: 'المكافأة',
                  value: '${verification.rewardCoins} عملة',
                ),
              ],
            ),
            const SizedBox(height: 14),
            Text(verification.explanation),
            const SizedBox(height: 8),
            Text(
              'تم التقييم في ${_formatDate(verification.verifiedAt)}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Chip(label: Text('$label: $value'));
  }
}

String _formatDate(DateTime value) {
  final local = value.toLocal();
  String two(int number) => number.toString().padLeft(2, '0');
  return '${two(local.day)}/${two(local.month)}/${local.year} '
      '${two(local.hour)}:${two(local.minute)}';
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../auth/session_controller.dart';
import '../monetization/free_plan_ads.dart';
import '../wallet/wallet_providers.dart';
import 'community_providers.dart';
import 'community_repository.dart';

enum PredictionPromptResult { published, skipped }

class StockPredictionPromptDialog extends ConsumerStatefulWidget {
  const StockPredictionPromptDialog({
    super.key,
    required this.ticker,
    this.displayName,
  });

  final String ticker;
  final String? displayName;

  static Future<PredictionPromptResult?> show(
    BuildContext context, {
    required String ticker,
    String? displayName,
  }) {
    return showModalBottomSheet<PredictionPromptResult>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        child: StockPredictionPromptDialog(
          ticker: ticker,
          displayName: displayName,
        ),
      ),
    );
  }

  @override
  ConsumerState<StockPredictionPromptDialog> createState() =>
      _StockPredictionPromptDialogState();
}

class _StockPredictionPromptDialogState
    extends ConsumerState<StockPredictionPromptDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _titleController;
  late final TextEditingController _contentController;
  String _periodType = 'next_session';
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    final name = widget.displayName ?? widget.ticker;
    _titleController = TextEditingController(
      text: 'توقعي لسهم $name للجلسة القادمة',
    );
    _contentController = TextEditingController();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _publishAndContinue() async {
    if (_submitting || !_formKey.currentState!.validate()) {
      return;
    }
    setState(() => _submitting = true);
    final submissionKey =
        'prediction-prompt-${DateTime.now().microsecondsSinceEpoch}';

    try {
      final result = await ref
          .read(communityRepositoryProvider)
          .submitDiscussion(
            submissionKey: submissionKey,
            ticker: widget.ticker,
            title: _titleController.text,
            content: _contentController.text,
            periodType: _periodType,
          );

      ref.invalidate(communityFeedProvider);
      ref.invalidate(myDiscussionsProvider);
      ref.invalidate(walletSummaryProvider);
      try {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
      } on Object {
        // Optional profile refresh
      }

      if (!mounted) return;

      await ref
          .read(freePlanInterstitialProvider)
          .recordMeaningfulAction(
            enabled:
                ref.read(sessionControllerProvider).profile?.adsEnabled == true,
          );

      if (!mounted) return;

      final message = switch (result.discussion.status) {
        'published' => 'تم نشر توقعك في المجتمع بنجاح.',
        'rejected' => 'لم يتم قبول نشر التوقع.',
        _ => 'تم إرسال التوقع وهو قيد المراجعة حاليًا.',
      };

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );

      Navigator.of(context).pop(PredictionPromptResult.published);
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.message)),
      );
    } on Object catch (error) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.toString())),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final stockLabel = widget.displayName != null
        ? '${widget.ticker} (${widget.displayName})'
        : widget.ticker;

    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
      child: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.onSurfaceVariant.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: theme.colorScheme.primaryContainer,
                    radius: 22,
                    child: Icon(
                      Icons.forum_rounded,
                      color: theme.colorScheme.primary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'هل لديك توقع لسهم $stockLabel؟',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'شارك رؤيتك مع مجتمع المتداولين قبل التحليل',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _titleController,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'عنوان التوقع',
                  hintText: 'أدخل عنوانًا مختصرًا ورأيـك في السهم',
                  prefixIcon: Icon(Icons.title_rounded),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'يرجى كتابة عنوان التوقع.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _contentController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'تفاصيل التوقع والملاحظات الفنية',
                  hintText:
                      'اكتب أسباب توقعك الصاعد/الهابط أو المستهدفات السعرية...',
                  alignLabelWithHint: true,
                ),
                validator: (value) {
                  if (value == null || value.trim().length < 5) {
                    return 'يرجى كتابة محتوى التوقع (5 أشكال على الأقل).';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              _PredictionDateDropdown(
                value: _periodType,
                onChanged: (value) {
                  if (value != null) setState(() => _periodType = value);
                },
              ),
              const SizedBox(height: 20),
              // Prominent Large Primary Button
              SizedBox(
                height: 54,
                child: FilledButton.icon(
                  onPressed: _submitting ? null : _publishAndContinue,
                  style: FilledButton.styleFrom(
                    backgroundColor: theme.colorScheme.primary,
                    foregroundColor: theme.colorScheme.onPrimary,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  icon: _submitting
                      ? const SizedBox.square(
                          dimension: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.send_rounded),
                  label: Text(
                    _submitting
                        ? 'جارٍ نشر التوقع...'
                        : 'نشر التوقع والمتابعة للتحليل',
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              // Smaller Secondary Button to Skip
              Center(
                child: TextButton.icon(
                  onPressed: _submitting
                      ? null
                      : () => Navigator.of(
                            context,
                          ).pop(PredictionPromptResult.skipped),
                  icon: Icon(
                    Icons.visibility_outlined,
                    size: 18,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  label: Text(
                    'رؤية التحليل أولاً',
                    style: TextStyle(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// A Riverpod-aware dropdown that fetches upcoming trading dates dynamically.
class _PredictionDateDropdown extends ConsumerWidget {
  const _PredictionDateDropdown({
    required this.value,
    required this.onChanged,
  });

  final String value;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final datesAsync = ref.watch(predictionDatesProvider);

    return datesAsync.when(
      loading: () => InputDecorator(
        decoration: const InputDecoration(
          labelText: 'أفق التوقع والتقييم',
          prefixIcon: Icon(Icons.schedule_rounded),
        ),
        child: const SizedBox(
          height: 20,
          child: LinearProgressIndicator(minHeight: 2),
        ),
      ),
      error: (_, __) => InputDecorator(
        decoration: const InputDecoration(
          labelText: 'أفق التوقع والتقييم',
          prefixIcon: Icon(Icons.schedule_rounded),
          errorText: 'تعذر تحميل الجلسات',
        ),
        child: const SizedBox.shrink(),
      ),
      data: (dates) {
        // Determine the current value: if it matches one of the dates use it,
        // otherwise fall back to the first date in the list.
        final validValues = dates.map((d) => d.date).toSet();
        final currentValue =
            validValues.contains(value) ? value : dates.firstOrNull?.date;

        // Notify parent if we needed to change the selected value.
        if (currentValue != null && currentValue != value) {
          WidgetsBinding.instance.addPostFrameCallback(
            (_) => onChanged(currentValue),
          );
        }

        return DropdownButtonFormField<String>(
          initialValue: currentValue,
          decoration: const InputDecoration(
            labelText: 'أفق التوقع والتقييم',
            prefixIcon: Icon(Icons.schedule_rounded),
          ),
          items: dates
              .map(
                (opt) => DropdownMenuItem<String>(
                  value: opt.date,
                  child: Text(opt.displayName),
                ),
              )
              .toList(),
          onChanged: onChanged,
        );
      },
    );
  }
}

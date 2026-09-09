import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'community_providers.dart';

/// A Riverpod-aware dropdown that fetches the current week's upcoming trading
/// dates dynamically and lets the user pick a single-session prediction date.
class PredictionDateDropdown extends ConsumerWidget {
  const PredictionDateDropdown({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final String value;
  final ValueChanged<String?>? onChanged;

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
            (_) => onChanged?.call(currentValue),
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
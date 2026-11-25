import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'volume_profile_models.dart';
import 'volume_profile_providers.dart';

/// بطاقة حجم السعر (POC/منطقة القيمة 70%) — WP-30.
///
/// هيستوجرام أفقي من شموم OHLCV اليومية (كل شمعة تُوزَّع على نطاقات سعرها):
/// تقريب موثّق، **لا بيانات tick حقيقية** (لا يوجد مصدر مجاني لـ EGX).
/// تُبرز شريحة POC ونطاق منطقة القيمة.
class VolumeProfileCard extends ConsumerWidget {
  const VolumeProfileCard({super.key, required this.ticker});

  final String ticker;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final state = ref.watch(volumeProfileProvider(ticker));
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.bar_chart_rounded,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  'حجم السعر',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              'POC ومنطقة القيمة 70% — تقريب من الشموم اليومية لا بيانات tick.',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 10),
            state.when(
              loading: () => const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Center(
                  child: SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2.5),
                  ),
                ),
              ),
              error: (error, stackTrace) => _ProfileError(
                error: error,
                onRetry: () => ref.invalidate(volumeProfileProvider(ticker)),
              ),
              data: (snapshot) => _ProfileData(snapshot: snapshot),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProfileData extends StatelessWidget {
  const _ProfileData({required this.snapshot});

  final StockVolumeProfileSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (!snapshot.available || snapshot.bins.isEmpty || snapshot.poc == null) {
      return _ProfileNote(
        message: snapshot.reason ?? 'بيانات حجم السعر غير متاحة حاليًا.',
      );
    }
    final maxVolume = snapshot.maxBinVolume ?? 0;
    final rows = snapshot.bins.reversed.toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 6,
          children: [
            _LevelChip(label: 'POC', value: _price(snapshot.poc!)),
            if (snapshot.valueAreaHigh != null)
              _LevelChip(
                label: 'VAH',
                value: _price(snapshot.valueAreaHigh!),
              ),
            if (snapshot.valueAreaLow != null)
              _LevelChip(
                label: 'VAL',
                value: _price(snapshot.valueAreaLow!),
              ),
            if (snapshot.aboveValuePct != null)
              _LevelChip(
                label: 'فوق القيمة',
                value: '${snapshot.aboveValuePct!.toStringAsFixed(1)}%',
              ),
            if (snapshot.belowValuePct != null)
              _LevelChip(
                label: 'تحت القيمة',
                value: '${snapshot.belowValuePct!.toStringAsFixed(1)}%',
              ),
          ],
        ),
        const SizedBox(height: 10),
        for (final bin in rows)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 1.5),
            child: Row(
              children: [
                SizedBox(
                  width: 58,
                  child: Text(
                    _price(bin.priceLow),
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(3),
                    child: FractionallySizedBox(
                      alignment: AlignmentDirectional.centerStart,
                      widthFactor: maxVolume > 0
                          ? (bin.volume / maxVolume).clamp(0.005, 1.0)
                          : 0.005,
                      child: Container(
                        height: 10,
                        color: _barColor(theme, bin),
                      ),
                    ),
                  ),
                ),
                SizedBox(
                  width: 56,
                  child: Text(
                    _volumeLabel(bin.volume),
                    textDirection: TextDirection.ltr,
                    textAlign: TextAlign.end,
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: snapshot.isPocBin(bin)
                          ? FontWeight.w800
                          : FontWeight.w400,
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Color _barColor(ThemeData theme, VolumeProfileBin bin) {
    if (snapshot.isPocBin(bin)) return theme.colorScheme.primary;
    if (snapshot.isInValueArea(bin)) {
      return theme.colorScheme.primary.withValues(alpha: 0.4);
    }
    return theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.35);
  }

  String _price(double value) => value.toStringAsFixed(2);

  String _volumeLabel(double value) {
    if (value >= 1_000_000) return '${(value / 1_000_000).toStringAsFixed(2)} م';
    if (value >= 1_000) return '${(value / 1_000).toStringAsFixed(1)} أ';
    return value.toStringAsFixed(0);
  }
}

class _LevelChip extends StatelessWidget {
  const _LevelChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            value,
            textDirection: TextDirection.ltr,
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfileError extends StatelessWidget {
  const _ProfileError({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 18,
              color: theme.colorScheme.error,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                error is ApiException
                    ? (error as ApiException).message
                    : 'تعذر تحميل حجم السعر.',
                style: theme.textTheme.bodySmall,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        OutlinedButton.icon(
          onPressed: onRetry,
          icon: const Icon(Icons.refresh_rounded, size: 16),
          label: const Text('إعادة المحاولة'),
          style: OutlinedButton.styleFrom(visualDensity: VisualDensity.compact),
        ),
      ],
    );
  }
}

class _ProfileNote extends StatelessWidget {
  const _ProfileNote({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final muted = theme.colorScheme.onSurfaceVariant;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: muted.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.info_outline_rounded, size: 18, color: muted),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: theme.textTheme.bodySmall?.copyWith(color: muted),
            ),
          ),
        ],
      ),
    );
  }
}

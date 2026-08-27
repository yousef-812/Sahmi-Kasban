import 'package:flutter/material.dart';

/// بطاقة عرض زخم القطاع مع تحذير بصري عند الهبوط الشديد.
/// تعكس ترقية "Sector Momentum Engine" في المحرك.
class SectorMomentumCard extends StatelessWidget {
  const SectorMomentumCard({
    required this.sectorMomentumPct,
    this.sectorName,
    super.key,
  });

  final double sectorMomentumPct;
  final String? sectorName;

  /// تحديد حالة القطاع بناءً على زخم آخر 5 أيام
  _SectorState get _state {
    if (sectorMomentumPct > 3.0) return _SectorState.strongBullish;
    if (sectorMomentumPct > 0.0) return _SectorState.mildBullish;
    if (sectorMomentumPct < -3.0) return _SectorState.strongBearish;
    if (sectorMomentumPct < -1.0) return _SectorState.mildBearish;
    return _SectorState.neutral;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final state = _state;

    return Card(
      color: state.backgroundColor(theme),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(state.icon, color: state.iconColor(theme), size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'أداء القطاع${sectorName != null ? ': $sectorName' : ''}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      Text('زخم آخر 5 جلسات', style: theme.textTheme.bodySmall),
                    ],
                  ),
                ),
                _MomentumBadge(pct: sectorMomentumPct, state: state),
              ],
            ),
            const SizedBox(height: 14),
            // شريط التقدم البصري
            _MomentumBar(pct: sectorMomentumPct, state: state),
            const SizedBox(height: 12),
            // رسالة التحذير/التشجيع
            Text(
              state.message(sectorMomentumPct),
              style: theme.textTheme.bodyMedium?.copyWith(
                color: state.messageColor(theme),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

enum _SectorState {
  strongBullish,
  mildBullish,
  neutral,
  mildBearish,
  strongBearish;

  IconData get icon => switch (this) {
    strongBullish => Icons.trending_up_rounded,
    mildBullish => Icons.arrow_upward_rounded,
    neutral => Icons.trending_flat_rounded,
    mildBearish => Icons.arrow_downward_rounded,
    strongBearish => Icons.trending_down_rounded,
  };

  Color iconColor(ThemeData theme) => switch (this) {
    strongBullish => Colors.green.shade700,
    mildBullish => Colors.green.shade500,
    neutral => theme.colorScheme.outline,
    mildBearish => Colors.orange.shade700,
    strongBearish => Colors.red.shade700,
  };

  Color backgroundColor(ThemeData theme) => switch (this) {
    strongBullish => Colors.green.shade50,
    mildBullish => Colors.green.shade50.withValues(alpha: 0.5),
    neutral => theme.colorScheme.surfaceContainerLow,
    mildBearish => Colors.orange.shade50,
    strongBearish => Colors.red.shade50,
  };

  Color messageColor(ThemeData theme) => switch (this) {
    strongBullish => Colors.green.shade800,
    mildBullish => Colors.green.shade700,
    neutral => theme.colorScheme.onSurface,
    mildBearish => Colors.orange.shade800,
    strongBearish => Colors.red.shade800,
  };

  String message(double pct) => switch (this) {
    strongBullish => '✅ القطاع في زخم صعودي قوي — بيئة داعمة للسهم',
    mildBullish => '📈 القطاع إيجابي — يدعم اتجاه السهم',
    neutral => '⚖️ القطاع محايد — لا ضغط إضافي على السهم',
    mildBearish => '⚠️ القطاع تحت ضغط — انتبه لمخاطر القطاع',
    strongBearish =>
      '🚨 القطاع في هبوط حاد — مخاطر قطاعية عالية، تم تحويل التوصية للمراقبة',
  };
}

class _MomentumBadge extends StatelessWidget {
  const _MomentumBadge({required this.pct, required this.state});
  final double pct;
  final _SectorState state;

  @override
  Widget build(BuildContext context) {
    final isPositive = pct >= 0;
    final color = state.iconColor(Theme.of(context));
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isPositive ? Icons.arrow_drop_up : Icons.arrow_drop_down,
            color: color,
            size: 22,
          ),
          Text(
            '${pct.abs().toStringAsFixed(2)}%',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w900,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}

class _MomentumBar extends StatelessWidget {
  const _MomentumBar({required this.pct, required this.state});
  final double pct;
  final _SectorState state;

  @override
  Widget build(BuildContext context) {
    // نحدد نطاق الشريط من -10% إلى +10%
    const range = 10.0;
    final clamped = pct.clamp(-range, range);
    final normalizedPosition = (clamped + range) / (2 * range); // 0 إلى 1

    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final center = width / 2;
        final position = normalizedPosition * width;
        final color = state.iconColor(Theme.of(context));

        return Stack(
          children: [
            // الشريط الخلفي
            Container(
              height: 8,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.outlineVariant,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            // خط المنتصف (الصفر)
            Positioned(
              left: center - 0.5,
              child: Container(
                width: 1,
                height: 8,
                color: Theme.of(context).colorScheme.outline,
              ),
            ),
            // مؤشر الموقع الحالي
            Positioned(
              left: position.clamp(0.0, width - 12),
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: color.withValues(alpha: 0.4),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

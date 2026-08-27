import 'package:flutter/material.dart';

/// نظام الألوان والطباعة لهوية "Trading Terminal"
/// Dark-first، كثافة معلومات عالية، ألوان نيون للإشارات.
class TerminalThemeData {
  TerminalThemeData({
    required this.bgBase,
    required this.bgSurface,
    required this.bgElevated,
    required this.textPrimary,
    required this.textSecondary,
    required this.textTertiary,
    required this.bullGreen,
    required this.bearRed,
    required this.signalGold,
    required this.border,
    required this.titleSmall,
    required this.monoHuge,
    required this.monoLarge,
    required this.monoMedium,
    required this.monoSmall,
    required this.monoTiny,
  });

  // Backgrounds
  final Color bgBase;       // #0A0E1A
  final Color bgSurface;    // #1C2130
  final Color bgElevated;   // #252A3A

  // Text
  final Color textPrimary;   // #E8ECF4
  final Color textSecondary; // #8892A6
  final Color textTertiary;  // #5A6478

  // Signals
  final Color bullGreen;    // #00E676
  final Color bearRed;      // #FF3D57
  final Color signalGold;   // #FFB800

  // Borders
  final Color border;       // #2A3040

  // Typography
  final TextStyle titleSmall;
  final TextStyle monoHuge;    // 32px للأرقام الكبيرة
  final TextStyle monoLarge;   // 24px
  final TextStyle monoMedium;  // 16px
  final TextStyle monoSmall;   // 13px
  final TextStyle monoTiny;    // 11px
}

class TerminalTheme extends InheritedWidget {
  const TerminalTheme({
    required super.child,
    required this.data,
    super.key,
  });

  final TerminalThemeData data;

  static TerminalThemeData of(BuildContext context) {
    final widget = context.dependOnInheritedWidgetOfExactType<TerminalTheme>();
    return widget?.data ?? _defaultTerminalTheme();
  }

  @override
  bool updateShouldNotify(TerminalTheme oldWidget) => data != oldWidget.data;
}

TerminalThemeData _defaultTerminalTheme() {
  const monoFamily = 'JetBrains Mono';
  const titleFamily = 'Cairo';

  return TerminalThemeData(
    bgBase: const Color(0xFF0A0E1A),
    bgSurface: const Color(0xFF1C2130),
    bgElevated: const Color(0xFF252A3A),
    textPrimary: const Color(0xFFE8ECF4),
    textSecondary: const Color(0xFF8892A6),
    textTertiary: const Color(0xFF5A6478),
    bullGreen: const Color(0xFF00E676),
    bearRed: const Color(0xFFFF3D57),
    signalGold: const Color(0xFFFFB800),
    border: const Color(0xFF2A3040),
    titleSmall: const TextStyle(
      fontFamily: titleFamily,
      fontSize: 15,
      fontWeight: FontWeight.w700,
      letterSpacing: 0.3,
    ),
    monoHuge: const TextStyle(
      fontFamily: monoFamily,
      fontSize: 32,
      fontWeight: FontWeight.w900,
      fontFeatures: [FontFeature.tabularFigures()],
    ),
    monoLarge: const TextStyle(
      fontFamily: monoFamily,
      fontSize: 24,
      fontWeight: FontWeight.w800,
      fontFeatures: [FontFeature.tabularFigures()],
    ),
    monoMedium: const TextStyle(
      fontFamily: monoFamily,
      fontSize: 16,
      fontWeight: FontWeight.w600,
      fontFeatures: [FontFeature.tabularFigures()],
    ),
    monoSmall: const TextStyle(
      fontFamily: monoFamily,
      fontSize: 13,
      fontWeight: FontWeight.w500,
      fontFeatures: [FontFeature.tabularFigures()],
    ),
    monoTiny: const TextStyle(
      fontFamily: monoFamily,
      fontSize: 11,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.5,
      fontFeatures: [FontFeature.tabularFigures()],
    ),
  );
}

import 'package:flutter/material.dart';

/// هوية "سهمي كسبان" الجديدة — ألوان العلامة التجارية.
///
/// الخلفية الأساسية: #0A0E1A (Deep Space)
/// الخلفية الثانوية: #141824 (Carbon)
/// الأسطح:           #1C2130 (Graphite)
/// الأخضر الصاعد:    #00E676 (Neon Bull)
/// الأحمر الهابط:    #FF3D57 (Alert Red)
/// الذهبي المميز:    #FFB800 (Signal Gold)
/// النصوص:           #E8ECF4 (Ice White)
abstract final class SahmiBrand {
  static const Color deepSpace = Color(0xFF0A0E1A);
  static const Color carbon = Color(0xFF141824);
  static const Color graphite = Color(0xFF1C2130);
  static const Color graphiteHigh = Color(0xFF252A3A);
  static const Color neonBull = Color(0xFF00E676);
  static const Color alertRed = Color(0xFFFF3D57);
  static const Color signalGold = Color(0xFFFFB800);
  static const Color iceWhite = Color(0xFFE8ECF4);

  static const Color glassBorder = Color(0xFF2A3040);
  static const Color textSecondary = Color(0xFF8892A6);
  static const Color textTertiary = Color(0xFF5A6478);

  // الأشكال الفاتحة (Light Mode) المشتقة من نفس الهوية.
  static const Color lightScaffold = Color(0xFFF3F5F8);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightPrimary = Color(0xFF009E5F);
  static const Color lightPrimaryContainer = Color(0xFFD7F5E6);
  static const Color lightText = Color(0xFF141824);
}

class SahmiTheme {
  const SahmiTheme._();

  /// السمة الداكنة — هوية "Deep Space" الافتراضية.
  static ThemeData dark() {
    final scheme = ColorScheme.fromSeed(
      seedColor: SahmiBrand.neonBull,
      brightness: Brightness.dark,
    ).copyWith(
      primary: SahmiBrand.neonBull,
      onPrimary: SahmiBrand.deepSpace,
      primaryContainer: const Color(0xFF0E3A2A),
      onPrimaryContainer: const Color(0xFFB4FFD9),
      secondary: SahmiBrand.signalGold,
      onSecondary: SahmiBrand.deepSpace,
      secondaryContainer: const Color(0xFF3A2F00),
      onSecondaryContainer: const Color(0xFFFFE9A8),
      tertiary: SahmiBrand.alertRed,
      onTertiary: Colors.white,
      tertiaryContainer: const Color(0xFF3A2026),
      onTertiaryContainer: const Color(0xFFFFB9C4),
      error: const Color(0xFFFF6B7D),
      errorContainer: const Color(0xFF4A1A22),
      onErrorContainer: const Color(0xFFFFD9DE),
      surface: SahmiBrand.graphite,
      onSurface: SahmiBrand.iceWhite,
      surfaceContainerLowest: SahmiBrand.deepSpace,
      surfaceContainerLow: const Color(0xFF161B28),
      surfaceContainer: SahmiBrand.graphite,
      surfaceContainerHigh: SahmiBrand.graphiteHigh,
      surfaceContainerHighest: const Color(0xFF2C3244),
      onSurfaceVariant: SahmiBrand.textSecondary,
      outline: SahmiBrand.glassBorder,
      outlineVariant: const Color(0xFF2A3040),
      inverseSurface: SahmiBrand.iceWhite,
      onInverseSurface: SahmiBrand.deepSpace,
      surfaceTint: SahmiBrand.neonBull,
    );

    return _build(scheme, deepSpaceScaffold: true);
  }

  /// السمة الفاتحة — نسخة مشتقة من نفس الهوية.
  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: SahmiBrand.lightPrimary,
      brightness: Brightness.light,
    ).copyWith(
      primary: SahmiBrand.lightPrimary,
      onPrimary: Colors.white,
      primaryContainer: SahmiBrand.lightPrimaryContainer,
      onPrimaryContainer: const Color(0xFF00351F),
      secondary: const Color(0xFFB8860B),
      onSecondary: Colors.white,
      secondaryContainer: const Color(0xFFFFE9A8),
      onSecondaryContainer: const Color(0xFF3A2F00),
      tertiary: SahmiBrand.alertRed,
      onTertiary: Colors.white,
      tertiaryContainer: const Color(0xFFFFD9DE),
      onTertiaryContainer: const Color(0xFF3B0A1A),
      error: const Color(0xFFB3261E),
      errorContainer: const Color(0xFFF9DEDC),
      onErrorContainer: const Color(0xFF410002),
      surface: SahmiBrand.lightSurface,
      onSurface: SahmiBrand.lightText,
      surfaceContainerLowest: Colors.white,
      surfaceContainerLow: const Color(0xFFF7F8FB),
      surfaceContainer: const Color(0xFFEDEFF4),
      surfaceContainerHigh: const Color(0xFFE4E7EE),
      surfaceContainerHighest: const Color(0xFFD7DBE4),
      onSurfaceVariant: const Color(0xFF4A5160),
      outline: const Color(0xFFB9BEC9),
      outlineVariant: const Color(0xFFDDE1E9),
      inverseSurface: SahmiBrand.deepSpace,
      onInverseSurface: SahmiBrand.iceWhite,
      surfaceTint: SahmiBrand.lightPrimary,
    );

    // استرجاع القراءة: النصوص بالفعل فاتحة على السطح الفاتح، لكننا نعيد
    // ضبط ألوان النصوص الأساسية لتكون داكنة.
    return _build(scheme, deepSpaceScaffold: false);
  }

  static ThemeData _build(ColorScheme scheme, {required bool deepSpaceScaffold}) {
    final isDark = scheme.brightness == Brightness.dark;

    final base = ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      fontFamily: 'Cairo',
      scaffoldBackgroundColor: isDark
          ? SahmiBrand.deepSpace
          : SahmiBrand.lightScaffold,
    );

    final ColorScheme cs = base.colorScheme;

    return base.copyWith(
      appBarTheme: AppBarTheme(
        elevation: 0,
        centerTitle: false,
        backgroundColor: isDark ? SahmiBrand.deepSpace : SahmiBrand.lightScaffold,
        surfaceTintColor: Colors.transparent,
        foregroundColor: cs.onSurface,
        titleTextStyle: TextStyle(
          color: cs.onSurface,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        margin: EdgeInsets.zero,
        color: isDark ? SahmiBrand.graphite : SahmiBrand.lightSurface,
        surfaceTintColor: Colors.transparent,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(20)),
          side: BorderSide(color: SahmiBrand.glassBorder, width: 0.6),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: SahmiBrand.glassBorder,
        thickness: 0.8,
        space: 1,
      ),
      chipTheme: base.chipTheme.copyWith(
        backgroundColor: isDark
            ? SahmiBrand.carbon
            : SahmiBrand.lightSurface,
        side: BorderSide(color: SahmiBrand.glassBorder),
        labelStyle: base.textTheme.labelMedium?.copyWith(
          color: cs.onSurface,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: isDark ? SahmiBrand.carbon : SahmiBrand.lightSurface,
        border: OutlineInputBorder(
          borderRadius: const BorderRadius.all(Radius.circular(16)),
          borderSide: BorderSide(color: SahmiBrand.glassBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: const BorderRadius.all(Radius.circular(16)),
          borderSide: BorderSide(color: SahmiBrand.glassBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: const BorderRadius.all(Radius.circular(16)),
          borderSide: BorderSide(color: SahmiBrand.neonBull, width: 1.6),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          side: BorderSide(color: SahmiBrand.glassBorder),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          textStyle: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: isDark ? SahmiBrand.graphiteHigh : Colors.white,
        contentTextStyle: TextStyle(color: cs.onSurface),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: BorderSide(color: SahmiBrand.glassBorder),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: isDark ? SahmiBrand.deepSpace : SahmiBrand.lightScaffold,
        indicatorColor: SahmiBrand.neonBull.withValues(alpha: 0.18),
        surfaceTintColor: Colors.transparent,
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: SahmiBrand.signalGold,
        linearTrackColor: SahmiBrand.glassBorder,
        circularTrackColor: SahmiBrand.glassBorder,
      ),
      listTileTheme: ListTileThemeData(
        iconColor: cs.onSurfaceVariant,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: isDark ? SahmiBrand.carbon : Colors.white,
        surfaceTintColor: Colors.transparent,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: isDark ? SahmiBrand.carbon : Colors.white,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      ),
      datePickerTheme: DatePickerThemeData(
        backgroundColor: isDark ? SahmiBrand.carbon : Colors.white,
        surfaceTintColor: Colors.transparent,
      ),
      popupMenuTheme: PopupMenuThemeData(
        color: isDark ? SahmiBrand.carbon : Colors.white,
        surfaceTintColor: Colors.transparent,
      ),
      tabBarTheme: TabBarThemeData(
        labelColor: SahmiBrand.neonBull,
        unselectedLabelColor: cs.onSurfaceVariant,
        indicatorColor: SahmiBrand.neonBull,
        dividerColor: SahmiBrand.glassBorder,
      ),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith(
          (states) =>
              states.contains(WidgetState.selected)
                  ? SahmiBrand.signalGold
                  : cs.outline,
        ),
        trackColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.selected)
              ? SahmiBrand.signalGold.withValues(alpha: 0.4)
              : cs.surfaceContainerHighest,
        ),
      ),
    );
  }
}

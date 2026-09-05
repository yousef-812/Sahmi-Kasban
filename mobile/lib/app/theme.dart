import 'package:flutter/material.dart';

class SahmiTheme {
  const SahmiTheme._();

  static ThemeData light() {
    const seed = Color(0xFF008955);
    final scheme = ColorScheme.fromSeed(
      seedColor: seed,
      primary: const Color(0xFF008955),
      surface: Colors.white,
      surfaceContainerHighest: const Color(0xFFF1F5F2),
      onSurface: const Color(0xFF1E293B),
      onSurfaceVariant: const Color(0xFF475569),
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: const Color(0xFFF8FAFC),
      appBarTheme: const AppBarTheme(
        centerTitle: false,
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleTextStyle: TextStyle(
          color: Color(0xFF0F172A),
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 1,
        shadowColor: const Color(0x14000000),
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: const BorderRadius.all(Radius.circular(18)),
          side: BorderSide(
            color: const Color(0xFFE2E8F0),
            width: 1,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: const BorderRadius.all(Radius.circular(16)),
          borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: const BorderRadius.all(Radius.circular(16)),
          borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: const BorderRadius.all(Radius.circular(16)),
          borderSide: const BorderSide(color: Color(0xFF008955), width: 1.5),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: const Color(0xFF008955),
          foregroundColor: Colors.white,
          minimumSize: const Size.fromHeight(52),
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: Colors.white,
        elevation: 2,
        indicatorColor: const Color(0xFFE6F4EA),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Color(0xFF008955),
            );
          }
          return const TextStyle(
            fontSize: 12,
            color: Color(0xFF64748B),
          );
        }),
      ),
    );
  }

  static ThemeData dark() {
    const seed = Color(0xFF00C875);
    final scheme = ColorScheme.fromSeed(
      seedColor: seed,
      brightness: Brightness.dark,
      primary: const Color(0xFF00C875),
      surface: const Color(0xFF1E2630),
      surfaceContainerHighest: const Color(0xFF283340),
      onSurface: const Color(0xFFF8FAFC),
      onSurfaceVariant: const Color(0xFFCBD5E1),
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: const Color(0xFF13181F),
      appBarTheme: const AppBarTheme(
        centerTitle: false,
        backgroundColor: Color(0xFF1E2630),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(color: Color(0xFFF8FAFC)),
      ),
      drawerTheme: const DrawerThemeData(backgroundColor: Color(0xFF171D26)),
      dialogTheme: const DialogThemeData(backgroundColor: Color(0xFF1E2630)),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: Color(0xFF1E2630),
      ),
      cardTheme: CardThemeData(
        color: const Color(0xFF1E2630),
        elevation: 2,
        shadowColor: const Color(0x33000000),
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: const BorderRadius.all(Radius.circular(18)),
          side: const BorderSide(
            color: Color(0xFF2D3748),
            width: 1,
          ),
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        fillColor: Color(0xFF1E2630),
        filled: true,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: const Color(0xFF00C875),
          foregroundColor: const Color(0xFF0F172A),
          minimumSize: const Size.fromHeight(52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// وضع السمة الذي يختاره المستخدم من إعدادات الحساب.
enum AppThemeMode {
  system,
  light,
  dark;

  ThemeMode toMaterialThemeMode() => switch (this) {
    AppThemeMode.system => ThemeMode.system,
    AppThemeMode.light => ThemeMode.light,
    AppThemeMode.dark => ThemeMode.dark,
  };
}

/// يتحكم بوضع السمة (دارك / لايت / تلقائي).
///
/// يعتمد تلقائيًا على تفضيلات النظام في أول تشغيل، ويمكن للمستخدم تغييره من
/// إعدادات الحساب، ويُحفظ الاختيار محليًا ليبقى كما هو في المرات القادمة.
class ThemeController extends StateNotifier<AppThemeMode> {
  ThemeController() : super(AppThemeMode.system) {
    _load();
  }

  static const _key = 'app_theme_mode';

  Future<void> _load() async {
    try {
      final preferences = await SharedPreferences.getInstance();
      final stored = preferences.getString(_key);
      if (stored != null) {
        state = AppThemeMode.values.asNameMap()[stored] ?? AppThemeMode.system;
      }
    } on Object catch (error, stackTrace) {
      debugPrint('Failed to load theme mode: $error\n$stackTrace');
    }
  }

  Future<void> setMode(AppThemeMode mode) async {
    state = mode;
    try {
      final preferences = await SharedPreferences.getInstance();
      await preferences.setString(_key, mode.name);
    } on Object catch (error, stackTrace) {
      debugPrint('Failed to save theme mode: $error\n$stackTrace');
    }
  }
}

final themeControllerProvider =
    StateNotifierProvider<ThemeController, AppThemeMode>((ref) {
      return ThemeController();
    });

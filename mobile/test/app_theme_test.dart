import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sahmi_kasban_mobile/app/app_theme_provider.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('themeModeProvider defaults to ThemeMode.dark', () async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    final initialMode = container.read(themeModeProvider);
    expect(initialMode, ThemeMode.dark);
  });

  test('themeModeProvider updates state and persists choice', () async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    final notifier = container.read(themeModeProvider.notifier);
    await notifier.setThemeMode(ThemeMode.light);

    expect(container.read(themeModeProvider), ThemeMode.light);

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString('app_theme_mode'), 'light');
  });
}

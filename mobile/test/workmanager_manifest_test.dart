import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Android manifest disables eager WorkManager startup', () {
    final manifest = File(
      'android/app/src/main/AndroidManifest.xml',
    ).readAsStringSync();

    expect(
      manifest,
      contains('xmlns:tools="http://schemas.android.com/tools"'),
    );
    expect(manifest, contains('androidx.startup.InitializationProvider'));
    expect(manifest, contains('androidx.work.WorkManagerInitializer'));
    expect(manifest, contains('tools:node="remove"'));
  });
}

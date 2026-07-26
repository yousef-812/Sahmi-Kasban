import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/observability/app_observability.dart';

void main() {
  test('trace sample rate is clamped safely', () {
    expect(AppObservability.parseSampleRate('0.25'), 0.25);
    expect(AppObservability.parseSampleRate('-1'), 0.0);
    expect(AppObservability.parseSampleRate('2'), 1.0);
    expect(AppObservability.parseSampleRate('invalid'), 0.0);
  });

  testWidgets('fallback error widget is Arabic and accessible', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AppObservability.buildErrorWidget(
          FlutterErrorDetails(exception: StateError('test')),
        ),
      ),
    );

    expect(find.textContaining('حدث خطأ غير متوقع'), findsOneWidget);
    expect(
      find.bySemanticsLabel('حدث خطأ غير متوقع. حاول فتح الشاشة مرة أخرى.'),
      findsOneWidget,
    );
  });
}

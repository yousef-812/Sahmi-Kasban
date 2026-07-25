import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/avatar_assets.dart';
import 'package:sahmi_kasban_mobile/widgets/structured_data_card.dart';

void main() {
  test('generated avatar registry is complete and deterministic', () {
    expect(avatarKeys, hasLength(12));
    expect(avatarKeys.toSet(), hasLength(12));
    expect(avatarAssetPath('avatar_01'), 'assets/avatars/avatar_01.webp');
    expect(
      avatarAssetPath('unsupported'),
      'assets/avatars/avatar_01.webp',
    );
  });

  testWidgets('structured data card renders and expands JSON payload', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: StructuredDataCard(
            title: 'تفاصيل التحليل',
            data: <String, dynamic>{
              'ticker': 'COMI',
              'score': 87.5,
            },
          ),
        ),
      ),
    );

    expect(find.text('تفاصيل التحليل'), findsOneWidget);
    expect(find.textContaining('COMI'), findsOneWidget);
    expect(find.textContaining('87.5'), findsOneWidget);
  });
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_models.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_providers.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_verification_card.dart';

void main() {
  testWidgets('eligible prediction shows verification action', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          predictionVerificationStatusProvider.overrideWith((ref, id) async {
            return PredictionVerificationStatus(
              discussionId: id,
              state: 'eligible',
              eligibleAt: DateTime(2026, 7, 26, 17),
              verification: null,
            );
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PredictionVerificationCard(
              discussionId: 'discussion-eligible',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('تحقق من صحة توقعي'), findsOneWidget);
    expect(find.textContaining('انتهت فترة التوقع'), findsOneWidget);
  });

  testWidgets('waiting prediction shows eligibility date without action', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          predictionVerificationStatusProvider.overrideWith((ref, id) async {
            return PredictionVerificationStatus(
              discussionId: id,
              state: 'waiting',
              eligibleAt: DateTime(2026, 7, 30, 17),
              verification: null,
            );
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PredictionVerificationCard(
              discussionId: 'discussion-waiting',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('تحقق من صحة توقعي'), findsNothing);
    expect(find.textContaining('لم يصبح جاهزًا'), findsOneWidget);
    expect(find.textContaining('30/07/2026'), findsOneWidget);
  });

  testWidgets('verified prediction displays score reward and explanation', (
    tester,
  ) async {
    final verification = PredictionVerification(
      id: 'verification-1',
      discussionId: 'discussion-verified',
      scoreBp: 8750,
      scorePercent: 87.5,
      strength: 'very_strong',
      rewardPoints: 200,
      rewardCoins: '2.00',
      evidence: const <String, dynamic>{
        'explanation': <String, dynamic>{
          'reason': 'تحقق الاتجاه والهدف خلال الفترة المحددة.',
        },
      },
      verifiedAt: DateTime(2026, 7, 27, 17, 5),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          predictionVerificationStatusProvider.overrideWith((ref, id) async {
            return PredictionVerificationStatus(
              discussionId: id,
              state: 'verified',
              eligibleAt: DateTime(2026, 7, 27, 17),
              verification: verification,
            );
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: PredictionVerificationCard(
              discussionId: 'discussion-verified',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('قوية جدًا'), findsOneWidget);
    expect(find.textContaining('87.50%'), findsOneWidget);
    expect(find.textContaining('2.00 عملة'), findsOneWidget);
    expect(
      find.text('تحقق الاتجاه والهدف خلال الفترة المحددة.'),
      findsOneWidget,
    );
  });
}

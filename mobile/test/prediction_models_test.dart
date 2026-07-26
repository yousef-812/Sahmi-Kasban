import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_models.dart';

Map<String, dynamic> _verificationJson() {
  return <String, dynamic>{
    'id': 'verification-1',
    'discussion_id': 'discussion-1',
    'score_bp': 8750,
    'score_percent': 87.5,
    'strength': 'very_strong',
    'reward_points': 200,
    'reward_coins': '2.00',
    'evidence': <String, dynamic>{
      'explanation': <String, dynamic>{
        'source': 'ai',
        'reason': 'تحقق الاتجاه والهدف خلال الفترة المحددة.',
      },
    },
    'verified_at': '2026-07-27T17:05:00+03:00',
  };
}

void main() {
  test('parses verified prediction status and Arabic labels', () {
    final status = PredictionVerificationStatus.fromJson(<String, dynamic>{
      'discussion_id': 'discussion-1',
      'state': 'verified',
      'eligible_at': '2026-07-27T17:00:00+03:00',
      'verification': _verificationJson(),
    });

    expect(status.isVerified, isTrue);
    expect(status.verification?.strengthLabel, 'قوية جدًا');
    expect(status.verification?.rewardCoins, '2.00');
    expect(
      status.verification?.explanation,
      'تحقق الاتجاه والهدف خلال الفترة المحددة.',
    );
  });

  test('parses waiting and eligible verification states', () {
    final waiting = PredictionVerificationStatus.fromJson(<String, dynamic>{
      'discussion_id': 'discussion-2',
      'state': 'waiting',
      'eligible_at': '2026-07-30T17:00:00+03:00',
      'verification': null,
    });
    final eligible = PredictionVerificationStatus.fromJson(<String, dynamic>{
      'discussion_id': 'discussion-3',
      'state': 'eligible',
      'eligible_at': '2026-07-26T17:00:00+03:00',
      'verification': null,
    });

    expect(waiting.isWaiting, isTrue);
    expect(waiting.eligibleAt, isNotNull);
    expect(eligible.isEligible, isTrue);
  });

  test('parses verification submission wallet result', () {
    final submission = PredictionVerificationSubmission.fromJson(
      <String, dynamic>{
        'verification': _verificationJson(),
        'balance_points': 500,
        'balance_coins': '5.00',
        'idempotent': false,
      },
    );

    expect(submission.verification.scorePercent, 87.5);
    expect(submission.balancePoints, 500);
    expect(submission.idempotent, isFalse);
  });

  test('parses personal prediction statistics', () {
    final stats = PredictionStats.fromJson(<String, dynamic>{
      'verified_predictions': 8,
      'accepted_predictions': 6,
      'accuracy_percent': 75.0,
      'average_score_percent': 68.25,
      'total_reward_points': 650,
      'total_reward_coins': '6.50',
    });

    expect(stats.verifiedPredictions, 8);
    expect(stats.accuracyPercent, 75.0);
    expect(stats.totalRewardCoins, '6.50');
  });
}

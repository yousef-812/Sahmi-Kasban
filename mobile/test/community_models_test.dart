import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/community_models.dart';

Map<String, dynamic> _discussionJson({
  String status = 'published',
  String? rejectionCode,
}) {
  return <String, dynamic>{
    'id': 'discussion-1',
    'ticker': 'COMI',
    'title': 'توقع حركة سهم البنك التجاري الدولي',
    'content': 'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
    'period_type': 'next_session',
    'status': status,
    'moderation_result': <String, dynamic>{'source': 'ai'},
    'frozen_prediction': <String, dynamic>{
      'direction': 'up',
      'target_price': 145.0,
    },
    'rejection_code': rejectionCode,
    'created_at': '2026-07-26T00:15:00+03:00',
    'reviewed_at': '2026-07-26T00:16:00+03:00',
    'published_at': status == 'published'
        ? '2026-07-26T00:16:00+03:00'
        : null,
    'author': <String, dynamic>{
      'user_id': 'user-1',
      'display_name': 'مستخدم تجريبي',
      'avatar_key': 'avatar_03',
    },
  };
}

void main() {
  test('parses community discussion pagination and labels', () {
    final page = CommunityDiscussionPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[_discussionJson()],
      'total': 21,
      'limit': 20,
      'offset': 0,
    });

    expect(page.total, 21);
    expect(page.hasMore, isTrue);
    expect(page.items.single.ticker, 'COMI');
    expect(page.items.single.periodLabel, 'الجلسة القادمة');
    expect(page.items.single.statusLabel, 'منشورة');
    expect(page.items.single.frozenPrediction['direction'], 'up');
  });

  test('rejected and hidden discussions are eligible for appeal', () {
    final rejected = CommunityDiscussion.fromJson(
      _discussionJson(status: 'rejected', rejectionCode: 'off_topic'),
    );
    final hidden = CommunityDiscussion.fromJson(
      _discussionJson(status: 'hidden'),
    );

    expect(rejected.canAppeal, isTrue);
    expect(rejected.statusLabel, 'مرفوضة');
    expect(hidden.canAppeal, isTrue);
    expect(hidden.statusLabel, 'مخفية');
  });

  test('parses discussion submission wallet state', () {
    final result = CommunityDiscussionSubmission.fromJson(<String, dynamic>{
      'discussion': _discussionJson(status: 'pending_review'),
      'held_points': 50,
      'held_coins': '0.50',
      'balance_points': 250,
      'balance_coins': '2.50',
      'idempotent': false,
    });

    expect(result.discussion.status, 'pending_review');
    expect(result.heldPoints, 50);
    expect(result.balanceCoins, '2.50');
    expect(result.idempotent, isFalse);
  });

  test('parses appeals and resolution metadata', () {
    final page = CommunityAppealPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'appeal-1',
          'discussion_id': 'discussion-1',
          'user_id': 'user-1',
          'source_status': 'rejected',
          'message': 'أطلب مراجعة القرار لأن المناقشة مرتبطة مباشرة بحركة السهم.',
          'status': 'accepted',
          'created_at': '2026-07-26T00:20:00+03:00',
          'resolved_at': '2026-07-26T00:25:00+03:00',
          'resolution_reason_code': null,
          'resolution_details': <String, dynamic>{'republished': true},
        },
      ],
      'total': 1,
      'limit': 20,
      'offset': 0,
    });

    expect(page.items.single.statusLabel, 'مقبول');
    expect(page.items.single.resolutionDetails['republished'], isTrue);
  });
}

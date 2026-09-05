import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/community/community_create_screen.dart';
import 'package:sahmi_kasban_mobile/features/community/community_feed_tab.dart';
import 'package:sahmi_kasban_mobile/features/community/community_models.dart';

CommunityDiscussion _discussion() {
  return CommunityDiscussion.fromJson(<String, dynamic>{
    'id': 'discussion-1',
    'ticker': 'COMI',
    'title': 'توقع حركة سهم البنك التجاري الدولي',
    'content':
        'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
    'period_type': 'next_session',
    'status': 'published',
    'moderation_result': <String, dynamic>{},
    'frozen_prediction': <String, dynamic>{'direction': 'up'},
    'rejection_code': null,
    'created_at': '2026-07-26T00:15:00+03:00',
    'reviewed_at': '2026-07-26T00:16:00+03:00',
    'published_at': '2026-07-26T00:16:00+03:00',
    'author': <String, dynamic>{
      'user_id': 'user-1',
      'display_name': 'مستخدم تجريبي',
      'avatar_key': 'avatar_03',
    },
  });
}

void main() {
  testWidgets('community discussion card renders Arabic summary and ticker', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: CommunityDiscussionCard(
              discussion: _discussion(),
              showStatus: true,
            ),
          ),
        ),
      ),
    );

    expect(find.text('مستخدم تجريبي'), findsOneWidget);
    expect(find.text('COMI'), findsOneWidget);
    expect(find.text('الجلسة القادمة'), findsOneWidget);
    expect(find.text('منشورة'), findsOneWidget);
    await tester.pumpAndSettle();
  });

  testWidgets('discussion creation screen explains wallet hold', (
    tester,
  ) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: CommunityCreateScreen())),
    );

    expect(find.text('إنشاء مناقشة'), findsOneWidget);
    expect(find.textContaining('حجز 0.5 عملة مؤقتًا'), findsOneWidget);
    expect(find.text('اختر السهم'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -700));
    await tester.pumpAndSettle();

    expect(find.text('إرسال للمراجعة'), findsOneWidget);
  });
}

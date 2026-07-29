import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/admin/admin_models.dart';
import 'package:sahmi_kasban_mobile/features/notifications/notification_models.dart';

void main() {
  test('parses admin overview metrics', () {
    final overview = AdminOverview.fromJson(<String, dynamic>{
      'users_total': 10,
      'users_active': 8,
      'users_suspended': 2,
      'discussions_pending': 3,
      'discussions_published': 7,
      'discussions_hidden': 1,
      'open_reports': 2,
      'open_appeals': 1,
      'verified_predictions': 4,
      'wallet_points_total': 1200,
      'notifications_today': 5,
    });
    expect(overview.usersTotal, 10);
    expect(overview.openReports, 2);
  });

  test('renders administrator audit codes as Arabic text', () {
    final item = AdminAuditItem.fromJson(<String, dynamic>{
      'action': 'admin_wallet_credit',
      'reason_code': 'admin_credit',
      'details': <String, dynamic>{
        'amount_coins': 5,
        'balance_before_points': 100,
        'balance_after_points': 600,
        'request_id': 'hidden-request-id',
      },
      'created_at': '2026-07-29T17:00:00Z',
    });

    expect(item.action, 'إضافة عملات لمستخدم');
    expect(item.reasonCode, 'إضافة رصيد بواسطة الإدارة');
    expect(item.details.toString(), contains('العملات المضافة: 5'));
    expect(item.details.toString(), contains('الرصيد قبل العملية: 100'));
    expect(item.details.toString(), isNot(contains('request_id')));
    expect(item.details.toString(), isNot(contains('{')));
  });

  test('parses notification unread state', () {
    final page = NotificationPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'n1',
          'title': 'تنبيه',
          'body': 'تم نشر التقرير.',
          'category': 'report',
          'data': <String, dynamic>{},
          'read_at': null,
          'sent_at': '2026-07-26T12:00:00Z',
        },
      ],
      'total': 1,
      'unread_count': 1,
      'limit': 20,
      'offset': 0,
    });
    expect(page.items.single.isUnread, isTrue);
    expect(page.unreadCount, 1);
  });
}

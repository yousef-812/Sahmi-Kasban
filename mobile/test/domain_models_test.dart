import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';

void main() {
  group('TokenPair', () {
    test('parses the backend token response', () {
      final tokens = TokenPair.fromJson(<String, dynamic>{
        'access_token': 'access',
        'refresh_token': 'refresh',
        'expires_in': 900,
      });

      expect(tokens.accessToken, 'access');
      expect(tokens.refreshToken, 'refresh');
      expect(tokens.expiresIn, 900);
    });
  });

  group('MarketReportPreview', () {
    test('parses dates, cost, and market summary', () {
      final preview = MarketReportPreview.fromJson(<String, dynamic>{
        'report_id': '76bf2df9-aadb-45fb-b1fb-22e97fb2c9e8',
        'source_session_date': '2026-07-23',
        'target_session_date': '2026-07-26',
        'generated_at': '2026-07-23T17:05:00+03:00',
        'status': 'complete',
        'item_count': 10,
        'unlocked': false,
        'unlock_cost_points': 100,
        'unlock_cost_coins': '1.00',
        'market_summary': <String, dynamic>{'eligible_count': 26},
      });

      expect(preview.itemCount, 10);
      expect(preview.unlockCostPoints, 100);
      expect(preview.targetSessionDate.day, 26);
      expect(preview.marketSummary['eligible_count'], 26);
    });
  });

  test('RegistrationResult keeps the free weekly grant default', () {
    final result = RegistrationResult.fromJson(<String, dynamic>{
      'user_id': '02140ff6-c9a2-45ef-892f-bd8b5713dd9d',
      'email': 'user@example.com',
      'requires_email_verification': true,
    });

    expect(result.requiresEmailVerification, isTrue);
    expect(result.weeklyPointsGranted, 300);
  });
}

import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/monetization/monetization_models.dart';

void main() {
  test('catalog exposes only server-defined store product IDs', () {
    final catalog = MonetizationCatalog.fromJson(<String, dynamic>{
      'plans': <Map<String, dynamic>>[
        <String, dynamic>{
          'code': 'free',
          'display_name_ar': 'المجانية',
          'weekly_points': 300,
          'weekly_coins': '3.00',
          'ads_enabled': true,
          'product_id': null,
          'history_limit': 20,
          'report_history_days': 1,
          'badge_code': null,
        },
        <String, dynamic>{
          'code': 'basic',
          'display_name_ar': 'الأساسية',
          'weekly_points': 1000,
          'weekly_coins': '10.00',
          'ads_enabled': false,
          'product_id': 'sahmi_basic_monthly',
          'history_limit': 100,
          'report_history_days': 30,
          'badge_code': 'basic',
        },
      ],
      'coin_packs': <Map<String, dynamic>>[
        <String, dynamic>{
          'product_id': 'sahmi_coins_5',
          'display_name_ar': '5 عملات',
          'points': 500,
          'coins': '5.00',
        },
      ],
      'ad_reward_points': 75,
      'ad_reward_coins': '0.75',
      'ad_reward_daily_limit': 4,
      'ad_reward_cooldown_seconds': 900,
    });

    expect(catalog.storeProductIds, <String>{
      'sahmi_basic_monthly',
      'sahmi_coins_5',
    });
    expect(catalog.isCoinPack('sahmi_coins_5'), isTrue);
    expect(catalog.isCoinPack('sahmi_basic_monthly'), isFalse);
    expect(catalog.adRewardPoints, 75);
  });

  test('rewarded session distinguishes development SSV simulation', () {
    final session = RewardedAdSessionModel.fromJson(<String, dynamic>{
      'session_id': '4f6c5633-e3af-4f30-a8dd-a0e6fb38ecb4',
      'ad_unit_id': 'ca-app-pub-test/rewarded',
      'custom_data': 'server-issued-random-value',
      'expires_at': '2026-07-25T19:00:00Z',
      'test_mode': true,
    });

    expect(session.testMode, isTrue);
    expect(session.customData, 'server-issued-random-value');
    expect(session.expiresAt.isUtc, isTrue);
  });

  test('purchase verification result keeps server entitlement decision', () {
    final result = PurchaseVerificationResultModel.fromJson(<String, dynamic>{
      'purchase_id': '28f87fb5-081b-4a13-8f30-c24bdbd73752',
      'product_id': 'sahmi_coins_5',
      'product_type': 'coins',
      'purchase_state': 'purchased',
      'acknowledgement_state': 'acknowledged',
      'entitlement_granted': true,
      'idempotent': false,
      'plan_code': 'free',
      'balance_points': 800,
      'balance_coins': '8.00',
      'subscription_expires_at': null,
    });

    expect(result.entitlementGranted, isTrue);
    expect(result.idempotent, isFalse);
    expect(result.balancePoints, 800);
  });
}

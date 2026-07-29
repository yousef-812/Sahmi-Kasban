import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/market/stock_comparison_models.dart';
import 'package:sahmi_kasban_mobile/features/monetization/free_plan_ads.dart';

void main() {
  group('InterstitialFrequencyPolicy', () {
    const policy = InterstitialFrequencyPolicy(
      actionsPerAd: 3,
      minimumInterval: Duration(minutes: 4),
    );
    final now = DateTime(2026, 7, 29, 8);

    test('requires enough meaningful actions', () {
      expect(
        policy.canShow(
          meaningfulActions: 2,
          now: now,
          lastShownAt: null,
        ),
        isFalse,
      );
      expect(
        policy.canShow(
          meaningfulActions: 3,
          now: now,
          lastShownAt: null,
        ),
        isTrue,
      );
    });

    test('enforces the minimum interval after an impression', () {
      expect(
        policy.canShow(
          meaningfulActions: 3,
          now: now,
          lastShownAt: now.subtract(const Duration(minutes: 3)),
        ),
        isFalse,
      );
      expect(
        policy.canShow(
          meaningfulActions: 3,
          now: now,
          lastShownAt: now.subtract(const Duration(minutes: 4)),
        ),
        isTrue,
      );
    });
  });

  test('StockComparisonResult parses server-authoritative costs and ranking', () {
    final result = StockComparisonResult.fromJson(<String, dynamic>{
      'comparison_id': 'comparison-id',
      'request_key': 'comparison_test_001',
      'tickers': <String>['COMI', 'DSCW'],
      'best_ticker': 'COMI',
      'summary': 'COMI حصل على أعلى تقييم مقارن.',
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'rank': 1,
          'ticker': 'COMI',
          'analysis_id': 'analysis-id',
          'data_as_of': '2026-07-28T12:00:00Z',
          'signal': 'BUY',
          'final_score': 82.5,
          'confidence': 77,
          'comparison_score': 80.1,
          'trend': 'bullish',
          'rsi': 58.2,
          'average_volume_20': 1200000,
          'risk_level': 'medium',
          'risk_score': 71,
          'entry': 75.1,
          'stop_loss': 71.8,
          'target_1': 80.4,
          'target_2': 84.2,
          'reward_risk_1': 1.6,
        },
      ],
      'included_allowance': false,
      'comparison_charged_points': 50,
      'comparison_charged_coins': '0.50',
      'analysis_charged_points': 100,
      'analysis_charged_coins': '1.00',
      'allowance_used': 0,
      'allowance_remaining': 0,
      'idempotent': false,
      'balance_points': 850,
      'balance_coins': '8.50',
      'disclaimer': 'ليست توصية شراء أو بيع.',
    });

    expect(result.bestTicker, 'COMI');
    expect(result.comparisonChargedPoints, 50);
    expect(result.analysisChargedPoints, 100);
    expect(result.balanceCoins, '8.50');
    expect(result.items.single.rank, 1);
    expect(result.items.single.comparisonScore, 80.1);
  });
}

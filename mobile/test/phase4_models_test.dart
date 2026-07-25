import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';

void main() {
  test('parses paginated wallet history', () {
    final page = WalletHistoryPage.fromJson(<String, dynamic>{
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'transaction_id': 'txn-1',
          'entry_type': 'debit',
          'amount_points': -50,
          'amount_coins': '-0.50',
          'status': 'confirmed',
          'reference_type': 'stock_analysis',
          'reference_id': 'analysis-1',
          'details': <String, dynamic>{'ticker': 'COMI'},
          'created_at': '2026-07-25T17:00:00Z',
          'confirmed_at': '2026-07-25T17:00:01Z',
        },
      ],
      'total': 21,
      'limit': 20,
      'offset': 0,
    });

    expect(page.total, 21);
    expect(page.items.single.amountPoints, -50);
    expect(page.items.single.details['ticker'], 'COMI');
  });

  test('parses paid analysis result and cached billing state', () {
    final result = StockAnalysisResult.fromJson(<String, dynamic>{
      'analysis_id': 'analysis-1',
      'ticker': 'COMI',
      'cached': true,
      'market_snapshot_cached': true,
      'charged_points': 0,
      'charged_coins': '0.00',
      'balance_points': 250,
      'balance_coins': '2.50',
      'data_as_of': '2026-07-25T14:00:00Z',
      'payload': <String, dynamic>{'decision': 'WATCH'},
    });

    expect(result.cached, isTrue);
    expect(result.chargedPoints, 0);
    expect(result.payload['decision'], 'WATCH');
  });

  test('parses unlocked Top 10 report and ranked items', () {
    final report = MarketReport.fromJson(<String, dynamic>{
      'report_id': 'report-1',
      'source_session_date': '2026-07-24',
      'target_session_date': '2026-07-26',
      'generated_at': '2026-07-24T17:00:00+03:00',
      'market_summary': <String, dynamic>{'eligible_count': 34},
      'items': <Map<String, dynamic>>[
        <String, dynamic>{
          'ticker': 'COMI',
          'rank': 1,
          'score': 87.35,
          'payload': <String, dynamic>{'reason': 'momentum'},
        },
      ],
    });

    expect(report.items.single.rank, 1);
    expect(report.items.single.score, closeTo(87.35, 0.001));
    expect(report.marketSummary['eligible_count'], 34);
  });

  test('avatar options use generated WebP assets', () {
    final option = AvatarOption.fromJson(<String, dynamic>{
      'key': 'avatar_12',
      'asset_path': 'assets/avatars/avatar_12.webp',
    });

    expect(option.key, 'avatar_12');
    expect(option.assetPath, endsWith('.webp'));
  });
}

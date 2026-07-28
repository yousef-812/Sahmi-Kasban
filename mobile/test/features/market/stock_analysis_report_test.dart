import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';
import 'package:sahmi_kasban_mobile/features/market/stock_analysis_report.dart';

void main() {
  testWidgets('renders Arabic analysis cards without locale initialization', (
    tester,
  ) async {
    final analysis = StockAnalysisResult(
      analysisId: 'analysis-1',
      ticker: 'DSCW',
      cached: false,
      marketSnapshotCached: false,
      chargedPoints: 50,
      chargedCoins: '0.50',
      balancePoints: 250,
      balanceCoins: '2.50',
      dataAsOf: DateTime.utc(2026, 7, 28, 7),
      payload: {
        'market_data': {
          'provider': 'tradingview',
          'interval': '1d',
          'period': '1y',
          'candle_count': 300,
        },
        'analysis': {
          'signal': 'BUY',
          'final_score': 82.11,
          'confidence': 84.73,
          'trade_plan': {
            'entry': 1.97,
            'stop_loss': 1.8778,
            'target_1': 2.1545,
            'target_2': 2.2929,
            'reward_risk_1': 2.0,
            'reward_risk_2': 3.5,
          },
          'engines': {
            'technical': {
              'score': 99.0,
              'confidence': 94.3,
              'details': {'trend': 'uptrend', 'close': 1.97, 'rsi': 67.52},
            },
            'risk': {
              'score': 83.79,
              'confidence': 88.0,
              'details': {'risk_level': 'low', 'total_risk_pct': 16.21},
            },
            'scenario': {
              'score': 69.45,
              'confidence': 75.0,
              'details': {
                'bullish': {'probability_pct': 52.22, 'target': 2.2929},
                'base': {'probability_pct': 34.44, 'target': 2.1545},
                'bearish': {'probability_pct': 13.33, 'target': 1.8778},
              },
            },
          },
          'warnings': <String>[],
        },
        'explanation': 'نتيجة المحركات: شراء مشروط.',
        'disclaimer': 'هذا تحليل آلي لدعم القرار وليس توصية شراء أو بيع.',
      },
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: StockAnalysisReport(analysis: analysis),
          ),
        ),
      ),
    );

    expect(tester.takeException(), isNull);
    expect(find.text('القرار الآلي: شراء مشروط'), findsOneWidget);
    expect(find.text('خطة التداول الافتراضية'), findsOneWidget);
    expect(find.text('الملخص الفني'), findsOneWidget);
    expect(find.text('السيناريوهات المحتملة'), findsOneWidget);
    expect(find.text('البيانات التقنية الخام'), findsNothing);
    expect(find.textContaining('"market_data"'), findsNothing);
  });
}

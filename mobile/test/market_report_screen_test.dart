import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/data/backend_repository.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';
import 'package:sahmi_kasban_mobile/features/reports/market_report_screen.dart';

class _MockBackendRepository extends Mock implements BackendRepository {}

void main() {
  testWidgets('Top 10 report renders Arabic cards without intl locale setup', (
    tester,
  ) async {
    final repository = _MockBackendRepository();
    final report = MarketReport(
      reportId: 'report-1',
      sourceSessionDate: DateTime.utc(2026, 7, 28),
      targetSessionDate: DateTime.utc(2026, 7, 29),
      generatedAt: DateTime.utc(2026, 7, 28, 17),
      marketSummary: const <String, dynamic>{
        'title': 'الأسهم الأعلى تقييمًا للجلسة القادمة',
        'analyzed_count': 180,
        'eligible_count': 24,
        'failed_count': 2,
        'average_top_score': 81.5,
        'signals': <String, dynamic>{'BUY': 7, 'WATCH': 3},
        'disclaimer': 'تحليل آلي وليس توصية استثمارية.',
      },
      items: <MarketReportItem>[
        MarketReportItem(
          ticker: 'COMI',
          rank: 1,
          score: 88.4,
          payload: const <String, dynamic>{
            'decision': 'فرصة قوية',
            'confidence': 91.2,
            'price_at_analysis': 82.5,
            'explanation': 'الاتجاه والسيولة يدعمان المراقبة الإيجابية.',
            'analysis': <String, dynamic>{
              'trade_plan': <String, dynamic>{
                'entry': 82.5,
                'stop_loss': 79.0,
                'target_1': 89.5,
                'target_2': 94.0,
                'reward_risk_1': 2.0,
              },
              'engines': <String, dynamic>{
                'technical': <String, dynamic>{
                  'details': <String, dynamic>{
                    'trend': 'uptrend',
                    'rsi': 61.0,
                    'volume_ratio': 1.4,
                  },
                  'reasons': <String>['Price above SMA20'],
                },
                'risk': <String, dynamic>{
                  'details': <String, dynamic>{'risk_level': 'low'},
                  'reasons': <String>[],
                },
              },
            },
          },
        ),
      ],
    );
    when(
      () => repository.getMarketReport('report-1'),
    ).thenAnswer((_) async => report);

    await tester.pumpWidget(
      ProviderScope(
        overrides: <Override>[
          backendRepositoryProvider.overrideWithValue(repository),
        ],
        child: const MaterialApp(
          home: MarketReportScreen(reportId: 'report-1'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('الأربعاء 29 يوليو 2026'), findsOneWidget);
    expect(find.text('ملخص السوق'), findsOneWidget);
    expect(find.text('COMI'), findsOneWidget);
    expect(find.text('خطة التداول'), findsOneWidget);
    expect(find.textContaining('السعر أعلى من متوسط 20 جلسة'), findsOneWidget);
    expect(find.textContaining('{'), findsNothing);
    expect(tester.takeException(), isNull);
  });
}

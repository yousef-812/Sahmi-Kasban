import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/performance/performance_models.dart';

void main() {
  test('parses transparent performance summary with negative results', () {
    final summary = PerformanceSummary.fromJson(<String, dynamic>{
      'window_sessions': 7,
      'sessions_found': 3,
      'complete_sessions': 2,
      'total_items': 30,
      'evaluated_items': 27,
      'pending_items': 2,
      'failed_items': 1,
      'data_completeness_pct': 90.0,
      'positive_count': 12,
      'negative_count': 14,
      'flat_count': 1,
      'average_return_bp': -25,
      'median_return_bp': -10,
      'positive_rate_pct': 44.44,
      'direction_accuracy_pct': 48.15,
      'target_one_hit_rate_pct': 20.0,
      'target_two_hit_rate_pct': 5.0,
      'stop_loss_hit_rate_pct': 30.0,
      'best_outcome': <String, dynamic>{
        'report_id': 'r1',
        'target_session_date': '2026-07-20',
        'ticker': 'COMI',
        'rank': 1,
        'return_bp': 450,
      },
      'worst_outcome': <String, dynamic>{
        'report_id': 'r2',
        'target_session_date': '2026-07-21',
        'ticker': 'SWDY',
        'rank': 4,
        'return_bp': -700,
      },
      'ranks': <Map<String, dynamic>>[
        <String, dynamic>{
          'rank': 1,
          'evaluated_items': 3,
          'average_return_bp': 100,
          'median_return_bp': 80,
          'positive_rate_pct': 66.67,
          'direction_accuracy_pct': 66.67,
          'target_one_hit_rate_pct': 33.33,
          'stop_loss_hit_rate_pct': 0.0,
        },
      ],
      'sessions': <Map<String, dynamic>>[],
      'benchmark': <String, dynamic>{'status': 'not_available'},
      'negative_results_retained': true,
    });

    expect(summary.negativeCount, 14);
    expect(summary.averageReturnBp, -25);
    expect(summary.worstOutcome?.returnBp, -700);
    expect(summary.dataCompletenessPct, 90);
    expect(summary.negativeResultsRetained, isTrue);
  });

  test('parses pending outcome and audited revision', () {
    final detail = PerformanceReportDetail.fromJson(<String, dynamic>{
      'report_id': 'r1',
      'target_session_date': '2026-07-20',
      'generated_at': '2026-07-19T15:00:00Z',
      'evaluation_status': 'partial',
      'session': <String, dynamic>{
        'report_id': 'r1',
        'target_session_date': '2026-07-20',
        'evaluation_status': 'partial',
        'total_items': 2,
        'evaluated_items': 1,
        'pending_items': 1,
        'failed_items': 0,
        'data_completeness_pct': 50.0,
        'average_return_bp': -200,
        'positive_count': 0,
        'negative_count': 1,
        'direction_accuracy_pct': 0.0,
        'target_one_hit_rate_pct': 0.0,
        'stop_loss_hit_rate_pct': 0.0,
      },
      'outcomes': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'o1',
          'ticker': 'COMI',
          'rank': 1,
          'status': 'pending_data',
          'expected_direction': 'up',
          'price_at_analysis': 100.0,
          'session_open': null,
          'session_high': null,
          'session_low': null,
          'session_close': null,
          'return_bp': null,
          'max_upside_bp': null,
          'max_drawdown_bp': null,
          'direction_correct': null,
          'target_one': 105.0,
          'target_two': 110.0,
          'stop_loss': 95.0,
          'target_one_hit': null,
          'target_two_hit': null,
          'stop_loss_hit': null,
          'provider': null,
          'data_as_of': null,
          'evaluated_at': null,
          'evaluator_version': 'report-performance-v1',
          'evidence': <String, dynamic>{
            'reason': 'target_session_candle_missing',
          },
          'correction_count': 1,
        },
      ],
      'revisions': <Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'rev1',
          'revision_number': 1,
          'reason': 'Official correction',
          'before_payload': <String, dynamic>{'status': 'pending_data'},
          'after_payload': <String, dynamic>{'status': 'complete'},
          'created_at': '2026-07-21T15:10:00Z',
        },
      ],
      'negative_results_retained': true,
    });

    expect(detail.outcomes.single.isComplete, isFalse);
    expect(detail.outcomes.single.evidence['reason'],
        'target_session_candle_missing');
    expect(detail.revisions.single.revisionNumber, 1);
  });
}

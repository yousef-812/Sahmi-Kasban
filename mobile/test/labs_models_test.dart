import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/labs/labs_models.dart';

void main() {
  group('LabsBacktestResult', () {
    test('parses a full response payload', () {
      final result = LabsBacktestResult.fromJson({
        'params': {
          'start_date': '2026-07-07',
          'end_date': '2026-07-28',
          'rank': 3,
          'exit_mode': 'target_2',
          'track_interval_minutes': 10,
          'source_interval': '5m',
        },
        'summary': {
          'reports_scanned': 3,
          'trades': 3,
          'hits': 2,
          'misses': 1,
          'skipped': 1,
          'hit_rate_pct': 66.67,
          'avg_return_pct': 1.9,
          'median_return_pct': 2.1,
          'avg_hit_return_pct': 5.4,
          'avg_miss_return_pct': -3.6,
          'median_minutes_to_hit': 35.0,
          'best_return_pct': 7.1,
          'worst_return_pct': -3.6,
          'cumulative_return_pct': 5.7,
        },
        'sessions': [
          {
            'target_session_date': '2026-07-28',
            'report_id': 'r-1',
            'rank': 3,
            'ticker': 'HRHO',
            'score': 81.5,
            'price_at_analysis': 12.4,
            'targets': [13.0, 14.2],
            'stop_loss': 11.8,
            'session_open': 12.5,
            'exit_price': 14.2,
            'exit_reason': 'target',
            'hit': true,
            'minutes_to_exit': 40,
            'return_pct': 13.6,
            'tracked': [
              {'time': '10:05', 'price': 12.6, 'high': 12.7, 'low': 12.5},
              {'time': '10:15', 'price': 13.2, 'high': 14.2, 'low': 13.0},
            ],
          },
          {
            'target_session_date': '2026-07-27',
            'report_id': 'r-1',
            'rank': 3,
            'ticker': 'HRHO',
            'score': 81.5,
            'price_at_analysis': null,
            'targets': <Object>[],
            'stop_loss': null,
            'session_open': null,
            'exit_price': null,
            'exit_reason': 'skipped',
            'hit': false,
            'minutes_to_exit': null,
            'return_pct': null,
            'tracked': <Object>[],
          },
        ],
        'meta': {'requested_by': 'user-1'},
      });

      expect(result.params.rank, 3);
      expect(result.params.exitMode, 'target_2');
      expect(result.params.trackIntervalMinutes, 10);
      expect(result.summary.hits, 2);
      expect(result.summary.hitRatePct, closeTo(66.67, 0.001));
      expect(result.summary.medianMinutesToHit, 35.0);
      expect(result.sessions, hasLength(2));

      final trade = result.sessions.first;
      expect(trade.ticker, 'HRHO');
      expect(trade.hit, isTrue);
      expect(trade.exitReason, 'target');
      expect(trade.minutesToExit, 40);
      expect(trade.returnPct, closeTo(13.6, 0.001));
      expect(trade.tracked, hasLength(2));
      expect(trade.tracked.first.time, '10:05');
      expect(trade.targets, [13.0, 14.2]);

      final skipped = result.sessions[1];
      expect(skipped.hit, isFalse);
      expect(skipped.exitReason, 'skipped');
      expect(skipped.returnPct, isNull);
      expect(skipped.tracked, isEmpty);
    });

    test('handles missing optional fields gracefully', () {
      final result = LabsBacktestResult.fromJson({
        'params': {
          'start_date': '2026-07-07',
          'end_date': '2026-07-28',
          'rank': null,
          'exit_mode': 'highest',
        },
        'summary': {'trades': 0},
        'sessions': null,
        'meta': <Object>{},
      });

      expect(result.params.rank, isNull);
      expect(result.params.exitMode, 'highest');
      expect(result.summary.trades, 0);
      expect(result.summary.hitRatePct, 0);
      expect(result.sessions, isEmpty);
    });
  });

  group('LabsBacktestQuery', () {
    test('value equality drives provider identity', () {
      final a = LabsBacktestQuery(
        startDate: DateTime(2026, 7, 7),
        endDate: DateTime(2026, 7, 28),
        rank: 1,
        exitMode: 'target_2',
      );
      final b = LabsBacktestQuery(
        startDate: DateTime(2026, 7, 7),
        endDate: DateTime(2026, 7, 28),
        rank: 1,
        exitMode: 'target_2',
      );
      final c = LabsBacktestQuery(
        startDate: DateTime(2026, 7, 7),
        endDate: DateTime(2026, 7, 28),
        rank: 2,
        exitMode: 'target_2',
      );

      expect(a, b);
      expect(a.hashCode, b.hashCode);
      expect(a == c, isFalse);
    });
  });

  group('LabsBacktestJob', () {
    test('parses a queued job without a result', () {
      final job = LabsBacktestJob.fromJson({
        'id': 'job-1',
        'status': 'queued',
        'start_date': '2026-07-07',
        'end_date': '2026-07-28',
        'rank': null,
        'exit_mode': 'target_2',
        'created_at': '2026-08-01T10:00:00Z',
      });

      expect(job.id, 'job-1');
      expect(job.status, 'queued');
      expect(job.isActive, isTrue);
      expect(job.summary, isNull);
      expect(job.sessions, isEmpty);
      expect(job.errorMessage, isNull);
    });

    test('parses a completed job with summary and sessions', () {
      final job = LabsBacktestJob.fromJson({
        'id': 'job-2',
        'status': 'complete',
        'start_date': '2026-07-07',
        'end_date': '2026-07-28',
        'rank': 2,
        'exit_mode': 'highest',
        'params': {
          'start_date': '2026-07-07',
          'end_date': '2026-07-28',
          'rank': 2,
          'exit_mode': 'highest',
          'track_interval_minutes': 10,
          'source_interval': '5m',
        },
        'summary': {
          'reports_scanned': 1,
          'trades': 1,
          'hits': 1,
          'misses': 0,
          'skipped': 0,
          'hit_rate_pct': 100.0,
        },
        'sessions': [
          {
            'target_session_date': '2026-07-28',
            'report_id': 'r-1',
            'rank': 2,
            'ticker': 'COMI',
            'score': 80.0,
            'price_at_analysis': 12.4,
            'targets': [13.0],
            'stop_loss': 11.8,
            'session_open': 12.5,
            'exit_price': 13.0,
            'exit_reason': 'target',
            'hit': true,
            'minutes_to_exit': 40,
            'return_pct': 4.0,
            'tracked': <Object>[],
          },
        ],
        'error_message': null,
        'started_at': '2026-08-01T10:00:00Z',
        'completed_at': '2026-08-01T10:02:00Z',
        'created_at': '2026-08-01T10:00:00Z',
      });

      expect(job.status, 'complete');
      expect(job.isActive, isFalse);
      expect(job.params?.exitMode, 'highest');
      expect(job.summary?.trades, 1);
      expect(job.summary?.hitRatePct, closeTo(100.0, 0.001));
      expect(job.sessions, hasLength(1));
      expect(job.sessions.first.ticker, 'COMI');
      expect(job.sessions.first.hit, isTrue);
      expect(job.completedAt, isNotNull);
    });

    test('parses a failed job with an error message', () {
      final job = LabsBacktestJob.fromJson({
        'id': 'job-3',
        'status': 'failed',
        'start_date': '2026-07-07',
        'end_date': '2026-07-28',
        'rank': null,
        'exit_mode': 'target_2',
        'error_message': 'نطاق أكبر من المسموح',
        'created_at': '2026-08-01T10:00:00Z',
      });

      expect(job.status, 'failed');
      expect(job.isActive, isFalse);
      expect(job.errorMessage, 'نطاق أكبر من المسموح');
    });
  });
}

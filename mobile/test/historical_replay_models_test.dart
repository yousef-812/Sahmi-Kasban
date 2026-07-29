import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/admin/historical_replay_models.dart';

void main() {
  test('parses account replay progress and download availability', () {
    final job = HistoricalReplayJob.fromJson(<String, dynamic>{
      'id': 'job-1',
      'engine_version': 'core-v2',
      'status': 'partial',
      'start_date': '2026-06-01',
      'end_date': '2026-06-30',
      'horizon_sessions': 5,
      'parallelism': 5,
      'total_tickers': 155,
      'processed_tickers': 155,
      'successful_tickers': 150,
      'failed_tickers': 5,
      'total_rows': 3200,
      'evaluated_rows': 2900,
      'pending_rows': 300,
      'progress_pct': 100,
      'download_ready': true,
      'created_at': '2026-07-29T18:00:00Z',
      'completed_at': '2026-07-29T19:00:00Z',
      'tickers': <Map<String, dynamic>>[
        <String, dynamic>{
          'ticker': 'COMI',
          'status': 'complete',
          'provider': 'tradingview',
          'rows_written': 22,
          'evaluated_rows': 20,
          'pending_rows': 2,
          'failed_rows': 0,
        },
      ],
    });

    expect(job.parallelism, 5);
    expect(job.downloadReady, isTrue);
    expect(job.progressPct, 100);
    expect(job.tickers.single.ticker, 'COMI');
    expect(job.tickers.single.pendingRows, 2);
  });
}

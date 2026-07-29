class HistoricalReplayTicker {
  const HistoricalReplayTicker({
    required this.ticker,
    required this.status,
    required this.rowsWritten,
    required this.evaluatedRows,
    required this.pendingRows,
    required this.failedRows,
    this.provider,
    this.errorMessage,
  });

  factory HistoricalReplayTicker.fromJson(Map<String, dynamic> json) {
    return HistoricalReplayTicker(
      ticker: json['ticker'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      provider: json['provider'] as String?,
      rowsWritten: (json['rows_written'] as num?)?.toInt() ?? 0,
      evaluatedRows: (json['evaluated_rows'] as num?)?.toInt() ?? 0,
      pendingRows: (json['pending_rows'] as num?)?.toInt() ?? 0,
      failedRows: (json['failed_rows'] as num?)?.toInt() ?? 0,
      errorMessage: json['error_message'] as String?,
    );
  }

  final String ticker;
  final String status;
  final String? provider;
  final int rowsWritten;
  final int evaluatedRows;
  final int pendingRows;
  final int failedRows;
  final String? errorMessage;
}

class HistoricalReplayJob {
  const HistoricalReplayJob({
    required this.id,
    required this.engineVersion,
    required this.status,
    required this.startDate,
    required this.endDate,
    required this.horizonSessions,
    required this.parallelism,
    required this.totalTickers,
    required this.processedTickers,
    required this.successfulTickers,
    required this.failedTickers,
    required this.totalRows,
    required this.evaluatedRows,
    required this.pendingRows,
    required this.progressPct,
    required this.downloadReady,
    required this.createdAt,
    this.completedAt,
    this.errorMessage,
    this.tickers = const <HistoricalReplayTicker>[],
  });

  factory HistoricalReplayJob.fromJson(Map<String, dynamic> json) {
    final rawTickers = json['tickers'];
    return HistoricalReplayJob(
      id: json['id'] as String? ?? '',
      engineVersion: json['engine_version'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      horizonSessions: (json['horizon_sessions'] as num?)?.toInt() ?? 5,
      parallelism: (json['parallelism'] as num?)?.toInt() ?? 5,
      totalTickers: (json['total_tickers'] as num?)?.toInt() ?? 0,
      processedTickers: (json['processed_tickers'] as num?)?.toInt() ?? 0,
      successfulTickers:
          (json['successful_tickers'] as num?)?.toInt() ?? 0,
      failedTickers: (json['failed_tickers'] as num?)?.toInt() ?? 0,
      totalRows: (json['total_rows'] as num?)?.toInt() ?? 0,
      evaluatedRows: (json['evaluated_rows'] as num?)?.toInt() ?? 0,
      pendingRows: (json['pending_rows'] as num?)?.toInt() ?? 0,
      progressPct: (json['progress_pct'] as num?)?.toDouble() ?? 0,
      downloadReady: json['download_ready'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      completedAt: json['completed_at'] == null
          ? null
          : DateTime.parse(json['completed_at'] as String),
      errorMessage: json['error_message'] as String?,
      tickers: rawTickers is List
          ? rawTickers
                .whereType<Map>()
                .map(
                  (item) => HistoricalReplayTicker.fromJson(
                    Map<String, dynamic>.from(item),
                  ),
                )
                .toList(growable: false)
          : const <HistoricalReplayTicker>[],
    );
  }

  final String id;
  final String engineVersion;
  final String status;
  final DateTime startDate;
  final DateTime endDate;
  final int horizonSessions;
  final int parallelism;
  final int totalTickers;
  final int processedTickers;
  final int successfulTickers;
  final int failedTickers;
  final int totalRows;
  final int evaluatedRows;
  final int pendingRows;
  final double progressPct;
  final bool downloadReady;
  final DateTime createdAt;
  final DateTime? completedAt;
  final String? errorMessage;
  final List<HistoricalReplayTicker> tickers;

  bool get isActive => status == 'pending' || status == 'running';
}

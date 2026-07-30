class HistoricalReplayWindow {
  const HistoricalReplayWindow({
    required this.startDate,
    required this.endDate,
  });

  final DateTime startDate;
  final DateTime endDate;

  Map<String, dynamic> toJson() => <String, dynamic>{
    'start_date': _dateOnly(startDate),
    'end_date': _dateOnly(endDate),
  };

  static String _dateOnly(DateTime value) {
    return '${value.year.toString().padLeft(4, '0')}-'
        '${value.month.toString().padLeft(2, '0')}-'
        '${value.day.toString().padLeft(2, '0')}';
  }
}

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
    this.controlState = 'pending',
    this.workerIsolated = false,
    this.canPause = false,
    this.canResume = false,
    this.canCancel = false,
    this.throughputTickersPerMinute,
    this.estimatedSecondsRemaining,
    this.startedAt,
    this.heartbeatAt,
    this.completedAt,
    this.errorMessage,
    this.tickers = const <HistoricalReplayTicker>[],
  });

  factory HistoricalReplayJob.fromJson(Map<String, dynamic> json) {
    final rawTickers = json['tickers'];
    final status = json['status'] as String? ?? 'pending';
    return HistoricalReplayJob(
      id: json['id'] as String? ?? '',
      engineVersion: json['engine_version'] as String? ?? '',
      status: status,
      controlState: json['control_state'] as String? ?? status,
      workerIsolated: json['worker_isolated'] as bool? ?? false,
      canPause: json['can_pause'] as bool? ?? false,
      canResume: json['can_resume'] as bool? ?? false,
      canCancel: json['can_cancel'] as bool? ?? false,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      horizonSessions: (json['horizon_sessions'] as num?)?.toInt() ?? 5,
      parallelism: (json['parallelism'] as num?)?.toInt() ?? 5,
      totalTickers: (json['total_tickers'] as num?)?.toInt() ?? 0,
      processedTickers: (json['processed_tickers'] as num?)?.toInt() ?? 0,
      successfulTickers: (json['successful_tickers'] as num?)?.toInt() ?? 0,
      failedTickers: (json['failed_tickers'] as num?)?.toInt() ?? 0,
      totalRows: (json['total_rows'] as num?)?.toInt() ?? 0,
      evaluatedRows: (json['evaluated_rows'] as num?)?.toInt() ?? 0,
      pendingRows: (json['pending_rows'] as num?)?.toInt() ?? 0,
      progressPct: (json['progress_pct'] as num?)?.toDouble() ?? 0,
      throughputTickersPerMinute:
          (json['throughput_tickers_per_minute'] as num?)?.toDouble(),
      estimatedSecondsRemaining:
          (json['estimated_seconds_remaining'] as num?)?.toInt(),
      downloadReady: json['download_ready'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      startedAt: _optionalDateTime(json['started_at']),
      heartbeatAt: _optionalDateTime(json['heartbeat_at']),
      completedAt: _optionalDateTime(json['completed_at']),
      errorMessage: json['error_message'] as String?,
      tickers: rawTickers is List
          ? rawTickers
                .whereType<Map<String, dynamic>>()
                .map(HistoricalReplayTicker.fromJson)
                .toList(growable: false)
          : const <HistoricalReplayTicker>[],
    );
  }

  final String id;
  final String engineVersion;
  final String status;
  final String controlState;
  final bool workerIsolated;
  final bool canPause;
  final bool canResume;
  final bool canCancel;
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
  final double? throughputTickersPerMinute;
  final int? estimatedSecondsRemaining;
  final bool downloadReady;
  final DateTime createdAt;
  final DateTime? startedAt;
  final DateTime? heartbeatAt;
  final DateTime? completedAt;
  final String? errorMessage;
  final List<HistoricalReplayTicker> tickers;

  bool get isActive => status == 'pending' || status == 'running';
  bool get isPaused => controlState == 'paused';
  bool get isCancelled => controlState == 'cancelled';
}

DateTime? _optionalDateTime(Object? value) {
  if (value is! String || value.isEmpty) return null;
  return DateTime.tryParse(value);
}

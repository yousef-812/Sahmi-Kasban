class LabsBacktestParams {
  const LabsBacktestParams({
    required this.startDate,
    required this.endDate,
    required this.rank,
    required this.exitMode,
    required this.trackIntervalMinutes,
    required this.sourceInterval,
  });

  final DateTime startDate;
  final DateTime endDate;
  final int? rank;
  final String exitMode;
  final int trackIntervalMinutes;
  final String sourceInterval;

  factory LabsBacktestParams.fromJson(Map<String, dynamic> json) {
    return LabsBacktestParams(
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      rank: json['rank'] as int?,
      exitMode: json['exit_mode'] as String,
      trackIntervalMinutes: json['track_interval_minutes'] as int? ?? 10,
      sourceInterval: json['source_interval'] as String? ?? '5m',
    );
  }
}

class LabsBacktestSummary {
  const LabsBacktestSummary({
    required this.reportsScanned,
    required this.trades,
    required this.hits,
    required this.misses,
    required this.skipped,
    required this.hitRatePct,
    required this.avgReturnPct,
    required this.medianReturnPct,
    required this.avgHitReturnPct,
    required this.avgMissReturnPct,
    required this.medianMinutesToHit,
    required this.bestReturnPct,
    required this.worstReturnPct,
    required this.cumulativeReturnPct,
  });

  final int reportsScanned;
  final int trades;
  final int hits;
  final int misses;
  final int skipped;
  final double hitRatePct;
  final double avgReturnPct;
  final double? medianReturnPct;
  final double avgHitReturnPct;
  final double avgMissReturnPct;
  final double? medianMinutesToHit;
  final double bestReturnPct;
  final double worstReturnPct;
  final double cumulativeReturnPct;

  factory LabsBacktestSummary.fromJson(Map<String, dynamic> json) {
    return LabsBacktestSummary(
      reportsScanned: json['reports_scanned'] as int? ?? 0,
      trades: json['trades'] as int? ?? 0,
      hits: json['hits'] as int? ?? 0,
      misses: json['misses'] as int? ?? 0,
      skipped: json['skipped'] as int? ?? 0,
      hitRatePct: (json['hit_rate_pct'] as num?)?.toDouble() ?? 0,
      avgReturnPct: (json['avg_return_pct'] as num?)?.toDouble() ?? 0,
      medianReturnPct: _doubleOrNull(json['median_return_pct']),
      avgHitReturnPct: (json['avg_hit_return_pct'] as num?)?.toDouble() ?? 0,
      avgMissReturnPct: (json['avg_miss_return_pct'] as num?)?.toDouble() ?? 0,
      medianMinutesToHit: _doubleOrNull(json['median_minutes_to_hit']),
      bestReturnPct: (json['best_return_pct'] as num?)?.toDouble() ?? 0,
      worstReturnPct: (json['worst_return_pct'] as num?)?.toDouble() ?? 0,
      cumulativeReturnPct:
          (json['cumulative_return_pct'] as num?)?.toDouble() ?? 0,
    );
  }
}

class LabsTrackedPoint {
  const LabsTrackedPoint({
    required this.time,
    required this.price,
    required this.high,
    required this.low,
  });

  final String time;
  final double price;
  final double high;
  final double low;

  factory LabsTrackedPoint.fromJson(Map<String, dynamic> json) {
    return LabsTrackedPoint(
      time: json['time'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0,
      high: (json['high'] as num?)?.toDouble() ?? 0,
      low: (json['low'] as num?)?.toDouble() ?? 0,
    );
  }
}

class LabsBacktestSession {
  const LabsBacktestSession({
    required this.targetSessionDate,
    required this.reportId,
    required this.rank,
    required this.ticker,
    required this.score,
    required this.priceAtAnalysis,
    required this.targets,
    required this.stopLoss,
    required this.sessionOpen,
    required this.exitPrice,
    required this.exitReason,
    required this.hit,
    required this.minutesToExit,
    required this.returnPct,
    required this.tracked,
  });

  final DateTime targetSessionDate;
  final String reportId;
  final int rank;
  final String ticker;
  final double score;
  final double? priceAtAnalysis;
  final List<double> targets;
  final double? stopLoss;
  final double? sessionOpen;
  final double? exitPrice;
  final String exitReason;
  final bool hit;
  final int? minutesToExit;
  final double? returnPct;
  final List<LabsTrackedPoint> tracked;

  factory LabsBacktestSession.fromJson(Map<String, dynamic> json) {
    return LabsBacktestSession(
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      reportId: json['report_id'] as String,
      rank: json['rank'] as int? ?? 0,
      ticker: json['ticker'] as String? ?? '',
      score: (json['score'] as num?)?.toDouble() ?? 0,
      priceAtAnalysis: _doubleOrNull(json['price_at_analysis']),
      targets: _doubleList(json['targets']),
      stopLoss: _doubleOrNull(json['stop_loss']),
      sessionOpen: _doubleOrNull(json['session_open']),
      exitPrice: _doubleOrNull(json['exit_price']),
      exitReason: json['exit_reason'] as String? ?? 'skipped',
      hit: json['hit'] as bool? ?? false,
      minutesToExit: json['minutes_to_exit'] as int?,
      returnPct: _doubleOrNull(json['return_pct']),
      tracked: _mapList(json['tracked'])
          .map(LabsTrackedPoint.fromJson)
          .toList(growable: false),
    );
  }
}

class LabsBacktestResult {
  const LabsBacktestResult({
    required this.params,
    required this.summary,
    required this.sessions,
    required this.meta,
  });

  final LabsBacktestParams params;
  final LabsBacktestSummary summary;
  final List<LabsBacktestSession> sessions;
  final Map<String, dynamic> meta;

  factory LabsBacktestResult.fromJson(Map<String, dynamic> json) {
    return LabsBacktestResult(
      params: LabsBacktestParams.fromJson(_map(json['params'])),
      summary: LabsBacktestSummary.fromJson(_map(json['summary'])),
      sessions: _mapList(json['sessions'])
          .map(LabsBacktestSession.fromJson)
          .toList(growable: false),
      meta: _map(json['meta']),
    );
  }
}

class LabsBacktestQuery {
  const LabsBacktestQuery({
    required this.startDate,
    required this.endDate,
    required this.rank,
    required this.exitMode,
  });

  final DateTime startDate;
  final DateTime endDate;
  final int? rank;
  final String exitMode;

  @override
  bool operator ==(Object other) {
    return other is LabsBacktestQuery &&
        other.startDate == startDate &&
        other.endDate == endDate &&
        other.rank == rank &&
        other.exitMode == exitMode;
  }

  @override
  int get hashCode => Object.hash(startDate, endDate, rank, exitMode);
}

double? _doubleOrNull(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return null;
}

List<double> _doubleList(Object? value) {
  if (value is List) {
    return value
        .whereType<num>()
        .map((item) => item.toDouble())
        .toList(growable: false);
  }
  return const <double>[];
}

List<Map<String, dynamic>> _mapList(Object? value) {
  if (value is List) {
    return value
        .map((item) => _map(item))
        .where((item) => item.isNotEmpty)
        .toList(growable: false);
  }
  return const <Map<String, dynamic>>[];
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

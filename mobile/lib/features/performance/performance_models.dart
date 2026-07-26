class PerformanceBestWorst {
  const PerformanceBestWorst({
    required this.reportId,
    required this.targetSessionDate,
    required this.ticker,
    required this.rank,
    required this.returnBp,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final String ticker;
  final int rank;
  final int returnBp;

  factory PerformanceBestWorst.fromJson(Map<String, dynamic> json) {
    return PerformanceBestWorst(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      ticker: json['ticker'] as String,
      rank: json['rank'] as int,
      returnBp: json['return_bp'] as int,
    );
  }
}

class PerformanceSession {
  const PerformanceSession({
    required this.reportId,
    required this.targetSessionDate,
    required this.evaluationStatus,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.dataCompletenessPct,
    required this.averageReturnBp,
    required this.positiveCount,
    required this.negativeCount,
    required this.directionAccuracyPct,
    required this.targetOneHitRatePct,
    required this.stopLossHitRatePct,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final String evaluationStatus;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final double dataCompletenessPct;
  final int? averageReturnBp;
  final int positiveCount;
  final int negativeCount;
  final double? directionAccuracyPct;
  final double? targetOneHitRatePct;
  final double? stopLossHitRatePct;

  factory PerformanceSession.fromJson(Map<String, dynamic> json) {
    return PerformanceSession(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      evaluationStatus: json['evaluation_status'] as String,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      dataCompletenessPct:
          (json['data_completeness_pct'] as num? ?? 0).toDouble(),
      averageReturnBp: json['average_return_bp'] as int?,
      positiveCount: json['positive_count'] as int? ?? 0,
      negativeCount: json['negative_count'] as int? ?? 0,
      directionAccuracyPct: _double(json['direction_accuracy_pct']),
      targetOneHitRatePct: _double(json['target_one_hit_rate_pct']),
      stopLossHitRatePct: _double(json['stop_loss_hit_rate_pct']),
    );
  }
}

class PerformanceRank {
  const PerformanceRank({
    required this.rank,
    required this.evaluatedItems,
    required this.averageReturnBp,
    required this.medianReturnBp,
    required this.positiveRatePct,
    required this.directionAccuracyPct,
    required this.targetOneHitRatePct,
    required this.stopLossHitRatePct,
  });

  final int rank;
  final int evaluatedItems;
  final int? averageReturnBp;
  final int? medianReturnBp;
  final double? positiveRatePct;
  final double? directionAccuracyPct;
  final double? targetOneHitRatePct;
  final double? stopLossHitRatePct;

  factory PerformanceRank.fromJson(Map<String, dynamic> json) {
    return PerformanceRank(
      rank: json['rank'] as int,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      averageReturnBp: json['average_return_bp'] as int?,
      medianReturnBp: json['median_return_bp'] as int?,
      positiveRatePct: _double(json['positive_rate_pct']),
      directionAccuracyPct: _double(json['direction_accuracy_pct']),
      targetOneHitRatePct: _double(json['target_one_hit_rate_pct']),
      stopLossHitRatePct: _double(json['stop_loss_hit_rate_pct']),
    );
  }
}

class PerformanceSummary {
  const PerformanceSummary({
    required this.windowSessions,
    required this.sessionsFound,
    required this.completeSessions,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.dataCompletenessPct,
    required this.positiveCount,
    required this.negativeCount,
    required this.flatCount,
    required this.averageReturnBp,
    required this.medianReturnBp,
    required this.positiveRatePct,
    required this.directionAccuracyPct,
    required this.targetOneHitRatePct,
    required this.targetTwoHitRatePct,
    required this.stopLossHitRatePct,
    required this.bestOutcome,
    required this.worstOutcome,
    required this.ranks,
    required this.sessions,
    required this.benchmark,
    required this.negativeResultsRetained,
  });

  final int windowSessions;
  final int sessionsFound;
  final int completeSessions;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final double dataCompletenessPct;
  final int positiveCount;
  final int negativeCount;
  final int flatCount;
  final int? averageReturnBp;
  final int? medianReturnBp;
  final double? positiveRatePct;
  final double? directionAccuracyPct;
  final double? targetOneHitRatePct;
  final double? targetTwoHitRatePct;
  final double? stopLossHitRatePct;
  final PerformanceBestWorst? bestOutcome;
  final PerformanceBestWorst? worstOutcome;
  final List<PerformanceRank> ranks;
  final List<PerformanceSession> sessions;
  final Map<String, dynamic> benchmark;
  final bool negativeResultsRetained;

  factory PerformanceSummary.fromJson(Map<String, dynamic> json) {
    return PerformanceSummary(
      windowSessions: json['window_sessions'] as int,
      sessionsFound: json['sessions_found'] as int? ?? 0,
      completeSessions: json['complete_sessions'] as int? ?? 0,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      dataCompletenessPct:
          (json['data_completeness_pct'] as num? ?? 0).toDouble(),
      positiveCount: json['positive_count'] as int? ?? 0,
      negativeCount: json['negative_count'] as int? ?? 0,
      flatCount: json['flat_count'] as int? ?? 0,
      averageReturnBp: json['average_return_bp'] as int?,
      medianReturnBp: json['median_return_bp'] as int?,
      positiveRatePct: _double(json['positive_rate_pct']),
      directionAccuracyPct: _double(json['direction_accuracy_pct']),
      targetOneHitRatePct: _double(json['target_one_hit_rate_pct']),
      targetTwoHitRatePct: _double(json['target_two_hit_rate_pct']),
      stopLossHitRatePct: _double(json['stop_loss_hit_rate_pct']),
      bestOutcome: json['best_outcome'] == null
          ? null
          : PerformanceBestWorst.fromJson(_map(json['best_outcome'])),
      worstOutcome: json['worst_outcome'] == null
          ? null
          : PerformanceBestWorst.fromJson(_map(json['worst_outcome'])),
      ranks: _list(json['ranks'])
          .map((item) => PerformanceRank.fromJson(_map(item)))
          .toList(growable: false),
      sessions: _list(json['sessions'])
          .map((item) => PerformanceSession.fromJson(_map(item)))
          .toList(growable: false),
      benchmark: _map(json['benchmark']),
      negativeResultsRetained:
          json['negative_results_retained'] as bool? ?? true,
    );
  }
}

class PerformanceReportListItem {
  const PerformanceReportListItem({
    required this.reportId,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.evaluationStatus,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.dataCompletenessPct,
    required this.averageReturnBp,
    required this.positiveCount,
    required this.negativeCount,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final String evaluationStatus;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final double dataCompletenessPct;
  final int? averageReturnBp;
  final int positiveCount;
  final int negativeCount;

  factory PerformanceReportListItem.fromJson(Map<String, dynamic> json) {
    return PerformanceReportListItem(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      evaluationStatus: json['evaluation_status'] as String,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      dataCompletenessPct:
          (json['data_completeness_pct'] as num? ?? 0).toDouble(),
      averageReturnBp: json['average_return_bp'] as int?,
      positiveCount: json['positive_count'] as int? ?? 0,
      negativeCount: json['negative_count'] as int? ?? 0,
    );
  }
}

class PerformanceReportPage {
  const PerformanceReportPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<PerformanceReportListItem> items;
  final int total;
  final int limit;
  final int offset;

  factory PerformanceReportPage.fromJson(Map<String, dynamic> json) {
    return PerformanceReportPage(
      items: _list(json['items'])
          .map((item) => PerformanceReportListItem.fromJson(_map(item)))
          .toList(growable: false),
      total: json['total'] as int? ?? 0,
      limit: json['limit'] as int? ?? 0,
      offset: json['offset'] as int? ?? 0,
    );
  }
}

class PerformanceOutcome {
  const PerformanceOutcome({
    required this.id,
    required this.ticker,
    required this.rank,
    required this.status,
    required this.expectedDirection,
    required this.priceAtAnalysis,
    required this.sessionOpen,
    required this.sessionHigh,
    required this.sessionLow,
    required this.sessionClose,
    required this.returnBp,
    required this.maxUpsideBp,
    required this.maxDrawdownBp,
    required this.directionCorrect,
    required this.targetOne,
    required this.targetTwo,
    required this.stopLoss,
    required this.targetOneHit,
    required this.targetTwoHit,
    required this.stopLossHit,
    required this.provider,
    required this.dataAsOf,
    required this.evaluatedAt,
    required this.evaluatorVersion,
    required this.evidence,
    required this.correctionCount,
  });

  final String id;
  final String ticker;
  final int rank;
  final String status;
  final String expectedDirection;
  final double priceAtAnalysis;
  final double? sessionOpen;
  final double? sessionHigh;
  final double? sessionLow;
  final double? sessionClose;
  final int? returnBp;
  final int? maxUpsideBp;
  final int? maxDrawdownBp;
  final bool? directionCorrect;
  final double? targetOne;
  final double? targetTwo;
  final double? stopLoss;
  final bool? targetOneHit;
  final bool? targetTwoHit;
  final bool? stopLossHit;
  final String? provider;
  final DateTime? dataAsOf;
  final DateTime? evaluatedAt;
  final String evaluatorVersion;
  final Map<String, dynamic> evidence;
  final int correctionCount;

  bool get isComplete => status == 'complete';

  factory PerformanceOutcome.fromJson(Map<String, dynamic> json) {
    return PerformanceOutcome(
      id: json['id'] as String,
      ticker: json['ticker'] as String,
      rank: json['rank'] as int,
      status: json['status'] as String,
      expectedDirection: json['expected_direction'] as String,
      priceAtAnalysis: (json['price_at_analysis'] as num).toDouble(),
      sessionOpen: _double(json['session_open']),
      sessionHigh: _double(json['session_high']),
      sessionLow: _double(json['session_low']),
      sessionClose: _double(json['session_close']),
      returnBp: json['return_bp'] as int?,
      maxUpsideBp: json['max_upside_bp'] as int?,
      maxDrawdownBp: json['max_drawdown_bp'] as int?,
      directionCorrect: json['direction_correct'] as bool?,
      targetOne: _double(json['target_one']),
      targetTwo: _double(json['target_two']),
      stopLoss: _double(json['stop_loss']),
      targetOneHit: json['target_one_hit'] as bool?,
      targetTwoHit: json['target_two_hit'] as bool?,
      stopLossHit: json['stop_loss_hit'] as bool?,
      provider: json['provider'] as String?,
      dataAsOf: _date(json['data_as_of']),
      evaluatedAt: _date(json['evaluated_at']),
      evaluatorVersion: json['evaluator_version'] as String,
      evidence: _map(json['evidence']),
      correctionCount: json['correction_count'] as int? ?? 0,
    );
  }
}

class PerformanceRevision {
  const PerformanceRevision({
    required this.id,
    required this.revisionNumber,
    required this.reason,
    required this.beforePayload,
    required this.afterPayload,
    required this.createdAt,
  });

  final String id;
  final int revisionNumber;
  final String reason;
  final Map<String, dynamic> beforePayload;
  final Map<String, dynamic> afterPayload;
  final DateTime createdAt;

  factory PerformanceRevision.fromJson(Map<String, dynamic> json) {
    return PerformanceRevision(
      id: json['id'] as String,
      revisionNumber: json['revision_number'] as int,
      reason: json['reason'] as String,
      beforePayload: _map(json['before_payload']),
      afterPayload: _map(json['after_payload']),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class PerformanceReportDetail {
  const PerformanceReportDetail({
    required this.reportId,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.evaluationStatus,
    required this.session,
    required this.outcomes,
    required this.revisions,
    required this.negativeResultsRetained,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final String evaluationStatus;
  final PerformanceSession session;
  final List<PerformanceOutcome> outcomes;
  final List<PerformanceRevision> revisions;
  final bool negativeResultsRetained;

  factory PerformanceReportDetail.fromJson(Map<String, dynamic> json) {
    return PerformanceReportDetail(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      evaluationStatus: json['evaluation_status'] as String,
      session: PerformanceSession.fromJson(_map(json['session'])),
      outcomes: _list(json['outcomes'])
          .map((item) => PerformanceOutcome.fromJson(_map(item)))
          .toList(growable: false),
      revisions: _list(json['revisions'])
          .map((item) => PerformanceRevision.fromJson(_map(item)))
          .toList(growable: false),
      negativeResultsRetained:
          json['negative_results_retained'] as bool? ?? true,
    );
  }
}

class PerformanceDelayedItem {
  const PerformanceDelayedItem({
    required this.reportId,
    required this.targetSessionDate,
    required this.evaluationId,
    required this.evaluationStatus,
    required this.totalItems,
    required this.evaluatedItems,
    required this.pendingItems,
    required this.failedItems,
    required this.lastAttemptAt,
    required this.reasons,
  });

  final String reportId;
  final DateTime targetSessionDate;
  final String? evaluationId;
  final String evaluationStatus;
  final int totalItems;
  final int evaluatedItems;
  final int pendingItems;
  final int failedItems;
  final DateTime? lastAttemptAt;
  final List<String> reasons;

  factory PerformanceDelayedItem.fromJson(Map<String, dynamic> json) {
    return PerformanceDelayedItem(
      reportId: json['report_id'] as String,
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      evaluationId: json['evaluation_id'] as String?,
      evaluationStatus: json['evaluation_status'] as String,
      totalItems: json['total_items'] as int? ?? 0,
      evaluatedItems: json['evaluated_items'] as int? ?? 0,
      pendingItems: json['pending_items'] as int? ?? 0,
      failedItems: json['failed_items'] as int? ?? 0,
      lastAttemptAt: _date(json['last_attempt_at']),
      reasons: _list(json['reasons']).map((item) => '$item').toList(),
    );
  }
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return <String, dynamic>{};
}

List<dynamic> _list(Object? value) {
  return value is List ? value : const <dynamic>[];
}

double? _double(Object? value) {
  return value is num ? value.toDouble() : null;
}

DateTime? _date(Object? value) {
  return value is String ? DateTime.parse(value) : null;
}

class StockComparisonItem {
  const StockComparisonItem({
    required this.rank,
    required this.ticker,
    required this.analysisId,
    required this.dataAsOf,
    required this.signal,
    required this.finalScore,
    required this.confidence,
    required this.comparisonScore,
    required this.trend,
    required this.rsi,
    required this.averageVolume20,
    required this.riskLevel,
    required this.riskScore,
    required this.entry,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.rewardRisk1,
  });

  final int rank;
  final String ticker;
  final String analysisId;
  final DateTime dataAsOf;
  final String signal;
  final double finalScore;
  final double confidence;
  final double comparisonScore;
  final String trend;
  final double rsi;
  final double averageVolume20;
  final String riskLevel;
  final double riskScore;
  final double entry;
  final double stopLoss;
  final double target1;
  final double target2;
  final double rewardRisk1;

  factory StockComparisonItem.fromJson(Map<String, dynamic> json) {
    return StockComparisonItem(
      rank: _int(json['rank']),
      ticker: _string(json['ticker']),
      analysisId: _string(json['analysis_id']),
      dataAsOf: DateTime.parse(_string(json['data_as_of'])),
      signal: _string(json['signal']),
      finalScore: _double(json['final_score']),
      confidence: _double(json['confidence']),
      comparisonScore: _double(json['comparison_score']),
      trend: _string(json['trend']),
      rsi: _double(json['rsi']),
      averageVolume20: _double(json['average_volume_20']),
      riskLevel: _string(json['risk_level']),
      riskScore: _double(json['risk_score']),
      entry: _double(json['entry']),
      stopLoss: _double(json['stop_loss']),
      target1: _double(json['target_1']),
      target2: _double(json['target_2']),
      rewardRisk1: _double(json['reward_risk_1']),
    );
  }
}

class StockComparisonResult {
  const StockComparisonResult({
    required this.comparisonId,
    required this.requestKey,
    required this.tickers,
    required this.bestTicker,
    required this.summary,
    required this.items,
    required this.includedAllowance,
    required this.comparisonChargedPoints,
    required this.comparisonChargedCoins,
    required this.analysisChargedPoints,
    required this.analysisChargedCoins,
    required this.allowanceUsed,
    required this.allowanceRemaining,
    required this.idempotent,
    required this.balancePoints,
    required this.balanceCoins,
    required this.disclaimer,
  });

  final String comparisonId;
  final String requestKey;
  final List<String> tickers;
  final String bestTicker;
  final String summary;
  final List<StockComparisonItem> items;
  final bool includedAllowance;
  final int comparisonChargedPoints;
  final String comparisonChargedCoins;
  final int analysisChargedPoints;
  final String analysisChargedCoins;
  final int allowanceUsed;
  final int allowanceRemaining;
  final bool idempotent;
  final int balancePoints;
  final String balanceCoins;
  final String disclaimer;

  factory StockComparisonResult.fromJson(Map<String, dynamic> json) {
    return StockComparisonResult(
      comparisonId: _string(json['comparison_id']),
      requestKey: _string(json['request_key']),
      tickers: _list(json['tickers']).map(_string).toList(growable: false),
      bestTicker: _string(json['best_ticker']),
      summary: _string(json['summary']),
      items: _list(json['items'])
          .map((item) => StockComparisonItem.fromJson(_map(item)))
          .toList(growable: false),
      includedAllowance: json['included_allowance'] as bool? ?? false,
      comparisonChargedPoints: _int(json['comparison_charged_points']),
      comparisonChargedCoins: _string(json['comparison_charged_coins']),
      analysisChargedPoints: _int(json['analysis_charged_points']),
      analysisChargedCoins: _string(json['analysis_charged_coins']),
      allowanceUsed: _int(json['allowance_used']),
      allowanceRemaining: _int(json['allowance_remaining']),
      idempotent: json['idempotent'] as bool? ?? false,
      balancePoints: _int(json['balance_points']),
      balanceCoins: _string(json['balance_coins']),
      disclaimer: _string(json['disclaimer']),
    );
  }
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

List<dynamic> _list(Object? value) => value is List ? value : const [];

String _string(Object? value) => value?.toString() ?? '';

int _int(Object? value) {
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.round();
  }
  return int.tryParse(_string(value)) ?? 0;
}

double _double(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(_string(value)) ?? 0;
}

class ReplayCandle {
  const ReplayCandle({
    required this.timestamp,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.volume,
  });

  final DateTime timestamp;
  final double open;
  final double high;
  final double low;
  final double close;
  final double volume;

  bool get isUp => close >= open;

  factory ReplayCandle.fromJson(Map<String, dynamic> json) {
    double asDouble(dynamic v) =>
        v is num ? v.toDouble() : double.tryParse('$v') ?? 0;
    return ReplayCandle(
      timestamp: DateTime.tryParse('${json['timestamp']}')?.toLocal() ??
          DateTime.now(),
      open: asDouble(json['open']),
      high: asDouble(json['high']),
      low: asDouble(json['low']),
      close: asDouble(json['close']),
      volume: asDouble(json['volume']),
    );
  }
}

class SessionReplay {
  const SessionReplay({
    required this.ticker,
    required this.sessionDate,
    required this.interval,
    required this.candles,
  });

  final String ticker;
  final String sessionDate;
  final String interval;
  final List<ReplayCandle> candles;

  factory SessionReplay.fromJson(Map<String, dynamic> json) {
    final raw = json['candles'];
    final list = raw is List ? raw : const [];
    return SessionReplay(
      ticker: '${json['ticker'] ?? ''}',
      sessionDate: '${json['session_date'] ?? ''}',
      interval: '${json['interval'] ?? ''}',
      candles: list
          .whereType<Map<String, dynamic>>()
          .map(ReplayCandle.fromJson)
          .toList(growable: false),
    );
  }
}

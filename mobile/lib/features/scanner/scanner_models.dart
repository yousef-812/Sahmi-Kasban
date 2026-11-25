class ScannerList<T> {
  const ScannerList({required this.items, required this.count});

  final List<T> items;
  final int count;

  factory ScannerList.fromJson(
    Map<String, dynamic> json,
    T Function(Object? item) parse,
  ) {
    return ScannerList<T>(
      items: _list(
        json['items'],
      ).map((Object? item) => parse(item)).toList(growable: false),
      count: json['count'] as int? ?? 0,
    );
  }
}

abstract class ScannerItem {
  const ScannerItem({
    required this.kind,
    required this.symbol,
    required this.timeframe,
    required this.asOf,
    required this.score,
    required this.rating,
    required this.sector,
  });

  final String kind;
  final String symbol;
  final String timeframe;
  final DateTime asOf;
  final double? score;
  final String? rating;
  final String? sector;
}

class ScannerTechnicalItem extends ScannerItem {
  const ScannerTechnicalItem({
    required super.kind,
    required super.symbol,
    required super.timeframe,
    required super.asOf,
    required super.score,
    required super.rating,
    required super.sector,
    required this.candleTimestamp,
    required this.candlesUsed,
    required this.technicalScore,
    required this.technicalRating,
    required this.rsi14,
    required this.macd,
    required this.macdSignal,
    required this.macdHistogram,
    required this.adx14,
    required this.atr14,
    required this.atrPercent,
    required this.bbPosition,
    required this.bbBandwidth,
    required this.sma20,
    required this.sma50,
    required this.sma200,
    required this.priceVsSma20,
    required this.priceVsSma50,
    required this.priceVsSma200,
    required this.ema20,
    required this.ema50,
    required this.relativeVolume20,
    required this.stochasticK,
    required this.stochasticD,
    required this.mfi14,
    required this.performance5d,
    required this.performance20d,
    required this.performance60d,
    required this.high52Week,
    required this.low52Week,
  });

  final String? candleTimestamp;
  final int candlesUsed;
  final double? technicalScore;
  final String? technicalRating;
  final double? rsi14;
  final double? macd;
  final double? macdSignal;
  final double? macdHistogram;
  final double? adx14;
  final double? atr14;
  final double? atrPercent;
  final double? bbPosition;
  final double? bbBandwidth;
  final double? sma20;
  final double? sma50;
  final double? sma200;
  final double? priceVsSma20;
  final double? priceVsSma50;
  final double? priceVsSma200;
  final double? ema20;
  final double? ema50;
  final double? relativeVolume20;
  final double? stochasticK;
  final double? stochasticD;
  final double? mfi14;
  final double? performance5d;
  final double? performance20d;
  final double? performance60d;
  final double? high52Week;
  final double? low52Week;

  factory ScannerTechnicalItem.fromJson(Map<String, dynamic> json) {
    return ScannerTechnicalItem(
      kind: json['kind'] as String,
      symbol: json['symbol'] as String,
      timeframe: json['timeframe'] as String,
      asOf: DateTime.parse(json['as_of'] as String),
      score: _double(json['score']),
      rating: json['rating'] as String?,
      sector: json['sector'] as String?,
      candleTimestamp: json['candleTimestamp'] as String?,
      candlesUsed: json['candlesUsed'] as int? ?? 0,
      technicalScore: _double(json['technicalScore']),
      technicalRating: json['technicalRating'] as String?,
      rsi14: _double(json['rsi14']),
      macd: _double(json['macd']),
      macdSignal: _double(json['macdSignal']),
      macdHistogram: _double(json['macdHistogram']),
      adx14: _double(json['adx14']),
      atr14: _double(json['atr14']),
      atrPercent: _double(json['atrPercent']),
      bbPosition: _double(json['bbPosition']),
      bbBandwidth: _double(json['bbBandwidth']),
      sma20: _double(json['sma20']),
      sma50: _double(json['sma50']),
      sma200: _double(json['sma200']),
      priceVsSma20: _double(json['priceVsSma20']),
      priceVsSma50: _double(json['priceVsSma50']),
      priceVsSma200: _double(json['priceVsSma200']),
      ema20: _double(json['ema20']),
      ema50: _double(json['ema50']),
      relativeVolume20: _double(json['relativeVolume20']),
      stochasticK: _double(json['stochasticK']),
      stochasticD: _double(json['stochasticD']),
      mfi14: _double(json['mfi14']),
      performance5d: _double(json['performance5d']),
      performance20d: _double(json['performance20d']),
      performance60d: _double(json['performance60d']),
      high52Week: _double(json['high52Week']),
      low52Week: _double(json['low52Week']),
    );
  }
}

class ScannerFibonacciZone {
  const ScannerFibonacciZone({
    this.kind,
    this.key,
    this.labelAr,
    this.labelEn,
    this.priceLow,
    this.priceHigh,
  });

  final String? kind;
  final String? key;
  final String? labelAr;
  final String? labelEn;
  final double? priceLow;
  final double? priceHigh;

  factory ScannerFibonacciZone.fromJson(Map<String, dynamic> json) {
    return ScannerFibonacciZone(
      kind: json['kind'] as String?,
      key: json['key'] as String?,
      labelAr: json['labelAr'] as String?,
      labelEn: json['labelEn'] as String?,
      priceLow: _double(json['priceLow']),
      priceHigh: _double(json['priceHigh']),
    );
  }
}

class ScannerFibonacciLevel {
  const ScannerFibonacciLevel({
    this.key,
    this.kind,
    this.ratio,
    this.price,
    this.labelAr,
    this.labelEn,
  });

  final String? key;
  final String? kind;
  final double? ratio;
  final double? price;
  final String? labelAr;
  final String? labelEn;

  factory ScannerFibonacciLevel.fromJson(Map<String, dynamic> json) {
    return ScannerFibonacciLevel(
      key: json['key'] as String?,
      kind: json['kind'] as String?,
      ratio: _double(json['ratio']),
      price: _double(json['price']),
      labelAr: json['labelAr'] as String?,
      labelEn: json['labelEn'] as String?,
    );
  }
}

class ScannerFibonacciItem extends ScannerItem {
  const ScannerFibonacciItem({
    required super.kind,
    required super.symbol,
    required super.timeframe,
    required super.asOf,
    required super.score,
    required super.rating,
    required super.sector,
    required this.price,
    required this.direction,
    required this.retracementPercent,
    required this.distancePercent,
    required this.status,
    required this.confidence,
    required this.trendAligned,
    required this.currentZone,
    required this.levels,
  });

  final double? price;
  final String? direction;
  final double? retracementPercent;
  final double? distancePercent;
  final String? status;
  final double? confidence;
  final bool trendAligned;
  final ScannerFibonacciZone? currentZone;
  final List<ScannerFibonacciLevel> levels;

  factory ScannerFibonacciItem.fromJson(Map<String, dynamic> json) {
    return ScannerFibonacciItem(
      kind: json['kind'] as String,
      symbol: json['symbol'] as String,
      timeframe: json['timeframe'] as String,
      asOf: DateTime.parse(json['as_of'] as String),
      score: _double(json['score']),
      rating: json['rating'] as String?,
      sector: json['sector'] as String?,
      price: _double(json['price']),
      direction: json['direction'] as String?,
      retracementPercent: _double(json['retracementPercent']),
      distancePercent: _double(json['distancePercent']),
      status: json['status'] as String?,
      confidence: _double(json['confidence']),
      trendAligned: _bool(json['trendAligned']),
      currentZone: json['currentZone'] is Map
          ? ScannerFibonacciZone.fromJson(_map(json['currentZone']))
          : null,
      levels: _list(json['levels'])
          .map((Object? item) => ScannerFibonacciLevel.fromJson(_map(item)))
          .toList(growable: false),
    );
  }
}

class ScannerHarmonicPattern {
  const ScannerHarmonicPattern({
    required this.type,
    required this.status,
    required this.score,
    required this.points,
    required this.ratios,
  });

  final String type;
  final String status;
  final double? score;
  final Map<String, dynamic> points;
  final Map<String, dynamic> ratios;

  factory ScannerHarmonicPattern.fromJson(Map<String, dynamic> json) {
    return ScannerHarmonicPattern(
      type: json['type'] as String? ?? '',
      status: json['status'] as String? ?? '',
      score: _double(json['score']),
      points: _map(json['points']),
      ratios: _map(json['ratios']),
    );
  }
}

class ScannerHarmonicItem extends ScannerItem {
  const ScannerHarmonicItem({
    required super.kind,
    required super.symbol,
    required super.timeframe,
    required super.asOf,
    required super.score,
    required super.rating,
    required super.sector,
    required this.patterns,
  });

  final List<ScannerHarmonicPattern> patterns;

  factory ScannerHarmonicItem.fromJson(Map<String, dynamic> json) {
    return ScannerHarmonicItem(
      kind: json['kind'] as String,
      symbol: json['symbol'] as String,
      timeframe: json['timeframe'] as String,
      asOf: DateTime.parse(json['as_of'] as String),
      score: _double(json['score']),
      rating: json['rating'] as String?,
      sector: json['sector'] as String?,
      patterns: _list(json['patterns'])
          .map((Object? item) => ScannerHarmonicPattern.fromJson(_map(item)))
          .toList(growable: false),
    );
  }
}

class ScannerSmcItem {
  const ScannerSmcItem({
    required this.symbol,
    required this.score,
    required this.details,
    required this.reasons,
  });

  final String symbol;
  final double score;
  final Map<String, dynamic> details;
  final List<String> reasons;

  factory ScannerSmcItem.fromJson(Map<String, dynamic> json) {
    return ScannerSmcItem(
      symbol: json['symbol'] as String,
      score: (json['score'] as num).toDouble(),
      details: _map(json['details']),
      reasons: _list(
        json['reasons'],
      ).map((Object? item) => item.toString()).toList(growable: false),
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

bool _bool(Object? value) {
  return value == true || value == 1;
}

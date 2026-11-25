// نماذج تدفق الأوامر — مطابقة لـ `backend/app/schemas/order_flow.py`.
//
// كل استجابة تحمل علم `available`: الواجهة تعرض حالة «غير متاح» صادقة
// عند انعدام مصدر العمق بدل اختلاق صفوف.

class OrderBookLevel {
  const OrderBookLevel({required this.price, required this.size});

  final double price;
  final double size;

  factory OrderBookLevel.fromJson(Map<String, dynamic> json) {
    return OrderBookLevel(
      price: (json['price'] as num).toDouble(),
      size: (json['size'] as num?)?.toDouble() ?? 0,
    );
  }
}

class OrderBookSnapshot {
  const OrderBookSnapshot({
    required this.available,
    required this.ticker,
    this.asOf,
    required this.bids,
    required this.asks,
  });

  final bool available;
  final String ticker;
  final DateTime? asOf;
  final List<OrderBookLevel> bids;
  final List<OrderBookLevel> asks;

  factory OrderBookSnapshot.fromJson(Map<String, dynamic> json) {
    return OrderBookSnapshot(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      asOf: _dateTime(json['as_of']),
      bids: _levels(json['bids']),
      asks: _levels(json['asks']),
    );
  }
}

class RecentTradeItem {
  const RecentTradeItem({
    this.executedAt,
    required this.price,
    required this.size,
    required this.turnoverEgp,
    required this.side,
  });

  final DateTime? executedAt;
  final double price;
  final double size;
  final double turnoverEgp;
  final String side;

  factory RecentTradeItem.fromJson(Map<String, dynamic> json) {
    return RecentTradeItem(
      executedAt: _dateTime(json['executed_at']),
      price: (json['price'] as num).toDouble(),
      size: (json['size'] as num?)?.toDouble() ?? 0,
      turnoverEgp: (json['turnover_egp'] as num?)?.toDouble() ?? 0,
      side: json['side'] as String? ?? 'unknown',
    );
  }
}

class RecentTradesSnapshot {
  const RecentTradesSnapshot({
    required this.available,
    required this.ticker,
    required this.items,
  });

  final bool available;
  final String ticker;
  final List<RecentTradeItem> items;

  factory RecentTradesSnapshot.fromJson(Map<String, dynamic> json) {
    return RecentTradesSnapshot(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      items: _list(
        json['items'],
      ).map((Object? item) => RecentTradeItem.fromJson(_map(item))).toList(growable: false),
    );
  }
}

class MarketDepthSnapshot {
  const MarketDepthSnapshot({
    required this.available,
    required this.ticker,
    this.asOf,
    required this.levels,
    required this.bidLevels,
    required this.askLevels,
    required this.totalBidVolume,
    required this.totalAskVolume,
    this.spread,
    this.midPrice,
  });

  final bool available;
  final String ticker;
  final DateTime? asOf;
  final int levels;
  final List<OrderBookLevel> bidLevels;
  final List<OrderBookLevel> askLevels;
  final double totalBidVolume;
  final double totalAskVolume;
  final double? spread;
  final double? midPrice;

  factory MarketDepthSnapshot.fromJson(Map<String, dynamic> json) {
    return MarketDepthSnapshot(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      asOf: _dateTime(json['as_of']),
      levels: json['levels'] as int? ?? 0,
      bidLevels: _levels(json['bid_levels']),
      askLevels: _levels(json['ask_levels']),
      totalBidVolume: (json['total_bid_volume'] as num?)?.toDouble() ?? 0,
      totalAskVolume: (json['total_ask_volume'] as num?)?.toDouble() ?? 0,
      spread: _double(json['spread']),
      midPrice: _double(json['mid_price']),
    );
  }
}

/// أفضل سعر شراء/بيع لحظي (bid/ask بدون أحجام) — WP-27.
class TopOfBookQuote {
  const TopOfBookQuote({
    required this.available,
    required this.ticker,
    this.bid,
    this.ask,
    this.midPrice,
    this.spread,
    this.spreadBp,
    this.asOf,
    this.source,
    this.reason,
  });

  final bool available;
  final String ticker;
  final double? bid;
  final double? ask;
  final double? midPrice;
  final double? spread;
  final double? spreadBp;
  final DateTime? asOf;
  final String? source;
  final String? reason;

  factory TopOfBookQuote.fromJson(Map<String, dynamic> json) {
    return TopOfBookQuote(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      bid: _double(json['bid']),
      ask: _double(json['ask']),
      midPrice: _double(json['mid_price']),
      spread: _double(json['spread']),
      spreadBp: _double(json['spread_bp']),
      asOf: _dateTime(json['as_of']),
      source: json['source'] as String?,
      reason: json['reason'] as String?,
    );
  }
}

/// جلسة تداول ذات دوران استثنائي — إشارة بديلة (proxy) لا بيانات order-flow فردية.
class WhaleActivityItem {
  const WhaleActivityItem({
    this.sessionDate,
    required this.close,
    required this.volume,
    required this.turnoverEgp,
    this.turnoverRatio,
  });

  final String? sessionDate;
  final double close;
  final double volume;
  final double turnoverEgp;

  /// نسبة الدوران مقابل متوسط الجلسات (>= 3 considered sharp activity).
  final double? turnoverRatio;

  bool get isSharpActivity => (turnoverRatio ?? 0) >= 3.0;

  factory WhaleActivityItem.fromJson(Map<String, dynamic> json) {
    return WhaleActivityItem(
      sessionDate: json['session_date'] as String?,
      close: (json['close'] as num).toDouble(),
      volume: (json['volume'] as num?)?.toDouble() ?? 0,
      turnoverEgp: (json['turnover_egp'] as num?)?.toDouble() ?? 0,
      turnoverRatio: _double(json['turnover_ratio']),
    );
  }
}

class WhaleDetectionSnapshot {
  const WhaleDetectionSnapshot({
    required this.available,
    required this.ticker,
    this.threshold,
    required this.items,
  });

  final bool available;
  final String ticker;
  final double? threshold;
  final List<WhaleActivityItem> items;

  factory WhaleDetectionSnapshot.fromJson(Map<String, dynamic> json) {
    return WhaleDetectionSnapshot(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      threshold: _double(json['threshold']),
      items: _list(json['items'])
          .map((Object? item) => WhaleActivityItem.fromJson(_map(item)))
          .toList(growable: false),
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

List<OrderBookLevel> _levels(Object? value) {
  return _list(
    value,
  ).map((Object? item) => OrderBookLevel.fromJson(_map(item))).toList(growable: false);
}

double? _double(Object? value) {
  return value is num ? value.toDouble() : null;
}

DateTime? _dateTime(Object? value) {
  return value is String && value.isNotEmpty ? DateTime.tryParse(value) : null;
}

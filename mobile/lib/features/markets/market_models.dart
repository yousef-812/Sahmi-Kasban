// نماذج الأسواق — مطابقة لـ
// `schemas/global_market.py::GlobalMarketResponse` و
// `schemas/market_status.py::MarketStatusResponse` و
// `schemas/market.py::MarketBreadthResponse`.

class GlobalMarketItem {
  const GlobalMarketItem({
    required this.symbol,
    required this.name,
    required this.nameAr,
    required this.value,
    this.changePct,
    this.currency,
    required this.kind,
  });

  final String symbol;
  final String name;
  final String nameAr;
  final double value;
  final double? changePct;
  final String? currency;
  final String kind;

  factory GlobalMarketItem.fromJson(Map<String, dynamic> json) {
    return GlobalMarketItem(
      symbol: json['symbol'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String? ?? '',
      value: (json['value'] as num).toDouble(),
      changePct: (json['change_pct'] as num?)?.toDouble(),
      currency: json['currency'] as String?,
      kind: json['kind'] as String? ?? 'index',
    );
  }
}

class GlobalMarketSnapshot {
  const GlobalMarketSnapshot({
    required this.available,
    this.source,
    this.asOf,
    this.indices = const [],
    this.fx = const [],
    this.commodities = const [],
    this.error,
  });

  final bool available;
  final String? source;
  final DateTime? asOf;
  final List<GlobalMarketItem> indices;
  final List<GlobalMarketItem> fx;
  final List<GlobalMarketItem> commodities;
  final String? error;

  factory GlobalMarketSnapshot.fromJson(Map<String, dynamic> json) {
    return GlobalMarketSnapshot(
      available: json['available'] == true,
      source: json['source'] as String?,
      asOf: _dateTime(json['as_of']),
      indices: [
        for (final item in json['indices'] as List<dynamic>? ?? const [])
          GlobalMarketItem.fromJson(Map<String, dynamic>.from(item as Map)),
      ],
      fx: [
        for (final item in json['fx'] as List<dynamic>? ?? const [])
          GlobalMarketItem.fromJson(Map<String, dynamic>.from(item as Map)),
      ],
      commodities: [
        for (final item in json['commodities'] as List<dynamic>? ?? const [])
          GlobalMarketItem.fromJson(Map<String, dynamic>.from(item as Map)),
      ],
      error: json['error'] as String?,
    );
  }
}

class MarketSessionWindow {
  const MarketSessionWindow({
    required this.opensAt,
    required this.closesAt,
  });

  final String opensAt;
  final String closesAt;

  factory MarketSessionWindow.fromJson(Map<String, dynamic> json) {
    return MarketSessionWindow(
      opensAt: json['opens_at'] as String? ?? '',
      closesAt: json['closes_at'] as String? ?? '',
    );
  }
}

class MarketStatusSnapshot {
  const MarketStatusSnapshot({
    required this.isOpen,
    required this.session,
    required this.timezone,
    required this.date,
    this.nextOpen,
    this.nextClose,
    required this.day,
    required this.isTradingDay,
  });

  final bool isOpen;
  final MarketSessionWindow session;
  final String timezone;
  final String date;
  final String? nextOpen;
  final String? nextClose;
  final String day;
  final bool isTradingDay;

  factory MarketStatusSnapshot.fromJson(Map<String, dynamic> json) {
    return MarketStatusSnapshot(
      isOpen: json['is_open'] == true,
      session: MarketSessionWindow.fromJson(json['session'] as Map<String, dynamic>? ?? {}),
      timezone: json['timezone'] as String? ?? 'Africa/Cairo',
      date: json['date'] as String? ?? '',
      nextOpen: json['next_open'] as String?,
      nextClose: json['next_close'] as String?,
      day: json['day'] as String? ?? 'monday',
      isTradingDay: json['is_trading_day'] == true,
    );
  }
}

class SectorPerformance {
  const SectorPerformance({
    required this.sector,
    required this.avgChangePct,
    required this.symbols,
  });

  final String sector;
  final double avgChangePct;
  final int symbols;

  factory SectorPerformance.fromJson(Map<String, dynamic> json) {
    return SectorPerformance(
      sector: json['sector'] as String? ?? '',
      avgChangePct: (json['avg_change_pct'] as num?)?.toDouble() ?? 0.0,
      symbols: json['symbols'] as int? ?? 0,
    );
  }
}

class MarketBreadthSnapshot {
  const MarketBreadthSnapshot({
    required this.available,
    required this.advancers,
    required this.decliners,
    required this.unchanged,
    required this.total,
    this.advanceDeclineRatio,
    this.sectorPerformance = const [],
    this.asOf,
    this.reason,
  });

  final bool available;
  final int advancers;
  final int decliners;
  final int unchanged;
  final int total;
  final double? advanceDeclineRatio;
  final List<SectorPerformance> sectorPerformance;
  final DateTime? asOf;
  final String? reason;

  factory MarketBreadthSnapshot.fromJson(Map<String, dynamic> json) {
    return MarketBreadthSnapshot(
      available: json['available'] == true,
      advancers: json['advancers'] as int? ?? 0,
      decliners: json['decliners'] as int? ?? 0,
      unchanged: json['unchanged'] as int? ?? 0,
      total: json['total'] as int? ?? 0,
      advanceDeclineRatio: (json['advance_decline_ratio'] as num?)?.toDouble(),
      sectorPerformance: [
        for (final item in json['sector_performance'] as List<dynamic>? ?? const [])
          SectorPerformance.fromJson(Map<String, dynamic>.from(item as Map)),
      ],
      asOf: _dateTime(json['as_of']),
      reason: json['reason'] as String?,
    );
  }
}

DateTime? _dateTime(Object? value) {
  return value is String && value.isNotEmpty ? DateTime.tryParse(value) : null;
}
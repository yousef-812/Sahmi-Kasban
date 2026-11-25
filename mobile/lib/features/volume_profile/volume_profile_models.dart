// نماذج حجم السعر (POC/منطقة القيمة) — مطابقة لـ
// `backend/app/schemas/market.py::StockVolumeProfileResponse`.
//
// محسوبة من شموم OHLCV اليومية (توزيع الحجم على نطاقات السعر) — تقريب
// لا بيانات tick حقيقية (لا يوجد مصدر مجاني لـ EGX).

class VolumeProfileBin {
  const VolumeProfileBin({
    required this.priceLow,
    required this.priceHigh,
    required this.volume,
  });

  final double priceLow;
  final double priceHigh;
  final double volume;

  factory VolumeProfileBin.fromJson(Map<String, dynamic> json) {
    return VolumeProfileBin(
      priceLow: (json['price_low'] as num).toDouble(),
      priceHigh: (json['price_high'] as num).toDouble(),
      volume: (json['volume'] as num).toDouble(),
    );
  }
}

class StockVolumeProfileSnapshot {
  const StockVolumeProfileSnapshot({
    required this.available,
    required this.ticker,
    this.poc,
    this.valueAreaHigh,
    this.valueAreaLow,
    required this.bins,
    this.aboveValuePct,
    this.belowValuePct,
    required this.windowDays,
    this.asOf,
    this.reason,
  });

  final bool available;
  final String ticker;
  final double? poc;
  final double? valueAreaHigh;
  final double? valueAreaLow;
  final List<VolumeProfileBin> bins;
  final double? aboveValuePct;
  final double? belowValuePct;
  final int windowDays;
  final DateTime? asOf;
  final String? reason;

  double? get maxBinVolume {
    double? max;
    for (final bin in bins) {
      if (max == null || bin.volume > max) max = bin.volume;
    }
    return max;
  }

  bool isInValueArea(VolumeProfileBin bin) {
    final low = valueAreaLow;
    final high = valueAreaHigh;
    if (low == null || high == null) return false;
    return bin.priceHigh > low && bin.priceLow < high;
  }

  bool isPocBin(VolumeProfileBin bin) {
    final value = poc;
    return value != null && bin.priceLow <= value && value <= bin.priceHigh;
  }

  factory StockVolumeProfileSnapshot.fromJson(Map<String, dynamic> json) {
    return StockVolumeProfileSnapshot(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      poc: _double(json['poc']),
      valueAreaHigh: _double(json['value_area_high']),
      valueAreaLow: _double(json['value_area_low']),
      bins: [
        for (final item in json['bins'] as List<dynamic>? ?? const [])
          VolumeProfileBin.fromJson(Map<String, dynamic>.from(item as Map)),
      ],
      aboveValuePct: _double(json['above_value_pct']),
      belowValuePct: _double(json['below_value_pct']),
      windowDays: json['window_days'] as int? ?? 0,
      asOf: _dateTime(json['as_of']),
      reason: json['reason'] as String?,
    );
  }
}

double? _double(Object? value) {
  return value is num ? value.toDouble() : null;
}

DateTime? _dateTime(Object? value) {
  return value is String && value.isNotEmpty ? DateTime.tryParse(value) : null;
}

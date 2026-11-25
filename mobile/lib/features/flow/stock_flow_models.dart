// نماذج ضغط الشراء/البيع — مطابقة لـ `backend/app/schemas/market.py::StockFlowResponse`.
//
// المصدر شموم OHLCV عبر CLV×الحجم — تقدير للضغط لا أوامر فعلية
// (لا يوجد دفتر عمق مجاني لـ EGX؛ انظر order_flow).

class StockFlowSnapshot {
  const StockFlowSnapshot({
    required this.available,
    required this.ticker,
    this.buySharePct,
    this.sellSharePct,
    this.buyVolume,
    this.sellVolume,
    this.netVolume,
    required this.adTrend,
    this.mfi14,
    required this.obvTrend,
    required this.verdict,
    required this.windowDays,
    this.asOf,
    this.reason,
  });

  final bool available;
  final String ticker;
  final double? buySharePct;
  final double? sellSharePct;
  final double? buyVolume;
  final double? sellVolume;
  final double? netVolume;

  /// ‎+1‎ تراكم، ‎-1‎ توزيع، ‎0‎ محايد.
  final int adTrend;
  final double? mfi14;
  final int obvTrend;

  /// `accumulate` | `distribute` | `neutral`.
  final String verdict;
  final int windowDays;
  final DateTime? asOf;
  final String? reason;

  factory StockFlowSnapshot.fromJson(Map<String, dynamic> json) {
    return StockFlowSnapshot(
      available: json['available'] == true,
      ticker: json['ticker'] as String? ?? '',
      buySharePct: _double(json['buy_share_pct']),
      sellSharePct: _double(json['sell_share_pct']),
      buyVolume: _double(json['buy_volume']),
      sellVolume: _double(json['sell_volume']),
      netVolume: _double(json['net_volume']),
      adTrend: json['ad_trend'] as int? ?? 0,
      mfi14: _double(json['mfi14']),
      obvTrend: json['obv_trend'] as int? ?? 0,
      verdict: json['verdict'] as String? ?? 'neutral',
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

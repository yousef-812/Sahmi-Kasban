/// درجة معنويات أخبار السهم — مطابقة لـ `SymbolSentimentResponse`
/// في `backend/app/schemas/sentiment.py`.
class SymbolSentiment {
  const SymbolSentiment({
    required this.ticker,
    required this.score,
    required this.sampleSize,
    required this.coverage,
    required this.asOf,
    required this.windowDays,
  });

  final String ticker;

  /// متوسط مرجّح لمعنويات الأخبار في النطاق [-1, 1].
  final double score;

  /// عدد الأخبار داخل النافذة.
  final int sampleSize;

  /// one of: insufficient | low | normal.
  final String coverage;

  final DateTime asOf;

  /// طول النافذة الزمنية بالdays (1..90).
  final int windowDays;

  /// لا توجد أخبار كافية لحساب درجة ذات مصداقية — ليست حالة خطأ.
  bool get isInsufficient => coverage == 'insufficient' || sampleSize == 0;

  factory SymbolSentiment.fromJson(Map<String, dynamic> json) {
    return SymbolSentiment(
      ticker: json['ticker'] as String? ?? '',
      score: (json['score'] as num?)?.toDouble() ?? 0,
      sampleSize: json['sample_size'] as int? ?? 0,
      coverage: json['coverage'] as String? ?? 'insufficient',
      asOf: DateTime.parse(json['as_of'] as String),
      windowDays: json['window_days'] as int? ?? 7,
    );
  }
}

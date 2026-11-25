class ApiList<T> {
  const ApiList({required this.items, required this.count});

  final List<T> items;
  final int count;

  factory ApiList.fromJson(
    Map<String, dynamic> json,
    T Function(Object? item) parse,
  ) {
    return ApiList<T>(
      items: _list(
        json['items'],
      ).map((Object? item) => parse(item)).toList(growable: false),
      count: json['count'] as int? ?? 0,
    );
  }
}

class SignalEvent {
  const SignalEvent({
    required this.id,
    required this.event,
    this.price,
    this.note,
    required this.createdAt,
  });

  final String id;
  final String event;
  final double? price;
  final String? note;
  final DateTime createdAt;

  factory SignalEvent.fromJson(Map<String, dynamic> json) {
    return SignalEvent(
      id: json['id'] as String,
      event: json['event'] as String,
      price: _double(json['price']),
      note: json['note'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

/// إشارة تداول بالحقول المطابقة لـ `SignalOut` من السكيمات.
///
/// الحقل `events` يُملأ فقط من نقطة النهاية التفصيلية `SignalDetailOut`
/// (تُرجعه قائمة الإشارات فارغًا).
class Signal {
  Signal.fromJson(Map<String, dynamic> json)
    : id = json['id'] as String,
      ticker = json['ticker'] as String,
      direction = json['direction'] as String,
      entry = _double(json['entry']) ?? 0,
      stop = _double(json['stop']) ?? 0,
      t1 = _double(json['t1']) ?? 0,
      t2 = _double(json['t2']),
      t3 = _double(json['t3']),
      state = json['state'] as String,
      openedAt = DateTime.parse(json['opened_at'] as String),
      updatedAt = DateTime.parse(json['updated_at'] as String),
      closedAt = _dateTime(json['closed_at']),
      pnlPct = _double(json['pnl_pct']),
      source = json['source'] as String,
      refReportId = json['ref_report_id'] as String?,
      userId = json['user_id'] as String?,
      meta = _map(json['meta']),
      events = _list(json['events'])
          .map((Object? item) => SignalEvent.fromJson(_map(item)))
          .toList(growable: false);

  final String id;
  final String ticker;
  final String direction;
  final double entry;
  final double stop;
  final double t1;
  final double? t2;
  final double? t3;
  final String state;
  final DateTime openedAt;
  final DateTime updatedAt;
  final DateTime? closedAt;
  final double? pnlPct;
  final String source;
  final String? refReportId;
  final String? userId;
  final Map<String, dynamic> meta;

  /// سجل انتقالات دورة حياة الإشارة (`SignalDetailOut.events`).
  final List<SignalEvent> events;

  bool get isLong => direction == 'long';

  /// مستوى الوقف المتحرك المخزَّن في `meta.trailing_stop` (إن وجد).
  double? get trailingStop => _double(meta['trailing_stop']);

  /// أقصى قيمة تفعيل مخزَّنة في `meta.activation_high` (إن وجدت).
  double? get activationHigh => _double(meta['activation_high']);
}

class AlertItem {
  const AlertItem({
    required this.id,
    required this.type,
    required this.refId,
    required this.title,
    required this.body,
    required this.isRead,
    required this.createdAt,
  });

  final String id;
  final String type;
  final String? refId;
  final String title;
  final String body;
  final bool isRead;
  final DateTime createdAt;

  factory AlertItem.fromJson(Map<String, dynamic> json) {
    return AlertItem(
      id: json['id'] as String,
      type: json['type'] as String,
      refId: json['ref_id'] as String?,
      title: json['title'] as String,
      body: json['body'] as String,
      isRead: json['is_read'] == true,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  AlertItem markRead() => AlertItem(
    id: id,
    type: type,
    refId: refId,
    title: title,
    body: body,
    isRead: true,
    createdAt: createdAt,
  );
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

DateTime? _dateTime(Object? value) {
  return value is String && value.isNotEmpty ? DateTime.parse(value) : null;
}

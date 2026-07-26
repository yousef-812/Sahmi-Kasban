class AppNotification {
  const AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.category,
    required this.data,
    required this.readAt,
    required this.sentAt,
  });

  final String id;
  final String title;
  final String body;
  final String category;
  final Map<String, dynamic> data;
  final DateTime? readAt;
  final DateTime sentAt;

  bool get isUnread => readAt == null;

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      category: json['category'] as String,
      data: _map(json['data']),
      readAt: json['read_at'] == null
          ? null
          : DateTime.parse(json['read_at'] as String),
      sentAt: DateTime.parse(json['sent_at'] as String),
    );
  }
}

class NotificationPage {
  const NotificationPage({
    required this.items,
    required this.total,
    required this.unreadCount,
    required this.limit,
    required this.offset,
  });

  final List<AppNotification> items;
  final int total;
  final int unreadCount;
  final int limit;
  final int offset;

  factory NotificationPage.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return NotificationPage(
      items: rawItems
          .map((item) => AppNotification.fromJson(_map(item)))
          .toList(growable: false),
      total: json['total'] as int? ?? 0,
      unreadCount: json['unread_count'] as int? ?? 0,
      limit: json['limit'] as int? ?? 20,
      offset: json['offset'] as int? ?? 0,
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

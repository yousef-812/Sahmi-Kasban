import '../community/community_models.dart';

class AdminOverview {
  const AdminOverview({
    required this.usersTotal,
    required this.usersActive,
    required this.usersSuspended,
    required this.discussionsPending,
    required this.discussionsPublished,
    required this.discussionsHidden,
    required this.openReports,
    required this.openAppeals,
    required this.verifiedPredictions,
    required this.walletPointsTotal,
    required this.notificationsToday,
  });

  final int usersTotal;
  final int usersActive;
  final int usersSuspended;
  final int discussionsPending;
  final int discussionsPublished;
  final int discussionsHidden;
  final int openReports;
  final int openAppeals;
  final int verifiedPredictions;
  final int walletPointsTotal;
  final int notificationsToday;

  factory AdminOverview.fromJson(Map<String, dynamic> json) {
    int value(String key) => json[key] as int? ?? 0;
    return AdminOverview(
      usersTotal: value('users_total'),
      usersActive: value('users_active'),
      usersSuspended: value('users_suspended'),
      discussionsPending: value('discussions_pending'),
      discussionsPublished: value('discussions_published'),
      discussionsHidden: value('discussions_hidden'),
      openReports: value('open_reports'),
      openAppeals: value('open_appeals'),
      verifiedPredictions: value('verified_predictions'),
      walletPointsTotal: value('wallet_points_total'),
      notificationsToday: value('notifications_today'),
    );
  }
}

class OperationalSetting {
  const OperationalSetting({
    required this.key,
    required this.category,
    required this.label,
    required this.description,
    required this.kind,
    required this.value,
    required this.minValue,
    required this.maxValue,
  });

  final String key;
  final String category;
  final String label;
  final String description;
  final String kind;
  final Object value;
  final num? minValue;
  final num? maxValue;

  factory OperationalSetting.fromJson(Map<String, dynamic> json) {
    return OperationalSetting(
      key: json['key'] as String,
      category: json['category'] as String,
      label: json['label'] as String,
      description: json['description'] as String,
      kind: json['kind'] as String,
      value: json['value'] as Object,
      minValue: json['min_value'] as num?,
      maxValue: json['max_value'] as num?,
    );
  }
}

class ServiceHealth {
  const ServiceHealth({
    required this.component,
    required this.provider,
    required this.status,
    required this.latencyMs,
    required this.observedAt,
  });

  final String component;
  final String provider;
  final String status;
  final int? latencyMs;
  final DateTime observedAt;

  factory ServiceHealth.fromJson(Map<String, dynamic> json) {
    return ServiceHealth(
      component: json['component'] as String,
      provider: json['provider'] as String,
      status: json['status'] as String,
      latencyMs: json['latency_ms'] as int?,
      observedAt: DateTime.parse(json['observed_at'] as String),
    );
  }
}

class AdminUserItem {
  const AdminUserItem({
    required this.id,
    required this.email,
    required this.displayName,
    required this.status,
    required this.planCode,
    required this.balancePoints,
    required this.discussionsCount,
  });

  final String id;
  final String email;
  final String displayName;
  final String status;
  final String planCode;
  final int balancePoints;
  final int discussionsCount;

  factory AdminUserItem.fromJson(Map<String, dynamic> json) {
    return AdminUserItem(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String,
      status: json['status'] as String,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int? ?? 0,
      discussionsCount: json['discussions_count'] as int? ?? 0,
    );
  }
}

class AdminAuditItem {
  const AdminAuditItem({
    required this.action,
    required this.reasonCode,
    required this.details,
    required this.createdAt,
  });

  final String action;
  final String? reasonCode;
  final Map<String, dynamic> details;
  final DateTime createdAt;

  factory AdminAuditItem.fromJson(Map<String, dynamic> json) {
    return AdminAuditItem(
      action: json['action'] as String,
      reasonCode: json['reason_code'] as String?,
      details: _map(json['details']),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class AdminDiscussionItem {
  const AdminDiscussionItem({
    required this.discussion,
    required this.openReportCount,
  });

  final CommunityDiscussion discussion;
  final int openReportCount;

  factory AdminDiscussionItem.fromJson(Map<String, dynamic> json) {
    return AdminDiscussionItem(
      discussion: CommunityDiscussion.fromJson(_map(json['discussion'])),
      openReportCount: json['open_report_count'] as int? ?? 0,
    );
  }
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return <String, dynamic>{};
}

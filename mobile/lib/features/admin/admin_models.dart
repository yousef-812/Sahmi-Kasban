import 'dart:collection';

import '../community/community_models.dart';

class AdminOverview {
  const AdminOverview({
    required this.usersTotal,
    required this.usersActive,
    required this.usersSuspended,
    required this.usersVerified,
    required this.usersUnverified,
    required this.usersActiveNow,
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
  final int usersVerified;
  final int usersUnverified;
  final int usersActiveNow;
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
      usersVerified: value('users_verified'),
      usersUnverified: value('users_unverified'),
      usersActiveNow: value('users_active_now'),
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

  String get componentLabel => switch (component) {
    'market_data' => 'بيانات السوق',
    'ai' => 'الذكاء الاصطناعي',
    _ => 'خدمة تشغيلية',
  };

  String get providerLabel => switch (provider) {
    'tradingview' => 'TradingView',
    'yfinance' => 'Yahoo Finance الاحتياطي',
    'tradingview+yfinance' => 'TradingView ثم Yahoo Finance',
    'configured_ai' => 'مزود الذكاء الاصطناعي',
    _ => provider,
  };

  String get statusLabel => switch (status) {
    'healthy' => 'سليم',
    'degraded' => 'يعمل بصورة جزئية',
    'failed' => 'متعطل',
    _ => 'غير معروف',
  };

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
    final rawReason = json['reason_code'] as String?;
    return AdminAuditItem(
      action: _auditActionLabel(json['action'] as String? ?? ''),
      reasonCode: rawReason == null ? null : _auditReasonLabel(rawReason),
      details: _ReadableAuditDetails(_map(json['details'])),
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

class _ReadableAuditDetails extends MapBase<String, dynamic> {
  _ReadableAuditDetails(this._source);

  final Map<String, dynamic> _source;

  @override
  dynamic operator [](Object? key) => _source[key];

  @override
  void operator []=(String key, dynamic value) => _source[key] = value;

  @override
  void clear() => _source.clear();

  @override
  Iterable<String> get keys => _source.keys;

  @override
  dynamic remove(Object? key) => _source.remove(key);

  @override
  String toString() {
    final lines = <String>[];
    for (final entry in _source.entries) {
      if (_hiddenAuditKeys.contains(entry.key)) continue;
      final label = _auditDetailLabel(entry.key);
      final value = _auditValue(entry.value);
      if (value.isNotEmpty) lines.add('$label: $value');
    }
    return lines.isEmpty ? 'لا توجد تفاصيل إضافية.' : lines.join('\n');
  }
}

const _hiddenAuditKeys = <String>{
  'request_id',
  'idempotency_key',
  'data_fingerprint',
  'before_payload',
  'after_payload',
  'token_hash',
};

String _auditActionLabel(String value) => switch (value) {
  'discussion_approved' || 'approve_discussion' => 'قبول مناقشة ونشرها',
  'discussion_rejected' || 'reject_discussion' => 'رفض مناقشة',
  'discussion_hidden' || 'hide_discussion' => 'إخفاء مناقشة',
  'discussion_restored' || 'restore_discussion' => 'استعادة مناقشة',
  'user_blocked' || 'block_user' => 'حظر مستخدم',
  'user_unblocked' || 'unblock_user' => 'إلغاء حظر مستخدم',
  'setting_updated' || 'update_operational_setting' => 'تعديل إعداد تشغيلي',
  'notification_broadcast' || 'broadcast_notification' => 'إرسال إشعار جماعي',
  'performance_outcome_corrected' ||
  'correct_performance_outcome' => 'تصحيح نتيجة أداء موثقة',
  'admin_wallet_credit' ||
  'wallet_credit' ||
  'credit_user_wallet' => 'إضافة عملات لمستخدم',
  'report_refund' || 'refund_discussion' => 'إرجاع رصيد لمستخدم',
  _ => 'إجراء إداري',
};

String _auditReasonLabel(String value) => switch (value) {
  'manual_rejection' => 'رفض يدوي بعد المراجعة',
  'policy_violation' => 'مخالفة سياسة النشر',
  'provider_unavailable' => 'تعذر مزود الخدمة',
  'admin_credit' => 'إضافة رصيد بواسطة الإدارة',
  'performance_correction' => 'تصحيح بيانات جلسة السوق',
  'user_request' => 'بناءً على طلب المستخدم',
  _ => 'سبب إداري مسجل',
};

String _auditDetailLabel(String key) => switch (key) {
  'setting_key' || 'key' => 'الإعداد',
  'old_value' || 'before' => 'القيمة السابقة',
  'new_value' || 'after' => 'القيمة الجديدة',
  'amount_coins' => 'العملات المضافة',
  'amount_points' => 'النقاط المضافة',
  'balance_before_points' => 'الرصيد قبل العملية',
  'balance_after_points' => 'الرصيد بعد العملية',
  'title' => 'العنوان',
  'body' => 'النص',
  'notifications_created' || 'recipients' => 'عدد المستلمين',
  'ticker' => 'السهم',
  'report_id' => 'التقرير',
  'discussion_id' => 'المناقشة',
  'target_user_id' || 'user_id' => 'المستخدم',
  'provider' => 'المزود',
  'status' => 'الحالة',
  'reason' => 'السبب',
  'score_bp' => 'الدرجة',
  'strength' => 'التقييم',
  _ => 'تفصيل',
};

String _auditValue(Object? value) {
  if (value == null) return '';
  if (value is bool) return value ? 'نعم' : 'لا';
  if (value is num) return value.toString();
  if (value is List) {
    return value.map(_auditValue).where((item) => item.isNotEmpty).join('، ');
  }
  if (value is Map) {
    final readable = _ReadableAuditDetails(Map<String, dynamic>.from(value));
    return readable.toString().replaceAll('\n', '، ');
  }
  final text = value.toString();
  return switch (text) {
    'active' => 'نشط',
    'suspended' => 'محظور',
    'free' => 'مجانية',
    'basic' => 'أساسية',
    'advanced' => 'متقدمة',
    'pro' => 'احترافية',
    'healthy' => 'سليم',
    'degraded' => 'جزئي',
    'failed' => 'فاشل',
    _ =>
      text.length > 36 && text.contains('-')
          ? '${text.substring(0, 8)}…'
          : text,
  };
}

Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return <String, dynamic>{};
}

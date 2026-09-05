class CommunityAuthor {
  const CommunityAuthor({
    required this.userId,
    required this.displayName,
    required this.avatarKey,
  });

  final String userId;
  final String displayName;
  final String avatarKey;

  factory CommunityAuthor.fromJson(Map<String, dynamic> json) {
    return CommunityAuthor(
      userId: _requiredString(json, 'user_id'),
      displayName: _requiredString(json, 'display_name'),
      avatarKey: _requiredString(json, 'avatar_key'),
    );
  }
}

class CommunityDiscussion {
  const CommunityDiscussion({
    required this.id,
    required this.ticker,
    required this.title,
    required this.content,
    required this.periodType,
    required this.status,
    required this.moderationResult,
    required this.frozenPrediction,
    required this.rejectionCode,
    required this.createdAt,
    required this.reviewedAt,
    required this.publishedAt,
    required this.author,
    this.viewsCount = 0,
    this.agreeCount = 0,
    this.disagreeCount = 0,
    this.userReaction,
  });

  final String id;
  final String ticker;
  final String title;
  final String content;
  final String periodType;
  final String status;
  final Map<String, dynamic> moderationResult;
  final Map<String, dynamic> frozenPrediction;
  final String? rejectionCode;
  final DateTime createdAt;
  final DateTime? reviewedAt;
  final DateTime? publishedAt;
  final CommunityAuthor author;
  final int viewsCount;
  final int agreeCount;
  final int disagreeCount;
  final String? userReaction;

  bool get canAppeal => status == 'rejected' || status == 'hidden';

  String get periodLabel => switch (periodType) {
    'next_session' => 'الجلسة القادمة',
    'week' => 'أسبوع',
    'month' => 'شهر',
    _ => periodType,
  };

  String get statusLabel => switch (status) {
    'pending_review' => 'قيد المراجعة',
    'published' => 'منشورة',
    'rejected' => 'مرفوضة',
    'hidden' => 'مخفية',
    _ => status,
  };

  factory CommunityDiscussion.fromJson(Map<String, dynamic> json) {
    return CommunityDiscussion(
      id: _requiredString(json, 'id'),
      ticker: _requiredString(json, 'ticker'),
      title: _requiredString(json, 'title'),
      content: _requiredString(json, 'content'),
      periodType: _requiredString(json, 'period_type'),
      status: _requiredString(json, 'status'),
      moderationResult: _mapOrEmpty(json['moderation_result']),
      frozenPrediction: _mapOrEmpty(json['frozen_prediction']),
      rejectionCode: json['rejection_code'] as String?,
      createdAt: _requiredDate(json, 'created_at'),
      reviewedAt: _optionalDate(json['reviewed_at']),
      publishedAt: _optionalDate(json['published_at']),
      author: CommunityAuthor.fromJson(_requiredMap(json['author'])),
      viewsCount: (json['views_count'] as num?)?.toInt() ?? 0,
      agreeCount: (json['agree_count'] as num?)?.toInt() ?? 0,
      disagreeCount: (json['disagree_count'] as num?)?.toInt() ?? 0,
      userReaction: json['user_reaction'] as String?,
    );
  }
}

class CommunityDiscussionPage {
  const CommunityDiscussionPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<CommunityDiscussion> items;
  final int total;
  final int limit;
  final int offset;

  bool get hasMore => offset + items.length < total;

  factory CommunityDiscussionPage.fromJson(Map<String, dynamic> json) {
    return CommunityDiscussionPage(
      items: _requiredList(json['items'])
          .map((item) => CommunityDiscussion.fromJson(_requiredMap(item)))
          .toList(growable: false),
      total: _requiredInt(json, 'total'),
      limit: _requiredInt(json, 'limit'),
      offset: _requiredInt(json, 'offset'),
    );
  }
}

class CommunityDiscussionSubmission {
  const CommunityDiscussionSubmission({
    required this.discussion,
    required this.heldPoints,
    required this.heldCoins,
    required this.balancePoints,
    required this.balanceCoins,
    required this.idempotent,
  });

  final CommunityDiscussion discussion;
  final int heldPoints;
  final String heldCoins;
  final int balancePoints;
  final String balanceCoins;
  final bool idempotent;

  factory CommunityDiscussionSubmission.fromJson(Map<String, dynamic> json) {
    return CommunityDiscussionSubmission(
      discussion: CommunityDiscussion.fromJson(
        _requiredMap(json['discussion']),
      ),
      heldPoints: _requiredInt(json, 'held_points'),
      heldCoins: _requiredString(json, 'held_coins'),
      balancePoints: _requiredInt(json, 'balance_points'),
      balanceCoins: _requiredString(json, 'balance_coins'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class CommunityReportResult {
  const CommunityReportResult({
    required this.reportId,
    required this.discussionId,
    required this.status,
    required this.idempotent,
  });

  final String reportId;
  final String discussionId;
  final String status;
  final bool idempotent;

  factory CommunityReportResult.fromJson(Map<String, dynamic> json) {
    return CommunityReportResult(
      reportId: _requiredString(json, 'report_id'),
      discussionId: _requiredString(json, 'discussion_id'),
      status: _requiredString(json, 'status'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class CommunityMuteResult {
  const CommunityMuteResult({
    required this.mutedUserId,
    required this.muted,
    required this.idempotent,
  });

  final String mutedUserId;
  final bool muted;
  final bool idempotent;

  factory CommunityMuteResult.fromJson(Map<String, dynamic> json) {
    return CommunityMuteResult(
      mutedUserId: _requiredString(json, 'muted_user_id'),
      muted: _requiredBool(json, 'muted'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class CommunityAppeal {
  const CommunityAppeal({
    required this.id,
    required this.discussionId,
    required this.userId,
    required this.sourceStatus,
    required this.message,
    required this.status,
    required this.createdAt,
    required this.resolvedAt,
    required this.resolutionReasonCode,
    required this.resolutionDetails,
  });

  final String id;
  final String discussionId;
  final String userId;
  final String sourceStatus;
  final String message;
  final String status;
  final DateTime createdAt;
  final DateTime? resolvedAt;
  final String? resolutionReasonCode;
  final Map<String, dynamic> resolutionDetails;

  String get statusLabel => switch (status) {
    'open' => 'قيد المراجعة',
    'accepted' => 'مقبول',
    'rejected' => 'مرفوض',
    _ => status,
  };

  factory CommunityAppeal.fromJson(Map<String, dynamic> json) {
    return CommunityAppeal(
      id: _requiredString(json, 'id'),
      discussionId: _requiredString(json, 'discussion_id'),
      userId: _requiredString(json, 'user_id'),
      sourceStatus: _requiredString(json, 'source_status'),
      message: _requiredString(json, 'message'),
      status: _requiredString(json, 'status'),
      createdAt: _requiredDate(json, 'created_at'),
      resolvedAt: _optionalDate(json['resolved_at']),
      resolutionReasonCode: json['resolution_reason_code'] as String?,
      resolutionDetails: _mapOrEmpty(json['resolution_details']),
    );
  }
}

class CommunityAppealPage {
  const CommunityAppealPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<CommunityAppeal> items;
  final int total;
  final int limit;
  final int offset;

  factory CommunityAppealPage.fromJson(Map<String, dynamic> json) {
    return CommunityAppealPage(
      items: _requiredList(json['items'])
          .map((item) => CommunityAppeal.fromJson(_requiredMap(item)))
          .toList(growable: false),
      total: _requiredInt(json, 'total'),
      limit: _requiredInt(json, 'limit'),
      offset: _requiredInt(json, 'offset'),
    );
  }
}

class CommunityAppealSubmission {
  const CommunityAppealSubmission({
    required this.appeal,
    required this.idempotent,
  });

  final CommunityAppeal appeal;
  final bool idempotent;

  factory CommunityAppealSubmission.fromJson(Map<String, dynamic> json) {
    return CommunityAppealSubmission(
      appeal: CommunityAppeal.fromJson(_requiredMap(json['appeal'])),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

Map<String, dynamic> _requiredMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  throw const FormatException('Expected a JSON object.');
}

Map<String, dynamic> _mapOrEmpty(Object? value) {
  if (value == null) {
    return const <String, dynamic>{};
  }
  return _requiredMap(value);
}

List<Object?> _requiredList(Object? value) {
  if (value is List) {
    return List<Object?>.from(value);
  }
  throw const FormatException('Expected a JSON list.');
}

String _requiredString(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

int _requiredInt(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is int) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

bool _requiredBool(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is bool) {
    return value;
  }
  throw FormatException('Missing or invalid $key.');
}

DateTime _requiredDate(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is String) {
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return parsed;
    }
  }
  throw FormatException('Missing or invalid $key.');
}

DateTime? _optionalDate(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is String) {
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return parsed;
    }
  }
  throw const FormatException('Invalid optional date.');
}

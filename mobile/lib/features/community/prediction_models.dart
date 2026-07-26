class PredictionVerification {
  const PredictionVerification({
    required this.id,
    required this.discussionId,
    required this.scoreBp,
    required this.scorePercent,
    required this.strength,
    required this.rewardPoints,
    required this.rewardCoins,
    required this.evidence,
    required this.verifiedAt,
  });

  final String id;
  final String discussionId;
  final int scoreBp;
  final double scorePercent;
  final String strength;
  final int rewardPoints;
  final String rewardCoins;
  final Map<String, dynamic> evidence;
  final DateTime verifiedAt;

  String get strengthLabel => switch (strength) {
    'rejected' => 'غير مقبولة',
    'weak' => 'ضعيفة',
    'strong' => 'قوية',
    'very_strong' => 'قوية جدًا',
    _ => strength,
  };

  String get explanation {
    final value = evidence['explanation'];
    if (value is Map) {
      final reason = value['reason'];
      if (reason is String && reason.trim().isNotEmpty) {
        return reason.trim();
      }
    }
    return 'تم حساب النتيجة من بيانات السوق والقواعد الثابتة.';
  }

  factory PredictionVerification.fromJson(Map<String, dynamic> json) {
    return PredictionVerification(
      id: _requiredString(json, 'id'),
      discussionId: _requiredString(json, 'discussion_id'),
      scoreBp: _requiredInt(json, 'score_bp'),
      scorePercent: _requiredDouble(json, 'score_percent'),
      strength: _requiredString(json, 'strength'),
      rewardPoints: _requiredInt(json, 'reward_points'),
      rewardCoins: _requiredString(json, 'reward_coins'),
      evidence: _requiredMap(json['evidence']),
      verifiedAt: _requiredDate(json, 'verified_at'),
    );
  }
}

class PredictionVerificationStatus {
  const PredictionVerificationStatus({
    required this.discussionId,
    required this.state,
    required this.eligibleAt,
    required this.verification,
  });

  final String discussionId;
  final String state;
  final DateTime? eligibleAt;
  final PredictionVerification? verification;

  bool get isEligible => state == 'eligible';
  bool get isWaiting => state == 'waiting';
  bool get isVerified => state == 'verified' && verification != null;

  factory PredictionVerificationStatus.fromJson(Map<String, dynamic> json) {
    final verificationJson = json['verification'];
    return PredictionVerificationStatus(
      discussionId: _requiredString(json, 'discussion_id'),
      state: _requiredString(json, 'state'),
      eligibleAt: _optionalDate(json['eligible_at']),
      verification: verificationJson == null
          ? null
          : PredictionVerification.fromJson(_requiredMap(verificationJson)),
    );
  }
}

class PredictionVerificationSubmission {
  const PredictionVerificationSubmission({
    required this.verification,
    required this.balancePoints,
    required this.balanceCoins,
    required this.idempotent,
  });

  final PredictionVerification verification;
  final int balancePoints;
  final String balanceCoins;
  final bool idempotent;

  factory PredictionVerificationSubmission.fromJson(Map<String, dynamic> json) {
    return PredictionVerificationSubmission(
      verification: PredictionVerification.fromJson(
        _requiredMap(json['verification']),
      ),
      balancePoints: _requiredInt(json, 'balance_points'),
      balanceCoins: _requiredString(json, 'balance_coins'),
      idempotent: _requiredBool(json, 'idempotent'),
    );
  }
}

class PredictionStats {
  const PredictionStats({
    required this.verifiedPredictions,
    required this.acceptedPredictions,
    required this.accuracyPercent,
    required this.averageScorePercent,
    required this.totalRewardPoints,
    required this.totalRewardCoins,
  });

  final int verifiedPredictions;
  final int acceptedPredictions;
  final double accuracyPercent;
  final double averageScorePercent;
  final int totalRewardPoints;
  final String totalRewardCoins;

  factory PredictionStats.fromJson(Map<String, dynamic> json) {
    return PredictionStats(
      verifiedPredictions: _requiredInt(json, 'verified_predictions'),
      acceptedPredictions: _requiredInt(json, 'accepted_predictions'),
      accuracyPercent: _requiredDouble(json, 'accuracy_percent'),
      averageScorePercent: _requiredDouble(json, 'average_score_percent'),
      totalRewardPoints: _requiredInt(json, 'total_reward_points'),
      totalRewardCoins: _requiredString(json, 'total_reward_coins'),
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

double _requiredDouble(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is num) {
    return value.toDouble();
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

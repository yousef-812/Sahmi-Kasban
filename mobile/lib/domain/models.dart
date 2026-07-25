class TokenPair {
  const TokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  final String accessToken;
  final String refreshToken;
  final int expiresIn;

  factory TokenPair.fromJson(Map<String, dynamic> json) {
    return TokenPair(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      expiresIn: json['expires_in'] as int,
    );
  }
}

class RegistrationResult {
  const RegistrationResult({
    required this.userId,
    required this.email,
    required this.requiresEmailVerification,
    required this.weeklyPointsGranted,
  });

  final String userId;
  final String email;
  final bool requiresEmailVerification;
  final int weeklyPointsGranted;

  factory RegistrationResult.fromJson(Map<String, dynamic> json) {
    return RegistrationResult(
      userId: json['user_id'] as String,
      email: json['email'] as String,
      requiresEmailVerification:
          json['requires_email_verification'] as bool? ?? true,
      weeklyPointsGranted: json['weekly_points_granted'] as int? ?? 300,
    );
  }
}

class UserProfile {
  const UserProfile({
    required this.id,
    required this.email,
    required this.displayName,
    required this.avatarKey,
    required this.emailVerified,
    required this.planCode,
    required this.balancePoints,
    required this.balanceCoins,
    required this.weeklyCoins,
    required this.adsEnabled,
  });

  final String id;
  final String email;
  final String displayName;
  final String avatarKey;
  final bool emailVerified;
  final String planCode;
  final int balancePoints;
  final String balanceCoins;
  final String weeklyCoins;
  final bool adsEnabled;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String,
      avatarKey: json['avatar_key'] as String,
      emailVerified: json['email_verified'] as bool,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
    );
  }
}

class WalletSummary {
  const WalletSummary({
    required this.balancePoints,
    required this.balanceCoins,
    required this.planCode,
    required this.weeklyCoins,
    required this.adsEnabled,
  });

  final int balancePoints;
  final String balanceCoins;
  final String planCode;
  final String weeklyCoins;
  final bool adsEnabled;

  factory WalletSummary.fromJson(Map<String, dynamic> json) {
    return WalletSummary(
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      planCode: json['plan_code'] as String,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
    );
  }
}

class MarketReportPreview {
  const MarketReportPreview({
    required this.reportId,
    required this.sourceSessionDate,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.status,
    required this.itemCount,
    required this.unlocked,
    required this.unlockCostPoints,
    required this.unlockCostCoins,
    required this.marketSummary,
  });

  final String reportId;
  final DateTime sourceSessionDate;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final String status;
  final int itemCount;
  final bool unlocked;
  final int unlockCostPoints;
  final String unlockCostCoins;
  final Map<String, dynamic> marketSummary;

  factory MarketReportPreview.fromJson(Map<String, dynamic> json) {
    return MarketReportPreview(
      reportId: json['report_id'] as String,
      sourceSessionDate: DateTime.parse(json['source_session_date'] as String),
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      status: json['status'] as String,
      itemCount: json['item_count'] as int,
      unlocked: json['unlocked'] as bool,
      unlockCostPoints: json['unlock_cost_points'] as int,
      unlockCostCoins: json['unlock_cost_coins'] as String,
      marketSummary: Map<String, dynamic>.from(
        json['market_summary'] as Map<dynamic, dynamic>,
      ),
    );
  }
}

class MonetizationPlan {
  const MonetizationPlan({
    required this.code,
    required this.displayNameAr,
    required this.weeklyPoints,
    required this.weeklyCoins,
    required this.adsEnabled,
    required this.productId,
    required this.historyLimit,
    required this.reportHistoryDays,
    required this.features,
    required this.comparisonMonthlyAllowance,
    required this.maxComparisonStocks,
    required this.priorityLevel,
    required this.badgeCode,
  });

  final String code;
  final String displayNameAr;
  final int weeklyPoints;
  final String weeklyCoins;
  final bool adsEnabled;
  final String? productId;
  final int historyLimit;
  final int reportHistoryDays;
  final List<String> features;
  final int comparisonMonthlyAllowance;
  final int maxComparisonStocks;
  final int priorityLevel;
  final String? badgeCode;

  factory MonetizationPlan.fromJson(Map<String, dynamic> json) {
    return MonetizationPlan(
      code: json['code'] as String,
      displayNameAr: json['display_name_ar'] as String,
      weeklyPoints: json['weekly_points'] as int,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
      productId: json['product_id'] as String?,
      historyLimit: json['history_limit'] as int,
      reportHistoryDays: json['report_history_days'] as int,
      features: _list(json['features'])
          .map((value) => value.toString())
          .toList(growable: false),
      comparisonMonthlyAllowance:
          json['comparison_monthly_allowance'] as int? ?? 0,
      maxComparisonStocks: json['max_comparison_stocks'] as int? ?? 0,
      priorityLevel: json['priority_level'] as int? ?? 0,
      badgeCode: json['badge_code'] as String?,
    );
  }
}

class CoinPack {
  const CoinPack({
    required this.productId,
    required this.displayNameAr,
    required this.points,
    required this.coins,
  });

  final String productId;
  final String displayNameAr;
  final int points;
  final String coins;

  factory CoinPack.fromJson(Map<String, dynamic> json) {
    return CoinPack(
      productId: json['product_id'] as String,
      displayNameAr: json['display_name_ar'] as String,
      points: json['points'] as int,
      coins: json['coins'] as String,
    );
  }
}

class MonetizationCatalog {
  const MonetizationCatalog({
    required this.plans,
    required this.coinPacks,
    required this.adRewardPoints,
    required this.adRewardCoins,
    required this.adRewardDailyLimit,
    required this.adRewardCooldownSeconds,
  });

  final List<MonetizationPlan> plans;
  final List<CoinPack> coinPacks;
  final int adRewardPoints;
  final String adRewardCoins;
  final int adRewardDailyLimit;
  final int adRewardCooldownSeconds;

  Set<String> get storeProductIds => <String>{
    ...plans.map((plan) => plan.productId).whereType<String>(),
    ...coinPacks.map((pack) => pack.productId),
  };

  bool isCoinPack(String productId) {
    return coinPacks.any((pack) => pack.productId == productId);
  }

  factory MonetizationCatalog.fromJson(Map<String, dynamic> json) {
    return MonetizationCatalog(
      plans: _list(json['plans'])
          .map((value) => MonetizationPlan.fromJson(_map(value)))
          .toList(growable: false),
      coinPacks: _list(
        json['coin_packs'],
      ).map((value) => CoinPack.fromJson(_map(value))).toList(growable: false),
      adRewardPoints: json['ad_reward_points'] as int,
      adRewardCoins: json['ad_reward_coins'] as String,
      adRewardDailyLimit: json['ad_reward_daily_limit'] as int,
      adRewardCooldownSeconds: json['ad_reward_cooldown_seconds'] as int,
    );
  }
}

class RewardedAdEligibilityModel {
  const RewardedAdEligibilityModel({
    required this.eligible,
    required this.reason,
    required this.rewardsUsedToday,
    required this.rewardsRemainingToday,
    required this.nextAvailableAt,
  });

  final bool eligible;
  final String? reason;
  final int rewardsUsedToday;
  final int rewardsRemainingToday;
  final DateTime? nextAvailableAt;

  factory RewardedAdEligibilityModel.fromJson(Map<String, dynamic> json) {
    return RewardedAdEligibilityModel(
      eligible: json['eligible'] as bool,
      reason: json['reason'] as String?,
      rewardsUsedToday: json['rewards_used_today'] as int,
      rewardsRemainingToday: json['rewards_remaining_today'] as int,
      nextAvailableAt: json['next_available_at'] == null
          ? null
          : DateTime.parse(json['next_available_at'] as String),
    );
  }
}

class MonetizationStatusModel {
  const MonetizationStatusModel({
    required this.planCode,
    required this.subscriptionStatus,
    required this.subscriptionExpiresAt,
    required this.weeklyPoints,
    required this.weeklyCoins,
    required this.adsEnabled,
    required this.rewardedAd,
  });

  final String planCode;
  final String subscriptionStatus;
  final DateTime? subscriptionExpiresAt;
  final int weeklyPoints;
  final String weeklyCoins;
  final bool adsEnabled;
  final RewardedAdEligibilityModel rewardedAd;

  factory MonetizationStatusModel.fromJson(Map<String, dynamic> json) {
    return MonetizationStatusModel(
      planCode: json['plan_code'] as String,
      subscriptionStatus: json['subscription_status'] as String,
      subscriptionExpiresAt: json['subscription_expires_at'] == null
          ? null
          : DateTime.parse(json['subscription_expires_at'] as String),
      weeklyPoints: json['weekly_points'] as int,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
      rewardedAd: RewardedAdEligibilityModel.fromJson(
        _map(json['rewarded_ad']),
      ),
    );
  }
}

class RewardedAdSessionModel {
  const RewardedAdSessionModel({
    required this.sessionId,
    required this.adUnitId,
    required this.customData,
    required this.expiresAt,
    required this.testMode,
  });

  final String sessionId;
  final String adUnitId;
  final String customData;
  final DateTime expiresAt;
  final bool testMode;

  factory RewardedAdSessionModel.fromJson(Map<String, dynamic> json) {
    return RewardedAdSessionModel(
      sessionId: json['session_id'] as String,
      adUnitId: json['ad_unit_id'] as String,
      customData: json['custom_data'] as String,
      expiresAt: DateTime.parse(json['expires_at'] as String),
      testMode: json['test_mode'] as bool? ?? false,
    );
  }
}

class RewardedAdSimulationResultModel {
  const RewardedAdSimulationResultModel({
    required this.idempotent,
    required this.balancePoints,
    required this.balanceCoins,
  });

  final bool idempotent;
  final int balancePoints;
  final String balanceCoins;

  factory RewardedAdSimulationResultModel.fromJson(Map<String, dynamic> json) {
    return RewardedAdSimulationResultModel(
      idempotent: json['idempotent'] as bool,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
    );
  }
}

class PurchaseVerificationResultModel {
  const PurchaseVerificationResultModel({
    required this.purchaseId,
    required this.productId,
    required this.productType,
    required this.purchaseState,
    required this.acknowledgementState,
    required this.entitlementGranted,
    required this.idempotent,
    required this.planCode,
    required this.balancePoints,
    required this.balanceCoins,
    required this.subscriptionExpiresAt,
  });

  final String purchaseId;
  final String productId;
  final String productType;
  final String purchaseState;
  final String acknowledgementState;
  final bool entitlementGranted;
  final bool idempotent;
  final String planCode;
  final int balancePoints;
  final String balanceCoins;
  final DateTime? subscriptionExpiresAt;

  factory PurchaseVerificationResultModel.fromJson(Map<String, dynamic> json) {
    return PurchaseVerificationResultModel(
      purchaseId: json['purchase_id'] as String,
      productId: json['product_id'] as String,
      productType: json['product_type'] as String,
      purchaseState: json['purchase_state'] as String,
      acknowledgementState: json['acknowledgement_state'] as String,
      entitlementGranted: json['entitlement_granted'] as bool,
      idempotent: json['idempotent'] as bool,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      subscriptionExpiresAt: json['subscription_expires_at'] == null
          ? null
          : DateTime.parse(json['subscription_expires_at'] as String),
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

List<dynamic> _list(Object? value) {
  return value is List ? value : const <dynamic>[];
}

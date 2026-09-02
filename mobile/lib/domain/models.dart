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
    this.isAdmin = false,
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
  final bool isAdmin;
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
      isAdmin: json['is_admin'] as bool? ?? false,
      planCode: json['plan_code'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      weeklyCoins: json['weekly_coins'] as String,
      adsEnabled: json['ads_enabled'] as bool,
    );
  }
}

class AvatarOption {
  const AvatarOption({required this.key, required this.assetPath});

  final String key;
  final String assetPath;

  factory AvatarOption.fromJson(Map<String, dynamic> json) {
    return AvatarOption(
      key: json['key'] as String,
      assetPath: json['asset_path'] as String,
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

class WalletEntryModel {
  const WalletEntryModel({
    required this.transactionId,
    required this.entryType,
    required this.amountPoints,
    required this.amountCoins,
    required this.status,
    required this.referenceType,
    required this.referenceId,
    required this.details,
    required this.createdAt,
    required this.confirmedAt,
  });

  final String transactionId;
  final String entryType;
  final int amountPoints;
  final String amountCoins;
  final String status;
  final String? referenceType;
  final String? referenceId;
  final Map<String, dynamic> details;
  final DateTime createdAt;
  final DateTime? confirmedAt;

  factory WalletEntryModel.fromJson(Map<String, dynamic> json) {
    return WalletEntryModel(
      transactionId: json['transaction_id'] as String,
      entryType: json['entry_type'] as String,
      amountPoints: json['amount_points'] as int,
      amountCoins: json['amount_coins'] as String,
      status: json['status'] as String,
      referenceType: json['reference_type'] as String?,
      referenceId: json['reference_id'] as String?,
      details: _map(json['details']),
      createdAt: DateTime.parse(json['created_at'] as String),
      confirmedAt: json['confirmed_at'] == null
          ? null
          : DateTime.parse(json['confirmed_at'] as String),
    );
  }
}

class WalletHistoryPage {
  const WalletHistoryPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  final List<WalletEntryModel> items;
  final int total;
  final int limit;
  final int offset;

  factory WalletHistoryPage.fromJson(Map<String, dynamic> json) {
    return WalletHistoryPage(
      items: _list(json['items'])
          .map((item) => WalletEntryModel.fromJson(_map(item)))
          .toList(growable: false),
      total: json['total'] as int,
      limit: json['limit'] as int,
      offset: json['offset'] as int,
    );
  }
}

class MarketInstrument {
  const MarketInstrument({
    required this.ticker,
    required this.providerSymbol,
    required this.exchange,
    this.description = '',
  });

  final String ticker;
  final String providerSymbol;
  final String exchange;
  final String description;

  factory MarketInstrument.fromJson(Map<String, dynamic> json) {
    return MarketInstrument(
      ticker: json['ticker'] as String,
      providerSymbol: json['provider_symbol'] as String,
      exchange: json['exchange'] as String,
      description: json['description'] as String? ?? '',
    );
  }
}

class MarketQuote {
  const MarketQuote({
    required this.ticker,
    required this.description,
    required this.exchange,
    this.sector,
    this.currentPrice,
    this.openPrice,
    this.previousClose,
    this.sessionHigh,
    this.sessionLow,
    this.change,
    this.changePercent,
    this.volume,
    this.week52High,
    this.week52Low,
    this.marketOpen = false,
    this.sessionChangePercent,
    this.sessionDate,
    this.nextSessionOpen,
  });

  final String ticker;
  final String description;
  final String exchange;
  final String? sector;
  final double? currentPrice;
  final double? openPrice;
  final double? previousClose;
  final double? sessionHigh;
  final double? sessionLow;
  final double? change;
  final double? changePercent;
  final double? volume;
  final double? week52High;
  final double? week52Low;
  final bool marketOpen;
  final double? sessionChangePercent;
  final String? sessionDate;
  final DateTime? nextSessionOpen;

  factory MarketQuote.fromJson(Map<String, dynamic> json) {
    return MarketQuote(
      ticker: json['ticker'] as String,
      description: json['description'] as String? ?? '',
      exchange: json['exchange'] as String? ?? 'EGX',
      sector: json['sector'] as String?,
      currentPrice: _asDouble(json['current_price']),
      openPrice: _asDouble(json['open_price']),
      previousClose: _asDouble(json['previous_close']),
      sessionHigh: _asDouble(json['session_high']),
      sessionLow: _asDouble(json['session_low']),
      change: _asDouble(json['change']),
      changePercent: _asDouble(json['change_percent']),
      volume: _asDouble(json['volume']),
      week52High: _asDouble(json['week52_high']),
      week52Low: _asDouble(json['week52_low']),
      marketOpen: json['market_open'] as bool? ?? false,
      sessionChangePercent: _asDouble(json['session_change_percent']),
      sessionDate: json['session_date'] as String?,
      nextSessionOpen: json['next_session_open'] == null
          ? null
          : DateTime.tryParse(json['next_session_open'] as String),
    );
  }
}

class MarketQuotesSnapshot {
  const MarketQuotesSnapshot({
    required this.source,
    required this.generatedAt,
    required this.marketOpen,
    required this.items,
    this.nextSessionOpen,
  });

  final String source;
  final DateTime generatedAt;
  final bool marketOpen;
  final DateTime? nextSessionOpen;
  final List<MarketQuote> items;

  factory MarketQuotesSnapshot.fromJson(Map<String, dynamic> json) {
    return MarketQuotesSnapshot(
      source: json['source'] as String,
      generatedAt: DateTime.parse(json['generated_at'] as String),
      marketOpen: json['market_open'] as bool? ?? false,
      nextSessionOpen: json['next_session_open'] == null
          ? null
          : DateTime.tryParse(json['next_session_open'] as String),
      items: _list(
        json['items'],
      ).map((item) => MarketQuote.fromJson(_map(item))).toList(growable: false),
    );
  }
}

class StockAnalysisResult {
  const StockAnalysisResult({
    required this.analysisId,
    required this.ticker,
    required this.cached,
    required this.marketSnapshotCached,
    required this.chargedPoints,
    required this.chargedCoins,
    required this.balancePoints,
    required this.balanceCoins,
    required this.dataAsOf,
    required this.payload,
  });

  final String analysisId;
  final String ticker;
  final bool cached;
  final bool marketSnapshotCached;
  final int chargedPoints;
  final String chargedCoins;
  final int balancePoints;
  final String balanceCoins;
  final DateTime dataAsOf;
  final Map<String, dynamic> payload;

  factory StockAnalysisResult.fromJson(Map<String, dynamic> json) {
    return StockAnalysisResult(
      analysisId: json['analysis_id'] as String,
      ticker: json['ticker'] as String,
      cached: json['cached'] as bool,
      marketSnapshotCached: json['market_snapshot_cached'] as bool,
      chargedPoints: json['charged_points'] as int,
      chargedCoins: json['charged_coins'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      dataAsOf: DateTime.parse(json['data_as_of'] as String),
      payload: _map(json['payload']),
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
      marketSummary: _map(json['market_summary']),
    );
  }
}

class MarketReportHistory {
  const MarketReportHistory({
    required this.historyDaysAllowed,
    required this.planCode,
    required this.reports,
  });

  final int historyDaysAllowed;
  final String planCode;
  final List<MarketReportPreview> reports;

  factory MarketReportHistory.fromJson(Map<String, dynamic> json) {
    return MarketReportHistory(
      historyDaysAllowed: json['history_days_allowed'] as int? ?? 1,
      planCode: json['plan_code'] as String? ?? 'free',
      reports: (json['reports'] as List? ?? const [])
          .map((item) => MarketReportPreview.fromJson(_map(item)))
          .toList(growable: false),
    );
  }
}

class MarketReportItem {
  const MarketReportItem({
    required this.ticker,
    required this.rank,
    required this.score,
    required this.payload,
  });

  final String ticker;
  final int rank;
  final double score;
  final Map<String, dynamic> payload;

  factory MarketReportItem.fromJson(Map<String, dynamic> json) {
    return MarketReportItem(
      ticker: json['ticker'] as String,
      rank: json['rank'] as int,
      score: (json['score'] as num).toDouble(),
      payload: _map(json['payload']),
    );
  }
}

class MarketReport {
  const MarketReport({
    required this.reportId,
    required this.sourceSessionDate,
    required this.targetSessionDate,
    required this.generatedAt,
    required this.marketSummary,
    required this.items,
    required this.extendedItems,
  });

  final String reportId;
  final DateTime sourceSessionDate;
  final DateTime targetSessionDate;
  final DateTime generatedAt;
  final Map<String, dynamic> marketSummary;
  final List<MarketReportItem> items;
  final List<MarketReportItem> extendedItems;

  factory MarketReport.fromJson(Map<String, dynamic> json) {
    return MarketReport(
      reportId: json['report_id'] as String,
      sourceSessionDate: DateTime.parse(json['source_session_date'] as String),
      targetSessionDate: DateTime.parse(json['target_session_date'] as String),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      marketSummary: _map(json['market_summary']),
      items: _list(json['items'])
          .map((item) => MarketReportItem.fromJson(_map(item)))
          .toList(growable: false),
      extendedItems: _list(json['extended_items'])
          .map((item) => MarketReportItem.fromJson(_map(item)))
          .toList(growable: false),
    );
  }
}

class MarketReportUnlockResult {
  const MarketReportUnlockResult({
    required this.chargedPoints,
    required this.chargedCoins,
    required this.balancePoints,
    required this.balanceCoins,
    required this.report,
  });

  final int chargedPoints;
  final String chargedCoins;
  final int balancePoints;
  final String balanceCoins;
  final MarketReport report;

  factory MarketReportUnlockResult.fromJson(Map<String, dynamic> json) {
    return MarketReportUnlockResult(
      chargedPoints: json['charged_points'] as int,
      chargedCoins: json['charged_coins'] as String,
      balancePoints: json['balance_points'] as int,
      balanceCoins: json['balance_coins'] as String,
      report: MarketReport.fromJson(_map(json['report'])),
    );
  }
}

double? _asDouble(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  if (value is String) {
    return double.tryParse(value);
  }
  return null;
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

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

/// تحليلات المحفظة (GET /portfolio/analytics).
final portfolioAnalyticsProvider = FutureProvider.autoDispose<PortfolioAnalyticsSnapshot>((ref) {
  return ref.watch(backendRepositoryProvider).getPortfolioAnalytics();
});
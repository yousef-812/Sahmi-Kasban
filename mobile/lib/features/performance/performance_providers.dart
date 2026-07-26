import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'performance_models.dart';
import 'performance_repository.dart';

final performanceWindowProvider = StateProvider<int>((ref) => 7);

final performanceSummaryProvider =
    FutureProvider.autoDispose<PerformanceSummary>((ref) {
      final window = ref.watch(performanceWindowProvider);
      return ref.watch(performanceRepositoryProvider).summary(window);
    });

final performanceReportsProvider =
    FutureProvider.autoDispose<PerformanceReportPage>((ref) {
      return ref.watch(performanceRepositoryProvider).reports();
    });

final performanceReportDetailProvider = FutureProvider.autoDispose
    .family<PerformanceReportDetail, String>((ref, reportId) {
      return ref.watch(performanceRepositoryProvider).reportDetail(reportId);
    });

final delayedPerformanceProvider =
    FutureProvider.autoDispose<List<PerformanceDelayedItem>>((ref) {
      return ref.watch(performanceRepositoryProvider).delayed();
    });

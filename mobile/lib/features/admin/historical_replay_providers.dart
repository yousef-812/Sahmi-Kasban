import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'historical_replay_models.dart';
import 'admin_repository.dart';

final historicalReplayJobsProvider =
    FutureProvider.autoDispose<List<HistoricalReplayJob>>((ref) {
      return ref.watch(adminRepositoryProvider).historicalReplayJobs();
    });

final historicalReplayJobProvider = FutureProvider.autoDispose
    .family<HistoricalReplayJob, String>((ref, jobId) {
      return ref.watch(adminRepositoryProvider).historicalReplayJob(jobId);
    });

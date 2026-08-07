import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'labs_models.dart';
import 'labs_repository.dart';

final labsBacktestJobsProvider =
    FutureProvider<List<LabsBacktestJob>>((ref) {
      return ref.watch(labsRepositoryProvider).backtestJobs();
    });

final labsBacktestJobProvider =
    FutureProvider.autoDispose.family<LabsBacktestJob, String>(
      (ref, jobId) => ref.watch(labsRepositoryProvider).backtestJob(jobId),
    );

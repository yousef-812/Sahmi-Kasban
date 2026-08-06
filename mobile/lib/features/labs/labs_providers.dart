import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'labs_models.dart';
import 'labs_repository.dart';

final dailyReportBacktestProvider =
    FutureProvider.autoDispose.family<LabsBacktestResult, LabsBacktestQuery>(
      (ref, query) =>
          ref.watch(labsRepositoryProvider).dailyReportBacktest(query),
    );

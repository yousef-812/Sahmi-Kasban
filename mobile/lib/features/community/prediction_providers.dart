import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'prediction_models.dart';
import 'prediction_repository.dart';

final predictionVerificationStatusProvider = FutureProvider.autoDispose
    .family<PredictionVerificationStatus, String>((ref, discussionId) {
      return ref
          .watch(predictionRepositoryProvider)
          .getVerificationStatus(discussionId);
    });

final myPredictionStatsProvider = FutureProvider.autoDispose<PredictionStats>((
  ref,
) {
  return ref.watch(predictionRepositoryProvider).getMyStats();
});

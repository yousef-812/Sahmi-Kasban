import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

final latestReportPreviewProvider =
    FutureProvider.autoDispose<MarketReportPreview?>((ref) {
  return ref.watch(backendRepositoryProvider).getLatestReportPreview();
});

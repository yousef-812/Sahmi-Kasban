import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'community_repository.dart';

class RealViewTracker {
  static final Set<String> _recordedIds = <String>{};
  static final Set<String> _pendingBatch = <String>{};
  static Timer? _flushTimer;

  static bool isRecorded(String discussionId) {
    return _recordedIds.contains(discussionId);
  }

  static void recordView(WidgetRef ref, String discussionId) {
    if (_recordedIds.contains(discussionId)) {
      return;
    }
    _recordedIds.add(discussionId);
    _pendingBatch.add(discussionId);

    _scheduleFlush(ref);
  }

  static void _scheduleFlush(WidgetRef ref) {
    _flushTimer ??= Timer(const Duration(seconds: 3), () {
      flush(ref);
    });
  }

  static void flush(WidgetRef ref) {
    _flushTimer?.cancel();
    _flushTimer = null;

    if (_pendingBatch.isEmpty) {
      return;
    }

    final batch = _pendingBatch.toList();
    _pendingBatch.clear();

    ref.read(communityRepositoryProvider).registerViews(batch);
  }
}

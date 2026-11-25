import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'signals_models.dart';
import 'signals_repository.dart';

/// فلاتر قائمة الإشارات — `state` و`mine` و`ticker` تُمرَّر للخادم.
class SignalsFilter {
  const SignalsFilter({this.state, this.mine = false, this.ticker});

  /// حالة واحدة من `new/buy/t1done/t2done/t3done/tsl/closed/expired` أو `null` للكل.
  final String? state;

  /// `true` → الإشارات المملوكة للمتصل فقط (`mine=true`).
  final bool mine;

  /// رمز سهم معيّن (`GET /signals?ticker=`) أو `null` لكل الإشارات.
  final String? ticker;

  @override
  bool operator ==(Object other) =>
      other is SignalsFilter &&
      other.state == state &&
      other.mine == mine &&
      other.ticker == ticker;

  @override
  int get hashCode => Object.hash(state, mine, ticker);
}

final signalsListProvider = FutureProvider.autoDispose
    .family<ApiList<Signal>, SignalsFilter>((ref, filter) {
      return ref
          .watch(signalsRepositoryProvider)
          .list(state: filter.state, ticker: filter.ticker, mine: filter.mine);
    });

final signalDetailProvider = FutureProvider.autoDispose.family<Signal, String>((
  ref,
  signalId,
) {
  return ref.watch(signalsRepositoryProvider).detail(signalId);
});

/// يحمل قائمة التنبيهات ويحدّثها محليًا (تعليم مقروء) دون إعادة تحميل كاملة.
class AlertsController extends StateNotifier<AsyncValue<ApiList<AlertItem>>> {
  AlertsController(this._repository, {required this.unreadOnly})
    : super(const AsyncValue.loading()) {
    refresh();
  }

  final SignalsRepository _repository;
  final bool unreadOnly;

  Future<void> refresh() async {
    try {
      final page = await _repository.alerts(unreadOnly: unreadOnly);
      state = AsyncValue.data(page);
    } on Object catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> markRead(String alertId) async {
    final updated = await _repository.markAlertRead(alertId);
    final current = state.valueOrNull;
    if (current == null) return;
    state = AsyncValue.data(
      ApiList<AlertItem>(
        count: current.count,
        items: current.items
            .map((AlertItem item) => item.id == alertId ? updated : item)
            .toList(growable: false),
      ),
    );
  }

  Future<void> markAllRead() async {
    await _repository.markAllAlertsRead();
    final current = state.valueOrNull;
    if (current == null) return;
    state = AsyncValue.data(
      ApiList<AlertItem>(
        count: current.count,
        items: current.items
            .map((AlertItem item) => item.isRead ? item : item.markRead())
            .toList(growable: false),
      ),
    );
  }
}

final alertsControllerProvider = StateNotifierProvider.autoDispose
    .family<AlertsController, AsyncValue<ApiList<AlertItem>>, bool>((
      ref,
      unreadOnly,
    ) {
      return AlertsController(
        ref.watch(signalsRepositoryProvider),
        unreadOnly: unreadOnly,
      );
    });

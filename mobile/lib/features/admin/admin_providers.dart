import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_models.dart';
import 'admin_repository.dart';

final adminOverviewProvider = FutureProvider.autoDispose<AdminOverview>((ref) {
  return ref.watch(adminRepositoryProvider).overview();
});

final adminSettingsProvider =
    FutureProvider.autoDispose<List<OperationalSetting>>((ref) {
      return ref.watch(adminRepositoryProvider).settings();
    });

final adminProvidersProvider = FutureProvider.autoDispose<List<ServiceHealth>>((
  ref,
) {
  return ref.watch(adminRepositoryProvider).providers();
});

final adminUsersProvider = FutureProvider.autoDispose<List<AdminUserItem>>((
  ref,
) {
  return ref.watch(adminRepositoryProvider).users();
});

final adminAuditProvider = FutureProvider.autoDispose<List<AdminAuditItem>>((
  ref,
) {
  return ref.watch(adminRepositoryProvider).audit();
});

final adminDiscussionsProvider =
    FutureProvider.autoDispose<List<AdminDiscussionItem>>((ref) {
      return ref.watch(adminRepositoryProvider).discussions();
    });

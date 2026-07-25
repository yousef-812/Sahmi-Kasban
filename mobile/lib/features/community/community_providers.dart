import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'community_models.dart';
import 'community_repository.dart';

final communityTickerFilterProvider = StateProvider.autoDispose<String?>((ref) {
  return null;
});

final communityFeedProvider =
    FutureProvider.autoDispose<CommunityDiscussionPage>((ref) {
      final ticker = ref.watch(communityTickerFilterProvider);
      return ref
          .watch(communityRepositoryProvider)
          .listDiscussions(ticker: ticker);
    });

final myDiscussionsProvider =
    FutureProvider.autoDispose<CommunityDiscussionPage>((ref) {
      return ref.watch(communityRepositoryProvider).listMyDiscussions();
    });

final myAppealsProvider = FutureProvider.autoDispose<CommunityAppealPage>((
  ref,
) {
  return ref.watch(communityRepositoryProvider).listMyAppeals();
});

final communityDiscussionProvider = FutureProvider.autoDispose
    .family<CommunityDiscussion, String>((ref, discussionId) {
      return ref.watch(communityRepositoryProvider).getDiscussion(discussionId);
    });

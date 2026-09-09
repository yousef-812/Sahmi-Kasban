import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'community_models.dart';

class CommunityRepository {
  const CommunityRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<CommunityDiscussionPage> listDiscussions({
    String? ticker,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions',
        queryParameters: <String, dynamic>{
          if (ticker != null && ticker.trim().isNotEmpty)
            'ticker': ticker.trim().toUpperCase(),
          'limit': limit,
          'offset': offset,
        },
      );
      return CommunityDiscussionPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussionPage> listMyDiscussions({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions/mine',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return CommunityDiscussionPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussion> getDiscussion(String discussionId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/discussions/$discussionId',
      );
      return CommunityDiscussion.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<List<PredictionDateOption>> getPredictionDates() async {
    try {
      final response = await _apiClient.dio.get<List<dynamic>>(
        '/community/prediction-dates',
      );
      final list = response.data ?? [];
      return list
          .map(
            (item) => PredictionDateOption.fromJson(
              Map<String, dynamic>.from(item as Map),
            ),
          )
          .toList();
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussion> pinDiscussion(String discussionId) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/pin',
      );
      return CommunityDiscussion.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> deleteDiscussion(String discussionId) async {
    try {
      await _apiClient.dio.delete<Map<String, dynamic>>(
        '/community/discussions/$discussionId',
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityDiscussionSubmission> submitDiscussion({
    required String submissionKey,
    required String ticker,
    required String title,
    required String content,
    required String periodType,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions',
        data: <String, dynamic>{
          'submission_key': submissionKey,
          'ticker': ticker.trim().toUpperCase(),
          'title': title.trim(),
          'content': content.trim(),
          'period_type': periodType,
        },
      );
      return CommunityDiscussionSubmission.fromJson(
        _requiredData(response.data),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityReportResult> reportDiscussion({
    required String discussionId,
    required String reasonCode,
    String details = '',
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/reports',
        data: <String, dynamic>{
          'reason_code': reasonCode,
          'details': details.trim(),
        },
      );
      return CommunityReportResult.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityMuteResult> muteUser(String userId) async {
    try {
      final response = await _apiClient.dio.put<Map<String, dynamic>>(
        '/community/users/$userId/mute',
      );
      return CommunityMuteResult.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityMuteResult> unmuteUser(String userId) async {
    try {
      final response = await _apiClient.dio.delete<Map<String, dynamic>>(
        '/community/users/$userId/mute',
      );
      return CommunityMuteResult.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityAppealSubmission> submitAppeal({
    required String discussionId,
    required String message,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/appeals',
        data: <String, dynamic>{'message': message.trim()},
      );
      return CommunityAppealSubmission.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> toggleReaction({
    required String discussionId,
    required String reactionType,
  }) async {
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/$discussionId/reactions',
        data: <String, dynamic>{'reaction_type': reactionType},
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<CommunityAppealPage> listMyAppeals({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/appeals/mine',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return CommunityAppealPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<void> registerViews(List<String> discussionIds) async {
    if (discussionIds.isEmpty) return;
    try {
      await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/discussions/views',
        data: <String, dynamic>{'discussion_ids': discussionIds},
      );
    } on Object {
      // Silently ignore view impression tracking errors
    }
  }

  Future<Map<String, dynamic>> toggleFollow(String userId) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/users/$userId/follow',
      );
      return _requiredData(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<UserPublicProfile> getUserProfile(String userId) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/users/$userId/profile',
      );
      return UserPublicProfile.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<UserFollowPage> getFollowers({
    required String userId,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/users/$userId/followers',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return UserFollowPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<UserFollowPage> getFollowing({
    required String userId,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/community/users/$userId/following',
        queryParameters: <String, dynamic>{'limit': limit, 'offset': offset},
      );
      return UserFollowPage.fromJson(_requiredData(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> sendCoinTip({
    required String receiverId,
    required int amountCoins,
  }) async {
    try {
      final response = await _apiClient.dio.post<Map<String, dynamic>>(
        '/community/users/$receiverId/tip',
        data: <String, dynamic>{'amount_coins': amountCoins},
      );
      return _requiredData(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<Map<String, dynamic>> updateTippingSettings({
    required bool tippingEnabled,
  }) async {
    try {
      final response = await _apiClient.dio.patch<Map<String, dynamic>>(
        '/profile/settings/tipping',
        data: <String, dynamic>{'tipping_enabled': tippingEnabled},
      );
      return _requiredData(response.data);
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _requiredData(Map<String, dynamic>? data) {
    if (data == null) {
      throw const FormatException('Community response is empty.');
    }
    return data;
  }
}

final communityRepositoryProvider = Provider<CommunityRepository>((ref) {
  return CommunityRepository(ref.watch(apiClientProvider));
});

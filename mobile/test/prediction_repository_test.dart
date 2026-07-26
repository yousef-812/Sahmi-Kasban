import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/api_exception.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';
import 'package:sahmi_kasban_mobile/features/community/prediction_repository.dart';

class _MockTokenStore extends Mock implements TokenStore {}

class _CallbackAdapter implements HttpClientAdapter {
  _CallbackAdapter(this.callback);

  final Future<ResponseBody> Function(RequestOptions options) callback;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<dynamic>? cancelFuture,
  ) {
    return callback(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _jsonBody(Object payload, int statusCode) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: <String, List<String>>{
      Headers.contentTypeHeader: <String>[Headers.jsonContentType],
    },
  );
}

Map<String, dynamic> _verificationJson() {
  return <String, dynamic>{
    'id': 'verification-1',
    'discussion_id': 'discussion-1',
    'score_bp': 9000,
    'score_percent': 90.0,
    'strength': 'very_strong',
    'reward_points': 200,
    'reward_coins': '2.00',
    'evidence': <String, dynamic>{
      'explanation': <String, dynamic>{
        'reason': 'تحقق الاتجاه والهدف.',
      },
    },
    'verified_at': '2026-07-27T17:05:00+03:00',
  };
}

PredictionRepository _repository(
  _MockTokenStore tokenStore,
  Future<ResponseBody> Function(RequestOptions options) callback,
) {
  when(tokenStore.readAccessToken).thenAnswer((_) async => 'access-token');
  final dio = Dio(BaseOptions(baseUrl: 'https://example.test/api/v1'));
  dio.httpClientAdapter = _CallbackAdapter(callback);
  return PredictionRepository(
    ApiClient(
      baseUrl: 'https://example.test',
      tokenStore: tokenStore,
      dio: dio,
    ),
  );
}

void main() {
  test('loads verification eligibility status', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(
        options.path,
        '/community/discussions/discussion-1/verification',
      );
      expect(options.method, 'GET');
      return _jsonBody(<String, dynamic>{
        'discussion_id': 'discussion-1',
        'state': 'eligible',
        'eligible_at': '2026-07-27T17:00:00+03:00',
        'verification': null,
      }, 200);
    });

    final status = await repository.getVerificationStatus('discussion-1');

    expect(status.isEligible, isTrue);
    expect(status.verification, isNull);
  });

  test('submits verification and parses exactly-once reward response', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(
        options.path,
        '/community/discussions/discussion-1/verification',
      );
      expect(options.method, 'POST');
      return _jsonBody(<String, dynamic>{
        'verification': _verificationJson(),
        'balance_points': 500,
        'balance_coins': '5.00',
        'idempotent': false,
      }, 200);
    });

    final result = await repository.verifyPrediction('discussion-1');

    expect(result.verification.rewardPoints, 200);
    expect(result.balanceCoins, '5.00');
    expect(result.idempotent, isFalse);
  });

  test('loads personal prediction statistics', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(options.path, '/community/predictions/stats/mine');
      return _jsonBody(<String, dynamic>{
        'verified_predictions': 3,
        'accepted_predictions': 2,
        'accuracy_percent': 66.67,
        'average_score_percent': 71.25,
        'total_reward_points': 250,
        'total_reward_coins': '2.50',
      }, 200);
    });

    final stats = await repository.getMyStats();

    expect(stats.verifiedPredictions, 3);
    expect(stats.accuracyPercent, 66.67);
    expect(stats.totalRewardPoints, 250);
  });

  test('maps unfinished-period conflict from the backend', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      return _jsonBody(<String, dynamic>{
        'detail': 'لم تنتهِ فترة التوقع بعد.',
      }, 409);
    });

    try {
      await repository.verifyPrediction('discussion-1');
      fail('Expected an ApiException.');
    } on ApiException catch (error) {
      expect(error.statusCode, 409);
      expect(error.message, 'لم تنتهِ فترة التوقع بعد.');
    }
  });
}

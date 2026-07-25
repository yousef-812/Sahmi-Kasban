import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/api_exception.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';
import 'package:sahmi_kasban_mobile/features/community/community_repository.dart';

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

ResponseBody _jsonBody(
  Object payload,
  int statusCode, {
  Map<String, List<String>> headers = const <String, List<String>>{},
}) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: <String, List<String>>{
      Headers.contentTypeHeader: <String>[Headers.jsonContentType],
      ...headers,
    },
  );
}

Map<String, dynamic> _discussionJson() {
  return <String, dynamic>{
    'id': 'discussion-1',
    'ticker': 'COMI',
    'title': 'توقع حركة سهم البنك التجاري الدولي',
    'content': 'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
    'period_type': 'next_session',
    'status': 'published',
    'moderation_result': <String, dynamic>{},
    'frozen_prediction': <String, dynamic>{'direction': 'up'},
    'rejection_code': null,
    'created_at': '2026-07-26T00:15:00+03:00',
    'reviewed_at': '2026-07-26T00:16:00+03:00',
    'published_at': '2026-07-26T00:16:00+03:00',
    'author': <String, dynamic>{
      'user_id': 'user-1',
      'display_name': 'مستخدم تجريبي',
      'avatar_key': 'avatar_03',
    },
  };
}

CommunityRepository _repository(
  _MockTokenStore tokenStore,
  Future<ResponseBody> Function(RequestOptions options) callback,
) {
  when(tokenStore.readAccessToken).thenAnswer((_) async => 'access-token');
  final dio = Dio(BaseOptions(baseUrl: 'https://example.test/api/v1'));
  dio.httpClientAdapter = _CallbackAdapter(callback);
  return CommunityRepository(
    ApiClient(
      baseUrl: 'https://example.test',
      tokenStore: tokenStore,
      dio: dio,
    ),
  );
}

void main() {
  test('loads filtered community page with pagination', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      expect(options.path, '/community/discussions');
      expect(options.queryParameters['ticker'], 'COMI');
      expect(options.queryParameters['limit'], 10);
      expect(options.queryParameters['offset'], 20);
      return _jsonBody(<String, dynamic>{
        'items': <Map<String, dynamic>>[_discussionJson()],
        'total': 21,
        'limit': 10,
        'offset': 20,
      }, 200);
    });

    final page = await repository.listDiscussions(
      ticker: 'comi',
      limit: 10,
      offset: 20,
    );

    expect(page.items.single.ticker, 'COMI');
    expect(page.total, 21);
    expect(page.hasMore, isFalse);
  });

  test('maps 429 response and Retry-After header', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      return _jsonBody(
        <String, dynamic>{'detail': 'Submission rate limit exceeded'},
        429,
        headers: <String, List<String>>{
          'retry-after': <String>['45'],
        },
      );
    });

    try {
      await repository.submitDiscussion(
        submissionKey: 'submission-key-123',
        ticker: 'COMI',
        title: 'توقع حركة سهم البنك التجاري الدولي',
        content:
            'أتوقع استمرار الاتجاه الصاعد خلال الجلسة القادمة مع مراقبة الحجم.',
        periodType: 'next_session',
      );
      fail('Expected an ApiException.');
    } on ApiException catch (error) {
      expect(error.statusCode, 429);
      expect(error.retryAfterSeconds, 45);
      expect(error.message, 'Submission rate limit exceeded');
    }
  });

  test('extracts FastAPI validation messages from 422 response', () async {
    final tokenStore = _MockTokenStore();
    final repository = _repository(tokenStore, (options) async {
      return _jsonBody(<String, dynamic>{
        'detail': <Map<String, dynamic>>[
          <String, dynamic>{'msg': 'String should have at least 20 characters'},
        ],
      }, 422);
    });

    try {
      await repository.submitAppeal(
        discussionId: 'discussion-1',
        message: 'قصير',
      );
      fail('Expected an ApiException.');
    } on ApiException catch (error) {
      expect(error.statusCode, 422);
      expect(error.message, 'String should have at least 20 characters');
    }
  });
}

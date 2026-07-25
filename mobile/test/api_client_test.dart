import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';

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

ResponseBody _jsonBody(Map<String, dynamic> payload, int statusCode) {
  return ResponseBody.fromString(
    jsonEncode(payload),
    statusCode,
    headers: <String, List<String>>{
      Headers.contentTypeHeader: <String>[Headers.jsonContentType],
    },
  );
}

void main() {
  group('ApiClient', () {
    test(
      'shares one refresh request across concurrent 401 responses',
      () async {
        final tokenStore = _MockTokenStore();
        var accessToken = 'old-access';
        var refreshToken = 'refresh-one';
        when(tokenStore.readAccessToken).thenAnswer((_) async => accessToken);
        when(tokenStore.readRefreshToken).thenAnswer((_) async => refreshToken);
        when(
          () => tokenStore.save(
            accessToken: any(named: 'accessToken'),
            refreshToken: any(named: 'refreshToken'),
          ),
        ).thenAnswer((invocation) async {
          accessToken = invocation.namedArguments[#accessToken] as String;
          refreshToken = invocation.namedArguments[#refreshToken] as String;
        });

        var refreshCalls = 0;
        final refreshDio = Dio(
          BaseOptions(baseUrl: 'https://example.test/api/v1'),
        );
        refreshDio.httpClientAdapter = _CallbackAdapter((options) async {
          refreshCalls += 1;
          await Future<void>.delayed(const Duration(milliseconds: 25));
          return _jsonBody(<String, dynamic>{
            'access_token': 'new-access',
            'refresh_token': 'refresh-two',
          }, 200);
        });

        final mainDio = Dio(
          BaseOptions(baseUrl: 'https://example.test/api/v1'),
        );
        mainDio.httpClientAdapter = _CallbackAdapter((options) async {
          final authorization = options.headers['Authorization'];
          if (authorization == 'Bearer new-access') {
            return _jsonBody(<String, dynamic>{'ok': true}, 200);
          }
          return _jsonBody(<String, dynamic>{'detail': 'expired'}, 401);
        });

        final client = ApiClient(
          baseUrl: 'https://example.test',
          tokenStore: tokenStore,
          dio: mainDio,
          refreshDio: refreshDio,
        );

        final responses = await Future.wait([
          client.dio.get<Map<String, dynamic>>('/protected'),
          client.dio.get<Map<String, dynamic>>('/protected'),
        ]);

        expect(responses, hasLength(2));
        expect(
          responses.every((response) => response.data?['ok'] == true),
          isTrue,
        );
        expect(refreshCalls, 1);
        expect(accessToken, 'new-access');
        expect(refreshToken, 'refresh-two');
        verify(
          () => tokenStore.save(
            accessToken: 'new-access',
            refreshToken: 'refresh-two',
          ),
        ).called(1);
      },
    );

    test('anonymous request does not read or attach an access token', () async {
      final tokenStore = _MockTokenStore();
      final mainDio = Dio(BaseOptions(baseUrl: 'https://example.test/api/v1'));
      Object? authorization;
      mainDio.httpClientAdapter = _CallbackAdapter((options) async {
        authorization = options.headers['Authorization'];
        return _jsonBody(<String, dynamic>{'ok': true}, 200);
      });

      final client = ApiClient(
        baseUrl: 'https://example.test',
        tokenStore: tokenStore,
        dio: mainDio,
      );
      await client.dio.get<Map<String, dynamic>>(
        '/public',
        options: Options(extra: <String, dynamic>{'anonymous': true}),
      );

      expect(authorization, isNull);
      verifyNever(tokenStore.readAccessToken);
    });
  });
}

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/core/network/api_client.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';
import 'package:sahmi_kasban_mobile/features/app_version/version_check_manager.dart';

class _TS extends Mock implements TokenStore {}

TokenStore _ts() {
  final t = _TS();
  when(t.readAccessToken).thenAnswer((_) async => null);
  return t;
}

class _Adapter implements HttpClientAdapter {
  _Adapter(this.handler);
  final ResponseBody Function() handler;
  @override
  void close({bool force = false}) {}
  @override
  Future<ResponseBody> fetch(
    RequestOptions o,
    Stream<List<int>>? s,
    Future<void>? c,
  ) async => handler();
}

AppVersionInfo info({int latest = 37, int min = 1, bool force = false}) =>
    AppVersionInfo.fromJson({
      'latest_version_code': latest,
      'min_required_version_code': min,
      'force_update': force,
    });

VersionCheckManager manager(ResponseBody Function() h, int? build) {
  final dio = Dio(BaseOptions(baseUrl: 'http://x'))
    ..httpClientAdapter = _Adapter(h);
  return VersionCheckManager(
    ApiClient(baseUrl: 'http://x', tokenStore: _ts(), dio: dio),
    installedBuild: () async => build,
  );
}

ResponseBody json(String s, [int code = 200]) => ResponseBody.fromString(
  s,
  code,
  headers: {
    Headers.contentTypeHeader: ['application/json'],
  },
);

void main() {
  group('evaluateUpdate', () {
    test('installed below latest prompts, not forced', () {
      final d = evaluateUpdate(36, info());
      expect(d.shouldPrompt, isTrue);
      expect(d.force, isFalse);
    });
    test('installed equal to latest does not prompt', () {
      expect(evaluateUpdate(37, info()).shouldPrompt, isFalse);
    });
    test('installed above latest does not prompt (staged rollout)', () {
      expect(evaluateUpdate(38, info()).shouldPrompt, isFalse);
    });
    test('below min required forces update even when latest is not newer', () {
      final d = evaluateUpdate(30, info(latest: 30, min: 33));
      expect(d.shouldPrompt, isTrue);
      expect(d.force, isTrue);
    });
    test('force flag only applies to outdated installs', () {
      expect(evaluateUpdate(37, info(force: true)).shouldPrompt, isFalse);
      final d = evaluateUpdate(36, info(force: true));
      expect(d.shouldPrompt, isTrue);
      expect(d.force, isTrue);
    });
    test('unknown or invalid installed build never prompts or locks', () {
      expect(evaluateUpdate(null, info(min: 99)).shouldPrompt, isFalse);
      expect(evaluateUpdate(0, info(min: 99)).force, isFalse);
    });
    test('server payload missing fields defaults to no prompt', () {
      final i = AppVersionInfo.fromJson(<String, dynamic>{});
      expect(evaluateUpdate(1, i).shouldPrompt, isFalse);
    });
  });

  group('checkVersion', () {
    test('parses a valid response', () async {
      final m = manager(
        () => json('{"latest_version_code":37,"latest_version":"1.0.10+37"}'),
        37,
      );
      final v = await m.checkVersion();
      expect(v?.latestVersionCode, 37);
      expect(v?.latestVersion, '1.0.10+37');
    });
    test('server error returns null without throwing', () async {
      final m = manager(() => json('{"detail":"x"}', 500), 37);
      expect(await m.checkVersion(), isNull);
    });
    test('network failure returns null without throwing', () async {
      final m = manager(() => throw const SocketLikeError(), 37);
      expect(await m.checkVersion(), isNull);
    });
    test('malformed response returns null or no-prompt', () async {
      final m = manager(() => json('[1,2]'), 37);
      final v = await m.checkVersion();
      expect(v == null || !evaluateUpdate(37, v).shouldPrompt, isTrue);
    });
  });

  group('prompt widget flow', () {
    Future<void> pump(WidgetTester t, VersionCheckManager m) async {
      await t.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (c) => TextButton(
              onPressed: () => m.checkAndShowPrompt(c),
              child: const Text('go'),
            ),
          ),
        ),
      );
      await t.tap(find.text('go'));
      await t.pumpAndSettle();
    }

    const body =
        '{"latest_version_code":37,"min_required_version_code":1,"force_update":false}';

    testWidgets('outdated install shows dialog once per session', (t) async {
      final m = manager(() => json(body), 36);
      await pump(t, m);
      expect(find.byType(AlertDialog), findsOneWidget);
      await t.tap(find.text('لاحقاً'));
      await t.pumpAndSettle();
      await t.tap(find.text('go'));
      await t.pumpAndSettle();
      expect(find.byType(AlertDialog), findsNothing);
    });

    testWidgets('updated install (build == latest) shows no dialog', (t) async {
      await pump(t, manager(() => json(body), 37));
      expect(find.byType(AlertDialog), findsNothing);
    });
  });
}

class SocketLikeError implements Exception {
  const SocketLikeError();
}

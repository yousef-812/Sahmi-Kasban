import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/core/network/token_store.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    FlutterSecureStorage.setMockInitialValues(<String, String>{});
  });

  test('stores reads and clears the rotating token pair', () async {
    const storage = FlutterSecureStorage();
    final store = TokenStore(storage);

    expect(await store.read(), isNull);

    await store.save(accessToken: 'access-one', refreshToken: 'refresh-one');
    final saved = await store.read();

    expect(saved, isNotNull);
    expect(saved!.accessToken, 'access-one');
    expect(saved.refreshToken, 'refresh-one');
    expect(await store.readAccessToken(), 'access-one');
    expect(await store.readRefreshToken(), 'refresh-one');

    await store.save(accessToken: 'access-two', refreshToken: 'refresh-two');
    expect((await store.read())!.refreshToken, 'refresh-two');

    await store.clear();
    expect(await store.read(), isNull);
  });
}

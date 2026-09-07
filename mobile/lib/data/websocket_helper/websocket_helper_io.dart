import 'dart:io';

Future<dynamic> connectWebSocketUri(Uri uri, {Duration? timeout}) async {
  return await WebSocket.connect(uri.toString()).timeout(timeout ?? const Duration(seconds: 8));
}

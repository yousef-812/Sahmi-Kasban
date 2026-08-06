import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Background/terminated pushes are surfaced by the OS notification tray.
  // A background isolate cannot touch the widget tree, so this handler stays
  // minimal; the inbox is refreshed when the user opens the app.
}

final initialNotificationMessageProvider = FutureProvider<RemoteMessage?>((ref) {
  return FirebaseMessaging.instance.getInitialMessage();
});

final openedNotificationMessageProvider = StreamProvider<RemoteMessage>((ref) {
  return FirebaseMessaging.onMessageOpenedApp;
});

final foregroundNotificationMessageProvider = StreamProvider<RemoteMessage>((ref) {
  return FirebaseMessaging.onMessage;
});

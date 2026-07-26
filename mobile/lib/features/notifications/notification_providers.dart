import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/session_controller.dart';
import 'notification_models.dart';
import 'notification_repository.dart';

final notificationInboxProvider = FutureProvider.autoDispose<NotificationPage>((
  ref,
) {
  return ref.watch(notificationRepositoryProvider).listNotifications();
});

final pushRegistrationProvider = FutureProvider<void>((ref) async {
  final session = ref.watch(sessionControllerProvider);
  if (session.status != SessionStatus.authenticated) {
    return;
  }
  try {
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp();
    }
    final messaging = FirebaseMessaging.instance;
    await messaging.requestPermission();
    final token = await messaging.getToken();
    if (token == null || token.length < 20) {
      return;
    }
    final platform = kIsWeb
        ? 'web'
        : defaultTargetPlatform == TargetPlatform.iOS
        ? 'ios'
        : 'android';
    await ref
        .read(notificationRepositoryProvider)
        .registerDevice(token: token, platform: platform);
  } on Object {
    // Push remains optional until Firebase project files are configured.
  }
});

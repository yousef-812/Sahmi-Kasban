import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'notification_messaging.dart';

/// Sits above the router so foreground pushes render as in-app banners and a
/// tapped push (cold start, background, or foreground) opens the inbox.
class NotificationMessagingShell extends ConsumerStatefulWidget {
  const NotificationMessagingShell({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<NotificationMessagingShell> createState() =>
      _NotificationMessagingShellState();
}

class _NotificationMessagingShellState
    extends ConsumerState<NotificationMessagingShell> {
  void _openInbox() {
    if (!mounted) {
      return;
    }
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.push('/notifications');
      }
    });
  }

  void _showForegroundBanner(RemoteMessage message) {
    if (!mounted) {
      return;
    }
    final messenger = ScaffoldMessenger.of(context);
    final title = message.notification?.title ?? 'إشعار جديد';
    final body = message.notification?.body;
    messenger
      ..hideCurrentMaterialBanner()
      ..showMaterialBanner(
        MaterialBanner(
          leading: const Icon(Icons.notifications_active_outlined),
          content: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(title, style: Theme.of(context).textTheme.titleSmall),
              if (body != null && body.isNotEmpty)
                Text(body, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                messenger.hideCurrentMaterialBanner();
                _openInbox();
              },
              child: const Text('فتح'),
            ),
            TextButton(
              onPressed: messenger.hideCurrentMaterialBanner,
              child: const Text('إغلاق'),
            ),
          ],
        ),
      );
    Future<void>.delayed(const Duration(seconds: 6), () {
      if (mounted) {
        messenger.hideCurrentMaterialBanner();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<AsyncValue<RemoteMessage?>>(
      initialNotificationMessageProvider,
      (previous, next) {
        if (next.valueOrNull != null) {
          _openInbox();
        }
      },
    );
    ref.listen<AsyncValue<RemoteMessage>>(
      openedNotificationMessageProvider,
      (previous, next) {
        if (next.valueOrNull != null) {
          _openInbox();
        }
      },
    );
    ref.listen<AsyncValue<RemoteMessage>>(
      foregroundNotificationMessageProvider,
      (previous, next) {
        final message = next.valueOrNull;
        if (message != null) {
          _showForegroundBanner(message);
        }
      },
    );
    return widget.child;
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'notification_models.dart';
import 'notification_providers.dart';
import 'notification_repository.dart';

class NotificationScreen extends ConsumerWidget {
  const NotificationScreen({super.key});

  Future<void> _refresh(WidgetRef ref) async {
    ref.invalidate(notificationInboxProvider);
    await ref.read(notificationInboxProvider.future);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final inbox = ref.watch(notificationInboxProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('الإشعارات'),
        actions: [
          TextButton(
            onPressed: () async {
              await ref.read(notificationRepositoryProvider).markAllRead();
              ref.invalidate(notificationInboxProvider);
            },
            child: const Text('قراءة الكل'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _refresh(ref),
        child: inbox.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => ListView(
            padding: const EdgeInsets.all(24),
            children: [
              const SizedBox(height: 100),
              const Text('تعذر تحميل الإشعارات.', textAlign: TextAlign.center),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: () => ref.invalidate(notificationInboxProvider),
                child: const Text('إعادة المحاولة'),
              ),
            ],
          ),
          data: (page) => page.items.isEmpty
              ? ListView(
                  padding: const EdgeInsets.all(24),
                  children: const [
                    SizedBox(height: 120),
                    Icon(Icons.notifications_none_rounded, size: 58),
                    SizedBox(height: 14),
                    Text(
                      'لا توجد إشعارات حتى الآن.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: page.items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 10),
                  itemBuilder: (context, index) => _NotificationCard(
                    item: page.items[index],
                    onRead: () async {
                      await ref
                          .read(notificationRepositoryProvider)
                          .markRead(page.items[index].id);
                      ref.invalidate(notificationInboxProvider);
                    },
                  ),
                ),
        ),
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({required this.item, required this.onRead});

  final AppNotification item;
  final VoidCallback onRead;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        onTap: item.isUnread ? onRead : null,
        leading: Icon(
          item.isUnread
              ? Icons.notifications_active_rounded
              : Icons.notifications_none_rounded,
        ),
        title: Text(
          item.title,
          style: TextStyle(
            fontWeight: item.isUnread ? FontWeight.w800 : FontWeight.w500,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 6),
          child: Text(item.body),
        ),
        trailing: item.isUnread
            ? const Icon(Icons.circle, size: 10)
            : const Icon(Icons.done_rounded),
      ),
    );
  }
}

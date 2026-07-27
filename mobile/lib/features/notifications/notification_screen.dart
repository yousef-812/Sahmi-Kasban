import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/ui/app_notice.dart';
import 'notification_models.dart';
import 'notification_providers.dart';
import 'notification_repository.dart';

class NotificationScreen extends ConsumerStatefulWidget {
  const NotificationScreen({super.key});

  @override
  ConsumerState<NotificationScreen> createState() =>
      _NotificationScreenState();
}

class _NotificationScreenState extends ConsumerState<NotificationScreen> {
  bool _unreadOnly = false;

  Future<void> _refresh() async {
    ref.invalidate(notificationInboxProvider);
    await ref.read(notificationInboxProvider.future);
  }

  Future<void> _markAllRead() async {
    try {
      await ref.read(notificationRepositoryProvider).markAllRead();
      ref.invalidate(notificationInboxProvider);
      if (mounted) {
        AppNotice.show(
          context,
          title: 'تم تحديث الإشعارات',
          message: 'تم تعليم كل الإشعارات كمقروءة.',
          tone: AppNoticeTone.success,
        );
      }
    } on Object {
      if (mounted) {
        AppNotice.show(
          context,
          title: 'تعذر التحديث',
          message: 'لم نتمكن من تعليم الإشعارات كمقروءة الآن.',
          tone: AppNoticeTone.error,
        );
      }
    }
  }

  Future<void> _markRead(AppNotification item) async {
    if (!item.isUnread) {
      return;
    }
    try {
      await ref.read(notificationRepositoryProvider).markRead(item.id);
      ref.invalidate(notificationInboxProvider);
    } on Object {
      if (mounted) {
        AppNotice.show(
          context,
          message: 'تعذر تحديث حالة الإشعار.',
          tone: AppNoticeTone.error,
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final inbox = ref.watch(notificationInboxProvider);
    final unreadCount = inbox.asData?.value.unreadCount;
    return Scaffold(
      appBar: AppBar(
        title: const Text('الإشعارات'),
        actions: [
          IconButton(
            tooltip: 'تعليم الكل كمقروء',
            onPressed: unreadCount == null || unreadCount == 0
                ? null
                : _markAllRead,
            icon: const Icon(Icons.done_all_rounded),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: inbox.when(
          loading: () => const _NotificationLoading(),
          error: (error, stackTrace) => ListView(
            padding: const EdgeInsets.all(24),
            children: [
              const SizedBox(height: 90),
              Icon(
                Icons.cloud_off_rounded,
                size: 62,
                color: Theme.of(context).colorScheme.outline,
              ),
              const SizedBox(height: 16),
              Text(
                'تعذر تحميل الإشعارات',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'اسحب الشاشة لأسفل أو حاول مرة أخرى.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 18),
              OutlinedButton.icon(
                onPressed: () => ref.invalidate(notificationInboxProvider),
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
          data: (page) {
            final items = _unreadOnly
                ? page.items.where((item) => item.isUnread).toList()
                : page.items;
            return CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 8),
                  sliver: SliverToBoxAdapter(
                    child: _NotificationSummary(
                      total: page.total,
                      unread: page.unreadCount,
                      unreadOnly: _unreadOnly,
                      onFilterChanged: (value) {
                        setState(() => _unreadOnly = value);
                      },
                    ),
                  ),
                ),
                if (items.isEmpty)
                  SliverFillRemaining(
                    hasScrollBody: false,
                    child: _EmptyNotifications(unreadOnly: _unreadOnly),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    sliver: SliverList.separated(
                      itemCount: items.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) => _NotificationCard(
                        item: items[index],
                        onRead: () => _markRead(items[index]),
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _NotificationSummary extends StatelessWidget {
  const _NotificationSummary({
    required this.total,
    required this.unread,
    required this.unreadOnly,
    required this.onFilterChanged,
  });

  final int total;
  final int unread;
  final bool unreadOnly;
  final ValueChanged<bool> onFilterChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            theme.colorScheme.primaryContainer,
            theme.colorScheme.surfaceContainerLowest,
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Icon(
                  Icons.notifications_active_rounded,
                  color: theme.colorScheme.onPrimary,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      unread == 0
                          ? 'كل شيء تحت السيطرة'
                          : 'لديك $unread إشعار غير مقروء',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      'إجمالي الإشعارات: $total',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 10,
            children: [
              ChoiceChip(
                label: const Text('الكل'),
                selected: !unreadOnly,
                onSelected: (_) => onFilterChanged(false),
              ),
              ChoiceChip(
                label: Text('غير المقروء ($unread)'),
                selected: unreadOnly,
                onSelected: (_) => onFilterChanged(true),
              ),
            ],
          ),
        ],
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
    final theme = Theme.of(context);
    final visual = _categoryVisual(item.category, theme.colorScheme);
    return Material(
      color: item.isUnread
          ? theme.colorScheme.primaryContainer.withValues(alpha: 0.28)
          : theme.colorScheme.surfaceContainerLowest,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: item.isUnread ? onRead : null,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: item.isUnread
                  ? theme.colorScheme.primary.withValues(alpha: 0.28)
                  : theme.colorScheme.outlineVariant,
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: visual.background,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(visual.icon, color: visual.foreground),
              ),
              const SizedBox(width: 13),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item.title,
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: item.isUnread
                                  ? FontWeight.w800
                                  : FontWeight.w600,
                            ),
                          ),
                        ),
                        if (item.isUnread)
                          Container(
                            width: 9,
                            height: 9,
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary,
                              shape: BoxShape.circle,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 7),
                    Text(
                      item.body,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.55,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Icon(
                          Icons.schedule_rounded,
                          size: 16,
                          color: theme.colorScheme.outline,
                        ),
                        const SizedBox(width: 5),
                        Text(
                          _relativeTime(item.sentAt),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.outline,
                          ),
                        ),
                        if (item.isUnread) ...[
                          const Spacer(),
                          Text(
                            'اضغط للتعليم كمقروء',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.primary,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyNotifications extends StatelessWidget {
  const _EmptyNotifications({required this.unreadOnly});

  final bool unreadOnly;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              unreadOnly
                  ? Icons.mark_email_read_rounded
                  : Icons.notifications_none_rounded,
              size: 68,
              color: theme.colorScheme.outline,
            ),
            const SizedBox(height: 16),
            Text(
              unreadOnly
                  ? 'لا توجد إشعارات غير مقروءة'
                  : 'لا توجد إشعارات حتى الآن',
              textAlign: TextAlign.center,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              unreadOnly
                  ? 'قرأت كل الإشعارات الحالية.'
                  : 'ستظهر هنا التنبيهات والتحديثات المهمة.',
              textAlign: TextAlign.center,
              style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotificationLoading extends StatelessWidget {
  const _NotificationLoading();

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 5,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, __) => Container(
        height: 112,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainer,
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }
}

_CategoryVisual _categoryVisual(String category, ColorScheme colors) {
  final normalized = category.toLowerCase();
  if (normalized.contains('reward') || normalized.contains('wallet')) {
    return const _CategoryVisual(
      icon: Icons.workspace_premium_rounded,
      background: Color(0xFFFFF1C7),
      foreground: Color(0xFF805B00),
    );
  }
  if (normalized.contains('report') || normalized.contains('analysis')) {
    return _CategoryVisual(
      icon: Icons.analytics_rounded,
      background: colors.primaryContainer,
      foreground: colors.onPrimaryContainer,
    );
  }
  if (normalized.contains('community')) {
    return const _CategoryVisual(
      icon: Icons.forum_rounded,
      background: Color(0xFFE9E4FF),
      foreground: Color(0xFF4F378B),
    );
  }
  return _CategoryVisual(
    icon: Icons.notifications_rounded,
    background: colors.surfaceContainerHighest,
    foreground: colors.onSurfaceVariant,
  );
}

String _relativeTime(DateTime value) {
  final difference = DateTime.now().difference(value.toLocal());
  if (difference.isNegative || difference.inMinutes < 1) {
    return 'الآن';
  }
  if (difference.inMinutes < 60) {
    return 'منذ ${difference.inMinutes} دقيقة';
  }
  if (difference.inHours < 24) {
    return 'منذ ${difference.inHours} ساعة';
  }
  if (difference.inDays < 7) {
    return 'منذ ${difference.inDays} يوم';
  }
  return '${value.toLocal().day}/${value.toLocal().month}/${value.toLocal().year}';
}

class _CategoryVisual {
  const _CategoryVisual({
    required this.icon,
    required this.background,
    required this.foreground,
  });

  final IconData icon;
  final Color background;
  final Color foreground;
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import 'signals_models.dart';
import 'signals_providers.dart';

class AlertsScreen extends ConsumerStatefulWidget {
  const AlertsScreen({super.key});

  @override
  ConsumerState<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends ConsumerState<AlertsScreen> {
  bool _unreadOnly = false;

  Future<void> _refresh() async {
    await ref.read(alertsControllerProvider(_unreadOnly).notifier).refresh();
  }

  Future<void> _markRead(AlertItem item) async {
    if (item.isRead) return;
    try {
      await ref
          .read(alertsControllerProvider(_unreadOnly).notifier)
          .markRead(item.id);
    } on Object catch (error) {
      if (!mounted) return;
      AppNotice.show(
        context,
        message: error is ApiException
            ? error.message
            : 'تعذر تحديث حالة التنبيه.',
        tone: AppNoticeTone.error,
      );
    }
  }

  Future<void> _markAllRead() async {
    try {
      await ref
          .read(alertsControllerProvider(_unreadOnly).notifier)
          .markAllRead();
      if (!mounted) return;
      AppNotice.show(
        context,
        title: 'تم تحديث التنبيهات',
        message: 'تم تعليم كل التنبيهات كمقروءة.',
        tone: AppNoticeTone.success,
      );
    } on Object catch (error) {
      if (!mounted) return;
      AppNotice.show(
        context,
        message: error is ApiException
            ? error.message
            : 'تعذر تعليم كل التنبيهات كمقروءة.',
        tone: AppNoticeTone.error,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final alertsState = ref.watch(alertsControllerProvider(_unreadOnly));
    final unreadCount =
        alertsState.valueOrNull?.items
            .where((AlertItem item) => !item.isRead)
            .length ??
        0;
    return Scaffold(
      appBar: AppBar(
        title: const Text('التنبيهات'),
        actions: [
          IconButton(
            tooltip: 'تعليم الكل كمقروء',
            onPressed: unreadCount == 0 ? null : _markAllRead,
            icon: const Icon(Icons.done_all_rounded),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: alertsState.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stackTrace) => _AlertsErrorView(
            error: error,
            onRetry: () =>
                ref.invalidate(alertsControllerProvider(_unreadOnly)),
          ),
          data: (page) => _buildList(context, page),
        ),
      ),
    );
  }

  Widget _buildList(BuildContext context, ApiList<AlertItem> page) {
    final theme = Theme.of(context);
    final unread = page.items.where((AlertItem item) => !item.isRead).length;
    final items = _unreadOnly
        ? page.items
              .where((AlertItem item) => !item.isRead)
              .toList(growable: false)
        : page.items;
    return CustomScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 4),
          sliver: SliverToBoxAdapter(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'التنبيهات المجلبة: ${page.count} · غير المقروء: $unread',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 6),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: [
                    ChoiceChip(
                      label: const Text('الكل'),
                      selected: !_unreadOnly,
                      onSelected: (_) => setState(() => _unreadOnly = false),
                    ),
                    ChoiceChip(
                      label: Text('غير المقروء ($unread)'),
                      selected: _unreadOnly,
                      onSelected: (_) => setState(() => _unreadOnly = true),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        if (items.isEmpty)
          SliverFillRemaining(
            hasScrollBody: false,
            child: _AlertsEmptyView(
              icon: _unreadOnly
                  ? Icons.mark_email_read_rounded
                  : Icons.notifications_none_rounded,
              message: _unreadOnly
                  ? 'لا توجد تنبيهات غير مقروءة'
                  : 'لا توجد تنبيهات حتى الآن',
              hint: _unreadOnly
                  ? 'قرأت كل التنبيهات الحالية.'
                  : 'ستظهر هنا تنبيهات الإشارات والانتقالات المهمة.',
            ),
          )
        else
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
            sliver: SliverList.separated(
              itemCount: items.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) => _AlertRow(
                item: items[index],
                onMarkRead: () => _markRead(items[index]),
              ),
            ),
          ),
      ],
    );
  }
}

class _AlertRow extends StatelessWidget {
  const _AlertRow({required this.item, required this.onMarkRead});

  final AlertItem item;
  final VoidCallback onMarkRead;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (badgeLabel, badgeColor) = _typeBadge(item.type);
    return Material(
      color: item.isRead
          ? theme.colorScheme.surfaceContainerLowest
          : theme.colorScheme.primaryContainer.withValues(alpha: 0.28),
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: item.isRead ? null : onMarkRead,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: item.isRead
                  ? theme.colorScheme.outlineVariant
                  : theme.colorScheme.primary.withValues(alpha: 0.28),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      item.title,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: item.isRead
                            ? FontWeight.w600
                            : FontWeight.w800,
                      ),
                    ),
                  ),
                  if (item.isRead)
                    Icon(
                      Icons.check_circle_rounded,
                      size: 18,
                      color: theme.colorScheme.outline,
                    )
                  else
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
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: badgeColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      badgeLabel,
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: badgeColor,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    Icons.schedule_rounded,
                    size: 16,
                    color: theme.colorScheme.outline,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      _relativeTime(item.createdAt),
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ),
                  if (!item.isRead) ...[
                    const SizedBox(width: 8),
                    OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        textStyle: theme.textTheme.labelSmall,
                      ),
                      onPressed: onMarkRead,
                      child: const Text('تعليم كمقروء'),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AlertsEmptyView extends StatelessWidget {
  const _AlertsEmptyView({
    required this.icon,
    required this.message,
    this.hint,
  });

  final IconData icon;
  final String message;
  final String? hint;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: theme.colorScheme.outline),
            const SizedBox(height: 14),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            if (hint != null) ...[
              const SizedBox(height: 8),
              Text(
                hint!,
                textAlign: TextAlign.center,
                style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _AlertsErrorView extends StatelessWidget {
  const _AlertsErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
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
          'تعذر تحميل التنبيهات',
          textAlign: TextAlign.center,
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        Text(
          error is ApiException
              ? (error as ApiException).message
              : 'اسحب الشاشة لأسفل أو حاول مرة أخرى.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 18),
        Center(
          child: OutlinedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('إعادة المحاولة'),
          ),
        ),
      ],
    );
  }
}

(String, Color) _typeBadge(String type) {
  final normalized = type.toLowerCase();
  if (normalized.contains('signal')) {
    return ('إشارة سعرية', Colors.blue.shade700);
  }
  if (normalized.contains('reward') || normalized.contains('wallet')) {
    return ('مكافأة', Colors.amber.shade800);
  }
  if (normalized.contains('report')) {
    return ('تقرير', Colors.purple.shade700);
  }
  return (type, Colors.blueGrey);
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
  final local = value.toLocal();
  final day = local.day.toString().padLeft(2, '0');
  final month = local.month.toString().padLeft(2, '0');
  return '$day/$month/${local.year}';
}

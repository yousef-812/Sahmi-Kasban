import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_exception.dart';
import 'admin_models.dart';
import 'admin_providers.dart';
import 'admin_repository.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 6,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مركز الإدارة'),
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'نظرة عامة'),
              Tab(text: 'المراجعة'),
              Tab(text: 'المستخدمون'),
              Tab(text: 'الإعدادات'),
              Tab(text: 'الإشعارات'),
              Tab(text: 'التدقيق'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            _OverviewTab(),
            _ModerationTab(),
            _UsersTab(),
            _SettingsTab(),
            _BroadcastTab(),
            _AuditTab(),
          ],
        ),
      ),
    );
  }
}

class _OverviewTab extends ConsumerWidget {
  const _OverviewTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final overview = ref.watch(adminOverviewProvider);
    final providers = ref.watch(adminProvidersProvider);
    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(adminOverviewProvider);
        ref.invalidate(adminProvidersProvider);
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          overview.when(
            loading: () => const _Loading(),
            error: (_, __) => const _Failure('تعذر تحميل مؤشرات الإدارة.'),
            data: (item) => Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _Metric('المستخدمون', item.usersTotal),
                _Metric('النشطون', item.usersActive),
                _Metric('الموقوفون', item.usersSuspended),
                _Metric('قيد المراجعة', item.discussionsPending),
                _Metric('البلاغات المفتوحة', item.openReports),
                _Metric('الاستئنافات', item.openAppeals),
                _Metric('توقعات متحققة', item.verifiedPredictions),
                _Metric('إشعارات اليوم', item.notificationsToday),
              ],
            ),
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              const Expanded(child: Text('حالة المزودات')),
              FilledButton.icon(
                onPressed: () async {
                  await ref
                      .read(adminRepositoryProvider)
                      .providers(probe: true);
                  ref.invalidate(adminProvidersProvider);
                },
                icon: const Icon(Icons.health_and_safety_outlined),
                label: const Text('فحص الآن'),
              ),
            ],
          ),
          const SizedBox(height: 10),
          providers.when(
            loading: () => const _Loading(),
            error: (_, __) => const _Failure('لا توجد حالة مزودات متاحة.'),
            data: (items) => Column(
              children: items
                  .map(
                    (item) => Card(
                      child: ListTile(
                        leading: Icon(
                          item.status == 'healthy'
                              ? Icons.check_circle_outline
                              : item.status == 'degraded'
                              ? Icons.warning_amber_rounded
                              : Icons.error_outline,
                        ),
                        title: Text('${item.component} — ${item.provider}'),
                        subtitle: Text(
                          '${item.status} • ${item.latencyMs ?? '-'} ms',
                        ),
                      ),
                    ),
                  )
                  .toList(growable: false),
            ),
          ),
        ],
      ),
    );
  }
}

class _ModerationTab extends ConsumerWidget {
  const _ModerationTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final discussions = ref.watch(adminDiscussionsProvider);
    return discussions.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل طابور المراجعة.'),
      data: (items) => RefreshIndicator(
        onRefresh: () async => ref.invalidate(adminDiscussionsProvider),
        child: items.isEmpty
            ? ListView(
                children: const [
                  SizedBox(height: 100),
                  Center(child: Text('الطابور فارغ.')),
                ],
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: items.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) {
                  final item = items[index];
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            '${item.discussion.ticker} — ${item.discussion.title}',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          Text(item.discussion.content),
                          if (item.openReportCount > 0)
                            Text('بلاغات مفتوحة: ${item.openReportCount}'),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: FilledButton(
                                  onPressed: () => _approve(context, ref, item),
                                  child: const Text('قبول'),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: OutlinedButton(
                                  onPressed: () => _reject(context, ref, item),
                                  child: const Text('رفض'),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
      ),
    );
  }

  Future<void> _approve(
    BuildContext context,
    WidgetRef ref,
    AdminDiscussionItem item,
  ) async {
    final direction = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('اتجاه التوقع'),
        children: [
          for (final value in const ['up', 'down', 'neutral'])
            SimpleDialogOption(
              onPressed: () => Navigator.pop(context, value),
              child: Text(value),
            ),
        ],
      ),
    );
    if (direction == null || !context.mounted) return;
    await _run(
      context,
      () => ref
          .read(adminRepositoryProvider)
          .moderateDiscussion(
            discussionId: item.discussion.id,
            action: 'approve',
            prediction: <String, dynamic>{
              'direction': direction,
              'target_price': item.discussion.frozenPrediction['target_price'],
              'deadline': item.discussion.frozenPrediction['deadline'],
              'claims':
                  item.discussion.frozenPrediction['claims'] ?? <String>[],
              'specificity':
                  item.discussion.frozenPrediction['specificity'] ?? 0.5,
            },
          ),
    );
    ref.invalidate(adminDiscussionsProvider);
    ref.invalidate(adminOverviewProvider);
  }

  Future<void> _reject(
    BuildContext context,
    WidgetRef ref,
    AdminDiscussionItem item,
  ) async {
    await _run(
      context,
      () => ref
          .read(adminRepositoryProvider)
          .moderateDiscussion(
            discussionId: item.discussion.id,
            action: 'reject',
            reasonCode: 'manual_rejection',
          ),
    );
    ref.invalidate(adminDiscussionsProvider);
    ref.invalidate(adminOverviewProvider);
  }
}

class _UsersTab extends ConsumerWidget {
  const _UsersTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final users = ref.watch(adminUsersProvider);
    return users.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل المستخدمين.'),
      data: (items) => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final user = items[index];
          final blocked = user.status == 'suspended';
          return Card(
            child: ListTile(
              title: Text(user.displayName),
              subtitle: Text(
                '${user.email}\n${user.planCode} • ${user.balancePoints} نقطة • ${user.discussionsCount} مناقشة',
              ),
              isThreeLine: true,
              trailing: OutlinedButton(
                onPressed: () async {
                  await _run(
                    context,
                    () => ref
                        .read(adminRepositoryProvider)
                        .setUserBlocked(user, !blocked),
                  );
                  ref.invalidate(adminUsersProvider);
                },
                child: Text(blocked ? 'إلغاء الحظر' : 'حظر'),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _SettingsTab extends ConsumerWidget {
  const _SettingsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(adminSettingsProvider);
    return settings.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل الإعدادات.'),
      data: (items) => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final item = items[index];
          return Card(
            child: ListTile(
              title: Text(item.label),
              subtitle: Text('${item.description}\nالقيمة: ${item.value}'),
              isThreeLine: true,
              trailing: const Icon(Icons.edit_outlined),
              onTap: () async {
                final value = await _editSetting(context, item);
                if (value == null || !context.mounted) return;
                await _run(
                  context,
                  () => ref
                      .read(adminRepositoryProvider)
                      .updateSetting(item.key, value),
                );
                ref.invalidate(adminSettingsProvider);
              },
            ),
          );
        },
      ),
    );
  }

  Future<Object?> _editSetting(
    BuildContext context,
    OperationalSetting item,
  ) async {
    if (item.kind == 'bool') {
      return showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(item.label),
          content: const Text('اختر حالة الإعداد.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('إيقاف'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('تفعيل'),
            ),
          ],
        ),
      );
    }
    final controller = TextEditingController(text: item.value.toString());
    return showDialog<Object>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(item.label),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () {
              final parsed = item.kind == 'float'
                  ? double.tryParse(controller.text)
                  : int.tryParse(controller.text);
              Navigator.pop(context, parsed);
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }
}

class _BroadcastTab extends ConsumerStatefulWidget {
  const _BroadcastTab();

  @override
  ConsumerState<_BroadcastTab> createState() => _BroadcastTabState();
}

class _BroadcastTabState extends ConsumerState<_BroadcastTab> {
  final _title = TextEditingController();
  final _body = TextEditingController();
  bool _busy = false;

  @override
  void dispose() {
    _title.dispose();
    _body.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        TextField(
          controller: _title,
          decoration: const InputDecoration(labelText: 'عنوان الإشعار'),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _body,
          minLines: 4,
          maxLines: 8,
          decoration: const InputDecoration(labelText: 'نص الإشعار'),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          onPressed: _busy ? null : _send,
          icon: const Icon(Icons.campaign_outlined),
          label: const Text('إرسال للمستخدمين النشطين'),
        ),
      ],
    );
  }

  Future<void> _send() async {
    if (_title.text.trim().length < 3 || _body.text.trim().length < 3) return;
    setState(() => _busy = true);
    try {
      final result = await ref
          .read(adminRepositoryProvider)
          .broadcast(title: _title.text, body: _body.text);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم إنشاء ${result['notifications_created']} إشعار.'),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
}

class _AuditTab extends ConsumerWidget {
  const _AuditTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final audit = ref.watch(adminAuditProvider);
    return audit.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل سجل التدقيق.'),
      data: (items) => ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) => Card(
          child: ListTile(
            title: Text(items[index].action),
            subtitle: Text(
              '${items[index].reasonCode ?? ''}\n${items[index].details}',
            ),
            isThreeLine: true,
          ),
        ),
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric(this.label, this.value);
  final String label;
  final int value;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 155,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text('$value', style: Theme.of(context).textTheme.headlineMedium),
            Text(label, textAlign: TextAlign.center),
          ],
        ),
      ),
    ),
  );
}

class _Loading extends StatelessWidget {
  const _Loading();
  @override
  Widget build(BuildContext context) => const Padding(
    padding: EdgeInsets.all(32),
    child: Center(child: CircularProgressIndicator()),
  );
}

class _Failure extends StatelessWidget {
  const _Failure(this.message);
  final String message;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(32),
    child: Center(child: Text(message)),
  );
}

Future<void> _run(BuildContext context, Future<void> Function() action) async {
  try {
    await action();
    if (context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('تم تنفيذ الإجراء.')));
    }
  } on ApiException catch (error) {
    if (context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.message)));
    }
  }
}

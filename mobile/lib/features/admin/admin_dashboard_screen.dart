import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/network/api_exception.dart';
import 'admin_models.dart';
import 'admin_providers.dart';
import 'admin_repository.dart';
import 'historical_replay_models.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 7,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مركز الإدارة'),
          actions: [
            IconButton(
              onPressed: () => context.push('/admin/performance'),
              icon: const Icon(Icons.assessment_outlined),
              tooltip: 'تشغيل سجل الأداء',
            ),
          ],
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'نظرة عامة'),
              Tab(text: 'المراجعة'),
              Tab(text: 'المستخدمون'),
              Tab(text: 'الإعدادات'),
              Tab(text: 'الإشعارات'),
              Tab(text: 'التدقيق'),
              Tab(text: 'وظائف إعادة اللعب'),
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
            _ReplayJobsTab(),
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

class _ReplayJobsTab extends ConsumerStatefulWidget {
  const _ReplayJobsTab();

  @override
  ConsumerState<_ReplayJobsTab> createState() => _ReplayJobsTabState();
}

class _ReplayJobsTabState extends ConsumerState<_ReplayJobsTab> {
  late DateTime _startDate;
  late DateTime _endDate;
  int? _rank;
  String _exitMode = 'target_2';
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<HistoricalReplayJob> _jobs = const [];
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _previousMonth(notify: false);
    unawaited(_load());
    _pollTimer = Timer.periodic(
      const Duration(seconds: 8),
      (_) => unawaited(_load(silent: true)),
    );
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _load({bool silent = false}) async {
    if (!silent && mounted) setState(() => _loading = true);
    try {
      final jobs = await ref
          .read(adminRepositoryProvider)
          .historicalReplayJobs();
      if (!mounted) return;
      setState(() {
        _jobs = jobs;
        _loading = false;
        _error = null;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error is ApiException ? error.message : error.toString();
      });
    }
  }

  void _previousMonth({bool notify = true}) {
    final firstCurrent = DateTime(DateTime.now().year, DateTime.now().month);
    final end = firstCurrent.subtract(const Duration(days: 1));
    final start = DateTime(end.year, end.month);
    if (notify) {
      setState(() {
        _startDate = start;
        _endDate = end;
      });
    } else {
      _startDate = start;
      _endDate = end;
    }
  }

  void _currentMonth() {
    final now = DateTime.now();
    setState(() {
      _startDate = DateTime(now.year, now.month);
      _endDate = DateTime(now.year, now.month, now.day);
    });
  }

  Future<void> _pickDate({required bool start}) async {
    final today = DateTime.now();
    final latestEnd = _startDate.add(const Duration(days: 45));
    final picked = await showDatePicker(
      context: context,
      initialDate: start
          ? _startDate
          : (_endDate.isAfter(latestEnd) ? latestEnd : _endDate),
      firstDate: start
          ? today.subtract(const Duration(days: 365 * 5))
          : _startDate,
      lastDate: start ? today : (latestEnd.isBefore(today) ? latestEnd : today),
      helpText: start ? 'اختر تاريخ البداية' : 'اختر تاريخ النهاية',
    );
    if (picked == null) return;
    setState(() {
      if (start) {
        _startDate = picked;
        if (_endDate.isBefore(picked)) _endDate = picked;
        if (_endDate.difference(picked).inDays > 45) {
          _endDate = picked.add(const Duration(days: 45));
        }
      } else {
        _endDate = picked;
      }
    });
  }

  bool _validateWindow() {
    final days = _endDate.difference(_startDate).inDays + 1;
    if (days < 1 || days > 45) {
      _message('الحد الأقصى لكل فترة هو 45 يومًا.');
      return false;
    }
    return true;
  }

  Future<void> _startLabsBacktest() async {
    if (!_validateWindow()) return;
    await _submit(() async {
      await ref
          .read(adminRepositoryProvider)
          .createLabsReplayJob(
            startDate: _startDate,
            endDate: _endDate,
            rank: _rank,
            exitMode: _exitMode,
          );
      _message('تم تشغيل محاكاة المختببرات على Worker منفصل.');
    });
  }

  Future<void> _submit(Future<void> Function() operation) async {
    setState(() => _submitting = true);
    try {
      await operation();
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) {
        _message(error is ApiException ? error.message : error.toString());
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _control(HistoricalReplayJob job, String action) async {
    try {
      final repository = ref.read(adminRepositoryProvider);
      switch (action) {
        case 'pause':
          await repository.pauseHistoricalReplay(job.id);
        case 'resume':
          await repository.resumeHistoricalReplay(job.id);
        case 'cancel':
          await repository.cancelHistoricalReplay(job.id);
      }
      await _load(silent: true);
    } on Object catch (error) {
      if (mounted) {
        _message(error is ApiException ? error.message : error.toString());
      }
    }
  }

  void _message(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(text)));
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('d MMMM y', 'ar');
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'تشغيل محاكاة المختببرات (Worker منفصل)',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'محاكاة تقرير الـ10 اليومي على Worker الاختبارات المنفصل دون إبطاء مستخدمي التطبيق.',
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    children: [
                      OutlinedButton(
                        onPressed: _previousMonth,
                        child: const Text('الشهر السابق'),
                      ),
                      OutlinedButton(
                        onPressed: _currentMonth,
                        child: const Text('الشهر الحالي'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _pickDate(start: true),
                          child: Text('من\n${dateFormat.format(_startDate)}'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _pickDate(start: false),
                          child: Text('إلى\n${dateFormat.format(_endDate)}'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<int?>(
                    initialValue: _rank,
                    decoration: const InputDecoration(
                      labelText: 'رتبة السهم في التقرير (اختياري)',
                      border: OutlineInputBorder(),
                    ),
                    items: [
                      const DropdownMenuItem<int?>(
                        value: null,
                        child: Text('كل الرتب (1-10)'),
                      ),
                      for (var r = 1; r <= 10; r++)
                        DropdownMenuItem<int?>(
                          value: r,
                          child: Text('الرتبة $r'),
                        ),
                    ],
                    onChanged: _submitting
                        ? null
                        : (value) => setState(() => _rank = value),
                  ),
                  const SizedBox(height: 12),
                  SegmentedButton<String>(
                    showSelectedIcon: false,
                    segments: const [
                      ButtonSegment(
                        value: 'target_2',
                        label: Text('الهدف الثاني'),
                      ),
                      ButtonSegment(value: 'highest', label: Text('أعلى هدف')),
                    ],
                    selected: <String>{_exitMode},
                    onSelectionChanged: _submitting
                        ? null
                        : (selection) =>
                              setState(() => _exitMode = selection.single),
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _submitting ? null : _startLabsBacktest,
                    icon: _submitting
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.play_arrow),
                    label: const Text('بدء المحاكاة'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'قائمة مهام Worker',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          if (_loading) const Center(child: CircularProgressIndicator()),
          if (_error != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: const Text('تعذر تحميل الوظائف'),
                subtitle: Text(_error!),
              ),
            ),
          if (!_loading && _jobs.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('لا توجد مهام مسجلة.')),
              ),
            ),
          for (final job in _jobs)
            Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            '${dateFormat.format(job.startDate)} — ${dateFormat.format(job.endDate)}',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ),
                        Chip(label: Text(job.status)),
                      ],
                    ),
                    LinearProgressIndicator(
                      value: job.totalTickers == 0
                          ? null
                          : job.progressPct / 100,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '${job.progressPct.toStringAsFixed(1)}% • ${job.processedTickers}/${job.totalTickers} سهم',
                    ),
                    if (job.errorMessage != null) Text(job.errorMessage!),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: [
                        if (job.canPause)
                          OutlinedButton(
                            onPressed: () => _control(job, 'pause'),
                            child: const Text('إيقاف مؤقت'),
                          ),
                        if (job.canResume)
                          FilledButton.tonal(
                            onPressed: () => _control(job, 'resume'),
                            child: const Text('استكمال'),
                          ),
                        if (job.canCancel)
                          TextButton(
                            onPressed: () => _control(job, 'cancel'),
                            child: const Text('إلغاء'),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

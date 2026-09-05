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
      length: 10,
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
              Tab(text: 'ترقية الخطط'),
              Tab(text: 'الإعدادات'),
              Tab(text: 'الإشعارات'),
              Tab(text: 'التدقيق'),
              Tab(text: 'وظائف إعادة اللعب'),
              Tab(text: 'إعادة التقرير'),
              Tab(text: 'ملاحظات المستخدمين'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            _OverviewTab(),
            _ModerationTab(),
            _UsersTab(),
            _UserPlanUpgradeTab(),
            _SettingsTab(),
            _BroadcastTab(),
            _AuditTab(),
            _ReplayJobsTab(),
            _RegenerateReportTab(),
            _UserFeedbacksTab(),
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
                _Metric('إجمالي المسجلين', item.usersTotal),
                _Metric('النشطون الآن 🟢', item.usersActiveNow),
                _Metric('حسابات مفعلة ✅', item.usersVerified),
                _Metric('غير مفعلة ❌', item.usersUnverified),
                _Metric('النشطون بالحساب', item.usersActive),
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

class _RegenerateReportTab extends ConsumerStatefulWidget {
  const _RegenerateReportTab();

  @override
  ConsumerState<_RegenerateReportTab> createState() =>
      _RegenerateReportTabState();
}

class _RegenerateReportTabState extends ConsumerState<_RegenerateReportTab> {
  bool _loading = false;
  String? _statusMessage;
  bool _isSuccess = false;

  bool _loadingInvestment = false;
  String? _investmentStatusMessage;
  bool _isInvestmentSuccess = false;

  Future<void> _regenerate() async {
    setState(() {
      _loading = true;
      _statusMessage = null;
    });

    try {
      final repo = ref.read(adminRepositoryProvider);
      final result = await repo.regenerateDailyReport();
      setState(() {
        _loading = false;
        _isSuccess = true;
        _statusMessage =
            result['message']?.toString() ?? 'تم إعادة التقرير بنجاح.';
      });
    } catch (error) {
      setState(() {
        _loading = false;
        _isSuccess = false;
        _statusMessage = error is ApiException
            ? error.message
            : 'حدث خطأ أثناء تنفيذ الطلب.';
      });
    }
  }

  Future<void> _regenerateInvestment() async {
    setState(() {
      _loadingInvestment = true;
      _investmentStatusMessage = null;
    });

    try {
      final repo = ref.read(adminRepositoryProvider);
      final result = await repo.regenerateInvestmentReport();
      setState(() {
        _loadingInvestment = false;
        _isInvestmentSuccess = true;
        _investmentStatusMessage =
            result['message']?.toString() ?? 'تم تحديث تقارير الاستثمار بنجاح.';
      });
    } catch (error) {
      setState(() {
        _loadingInvestment = false;
        _isInvestmentSuccess = false;
        _investmentStatusMessage = error is ApiException
            ? error.message
            : 'حدث خطأ أثناء إعادة تقرير الاستثمار.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Icon(
                  Icons.published_with_changes_rounded,
                  size: 48,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(height: 12),
                Text(
                  'إعادة إنشاء تقرير المضاربة اليومي',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 6),
                Text(
                  'استخدم هذا الخيار لإعادة تشغيل محرك التقارير فور إدخال تحديثات جديدة على خوارزميات المحرك (VWAP, Momentum).',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
                if (_statusMessage != null) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: _isSuccess
                          ? Colors.green.withValues(alpha: 0.1)
                          : theme.colorScheme.errorContainer,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      _statusMessage!,
                      style: TextStyle(
                        color: _isSuccess
                            ? Colors.green
                            : theme.colorScheme.onErrorContainer,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: _loading ? null : _regenerate,
                  icon: _loading
                      ? const SizedBox.square(
                          dimension: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.refresh_rounded),
                  label: Text(
                    _loading
                        ? 'جاري إعادة الإنشاء...'
                        : 'تشغيل إعادة تقرير المضاربة',
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Icon(
                  Icons.account_balance_rounded,
                  size: 48,
                  color: theme.colorScheme.secondary,
                ),
                const SizedBox(height: 12),
                Text(
                  'إعادة إنشاء تقارير الأسهم الاستثمارية',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 6),
                Text(
                  'استخدم هذا الخيار لإعادة مسح مؤشرات TradingView الأساسية وحساب القيمة العادلة وهامش الأمان وتحديث الفرص فوراً.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
                if (_investmentStatusMessage != null) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: _isInvestmentSuccess
                          ? Colors.green.withValues(alpha: 0.1)
                          : theme.colorScheme.errorContainer,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      _investmentStatusMessage!,
                      style: TextStyle(
                        color: _isInvestmentSuccess
                            ? Colors.green
                            : theme.colorScheme.onErrorContainer,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                FilledButton.tonalIcon(
                  onPressed: _loadingInvestment ? null : _regenerateInvestment,
                  icon: _loadingInvestment
                      ? const SizedBox.square(
                          dimension: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.sync_rounded),
                  label: Text(
                    _loadingInvestment
                        ? 'جاري تحديث تقارير الاستثمار...'
                        : 'إعادة إنشاء تقارير الاستثمار الآن',
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _UserPlanUpgradeTab extends ConsumerStatefulWidget {
  const _UserPlanUpgradeTab();

  @override
  ConsumerState<_UserPlanUpgradeTab> createState() =>
      _UserPlanUpgradeTabState();
}

class _UserPlanUpgradeTabState extends ConsumerState<_UserPlanUpgradeTab> {
  AdminUserItem? _selectedUser;
  String _searchQuery = '';
  String _selectedPlan = 'pro';
  int _durationDays = 30;
  final _bonusPointsController = TextEditingController(text: '0');
  bool _loading = false;
  String? _statusMessage;
  bool _isSuccess = false;

  @override
  void dispose() {
    _bonusPointsController.dispose();
    super.dispose();
  }

  Future<void> _upgradePlan() async {
    final user = _selectedUser;
    if (user == null) {
      setState(() {
        _statusMessage = 'يرجى اختيار مستخدم أولاً.';
        _isSuccess = false;
      });
      return;
    }

    setState(() {
      _loading = true;
      _statusMessage = null;
    });

    try {
      final repo = ref.read(adminRepositoryProvider);
      final bonus = int.tryParse(_bonusPointsController.text.trim()) ?? 0;
      final res = await repo.upgradeUserPlan(
        userId: user.id,
        planCode: _selectedPlan,
        durationDays: _durationDays > 0 ? _durationDays : null,
        bonusPoints: bonus,
      );
      if (!mounted) return;
      setState(() {
        _loading = false;
        _isSuccess = true;
        _statusMessage =
            res['message']?.toString() ?? 'تمت ترقية خطة المستخدم بنجاح.';
      });
      ref.invalidate(adminUsersProvider);
      ref.invalidate(adminOverviewProvider);
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _isSuccess = false;
        _statusMessage = error is ApiException
            ? error.message
            : 'فشلت ترقية الخطة.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final usersAsync = ref.watch(adminUsersProvider);

    return usersAsync.when(
      loading: () => const _Loading(),
      error: (_, __) => const _Failure('تعذر تحميل المستخدمين.'),
      data: (users) {
        final filteredUsers = users.where((u) {
          if (_searchQuery.isEmpty) return true;
          return u.displayName.toLowerCase().contains(
                _searchQuery.toLowerCase(),
              ) ||
              u.email.toLowerCase().contains(_searchQuery.toLowerCase());
        }).toList();

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              'ترقية خطة مستخدم يدويًا',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'اختر المستخدم والمدة والخطة المطلوبة لترقيته فوريًا.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextField(
                      decoration: const InputDecoration(
                        labelText: 'بحث عن مستخدم بالاسم أو الإيميل',
                        prefixIcon: Icon(Icons.search_rounded),
                      ),
                      onChanged: (val) =>
                          setState(() => _searchQuery = val.trim()),
                    ),
                    const SizedBox(height: 12),
                    if (_selectedUser != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.person_rounded,
                              color: theme.colorScheme.onPrimaryContainer,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _selectedUser!.displayName,
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color:
                                          theme.colorScheme.onPrimaryContainer,
                                    ),
                                  ),
                                  Text(
                                    '${_selectedUser!.email} • خطته الحالية: ${_selectedUser!.planCode}',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: theme
                                          .colorScheme
                                          .onPrimaryContainer
                                          .withValues(alpha: 0.8),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              onPressed: () =>
                                  setState(() => _selectedUser = null),
                              icon: const Icon(Icons.close_rounded),
                              tooltip: 'إلغاء التحديد',
                            ),
                          ],
                        ),
                      ),
                    ] else ...[
                      Text(
                        'اختر مستخدمًا من القائمة (${filteredUsers.length}):',
                        style: theme.textTheme.bodySmall,
                      ),
                      const SizedBox(height: 8),
                      Container(
                        constraints: const BoxConstraints(maxHeight: 180),
                        decoration: BoxDecoration(
                          border: Border.all(color: theme.dividerColor),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: ListView.builder(
                          shrinkWrap: true,
                          itemCount: filteredUsers.take(20).length,
                          itemBuilder: (context, idx) {
                            final u = filteredUsers[idx];
                            return ListTile(
                              dense: true,
                              title: Text(u.displayName),
                              subtitle: Text('${u.email} (${u.planCode})'),
                              trailing: const Icon(
                                Icons.arrow_forward_ios_rounded,
                                size: 14,
                              ),
                              onTap: () => setState(() => _selectedUser = u),
                            );
                          },
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'الخطة المستهدفة:',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 10),
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'free', label: Text('المجانية')),
                        ButtonSegment(value: 'basic', label: Text('الأساسية')),
                        ButtonSegment(
                          value: 'advanced',
                          label: Text('المتقدمة'),
                        ),
                        ButtonSegment(value: 'pro', label: Text('الاحترافية')),
                      ],
                      selected: {_selectedPlan},
                      onSelectionChanged: (set) =>
                          setState(() => _selectedPlan = set.first),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'مدة الاشتراك:',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 10),
                    SegmentedButton<int>(
                      segments: const [
                        ButtonSegment(value: 30, label: Text('شهر')),
                        ButtonSegment(value: 90, label: Text('3 أشهر')),
                        ButtonSegment(value: 365, label: Text('سنة')),
                        ButtonSegment(value: 0, label: Text('دائم')),
                      ],
                      selected: {_durationDays},
                      onSelectionChanged: (set) =>
                          setState(() => _durationDays = set.first),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _bonusPointsController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'نقاط إضافية للمحفظة (اختياري)',
                        hintText: '0',
                        prefixIcon: Icon(Icons.monetization_on_outlined),
                      ),
                    ),
                    const SizedBox(height: 20),
                    if (_statusMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: _isSuccess
                              ? Colors.green.withValues(alpha: 0.1)
                              : theme.colorScheme.errorContainer,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          _statusMessage!,
                          style: TextStyle(
                            color: _isSuccess
                                ? Colors.green
                                : theme.colorScheme.onErrorContainer,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                    FilledButton.icon(
                      onPressed: _loading || _selectedUser == null
                          ? null
                          : _upgradePlan,
                      icon: _loading
                          ? const SizedBox.square(
                              dimension: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.verified_user_rounded),
                      label: Text(
                        _loading
                            ? 'جاري ترقية الخطة...'
                            : 'تنفيذ ترقية الخطة الآن',
                      ),
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _UserFeedbacksTab extends ConsumerStatefulWidget {
  const _UserFeedbacksTab();

  @override
  ConsumerState<_UserFeedbacksTab> createState() => _UserFeedbacksTabState();
}

class _UserFeedbacksTabState extends ConsumerState<_UserFeedbacksTab> {
  bool _loading = false;
  String? _error;
  List<Map<String, dynamic>> _items = [];
  int _total = 0;

  @override
  void initState() {
    super.initState();
    _loadFeedbacks();
  }

  Future<void> _loadFeedbacks() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final repository = ref.read(adminRepositoryProvider);
      final data = await repository.fetchUserFeedbacks();
      if (mounted) {
        setState(() {
          _items = List<Map<String, dynamic>>.from(data['items'] as List);
          _total = (data['total'] as num?)?.toInt() ?? _items.length;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() => _error = e.message);
      }
    } on Object catch (e) {
      if (mounted) {
        setState(() => _error = e.toString());
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _updateStatus(String feedbackId, String newStatus) async {
    try {
      final repository = ref.read(adminRepositoryProvider);
      await repository.updateFeedbackStatus(feedbackId, newStatus);
      await _loadFeedbacks();
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تعذر تحديث الحالة: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null && _items.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_error!),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: _loadFeedbacks,
              child: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadFeedbacks,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'إجمالي الملاحظات: $_total',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              IconButton(
                onPressed: _loadFeedbacks,
                icon: const Icon(Icons.refresh_rounded),
                tooltip: 'تحديث',
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (_items.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(28),
                child: Center(
                  child: Text('لا توجد ملاحظات من المستخدمين حالياً.'),
                ),
              ),
            )
          else
            for (final fb in _items) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            ((fb['user'] as Map?)?['display_name'] as String?) ?? 'مستخدم',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          PopupMenuButton<String>(
                            onSelected: (String status) => _updateStatus(fb['id'] as String, status),
                            itemBuilder: (context) => const [
                              PopupMenuItem(value: 'new', child: Text('جديدة 🟡')),
                              PopupMenuItem(value: 'reviewed', child: Text('تمت المراجعة 🔵')),
                              PopupMenuItem(value: 'resolved', child: Text('تم الحل 🟢')),
                              PopupMenuItem(value: 'archived', child: Text('مؤرشفة ⚪')),
                            ],
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: fb['status'] == 'new'
                                    ? Colors.amber.withOpacity(0.15)
                                    : fb['status'] == 'reviewed'
                                        ? Colors.blue.withOpacity(0.15)
                                        : fb['status'] == 'resolved'
                                            ? Colors.green.withOpacity(0.15)
                                            : Colors.grey.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: fb['status'] == 'new'
                                      ? Colors.amber
                                      : fb['status'] == 'reviewed'
                                          ? Colors.blue
                                          : fb['status'] == 'resolved'
                                              ? Colors.green
                                              : Colors.grey,
                                ),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    fb['status'] == 'new'
                                        ? 'جديدة'
                                        : fb['status'] == 'reviewed'
                                            ? 'تمت المراجعة'
                                            : fb['status'] == 'resolved'
                                                ? 'تم الحل'
                                                : 'مؤرشفة',
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      color: fb['status'] == 'new'
                                          ? Colors.amber.shade300
                                          : fb['status'] == 'reviewed'
                                              ? Colors.blue.shade300
                                              : fb['status'] == 'resolved'
                                                  ? Colors.green.shade300
                                                  : Colors.grey.shade300,
                                    ),
                                  ),
                                  const SizedBox(width: 4),
                                  Icon(
                                    Icons.arrow_drop_down_rounded,
                                    size: 18,
                                    color: fb['status'] == 'new'
                                        ? Colors.amber.shade300
                                        : fb['status'] == 'reviewed'
                                            ? Colors.blue.shade300
                                            : fb['status'] == 'resolved'
                                                ? Colors.green.shade300
                                                : Colors.grey.shade300,
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                      Text(
                        ((fb['user'] as Map?)?['email'] as String?) ?? '',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 10),
                      Text(
                        fb['message'] as String? ?? '',
                        style: const TextStyle(fontSize: 15, height: 1.4),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          if (fb['status'] != 'reviewed')
                            OutlinedButton.icon(
                              onPressed: () => _updateStatus(
                                fb['id'] as String,
                                'reviewed',
                              ),
                              icon: const Icon(Icons.check_circle_outline, size: 16),
                              label: const Text('تعليم كمراجعة'),
                            ),
                          const SizedBox(width: 8),
                          if (fb['status'] != 'resolved')
                            FilledButton.icon(
                              onPressed: () => _updateStatus(
                                fb['id'] as String,
                                'resolved',
                              ),
                              icon: const Icon(Icons.done_all_rounded, size: 16),
                              label: const Text('تم التعامل معها'),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 10),
            ],
        ],
      ),
    );
  }
}

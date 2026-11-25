import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import 'signals_models.dart';
import 'signals_providers.dart';

/// تسميات حالات الإشارة بالعربية (تُستخدم في القائمة وشاشة التفاصيل).
const Map<String, String> signalStateLabels = <String, String>{
  'new': 'جديد',
  'buy': 'شراء',
  't1done': 'حقق الهدف 1',
  't2done': 'حقق الهدف 2',
  't3done': 'حقق الهدف 3',
  'tsl': 'وقف متحرك',
  'closed': 'مغلق',
  'expired': 'منتهية',
};

class SignalsScreen extends ConsumerStatefulWidget {
  const SignalsScreen({super.key});

  @override
  ConsumerState<SignalsScreen> createState() => _SignalsScreenState();
}

class _SignalsScreenState extends ConsumerState<SignalsScreen> {
  String? _state;
  bool _mine = false;
  String _query = '';

  SignalsFilter get _filter => SignalsFilter(state: _state, mine: _mine);

  Future<void> _refresh(SignalsFilter filter) async {
    ref.invalidate(signalsListProvider(filter));
    try {
      await ref.read(signalsListProvider(filter).future);
    } on Object catch (error) {
      debugPrint('signals refresh failed: $error');
    }
  }

  @override
  Widget build(BuildContext context) {
    final filter = _filter;
    final listState = ref.watch(signalsListProvider(filter));
    return Scaffold(
      appBar: AppBar(title: const Text('الإشارات')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: TextField(
              textDirection: TextDirection.ltr,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search_rounded),
                hintText: 'بحث برمز السهم — COMI',
                isDense: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(14)),
                ),
              ),
              onChanged: (value) =>
                  setState(() => _query = value.trim().toUpperCase()),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Wrap(
              spacing: 8,
              runSpacing: 4,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                const Text(
                  'الحالة:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                ChoiceChip(
                  label: const Text('الكل'),
                  selected: _state == null,
                  onSelected: (_) => setState(() => _state = null),
                ),
                for (final entry in signalStateLabels.entries)
                  ChoiceChip(
                    label: Text(entry.value),
                    selected: _state == entry.key,
                    onSelected: (_) => setState(() => _state = entry.key),
                  ),
                FilterChip(
                  label: const Text('ملكي فقط'),
                  selected: _mine,
                  onSelected: (value) => setState(() => _mine = value),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Text(
                'عرض الإشارات من الخادم: ${listState.valueOrNull?.count ?? 0}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          Expanded(
            child: listState.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stackTrace) => _SignalsErrorView(
                error: error,
                onRetry: () => ref.invalidate(signalsListProvider(filter)),
              ),
              data: (page) => _buildList(page, filter),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildList(ApiList<Signal> page, SignalsFilter filter) {
    final items = page.items
        .where(
          (Signal signal) =>
              _query.isEmpty || signal.ticker.toUpperCase().contains(_query),
        )
        .toList(growable: false);
    return RefreshIndicator(
      onRefresh: () => _refresh(filter),
      child: items.isEmpty
          ? ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 24),
              children: [
                _SignalsEmptyView(
                  icon: page.items.isEmpty
                      ? Icons.show_chart_rounded
                      : Icons.search_off_rounded,
                  message: page.items.isEmpty
                      ? 'لا توجد إشارات متاحة حاليًا.'
                      : 'لا توجد نتائج مطابقة للفلاتر أو البحث الحالي.',
                  hint: 'اسحب للأسفل لتحديث البيانات.',
                ),
              ],
            )
          : ListView.builder(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              itemCount: items.length,
              itemBuilder: (context, index) => _SignalRow(signal: items[index]),
            ),
    );
  }
}

class _SignalRow extends StatelessWidget {
  const _SignalRow({required this.signal});

  final Signal signal;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/signals/${signal.id}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    signal.ticker,
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(width: 8),
                  _LabelChip(
                    label: signal.isLong ? 'شراء' : 'بيع',
                    color: signal.isLong
                        ? Colors.green.shade700
                        : Colors.red.shade700,
                  ),
                  const SizedBox(width: 8),
                  _LabelChip(
                    label: signalStateLabels[signal.state] ?? signal.state,
                    color: signalStateColor(signal.state),
                  ),
                  const Spacer(),
                  Text(
                    _formatSigned(signal.pnlPct, suffix: '%'),
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: _signedColor(signal.pnlPct),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _Metric(
                      label: 'الدخول',
                      value: _formatNumber(signal.entry),
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'الوقف',
                      value: _formatNumber(signal.stop),
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'هدف 1',
                      value: _formatNumber(signal.t1),
                    ),
                  ),
                ],
              ),
              if (signal.t2 != null ||
                  signal.t3 != null ||
                  signal.trailingStop != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    if (signal.t2 != null)
                      Expanded(
                        child: _Metric(
                          label: 'هدف 2',
                          value: _formatNumber(signal.t2),
                        ),
                      ),
                    if (signal.t3 != null)
                      Expanded(
                        child: _Metric(
                          label: 'هدف 3',
                          value: _formatNumber(signal.t3),
                        ),
                      ),
                    if (signal.trailingStop != null)
                      Expanded(
                        child: _Metric(
                          label: 'وقف متحرك',
                          value: _formatNumber(signal.trailingStop),
                          color: Colors.amber.shade800,
                        ),
                      ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value, this.color});

  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          value,
          textDirection: TextDirection.ltr,
          textAlign: TextAlign.center,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w800,
            color: color,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          textAlign: TextAlign.center,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

class _LabelChip extends StatelessWidget {
  const _LabelChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

class _SignalsEmptyView extends StatelessWidget {
  const _SignalsEmptyView({
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
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: theme.colorScheme.onSurfaceVariant),
          const SizedBox(height: 12),
          Text(
            message,
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          if (hint != null) ...[
            const SizedBox(height: 6),
            Text(
              hint!,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _SignalsErrorView extends StatelessWidget {
  const _SignalsErrorView({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 48),
            const SizedBox(height: 12),
            Text(
              error is ApiException
                  ? (error as ApiException).message
                  : 'تعذر تحميل بيانات الإشارات.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

/// لون شارة الحالة: الرمادي للجديد، الأزرق للشراء، الأخضر تصاعديًا مع
/// تحقق الأهداف، الكهرماني للوقف المتحرك، والأزرق الرمادي للمغلق/المنتهي.
Color signalStateColor(String state) {
  return switch (state) {
    'new' => Colors.grey,
    'buy' => Colors.blue.shade700,
    't1done' => Colors.lightGreen.shade700,
    't2done' => Colors.green.shade700,
    't3done' => Colors.green.shade900,
    'tsl' => Colors.amber.shade700,
    'closed' || 'expired' => Colors.blueGrey,
    _ => Colors.blueGrey.shade400,
  };
}

Color? _signedColor(double? value) {
  if (value == null) return null;
  if (value > 0) return Colors.green.shade700;
  if (value < 0) return Colors.red.shade700;
  return null;
}

String _formatNumber(double? value) {
  if (value == null) return '—';
  return value.toStringAsFixed(2);
}

String _formatSigned(double? value, {String suffix = ''}) {
  if (value == null) return '—';
  final sign = value > 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(2)}$suffix';
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import 'scanner_models.dart';
import 'scanner_providers.dart';

const String _allOption = 'الجميع';

const Map<String, String> _patternLabels = <String, String>{
  'gartley': 'جيرتلي',
  'bat': 'الخفاش',
  'butterfly': 'الفراشة',
  'crab': 'السلطعون',
};

class ScannerScreen extends ConsumerStatefulWidget {
  const ScannerScreen({super.key});

  @override
  ConsumerState<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends ConsumerState<ScannerScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(
    length: 3,
    vsync: this,
  );
  int _tabIndex = 0;

  @override
  void initState() {
    super.initState();
    _tabController.addListener(_handleTabChange);
  }

  void _handleTabChange() {
    if (_tabController.index != _tabIndex) {
      setState(() => _tabIndex = _tabController.index);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الأسكانر'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'فني'),
            Tab(text: 'فيبوناتشي'),
            Tab(text: 'هارمونيك'),
          ],
        ),
      ),
      body: IndexedStack(
        index: _tabIndex,
        children: const [
          _TechnicalScannerTab(),
          _FibonacciScannerTab(),
          _HarmonicScannerTab(),
        ],
      ),
    );
  }
}

enum _TechnicalSort { score, performance20d, rsi }

class _TechnicalScannerTab extends ConsumerStatefulWidget {
  const _TechnicalScannerTab();

  @override
  ConsumerState<_TechnicalScannerTab> createState() =>
      _TechnicalScannerTabState();
}

class _TechnicalScannerTabState extends ConsumerState<_TechnicalScannerTab> {
  final Set<String> _knownSectors = <String>{};
  String _query = '';
  String _sector = _allOption;
  String _rating = _allOption;
  _TechnicalSort _sort = _TechnicalSort.score;
  bool _descending = true;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(scannerTechnicalProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => _ScannerErrorView(
        error: error,
        onRetry: () => ref.invalidate(scannerTechnicalProvider),
      ),
      data: (list) {
        _knownSectors
          ..clear()
          ..addAll(
            list.items
                .map((ScannerTechnicalItem item) => item.sector)
                .whereType<String>()
                .where((String sector) => sector.isNotEmpty),
          );
        return _buildContent(list.items);
      },
    );
  }

  Widget _buildContent(List<ScannerTechnicalItem> items) {
    final theme = Theme.of(context);
    if (_sector != _allOption && !_knownSectors.contains(_sector)) {
      _sector = _allOption;
    }
    if (_rating != _allOption &&
        !const <String>{'buy', 'sell', 'neutral'}.contains(_rating)) {
      _rating = _allOption;
    }
    final sectors = _knownSectors.toList()..sort();
    final results = _applyFilters(items);

    return Column(
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
                'الترتيب:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              _sortChip('التقييم الفني', _TechnicalSort.score),
              _sortChip('أداء 20 يوم', _TechnicalSort.performance20d),
              _sortChip('RSI', _TechnicalSort.rsi),
              IconButton(
                visualDensity: VisualDensity.compact,
                icon: Icon(
                  _descending
                      ? Icons.arrow_downward_rounded
                      : Icons.arrow_upward_rounded,
                ),
                tooltip: _descending
                    ? 'تنازلي (الأعلى أولًا)'
                    : 'تصاعدي (الأدنى أولًا)',
                onPressed: () => setState(() => _descending = !_descending),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
          child: Row(
            children: [
              Expanded(child: _sectorDropdown(sectors)),
              const SizedBox(width: 12),
              Expanded(child: _ratingDropdown()),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 4),
          child: Align(
            alignment: AlignmentDirectional.centerStart,
            child: Text(
              'عدد النتائج: ${results.length}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _refresh,
            child: results.isEmpty
                ? ListView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    children: [
                      _ScannerEmptyView(
                        icon: items.isEmpty
                            ? Icons.query_stats_rounded
                            : Icons.search_off_rounded,
                        message: items.isEmpty
                            ? 'لا توجد بيانات أسكانر فنية متاحة حاليًا.'
                            : 'لا توجد نتائج مطابقة للفلاتر أو البحث الحالي.',
                        hint: 'اسحب للأسفل لتحديث البيانات.',
                      ),
                    ],
                  )
                : ListView.builder(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
                    itemCount: results.length,
                    itemBuilder: (context, index) =>
                        _TechnicalRow(item: results[index]),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _sortChip(String label, _TechnicalSort value) {
    return ChoiceChip(
      label: Text(label),
      selected: _sort == value,
      onSelected: (_) => setState(() => _sort = value),
    );
  }

  Widget _sectorDropdown(List<String> sectors) {
    return DropdownButtonFormField<String>(
      initialValue: _sector,
      isExpanded: true,
      decoration: const InputDecoration(
        isDense: true,
        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        border: OutlineInputBorder(),
      ),
      items: <String>[_allOption, ...sectors]
          .map(
            (String sector) => DropdownMenuItem<String>(
              value: sector,
              child: Text(sector, overflow: TextOverflow.ellipsis),
            ),
          )
          .toList(growable: false),
      onChanged: (value) {
        if (value != null) {
          setState(() => _sector = value);
        }
      },
    );
  }

  Widget _ratingDropdown() {
    const labels = <String, String>{
      _allOption: 'الجميع',
      'buy': 'شراء',
      'sell': 'بيع',
      'neutral': 'محايد',
    };
    return DropdownButtonFormField<String>(
      initialValue: _rating,
      isExpanded: true,
      decoration: const InputDecoration(
        isDense: true,
        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        border: OutlineInputBorder(),
      ),
      items: labels.entries
          .map(
            (entry) => DropdownMenuItem<String>(
              value: entry.key,
              child: Text(entry.value, overflow: TextOverflow.ellipsis),
            ),
          )
          .toList(growable: false),
      onChanged: (value) {
        if (value != null) {
          setState(() => _rating = value);
        }
      },
    );
  }

  List<ScannerTechnicalItem> _applyFilters(List<ScannerTechnicalItem> items) {
    final results = items.where((ScannerTechnicalItem item) {
      if (_query.isNotEmpty && !item.symbol.toUpperCase().contains(_query)) {
        return false;
      }
      if (_sector != _allOption && item.sector != _sector) {
        return false;
      }
      if (_rating != _allOption &&
          (item.technicalRating ?? item.rating) != _rating) {
        return false;
      }
      return true;
    }).toList();
    results.sort(_compare);
    return results;
  }

  int _compare(ScannerTechnicalItem a, ScannerTechnicalItem b) {
    final left = _sortValue(a);
    final right = _sortValue(b);
    if (left == null || right == null) {
      final nullAware = _nullAwareCompare(left, right);
      if (nullAware != 0) {
        return nullAware;
      }
    } else {
      final ordered = left.compareTo(right);
      if (ordered != 0) {
        return _descending ? -ordered : ordered;
      }
    }
    return a.symbol.compareTo(b.symbol);
  }

  double? _sortValue(ScannerTechnicalItem item) {
    return switch (_sort) {
      _TechnicalSort.score => item.technicalScore,
      _TechnicalSort.performance20d => item.performance20d,
      _TechnicalSort.rsi => item.rsi14,
    };
  }

  static int _nullAwareCompare(double? a, double? b) {
    if (a == null && b == null) return 0;
    if (a == null) return 1;
    if (b == null) return -1;
    return 0;
  }

  Future<void> _refresh() async {
    ref.invalidate(scannerTechnicalProvider);
    await ref.read(scannerTechnicalProvider.future);
  }
}

class _FibonacciScannerTab extends ConsumerWidget {
  const _FibonacciScannerTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(scannerFibonacciProvider);
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stackTrace) => _ScannerErrorView(
        error: error,
        onRetry: () => ref.invalidate(scannerFibonacciProvider),
      ),
      data: (list) {
        final items = list.items;
        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(scannerFibonacciProvider);
            await ref.read(scannerFibonacciProvider.future);
          },
          child: items.isEmpty
              ? ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  children: const [
                    _ScannerEmptyView(
                      icon: Icons.timeline_rounded,
                      message: 'لا توجد بيانات أسكانر فيبوناتشي متاحة حاليًا.',
                      hint: 'اسحب للأسفل لتحديث البيانات.',
                    ),
                  ],
                )
              : ListView.builder(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  itemCount: items.length,
                  itemBuilder: (context, index) =>
                      _FibonacciRow(item: items[index]),
                ),
        );
      },
    );
  }
}

class _HarmonicScannerTab extends ConsumerStatefulWidget {
  const _HarmonicScannerTab();

  @override
  ConsumerState<_HarmonicScannerTab> createState() =>
      _HarmonicScannerTabState();
}

class _HarmonicScannerTabState extends ConsumerState<_HarmonicScannerTab> {
  final TextEditingController _controller = TextEditingController();
  final List<String> _symbols = <String>[];
  String _input = '';

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _checkSymbol() {
    final symbol = _controller.text.trim().toUpperCase();
    if (symbol.isEmpty) return;
    setState(() {
      if (!_symbols.contains(symbol)) {
        _symbols.add(symbol);
      }
      _controller.clear();
      _input = '';
    });
  }

  Future<void> _refresh() async {
    final pending = <Future<ScannerHarmonicItem>>[];
    for (final symbol in _symbols) {
      ref.invalidate(scannerHarmonicProvider(symbol));
      pending.add(ref.read(scannerHarmonicProvider(symbol).future));
    }
    if (pending.isEmpty) return;
    try {
      await Future.wait(pending);
    } on Object {
      return;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  textDirection: TextDirection.ltr,
                  textCapitalization: TextCapitalization.characters,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search_rounded),
                    hintText: 'أدخل رمز السهم — COMI',
                    isDense: true,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.all(Radius.circular(14)),
                    ),
                  ),
                  onChanged: (value) => setState(() => _input = value),
                  onSubmitted: (_) => _checkSymbol(),
                ),
              ),
              const SizedBox(width: 8),
              FilledButton.icon(
                onPressed: _input.trim().isEmpty ? null : _checkSymbol,
                icon: const Icon(Icons.radar_rounded, size: 18),
                label: const Text('فحص'),
              ),
            ],
          ),
        ),
        Expanded(child: _buildResults()),
      ],
    );
  }

  Widget _buildResults() {
    if (_symbols.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 24),
        children: const [
          _ScannerEmptyView(
            icon: Icons.travel_explore_rounded,
            message: 'لم يتم فحص أي سهم بعد.',
            hint: 'أدخل رمز سهم للكشف عن الأنماط الهارمونية المكتشفة.',
          ),
        ],
      );
    }

    final states = <String, AsyncValue<ScannerHarmonicItem>>{};
    for (final symbol in _symbols) {
      states[symbol] = ref.watch(scannerHarmonicProvider(symbol));
    }
    final anyLoading = states.values.any(
      (AsyncValue<ScannerHarmonicItem> state) => state.isLoading,
    );
    final anyDetected = states.values.any(
      (AsyncValue<ScannerHarmonicItem> state) =>
          state.valueOrNull?.patterns.isNotEmpty ?? false,
    );

    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
        children: [
          if (!anyLoading && !anyDetected)
            const _ScannerEmptyView(
              icon: Icons.travel_explore_rounded,
              message: 'لا توجد أنماط هارمونية مكتشفة حاليًا.',
              hint: 'جرّب رموزًا أخرى أو حدّث البيانات.',
            ),
          for (final symbol in _symbols)
            _buildSymbolState(symbol, states[symbol]!),
        ],
      ),
    );
  }

  Widget _buildSymbolState(
    String symbol,
    AsyncValue<ScannerHarmonicItem> state,
  ) {
    return state.when(
      loading: () => _symbolShell(
        symbol,
        children: [
          const Spacer(),
          const SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          const SizedBox(width: 8),
          Text(
            'جارٍ الفحص...',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
      error: (error, stackTrace) {
        final notFound = error is ApiException && error.statusCode == 404;
        final message = notFound
            ? 'لا توجد نتائج هارمونية محفوظة لهذا الرمز.'
            : error is ApiException
            ? error.message
            : 'تعذر فحص هذا الرمز.';
        return _symbolShell(
          symbol,
          children: [
            Expanded(
              child: Text(
                message,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
            TextButton(
              onPressed: () => ref.invalidate(scannerHarmonicProvider(symbol)),
              child: const Text('إعادة المحاولة'),
            ),
          ],
        );
      },
      data: (item) {
        if (item.patterns.isEmpty) {
          return _symbolShell(
            symbol,
            children: [
              const Spacer(),
              Text(
                'لم يتم اكتشاف أنماط هارمونية لهذا الرمز.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          );
        }
        return _HarmonicResultView(item: item);
      },
    );
  }

  Widget _symbolShell(String symbol, {required List<Widget> children}) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 10, 8, 10),
        child: Row(
          children: [
            Text(
              symbol,
              textDirection: TextDirection.ltr,
              style: Theme.of(
                context,
              ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(width: 10),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _TechnicalRow extends StatelessWidget {
  const _TechnicalRow({required this.item});

  final ScannerTechnicalItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (ratingLabel, ratingColor) = _ratingStyle(
      item.technicalRating ?? item.rating,
    );
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/stocks/${item.symbol}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    item.symbol,
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item.sector ?? '',
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                  _LabelChip(label: ratingLabel, color: ratingColor),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _Metric(
                      label: 'التقييم الفني',
                      value: _formatSigned(item.technicalScore),
                      color: _signedColor(item.technicalScore),
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'RSI (14)',
                      value: _formatNumber(item.rsi14),
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'أداء 20 يوم',
                      value: _formatSigned(item.performance20d, suffix: '%'),
                      color: _signedColor(item.performance20d),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FibonacciRow extends StatelessWidget {
  const _FibonacciRow({required this.item});

  final ScannerFibonacciItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/stocks/${item.symbol}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    item.symbol,
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item.sector ?? '',
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                  _LabelChip(
                    label: _fibStatusLabel(item.status),
                    color: _fibStatusColor(item.status),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _Metric(
                      label: 'السعر',
                      value: _formatNumber(item.price),
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'نسبة الانسحاب',
                      value: _formatNumber(
                        item.retracementPercent,
                        suffix: '%',
                      ),
                      color: _signedColor(item.retracementPercent),
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'التقييم',
                      value: _formatNumber(item.score),
                      color: _scoreColor(item.score),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'المنطقة الحالية: ${item.currentZone?.labelAr ?? '—'}',
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (item.distancePercent != null)
                Text(
                  'المسافة لأقرب مستوى: ${_formatNumber(item.distancePercent, suffix: '%')}',
                  textDirection: TextDirection.ltr,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HarmonicResultView extends StatelessWidget {
  const _HarmonicResultView({required this.item});

  final ScannerHarmonicItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (ratingLabel, ratingColor) = _ratingStyle(item.rating);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/stocks/${item.symbol}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    item.symbol,
                    textDirection: TextDirection.ltr,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${item.patterns.length} نمط مكتشف',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                  _LabelChip(label: ratingLabel, color: ratingColor),
                ],
              ),
              const SizedBox(height: 6),
              for (final pattern in item.patterns)
                Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.change_history_rounded,
                        size: 16,
                        color: Colors.amber,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          _patternLabels[pattern.type] ?? pattern.type,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      Text(
                        _patternStatusLabel(pattern.status),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        _formatNumber(pattern.score),
                        textDirection: TextDirection.ltr,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
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

class _ScannerEmptyView extends StatelessWidget {
  const _ScannerEmptyView({
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

class _ScannerErrorView extends StatelessWidget {
  const _ScannerErrorView({required this.error, required this.onRetry});

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
                  : 'تعذر تحميل بيانات الأسكانر.',
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

(String, Color) _ratingStyle(String? rating) {
  return switch (rating) {
    'buy' => ('شراء', Colors.green.shade700),
    'sell' => ('بيع', Colors.red.shade700),
    'neutral' => ('محايد', Colors.blueGrey),
    _ => (rating ?? '—', Colors.grey),
  };
}

String _fibStatusLabel(String? status) {
  return switch (status) {
    'testing' => 'اختبار',
    'approaching' => 'اقترب',
    'broken' => 'خارج النطاق',
    _ => status ?? '—',
  };
}

Color _fibStatusColor(String? status) {
  return switch (status) {
    'testing' => Colors.orange.shade700,
    'approaching' => Colors.blue.shade700,
    'broken' => Colors.red.shade700,
    _ => Colors.blueGrey,
  };
}

String _patternStatusLabel(String status) {
  if (status == 'complete') return 'مكتمل';
  if (status.isEmpty) return '—';
  return status;
}

Color? _signedColor(double? value) {
  if (value == null) return null;
  if (value > 0) return Colors.green.shade700;
  if (value < 0) return Colors.red.shade700;
  return null;
}

Color? _scoreColor(double? value) {
  if (value == null) return null;
  if (value >= 60) return Colors.green.shade700;
  if (value <= 40) return Colors.red.shade700;
  return Colors.orange.shade700;
}

String _formatNumber(double? value, {String suffix = ''}) {
  if (value == null) return '—';
  return '${value.toStringAsFixed(2)}$suffix';
}

String _formatSigned(double? value, {String suffix = ''}) {
  if (value == null) return '—';
  final sign = value > 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(2)}$suffix';
}

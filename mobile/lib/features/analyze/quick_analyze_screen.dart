import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/haptics.dart';
import '../../core/theme/terminal_theme.dart';
import '../../domain/models.dart';
import '../market/report_providers.dart';
import 'analyze_providers.dart';

/// شاشة التحليل السريع — قلب تجربة المتداول.
/// مصممة للوصول لتحليل سهم في أقل من 3 ثواني.
class QuickAnalyzeScreen extends ConsumerStatefulWidget {
  const QuickAnalyzeScreen({super.key});

  @override
  ConsumerState<QuickAnalyzeScreen> createState() => _QuickAnalyzeScreenState();
}

class _QuickAnalyzeScreenState extends ConsumerState<QuickAnalyzeScreen> {
  final _searchController = TextEditingController();
  final _focusNode = FocusNode();
  Timer? _debounce;
  List<MarketInstrument> _searchResults = [];
  bool _searching = false;
  String? _searchError;

  @override
  void initState() {
    super.initState();
    // التركيز التلقائي على حقل البحث عند فتح الشاشة
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _focusNode.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 250), () {
      _performSearch(query);
    });
  }

  Future<void> _performSearch(String query) async {
    final trimmed = query.trim();
    if (trimmed.length < 2) {
      setState(() {
        _searchResults = [];
        _searchError = null;
      });
      return;
    }

    setState(() {
      _searching = true;
      _searchError = null;
    });

    try {
      final repo = ref.read(backendRepositoryProvider);
      final instruments = await repo.searchInstruments(trimmed, limit: 8);
      if (!mounted) return;
      setState(() {
        _searchResults = instruments;
        _searching = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _searchError = 'تعذر البحث';
        _searching = false;
      });
    }
  }

  void _openAnalysis(String ticker) {
    TerminalHaptics.medium();
    context.push('/stocks/$ticker');
  }

  @override
  Widget build(BuildContext context) {
    final theme = TerminalTheme.of(context);
    final historyAsync = ref.watch(analysisHistoryProvider);
    final popular = ref.watch(popularTickersProvider);

    return Scaffold(
      backgroundColor: theme.bgBase,
      appBar: AppBar(
        backgroundColor: theme.bgBase,
        elevation: 0,
        leading: const SizedBox.shrink(),
        title: Row(
          children: [
            Icon(Icons.bolt_rounded, color: theme.signalGold, size: 24),
            const SizedBox(width: 10),
            Text(
              'تحليل سريع',
              style: theme.titleSmall.copyWith(
                color: theme.textPrimary,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        children: [
          // شريط البحث
          _SearchBar(
            controller: _searchController,
            focusNode: _focusNode,
            theme: theme,
            onChanged: _onSearchChanged,
            onSubmitted: (value) {
              if (value.trim().length >= 2) {
                _openAnalysis(value.trim().toUpperCase());
              }
            },
          ),
          const SizedBox(height: 16),

          // نتائج البحث
          if (_searching) const _SearchSkeleton(),
          if (_searchError != null)
            _ErrorMessage(message: _searchError!, theme: theme),
          if (_searchResults.isNotEmpty) ...[
            _SectionHeader(title: 'نتائج البحث', theme: theme),
            const SizedBox(height: 8),
            ..._searchResults.map(
              (instrument) => _InstrumentTile(
                instrument: instrument,
                theme: theme,
                onTap: () => _openAnalysis(instrument.ticker),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // التحليلات الأخيرة
          _SectionHeader(title: 'آخر التحليلات', theme: theme, action: 'عرض الكل'),
          const SizedBox(height: 8),
          historyAsync.when(
            data: (response) => response.items.isEmpty
                ? _EmptyHistory(theme: theme)
                : Column(
                    children: response.items
                        .map(
                          (item) => _RecentAnalysisTile(
                            item: item,
                            theme: theme,
                            onTap: () => _openAnalysis(item.ticker),
                          ),
                        )
                        .toList(),
                  ),
            loading: () => const _HistorySkeleton(),
            error: (_, __) => _ErrorMessage(
              message: 'تعذر تحميل السجل',
              theme: theme,
            ),
          ),
          const SizedBox(height: 16),

          // الأسهم الشائعة
          _SectionHeader(title: 'الأسهم الشائعة', theme: theme),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: popular
                .map(
                  (ticker) => _PopularTickerChip(
                    ticker: ticker,
                    theme: theme,
                    onTap: () => _openAnalysis(ticker),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

/// شريط البحث الرئيسي
class _SearchBar extends StatelessWidget {
  const _SearchBar({
    required this.controller,
    required this.focusNode,
    required this.theme,
    required this.onChanged,
    required this.onSubmitted,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final TerminalThemeData theme;
  final ValueChanged<String> onChanged;
  final ValueChanged<String> onSubmitted;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: theme.bgSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: theme.signalGold.withValues(alpha: 0.4), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: theme.signalGold.withValues(alpha: 0.1),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const SizedBox(width: 14),
          Icon(Icons.search_rounded, color: theme.signalGold, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              controller: controller,
              focusNode: focusNode,
              textCapitalization: TextCapitalization.characters,
              style: theme.monoMedium.copyWith(
                color: theme.textPrimary,
                fontWeight: FontWeight.w700,
              ),
              decoration: InputDecoration(
                hintText: 'ابحث عن سهم... (COMI, HRHO)',
                hintStyle: theme.monoSmall.copyWith(color: theme.textTertiary),
                border: InputBorder.none,
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(vertical: 16),
              ),
              onChanged: onChanged,
              onSubmitted: onSubmitted,
            ),
          ),
          if (controller.text.isNotEmpty)
            IconButton(
              onPressed: () {
                controller.clear();
                onChanged('');
              },
              icon: Icon(Icons.close_rounded, color: theme.textSecondary, size: 20),
              visualDensity: VisualDensity.compact,
            ),
          const SizedBox(width: 8),
        ],
      ),
    );
  }
}

/// بلاطة سهم من نتائج البحث
class _InstrumentTile extends StatelessWidget {
  const _InstrumentTile({
    required this.instrument,
    required this.theme,
    required this.onTap,
  });

  final MarketInstrument instrument;
  final TerminalThemeData theme;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: theme.bgSurface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: theme.border),
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: theme.signalGold.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Text(
                    instrument.ticker.substring(0, 1),
                    style: theme.monoMedium.copyWith(
                      color: theme.signalGold,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      instrument.ticker,
                      style: theme.monoMedium.copyWith(
                        color: theme.textPrimary,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    if (instrument.description.isNotEmpty)
                      Text(
                        instrument.description,
                        style: theme.monoTiny.copyWith(color: theme.textSecondary),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                  ],
                ),
              ),
              Icon(Icons.chevron_left, color: theme.textTertiary, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}

/// بلاطة تحليل سابق
class _RecentAnalysisTile extends StatelessWidget {
  const _RecentAnalysisTile({
    required this.item,
    required this.theme,
    required this.onTap,
  });

  final AnalysisHistoryItem item;
  final TerminalThemeData theme;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final (signalColor, signalLabel) = switch (item.signal.toUpperCase()) {
      'BUY' => (theme.bullGreen, 'شراء'),
      'AVOID' => (theme.bearRed, 'تجنب'),
      _ => (theme.textSecondary, 'مراقبة'),
    };

    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: theme.bgSurface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: theme.border),
          ),
          child: Row(
            children: [
              // رمز السهم
              Expanded(
                flex: 2,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.ticker,
                      style: theme.monoMedium.copyWith(
                        color: theme.textPrimary,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _formatTimeAgo(item.dataAsOf),
                      style: theme.monoTiny.copyWith(color: theme.textTertiary),
                    ),
                  ],
                ),
              ),
              // السعر
              if (item.priceAtAnalysis != null)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Text(
                    item.priceAtAnalysis!.toStringAsFixed(2),
                    style: theme.monoSmall.copyWith(
                      color: theme.textSecondary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              // الدرجة
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                decoration: BoxDecoration(
                  color: theme.signalGold.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  item.score.toStringAsFixed(0),
                  style: theme.monoSmall.copyWith(
                    color: theme.signalGold,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              // شارة الإشارة
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: signalColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: signalColor.withValues(alpha: 0.4)),
                ),
                child: Text(
                  signalLabel,
                  style: theme.monoTiny.copyWith(
                    color: signalColor,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.5,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatTimeAgo(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 1) return 'الآن';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} د';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} س';
    if (diff.inDays < 7) return 'منذ ${diff.inDays} ي';
    return '${time.day}/${time.month}';
  }
}

/// شريحة سهم شائع
class _PopularTickerChip extends StatelessWidget {
  const _PopularTickerChip({
    required this.ticker,
    required this.theme,
    required this.onTap,
  });

  final String ticker;
  final TerminalThemeData theme;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: theme.bgSurface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: theme.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.trending_up_rounded, color: theme.signalGold, size: 14),
            const SizedBox(width: 6),
            Text(
              ticker,
              style: theme.monoSmall.copyWith(
                color: theme.textPrimary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// عنوان قسم
class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.title,
    required this.theme,
    this.action,
  });

  final String title;
  final TerminalThemeData theme;
  final String? action;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            title,
            style: theme.monoSmall.copyWith(
              color: theme.textSecondary,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ),
        if (action != null)
          Text(
            action!,
            style: theme.monoTiny.copyWith(
              color: theme.signalGold,
              fontWeight: FontWeight.w700,
            ),
          ),
      ],
    );
  }
}

/// حالة فارغة لسجل التحليلات
class _EmptyHistory extends StatelessWidget {
  const _EmptyHistory({required this.theme});
  final TerminalThemeData theme;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: theme.bgSurface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: theme.border),
      ),
      child: Row(
        children: [
          Icon(Icons.history_rounded, color: theme.textTertiary, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'لا توجد تحليلات سابقة',
                  style: theme.monoSmall.copyWith(
                    color: theme.textPrimary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'ابدأ بتحليل أول سهم من القائمة أدناه',
                  style: theme.monoTiny.copyWith(color: theme.textSecondary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Skeleton loaders
class _SearchSkeleton extends StatelessWidget {
  const _SearchSkeleton();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        3,
        (_) => Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Container(
            height: 60,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.03),
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
      ),
    );
  }
}

class _HistorySkeleton extends StatelessWidget {
  const _HistorySkeleton();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        4,
        (_) => Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Container(
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.03),
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
      ),
    );
  }
}

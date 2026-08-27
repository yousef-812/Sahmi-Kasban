import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/network/api_exception.dart';
import '../../domain/models.dart';
import 'market_quotes_providers.dart';
import 'stock_quote_card.dart';

class StocksScreen extends ConsumerStatefulWidget {
  const StocksScreen({super.key});

  @override
  ConsumerState<StocksScreen> createState() => _StocksScreenState();
}

class _StocksScreenState extends ConsumerState<StocksScreen>
    with SingleTickerProviderStateMixin {
  String _query = '';
  String _selectedSector = 'الجميع';
  TabController? _tabController;
  int _currentTabIndex = 0;

  // Custom User Watchlists stored locally: { watchlistName: [ticker1, ticker2] }
  Map<String, List<String>> _userWatchlists = {'متابعة 1': []};

  final List<String> _sectors = const [
    'الجميع',
    'العقارات',
    'البنوك',
    'الخدمات المالية',
    'الأغذية والمشروبات',
    'الكيماويات',
    'موارد أساسية',
    'الرعاية الصحية',
    'الاتصالات والتكنولوجيا',
    'مغاسل وغزل ونسيج',
    'مواد البناء',
  ];

  @override
  void initState() {
    super.initState();
    _loadState();
  }

  Future<void> _loadState() async {
    final prefs = await SharedPreferences.getInstance();
    final savedTab = prefs.getInt('last_home_tab_index') ?? 0;
    final rawWatchlists = prefs.getString('user_watchlists_data');

    if (rawWatchlists != null) {
      try {
        final decoded = Map<String, dynamic>.from(
          jsonDecode(rawWatchlists) as Map,
        );
        _userWatchlists = decoded.map(
          (k, v) => MapEntry(k, (v as List).map((e) => e.toString()).toList()),
        );
        if (_userWatchlists.isEmpty) {
          _userWatchlists = {'متابعة 1': []};
        }
      } catch (_) {}
    }

    _initTabController(initialIndex: savedTab);
  }

  void _initTabController({int initialIndex = 0}) {
    final totalTabs =
        2 + _userWatchlists.length; // 0: All, 1: Sectors, 2+: Custom Watchlists
    final targetIndex = initialIndex < totalTabs ? initialIndex : 0;

    _tabController?.dispose();
    _tabController = TabController(
      length: totalTabs,
      vsync: this,
      initialIndex: targetIndex,
    );
    _currentTabIndex = targetIndex;

    _tabController!.addListener(() {
      if (_tabController!.indexIsChanging ||
          _tabController!.index != _currentTabIndex) {
        setState(() {
          _currentTabIndex = _tabController!.index;
        });
        _saveTabPreference(_tabController!.index);
      }
    });

    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _saveState() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_watchlists_data', jsonEncode(_userWatchlists));
  }

  Future<void> _saveTabPreference(int index) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('last_home_tab_index', index);
  }

  void _createWatchlist() {
    final textController = TextEditingController();
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('إنشاء قائمة متابعة جديدة'),
        content: TextField(
          controller: textController,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'مثال: قائمة التداول اليومي',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () {
              final name = textController.text.trim();
              if (name.isNotEmpty && !_userWatchlists.containsKey(name)) {
                setState(() {
                  _userWatchlists[name] = [];
                });
                _saveState();
                _initTabController(initialIndex: 1 + _userWatchlists.length);
              }
              Navigator.of(ctx).pop();
            },
            child: const Text('إنشاء'),
          ),
        ],
      ),
    );
  }

  void _addStockToWatchlist(String watchlistName, String ticker) {
    if (_userWatchlists.containsKey(watchlistName)) {
      if (!_userWatchlists[watchlistName]!.contains(ticker)) {
        setState(() {
          _userWatchlists[watchlistName]!.add(ticker);
        });
        _saveState();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم إضافة $ticker إلى قائمة "$watchlistName"'),
            duration: const Duration(seconds: 2),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'السهم $ticker موجود بالفعل في قائمة "$watchlistName"',
            ),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  void _showAddStockPicker(String watchlistName, List<MarketQuote> allQuotes) {
    String search = '';
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) {
          final filtered = allQuotes.where((q) {
            if (search.isEmpty) return true;
            return q.ticker.contains(search.toUpperCase()) ||
                q.description.contains(search);
          }).toList();

          return Container(
            height: MediaQuery.of(ctx).size.height * 0.7,
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text(
                  'إضافة سهم لقائمة "$watchlistName"',
                  style: Theme.of(ctx).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search),
                    hintText: 'بحث برمز السهم أو الاسم...',
                    isDense: true,
                  ),
                  onChanged: (val) => setModalState(() => search = val.trim()),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: ListView.separated(
                    itemCount: filtered.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (ctx, index) {
                      final item = filtered[index];
                      final isAdded =
                          _userWatchlists[watchlistName]?.contains(
                            item.ticker,
                          ) ??
                          false;
                      return ListTile(
                        title: Text(
                          item.ticker,
                          textDirection: TextDirection.ltr,
                        ),
                        subtitle: Text(item.description),
                        trailing: Icon(
                          isAdded
                              ? Icons.check_circle_rounded
                              : Icons.add_circle_outline_rounded,
                          color: isAdded
                              ? Colors.green
                              : Theme.of(ctx).colorScheme.primary,
                        ),
                        onTap: () {
                          _addStockToWatchlist(watchlistName, item.ticker);
                          setModalState(() {});
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _showLongPressBottomSheet(MarketQuote quote) {
    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    'إضافة ${quote.ticker} إلى قوائم المتابعة',
                    style: Theme.of(ctx).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(ctx).pop(),
                  ),
                ],
              ),
              const Divider(),
              if (_userWatchlists.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(12),
                  child: Text(
                    'لا توجد قوائم متابعة حالية. اضغط + لإضافة قائمة.',
                  ),
                )
              else
                ..._userWatchlists.keys.map((name) {
                  final inList =
                      _userWatchlists[name]?.contains(quote.ticker) ?? false;
                  return ListTile(
                    leading: Icon(
                      inList
                          ? Icons.bookmark_added_rounded
                          : Icons.bookmark_add_outlined,
                      color: inList
                          ? Colors.green
                          : Theme.of(ctx).colorScheme.primary,
                    ),
                    title: Text(name),
                    trailing: inList
                        ? const Text(
                            'مضاف',
                            style: TextStyle(
                              color: Colors.green,
                              fontWeight: FontWeight.bold,
                            ),
                          )
                        : const Text(
                            '+ إضافة',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                    onTap: () {
                      Navigator.of(ctx).pop();
                      _addStockToWatchlist(name, quote.ticker);
                    },
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final snapshot = ref.watch(marketQuotesProvider).valueOrNull;
    final allQuotes = snapshot?.items ?? [];

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(marketQuotesProvider);
        await ref.read(marketQuotesProvider.future);
      },
      child: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: TextField(
              textDirection: TextDirection.ltr,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search_rounded),
                hintText: 'بحث برمز السهم أو الاسم — COMI',
                isDense: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(14)),
                ),
              ),
              onChanged: (value) =>
                  setState(() => _query = value.trim().toUpperCase()),
            ),
          ),

          // Tab Bar with Add List Button
          if (_tabController != null)
            Row(
              children: [
                Expanded(
                  child: TabBar(
                    controller: _tabController,
                    isScrollable: true,
                    tabAlignment: TabAlignment.start,
                    tabs: [
                      const Tab(text: 'كل الأسهم'),
                      const Tab(text: 'القطاعات'),
                      ..._userWatchlists.keys.map((name) => Tab(text: name)),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add_rounded),
                  tooltip: 'إضافة قائمة متابعة',
                  onPressed: _createWatchlist,
                ),
              ],
            ),

          Expanded(
            child: ref
                .watch(marketQuotesProvider)
                .when(
                  loading: () =>
                      const Center(child: CircularProgressIndicator()),
                  error: (error, stack) => _ErrorView(
                    error: error,
                    onRetry: () => ref.invalidate(marketQuotesProvider),
                  ),
                  data: (_) => _buildActiveTabContent(allQuotes),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildActiveTabContent(List<MarketQuote> allQuotes) {
    if (_currentTabIndex == 0) {
      // Tab 0: All stocks
      final items = _filterQuotes(allQuotes);
      return _buildGrid(items);
    } else if (_currentTabIndex == 1) {
      // Tab 1: Sectors filter
      final items = _filterQuotes(allQuotes);
      return Column(
        children: [
          Container(
            height: 48,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _sectors.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (ctx, idx) {
                final sec = _sectors[idx];
                final isSelected = sec == _selectedSector;
                return ChoiceChip(
                  label: Text(sec),
                  selected: isSelected,
                  onSelected: (val) {
                    if (val) setState(() => _selectedSector = sec);
                  },
                );
              },
            ),
          ),
          Expanded(child: _buildGrid(items)),
        ],
      );
    } else {
      // Tab 2+: User custom watchlists
      final listIndex = _currentTabIndex - 2;
      final watchlistNames = _userWatchlists.keys.toList();
      if (listIndex < 0 || listIndex >= watchlistNames.length) {
        return _buildGrid([]);
      }

      final currentListName = watchlistNames[listIndex];
      final targetTickers = _userWatchlists[currentListName] ?? [];
      final listQuotes = allQuotes
          .where((q) => targetTickers.contains(q.ticker))
          .toList();

      final filtered = _filterQuotes(listQuotes);

      return Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                Text(
                  'عدد الأسهم: ${filtered.length}',
                  style: Theme.of(
                    context,
                  ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: () =>
                      _showAddStockPicker(currentListName, allQuotes),
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('إضافة سهم'),
                ),
              ],
            ),
          ),
          Expanded(child: _buildGrid(filtered)),
        ],
      );
    }
  }

  static final Map<String, List<String>> _sectorStockMap = {
    'العقارات': [
      'TMGH',
      'PHDC',
      'HELI',
      'EMFD',
      'SODI',
      'ORHD',
      'EGTS',
      'OCDI',
      'RREI',
      'EHDR',
      'ACAP',
      'AREH',
      'ARAB',
      'CCRS',
      'DAPH',
      'IDRE',
      'KORA',
      'MAAL',
      'MASR',
      'MOED',
      'NARE',
      'ODIN',
      'ROTO',
      'UEGC',
      'UNIT',
      'UPMS',
      'UTOP',
    ],
    'البنوك': [
      'COMI',
      'ADIB',
      'HDBK',
      'CIEB',
      'QNBE',
      'EGBE',
      'EXPA',
      'SAIB',
      'NBKE',
      'CANA',
      'CBKD',
      'FAIT',
      'FAITA',
    ],
    'الخدمات المالية': [
      'HRHO',
      'FWRY',
      'CCAP',
      'RAYA',
      'BTFH',
      'CICH',
      'BINV',
      'CNFN',
      'EFIH',
      'VALU',
      'AIFI',
      'AIH',
      'BONY',
      'CFGH',
      'GDWA',
      'GIHD',
      'GRCA',
      'OFH',
      'OIH',
      'PIOH',
      'PRMH',
      'RKAZ',
      'SDTI',
      'TYCN',
    ],
    'الأغذية والمشروبات': [
      'JUFO',
      'OLFI',
      'EAST',
      'DOMT',
      'GOUR',
      'SUGR',
      'EFID',
      'ISMA',
      'POUL',
      'AJWA',
      'AFDI',
      'AFMC',
      'AMER',
      'BIDI',
      'COSG',
      'DTPP',
      'EASB',
      'EBSC',
      'EGWA',
      'INFI',
      'ISMQ',
      'LKGP',
      'MBEG',
      'MILS',
      'MITR',
      'MPCO',
      'NEDA',
      'SNFC',
      'UEFM',
      'WATP',
    ],
    'الكيماويات': [
      'KIMA',
      'MFPC',
      'ABUK',
      'SKPC',
      'AMOC',
      'SIDM',
      'EFIC',
      'PACH',
      'AALR',
      'ACAMD',
      'BIOC',
      'CPCI',
      'EGCH',
      'ICID',
      'MICH',
      'MPCI',
      'NCGC',
      'NFCI',
      'NIPH',
      'SIPC',
      'SMFR',
      'ZEOT',
    ],
    'موارد أساسية': [
      'EGAL',
      'ESRS',
      'IRON',
      'ALUM',
      'SPMD',
      'ASCM',
      'ANCC',
      'ARCC',
      'DCRC',
      'IRAX',
      'LCSW',
      'MCQE',
      'SCEM',
      'SCFM',
      'SINA',
      'SVCE',
    ],
    'الرعاية الصحية': [
      'CLHO',
      'PHAR',
      'RMDA',
      'ISPH',
      'EITP',
      'ADCI',
      'AXPH',
      'CEFM',
      'CERA',
      'CID',
      'EPCO',
      'FCMD',
      'MCRO',
      'MEPA',
      'MIPH',
      'OBRI',
      'OCPH',
      'SPHT',
    ],
    'الاتصالات والتكنولوجيا': [
      'ETEL',
      'ORAS',
      'SWDY',
      'GTWL',
      'ELEC',
      'AIDC',
      'ENGC',
      'FTNS',
      'HAEX',
      'HAVC',
      'HBCO',
      'ICFC',
      'IEEC',
      'INEG',
      'MOIL',
      'NAHO',
      'NCCW',
      'TAQA',
    ],
    'مغاسل وغزل ونسيج': [
      'ORWE',
      'KABO',
      'UNIP',
      'SPIN',
      'GTEX',
      'ACFR',
      'ACGC',
      'AMIA',
      'AMII',
      'AMPI',
      'APSW',
      'DCCC',
      'EEII',
      'ELKA',
      'ELNA',
      'ELWA',
      'EPPK',
      'ETRS',
      'FIRE',
      'FNAR',
      'GGCC',
      'GGRN',
      'GPIM',
      'GPPL',
      'GSSC',
      'GTHE',
      'HDST',
      'IBCT',
      'ICLE',
      'IFAP',
      'KWIN',
      'KZPC',
      'LUTS',
      'MBSC',
      'MENA',
      'MFSC',
      'MHOT',
      'MISR',
      'MKIT',
      'MLIC',
      'MMAT',
      'MMHC',
      'MOIN',
      'MOSC',
      'MPRC',
      'NHPS',
      'NINH',
      'NMIN',
      'OCAP',
      'PHTV',
      'PMSC',
      'POCO',
      'PRCL',
      'PRDC',
      'RACC',
      'RAKT',
      'RMTV',
      'RUBX',
      'SACE',
      'SAUD',
      'SCTS',
      'SEIG',
      'SIEG',
      'SMPP',
      'SNFI',
      'TALM',
      'TANM',
      'TORA',
      'TRTO',
      'TWSA',
      'UBEE',
      'VERT',
      'VLMR',
      'VLMRA',
      'WCDF',
      'WKOL',
      'YAYT',
      'ZMID',
    ],
    'مواد البناء': [
      'ARCC',
      'SCEM',
      'MCQE',
      'TORA',
      'PRCL',
      'ALUM',
      'EALR',
      'ECAP',
      'EDFM',
      'EEP',
      'EFAC',
      'EGAS',
      'EGOTH',
      'EGREF',
      'ELAB',
      'ENPI',
      'EOSB',
      'EXPA',
      'GEOS',
    ],
  };

  bool _matchSector(MarketQuote quote, String selectedSector) {
    if (selectedSector == 'الجميع') return true;

    // 1. Check curated ticker map
    final list = _sectorStockMap[selectedSector];
    if (list != null && list.contains(quote.ticker)) {
      return true;
    }

    // 2. Check quote.sector if present
    if (quote.sector != null && quote.sector!.isNotEmpty) {
      if (quote.sector!.contains(selectedSector) ||
          selectedSector.contains(quote.sector!)) {
        return true;
      }
    }

    // 3. Keyword fallbacks in ticker or description
    final desc = '${quote.ticker} ${quote.description}';
    switch (selectedSector) {
      case 'العقارات':
        return desc.contains('عقار') ||
            desc.contains('إسكان') ||
            desc.contains('تعمير') ||
            desc.contains('تنمية') ||
            desc.contains('أراضي') ||
            desc.contains('مصطفى') ||
            desc.contains('هيلز');
      case 'البنوك':
        return desc.contains('بنك') ||
            desc.contains('مصرف') ||
            desc.contains('تجاري دولي') ||
            desc.contains('أبوظبي') ||
            desc.contains('كريدي');
      case 'الخدمات المالية':
        return desc.contains('مالية') ||
            desc.contains('استثمار') ||
            desc.contains('فوري') ||
            desc.contains('هيرميس') ||
            desc.contains('القلعة') ||
            desc.contains('راية') ||
            desc.contains('بلتون');
      case 'الأغذية والمشروبات':
        return desc.contains('أغذية') ||
            desc.contains('مشروب') ||
            desc.contains('جهينة') ||
            desc.contains('لاند') ||
            desc.contains('دومتي') ||
            desc.contains('دخان') ||
            desc.contains('مطاحن') ||
            desc.contains('دواجن') ||
            desc.contains('سكر');
      case 'الكيماويات':
        return desc.contains('كيماو') ||
            desc.contains('كيما') ||
            desc.contains('موبكو') ||
            desc.contains('أسمدة') ||
            desc.contains('بتروكيماويات') ||
            desc.contains('زيوت');
      case 'موارد أساسية':
        return desc.contains('حديد') ||
            desc.contains('صلب') ||
            desc.contains('ألومنيوم') ||
            desc.contains('معادن') ||
            desc.contains('مناجم');
      case 'الرعاية الصحية':
        return desc.contains('أدوية') ||
            desc.contains('صيدل') ||
            desc.contains('مستشفى') ||
            desc.contains('رعاية') ||
            desc.contains('طبي');
      case 'الاتصالات والتكنولوجيا':
        return desc.contains('اتصالا') ||
            desc.contains('كهربا') ||
            desc.contains('شبكات') ||
            desc.contains('تكنولوجيا') ||
            desc.contains('سويدي');
      case 'مغاسل وغزل ونسيج':
        return desc.contains('غزل') ||
            desc.contains('نسيج') ||
            desc.contains('سجاد') ||
            desc.contains('ملابس') ||
            desc.contains('نساجون') ||
            desc.contains('دايس');
      case 'مواد البناء':
        return desc.contains('أسمنت') ||
            desc.contains('سيراميك') ||
            desc.contains('بناء') ||
            desc.contains('حراريات') ||
            desc.contains('بورسلين');
      default:
        return desc.contains(selectedSector);
    }
  }

  List<MarketQuote> _filterQuotes(List<MarketQuote> quotes) {
    return quotes.where((quote) {
      if (_query.isNotEmpty) {
        final match =
            quote.ticker.contains(_query) || quote.description.contains(_query);
        if (!match) return false;
      }
      if (_currentTabIndex == 1 && _selectedSector != 'الجميع') {
        if (!_matchSector(quote, _selectedSector)) return false;
      }
      return true;
    }).toList();
  }

  Widget _buildGrid(List<MarketQuote> items) {
    if (items.isEmpty) {
      return ListView(
        padding: const EdgeInsets.all(24),
        children: const [
          Icon(Icons.search_off_rounded, size: 48),
          SizedBox(height: 12),
          Text('لا توجد أسهم في هذه القائمة.', textAlign: TextAlign.center),
        ],
      );
    }
    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 220,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.92,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final quote = items[index];
        return StockQuoteCard(
          quote: quote,
          onTap: () => context.push('/stocks/${quote.ticker}'),
          onLongPress: () => _showLongPressBottomSheet(quote),
        );
      },
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});

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
                  : 'تعذر تحميل أسعار السوق.',
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

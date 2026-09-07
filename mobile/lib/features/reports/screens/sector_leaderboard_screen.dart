import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_exception.dart';
import '../../auth/session_controller.dart';

class SectorItem {
  const SectorItem({
    required this.ticker,
    required this.companyName,
    required this.rank,
    required this.score,
    required this.entryPrice,
    required this.targetPrice,
    required this.stopLoss,
    required this.volumeZscore,
    required this.atr,
    required this.signal,
  });

  final String ticker;
  final String companyName;
  final int rank;
  final int score;
  final double entryPrice;
  final double targetPrice;
  final double stopLoss;
  final double volumeZscore;
  final double atr;
  final String signal;

  factory SectorItem.fromJson(Map<String, dynamic> json) {
    return SectorItem(
      ticker: json['ticker'] as String,
      companyName: json['company_name'] as String,
      rank: (json['rank'] as num).toInt(),
      score: (json['score'] as num).toInt(),
      entryPrice: (json['entry_price'] as num).toDouble(),
      targetPrice: (json['target_price'] as num).toDouble(),
      stopLoss: (json['stop_loss'] as num).toDouble(),
      volumeZscore: (json['volume_zscore'] as num).toDouble(),
      atr: (json['atr'] as num).toDouble(),
      signal: json['signal'] as String,
    );
  }
}

class SectorLeaderboardScreen extends ConsumerStatefulWidget {
  const SectorLeaderboardScreen({super.key});

  static Route<void> route() {
    return MaterialPageRoute<void>(
      builder: (_) => const SectorLeaderboardScreen(),
    );
  }

  @override
  ConsumerState<SectorLeaderboardScreen> createState() =>
      _SectorLeaderboardScreenState();
}

class _SectorLeaderboardScreenState
    extends ConsumerState<SectorLeaderboardScreen> {
  String _selectedSector = 'banking';
  bool _isLoading = false;
  List<SectorItem> _items = [];
  String _sectorName = 'قطاع البنوك';

  final Map<String, String> _sectorMap = {
    'banking': 'قطاع البنوك',
    'real_estate': 'قطاع العقارات والأراضي',
    'technology': 'قطاع التكنولوجيا والاتصالات',
    'financial_services': 'قطاع الخدمات المالية والسيولة',
  };

  @override
  void initState() {
    super.initState();
    _fetchReport();
  }

  Future<void> _fetchReport() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.dio.get<Map<String, dynamic>>(
        '/reports/sectors/$_selectedSector/leaderboard',
      );

      final data = response.data?['data'] as Map<String, dynamic>? ?? response.data ?? {};
      final list = (data['items'] as List<dynamic>? ?? [])
          .map((e) => SectorItem.fromJson(e as Map<String, dynamic>))
          .toList();

      await ref.read(sessionControllerProvider.notifier).refreshProfile();

      if (mounted) {
        setState(() {
          _items = list;
          _sectorName = data['sector_name'] as String? ?? _sectorMap[_selectedSector]!;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('حدث خطأ: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final userCoins = ref.watch(sessionControllerProvider).profile?.balanceCoins ?? '0';

    return Scaffold(
      appBar: AppBar(
        title: const Text('تقرير ترقية ومقارنة القطاعات'),
        centerTitle: true,
        actions: [
          Container(
            margin: const EdgeInsets.only(left: 12),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.monetization_on, size: 16, color: Colors.amber),
                const SizedBox(width: 4),
                Text(
                  '$userCoins عملة',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Sector Dropdown Selector & Cost Badge
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'اختر القطاع للتحليل:',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Chip(
                            avatar: const Icon(Icons.stars, size: 14, color: Colors.amber),
                            label: const Text('2.0 عملة / تقرير'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        initialValue: _selectedSector,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        ),
                        items: _sectorMap.entries.map((entry) {
                          return DropdownMenuItem<String>(
                            value: entry.key,
                            child: Text(entry.value),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null && val != _selectedSector) {
                            setState(() {
                              _selectedSector = val;
                            });
                            _fetchReport();
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              if (_isLoading)
                const Padding(
                  padding: EdgeInsets.all(32),
                  child: Center(child: CircularProgressIndicator()),
                )
              else ...[
                // Sector Leader Spotlight Card
                if (_items.isNotEmpty) ...[
                  Card(
                    color: theme.colorScheme.primaryContainer,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.workspace_premium, color: Colors.amber, size: 28),
                              const SizedBox(width: 8),
                              Text(
                                'السهم القائد لقطاع $_sectorName',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: theme.colorScheme.onPrimaryContainer,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _items[0].ticker,
                            style: TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.w900,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                          Text(
                            _items[0].companyName,
                            style: const TextStyle(fontSize: 14, color: Colors.grey),
                          ),
                          const SizedBox(height: 12),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.green,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              'إشارة التحليل: ${_items[0].signal} | تقييم الجودة: ${_items[0].score}/100',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                ],

                // Leaderboard Table Section Header
                Text(
                  'ترتيب أسهم القطاع والمخاطرة',
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 10),

                // Leaderboard List
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = _items[index];
                    return Card(
                      elevation: 1,
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          children: [
                            Row(
                              children: [
                                CircleAvatar(
                                  radius: 14,
                                  backgroundColor: index == 0
                                      ? Colors.amber
                                      : theme.colorScheme.primaryContainer,
                                  child: Text(
                                    '#${item.rank}',
                                    style: const TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        '${item.ticker} - ${item.companyName}',
                                        style: const TextStyle(fontWeight: FontWeight.bold),
                                      ),
                                      Text(
                                        'سعر الدخول: ${item.entryPrice} ج.م | المستهدف: ${item.targetPrice} ج.م',
                                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                                      ),
                                    ],
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: theme.colorScheme.surfaceContainerHighest,
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    item.signal,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const Divider(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _SubMetric(label: 'وقف الخسارة', value: '${item.stopLoss}'),
                                _SubMetric(label: 'زخم السيولة (Z)', value: '${item.volumeZscore}'),
                                _SubMetric(label: 'مذبذبات المخاطرة (ATR)', value: '${item.atr}'),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _SubMetric extends StatelessWidget {
  const _SubMetric({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 10, color: Colors.grey),
        ),
      ],
    );
  }
}

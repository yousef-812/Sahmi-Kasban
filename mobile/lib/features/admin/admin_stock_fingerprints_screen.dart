import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_models.dart';
import 'admin_providers.dart';
import 'admin_repository.dart';

class AdminStockFingerprintsScreen extends ConsumerStatefulWidget {
  const AdminStockFingerprintsScreen({super.key});

  @override
  ConsumerState<AdminStockFingerprintsScreen> createState() =>
      _AdminStockFingerprintsScreenState();
}

class _AdminStockFingerprintsScreenState
    extends ConsumerState<AdminStockFingerprintsScreen> {
  bool _isRebuilding = false;
  bool _isDownloading = false;
  final _tickerController = TextEditingController();

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  Future<void> _handleRebuild({String? ticker}) async {
    setState(() => _isRebuilding = true);
    try {
      await ref
          .read(adminRepositoryProvider)
          .rebuildStockFingerprints(ticker: ticker);
      ref.invalidate(adminStockFingerprintsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              ticker != null && ticker.isNotEmpty
                  ? 'تم تحديث بصمة السهم $ticker بنجاح'
                  : 'تمت إعادة بناء البصمات الخوارزمية لجميع الأسهم بنجاح',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('حدث خطأ أثناء التحديث: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isRebuilding = false);
    }
  }

  Future<void> _handleDownloadExcel() async {
    setState(() => _isDownloading = true);
    try {
      final bytes = await ref
          .read(adminRepositoryProvider)
          .downloadStockFingerprintsExcel();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'تم إنشاء وتحميل ملف التقرير بنجاح (${bytes.length} بايت)',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('حدث خطأ أثناء تنزيل الملف: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isDownloading = false);
    }
  }

  void _showRebuildDialog() {
    _tickerController.clear();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('تحديث البصمة الخوارزمية'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'أدخل رمز السهم لتحديث بصمته خصيصاً عبر الـ AI Critic، أو اترك الحقل فارغاً لتحديث كل الأسهم.',
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _tickerController,
              decoration: const InputDecoration(
                labelText: 'رمز السهم (اختياري، مثل COMI)',
                border: OutlineInputBorder(),
              ),
              textCapitalization: TextCapitalization.characters,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              final ticker = _tickerController.text.trim();
              Navigator.of(ctx).pop();
              _handleRebuild(ticker: ticker.isNotEmpty ? ticker : null);
            },
            child: const Text('تحديث الان'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final fingerprintsAsync = ref.watch(adminStockFingerprintsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('إدارة البصمات الخوارزمية'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(adminStockFingerprintsProvider),
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isRebuilding ? null : _showRebuildDialog,
                    icon: _isRebuilding
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.auto_mode),
                    label: const Text('تحديث البصمة الخوارزمية'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isDownloading ? null : _handleDownloadExcel,
                    icon: _isDownloading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.file_download),
                    label: const Text('تنزيل ملف Excel'),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: fingerprintsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('خطأ: $err')),
              data: (items) {
                if (items.isEmpty) {
                  return const Center(
                    child: Text(
                      'لا توجد بصمات خوارزمية مسجلة حتى الآن. اضغط زر التحديث لإنشائها.',
                    ),
                  );
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (ctx, index) {
                    final item = items[index];
                    return _buildFingerprintCard(item);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFingerprintCard(StockFingerprintItem item) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  item.ticker,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Chip(
                  avatar: Icon(
                    item.approvedByCritic ? Icons.check_circle : Icons.warning,
                    size: 16,
                    color: item.approvedByCritic ? Colors.green : Colors.orange,
                  ),
                  label: Text(
                    item.approvedByCritic
                        ? 'مقبول AI (${item.criticConfidence.toInt()}%)'
                        : 'غير مؤكد',
                  ),
                ),
              ],
            ),
            const Divider(),
            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    'الدرجة الكلية',
                    '${item.overallQualityScore}',
                  ),
                ),
                Expanded(
                  child: _buildMetricTile(
                    'الدورة الزمنية',
                    '${item.dominantCycleSessions} جلسة (${item.cycleStabilityScore.toInt()}%)',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    'عمق الاكتساح',
                    '${item.avgSweepDepthPct}%',
                  ),
                ),
                Expanded(
                  child: _buildMetricTile(
                    'احتمال الارتداد',
                    '${item.bounceProbabilityPct}%',
                  ),
                ),
              ],
            ),
            if (item.criticSummary.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                'تقييم الـ AI: ${item.criticSummary}',
                style: TextStyle(
                  fontSize: 13,
                  color: Theme.of(context).colorScheme.outline,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTile(String title, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}

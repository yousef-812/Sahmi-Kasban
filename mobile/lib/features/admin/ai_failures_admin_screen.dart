import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import '../../core/network/api_exception.dart';

class AiFailuresAdminScreen extends ConsumerStatefulWidget {
  const AiFailuresAdminScreen({super.key});

  static Route<void> route() {
    return MaterialPageRoute<void>(
      builder: (_) => const AiFailuresAdminScreen(),
    );
  }

  @override
  ConsumerState<AiFailuresAdminScreen> createState() =>
      _AiFailuresAdminScreenState();
}

class _AiFailuresAdminScreenState extends ConsumerState<AiFailuresAdminScreen> {
  List<Map<String, dynamic>> _failures = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchFailures();
  }

  Future<void> _fetchFailures() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.dio.get<List<dynamic>>(
        '/admin/ai-failures',
      );

      final list = (response.data ?? [])
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();

      if (mounted) {
        setState(() {
          _failures = list;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() => _error = e.message);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = e.toString());
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _clearCooldown(String userId, String userName) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إلغاء حظر المساعد الذكي'),
        content: Text(
          'هل أنت تأكد من إلغاء الحظر الإجباري مؤقتاً عن المستخدم ($userName)؟',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('تأكيد الإلغاء'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.post<Map<String, dynamic>>(
        '/admin/ai-failures/users/$userId/clear-cooldown',
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم إلغاء حظر المساعد الذكي عن ($userName) بنجاح.'),
            backgroundColor: Colors.green,
          ),
        );
      }
      _fetchFailures();
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
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('سجل أعطال المساعد الذكي (AI Failures)'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _fetchFailures,
            tooltip: 'تحديث',
          ),
        ],
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          _error!,
                          style: TextStyle(color: theme.colorScheme.error),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(
                          onPressed: _fetchFailures,
                          icon: const Icon(Icons.refresh_rounded),
                          label: const Text('إعادة المحاولة'),
                        ),
                      ],
                    ),
                  )
                : _failures.isEmpty
                    ? const Center(
                        child: Text('لا توجد سجلات أعطال للمساعد الذكي حالياً.'),
                      )
                    : RefreshIndicator(
                        onRefresh: _fetchFailures,
                        child: ListView.separated(
                          padding: const EdgeInsets.all(16),
                          itemCount: _failures.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 12),
                          itemBuilder: (context, index) {
                            final item = _failures[index];
                            final userId = item['user_id'] as String?;
                            final userName = item['user_name'] as String? ?? 'مستخدم';
                            final userEmail = item['user_email'] as String? ?? '';
                            final ticker = item['ticker'] as String?;
                            final question = item['question'] as String? ?? '';
                            final errorMsg = item['error_message'] as String? ?? '';
                            final traceback = item['error_traceback'] as String?;
                            final createdAt = item['created_at'] as String? ?? '';

                            return Card(
                              elevation: 2,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(14),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                userName,
                                                style: const TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 14,
                                                ),
                                              ),
                                              Text(
                                                userEmail,
                                                style: const TextStyle(
                                                  fontSize: 11,
                                                  color: Colors.grey,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                        if (ticker != null && ticker.isNotEmpty)
                                          Chip(
                                            label: Text(ticker),
                                            padding: EdgeInsets.zero,
                                          ),
                                      ],
                                    ),
                                    const Divider(height: 16),
                                    const Text(
                                      'السؤال الموجه:',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.grey,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      question,
                                      style: const TextStyle(fontSize: 13),
                                    ),
                                    const SizedBox(height: 8),
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: Colors.red.withValues(alpha: 0.1),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Row(
                                        children: [
                                          const Icon(
                                            Icons.error_outline_rounded,
                                            color: Colors.red,
                                            size: 18,
                                          ),
                                          const SizedBox(width: 8),
                                          Expanded(
                                            child: Text(
                                              errorMsg,
                                              style: const TextStyle(
                                                color: Colors.red,
                                                fontSize: 12,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    if (traceback != null && traceback.isNotEmpty) ...[
                                      const SizedBox(height: 6),
                                      ExpansionTile(
                                        dense: true,
                                        title: const Text(
                                          'تفاصيل الخطأ (Traceback)',
                                          style: TextStyle(fontSize: 11),
                                        ),
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.all(8),
                                            color: Colors.black12,
                                            width: double.infinity,
                                            child: Text(
                                              traceback,
                                              style: const TextStyle(
                                                fontFamily: 'monospace',
                                                fontSize: 10,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                    const SizedBox(height: 8),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          createdAt.substring(0, 16).replaceAll('T', ' '),
                                          style: const TextStyle(
                                            fontSize: 10,
                                            color: Colors.grey,
                                          ),
                                        ),
                                        if (userId != null)
                                          FilledButton.tonal(
                                            onPressed: () => _clearCooldown(
                                              userId,
                                              userName,
                                            ),
                                            child: const Text(
                                              'إلغاء حظر المساعد',
                                              style: TextStyle(fontSize: 12),
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
      ),
    );
  }
}

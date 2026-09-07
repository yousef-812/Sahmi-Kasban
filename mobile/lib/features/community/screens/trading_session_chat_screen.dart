import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_exception.dart';
import '../../auth/session_controller.dart';

class TradingSessionChatScreen extends ConsumerStatefulWidget {
  const TradingSessionChatScreen({super.key});

  static Route<void> route() {
    return MaterialPageRoute<void>(
      builder: (_) => const TradingSessionChatScreen(),
    );
  }

  @override
  ConsumerState<TradingSessionChatScreen> createState() =>
      _TradingSessionChatScreenState();
}

class _TradingSessionChatScreenState
    extends ConsumerState<TradingSessionChatScreen> {
  bool _isLoading = false;
  bool _isVoting = false;
  bool _isSending = false;

  int _votesCount = 0;
  int _votesTarget = 40;
  bool _isUnlocked = false;
  bool _isSessionOpen = false;
  bool _hasVoted = false;

  List<Map<String, dynamic>> _messages = [];
  final TextEditingController _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchStatus();
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _fetchStatus() async {
    setState(() => _isLoading = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.dio.get<Map<String, dynamic>>(
        '/trading-chat/status',
      );
      final data = response.data?['data'] as Map<String, dynamic>? ?? response.data ?? {};

      if (mounted) {
        setState(() {
          _votesCount = (data['votes_count'] as num?)?.toInt() ?? 0;
          _votesTarget = (data['votes_target'] as num?)?.toInt() ?? 40;
          _isUnlocked = data['is_unlocked'] as bool? ?? false;
          _isSessionOpen = data['is_session_open'] as bool? ?? false;
          _hasVoted = data['has_voted'] as bool? ?? false;
        });
      }

      if (_isUnlocked) {
        await _fetchMessages();
      }
    } catch (e) {
      // Ignore network status fetch error initially
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _fetchMessages() async {
    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.dio.get<List<dynamic>>(
        '/trading-chat/messages',
      );
      final list = (response.data ?? [])
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();

      if (mounted) {
        setState(() {
          _messages = list;
        });
      }
    } catch (e) {
      // Ignore
    }
  }

  Future<void> _vote() async {
    if (_isVoting || _hasVoted) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('التصويت لفتح الغرفة'),
        content: const Text(
          'تكلفة التصويت 0.5 عملة. إذا لم تصل الغرفة إلى 40 صوتًا قبل الساعة 3:00 مساءً، سيتم استرداد العملات تلقائيًا.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('تأكيد التصويت — 0.5 عملة'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    setState(() => _isVoting = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.post<Map<String, dynamic>>('/trading-chat/vote');

      await ref.read(sessionControllerProvider.notifier).refreshProfile();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم تصويتك بنجاح!')),
        );
      }
      await _fetchStatus();
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
        setState(() => _isVoting = false);
      }
    }
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty || _isSending) return;

    setState(() => _isSending = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.post<Map<String, dynamic>>(
        '/trading-chat/messages',
        data: {'content': text},
      );
      _textController.clear();
      await _fetchMessages();
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message)),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
      }
    }
  }

  Future<void> _openTelegram() async {
    final uri = Uri.parse('https://t.me/sahmikasban');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final userCoins = ref.watch(sessionControllerProvider).profile?.balanceCoins ?? '0';
    final progress = (_votesCount / _votesTarget).clamp(0.0, 1.0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('غرفة التداول اليومية المباشرة'),
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
        child: Column(
          children: [
            // Telegram Official Community Banner
            Card(
              margin: const EdgeInsets.all(12),
              color: const Color(0xFF0088CC),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: InkWell(
                onTap: _openTelegram,
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      const Icon(Icons.send_rounded, color: Colors.white, size: 28),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'مجتمع التليجرام الرسمي (Sahmi Kasban)',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            Text(
                              'انضم الآن إلى القروب الرسمي لمتابعة التحليلات والنقاشات',
                              style: TextStyle(color: Colors.white70, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                      ElevatedButton(
                        onPressed: _openTelegram,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: const Color(0xFF0088CC),
                        ),
                        child: const Text('انضم الآن'),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Daily Campaign Voting Card Header
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'حالة التصويت اليومية:',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Chip(
                          avatar: const Icon(Icons.stars, size: 14, color: Colors.amber),
                          label: Text('$_votesCount / $_votesTarget صوت'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(
                      value: progress,
                      minHeight: 10,
                      borderRadius: BorderRadius.circular(99),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'ملاحظة: تكلفة التصويت 0.5 عملة. إذا لم تُفتح الغرفة بـ 40 صوتًا قبل الساعة 3:00 مساءً، سيتم رد العملات تلقائيًا إلى حسابك.',
                      style: TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                    const SizedBox(height: 12),
                    if (!_isUnlocked)
                      FilledButton.icon(
                        onPressed: (_hasVoted || _isVoting) ? null : _vote,
                        icon: _isVoting
                            ? const SizedBox.square(
                                dimension: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.how_to_vote_rounded),
                        label: Text(
                          _hasVoted
                              ? 'لقد قمت بالتصويت اليوم'
                              : 'تصويت لفتح الغرفة — 0.5 عملة',
                        ),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Live Chat Area
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : !_isUnlocked
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(
                                  Icons.lock_clock_rounded,
                                  size: 64,
                                  color: Colors.grey,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  'الغرفة مغلقة حتى اكتمال 40 صوتًا',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  'صوت الآن بـ 0.5 عملة للمساهمة في فتح الغرفة لجلسة اليوم المباشرة (من 9 صباحاً إلى 3 مساءً).',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(color: Colors.grey),
                                ),
                              ],
                            ),
                          ),
                        )
                      : Column(
                          children: [
                            Expanded(
                              child: ListView.builder(
                                padding: const EdgeInsets.all(12),
                                itemCount: _messages.length,
                                itemBuilder: (context, index) {
                                  final msg = _messages[index];
                                  return Align(
                                    alignment: Alignment.centerRight,
                                    child: Container(
                                      margin: const EdgeInsets.only(bottom: 8),
                                      padding: const EdgeInsets.all(10),
                                      decoration: BoxDecoration(
                                        color: theme.colorScheme.surfaceContainerHighest,
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            msg['user_name'] as String? ?? 'متداول',
                                            style: const TextStyle(
                                              fontSize: 11,
                                              fontWeight: FontWeight.bold,
                                              color: Colors.amber,
                                            ),
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            msg['content'] as String? ?? '',
                                            style: const TextStyle(fontSize: 13),
                                          ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                            if (_isSessionOpen)
                              Container(
                                padding: const EdgeInsets.all(8),
                                color: theme.colorScheme.surface,
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: TextField(
                                        controller: _textController,
                                        decoration: const InputDecoration(
                                          hintText: 'اكتب رسالتك في الغرفة المباشرة...',
                                          border: OutlineInputBorder(),
                                          contentPadding: EdgeInsets.symmetric(
                                            horizontal: 12,
                                            vertical: 8,
                                          ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    IconButton(
                                      icon: const Icon(Icons.send_rounded),
                                      onPressed: _isSending ? null : _sendMessage,
                                    ),
                                  ],
                                ),
                              )
                            else
                              Container(
                                padding: const EdgeInsets.all(12),
                                color: Colors.amber.withValues(alpha: 0.1),
                                child: const Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.info_outline_rounded, size: 16),
                                    SizedBox(width: 8),
                                    Text(
                                      'المحادثة المباشرة تفتح فقط أثناء ساعات التداول (9 ص - 3 م).',
                                      style: TextStyle(fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
            ),
          ],
        ),
      ),
    );
  }
}

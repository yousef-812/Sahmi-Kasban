import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_exception.dart';

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
  bool _isSending = false;

  bool _isSessionOpen = false;

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
          _isSessionOpen = data['is_session_open'] as bool? ?? false;
        });
      }

      await _fetchMessages();
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

    return Scaffold(
      appBar: AppBar(
        title: const Text('غرفة التداول اليومية المباشرة'),
        centerTitle: true,
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

            // Session Status Banner
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      _isSessionOpen ? Icons.wifi : Icons.wifi_off_rounded,
                      color: _isSessionOpen ? Colors.green : Colors.orange,
                      size: 28,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _isSessionOpen ? 'الغرفة مفتوحة الآن' : 'الغرفة مغلقة',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                              color: _isSessionOpen ? Colors.green : Colors.orange,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'ساعات العمل: 10:00 صباحاً - 2:30 مساءً بتوقيت مصر',
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),

            // Live Chat Area
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _messages.isEmpty
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  _isSessionOpen ? Icons.chat_bubble_outline : Icons.chat_bubble_outline,
                                  size: 64,
                                  color: Colors.grey,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  _isSessionOpen
                                      ? 'لم تُرسل رسائل بعد'
                                      : 'الغرفة مغلقة حالياً',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  _isSessionOpen
                                      ? 'ابدأ المحادثة الآن!'
                                      : 'افتح الغرفة في الموعد المحدد (10 ص - 2:30 م)',
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(color: Colors.grey),
                                ),
                              ],
                            ),
                          ),
                        )
                      : ListView.builder(
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

            // Message input — always visible while the session is open
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
                        onSubmitted: (_) => _sendMessage(),
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
                      'المحادثة المباشرة متاحة فقط بين 10:00 صباحاً و 2:30 مساءً بتوقيت مصر.',
                      style: TextStyle(fontSize: 12),
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

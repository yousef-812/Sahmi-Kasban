import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_exception.dart';
import '../../auth/session_controller.dart';
import '../widgets/referral_gate_dialog.dart';

class AiCopilotMessage {
  const AiCopilotMessage({
    required this.text,
    required this.isUser,
    this.ticker,
  });

  final String text;
  final bool isUser;
  final String? ticker;
}

class AiCopilotScreen extends ConsumerStatefulWidget {
  const AiCopilotScreen({
    super.key,
    this.initialTicker,
  });

  final String? initialTicker;

  static Route<void> route({String? initialTicker}) {
    return MaterialPageRoute<void>(
      builder: (_) => AiCopilotScreen(initialTicker: initialTicker),
    );
  }

  @override
  ConsumerState<AiCopilotScreen> createState() => _AiCopilotScreenState();
}

class _AiCopilotScreenState extends ConsumerState<AiCopilotScreen> {
  final List<AiCopilotMessage> _messages = [];
  final _questionController = TextEditingController();
  late final TextEditingController _tickerController;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tickerController = TextEditingController(text: widget.initialTicker ?? '');
    _messages.add(
      const AiCopilotMessage(
        text: 'أهلاً بك! أنا مساعدك الذكي المباشر لأسهم البورصة المصرية.\nاطرح أي سؤال عن سعر الدخول، الاتجاه، أو الجودة الفنية للسهم.',
        isUser: false,
      ),
    );
  }

  @override
  void dispose() {
    _questionController.dispose();
    _tickerController.dispose();
    super.dispose();
  }

  Future<void> _sendQuery() async {
    final question = _questionController.text.trim();
    if (question.isEmpty || _isLoading) return;

    final ticker = _tickerController.text.trim().toUpperCase();

    setState(() {
      _messages.add(
        AiCopilotMessage(
          text: question,
          isUser: true,
          ticker: ticker.isNotEmpty ? ticker : null,
        ),
      );
      _questionController.clear();
      _isLoading = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.dio.post<Map<String, dynamic>>(
        '/ai-copilot/query',
        data: <String, dynamic>{
          if (ticker.isNotEmpty) 'ticker': ticker,
          'question': question,
        },
      );

      final data = response.data?['data'] as Map<String, dynamic>? ?? response.data ?? {};
      final answer = data['answer'] as String? ?? 'تمت معالجة الاستفسار بنجاح.';

      ref.invalidate(sessionControllerProvider);

      if (mounted) {
        setState(() {
          _messages.add(
            AiCopilotMessage(
              text: answer,
              isUser: false,
              ticker: ticker.isNotEmpty ? ticker : null,
            ),
          );
        });
      }
    } on ApiException catch (e) {
      if (e.statusCode == 403 && e.payload is Map) {
        final details = e.payload as Map<String, dynamic>;
        if (details['error_code'] == 'REFERRAL_GATE_LOCKED' && mounted) {
          ReferralGateDialog.show(
            context,
            currentCount: (details['current'] as num?)?.toInt() ?? 0,
            requiredCount: (details['required'] as num?)?.toInt() ?? 5,
            referralCode: details['referral_code'] as String? ?? '',
          );
        }
      } else if (mounted) {
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
        title: const Text('المساعد الذكي للسهم'),
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
            // Info Header Banner
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: theme.colorScheme.surfaceContainerHighest,
              child: Row(
                children: const [
                  Icon(Icons.info_outline, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'تكلفة الاستفسار المباشر: 0.5 عملة. متاح مجاناً للمجتمعيين (5+ دعوات).',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),

            // Chat Messages List
            Expanded(
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final msg = _messages[index];
                  return _ChatBubble(message: msg);
                },
              ),
            ),

            if (_isLoading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: CircularProgressIndicator(),
              ),

            // Input Control Bar
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 4,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      SizedBox(
                        width: 90,
                        child: TextField(
                          controller: _tickerController,
                          textCapitalization: TextCapitalization.characters,
                          decoration: const InputDecoration(
                            hintText: 'السهم',
                            contentPadding: EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 10,
                            ),
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: TextField(
                          controller: _questionController,
                          decoration: const InputDecoration(
                            hintText: 'اطرح سؤالك هنا...',
                            contentPadding: EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 10,
                            ),
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (_) => _sendQuery(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton.filled(
                        onPressed: _isLoading ? null : _sendQuery,
                        icon: const Icon(Icons.send_rounded),
                      ),
                    ],
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

class _ChatBubble extends StatelessWidget {
  const _ChatBubble({required this.message});

  final AiCopilotMessage message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUser = message.isUser;

    return Align(
      alignment: isUser ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.82,
        ),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isUser
              ? theme.colorScheme.primary
              : theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16).copyWith(
            bottomLeft: isUser ? Radius.zero : const Radius.circular(16),
            bottomRight: !isUser ? Radius.zero : const Radius.circular(16),
          ),
        ),
        child: Column(
          crossAxisAlignment:
              isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            if (message.ticker != null && message.ticker!.isNotEmpty) ...[
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isUser
                      ? Colors.white.withValues(alpha: 0.2)
                      : theme.colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  message.ticker!,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: isUser
                        ? Colors.white
                        : theme.colorScheme.onPrimaryContainer,
                  ),
                ),
              ),
              const SizedBox(height: 6),
            ],
            Text(
              message.text,
              style: TextStyle(
                fontSize: 14,
                color: isUser
                    ? theme.colorScheme.onPrimary
                    : theme.colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

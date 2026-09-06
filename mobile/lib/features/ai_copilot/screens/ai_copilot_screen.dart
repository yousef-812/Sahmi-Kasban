import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../../data/backend_repository.dart';
import '../../../domain/models.dart';
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
  final FocusNode _tickerFocusNode = FocusNode();
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
    _tickerFocusNode.dispose();
    super.dispose();
  }

  Future<void> _openStockSearchModal() async {
    final selected = await showModalBottomSheet<MarketInstrument>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => const _StockSearchSheet(),
    );

    if (selected != null && mounted) {
      setState(() {
        _tickerController.text = selected.ticker;
      });
    }
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
    } catch (e) {
      final apiClient = ref.read(apiClientProvider);
      final apiError = apiClient.mapError(e);

      if (apiError.statusCode == 403 && apiError.payload is Map) {
        final details = apiError.payload as Map<String, dynamic>;
        final detailMap = details['detail'] is Map
            ? details['detail'] as Map<String, dynamic>
            : details;

        if (detailMap['error_code'] == 'REFERRAL_GATE_LOCKED' && mounted) {
          ReferralGateDialog.show(
            context,
            currentCount: (detailMap['current'] as num?)?.toInt() ?? 0,
            requiredCount: (detailMap['required'] as num?)?.toInt() ?? 5,
            referralCode: detailMap['referral_code'] as String? ?? '',
          );
          return;
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiError.message)),
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

            // Input Control Bar (Stacked Column layout)
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
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Full-width Stock Autocomplete Field (Stacked above)
                  RawAutocomplete<MarketInstrument>(
                    textEditingController: _tickerController,
                    focusNode: _tickerFocusNode,
                    optionsBuilder: (TextEditingValue textEditingValue) async {
                      final query = textEditingValue.text.trim();
                      if (query.isEmpty) return const [];
                      try {
                        return await ref
                            .read(backendRepositoryProvider)
                            .searchInstruments(query, limit: 10);
                      } catch (_) {
                        return const [];
                      }
                    },
                    displayStringForOption: (MarketInstrument option) => option.ticker,
                    fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
                      return TextField(
                        controller: controller,
                        focusNode: focusNode,
                        textCapitalization: TextCapitalization.characters,
                        decoration: InputDecoration(
                          labelText: 'السهم المستهدف (البورصة المصرية)',
                          hintText: 'ابحث باسم أو رمز السهم... (مثال: COMI, HELI)',
                          prefixIcon: const Icon(Icons.show_chart_rounded, size: 20),
                          suffixIcon: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              if (controller.text.isNotEmpty)
                                IconButton(
                                  icon: const Icon(Icons.clear_rounded, size: 18),
                                  onPressed: () {
                                    controller.clear();
                                  },
                                ),
                              IconButton(
                                icon: const Icon(Icons.search_rounded),
                                onPressed: _openStockSearchModal,
                              ),
                            ],
                          ),
                          border: const OutlineInputBorder(),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 10,
                          ),
                        ),
                      );
                    },
                    optionsViewBuilder: (context, onSelected, options) {
                      return Align(
                        alignment: Alignment.bottomRight,
                        child: Material(
                          elevation: 6,
                          borderRadius: BorderRadius.circular(8),
                          child: Container(
                            width: MediaQuery.of(context).size.width - 24,
                            constraints: const BoxConstraints(maxHeight: 200),
                            color: theme.colorScheme.surface,
                            child: ListView.separated(
                              padding: const EdgeInsets.symmetric(vertical: 4),
                              shrinkWrap: true,
                              itemCount: options.length,
                              separatorBuilder: (_, __) => const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final option = options.elementAt(index);
                                return ListTile(
                                  dense: true,
                                  title: Text(
                                    '${option.ticker} — ${option.description.isNotEmpty ? option.description : option.providerSymbol}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                    ),
                                  ),
                                  onTap: () {
                                    onSelected(option);
                                  },
                                );
                              },
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 10),

                  // Message Input Field + Send Button (Stacked below, full width, 5000 character limit)
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _questionController,
                          maxLength: 5000,
                          maxLengthEnforcement: MaxLengthEnforcement.enforced,
                          minLines: 1,
                          maxLines: 4,
                          decoration: const InputDecoration(
                            hintText: 'اطرح سؤالك هنا (حتى 5000 حرف)...',
                            contentPadding: EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 10,
                            ),
                            border: OutlineInputBorder(),
                            counterText: '',
                          ),
                          onSubmitted: (_) => _sendQuery(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Padding(
                        padding: const EdgeInsets.only(bottom: 2),
                        child: IconButton.filled(
                          onPressed: _isLoading ? null : _sendQuery,
                          icon: const Icon(Icons.send_rounded),
                        ),
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

class _StockSearchSheet extends ConsumerStatefulWidget {
  const _StockSearchSheet();

  @override
  ConsumerState<_StockSearchSheet> createState() => _StockSearchSheetState();
}

class _StockSearchSheetState extends ConsumerState<_StockSearchSheet> {
  final _searchController = TextEditingController();
  List<MarketInstrument> _items = const [];
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) {
      setState(() => _items = const []);
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await ref
          .read(backendRepositoryProvider)
          .searchInstruments(query, limit: 30);
      if (mounted) {
        setState(() => _items = items);
      }
    } on Object catch (error) {
      if (mounted) {
        setState(() => _error = error.toString());
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          16,
          16,
          16,
          16 + MediaQuery.viewInsetsOf(context).bottom,
        ),
        child: SizedBox(
          height: MediaQuery.sizeOf(context).height * 0.65,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'اختر سهمًا من البورصة المصرية',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close_rounded),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _searchController,
                autofocus: true,
                textCapitalization: TextCapitalization.characters,
                textInputAction: TextInputAction.search,
                decoration: InputDecoration(
                  hintText: 'ابحث باسم أو رمز السهم (مثال: COMI, HELI...)',
                  prefixIcon: const Icon(Icons.search_rounded),
                  suffixIcon: IconButton(
                    onPressed: _loading ? null : _search,
                    icon: const Icon(Icons.arrow_forward_rounded),
                  ),
                  border: const OutlineInputBorder(),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                ),
                onChanged: (_) => _search(),
                onSubmitted: (_) => _search(),
              ),
              if (_error != null) ...[
                const SizedBox(height: 8),
                Text(
                  _error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error, fontSize: 12),
                ),
              ],
              const SizedBox(height: 10),
              Expanded(
                child: _loading
                    ? const Center(child: CircularProgressIndicator())
                    : _items.isEmpty
                        ? const Center(child: Text('ابحث باسم أو رمز السهم للاختيار.'))
                        : ListView.separated(
                            itemCount: _items.length,
                            separatorBuilder: (context, index) => const Divider(height: 1),
                            itemBuilder: (context, index) {
                              final item = _items[index];
                              return ListTile(
                                dense: true,
                                title: Text(
                                  item.ticker,
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text(
                                  item.description.isEmpty ? item.providerSymbol : item.description,
                                ),
                                onTap: () => Navigator.of(context).pop(item),
                              );
                            },
                          ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

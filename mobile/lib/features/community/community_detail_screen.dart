import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../../core/network/api_exception.dart';
import '../../widgets/structured_data_card.dart';
import '../auth/session_controller.dart';
import 'community_models.dart';
import 'community_providers.dart';
import 'community_repository.dart';
import 'prediction_verification_card.dart';

class CommunityDetailScreen extends ConsumerStatefulWidget {
  const CommunityDetailScreen({required this.discussionId, super.key});

  final String discussionId;

  @override
  ConsumerState<CommunityDetailScreen> createState() =>
      _CommunityDetailScreenState();
}

class _CommunityDetailScreenState extends ConsumerState<CommunityDetailScreen> {
  bool _mutedLocally = false;
  bool _actionBusy = false;

  Future<void> _refresh() async {
    ref.invalidate(communityDiscussionProvider(widget.discussionId));
    await ref.read(communityDiscussionProvider(widget.discussionId).future);
  }

  Future<void> _report(CommunityDiscussion discussion) async {
    final result = await showDialog<_ReportInput>(
      context: context,
      builder: (context) => const _ReportDialog(),
    );
    if (result == null) {
      return;
    }
    await _runAction(
      () => ref
          .read(communityRepositoryProvider)
          .reportDiscussion(
            discussionId: discussion.id,
            reasonCode: result.reasonCode,
            details: result.details,
          ),
      successMessage: 'تم إرسال البلاغ للمراجعة.',
    );
  }

  Future<void> _toggleMute(CommunityDiscussion discussion) async {
    if (_mutedLocally) {
      await _runAction(
        () => ref
            .read(communityRepositoryProvider)
            .unmuteUser(discussion.author.userId),
        successMessage: 'تم إلغاء كتم المستخدم.',
        afterSuccess: () => setState(() => _mutedLocally = false),
      );
    } else {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('كتم المستخدم'),
          content: const Text(
            'ستختفي مناقشات هذا المستخدم من صفحة المجتمع الخاصة بك.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('إلغاء'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('كتم'),
            ),
          ],
        ),
      );
      if (confirmed != true) {
        return;
      }
      await _runAction(
        () => ref
            .read(communityRepositoryProvider)
            .muteUser(discussion.author.userId),
        successMessage: 'تم كتم المستخدم وإخفاء مناقشاته من المجتمع.',
        afterSuccess: () => setState(() => _mutedLocally = true),
      );
    }
    ref.invalidate(communityFeedProvider);
  }

  Future<void> _appeal(CommunityDiscussion discussion) async {
    final message = await showDialog<String>(
      context: context,
      builder: (context) => const _AppealDialog(),
    );
    if (message == null) {
      return;
    }
    await _runAction(
      () => ref
          .read(communityRepositoryProvider)
          .submitAppeal(discussionId: discussion.id, message: message),
      successMessage: 'تم إرسال الاستئناف للمراجعة.',
      afterSuccess: () {
        ref.invalidate(myAppealsProvider);
        ref.invalidate(myDiscussionsProvider);
      },
    );
  }

  Future<void> _toggleReaction(
    CommunityDiscussion discussion,
    String reactionType,
  ) async {
    await _runAction(
      () => ref.read(communityRepositoryProvider).toggleReaction(
        discussionId: discussion.id,
        reactionType: reactionType,
      ),
      successMessage: 'تم تحديث تفاعلك مع المناقشة.',
      afterSuccess: () {
        ref.invalidate(communityDiscussionProvider(discussion.id));
        ref.invalidate(communityFeedProvider);
      },
    );
  }

  Future<void> _runAction(
    Future<Object?> Function() action, {
    required String successMessage,
    VoidCallback? afterSuccess,
  }) async {
    if (_actionBusy) {
      return;
    }
    setState(() => _actionBusy = true);
    try {
      await action();
      afterSuccess?.call();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(successMessage)));
      }
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    } finally {
      if (mounted) {
        setState(() => _actionBusy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final discussion = ref.watch(
      communityDiscussionProvider(widget.discussionId),
    );
    final currentUserId = ref.watch(sessionControllerProvider).profile?.id;

    return Scaffold(
      appBar: AppBar(title: const Text('تفاصيل المناقشة')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: discussion.when(
          loading: () => ListView(
            children: [
              SizedBox(height: 240),
              Center(child: CircularProgressIndicator()),
            ],
          ),
          error: (error, stackTrace) => ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Text('تعذر تحميل المناقشة.'),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        onPressed: () => ref.invalidate(
                          communityDiscussionProvider(widget.discussionId),
                        ),
                        child: const Text('إعادة المحاولة'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          data: (item) {
            final isOwner = currentUserId == item.author.userId;
            return ListView(
              padding: const EdgeInsets.all(20),
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 24,
                              backgroundImage: AssetImage(
                                avatarAssetPath(item.author.avatarKey),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                item.author.displayName,
                                style: Theme.of(context).textTheme.titleMedium
                                    ?.copyWith(fontWeight: FontWeight.w800),
                              ),
                            ),
                            Chip(label: Text(item.ticker)),
                          ],
                        ),
                        const SizedBox(height: 18),
                        Text(
                          item.title,
                          style: Theme.of(context).textTheme.titleLarge
                              ?.copyWith(fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(height: 12),
                        MarkdownBody(
                          data: item.content,
                          selectable: true,
                          styleSheet:
                              MarkdownStyleSheet.fromTheme(
                                Theme.of(context),
                              ).copyWith(
                                p: Theme.of(
                                  context,
                                ).textTheme.bodyMedium?.copyWith(height: 1.5),
                              ),
                        ),
                        const SizedBox(height: 16),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          children: [
                            Chip(label: Text(item.periodLabel)),
                            Chip(label: Text(item.statusLabel)),
                            if (isOwner)
                              Chip(
                                avatar: const Icon(Icons.remove_red_eye_outlined, size: 14),
                                label: Text('${item.viewsCount} مشاهدة'),
                              ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        const Divider(),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: item.userReaction == 'agree'
                                  ? FilledButton(
                                      onPressed: _actionBusy
                                          ? null
                                          : () => _toggleReaction(item, 'agree'),
                                      child: Text('متفق (${item.agreeCount})'),
                                    )
                                  : OutlinedButton(
                                      onPressed: _actionBusy
                                          ? null
                                          : () => _toggleReaction(item, 'agree'),
                                      child: Text('متفق (${item.agreeCount})'),
                                    ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: item.userReaction == 'disagree'
                                  ? FilledButton(
                                      onPressed: _actionBusy
                                          ? null
                                          : () => _toggleReaction(item, 'disagree'),
                                      child: Text('غير متفق (${item.disagreeCount})'),
                                    )
                                  : OutlinedButton(
                                      onPressed: _actionBusy
                                          ? null
                                          : () => _toggleReaction(item, 'disagree'),
                                      child: Text('غير متفق (${item.disagreeCount})'),
                                    ),
                            ),
                          ],
                        ),
                        if (item.rejectionCode != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            'سبب الرفض: ${item.rejectionCode}',
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                if (item.frozenPrediction.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  StructuredDataCard(
                    title: 'التوقع المجمد وقت النشر',
                    data: item.frozenPrediction,
                  ),
                ],
                if (isOwner && item.status == 'published') ...[
                  const SizedBox(height: 14),
                  PredictionVerificationCard(discussionId: item.id),
                ],
                if (item.moderationResult.isNotEmpty && isOwner) ...[
                  const SizedBox(height: 14),
                  StructuredDataCard(
                    title: 'نتيجة المراجعة',
                    data: item.moderationResult,
                  ),
                ],
                const SizedBox(height: 18),
                if (isOwner && item.canAppeal)
                  FilledButton.icon(
                    onPressed: _actionBusy ? null : () => _appeal(item),
                    icon: const Icon(Icons.gavel_outlined),
                    label: const Text('تقديم استئناف'),
                  ),
                if (!isOwner) ...[
                  OutlinedButton.icon(
                    onPressed: _actionBusy ? null : () => _report(item),
                    icon: const Icon(Icons.flag_outlined),
                    label: const Text('الإبلاغ عن المناقشة'),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    onPressed: _actionBusy ? null : () => _toggleMute(item),
                    icon: Icon(
                      _mutedLocally
                          ? Icons.volume_up_outlined
                          : Icons.volume_off_outlined,
                    ),
                    label: Text(
                      _mutedLocally ? 'إلغاء كتم المستخدم' : 'كتم المستخدم',
                    ),
                  ),
                ],
                if (_actionBusy) ...[
                  const SizedBox(height: 16),
                  const Center(child: CircularProgressIndicator()),
                ],
              ],
            );
          },
        ),
      ),
    );
  }
}

class _ReportInput {
  const _ReportInput({required this.reasonCode, required this.details});

  final String reasonCode;
  final String details;
}

class _ReportDialog extends StatefulWidget {
  const _ReportDialog();

  @override
  State<_ReportDialog> createState() => _ReportDialogState();
}

class _ReportDialogState extends State<_ReportDialog> {
  final _detailsController = TextEditingController();
  String _reasonCode = 'spam';

  @override
  void dispose() {
    _detailsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('الإبلاغ عن المناقشة'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _reasonCode,
            decoration: const InputDecoration(labelText: 'سبب البلاغ'),
            items: const [
              DropdownMenuItem(
                value: 'spam',
                child: Text('محتوى مكرر أو مزعج'),
              ),
              DropdownMenuItem(value: 'abuse', child: Text('إساءة')),
              DropdownMenuItem(value: 'misleading', child: Text('محتوى مضلل')),
              DropdownMenuItem(
                value: 'contact_info',
                child: Text('بيانات تواصل'),
              ),
              DropdownMenuItem(value: 'off_topic', child: Text('خارج الموضوع')),
              DropdownMenuItem(value: 'other', child: Text('سبب آخر')),
            ],
            onChanged: (value) => setState(() => _reasonCode = value ?? 'spam'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _detailsController,
            maxLength: 1000,
            minLines: 2,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: 'تفاصيل إضافية',
              alignLabelWithHint: true,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('إلغاء'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(
            _ReportInput(
              reasonCode: _reasonCode,
              details: _detailsController.text,
            ),
          ),
          child: const Text('إرسال البلاغ'),
        ),
      ],
    );
  }
}

class _AppealDialog extends StatefulWidget {
  const _AppealDialog();

  @override
  State<_AppealDialog> createState() => _AppealDialogState();
}

class _AppealDialogState extends State<_AppealDialog> {
  final _controller = TextEditingController();
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submit() {
    final message = _controller.text.trim();
    if (message.length < 20) {
      setState(() => _error = 'اكتب سببًا واضحًا لا يقل عن 20 حرفًا.');
      return;
    }
    Navigator.of(context).pop(message);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('تقديم استئناف'),
      content: TextField(
        controller: _controller,
        autofocus: true,
        minLines: 4,
        maxLines: 8,
        maxLength: 2000,
        decoration: InputDecoration(
          labelText: 'وضح سبب طلب إعادة المراجعة',
          alignLabelWithHint: true,
          errorText: _error,
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('إلغاء'),
        ),
        FilledButton(onPressed: _submit, child: const Text('إرسال الاستئناف')),
      ],
    );
  }
}

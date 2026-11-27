import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import '../auth/session_controller.dart';
import 'admin_badge.dart';
import 'community_models.dart';
import 'community_repository.dart';

/// Comments and one-level replies for a discussion.
class DiscussionCommentsScreen extends ConsumerStatefulWidget {
  const DiscussionCommentsScreen({
    required this.discussionId,
    required this.title,
    super.key,
  });

  final String discussionId;
  final String title;

  @override
  ConsumerState<DiscussionCommentsScreen> createState() =>
      _DiscussionCommentsScreenState();
}

class _DiscussionCommentsScreenState
    extends ConsumerState<DiscussionCommentsScreen> {
  final TextEditingController _controller = TextEditingController();
  List<DiscussionComment> _comments = const <DiscussionComment>[];
  bool _loading = true;
  bool _sending = false;
  String? _error;
  DiscussionComment? _replyTo;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await ref
          .read(communityRepositoryProvider)
          .listComments(widget.discussionId);
      if (!mounted) return;
      setState(() {
        _comments = items;
        _loading = false;
      });
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.message;
        _loading = false;
      });
    }
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _sending) return;
    setState(() => _sending = true);
    try {
      await ref.read(communityRepositoryProvider).addComment(
            discussionId: widget.discussionId,
            content: text,
            parentId: _replyTo?.id,
          );
      _controller.clear();
      _replyTo = null;
      await _load();
    } on ApiException catch (error) {
      if (!mounted) return;
      AppNotice.show(
        context,
        message: error.statusCode == 422
            ? 'التعليق مرفوض: ممنوع الروابط وأرقام التواصل ووعود الربح المضمون.'
            : error.message,
        tone: AppNoticeTone.error,
      );
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  Future<void> _delete(DiscussionComment comment) async {
    try {
      await ref.read(communityRepositoryProvider).deleteComment(
            discussionId: widget.discussionId,
            commentId: comment.id,
          );
      await _load();
    } on ApiException catch (error) {
      if (!mounted) return;
      AppNotice.show(context, message: error.message, tone: AppNoticeTone.error);
    }
  }

  Widget _commentTile(DiscussionComment comment, {required bool isReply}) {
    final profile = ref.watch(sessionControllerProvider).profile;
    final canDelete = comment.isMine || (profile?.isAdmin ?? false);
    return Padding(
      padding: EdgeInsetsDirectional.only(start: isReply ? 40 : 0, bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: isReply ? 14 : 18,
            backgroundImage: AssetImage(avatarAssetPath(comment.author.avatarKey)),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Flexible(
                        child: Text(
                          comment.author.displayName,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                      if (comment.author.isAdmin) const AdminBadge(),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(comment.content),
                  Row(
                    children: [
                      TextButton(
                        onPressed: () => setState(() => _replyTo = comment),
                        child: const Text('رد'),
                      ),
                      if (canDelete)
                        TextButton(
                          onPressed: () => _delete(comment),
                          child: const Text('حذف'),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final top = _comments.where((c) => c.parentId == null).toList();
    final signedIn = ref.watch(sessionControllerProvider).profile != null;
    return Scaffold(
      appBar: AppBar(title: Text('التعليقات: ${widget.title}')),
      body: Column(
        children: [
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                    ? Center(child: Text(_error!))
                    : top.isEmpty
                        ? const Center(child: Text('لا توجد تعليقات بعد. كن أول من يعلّق.'))
                        : RefreshIndicator(
                            onRefresh: _load,
                            child: ListView(
                              padding: const EdgeInsets.all(16),
                              children: [
                                for (final c in top) ...[
                                  _commentTile(c, isReply: false),
                                  for (final r in _comments.where((x) => x.parentId == c.id))
                                    _commentTile(r, isReply: true),
                                ],
                              ],
                            ),
                          ),
          ),
          if (signedIn)
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(12, 4, 12, 8),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (_replyTo != null)
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              'رد على ${_replyTo!.author.displayName}',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, size: 18),
                            onPressed: () => setState(() => _replyTo = null),
                          ),
                        ],
                      ),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            maxLength: 500,
                            minLines: 1,
                            maxLines: 4,
                            decoration: const InputDecoration(
                              hintText: 'اكتب تعليقك...',
                              counterText: '',
                            ),
                          ),
                        ),
                        IconButton(
                          icon: _sending
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.send),
                          onPressed: _sending ? null : _send,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

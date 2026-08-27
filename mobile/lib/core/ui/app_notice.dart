import 'dart:async';

import 'package:flutter/material.dart';

enum AppNoticeTone { success, error, warning, info }

class AppNotice {
  AppNotice._();

  static OverlayEntry? _activeEntry;
  static Timer? _dismissTimer;

  static void show(
    BuildContext context, {
    required String message,
    String? title,
    AppNoticeTone tone = AppNoticeTone.info,
    Duration duration = const Duration(seconds: 4),
  }) {
    _dismissTimer?.cancel();
    _removeActive();

    final overlay = Overlay.maybeOf(context, rootOverlay: true);
    if (overlay == null) {
      return;
    }

    late final OverlayEntry entry;
    entry = OverlayEntry(
      builder: (overlayContext) => _AppNoticeBanner(
        title: title,
        message: message,
        tone: tone,
        onDismiss: () {
          if (identical(_activeEntry, entry)) {
            _dismissTimer?.cancel();
            _activeEntry = null;
          }
          entry.remove();
        },
      ),
    );
    _activeEntry = entry;
    overlay.insert(entry);
    _dismissTimer = Timer(duration, () {
      if (identical(_activeEntry, entry)) {
        _removeActive();
      }
    });
  }

  static void _removeActive() {
    _dismissTimer?.cancel();
    _dismissTimer = null;
    final entry = _activeEntry;
    _activeEntry = null;
    entry?.remove();
  }
}

class _AppNoticeBanner extends StatefulWidget {
  const _AppNoticeBanner({
    required this.message,
    required this.tone,
    required this.onDismiss,
    this.title,
  });

  final String? title;
  final String message;
  final AppNoticeTone tone;
  final VoidCallback onDismiss;

  @override
  State<_AppNoticeBanner> createState() => _AppNoticeBannerState();
}

class _AppNoticeBannerState extends State<_AppNoticeBanner>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<Offset> _slide;
  late final Animation<double> _fade;
  bool _closing = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 280),
      reverseDuration: const Duration(milliseconds: 180),
    );
    final curve = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
      reverseCurve: Curves.easeInCubic,
    );
    _slide = Tween<Offset>(
      begin: const Offset(0, -1.15),
      end: Offset.zero,
    ).animate(curve);
    _fade = Tween<double>(begin: 0, end: 1).animate(curve);
    _controller.forward();
  }

  Future<void> _dismiss() async {
    if (_closing) {
      return;
    }
    _closing = true;
    await _controller.reverse();
    widget.onDismiss();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final palette = _palette(theme.colorScheme, widget.tone);
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        minimum: const EdgeInsets.fromLTRB(14, 10, 14, 0),
        child: SlideTransition(
          position: _slide,
          child: FadeTransition(
            opacity: _fade,
            child: Material(
              color: Colors.transparent,
              child: Container(
                constraints: const BoxConstraints(maxWidth: 560),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                padding: const EdgeInsetsDirectional.fromSTEB(16, 14, 8, 14),
                decoration: BoxDecoration(
                  color: palette.background,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: palette.border),
                  boxShadow: const [
                    BoxShadow(
                      blurRadius: 24,
                      offset: Offset(0, 10),
                      color: Color(0x24000000),
                    ),
                  ],
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: palette.iconBackground,
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: Icon(palette.icon, color: palette.foreground),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (widget.title?.trim().isNotEmpty == true) ...[
                            Text(
                              widget.title!,
                              style: theme.textTheme.titleSmall?.copyWith(
                                color: palette.foreground,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 3),
                          ],
                          Text(
                            widget.message,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: palette.foreground,
                              height: 1.45,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      tooltip: 'إغلاق',
                      onPressed: _dismiss,
                      visualDensity: VisualDensity.compact,
                      icon: Icon(
                        Icons.close_rounded,
                        color: palette.foreground.withValues(alpha: 0.75),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

_NoticePalette _palette(ColorScheme scheme, AppNoticeTone tone) {
  final dark = scheme.brightness == Brightness.dark;
  return switch (tone) {
    AppNoticeTone.success =>
      dark
          ? _NoticePalette(
              background: const Color(0xFF10301F),
              border: const Color(0xFF00E676).withValues(alpha: 0.35),
              iconBackground: const Color(0xFF00E676).withValues(alpha: 0.14),
              foreground: const Color(0xFF7CF0B5),
              icon: Icons.check_circle_rounded,
            )
          : const _NoticePalette(
              background: Color(0xFFF0F9F4),
              border: Color(0xFFB8DFC9),
              iconBackground: Color(0xFFD8F0E2),
              foreground: Color(0xFF145A43),
              icon: Icons.check_circle_rounded,
            ),
    AppNoticeTone.error => _NoticePalette(
      background: scheme.errorContainer,
      border: scheme.error.withValues(alpha: 0.28),
      iconBackground: scheme.error.withValues(alpha: 0.12),
      foreground: scheme.onErrorContainer,
      icon: Icons.error_rounded,
    ),
    AppNoticeTone.warning =>
      dark
          ? _NoticePalette(
              background: const Color(0xFF332A10),
              border: const Color(0xFFFFB800).withValues(alpha: 0.35),
              iconBackground: const Color(0xFFFFB800).withValues(alpha: 0.14),
              foreground: const Color(0xFFFFDCA6),
              icon: Icons.warning_amber_rounded,
            )
          : const _NoticePalette(
              background: Color(0xFFFFF8E7),
              border: Color(0xFFF0D391),
              iconBackground: Color(0xFFFFE8B1),
              foreground: Color(0xFF6B4B00),
              icon: Icons.warning_amber_rounded,
            ),
    AppNoticeTone.info => _NoticePalette(
      background: scheme.surfaceContainerHighest,
      border: scheme.outlineVariant,
      iconBackground: scheme.primary.withValues(alpha: 0.12),
      foreground: scheme.onSurface,
      icon: Icons.info_rounded,
    ),
  };
}

class _NoticePalette {
  const _NoticePalette({
    required this.background,
    required this.border,
    required this.iconBackground,
    required this.foreground,
    required this.icon,
  });

  final Color background;
  final Color border;
  final Color iconBackground;
  final Color foreground;
  final IconData icon;
}

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class DesktopCustomTitleBar extends StatefulWidget {
  const DesktopCustomTitleBar({super.key, required this.child});

  final Widget child;

  @override
  State<DesktopCustomTitleBar> createState() => _DesktopCustomTitleBarState();
}

class _DesktopCustomTitleBarState extends State<DesktopCustomTitleBar> {
  bool _isFullscreen = true;
  bool _showHint = true;
  Timer? _hintTimer;

  @override
  void initState() {
    super.initState();
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.windows) {
      _applyFullscreen(_isFullscreen);
      _scheduleHintDismiss();
    }
  }

  @override
  void dispose() {
    _hintTimer?.cancel();
    super.dispose();
  }

  void _scheduleHintDismiss() {
    _hintTimer?.cancel();
    setState(() {
      _showHint = true;
    });
    _hintTimer = Timer(const Duration(seconds: 4), () {
      if (mounted) {
        setState(() {
          _showHint = false;
        });
      }
    });
  }

  void _applyFullscreen(bool enable) {
    if (enable) {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
    } else {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    }
  }

  void _toggleFullscreen() {
    setState(() {
      _isFullscreen = !_isFullscreen;
    });
    _applyFullscreen(_isFullscreen);
    if (_isFullscreen) {
      _scheduleHintDismiss();
    } else {
      _hintTimer?.cancel();
      setState(() {
        _showHint = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.windows) {
      return widget.child;
    }

    return CallbackShortcuts(
      bindings: {
        const SingleActivator(LogicalKeyboardKey.escape): _toggleFullscreen,
        const SingleActivator(LogicalKeyboardKey.f11): _toggleFullscreen,
      },
      child: Focus(
        autofocus: true,
        child: Stack(
          children: [
            widget.child,
            AnimatedOpacity(
              opacity: (_isFullscreen && _showHint) ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 300),
              child: IgnorePointer(
                ignoring: !(_isFullscreen && _showHint),
                child: SafeArea(
                  child: Align(
                    alignment: Alignment.topCenter,
                    child: Container(
                      margin: const EdgeInsets.only(top: 16),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.85),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: const Color(0xFF2FA87B).withValues(alpha: 0.5),
                          width: 1,
                        ),
                        boxShadow: const [
                          BoxShadow(
                            color: Colors.black38,
                            blurRadius: 10,
                            offset: Offset(0, 4),
                          ),
                        ],
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.fullscreen_rounded,
                            size: 18,
                            color: Color(0xFF2FA87B),
                          ),
                          SizedBox(width: 8),
                          Text(
                            'اضغط ESC أو F11 للخروج من ملء الشاشة',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                              fontFamily: '-apple-system, "Segoe UI", Roboto',
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

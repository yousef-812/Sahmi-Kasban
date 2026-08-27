import 'package:flutter/material.dart';
import '../theme/terminal_theme.dart';

/// Skeleton loading موحد بهوية Terminal.
/// يُستخدم في كل الشاشات أثناء التحميل.
class TerminalSkeleton extends StatefulWidget {
  const TerminalSkeleton({
    required this.width,
    required this.height,
    this.borderRadius = 8,
    super.key,
  });

  final double width;
  final double height;
  final double borderRadius;

  @override
  State<TerminalSkeleton> createState() => _TerminalSkeletonState();
}

class _TerminalSkeletonState extends State<TerminalSkeleton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = TerminalTheme.of(context);
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final progress = _controller.value;
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [theme.bgSurface, theme.bgElevated, theme.bgSurface],
              stops: [
                (progress - 0.3).clamp(0.0, 1.0),
                progress,
                (progress + 0.3).clamp(0.0, 1.0),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Skeleton لشاشة التحليل السريع.
class QuickAnalyzeSkeleton extends StatelessWidget {
  const QuickAnalyzeSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // شريط البحث
        const TerminalSkeleton(
          width: double.infinity,
          height: 56,
          borderRadius: 12,
        ),
        const SizedBox(height: 24),
        // عنوان القسم
        const TerminalSkeleton(width: 120, height: 14),
        const SizedBox(height: 12),
        // آخر التحليلات
        ...List.generate(
          3,
          (_) => const Padding(
            padding: EdgeInsets.only(bottom: 8),
            child: TerminalSkeleton(width: double.infinity, height: 60),
          ),
        ),
        const SizedBox(height: 16),
        // الأسهم الشائعة
        const TerminalSkeleton(width: 100, height: 14),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: List.generate(
            5,
            (i) => TerminalSkeleton(
              width: 70 + (i * 10) % 30,
              height: 32,
              borderRadius: 20,
            ),
          ),
        ),
      ],
    );
  }
}

/// Skeleton لشاشة قائمة المراقبة.
class WatchlistSkeleton extends StatelessWidget {
  const WatchlistSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        6,
        (_) => const Padding(
          padding: EdgeInsets.only(bottom: 8),
          child: TerminalSkeleton(width: double.infinity, height: 72),
        ),
      ),
    );
  }
}

/// Skeleton لشاشة Pulse.
class PulseSkeleton extends StatelessWidget {
  const PulseSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Market Status
        const TerminalSkeleton(
          width: double.infinity,
          height: 120,
          borderRadius: 12,
        ),
        const SizedBox(height: 16),
        // Quick Stats
        Row(
          children: List.generate(
            3,
            (_) => const Expanded(
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 4),
                child: TerminalSkeleton(width: double.infinity, height: 80),
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        // Last Analysis
        const TerminalSkeleton(
          width: double.infinity,
          height: 80,
          borderRadius: 12,
        ),
        const SizedBox(height: 16),
        // Top 10
        const TerminalSkeleton(
          width: double.infinity,
          height: 200,
          borderRadius: 12,
        ),
      ],
    );
  }
}

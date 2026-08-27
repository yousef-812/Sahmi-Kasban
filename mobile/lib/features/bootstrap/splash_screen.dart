import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/auth/biometric_service.dart';
import '../../core/haptics.dart';
import '../auth/session_controller.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _tryBiometricAutoLogin();
  }

  Future<void> _tryBiometricAutoLogin() async {
    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;

    try {
      final biometricService = ref.read(biometricServiceProvider);
      final biometricResult = await biometricService.tryLogin();

      if (biometricResult != null && mounted) {
        final session = ref.read(sessionControllerProvider.notifier);
        await session.authenticateWithTokens(
          accessToken: biometricResult.accessToken,
          refreshToken: biometricResult.refreshToken,
        );
        TerminalHaptics.success();
        if (mounted) {
          context.go('/pulse');
        }
      }
    } catch (_) {
      // Ignore errors so normal authentication flow takes over safely.
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Directionality(
        textDirection: TextDirection.rtl,
        child: DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: [Color(0xFF041F18), Color(0xFF07543A), Color(0xFF0B382A)],
            ),
          ),
          child: Stack(
            fit: StackFit.expand,
            children: [
              _AmbientCircle(
                alignment: Alignment.topLeft,
                size: 260,
                color: Color(0x1FC9A85C),
              ),
              _AmbientCircle(
                alignment: Alignment.bottomRight,
                size: 310,
                color: Color(0x1F2EB67D),
              ),
              SafeArea(
                child: Center(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 32),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _BrandMark(),
                        SizedBox(height: 28),
                        Text(
                          'سهمي كسبان',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 38,
                            height: 1.15,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.2,
                          ),
                        ),
                        SizedBox(height: 10),
                        Text(
                          'تحليل أذكى • قرارات أوضح',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFFE8D39A),
                            fontSize: 16,
                            height: 1.5,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        SizedBox(height: 34),
                        SizedBox(
                          width: 104,
                          child: LinearProgressIndicator(
                            minHeight: 4,
                            borderRadius: BorderRadius.all(Radius.circular(20)),
                            backgroundColor: Color(0x33FFFFFF),
                            color: Color(0xFFD8B867),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BrandMark extends StatelessWidget {
  const _BrandMark();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 132,
      height: 132,
      padding: const EdgeInsets.all(7),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(36),
        gradient: const LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [Color(0xFFF2D996), Color(0xFFB98B2F)],
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x66000000),
            blurRadius: 30,
            offset: Offset(0, 14),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(30),
        child: Image.asset(
          'assets/branding/app_icon.png',
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return const ColoredBox(
              color: Color(0xFF07543A),
              child: Icon(
                Icons.trending_up_rounded,
                size: 56,
                color: Color(0xFFD8B867),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _AmbientCircle extends StatelessWidget {
  const _AmbientCircle({
    required this.alignment,
    required this.size,
    required this.color,
  });

  final Alignment alignment;
  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Transform.translate(
        offset: Offset(
          alignment.x.isNegative ? -size * 0.34 : size * 0.34,
          alignment.y.isNegative ? -size * 0.34 : size * 0.34,
        ),
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
      ),
    );
  }
}

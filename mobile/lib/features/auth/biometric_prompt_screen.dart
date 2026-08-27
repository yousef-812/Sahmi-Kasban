import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/auth/biometric_service.dart';
import '../../core/theme/terminal_theme.dart';

/// شاشة تفعيل المصادقة البيومترية — تظهر بعد أول تسجيل دخول ناجح.
class BiometricPromptScreen extends ConsumerStatefulWidget {
  const BiometricPromptScreen({
    required this.accessToken,
    required this.refreshToken,
    required this.onComplete,
    super.key,
  });

  final String accessToken;
  final String refreshToken;
  final VoidCallback onComplete;

  @override
  ConsumerState<BiometricPromptScreen> createState() =>
      _BiometricPromptScreenState();
}

class _BiometricPromptScreenState extends ConsumerState<BiometricPromptScreen> {
  bool _enabling = false;
  String? _error;

  Future<void> _enable() async {
    setState(() {
      _enabling = true;
      _error = null;
    });

    try {
      final service = ref.read(biometricServiceProvider);
      final success = await service.enable(
        accessToken: widget.accessToken,
        refreshToken: widget.refreshToken,
      );

      if (!mounted) return;
      HapticFeedback.heavyImpact();

      if (success) {
        widget.onComplete();
      } else {
        setState(() {
          _enabling = false;
          _error = 'تم إلغاء العملية';
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _enabling = false;
        _error = 'تعذر تفعيل المصادقة البيومترية';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = TerminalTheme.of(context);
    final availability = ref.watch(biometricAvailabilityProvider);

    return Scaffold(
      backgroundColor: theme.bgBase,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // أيقونة كبيرة متحركة
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      theme.signalGold.withValues(alpha: 0.3),
                      theme.signalGold.withValues(alpha: 0.05),
                    ],
                  ),
                ),
                child: Icon(
                  Icons.fingerprint_rounded,
                  color: theme.signalGold,
                  size: 72,
                ),
              ),
              const SizedBox(height: 32),
              Text(
                'دخول أسرع ببصمتك',
                style: theme.monoLarge.copyWith(
                  color: theme.textPrimary,
                  fontWeight: FontWeight.w900,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                'فعّل الدخول السريع عبر Face ID أو البصمة\nلتوفير 15 ثانية في كل دخول',
                style: theme.monoSmall.copyWith(
                  color: theme.textSecondary,
                  height: 1.6,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.bearRed.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: theme.bearRed.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: theme.bearRed, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _error!,
                          style: theme.monoSmall.copyWith(color: theme.bearRed),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],
              availability.when(
                data: (status) => Column(
                  children: [
                    if (status == BiometricAvailability.available)
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: _enabling ? null : _enable,
                          icon: _enabling
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Color(0xFF0A0E1A),
                                  ),
                                )
                              : const Icon(Icons.fingerprint_rounded),
                          label: Text(
                            _enabling ? 'جاري التفعيل...' : 'تفعيل الآن',
                            style: theme.monoSmall.copyWith(
                              color: const Color(0xFF0A0E1A),
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          style: FilledButton.styleFrom(
                            backgroundColor: theme.signalGold,
                            foregroundColor: const Color(0xFF0A0E1A),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    if (status != BiometricAvailability.available)
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: theme.bgSurface,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: theme.border),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.info_outline,
                              color: theme.textSecondary,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                _biometricMessage(status),
                                style: theme.monoSmall.copyWith(
                                  color: theme.textSecondary,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
                loading: () => const CircularProgressIndicator(),
                error: (_, __) => const SizedBox.shrink(),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: _enabling ? null : widget.onComplete,
                child: Text(
                  'تخطي الآن',
                  style: theme.monoSmall.copyWith(
                    color: theme.textTertiary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _biometricMessage(BiometricAvailability status) {
    return switch (status) {
      BiometricAvailability.noBiometrics => 'جهازك لا يدعم البصمة أو Face ID',
      BiometricAvailability.notSupported =>
        'المصادقة البيومترية غير متوفرة على هذا الجهاز',
      BiometricAvailability.error => 'حدث خطأ في التحقق من التوفر',
      BiometricAvailability.available => '',
    };
  }
}

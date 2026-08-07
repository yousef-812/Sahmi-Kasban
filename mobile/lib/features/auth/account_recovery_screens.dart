import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import '../../data/backend_repository.dart';

class VerifyEmailScreen extends ConsumerStatefulWidget {
  const VerifyEmailScreen({super.key, this.email});

  final String? email;

  @override
  ConsumerState<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends ConsumerState<VerifyEmailScreen> {
  final _codeController = TextEditingController();
  late final TextEditingController _emailController;
  Timer? _cooldownTimer;
  bool _verifying = false;
  bool _resending = false;
  int _resendCooldown = 0;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.email ?? '');
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    _codeController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    final email = _emailController.text.trim();
    final code = _codeController.text.trim();
    if (!_isValidEmail(email)) {
      _showNotice('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    if (!RegExp(r'^\d{6}$').hasMatch(code) || _verifying) {
      _showNotice(
        'أدخل رمز التأكيد المكوّن من 6 أرقام.',
        AppNoticeTone.warning,
      );
      return;
    }
    setState(() => _verifying = true);
    try {
      await ref
          .read(backendRepositoryProvider)
          .verifyEmail(email: email, code: code);
      if (!mounted) {
        return;
      }
      _showNotice(
        'تم تأكيد بريدك بنجاح. يمكنك تسجيل الدخول الآن.',
        AppNoticeTone.success,
        title: 'تم التأكيد',
      );
      context.go('/login');
    } on ApiException catch (error) {
      _showNotice(error.message, AppNoticeTone.error, title: 'تعذر التأكيد');
    } finally {
      if (mounted) {
        setState(() => _verifying = false);
      }
    }
  }

  Future<void> _resend() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email)) {
      _showNotice('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    if (_resending || _resendCooldown > 0) {
      return;
    }
    setState(() => _resending = true);
    try {
      await ref.read(backendRepositoryProvider).resendVerification(email);
      if (!mounted) {
        return;
      }
      _startResendCooldown();
      _showNotice(
        'أرسلنا رمزًا جديدًا إلى بريدك. راجع البريد غير الهام أيضًا.',
        AppNoticeTone.success,
        title: 'تم إرسال الرمز',
      );
    } on ApiException catch (error) {
      _showNotice(error.message, AppNoticeTone.error, title: 'تعذر الإرسال');
    } finally {
      if (mounted) {
        setState(() => _resending = false);
      }
    }
  }

  void _startResendCooldown() {
    _cooldownTimer?.cancel();
    setState(() => _resendCooldown = 30);
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted || _resendCooldown <= 1) {
        timer.cancel();
        if (mounted) {
          setState(() => _resendCooldown = 0);
        }
        return;
      }
      setState(() => _resendCooldown -= 1);
    });
  }

  void _showNotice(String message, AppNoticeTone tone, {String? title}) {
    if (!mounted) {
      return;
    }
    AppNotice.show(context, message: message, title: title, tone: tone);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return _AccountActionScaffold(
      icon: Icons.mark_email_read_outlined,
      title: 'تأكيد البريد الإلكتروني',
      subtitle: 'أدخل الكود المكوّن من 6 أرقام الذي أرسلناه إلى بريدك.',
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: theme.colorScheme.primaryContainer.withValues(alpha: 0.35),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: theme.colorScheme.outlineVariant),
          ),
          child: Row(
            children: [
              Icon(Icons.schedule_rounded, color: theme.colorScheme.primary),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'الكود صالح لمدة 10 دقائق. لا تشاركه مع أي شخص.',
                  style: TextStyle(height: 1.5, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          textDirection: TextDirection.ltr,
          autofillHints: const [AutofillHints.email],
          decoration: const InputDecoration(
            labelText: 'البريد الإلكتروني',
            prefixIcon: Icon(Icons.alternate_email_rounded),
          ),
        ),
        const SizedBox(height: 18),
        TextField(
          controller: _codeController,
          autofocus: true,
          keyboardType: TextInputType.number,
          textInputAction: TextInputAction.done,
          autofillHints: const [AutofillHints.oneTimeCode],
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
            LengthLimitingTextInputFormatter(6),
          ],
          maxLength: 6,
          textAlign: TextAlign.center,
          textDirection: TextDirection.ltr,
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.w800,
            letterSpacing: 12,
          ),
          decoration: InputDecoration(
            counterText: '',
            hintText: '000000',
            hintStyle: TextStyle(
              color: theme.colorScheme.outlineVariant,
              letterSpacing: 12,
            ),
            filled: true,
            fillColor: theme.colorScheme.surfaceContainerLowest,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 20,
              vertical: 22,
            ),
          ),
          onSubmitted: (_) => _verify(),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          onPressed: _verifying ? null : _verify,
          icon: _verifying
              ? const _ButtonLoader()
              : const Icon(Icons.verified_rounded),
          label: Text(_verifying ? 'جاري التأكيد...' : 'تأكيد البريد'),
        ),
        const SizedBox(height: 24),
        const Divider(),
        const SizedBox(height: 14),
        OutlinedButton.icon(
          onPressed: _resending || _resendCooldown > 0 ? null : _resend,
          icon: _resending
              ? const _ButtonLoader()
              : const Icon(Icons.refresh_rounded),
          label: Text(
            _resending
                ? 'جاري الإرسال...'
                : _resendCooldown > 0
                ? 'إعادة الإرسال بعد $_resendCooldown ثانية'
                : 'إعادة إرسال الكود',
          ),
        ),
        TextButton(
          onPressed: () => context.go('/login'),
          child: const Text('العودة لتسجيل الدخول'),
        ),
      ],
    );
  }
}

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email) || _submitting) {
      _showMessage('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref.read(backendRepositoryProvider).forgotPassword(email);
      if (!mounted) {
        return;
      }
      _showMessage(
        'إذا كان الحساب موجودًا فستصلك تعليمات الاستعادة.',
        AppNoticeTone.success,
      );
      context.go('/reset-password?email=${Uri.encodeQueryComponent(email)}');
    } on ApiException catch (error) {
      _showMessage(error.message, AppNoticeTone.error);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  void _showMessage(String message, AppNoticeTone tone) {
    if (mounted) {
      AppNotice.show(context, message: message, tone: tone);
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AccountActionScaffold(
      icon: Icons.lock_reset_rounded,
      title: 'نسيت كلمة المرور؟',
      subtitle: 'أدخل بريدك وسنرسل تعليمات الاستعادة دون الكشف عن وجود الحساب.',
      children: [
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'البريد الإلكتروني',
            prefixIcon: Icon(Icons.alternate_email_rounded),
          ),
          onSubmitted: (_) => _submit(),
        ),
        const SizedBox(height: 18),
        FilledButton(
          onPressed: _submitting ? null : _submit,
          child: _submitting
              ? const _ButtonLoader()
              : const Text('إرسال تعليمات الاستعادة'),
        ),
        TextButton(
          onPressed: () => context.go('/login'),
          child: const Text('العودة لتسجيل الدخول'),
        ),
      ],
    );
  }
}

class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({super.key, this.email});

  final String? email;

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  late final TextEditingController _emailController;
  final _passwordController = TextEditingController();
  final _confirmationController = TextEditingController();
  final _otpFocusNode = FocusNode();
  final _otpController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;
  Timer? _cooldownTimer;
  bool _resending = false;
  int _resendCooldown = 0;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.email ?? '');
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmationController.dispose();
    _otpFocusNode.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _resend() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email) || _resending || _resendCooldown > 0) return;
    setState(() => _resending = true);
    try {
      await ref.read(backendRepositoryProvider).forgotPassword(email);
      if (!mounted) return;
      _startResendCooldown();
      _showMessage('تم إرسال رمز جديد إلى بريدك.', AppNoticeTone.success);
    } on ApiException catch (error) {
      _showMessage(error.message, AppNoticeTone.error);
    } finally {
      if (mounted) setState(() => _resending = false);
    }
  }

  void _startResendCooldown() {
    _cooldownTimer?.cancel();
    setState(() => _resendCooldown = 60);
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted || _resendCooldown <= 1) {
        timer.cancel();
        if (mounted) setState(() => _resendCooldown = 0);
        return;
      }
      setState(() => _resendCooldown -= 1);
    });
  }

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    final code = _otpController.text.trim();
    final password = _passwordController.text;
    if (!_isValidEmail(email)) {
      _showMessage('أدخل بريدًا إلكترونيًا صحيحًا.', AppNoticeTone.warning);
      return;
    }
    if (!RegExp(r'^\d{6}$').hasMatch(code)) {
      _showMessage(
        'أدخل رمز التحقق المكوّن من 6 أرقام.',
        AppNoticeTone.warning,
      );
      return;
    }
    final passwordError = _passwordError(password);
    if (passwordError != null) {
      _showMessage(passwordError, AppNoticeTone.warning);
      return;
    }
    if (password != _confirmationController.text) {
      _showMessage('تأكيد كلمة المرور غير مطابق.', AppNoticeTone.warning);
      return;
    }
    if (_submitting) return;
    setState(() => _submitting = true);
    try {
      await ref
          .read(backendRepositoryProvider)
          .resetPassword(email: email, code: code, newPassword: password);
      if (!mounted) return;
      _showMessage(
        'تم تغيير كلمة المرور. سجّل الدخول بالكلمة الجديدة.',
        AppNoticeTone.success,
      );
      context.go('/login');
    } on ApiException catch (error) {
      _showMessage(error.message, AppNoticeTone.error);
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _showMessage(String message, AppNoticeTone tone) {
    if (mounted) AppNotice.show(context, message: message, tone: tone);
  }

  @override
  Widget build(BuildContext context) {
    final email = widget.email;
    return _AccountActionScaffold(
      icon: Icons.lock_reset_rounded,
      title: 'إعادة تعيين كلمة المرور',
      subtitle: email != null
          ? 'أرسلنا رمزًا مكوّنًا من 6 أرقام إلى $email'
          : 'أدخل بريدك ورمز التحقق الذي أرسلناه إليك.',
      children: [
        if (email == null) ...[
          TextField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            textDirection: TextDirection.ltr,
            decoration: const InputDecoration(
              labelText: 'البريد الإلكتروني',
              prefixIcon: Icon(Icons.alternate_email_rounded),
            ),
          ),
          const SizedBox(height: 18),
        ],
        // ─── OTP 6-Box Widget ────────────────────────────────────────
        _OtpBoxField(
          controller: _otpController,
          focusNode: _otpFocusNode,
          onCompleted: (_) => FocusScope.of(context).nextFocus(),
        ),
        const SizedBox(height: 18),
        // ─── Password fields ─────────────────────────────────────────
        TextField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          textDirection: TextDirection.ltr,
          decoration: InputDecoration(
            labelText: 'كلمة المرور الجديدة',
            helperText: '10 أحرف على الأقل وحرف كبير وصغير ورقم.',
            prefixIcon: const Icon(Icons.lock_outline_rounded),
            suffixIcon: IconButton(
              onPressed: () =>
                  setState(() => _obscurePassword = !_obscurePassword),
              icon: Icon(
                _obscurePassword
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
              ),
            ),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _confirmationController,
          obscureText: _obscurePassword,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'تأكيد كلمة المرور',
            prefixIcon: Icon(Icons.verified_user_outlined),
          ),
          onSubmitted: (_) => _submit(),
        ),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: _submitting ? null : _submit,
          icon: _submitting
              ? const _ButtonLoader()
              : const Icon(Icons.check_circle_rounded),
          label: Text(
            _submitting ? 'جارٍ الحفظ...' : 'حفظ كلمة المرور الجديدة',
          ),
        ),
        const SizedBox(height: 14),
        OutlinedButton.icon(
          onPressed: _resending || _resendCooldown > 0 ? null : _resend,
          icon: _resending
              ? const _ButtonLoader()
              : const Icon(Icons.refresh_rounded),
          label: Text(
            _resending
                ? 'جارٍ الإرسال...'
                : _resendCooldown > 0
                ? 'إعادة الإرسال بعد $_resendCooldown ثانية'
                : 'إعادة إرسال الرمز',
          ),
        ),
        TextButton(
          onPressed: () => context.go('/login'),
          child: const Text('العودة لتسجيل الدخول'),
        ),
      ],
    );
  }
}

// ─── Custom 6-box OTP input widget ──────────────────────────────────────────
class _OtpBoxField extends StatefulWidget {
  const _OtpBoxField({
    required this.controller,
    required this.focusNode,
    this.onCompleted,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final ValueChanged<String>? onCompleted;

  @override
  State<_OtpBoxField> createState() => _OtpBoxFieldState();
}

class _OtpBoxFieldState extends State<_OtpBoxField> {
  static const int _length = 6;

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onTextChanged);
  }

  void _onTextChanged() {
    setState(() {});
    if (widget.controller.text.length == _length) {
      widget.onCompleted?.call(widget.controller.text);
    }
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onTextChanged);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final code = widget.controller.text;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        GestureDetector(
          onTap: () => widget.focusNode.requestFocus(),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(_length, (i) {
              final isFilled = i < code.length;
              final isActive = i == code.length && widget.focusNode.hasFocus;
              return AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                margin: const EdgeInsets.symmetric(horizontal: 5),
                width: 46,
                height: 56,
                decoration: BoxDecoration(
                  color: isFilled
                      ? theme.colorScheme.primaryContainer.withValues(
                          alpha: 0.5,
                        )
                      : theme.colorScheme.surfaceContainerLowest,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isActive
                        ? theme.colorScheme.primary
                        : isFilled
                        ? theme.colorScheme.primary.withValues(alpha: 0.5)
                        : theme.colorScheme.outlineVariant,
                    width: isActive ? 2.2 : 1.5,
                  ),
                ),
                alignment: Alignment.center,
                child: isFilled
                    ? Text(
                        code[i],
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: theme.colorScheme.onSurface,
                        ),
                      )
                    : isActive
                    ? Container(
                        width: 2,
                        height: 24,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      )
                    : null,
              );
            }),
          ),
        ),
        // Hidden real text field
        SizedBox(
          height: 0,
          child: Opacity(
            opacity: 0,
            child: TextField(
              controller: widget.controller,
              focusNode: widget.focusNode,
              keyboardType: TextInputType.number,
              autofillHints: const [AutofillHints.oneTimeCode],
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(_length),
              ],
              maxLength: _length,
            ),
          ),
        ),
      ],
    );
  }
}

class _AccountActionScaffold extends StatelessWidget {
  const _AccountActionScaffold({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.children,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    icon,
                    size: 58,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    title,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    subtitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.6,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 28),
                  ...children,
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ButtonLoader extends StatelessWidget {
  const _ButtonLoader();

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: 22,
      height: 22,
      child: CircularProgressIndicator(strokeWidth: 2.5),
    );
  }
}

bool _isValidEmail(String email) {
  return RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email);
}

String? _passwordError(String password) {
  if (password.length < 10) {
    return 'كلمة المرور يجب أن تكون 10 أحرف على الأقل.';
  }
  if (!RegExp('[a-z]').hasMatch(password) ||
      !RegExp('[A-Z]').hasMatch(password) ||
      !RegExp('[0-9]').hasMatch(password)) {
    return 'يجب أن تحتوي كلمة المرور على حرف كبير وصغير ورقم.';
  }
  return null;
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../data/backend_repository.dart';

class VerifyEmailScreen extends ConsumerStatefulWidget {
  const VerifyEmailScreen({super.key, this.email});

  final String? email;

  @override
  ConsumerState<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends ConsumerState<VerifyEmailScreen> {
  final _tokenController = TextEditingController();
  late final TextEditingController _emailController;
  bool _verifying = false;
  bool _resending = false;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.email ?? '');
  }

  @override
  void dispose() {
    _tokenController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    final token = _tokenController.text.trim();
    if (token.length < 20 || _verifying) {
      _showMessage('أدخل رمز التأكيد الكامل الموجود في البريد.');
      return;
    }
    setState(() => _verifying = true);
    try {
      await ref.read(backendRepositoryProvider).verifyEmail(token);
      if (!mounted) {
        return;
      }
      _showMessage('تم تأكيد البريد بنجاح. يمكنك تسجيل الدخول الآن.');
      context.go('/login');
    } on ApiException catch (error) {
      _showMessage(error.message);
    } finally {
      if (mounted) {
        setState(() => _verifying = false);
      }
    }
  }

  Future<void> _resend() async {
    final email = _emailController.text.trim();
    if (!_isValidEmail(email) || _resending) {
      _showMessage('أدخل بريدًا إلكترونيًا صحيحًا.');
      return;
    }
    setState(() => _resending = true);
    try {
      await ref.read(backendRepositoryProvider).resendVerification(email);
      _showMessage('إذا كان الحساب يحتاج تأكيدًا فسيتم إرسال رسالة جديدة.');
    } on ApiException catch (error) {
      _showMessage(error.message);
    } finally {
      if (mounted) {
        setState(() => _resending = false);
      }
    }
  }

  void _showMessage(String message) {
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return _AccountActionScaffold(
      icon: Icons.mark_email_read_outlined,
      title: 'تأكيد البريد الإلكتروني',
      subtitle:
          'ألصق رمز التأكيد الذي وصلك. لا يمكن تسجيل الدخول قبل تأكيد البريد.',
      children: [
        TextField(
          controller: _tokenController,
          minLines: 2,
          maxLines: 4,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'رمز التأكيد',
            prefixIcon: Icon(Icons.key_rounded),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: _verifying ? null : _verify,
          child: _verifying
              ? const _ButtonLoader()
              : const Text('تأكيد البريد'),
        ),
        const SizedBox(height: 28),
        const Divider(),
        const SizedBox(height: 20),
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'البريد الإلكتروني',
            prefixIcon: Icon(Icons.alternate_email_rounded),
          ),
        ),
        const SizedBox(height: 14),
        OutlinedButton(
          onPressed: _resending ? null : _resend,
          child: _resending
              ? const _ButtonLoader()
              : const Text('إعادة إرسال رسالة التأكيد'),
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
      _showMessage('أدخل بريدًا إلكترونيًا صحيحًا.');
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref.read(backendRepositoryProvider).forgotPassword(email);
      if (!mounted) {
        return;
      }
      _showMessage('إذا كان الحساب موجودًا فستصلك تعليمات الاستعادة.');
      context.go('/reset-password?email=${Uri.encodeQueryComponent(email)}');
    } on ApiException catch (error) {
      _showMessage(error.message);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  void _showMessage(String message) {
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
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
  const ResetPasswordScreen({super.key, this.initialToken, this.email});

  final String? initialToken;
  final String? email;

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  late final TextEditingController _tokenController;
  final _passwordController = TextEditingController();
  final _confirmationController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _tokenController = TextEditingController(text: widget.initialToken ?? '');
  }

  @override
  void dispose() {
    _tokenController.dispose();
    _passwordController.dispose();
    _confirmationController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final token = _tokenController.text.trim();
    final password = _passwordController.text;
    if (token.length < 20) {
      _showMessage('أدخل رمز الاستعادة الكامل.');
      return;
    }
    final passwordError = _passwordError(password);
    if (passwordError != null) {
      _showMessage(passwordError);
      return;
    }
    if (password != _confirmationController.text) {
      _showMessage('تأكيد كلمة المرور غير مطابق.');
      return;
    }
    if (_submitting) {
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref
          .read(backendRepositoryProvider)
          .resetPassword(token: token, newPassword: password);
      if (!mounted) {
        return;
      }
      _showMessage('تم تغيير كلمة المرور. سجّل الدخول بالكلمة الجديدة.');
      context.go('/login');
    } on ApiException catch (error) {
      _showMessage(error.message);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  void _showMessage(String message) {
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AccountActionScaffold(
      icon: Icons.password_rounded,
      title: 'إعادة تعيين كلمة المرور',
      subtitle: widget.email == null
          ? 'ألصق رمز الاستعادة واختر كلمة مرور جديدة.'
          : 'تم إرسال التعليمات إلى ${widget.email}. ألصق الرمز واختر كلمة مرور جديدة.',
      children: [
        TextField(
          controller: _tokenController,
          minLines: 2,
          maxLines: 4,
          textDirection: TextDirection.ltr,
          decoration: const InputDecoration(
            labelText: 'رمز الاستعادة',
            prefixIcon: Icon(Icons.key_rounded),
          ),
        ),
        const SizedBox(height: 14),
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
        const SizedBox(height: 18),
        FilledButton(
          onPressed: _submitting ? null : _submit,
          child: _submitting
              ? const _ButtonLoader()
              : const Text('حفظ كلمة المرور الجديدة'),
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

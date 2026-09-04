import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_exception.dart';
import '../../core/ui/app_notice.dart';
import 'session_controller.dart';

import 'package:google_sign_in/google_sign_in.dart';

Future<void> _handleGoogleSignIn(
  BuildContext context,
  WidgetRef ref, {
  String? referralCode,
}) async {
  try {
    final googleSignIn = GoogleSignIn(
      serverClientId:
          '48076310012-d1fp6anhhne69d0lljslt8b86caneets.apps.googleusercontent.com',
      scopes: ['email', 'profile'],
    );
    final account = await googleSignIn.signIn();
    if (account == null) {
      return;
    }
    final auth = await account.authentication;
    final idToken = auth.idToken;
    if (idToken == null || idToken.isEmpty) {
      if (context.mounted) {
        AppNotice.show(
          context,
          title: 'تعذر الدخول بجوجل',
          message: 'لم نتمكن من الحصول على توكن المصادقة الخاص بجوجل.',
          tone: AppNoticeTone.error,
        );
      }
      return;
    }
    await ref
        .read(sessionControllerProvider.notifier)
        .loginWithGoogle(idToken: idToken, referralCode: referralCode);
    if (context.mounted) {
      AppNotice.show(
        context,
        title: 'مرحباً بك!',
        message: 'تم تسجيل الدخول بنجاح بواسطة Google.',
        tone: AppNoticeTone.success,
      );
      context.go('/home');
    }
  } on ApiException catch (error) {
    if (context.mounted) {
      AppNotice.show(
        context,
        title: 'تعذر تسجيل الدخول',
        message: error.message,
        tone: AppNoticeTone.error,
      );
    }
  } catch (error) {
    if (context.mounted) {
      final detail = error.toString();
      final displayMessage = detail.length > 120
          ? '${detail.substring(0, 120)}...'
          : detail;
      AppNotice.show(
        context,
        title: 'تعذر الاتصال بـ Google',
        message: 'خطأ من Google: $displayMessage',
        tone: AppNoticeTone.error,
      );
    }
  }
}

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _submitting) {
      return;
    }
    setState(() => _submitting = true);
    try {
      await ref
          .read(sessionControllerProvider.notifier)
          .login(
            email: _emailController.text,
            password: _passwordController.text,
          );
    } on ApiException catch (error) {
      if (!mounted) {
        return;
      }
      AppNotice.show(
        context,
        title: error.statusCode == 403
            ? 'البريد غير مؤكد'
            : 'تعذر تسجيل الدخول',
        message: error.statusCode == 403
            ? 'أكد بريدك بالكود المرسل أولًا.'
            : error.message,
        tone: error.statusCode == 403
            ? AppNoticeTone.warning
            : AppNoticeTone.error,
      );
      if (error.statusCode == 403) {
        final email = Uri.encodeQueryComponent(_emailController.text.trim());
        context.go('/verify-email?email=$email');
      }
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AuthScaffold(
      title: 'مرحبًا بعودتك',
      subtitle: 'سجّل الدخول للوصول إلى التقارير والتحليلات ورصيدك.',
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              textDirection: TextDirection.ltr,
              decoration: const InputDecoration(
                labelText: 'البريد الإلكتروني',
                prefixIcon: Icon(Icons.alternate_email_rounded),
              ),
              validator: _validateEmail,
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _passwordController,
              obscureText: _obscurePassword,
              textDirection: TextDirection.ltr,
              decoration: InputDecoration(
                labelText: 'كلمة المرور',
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
              validator: (value) =>
                  value == null || value.isEmpty ? 'أدخل كلمة المرور.' : null,
              onFieldSubmitted: (_) => _submit(),
            ),
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child: TextButton(
                onPressed: () => context.go('/forgot-password'),
                child: const Text('نسيت كلمة المرور؟'),
              ),
            ),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2.5),
                    )
                  : const Text('تسجيل الدخول'),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Expanded(child: Divider()),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 12),
                  child: Text('أو', style: TextStyle(color: Colors.grey)),
                ),
                Expanded(child: Divider()),
              ],
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _submitting
                  ? null
                  : () => _handleGoogleSignIn(context, ref),
              icon: const Icon(
                Icons.g_mobiledata_rounded,
                size: 28,
                color: Colors.redAccent,
              ),
              label: const Text('تسجيل الدخول بواسطة Google'),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => context.go('/register'),
              child: const Text('ليس لديك حساب؟ أنشئ حسابًا'),
            ),
          ],
        ),
      ),
    );
  }
}

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _referralCodeController = TextEditingController();
  bool _obscurePassword = true;
  bool _submitting = false;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _referralCodeController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate() || _submitting) {
      return;
    }
    setState(() => _submitting = true);
    try {
      final codeText = _referralCodeController.text.trim();
      final result = await ref
          .read(sessionControllerProvider.notifier)
          .register(
            email: _emailController.text,
            password: _passwordController.text,
            displayName: _nameController.text,
            referralCode: codeText.isEmpty ? null : codeText,
          );
      if (!mounted) {
        return;
      }
      final recoveredPendingAccount = result.weeklyPointsGranted == 0;
      AppNotice.show(
        context,
        title: recoveredPendingAccount
            ? 'استكمال تأكيد الحساب'
            : 'تم إنشاء الحساب',
        message: recoveredPendingAccount
            ? 'الحساب موجود لكنه لم يُؤكد بعد. أرسلنا كودًا جديدًا إلى بريدك دون إنشاء حساب أو رصيد مكرر.'
            : 'أضفنا ${result.weeklyPointsGranted ~/ 100} عملات إلى خطتك المجانية وأرسلنا كود التأكيد إلى بريدك.',
        tone: AppNoticeTone.success,
        duration: const Duration(seconds: 5),
      );
      final email = Uri.encodeQueryComponent(result.email);
      context.go('/verify-email?email=$email');
    } on ApiException catch (error) {
      if (mounted) {
        AppNotice.show(
          context,
          title: 'تعذر إنشاء الحساب',
          message: error.message,
          tone: AppNoticeTone.error,
        );
      }
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _AuthScaffold(
      title: 'إنشاء حساب جديد',
      subtitle: 'ابدأ بالخطة المجانية واحصل على 3 عملات أسبوعيًا.',
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'الاسم الظاهر',
                prefixIcon: Icon(Icons.person_outline_rounded),
              ),
              validator: (value) {
                final cleaned = value?.trim() ?? '';
                return cleaned.length < 2 ? 'الاسم قصير جدًا.' : null;
              },
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              textDirection: TextDirection.ltr,
              decoration: const InputDecoration(
                labelText: 'البريد الإلكتروني',
                prefixIcon: Icon(Icons.alternate_email_rounded),
              ),
              validator: _validateEmail,
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _passwordController,
              obscureText: _obscurePassword,
              textDirection: TextDirection.ltr,
              decoration: InputDecoration(
                labelText: 'كلمة المرور',
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
              validator: _validatePassword,
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _referralCodeController,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                labelText: 'كود الدعوة / الإحالة (اختياري)',
                hintText: 'مثال: SK-7A39B8',
                prefixIcon: Icon(Icons.card_giftcard_rounded),
              ),
            ),
            const SizedBox(height: 22),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2.5),
                    )
                  : const Text('إنشاء الحساب'),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Expanded(child: Divider()),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 12),
                  child: Text('أو', style: TextStyle(color: Colors.grey)),
                ),
                Expanded(child: Divider()),
              ],
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _submitting
                  ? null
                  : () {
                      final code = _referralCodeController.text.trim();
                      _handleGoogleSignIn(
                        context,
                        ref,
                        referralCode: code.isEmpty ? null : code,
                      );
                    },
              icon: const Icon(
                Icons.g_mobiledata_rounded,
                size: 28,
                color: Colors.redAccent,
              ),
              label: const Text('التسجيل المباشر بواسطة Google'),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => context.go('/login'),
              child: const Text('لديك حساب بالفعل؟ سجّل الدخول'),
            ),
          ],
        ),
      ),
    );
  }
}

class _AuthScaffold extends StatelessWidget {
  const _AuthScaffold({
    required this.title,
    required this.subtitle,
    required this.child,
  });

  final String title;
  final String subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
                    Icons.show_chart_rounded,
                    size: 52,
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
                  child,
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

String? _validateEmail(String? value) {
  final email = value?.trim() ?? '';
  final valid = RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email);
  return valid ? null : 'أدخل بريدًا إلكترونيًا صحيحًا.';
}

String? _validatePassword(String? value) {
  final password = value ?? '';
  if (password.length < 10) {
    return 'كلمة المرور يجب أن تكون 10 أحرف على الأقل.';
  }
  if (!RegExp('[a-z]').hasMatch(password) ||
      !RegExp('[A-Z]').hasMatch(password) ||
      !RegExp('[0-9]').hasMatch(password)) {
    return 'يجب أن تحتوي على حرف كبير وصغير ورقم.';
  }
  return null;
}

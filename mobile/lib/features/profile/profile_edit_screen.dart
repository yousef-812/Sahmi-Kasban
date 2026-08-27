import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/avatar_assets.dart';
import '../../core/config/app_config.dart';
import '../../core/network/api_client.dart';
import '../../core/network/api_exception.dart';
import '../../core/theme/theme_controller.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';
import '../auth/session_controller.dart';

final avatarOptionsProvider = FutureProvider.autoDispose<List<AvatarOption>>((
  ref,
) {
  return ref.watch(backendRepositoryProvider).getAvatarOptions();
});

class ProfileEditScreen extends ConsumerStatefulWidget {
  const ProfileEditScreen({super.key});

  @override
  ConsumerState<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends ConsumerState<ProfileEditScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late String _avatarKey;
  bool _saving = false;
  bool _deleting = false;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(sessionControllerProvider).profile;
    _nameController = TextEditingController(text: profile?.displayName ?? '');
    _avatarKey = profile?.avatarKey ?? avatarKeys.first;
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _saving) {
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(sessionControllerProvider.notifier)
          .updateProfile(
            displayName: _nameController.text,
            avatarKey: _avatarKey,
          );
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('تم تحديث الملف الشخصي.')));
      Navigator.of(context).pop();
    } on ApiException catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.message)));
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  Future<void> _deleteAccount() async {
    if (_deleting) {
      return;
    }
    final passwordController = TextEditingController();
    final password = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('حذف الحساب نهائيًا'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'سيتم إلغاء جلساتك وإخفاء البريد والاسم، ولن تتمكن من استعادة الحساب. إذا كان لديك اشتراك مدفوع عبر Google Play، فحذف الحساب لا يلغي التجديد التلقائي؛ ألغِ الاشتراك من Google Play أولًا لتجنب أي تجديد لاحق. أدخل كلمة المرور للتأكيد.',
            ),
            const SizedBox(height: 16),
            TextField(
              controller: passwordController,
              obscureText: true,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'كلمة المرور الحالية',
                prefixIcon: Icon(Icons.lock_outline_rounded),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(dialogContext).colorScheme.error,
            ),
            onPressed: () {
              final value = passwordController.text;
              if (value.isNotEmpty) {
                Navigator.pop(dialogContext, value);
              }
            },
            child: const Text('تأكيد الحذف'),
          ),
        ],
      ),
    );
    passwordController.dispose();
    if (password == null || !mounted) {
      return;
    }

    setState(() => _deleting = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.delete<Map<String, dynamic>>(
        '/profile/me',
        data: <String, dynamic>{'password': password},
      );
      await ref.read(sessionControllerProvider.notifier).logout();
    } on Object catch (error) {
      if (mounted) {
        final message = ref.read(apiClientProvider).mapError(error).message;
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(message)));
      }
    } finally {
      if (mounted) {
        setState(() => _deleting = false);
      }
    }
  }

  Future<void> _copyLegalUrl(String path) async {
    final baseUrl = ref
        .read(appConfigProvider)
        .apiBaseUrl
        .replaceFirst(RegExp(r'/+$'), '');
    await Clipboard.setData(ClipboardData(text: '$baseUrl$path'));
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('تم نسخ الرابط.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final avatars = ref.watch(avatarOptionsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('تعديل الملف الشخصي')),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Center(
                child: CircleAvatar(
                  radius: 52,
                  backgroundImage: AssetImage(avatarAssetPath(_avatarKey)),
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _nameController,
                maxLength: 60,
                decoration: const InputDecoration(
                  labelText: 'الاسم الظاهر',
                  prefixIcon: Icon(Icons.badge_outlined),
                ),
                validator: (value) {
                  final cleaned = value?.trim() ?? '';
                  return cleaned.length < 2 ? 'الاسم قصير جدًا.' : null;
                },
              ),
              const SizedBox(height: 18),
              Text(
                'اختر الصورة الرمزية',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 12),
              avatars.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stackTrace) => Column(
                  children: [
                    const Text('تعذر تحميل قائمة الصور من الخادم.'),
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: () => ref.invalidate(avatarOptionsProvider),
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
                data: (options) => GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                  ),
                  itemCount: options.length,
                  itemBuilder: (context, index) {
                    final option = options[index];
                    final selected = option.key == _avatarKey;
                    return InkWell(
                      borderRadius: BorderRadius.circular(22),
                      onTap: () => setState(() => _avatarKey = option.key),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 180),
                        padding: const EdgeInsets.all(5),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(
                            width: selected ? 3 : 1,
                            color: selected
                                ? Theme.of(context).colorScheme.primary
                                : Theme.of(context).colorScheme.outlineVariant,
                          ),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(17),
                          child: Image.asset(
                            avatarAssetPath(option.key),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 24),
              const _ThemeModeCard(),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _saving ? null : _save,
                icon: _saving
                    ? const SizedBox.square(
                        dimension: 20,
                        child: CircularProgressIndicator(strokeWidth: 2.5),
                      )
                    : const Icon(Icons.save_outlined),
                label: const Text('حفظ التعديلات'),
              ),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'الخصوصية والحساب',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'الصفحات القانونية منشورة على خادم التطبيق ويمكن استخدام روابطها في Google Play.',
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton.icon(
                        onPressed: () => _copyLegalUrl('/privacy'),
                        icon: const Icon(Icons.copy_rounded),
                        label: const Text('نسخ رابط سياسة الخصوصية'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () => _copyLegalUrl('/delete-account'),
                        icon: const Icon(Icons.copy_rounded),
                        label: const Text('نسخ رابط حذف الحساب'),
                      ),
                      const Divider(height: 28),
                      FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: Theme.of(context).colorScheme.error,
                        ),
                        onPressed: _deleting ? null : _deleteAccount,
                        icon: _deleting
                            ? const SizedBox.square(
                                dimension: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                ),
                              )
                            : const Icon(Icons.delete_forever_outlined),
                        label: const Text('حذف الحساب نهائيًا'),
                      ),
                    ],
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

class _ThemeModeCard extends ConsumerWidget {
  const _ThemeModeCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mode = ref.watch(themeControllerProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Icon(Icons.dark_mode_outlined),
                const SizedBox(width: 10),
                Text(
                  'المظهر',
                  style: Theme.of(
                    context,
                  ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text('اختر مظهر التطبيق (دارك أو فاتح).'),
            const SizedBox(height: 12),
            _ModeOption(
              value: AppThemeMode.system,
              selected: mode,
              icon: Icons.brightness_auto_rounded,
              label: 'تلقائي (حسب النظام)',
              onSelected: (value) =>
                  ref.read(themeControllerProvider.notifier).setMode(value),
            ),
            const SizedBox(height: 8),
            _ModeOption(
              value: AppThemeMode.dark,
              selected: mode,
              icon: Icons.dark_mode_rounded,
              label: 'دارك',
              onSelected: (value) =>
                  ref.read(themeControllerProvider.notifier).setMode(value),
            ),
            const SizedBox(height: 8),
            _ModeOption(
              value: AppThemeMode.light,
              selected: mode,
              icon: Icons.light_mode_rounded,
              label: 'فاتح',
              onSelected: (value) =>
                  ref.read(themeControllerProvider.notifier).setMode(value),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModeOption extends StatelessWidget {
  const _ModeOption({
    required this.value,
    required this.selected,
    required this.label,
    required this.icon,
    required this.onSelected,
  });

  final AppThemeMode value;
  final AppThemeMode selected;
  final String label;
  final IconData icon;
  final ValueChanged<AppThemeMode> onSelected;

  @override
  Widget build(BuildContext context) {
    final isSelected = value == selected;
    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: () => onSelected(value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          color: isSelected
              ? Theme.of(context).colorScheme.primaryContainer
              : Colors.transparent,
          border: Border.all(
            color: isSelected
                ? Theme.of(context).colorScheme.primary
                : Theme.of(context).colorScheme.outlineVariant,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: isSelected
                  ? Theme.of(context).colorScheme.onPrimaryContainer
                  : Theme.of(context).colorScheme.onSurfaceVariant,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: TextStyle(
                  fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                ),
              ),
            ),
            if (isSelected)
              Icon(
                Icons.check_circle_rounded,
                color: Theme.of(context).colorScheme.primary,
              ),
          ],
        ),
      ),
    );
  }
}

import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:local_auth/local_auth.dart';

/// خدمة المصادقة البيومترية (Face ID / Fingerprint).
/// تُستخدم لتسريع الدخول بعد أول تسجيل دخول ناجح.
class BiometricService {
  BiometricService({
    LocalAuthentication? localAuth,
    FlutterSecureStorage? storage,
  }) : _localAuth = localAuth ?? LocalAuthentication(),
       _storage = storage ?? const FlutterSecureStorage();

  final LocalAuthentication _localAuth;
  final FlutterSecureStorage _storage;

  static const _enabledKey = 'biometric_enabled';
  static const _credentialKey = 'biometric_credential';

  /// التحقق من توفر المصادقة البيومترية على الجهاز.
  Future<BiometricAvailability> checkAvailability() async {
    try {
      final isDeviceSupported = await _localAuth.isDeviceSupported();
      if (!isDeviceSupported) return BiometricAvailability.notSupported;

      final canCheck = await _localAuth.canCheckBiometrics;
      if (!canCheck) return BiometricAvailability.noBiometrics;

      final availableBiometrics = await _localAuth.getAvailableBiometrics();
      if (availableBiometrics.isEmpty) {
        return BiometricAvailability.noBiometrics;
      }

      return BiometricAvailability.available;
    } on PlatformException catch (e) {
      if (e.code == 'NotAvailable' || e.code == 'PasscodeNotSet') {
        return BiometricAvailability.notSupported;
      }
      return BiometricAvailability.error;
    } catch (_) {
      return BiometricAvailability.error;
    }
  }

  /// تفعيل المصادقة البيومترية وحفظ بيانات الدخول بشكل مشفر.
  Future<bool> enable({
    required String accessToken,
    required String refreshToken,
  }) async {
    try {
      final authenticated = await _localAuth.authenticate(
        localizedReason: 'استخدم بصمتك للدخول السريع إلى سهمي كسبان',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false,
        ),
      );

      if (!authenticated) return false;

      // حفظ البيانات بشكل مشفر في Keychain/Keystore
      await _storage.write(
        key: _credentialKey,
        value: '$accessToken|$refreshToken',
        aOptions: const AndroidOptions(encryptedSharedPreferences: true),
        iOptions: const IOSOptions(
          accessibility: KeychainAccessibility.first_unlock,
        ),
      );
      await _storage.write(key: _enabledKey, value: 'true');
      return true;
    } catch (_) {
      return false;
    }
  }

  /// محاولة الدخول بالمصادقة البيومترية.
  Future<BiometricLoginResult?> tryLogin() async {
    try {
      final isEnabled = await _storage.read(key: _enabledKey);
      if (isEnabled != 'true') return null;

      final authenticated = await _localAuth.authenticate(
        localizedReason: 'المس للبصمة للدخول السريع',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false,
        ),
      );

      if (!authenticated) return null;

      final credential = await _storage.read(key: _credentialKey);
      if (credential == null) return null;

      final parts = credential.split('|');
      if (parts.length != 2) return null;

      return BiometricLoginResult(
        accessToken: parts[0],
        refreshToken: parts[1],
      );
    } catch (_) {
      return null;
    }
  }

  /// تعطيل المصادقة البيومترية وحذف البيانات.
  Future<void> disable() async {
    await _storage.delete(key: _enabledKey);
    await _storage.delete(key: _credentialKey);
  }

  /// هل المصادقة البيومترية مفعلة؟
  Future<bool> isEnabled() async {
    final value = await _storage.read(key: _enabledKey);
    return value == 'true';
  }
}

enum BiometricAvailability { available, noBiometrics, notSupported, error }

class BiometricLoginResult {
  const BiometricLoginResult({
    required this.accessToken,
    required this.refreshToken,
  });

  final String accessToken;
  final String refreshToken;
}

/// Provider للخدمة.
final biometricServiceProvider = Provider<BiometricService>((ref) {
  return BiometricService();
});

/// Provider لحالة توفر المصادقة البيومترية.
final biometricAvailabilityProvider = FutureProvider<BiometricAvailability>((
  ref,
) async {
  return ref.read(biometricServiceProvider).checkAvailability();
});

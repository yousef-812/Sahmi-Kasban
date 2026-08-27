import 'package:flutter/services.dart';

/// نظام اهتزاز موحد — يوفر إحساساً احترافياً لكل تفاعل.
/// يُستخدم في كل الأزرار المهمة بدلاً من استدعاء HapticFeedback مباشرة.
class TerminalHaptics {
  TerminalHaptics._();

  /// نقرة خفيفة — للأزرار العادية والشرائح.
  static Future<void> light() async {
    try {
      await HapticFeedback.lightImpact();
    } catch (_) {
      // تجاهل الأخطاء — الاهتزاز اختياري
    }
  }

  /// نقرة متوسطة — للأزرار المهمة (إضافة، حذف).
  static Future<void> medium() async {
    try {
      await HapticFeedback.mediumImpact();
    } catch (_) {}
  }

  /// نقلة قوية — للإجراءات الحرجة (شراء، بيع، تأكيد).
  static Future<void> heavy() async {
    try {
      await HapticFeedback.heavyImpact();
    } catch (_) {}
  }

  /// اهتزاز نجاح — عند إتمام عملية بنجاح.
  static Future<void> success() async {
    try {
      await HapticFeedback.lightImpact();
      await Future.delayed(const Duration(milliseconds: 80));
      await HapticFeedback.mediumImpact();
    } catch (_) {}
  }

  /// اهتزاز خطأ — عند فشل عملية.
  static Future<void> error() async {
    try {
      await HapticFeedback.heavyImpact();
      await Future.delayed(const Duration(milliseconds: 100));
      await HapticFeedback.heavyImpact();
    } catch (_) {}
  }

  /// اهتزاز اختيار — عند التبديل بين التبويبات أو الاختيارات.
  static Future<void> selection() async {
    try {
      await HapticFeedback.selectionClick();
    } catch (_) {}
  }

  /// نقرات متتالية — للسحب أو التمرير عبر عناصر مهمة.
  static Future<void> tick() async {
    try {
      await HapticFeedback.selectionClick();
    } catch (_) {}
  }
}

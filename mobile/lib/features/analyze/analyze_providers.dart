import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/backend_repository.dart';
import '../../domain/models.dart';

/// Provider للتحليلات الأخيرة — يُستخدم في شاشة التحليل السريع.
final analysisHistoryProvider =
    FutureProvider.autoDispose<AnalysisHistoryResponse>((ref) async {
      final repo = ref.read(backendRepositoryProvider);
      return repo.getAnalysisHistory(limit: 10);
    });

/// Provider للأسهم الشائعة — قائمة ثابتة من أكثر الأسهم تحليلاً.
final popularTickersProvider = Provider<List<String>>((ref) {
  return const [
    'COMI', // البنك التجاري الدولي
    'HRHO', // بلتون المالية / إي أف جي القابضة
    'ETEL', // المصرية للاتصالات
    'FWRY', // فوري
    'ORAS', // أوراسكوم
    'TMGH', // طلعت مصطفى
    'EAST', // الشرقية للدخان
    'ABUK', // أبوقير لليوريا
  ];
});

import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/performance/performance_widgets.dart';

void main() {
  test(
    'performance date formatting never crashes without locale bootstrap',
    () {
      final value = formatPerformanceDate(
        DateTime(2026, 7, 29, 13, 45),
        includeTime: true,
      );

      expect(value, isNotEmpty);
      expect(value, contains('2026'));
    },
  );

  test('performance progress is clamped to the indicator range', () {
    expect(performanceProgress(-5), 0);
    expect(performanceProgress(50), 0.5);
    expect(performanceProgress(125), 1);
  });

  test('performance statuses are presented in Arabic', () {
    expect(performanceStatusLabel('complete'), 'مكتمل');
    expect(performanceStatusLabel('pending_data'), 'بانتظار البيانات');
    expect(performanceStatusLabel('not_started'), 'لم يبدأ التقييم');
  });
}

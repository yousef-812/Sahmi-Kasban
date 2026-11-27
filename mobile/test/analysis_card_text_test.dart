import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/market/analysis_card_text.dart';

void main() {
  test('formatPrice uses two decimals', () {
    expect(formatPrice(149.9976), '150.00');
    expect(formatPrice('143.9558'), '143.96');
    expect(formatPrice(null), isNull);
  });

  test('cleanAnalysisText strips tables, html and marks', () {
    const raw = '''
**القرار:** WATCH
|---|---|
| المحرك | يدعم المراقبة <br> بوضوح |
''';
    final cleaned = cleanAnalysisText(raw);
    expect(cleaned.contains('<br>'), isFalse);
    expect(cleaned.contains('|'), isFalse);
    expect(cleaned.contains('*'), isFalse);
  });

  test('extractHighlights skips internal keys and limits items', () {
    const raw = '''
1. السوق العام مستقر ولا توجد إشارات ضعف واضحة اليوم.
2. وجود resistanceproximitypct عند حد معين غير مفهوم للمستخدم.
3. حجم التداول أعلى من المتوسط مما يدعم الحركة الحالية.
''';
    final items = extractHighlights(raw);
    expect(items.length, 2);
    expect(items.any((i) => i.contains('resistanceproximitypct')), isFalse);
  });
}

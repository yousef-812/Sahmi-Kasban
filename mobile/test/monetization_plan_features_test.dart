import 'package:flutter_test/flutter_test.dart';
import 'package:sahmi_kasban_mobile/features/monetization/monetization_models.dart';

void main() {
  test('MonetizationPlan parses comparison limits and feature list', () {
    final plan = MonetizationPlan.fromJson(<String, dynamic>{
      'code': 'advanced',
      'display_name_ar': 'المتقدمة',
      'weekly_points': 6000,
      'weekly_coins': '60.00',
      'ads_enabled': false,
      'product_id': 'sahmi_advanced_monthly',
      'history_limit': 1000,
      'report_history_days': 365,
      'features': <String>[
        '60 عملة أسبوعيًا',
        'مقارنة حتى 3 أسهم 12 مرة شهريًا',
      ],
      'comparison_monthly_allowance': 12,
      'max_comparison_stocks': 3,
      'priority_level': 2,
      'badge_code': 'advanced',
    });

    expect(plan.features, hasLength(2));
    expect(plan.comparisonMonthlyAllowance, 12);
    expect(plan.maxComparisonStocks, 3);
    expect(plan.priorityLevel, 2);
  });
}

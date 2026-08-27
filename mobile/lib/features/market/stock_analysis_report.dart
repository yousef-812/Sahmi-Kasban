import 'package:flutter/material.dart';

import '../../domain/models.dart';
import '../../widgets/structured_data_card.dart';

class StockAnalysisReport extends StatelessWidget {
  const StockAnalysisReport({required this.analysis, super.key});

  final StockAnalysisResult analysis;

  @override
  Widget build(BuildContext context) {
    final payload = _asMap(analysis.payload);
    final analysisData = _asMap(payload['analysis']);
    final marketData = _asMap(payload['market_data']);
    final engines = _asMap(analysisData['engines']);
    final technical = _engineDetails(engines, 'technical');
    final marketEnvironment = _engineDetails(engines, 'market_environment');
    final risk = _engineDetails(engines, 'risk');
    final scenario = _engineDetails(engines, 'scenario');
    final tradePlan = _asMap(analysisData['trade_plan']);
    final explanation = _text(payload['explanation']);
    final disclaimer = _text(payload['disclaimer']);
    final warnings = _asList(analysisData['warnings'])
        .map((item) => item.toString())
        .where((item) => item.trim().isNotEmpty)
        .toList(growable: false);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _DecisionCard(
          ticker: analysis.ticker,
          signal: _text(analysisData['signal']),
          score: _number(analysisData['final_score']),
          confidence: _number(analysisData['confidence']),
          explanation: explanation,
          cached: analysis.cached,
          chargedCoins: analysis.chargedCoins,
          balanceCoins: analysis.balanceCoins,
        ),
        const SizedBox(height: 12),
        _SectorQualityCard(
          sectorQuality: _asMap(payload['sector_quality']),
          fallbackSector: _text(marketData['sector']).isNotEmpty
              ? _text(marketData['sector'])
              : _text(payload['sector']),
          score: _number(analysisData['final_score']),
        ),
        const SizedBox(height: 12),
        _EngineUpgradesExplanationCard(
          sector: _text(marketData['sector']).isNotEmpty
              ? _text(marketData['sector'])
              : _text(payload['sector']),
        ),
        const SizedBox(height: 12),
        _TradePlanCard(tradePlan: tradePlan, risk: risk),
        const SizedBox(height: 12),
        _TechnicalOverviewCard(
          technical: technical,
          marketEnvironment: marketEnvironment,
          risk: risk,
        ),
        const SizedBox(height: 12),
        _ScenarioCard(scenario: scenario),
        const SizedBox(height: 12),
        _EngineScoresCard(engines: engines),
        const SizedBox(height: 12),
        _MarketDataCard(marketData: marketData, dataAsOf: analysis.dataAsOf),
        if (warnings.isNotEmpty) ...[
          const SizedBox(height: 12),
          _NoticeCard(
            icon: Icons.warning_amber_rounded,
            title: 'تنبيهات التحليل',
            body: warnings.join('\n'),
            isWarning: true,
          ),
        ],
        if (disclaimer.isNotEmpty) ...[
          const SizedBox(height: 12),
          _NoticeCard(
            icon: Icons.info_outline_rounded,
            title: 'تنبيه مهم',
            body: disclaimer,
          ),
        ],
        const SizedBox(height: 12),
        StructuredDataCard(
          title: 'البيانات التقنية الخام',
          data: analysis.payload,
          initiallyExpanded: false,
        ),
      ],
    );
  }
}

class _DecisionCard extends StatelessWidget {
  const _DecisionCard({
    required this.ticker,
    required this.signal,
    required this.score,
    required this.confidence,
    required this.explanation,
    required this.cached,
    required this.chargedCoins,
    required this.balanceCoins,
  });

  final String ticker;
  final String signal;
  final double? score;
  final double? confidence;
  final String explanation;
  final bool cached;
  final String chargedCoins;
  final String balanceCoins;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final normalizedSignal = signal.toUpperCase();
    final signalLabel = _signalLabel(normalizedSignal);
    final signalIcon = switch (normalizedSignal) {
      'BUY' => Icons.trending_up_rounded,
      'SELL' => Icons.trending_down_rounded,
      _ => Icons.horizontal_rule_rounded,
    };
    final background = switch (normalizedSignal) {
      'SELL' => scheme.errorContainer,
      'BUY' => scheme.secondaryContainer,
      _ => scheme.surfaceContainerHighest,
    };

    return Card(
      color: background,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ticker,
                        textDirection: TextDirection.ltr,
                        style: Theme.of(context).textTheme.headlineMedium
                            ?.copyWith(fontWeight: FontWeight.w900),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'القرار الآلي: $signalLabel',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(signalIcon, size: 42),
              ],
            ),
            const SizedBox(height: 16),
            _MetricGrid(
              items: [
                _MetricData(
                  label: 'الدرجة النهائية',
                  value: '${_formatNumber(score)}/100',
                ),
                _MetricData(
                  label: 'الثقة',
                  value: '${_formatNumber(confidence)}%',
                ),
              ],
            ),
            if (score != null) ...[
              const SizedBox(height: 12),
              LinearProgressIndicator(
                value: (score! / 100).clamp(0.0, 1.0).toDouble(),
                minHeight: 8,
                borderRadius: BorderRadius.circular(99),
              ),
            ],
            if (explanation.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(explanation, style: Theme.of(context).textTheme.bodyLarge),
            ],
            const SizedBox(height: 12),
            Text(
              cached
                  ? 'تم عرض تحليل محفوظ سابقًا، ولم يتم خصم عملات جديدة.'
                  : 'تم خصم $chargedCoins عملة بعد نجاح التحليل.',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            Text('الرصيد الحالي: $balanceCoins عملة'),
          ],
        ),
      ),
    );
  }
}

class _TradePlanCard extends StatelessWidget {
  const _TradePlanCard({required this.tradePlan, required this.risk});

  final Map<String, dynamic> tradePlan;
  final Map<String, dynamic> risk;

  @override
  Widget build(BuildContext context) {
    if (tradePlan.isEmpty) {
      return const SizedBox.shrink();
    }
    return _SectionCard(
      icon: Icons.route_rounded,
      title: 'خطة التداول الافتراضية',
      subtitle:
          'الأرقام محسوبة آليًا وفق إعدادات رأس المال والمخاطر داخل النظام.',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'سعر الدخول',
            value: _formatMoney(tradePlan['entry']),
          ),
          _MetricData(
            label: 'وقف الخسارة',
            value: _formatMoney(tradePlan['stop_loss']),
          ),
          _MetricData(
            label: 'الهدف الأول',
            value: _formatMoney(tradePlan['target_1']),
          ),
          _MetricData(
            label: 'الهدف الثاني',
            value: _formatMoney(tradePlan['target_2']),
          ),
          _MetricData(
            label: 'العائد/المخاطرة 1',
            value: _formatNumber(tradePlan['reward_risk_1']),
          ),
          _MetricData(
            label: 'العائد/المخاطرة 2',
            value: _formatNumber(tradePlan['reward_risk_2']),
          ),
          _MetricData(
            label: 'حجم المركز المقترح',
            value: _formatInteger(tradePlan['position_size']),
          ),
          _MetricData(
            label: 'قيمة المركز',
            value: '${_formatNumber(tradePlan['position_value'])} ج.م',
          ),
          _MetricData(
            label: 'مبلغ المخاطرة',
            value: '${_formatNumber(tradePlan['risk_amount'])} ج.م',
          ),
          _MetricData(
            label: 'مستوى المخاطرة',
            value: _riskLabel(_text(risk['risk_level'])),
          ),
        ],
      ),
    );
  }
}

class _TechnicalOverviewCard extends StatelessWidget {
  const _TechnicalOverviewCard({
    required this.technical,
    required this.marketEnvironment,
    required this.risk,
  });

  final Map<String, dynamic> technical;
  final Map<String, dynamic> marketEnvironment;
  final Map<String, dynamic> risk;

  @override
  Widget build(BuildContext context) {
    return _SectionCard(
      icon: Icons.query_stats_rounded,
      title: 'الملخص الفني',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'الاتجاه',
            value: _trendLabel(_text(technical['trend'])),
          ),
          _MetricData(
            label: 'حالة السوق',
            value: _trendLabel(_text(marketEnvironment['regime'])),
          ),
          _MetricData(
            label: 'الإغلاق',
            value: _formatMoney(technical['close']),
          ),
          _MetricData(label: 'RSI', value: _formatNumber(technical['rsi'])),
          _MetricData(
            label: 'متوسط 20 يوم',
            value: _formatMoney(technical['sma_20']),
          ),
          _MetricData(
            label: 'متوسط 50 يوم',
            value: _formatMoney(technical['sma_50']),
          ),
          _MetricData(
            label: 'متوسط 200 يوم',
            value: _formatMoney(technical['sma_200']),
          ),
          _MetricData(
            label: 'MACD',
            value: _formatNumber(technical['macd'], decimals: 4),
          ),
          _MetricData(
            label: 'عائد 20 يوم',
            value: '${_formatNumber(technical['return_20d_pct'])}%',
          ),
          _MetricData(
            label: 'نسبة الحجم',
            value: _formatNumber(technical['volume_ratio']),
          ),
          _MetricData(
            label: 'إجمالي المخاطرة',
            value: '${_formatNumber(risk['total_risk_pct'])}%',
          ),
          _MetricData(
            label: 'ATR',
            value: '${_formatNumber(risk['atr_pct'])}%',
          ),
        ],
      ),
    );
  }
}

class _ScenarioCard extends StatelessWidget {
  const _ScenarioCard({required this.scenario});

  final Map<String, dynamic> scenario;

  @override
  Widget build(BuildContext context) {
    if (scenario.isEmpty) {
      return const SizedBox.shrink();
    }
    final bullish = _asMap(scenario['bullish']);
    final base = _asMap(scenario['base']);
    final bearish = _asMap(scenario['bearish']);
    return _SectionCard(
      icon: Icons.alt_route_rounded,
      title: 'السيناريوهات المحتملة',
      subtitle: 'احتمالات نموذجية وليست ضمانًا لحركة السعر.',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'الصعود',
            value: '${_formatNumber(bullish['probability_pct'])}%',
            subtitle: 'هدف ${_formatMoney(bullish['target'])}',
          ),
          _MetricData(
            label: 'السيناريو الأساسي',
            value: '${_formatNumber(base['probability_pct'])}%',
            subtitle: 'هدف ${_formatMoney(base['target'])}',
          ),
          _MetricData(
            label: 'الهبوط',
            value: '${_formatNumber(bearish['probability_pct'])}%',
            subtitle: 'مستوى ${_formatMoney(bearish['target'])}',
          ),
        ],
      ),
    );
  }
}

class _EngineScoresCard extends StatelessWidget {
  const _EngineScoresCard({required this.engines});

  final Map<String, dynamic> engines;

  @override
  Widget build(BuildContext context) {
    final entries = engines.entries
        .map((entry) => MapEntry(entry.key, _asMap(entry.value)))
        .where((entry) => entry.value.isNotEmpty)
        .toList(growable: false);
    if (entries.isEmpty) {
      return const SizedBox.shrink();
    }
    return _SectionCard(
      icon: Icons.hub_rounded,
      title: 'درجات محركات التحليل',
      child: Column(
        children: [
          for (var index = 0; index < entries.length; index++) ...[
            _EngineScoreRow(
              name: _engineLabel(entries[index].key),
              score: _number(entries[index].value['score']),
              confidence: _number(entries[index].value['confidence']),
            ),
            if (index != entries.length - 1) const Divider(height: 22),
          ],
        ],
      ),
    );
  }
}

class _EngineScoreRow extends StatelessWidget {
  const _EngineScoreRow({
    required this.name,
    required this.score,
    required this.confidence,
  });

  final String name;
  final double? score;
  final double? confidence;

  @override
  Widget build(BuildContext context) {
    final progress = ((score ?? 0) / 100).clamp(0.0, 1.0).toDouble();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                name,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
            Text('${_formatNumber(score)}/100'),
          ],
        ),
        const SizedBox(height: 6),
        LinearProgressIndicator(
          value: progress,
          minHeight: 7,
          borderRadius: BorderRadius.circular(99),
        ),
        if (confidence != null) ...[
          const SizedBox(height: 5),
          Text(
            'الثقة ${_formatNumber(confidence)}%',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ],
    );
  }
}

class _MarketDataCard extends StatelessWidget {
  const _MarketDataCard({required this.marketData, required this.dataAsOf});

  final Map<String, dynamic> marketData;
  final DateTime dataAsOf;

  @override
  Widget build(BuildContext context) {
    final provider = _text(marketData['provider']);
    return _SectionCard(
      icon: Icons.storage_rounded,
      title: 'بيانات السوق المستخدمة',
      child: _MetricGrid(
        items: [
          _MetricData(
            label: 'المصدر',
            value: provider.toLowerCase() == 'tradingview'
                ? 'TradingView'
                : provider,
          ),
          _MetricData(
            label: 'عدد الشموع',
            value: _formatInteger(marketData['candle_count']),
          ),
          _MetricData(
            label: 'الإطار الزمني',
            value: _intervalLabel(_text(marketData['interval'])),
          ),
          _MetricData(
            label: 'الفترة',
            value: _periodLabel(_text(marketData['period'])),
          ),
          _MetricData(
            label: 'آخر تحديث للبيانات',
            value: _formatArabicDate(dataAsOf),
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.icon,
    required this.title,
    required this.child,
    this.subtitle,
  });

  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(icon),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            if (subtitle case final text?) ...[
              const SizedBox(height: 6),
              Text(text, style: Theme.of(context).textTheme.bodySmall),
            ],
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}

class _MetricGrid extends StatelessWidget {
  const _MetricGrid({required this.items});

  final List<_MetricData> items;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final useTwoColumns = constraints.maxWidth >= 320;
        final width = useTwoColumns
            ? (constraints.maxWidth - 10) / 2
            : constraints.maxWidth;
        return Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            for (final item in items)
              SizedBox(
                width: width,
                child: _MetricTile(data: item),
              ),
          ],
        );
      },
    );
  }
}

class _MetricData {
  const _MetricData({required this.label, required this.value, this.subtitle});

  final String label;
  final String value;
  final String? subtitle;
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({required this.data});

  final _MetricData data;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minHeight: 88),
      padding: const EdgeInsets.all(13),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(data.label, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 6),
          Text(
            data.value.isEmpty ? '—' : data.value,
            textDirection: _containsLatinOrNumber(data.value)
                ? TextDirection.ltr
                : TextDirection.rtl,
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
          if (data.subtitle case final subtitle?) ...[
            const SizedBox(height: 4),
            Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
          ],
        ],
      ),
    );
  }
}

class _NoticeCard extends StatelessWidget {
  const _NoticeCard({
    required this.icon,
    required this.title,
    required this.body,
    this.isWarning = false,
  });

  final IconData icon;
  final String title;
  final String body;
  final bool isWarning;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      color: isWarning ? scheme.errorContainer : scheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  Text(body),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

Map<String, dynamic> _asMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return value.map((key, item) => MapEntry(key.toString(), item));
  }
  return const {};
}

List<Object?> _asList(Object? value) {
  return value is List ? value.cast<Object?>() : const [];
}

Map<String, dynamic> _engineDetails(Map<String, dynamic> engines, String key) {
  return _asMap(_asMap(engines[key])['details']);
}

double? _number(Object? value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '');
}

String _text(Object? value) => value?.toString().trim() ?? '';

String _formatNumber(Object? value, {int decimals = 2}) {
  final number = _number(value);
  if (number == null) {
    return '—';
  }
  var text = number.toStringAsFixed(decimals);
  if (text.contains('.')) {
    text = text.replaceFirst(RegExp(r'0+$'), '');
    text = text.replaceFirst(RegExp(r'\.$'), '');
  }
  return text;
}

String _formatInteger(Object? value) {
  final number = _number(value);
  return number == null ? '—' : number.round().toString();
}

String _formatMoney(Object? value) {
  final formatted = _formatNumber(value, decimals: 4);
  return formatted == '—' ? formatted : '$formatted ج.م';
}

String _signalLabel(String signal) {
  return switch (signal) {
    'BUY' => 'شراء مشروط',
    'SELL' => 'بيع أو خروج',
    'HOLD' => 'انتظار',
    _ => signal.isEmpty ? 'غير محدد' : signal,
  };
}

String _trendLabel(String value) {
  return switch (value.toLowerCase()) {
    'bullish' => 'صاعد',
    'weak_bullish' => 'صاعد ضعيف',
    'uptrend' => 'اتجاه صاعد',
    'bearish' => 'هابط',
    'weak_bearish' => 'هابط ضعيف',
    'downtrend' => 'اتجاه هابط',
    'sideways' || 'neutral' => 'عرضي / محايد',
    _ => value.isEmpty ? '—' : value,
  };
}

String _riskLabel(String value) {
  return switch (value.toLowerCase()) {
    'low' => 'منخفض',
    'medium' => 'متوسط',
    'high' => 'مرتفع',
    _ => value.isEmpty ? '—' : value,
  };
}

String _engineLabel(String key) {
  return switch (key) {
    'stock_qualification' => 'تأهيل السهم',
    'market_environment' => 'بيئة السوق',
    'technical' => 'التحليل الفني',
    'smc' => 'هيكل السوق SMC',
    'multi_timeframe' => 'تعدد الأطر الزمنية',
    'quantitative' => 'التحليل الكمي',
    'risk' => 'إدارة المخاطر',
    'scenario' => 'السيناريوهات',
    _ => key,
  };
}

String _intervalLabel(String value) {
  return switch (value) {
    '1d' => 'يومي',
    '1h' => 'ساعة',
    '1w' => 'أسبوعي',
    _ => value.isEmpty ? '—' : value,
  };
}

String _periodLabel(String value) {
  return switch (value) {
    '1y' => 'سنة',
    '6mo' => '6 أشهر',
    '3mo' => '3 أشهر',
    _ => value.isEmpty ? '—' : value,
  };
}

String _formatArabicDate(DateTime value) {
  const months = [
    'يناير',
    'فبراير',
    'مارس',
    'أبريل',
    'مايو',
    'يونيو',
    'يوليو',
    'أغسطس',
    'سبتمبر',
    'أكتوبر',
    'نوفمبر',
    'ديسمبر',
  ];
  final local = value.toLocal();
  final hour = local.hour == 0
      ? 12
      : (local.hour > 12 ? local.hour - 12 : local.hour);
  final minute = local.minute.toString().padLeft(2, '0');
  final period = local.hour >= 12 ? 'م' : 'ص';
  return '${local.day} ${months[local.month - 1]} ${local.year}، $hour:$minute $period';
}

bool _containsLatinOrNumber(String value) {
  return RegExp(r'[A-Za-z0-9]').hasMatch(value);
}

class _EngineUpgradesExplanationCard extends StatelessWidget {
  const _EngineUpgradesExplanationCard({required this.sector});

  final String sector;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.stars_rounded, color: Colors.amber, size: 22),
                const SizedBox(width: 8),
                Text(
                  'مواصفات المحرك ومؤشرات المؤسسات',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (sector.isNotEmpty)
                  Chip(
                    avatar: const Icon(Icons.category_outlined, size: 14),
                    label: Text('القطاع: $sector'),
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            _FeatureRow(
              icon: Icons.show_chart_rounded,
              title: 'مؤشر VWAP المؤسسي',
              desc:
                  'حساب متوسط السعر المرجح بحجم التداول لكشف دخول وصانع السوق.',
            ),
            const SizedBox(height: 8),
            _FeatureRow(
              icon: Icons.shield_rounded,
              title: 'محرك زخم القطاع (Sector Engine)',
              desc:
                  'حماية إشارات الشراء وضمان عدم الدخول في سهم جيد داخل قطاع هابط.',
            ),
            const SizedBox(height: 8),
            _FeatureRow(
              icon: Icons.auto_graph_rounded,
              title: 'وقف الخسارة التكيفي (Adaptive ATR)',
              desc:
                  'متابعة الأرباح ووقف الخسارة ديناميكياً بحسب نسبة تذبذب السهم.',
            ),
            const SizedBox(height: 8),
            _FeatureRow(
              icon: Icons.account_balance_wallet_rounded,
              title: 'حماية التكاليف والانزلاق (0.3% Guard)',
              desc:
                  'خصم تلقائي 0.3% لعمولات البورصة والانزلاق السعري لنتائج واقعية 100%.',
            ),
          ],
        ),
      ),
    );
  }
}

class _FeatureRow extends StatelessWidget {
  const _FeatureRow({
    required this.icon,
    required this.title,
    required this.desc,
  });

  final IconData icon;
  final String title;
  final String desc;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: theme.colorScheme.primary),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: theme.textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                desc,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _SectorQualityCard extends StatelessWidget {
  const _SectorQualityCard({
    required this.sectorQuality,
    required this.fallbackSector,
    required this.score,
  });

  final Map<String, dynamic> sectorQuality;
  final String fallbackSector;
  final double? score;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currentScore = score;
    final sectorName = _text(sectorQuality['sector_name']).isNotEmpty
        ? _text(sectorQuality['sector_name'])
        : (fallbackSector.isNotEmpty ? fallbackSector : 'عام');

    final qualityLabel = _text(sectorQuality['quality_label']).isNotEmpty
        ? _text(sectorQuality['quality_label'])
        : ((currentScore ?? 0) >= 75
              ? 'متفوق على قطاع $sectorName'
              : ((currentScore ?? 0) >= 50
                    ? 'متوافق مع قطاع $sectorName'
                    : 'أقل من متوسط قطاع $sectorName'));

    final qualityStatus = _text(sectorQuality['quality_status']).isNotEmpty
        ? _text(sectorQuality['quality_status'])
        : ((currentScore ?? 0) >= 75
              ? 'outperforming'
              : ((currentScore ?? 0) >= 50 ? 'in_line' : 'underperforming'));

    final summaryAr = _text(sectorQuality['summary_ar']).isNotEmpty
        ? _text(sectorQuality['summary_ar'])
        : 'أداء وتقييم السهم بالمقارنة مع معايير ومتوسط حركة قطاع $sectorName.';

    final return20d = _number(sectorQuality['return_20d_pct']);
    final sectorTrendAr = _text(sectorQuality['sector_trend_ar']).isNotEmpty
        ? _text(sectorQuality['sector_trend_ar'])
        : ((return20d ?? 0) >= 0 ? 'صاعد 📈' : 'هابط 📉');

    final badgeColor = switch (qualityStatus) {
      'outperforming' => Colors.green.shade700,
      'in_line' => Colors.blue.shade700,
      _ => Colors.orange.shade800,
    };

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Icon(
                  Icons.pie_chart_outline_rounded,
                  color: Colors.amber,
                  size: 24,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'جودة السهم مقابل القطاع',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: badgeColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: badgeColor.withValues(alpha: 0.4),
                    ),
                  ),
                  child: Text(
                    qualityLabel,
                    style: TextStyle(
                      color: badgeColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              summaryAr,
              style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
            ),
            const SizedBox(height: 14),
            _MetricGrid(
              items: [
                _MetricData(label: 'اسم القطاع', value: sectorName),
                _MetricData(label: 'اتجاه القطاع', value: sectorTrendAr),
                _MetricData(
                  label: 'درجة التقييم النسبي',
                  value: currentScore != null
                      ? '${currentScore.toStringAsFixed(1)}/100'
                      : '—',
                ),
                if (return20d != null && return20d != 0)
                  _MetricData(
                    label: 'عائد السهم (20 يوم)',
                    value: '${_formatNumber(return20d)}%',
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

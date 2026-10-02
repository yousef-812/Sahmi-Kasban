import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;

import '../../core/network/api_exception.dart';
import 'session_replay_models.dart';
import 'session_replay_repository.dart';

/// محاكاة جلسة كاملة كأنها فيديو: حركة لحظية (tick) داخل كل شمعة.
///
/// الشموع (O/H/L/C) حقيقية من `GET /market/session-replay` بفاصل 1m.
/// الحركة *داخل* الشمعة محاكاة تقديرية على مسار O → H → L → C
/// (للشمعة الهابطة) أو O → L → H → C (للصاعدة)، لأن المزود لا يعطي
/// تيكات حقيقية. المستخدم يشاهد الجلسة من الافتتاح للإغلاق، يوقف
/// عند أي نقطة ويدرسها بالكروسهير، ويكمل من نفس النقطة.
class SessionReplayScreen extends ConsumerStatefulWidget {
  const SessionReplayScreen({super.key, this.initialTicker});

  final String? initialTicker;

  @override
  ConsumerState<SessionReplayScreen> createState() =>
      _SessionReplayScreenState();
}

/// نقطة حركة واحدة داخل شمعة.
class _Tick {
  const _Tick({
    required this.time,
    required this.price,
    required this.tickVolume,
    required this.candleIndex,
    required this.isCandleStart,
  });

  final DateTime time;
  final double price;
  final double tickVolume;
  final int candleIndex;
  final bool isCandleStart;
}

class _SessionReplayScreenState extends ConsumerState<SessionReplayScreen> {
  static const _speeds = <int>[1, 2, 4, 8, 16];
  static const _intervals = <String>['1m', '5m', '15m', '30m'];

  /// عدد نقاط الحركة داخل كل شمعة.
  static const _ticksPerCandle = 12;

  /// سرعة الأساس: تيك/ثانية عند 1x (الجلسة الكاملة ≈ 9 دقائق).
  static const _baseTicksPerSecond = 5.0;
  static const _frameMs = 200;

  late final TextEditingController _tickerController;
  String _interval = '1m';
  int _speedIndex = 0;

  bool _loading = false;
  String? _error;
  SessionReplay? _replay;
  List<_Tick> _ticks = const [];

  /// مؤشر آخر تيك ظاهر.
  int _tickPos = 0;
  bool _playing = false;
  Timer? _timer;

  /// نقطة الكروسهير للدراسة (إحداثيات داخل مساحة الشارت).
  Offset? _cross;

  @override
  void initState() {
    super.initState();
    _tickerController = TextEditingController(
      text: (widget.initialTicker ?? 'COMI').toUpperCase(),
    );
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _load();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _tickerController.dispose();
    super.dispose();
  }

  int get _speed => _speeds[_speedIndex];

  Future<void> _load() async {
    final ticker = _tickerController.text.trim().toUpperCase();
    if (ticker.isEmpty) return;
    _stop();
    setState(() {
      _loading = true;
      _error = null;
      _cross = null;
    });
    try {
      final replay = await ref
          .read(sessionReplayRepositoryProvider)
          .fetch(ticker: ticker, interval: _interval);
      if (!mounted) return;
      setState(() {
        _replay = replay;
        _ticks = _buildTicks(replay.candles);
        _tickPos = 0;
        _loading = false;
      });
    } on Object catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error =
            error is ApiException ? error.message : 'تعذر تحميل شموع الجلسة.';
      });
    }
  }

  /// يبني مسار الحركة اللحظية لكل شمعة.
  static List<_Tick> _buildTicks(
    List<ReplayCandle> candles, [
    int perCandle = _ticksPerCandle,
  ]) {
    final out = <_Tick>[];
    for (var i = 0; i < candles.length; i++) {
      final candle = candles[i];
      final next = i + 1 < candles.length
          ? candles[i + 1].timestamp
          : candle.timestamp.add(const Duration(minutes: 1));
      var span = next.difference(candle.timestamp);
      if (span.inSeconds <= 0) span = const Duration(minutes: 1);
      // مسار الحركة: هابطة O→H→L→C، صاعدة O→L→H→C.
      final path = candle.close >= candle.open
          ? <double>[candle.open, candle.low, candle.high, candle.close]
          : <double>[candle.open, candle.high, candle.low, candle.close];
      const legs = 3;
      final perLeg = (perCandle / legs).ceil();
      var step = 0;
      for (var leg = 0; leg < legs; leg++) {
        final from = path[leg];
        final to = path[leg + 1];
        for (var k = 0; k < perLeg && step < perCandle; k++, step++) {
          final f = perLeg == 1 ? 1.0 : (k + 1) / perLeg;
          out.add(
            _Tick(
              time: candle.timestamp.add(
                Duration(
                  milliseconds:
                      (span.inMilliseconds * (step + 1) ~/ perCandle),
                ),
              ),
              price: from + (to - from) * f,
              tickVolume: candle.volume / perCandle,
              candleIndex: i,
              isCandleStart: step == 0,
            ),
          );
        }
      }
    }
    return out;
  }

  void _start() {
    if (_ticks.isEmpty) return;
    if (_tickPos >= _ticks.length - 1) {
      setState(() => _tickPos = 0);
    }
    _timer?.cancel();
    final step = (_baseTicksPerSecond * _frameMs / 1000 * _speed)
        .round()
        .clamp(1, 1 << 20);
    _timer = Timer.periodic(const Duration(milliseconds: _frameMs), (_) {
      if (!mounted) return;
      if (_tickPos >= _ticks.length - 1) {
        _stop();
        return;
      }
      setState(() {
        _tickPos = (_tickPos + step).clamp(0, _ticks.length - 1);
      });
    });
    setState(() => _playing = true);
  }

  void _stop() {
    _timer?.cancel();
    _timer = null;
    if (mounted && _playing) setState(() => _playing = false);
  }

  void _toggle() {
    if (_playing) {
      _stop();
    } else {
      _start();
    }
  }

  /// قفزة لأول تيك في شمعة نسبية من الشمعة الحالية.
  void _jumpCandle(int delta) {
    if (_ticks.isEmpty) return;
    _stop();
    final currentCandle = _ticks[_tickPos].candleIndex;
    final target = (currentCandle + delta).clamp(
      0,
      _replay!.candles.length - 1,
    );
    final idx = _ticks.indexWhere((t) => t.candleIndex == target);
    setState(() => _tickPos = idx < 0 ? _tickPos : idx);
  }

  @override
  Widget build(BuildContext context) {
    final replay = _replay;
    return Scaffold(
      appBar: AppBar(
        title: const Text('محاكاة الجلسة — فيديو الشموع'),
        actions: [
          IconButton(
            tooltip: 'إعادة التحميل',
            onPressed: _loading ? null : _load,
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        children: [
          _PickerCard(
            controller: _tickerController,
            interval: _interval,
            intervals: _intervals,
            loading: _loading,
            onIntervalChanged: (value) {
              if (value != null) setState(() => _interval = value);
            },
            onLoad: _load,
          ),
          const SizedBox(height: 12),
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(32),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (_error != null)
            _ErrorCard(message: _error!, onRetry: _load)
          else if (replay == null || _ticks.isEmpty)
            const _EmptyCard()
          else ...[
            _StatsBar(
              replay: replay,
              tick: _ticks[_tickPos],
              tickPos: _tickPos,
              totalTicks: _ticks.length,
            ),
            const SizedBox(height: 8),
            _ChartCard(
              replay: replay,
              ticks: _ticks,
              tickPos: _tickPos,
              cross: _cross,
              onCross: (offset) => setState(() => _cross = offset),
              onScrub: (tickIndex) {
                _stop();
                setState(() {
                  _tickPos = tickIndex;
                  _cross = null;
                });
              },
            ),
            const SizedBox(height: 8),
            _ControlsRow(
              playing: _playing,
              onToggle: _toggle,
              onRestart: () {
                _stop();
                setState(() {
                  _tickPos = 0;
                  _cross = null;
                });
              },
              onBackCandle: () => _jumpCandle(-1),
              onForwardCandle: () => _jumpCandle(1),
              onReplay: () {
                setState(() {
                  _tickPos = 0;
                  _cross = null;
                });
                _start();
              },
            ),
            const SizedBox(height: 8),
            Wrap(
              alignment: WrapAlignment.center,
              spacing: 8,
              children: [
                for (var i = 0; i < _speeds.length; i++)
                  ChoiceChip(
                    label: Text('${_speeds[i]}x'),
                    selected: i == _speedIndex,
                    onSelected: (_) {
                      setState(() => _speedIndex = i);
                      if (_playing) _start();
                    },
                  ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              'السرعة ${_speed}x من إيقاع الجلسة • اسحب على الشارت للدراسة ثم أكمل التشغيل من نفس النقطة',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 4),
            Text(
              'الشموع حقيقية (1m) — الحركة داخل الشمعة محاكاة تقديرية بين O/H/L/C',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                    fontSize: 11,
                  ),
            ),
          ],
        ],
      ),
    );
  }
}

/// شريط السعر الحالي والتغير وساعة الجلسة.
class _StatsBar extends StatelessWidget {
  const _StatsBar({
    required this.replay,
    required this.tick,
    required this.tickPos,
    required this.totalTicks,
  });

  final SessionReplay replay;
  final _Tick tick;
  final int tickPos;
  final int totalTicks;

  @override
  Widget build(BuildContext context) {
    final sessionOpen = replay.candles.first.open;
    final changePct =
        sessionOpen == 0 ? 0.0 : ((tick.price - sessionOpen) / sessionOpen) * 100;
    final positive = changePct >= 0;
    final color = positive ? const Color(0xFF26A69A) : const Color(0xFFEF5350);
    final progress = totalTicks <= 1 ? 0.0 : tickPos / (totalTicks - 1);
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _Stat(
                  label: 'السعر',
                  value: tick.price.toStringAsFixed(2),
                  color: color,
                ),
                _Stat(
                  label: 'تغير الجلسة',
                  value:
                      '${positive ? '+' : ''}${changePct.toStringAsFixed(2)}%',
                  color: color,
                ),
                _Stat(
                  label: 'ساعة الجلسة',
                  value: DateFormat('HH:mm:ss').format(tick.time),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: progress.clamp(0.0, 1.0),
                minHeight: 6,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value, this.color});

  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 2),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
                color: color,
              ),
        ),
      ],
    );
  }
}

/// كارت الشارت: شموع + فوليوم + محور أسعار + محور زمني + كروسهير.
class _ChartCard extends StatelessWidget {
  const _ChartCard({
    required this.replay,
    required this.ticks,
    required this.tickPos,
    required this.cross,
    required this.onCross,
    required this.onScrub,
  });

  final SessionReplay replay;
  final List<_Tick> ticks;
  final int tickPos;
  final Offset? cross;
  final ValueChanged<Offset> onCross;
  final ValueChanged<int> onScrub;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      color: const Color(0xFF131722),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(8, 8, 8, 4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _LegendBar(
              replay: replay,
              ticks: ticks,
              tickPos: tickPos,
              cross: cross,
            ),
            const SizedBox(height: 4),
            LayoutBuilder(
              builder: (context, constraints) {
                final size = Size(constraints.maxWidth, 300);
                return GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTapDown: (d) => onCross(d.localPosition),
                  onPanUpdate: (d) => onCross(d.localPosition),
                  child: CustomPaint(
                    size: size,
                    painter: _TvChartPainter(
                      candles: replay.candles,
                      ticks: ticks,
                      tickPos: tickPos,
                      cross: cross,
                      chartSize: size,
                    ),
                  ),
                );
              },
            ),
            Slider(
              value: tickPos.toDouble(),
              min: 0,
              max: (ticks.length - 1).toDouble(),
              onChanged: (value) => onScrub(value.round()),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                'اسحب المؤشر للتنقل في زمن الجلسة — التشغيل يكمل من حيث تقف',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: Colors.white60,
                  fontSize: 11,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// سطر OHLC: يعرض بيانات الشمعة تحت الكروسهير أو الشمعة الجارية.
class _LegendBar extends StatelessWidget {
  const _LegendBar({
    required this.replay,
    required this.ticks,
    required this.tickPos,
    required this.cross,
  });

  final SessionReplay replay;
  final List<_Tick> ticks;
  final int tickPos;
  final Offset? cross;

  @override
  Widget build(BuildContext context) {
    var candleIndex = ticks[tickPos].candleIndex;
    // تقدير الشمعة تحت الكروسهير من موضعه الأفقي (يُضبط بدقة في الرسام).
    if (cross != null) {
      final plotW = MediaQuery.of(context).size.width - 32 - 16 - 56;
      final n = replay.candles.length;
      final slot = plotW / n;
      final estimated = (cross!.dx - 8) ~/ slot;
      if (estimated >= 0 && estimated < n) candleIndex = estimated;
    }
    final candle = replay.candles[candleIndex.clamp(0, replay.candles.length - 1)];
    final up = candle.close >= candle.open;
    final color = up ? const Color(0xFF26A69A) : const Color(0xFFEF5350);
    String fmt(double v) => v.toStringAsFixed(2);
    return Wrap(
      crossAxisAlignment: WrapCrossAlignment.center,
      spacing: 10,
      children: [
        Text(
          replay.ticker,
          textDirection: TextDirection.ltr,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w800,
          ),
        ),
        Text(
          DateFormat('HH:mm').format(candle.timestamp),
          textDirection: TextDirection.ltr,
          style: const TextStyle(color: Colors.white60, fontSize: 12),
        ),
        _Ohlc(label: 'O', value: fmt(candle.open)),
        _Ohlc(label: 'H', value: fmt(candle.high)),
        _Ohlc(label: 'L', value: fmt(candle.low)),
        _Ohlc(label: 'C', value: fmt(candle.close), color: color),
      ],
    );
  }
}

class _Ohlc extends StatelessWidget {
  const _Ohlc({required this.label, required this.value, this.color});

  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Text.rich(
      textDirection: TextDirection.ltr,
      TextSpan(
        children: [
          TextSpan(
            text: '$label ',
            style: const TextStyle(color: Colors.white38, fontSize: 11),
          ),
          TextSpan(
            text: value,
            style: TextStyle(
              color: color ?? Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class _ControlsRow extends StatelessWidget {
  const _ControlsRow({
    required this.playing,
    required this.onToggle,
    required this.onRestart,
    required this.onBackCandle,
    required this.onForwardCandle,
    required this.onReplay,
  });

  final bool playing;
  final VoidCallback onToggle;
  final VoidCallback onRestart;
  final VoidCallback onBackCandle;
  final VoidCallback onForwardCandle;
  final VoidCallback onReplay;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          tooltip: 'من البداية',
          onPressed: onRestart,
          icon: const Icon(Icons.skip_previous_rounded),
        ),
        IconButton(
          tooltip: 'شمعة للخلف',
          onPressed: onBackCandle,
          icon: const Icon(Icons.chevron_left_rounded),
        ),
        FilledButton.icon(
          onPressed: onToggle,
          icon: Icon(playing ? Icons.pause_rounded : Icons.play_arrow_rounded),
          label: Text(playing ? 'إيقاف مؤقت' : 'تشغيل'),
        ),
        IconButton(
          tooltip: 'شمعة للأمام',
          onPressed: onForwardCandle,
          icon: const Icon(Icons.chevron_right_rounded),
        ),
        IconButton(
          tooltip: 'إعادة من الأول',
          onPressed: onReplay,
          icon: const Icon(Icons.replay_rounded),
        ),
      ],
    );
  }
}

class _PickerCard extends StatelessWidget {
  const _PickerCard({
    required this.controller,
    required this.interval,
    required this.intervals,
    required this.loading,
    required this.onIntervalChanged,
    required this.onLoad,
  });

  final TextEditingController controller;
  final String interval;
  final List<String> intervals;
  final bool loading;
  final ValueChanged<String?> onIntervalChanged;
  final VoidCallback onLoad;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                textDirection: TextDirection.ltr,
                textCapitalization: TextCapitalization.characters,
                decoration: const InputDecoration(
                  labelText: 'رمز السهم',
                  hintText: 'COMI',
                  isDense: true,
                ),
                onSubmitted: (_) => onLoad(),
              ),
            ),
            const SizedBox(width: 12),
            DropdownButton<String>(
              value: interval,
              items: [
                for (final item in intervals)
                  DropdownMenuItem(value: item, child: Text(item)),
              ],
              onChanged: onIntervalChanged,
            ),
            const SizedBox(width: 12),
            FilledButton(
              onPressed: loading ? null : onLoad,
              child: const Text('تحميل الجلسة'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Icon(Icons.cloud_off_rounded, size: 40),
            const SizedBox(height: 8),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  const _EmptyCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.smart_display_outlined, size: 48),
            SizedBox(height: 12),
            Text(
              'حمّل الجلسة الأخيرة وشاهدها كفيديو: حركة لحظية داخل كل شمعة من الافتتاح حتى الإغلاق.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

/// رسام شارت بروح TradingView: شبكة + شموع + فوليوم +
/// محور أسعار + محور زمني + خط السعر الأخير + كروسهير.
class _TvChartPainter extends CustomPainter {
  _TvChartPainter({
    required this.candles,
    required this.ticks,
    required this.tickPos,
    required this.cross,
    required this.chartSize,
  });

  final List<ReplayCandle> candles;
  final List<_Tick> ticks;
  final int tickPos;
  final Offset? cross;
  final Size chartSize;

  static const _priceScaleW = 56.0;
  static const _timeScaleH = 22.0;
  static const _pad = 8.0;

  @override
  void paint(Canvas canvas, Size size) {
    if (candles.isEmpty || ticks.isEmpty) return;
    final tick = ticks[tickPos.clamp(0, ticks.length - 1)];
    final currentCandle = tick.candleIndex;

    final plotW = size.width - _priceScaleW - _pad;
    final plotH = size.height - _timeScaleH;
    const volumeH = 44.0;
    final priceH = plotH - volumeH - 6;

    // النطاق السعري من الشموع الظاهرة + التيك الحالي.
    var minP = candles.first.low;
    var maxP = candles.first.high;
    for (var i = 0; i <= currentCandle; i++) {
      final c = candles[i];
      if (c.low < minP) minP = c.low;
      if (c.high > maxP) maxP = c.high;
    }
    if (tick.price < minP) minP = tick.price;
    if (tick.price > maxP) maxP = tick.price;
    var range = maxP - minP;
    if (range <= 0) range = 1;
    final padR = range * 0.07;
    minP -= padR;
    maxP += padR;
    range = maxP - minP;

    double py(double price) => priceH - ((price - minP) / range) * priceH;
    final n = candles.length;
    final slot = plotW / n;
    double cx(int i) => slot * i + slot / 2;

    const up = Color(0xFF26A69A);
    const down = Color(0xFFEF5350);
    const grid = Color(0x1FFFFFFF);
    const labelStyle = TextStyle(color: Color(0xFF787B86), fontSize: 10);

    void text(String s, Offset at) {
      final tp = TextPainter(
        text: TextSpan(text: s, style: labelStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, at);
    }

    // شبكة أفقية + أسعار (5 مستويات).
    for (var i = 0; i <= 4; i++) {
      final price = maxP - (range * i / 4);
      final y = py(price);
      canvas.drawLine(
        Offset(0, y),
        Offset(plotW, y),
        Paint()..color = grid,
      );
      text(
        price.toStringAsFixed(2),
        Offset(plotW + 4, (y - 7).clamp(0.0, priceH - 12)),
      );
    }
    // شبكة عمودية كل 30 دقيقة + محور زمني.
    var lastLabelMin = -100;
    for (var i = 0; i < n; i++) {
      final t = candles[i].timestamp;
      final totalMin = t.hour * 60 + t.minute;
      if (totalMin - lastLabelMin >= 30) {
        lastLabelMin = totalMin;
        final x = cx(i);
        canvas.drawLine(
          Offset(x, 0),
          Offset(x, priceH),
          Paint()..color = grid,
        );
        final label =
            '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}';
        final tp = TextPainter(
          text: TextSpan(text: label, style: labelStyle),
          textDirection: TextDirection.ltr,
        )..layout();
        tp.paint(canvas, Offset((x - tp.width / 2).clamp(0.0, plotW - 34), plotH + 4));
      }
    }

    // الشموع المكتملة.
    for (var i = 0; i < currentCandle; i++) {
      _candle(canvas, candles[i], cx(i), py, slot, up, down);
    }
    // الشمعة الجارية: تُبنى لحظياً من تيكاتها.
    final cur = candles[currentCandle];
    var intraHigh = cur.open;
    var intraLow = cur.open;
    var intraVol = 0.0;
    for (var k = 0; k <= tickPos && k < ticks.length; k++) {
      final t = ticks[k];
      if (t.candleIndex != currentCandle) continue;
      if (t.price > intraHigh) intraHigh = t.price;
      if (t.price < intraLow) intraLow = t.price;
      intraVol += t.tickVolume;
    }
    _candlePartial(
      canvas,
      open: cur.open,
      high: intraHigh,
      low: intraLow,
      close: tick.price,
      x: cx(currentCandle),
      py: py,
      slot: slot,
      up: up,
      down: down,
    );

    // الفوليوم.
    var maxVol = 0.0;
    for (var i = 0; i <= currentCandle; i++) {
      if (candles[i].volume > maxVol) maxVol = candles[i].volume;
    }
    if (maxVol <= 0) maxVol = 1;
    final volTop = priceH + 6;
    for (var i = 0; i < currentCandle; i++) {
      final c = candles[i];
      final h = (c.volume / maxVol) * volumeH;
      canvas.drawRect(
        Rect.fromLTWH(cx(i) - slot * 0.3, volTop + volumeH - h, slot * 0.6, h),
        Paint()..color = (c.close >= c.open ? up : down).withValues(alpha: 0.5),
      );
    }
    final curVolH = (intraVol / maxVol) * volumeH;
    canvas.drawRect(
      Rect.fromLTWH(
        cx(currentCandle) - slot * 0.3,
        volTop + volumeH - curVolH,
        slot * 0.6,
        curVolH,
      ),
      Paint()..color = (tick.price >= cur.open ? up : down).withValues(alpha: 0.8),
    );

    // خط السعر الأخير + بطاقة السعر على المحور.
    final ly = py(tick.price);
    final linePaint = Paint()
      ..color = (tick.price >= cur.open ? up : down).withValues(alpha: 0.7)
      ..strokeWidth = 1;
    var dx = 0.0;
    while (dx < plotW) {
      canvas.drawLine(Offset(dx, ly), Offset((dx + 5).clamp(0.0, plotW), ly), linePaint);
      dx += 9;
    }
    final tag = tick.price.toStringAsFixed(2);
    final tagTp = TextPainter(
      text: const TextSpan(
        text: '',
        style: TextStyle(fontSize: 10, color: Colors.white),
      ),
      textDirection: TextDirection.ltr,
    );
    tagTp.text = TextSpan(
      text: tag,
      style: const TextStyle(fontSize: 10, color: Colors.white),
    );
    tagTp.layout();
    final tagRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(plotW + 2, ly - 9, _priceScaleW - 4, 18),
      const Radius.circular(4),
    );
    canvas.drawRRect(
      tagRect,
      Paint()..color = tick.price >= cur.open ? up : down,
    );
    tagTp.paint(canvas, Offset(plotW + 2 + ((_priceScaleW - 4 - tagTp.width) / 2), ly - 7));

    // الكروسهير للدراسة.
    if (cross != null &&
        cross!.dx >= 0 &&
        cross!.dx <= plotW &&
        cross!.dy >= 0 &&
        cross!.dy <= plotH) {
      final cp = Paint()
        ..color = const Color(0xFF787B86).withValues(alpha: 0.7)
        ..strokeWidth = 1;
      var hx = 0.0;
      while (hx < plotW) {
        canvas.drawLine(
          Offset(hx, cross!.dy),
          Offset((hx + 4).clamp(0.0, plotW), cross!.dy),
          cp,
        );
        hx += 8;
      }
      canvas.drawLine(Offset(cross!.dx, 0), Offset(cross!.dx, plotH), cp);
    }
  }

  void _candle(
    Canvas canvas,
    ReplayCandle c,
    double x,
    double Function(double) py,
    double slot,
    Color up,
    Color down,
  ) {
    _candlePartial(
      canvas,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
      x: x,
      py: py,
      slot: slot,
      up: up,
      down: down,
    );
  }

  void _candlePartial({
    required Canvas canvas,
    required double open,
    required double high,
    required double low,
    required double close,
    required double x,
    required double Function(double) py,
    required double slot,
    required Color up,
    required Color down,
  }) {
    final color = close >= open ? up : down;
    canvas.drawLine(
      Offset(x, py(high)),
      Offset(x, py(low)),
      Paint()
        ..color = color
        ..strokeWidth = 1.2,
    );
    final top = py(open > close ? open : close);
    final bottom = py(open > close ? close : open);
    final w = (slot * 0.6).clamp(1.5, 12.0);
    canvas.drawRect(
      Rect.fromCenter(
        center: Offset(x, (top + bottom) / 2),
        width: w,
        height: (bottom - top).abs().clamp(1.5, 10000.0),
      ),
      Paint()..color = color,
    );
  }

  @override
  bool shouldRepaint(covariant _TvChartPainter old) {
    return old.tickPos != tickPos ||
        old.cross != cross ||
        old.candles.length != candles.length;
  }
}

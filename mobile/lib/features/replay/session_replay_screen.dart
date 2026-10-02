import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' show DateFormat;

import '../../core/network/api_exception.dart';
import 'session_replay_models.dart';
import 'session_replay_repository.dart';

/// إعادة محاكاة شموع الجلسة الأخيرة على الشارت من الافتتاح للإغلاق.
///
/// نظام جديد مستقل: يجلب شموع الجلسة الأخيرة من
/// `GET /market/session-replay` ثم يعيد لعبها شمعة بشمعة بسرعات
/// قابلة للضبط (1x حتى 16x) بعد قفل السوق.
class SessionReplayScreen extends ConsumerStatefulWidget {
  const SessionReplayScreen({super.key, this.initialTicker});

  final String? initialTicker;

  @override
  ConsumerState<SessionReplayScreen> createState() =>
      _SessionReplayScreenState();
}

class _SessionReplayScreenState extends ConsumerState<SessionReplayScreen> {
  static const _speeds = <int>[1, 2, 4, 8, 16];
  static const _intervals = <String>['1m', '5m', '15m', '30m'];
  static const _baseTickMs = 600;

  late final TextEditingController _tickerController;
  String _interval = '5m';
  int _speedIndex = 0;

  bool _loading = false;
  String? _error;
  SessionReplay? _replay;

  int _position = 0;
  bool _playing = false;
  Timer? _timer;

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
    });
    try {
      final replay = await ref
          .read(sessionReplayRepositoryProvider)
          .fetch(ticker: ticker, interval: _interval);
      if (!mounted) return;
      setState(() {
        _replay = replay;
        _position = 0;
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

  void _start() {
    final replay = _replay;
    if (replay == null || replay.candles.isEmpty) return;
    if (_position >= replay.candles.length - 1) {
      setState(() => _position = 0);
    }
    _timer?.cancel();
    final periodMs = (_baseTickMs / _speed).round().clamp(30, 2000);
    _timer = Timer.periodic(Duration(milliseconds: periodMs), (_) {
      if (!mounted) return;
      final total = _replay?.candles.length ?? 0;
      if (_position >= total - 1) {
        _stop();
        return;
      }
      setState(() => _position += 1);
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

  void _step(int delta) {
    final total = _replay?.candles.length ?? 0;
    if (total == 0) return;
    _stop();
    setState(() {
      _position = (_position + delta).clamp(0, total - 1);
    });
  }

  @override
  Widget build(BuildContext context) {
    final replay = _replay;
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('محاكاة الجلسة الأخيرة'),
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
          else if (replay == null || replay.candles.isEmpty)
            const _EmptyCard()
          else ...[
            _StatsCard(replay: replay, position: _position),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Text(
                          replay.ticker,
                          textDirection: TextDirection.ltr,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'جلسة ${replay.sessionDate} • ${replay.interval}',
                          style: theme.textTheme.bodySmall,
                        ),
                        const Spacer(),
                        _SessionClock(
                          candle: replay.candles[_position],
                          position: _position,
                          total: replay.candles.length,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      height: 260,
                      child: CustomPaint(
                        painter: _CandleChartPainter(
                          candles: replay.candles
                              .take(_position + 1)
                              .toList(growable: false),
                          upColor: Colors.green,
                          downColor: Colors.red,
                          gridColor: theme.dividerColor,
                        ),
                        child: const SizedBox.expand(),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Slider(
                      value: _position.toDouble(),
                      min: 0,
                      max: (replay.candles.length - 1).toDouble(),
                      divisions: replay.candles.length - 1,
                      label: 'شمعة ${_position + 1}/${replay.candles.length}',
                      onChanged: (value) {
                        _stop();
                        setState(() => _position = value.round());
                      },
                    ),
                    _ControlsRow(
                      playing: _playing,
                      onToggle: _toggle,
                      onRestart: () {
                        _stop();
                        setState(() => _position = 0);
                      },
                      onBack: () => _step(-1),
                      onForward: () => _step(1),
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
                    const SizedBox(height: 4),
                    Text(
                      'السرعة ${_speed}x — الشموع تتحرك من أول الجلسة لآخرها',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
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

class _StatsCard extends StatelessWidget {
  const _StatsCard({required this.replay, required this.position});

  final SessionReplay replay;
  final int position;

  @override
  Widget build(BuildContext context) {
    final visible = replay.candles.take(position + 1).toList(growable: false);
    final sessionOpen = replay.candles.first.open;
    final current = visible.last.close;
    final changePct =
        sessionOpen == 0 ? 0.0 : ((current - sessionOpen) / sessionOpen) * 100;
    var high = visible.first.high;
    var low = visible.first.low;
    for (final candle in visible) {
      if (candle.high > high) high = candle.high;
      if (candle.low < low) low = candle.low;
    }
    final positive = changePct >= 0;
    final color = positive ? Colors.green : Colors.red;
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _Stat(
              label: 'السعر الآن',
              value: current.toStringAsFixed(2),
              color: color,
            ),
            _Stat(
              label: 'التغير',
              value:
                  '${positive ? '+' : ''}${changePct.toStringAsFixed(2)}%',
              color: color,
            ),
            _Stat(label: 'الأعلى', value: high.toStringAsFixed(2)),
            _Stat(label: 'الأدنى', value: low.toStringAsFixed(2)),
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
        const SizedBox(height: 4),
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

class _SessionClock extends StatelessWidget {
  const _SessionClock({
    required this.candle,
    required this.position,
    required this.total,
  });

  final ReplayCandle candle;
  final int position;
  final int total;

  @override
  Widget build(BuildContext context) {
    final time = DateFormat('HH:mm').format(candle.timestamp);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        '$time • ${position + 1}/$total',
        textDirection: TextDirection.ltr,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }
}

class _ControlsRow extends StatelessWidget {
  const _ControlsRow({
    required this.playing,
    required this.onToggle,
    required this.onRestart,
    required this.onBack,
    required this.onForward,
  });

  final bool playing;
  final VoidCallback onToggle;
  final VoidCallback onRestart;
  final VoidCallback onBack;
  final VoidCallback onForward;

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
          onPressed: onBack,
          icon: const Icon(Icons.chevron_left_rounded),
        ),
        FilledButton.icon(
          onPressed: onToggle,
          icon: Icon(
            playing ? Icons.pause_rounded : Icons.play_arrow_rounded,
          ),
          label: Text(playing ? 'إيقاف' : 'تشغيل'),
        ),
        IconButton(
          tooltip: 'شمعة للأمام',
          onPressed: onForward,
          icon: const Icon(Icons.chevron_right_rounded),
        ),
        IconButton(
          tooltip: 'إعادة التشغيل',
          onPressed: () {
            onRestart();
            onToggle();
          },
          icon: const Icon(Icons.replay_rounded),
        ),
      ],
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
            Icon(Icons.candlestick_chart_outlined, size: 48),
            SizedBox(height: 12),
            Text(
              'اختر سهماً وحمّل الجلسة الأخيرة لإعادة مشاهدة شموعها من الافتتاح حتى الإغلاق.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _CandleChartPainter extends CustomPainter {
  _CandleChartPainter({
    required this.candles,
    required this.upColor,
    required this.downColor,
    required this.gridColor,
  });

  final List<ReplayCandle> candles;
  final Color upColor;
  final Color downColor;
  final Color gridColor;

  @override
  void paint(Canvas canvas, Size size) {
    if (candles.isEmpty) return;
    var minPrice = candles.first.low;
    var maxPrice = candles.first.high;
    for (final candle in candles) {
      if (candle.low < minPrice) minPrice = candle.low;
      if (candle.high > maxPrice) maxPrice = candle.high;
    }
    var range = maxPrice - minPrice;
    if (range <= 0) range = 1;
    final pad = range * 0.08;
    minPrice -= pad;
    maxPrice += pad;
    range = maxPrice - minPrice;

    double y(double price) =>
        size.height - ((price - minPrice) / range) * size.height;

    final gridPaint = Paint()
      ..color = gridColor
      ..strokeWidth = 0.5;
    for (var i = 1; i < 4; i++) {
      final dy = (size.height / 4) * i;
      canvas.drawLine(Offset(0, dy), Offset(size.width, dy), gridPaint);
    }

    final slot = size.width / candles.length;
    final bodyWidth = (slot * 0.6).clamp(2.0, 14.0);
    for (var i = 0; i < candles.length; i++) {
      final candle = candles[i];
      final color = candle.isUp ? upColor : downColor;
      final cx = slot * i + slot / 2;
      final paint = Paint()
        ..color = color
        ..strokeWidth = 1.5;
      // Wick.
      canvas.drawLine(
        Offset(cx, y(candle.high)),
        Offset(cx, y(candle.low)),
        paint,
      );
      // Body.
      final top = y(candle.open > candle.close ? candle.open : candle.close);
      final bottom =
          y(candle.open > candle.close ? candle.close : candle.open);
      final rect = Rect.fromCenter(
        center: Offset(cx, (top + bottom) / 2),
        width: bodyWidth,
        height: (bottom - top).abs().clamp(2.0, size.height),
      );
      canvas.drawRect(rect, Paint()..color = color);
    }

    // Last price line.
    final last = candles.last.close;
    final linePaint = Paint()
      ..color = (candles.last.isUp ? upColor : downColor).withValues(
        alpha: 0.6,
      )
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;
    final path = Path();
    const dash = 5.0;
    const gap = 4.0;
    var x = 0.0;
    final ly = y(last);
    while (x < size.width) {
      path.moveTo(x, ly);
      path.lineTo((x + dash).clamp(0.0, size.width), ly);
      x += dash + gap;
    }
    canvas.drawPath(path, linePaint);
  }

  @override
  bool shouldRepaint(covariant _CandleChartPainter oldDelegate) {
    return oldDelegate.candles.length != candles.length ||
        oldDelegate.candles.isEmpty ||
        candles.isEmpty ||
        oldDelegate.candles.last.close != candles.last.close;
  }
}

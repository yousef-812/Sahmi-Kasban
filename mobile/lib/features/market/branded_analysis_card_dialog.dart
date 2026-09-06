import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class BrandedAnalysisCardDialog extends StatefulWidget {
  const BrandedAnalysisCardDialog({
    required this.ticker,
    required this.signal,
    required this.score,
    required this.confidence,
    required this.explanation,
    this.tradePlan = const {},
    super.key,
  });

  final String ticker;
  final String signal;
  final double? score;
  final double? confidence;
  final String explanation;
  final Map<String, dynamic> tradePlan;

  static const String signatureText = '''
--------------------------------------------------
تم استخراج هذا التحليل عبر تطبيق سهمي كسبان (Sahmi Kasban)
حمل تطبيق سهمي كسبان من علي متجر بلاي
--------------------------------------------------''';

  @override
  State<BrandedAnalysisCardDialog> createState() =>
      _BrandedAnalysisCardDialogState();
}

class _BrandedAnalysisCardDialogState extends State<BrandedAnalysisCardDialog> {
  final GlobalKey _repaintKey = GlobalKey();
  Uint8List? _imageBytes;
  bool _isGenerating = true;
  bool _isActionInProgress = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _generateImage();
    });
  }

  Future<void> _generateImage() async {
    // Small delay to allow fonts and widgets to render completely
    await Future<void>.delayed(const Duration(milliseconds: 180));
    try {
      final boundary =
          _repaintKey.currentContext?.findRenderObject()
              as RenderRepaintBoundary?;
      if (boundary != null) {
        final image = await boundary.toImage(pixelRatio: 2.8);
        final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
        if (mounted && byteData != null) {
          setState(() {
            _imageBytes = byteData.buffer.asUint8List();
            _isGenerating = false;
          });
          return;
        }
      }
    } catch (e) {
      debugPrint('Error generating image: $e');
    }
    if (mounted) {
      setState(() => _isGenerating = false);
    }
  }

  String _buildCopyableText() {
    final cleanExplanation = widget.explanation
        .replaceAll(RegExp(r'[#*`_]'), '')
        .trim();
    final scoreStr =
        widget.score != null
            ? '${widget.score!.toStringAsFixed(1)}/100'
            : 'غير متوفر';
    final confStr =
        widget.confidence != null
            ? '${widget.confidence!.toStringAsFixed(0)}%'
            : 'غير متوفر';

    final StringBuffer sb = StringBuffer();
    sb.writeln('تقرير تحليل سهم شامل: ${widget.ticker}');
    sb.writeln('القرار الآلي: ${widget.signal}');
    sb.writeln('تقييم الجودة: $scoreStr | نسبة الثقة: $confStr');
    if (widget.tradePlan.isNotEmpty) {
      sb.writeln('--- خطة التداول الافتراضية ---');
      if (widget.tradePlan['entry'] != null) {
        sb.writeln('سعر الدخول: ${widget.tradePlan['entry']}');
      }
      if (widget.tradePlan['target_1'] != null) {
        sb.writeln('الهدف الأول: ${widget.tradePlan['target_1']}');
      }
      if (widget.tradePlan['target_2'] != null) {
        sb.writeln('الهدف الثاني: ${widget.tradePlan['target_2']}');
      }
      if (widget.tradePlan['stop_loss'] != null) {
        sb.writeln('وقف الخسارة: ${widget.tradePlan['stop_loss']}');
      }
    }
    sb.writeln('\nملخص التحليل الفني:');
    sb.writeln(cleanExplanation);
    sb.writeln('\n${BrandedAnalysisCardDialog.signatureText}');
    return sb.toString();
  }

  void _copyToClipboard() {
    final text = _buildCopyableText();
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم نسخ التحليل كاملاً مع بيانات التداول بنجاح'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Future<void> _downloadImage() async {
    if (_imageBytes == null) return;
    setState(() => _isActionInProgress = true);
    try {
      final Directory dir =
          Platform.isAndroid
              ? (await getExternalStorageDirectory() ??
                  await getApplicationDocumentsDirectory())
              : await getApplicationDocumentsDirectory();

      final String timestamp = DateTime.now().millisecondsSinceEpoch.toString();
      final String filePath =
          '${dir.path}/sahmi_analysis_${widget.ticker}_$timestamp.png';
      final File file = File(filePath);
      await file.writeAsBytes(_imageBytes!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم حفظ صورة التحليل بنجاح في جهازك:\n$filePath'),
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل حفظ الصورة: $e'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isActionInProgress = false);
    }
  }

  Future<void> _shareImage() async {
    if (_imageBytes == null) return;
    setState(() => _isActionInProgress = true);
    try {
      final tempDir = await getTemporaryDirectory();
      final String filePath = '${tempDir.path}/sahmi_analysis_${widget.ticker}.png';
      final File file = File(filePath);
      await file.writeAsBytes(_imageBytes!);

      final String shareText =
          'تقرير تحليل سهم ${widget.ticker} عبر تطبيق سهمي كسبان:\n'
          'القرار الآلي: ${widget.signal}\n'
          'الدرجة: ${widget.score?.toStringAsFixed(1) ?? "-"}/100';

      await Share.shareXFiles(
        [XFile(file.path)],
        text: shareText,
        subject: 'تحليل سهم ${widget.ticker}',
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل مشاركة الصورة: $e'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isActionInProgress = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 680, maxHeight: 780),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0F172A),
              Color(0xFF1E293B),
              Color(0xFF0F172A),
            ],
          ),
          border: Border.all(
            color: Colors.amber.withValues(alpha: 0.3),
            width: 1.5,
          ),
        ),
        padding: const EdgeInsets.all(18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Modal Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.amber.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.image_search_rounded,
                          color: Colors.amber,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'معاينة صورة التحليل الكاملة',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              'صورة عالية الدقة تحتوي كامل التقرير بدون اقتصاص',
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.7),
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white70),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const Divider(color: Colors.white12, height: 24),

            // Content Area (Image Preview or Render Boundary)
            Expanded(
              child: Stack(
                children: [
                  // Hidden Offscreen RepaintBoundary for rendering
                  SingleChildScrollView(
                    child: UnconstrainedBox(
                      alignment: Alignment.topCenter,
                      child: SizedBox(
                        width: 640,
                        child: RepaintBoundary(
                          key: _repaintKey,
                          child: _BrandedCardExportContent(
                            ticker: widget.ticker,
                            signal: widget.signal,
                            score: widget.score,
                            confidence: widget.confidence,
                            explanation: widget.explanation,
                            tradePlan: widget.tradePlan,
                            theme: theme,
                          ),
                        ),
                      ),
                    ),
                  ),

                  // Overlay Preview once generated
                  if (_isGenerating)
                    Container(
                      color: const Color(0xFF0F172A),
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(color: Colors.amber),
                            SizedBox(height: 16),
                            Text(
                              'جاري توليد صورة التحليل الكاملة...',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'يتم تجميع كافة تفاصيل التقرير في صورة واحدة عالية الجودة',
                              style: TextStyle(
                                color: Colors.white60,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                  else if (_imageBytes != null)
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.black38,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.white12),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: InteractiveViewer(
                          maxScale: 4.0,
                          minScale: 0.8,
                          child: SingleChildScrollView(
                            child: Image.memory(
                              _imageBytes!,
                              fit: BoxFit.contain,
                              width: double.infinity,
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Action Buttons Bar
            if (_isActionInProgress)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(8.0),
                  child: CircularProgressIndicator(color: Colors.amber),
                ),
              )
            else
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: _imageBytes != null ? _shareImage : null,
                          style: FilledButton.styleFrom(
                            backgroundColor: Colors.amber,
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          icon: const Icon(Icons.share_rounded, size: 20),
                          label: const Text(
                            'مشاركة الصورة',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: FilledButton.icon(
                          onPressed:
                              _imageBytes != null ? _downloadImage : null,
                          style: FilledButton.styleFrom(
                            backgroundColor: theme.colorScheme.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          icon: const Icon(Icons.download_rounded, size: 20),
                          label: const Text(
                            'تنزيل الصورة',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _copyToClipboard,
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.white70,
                            side: const BorderSide(color: Colors.white24),
                          ),
                          icon: const Icon(
                            Icons.content_copy_rounded,
                            size: 16,
                          ),
                          label: const Text('نسخ كـ نص'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.white60,
                        ),
                        child: const Text('إغلاق'),
                      ),
                    ],
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _BrandedCardExportContent extends StatelessWidget {
  const _BrandedCardExportContent({
    required this.ticker,
    required this.signal,
    required this.score,
    required this.confidence,
    required this.explanation,
    required this.tradePlan,
    required this.theme,
  });

  final String ticker;
  final String signal;
  final double? score;
  final double? confidence;
  final String explanation;
  final Map<String, dynamic> tradePlan;
  final ThemeData theme;

  @override
  Widget build(BuildContext context) {
    final scoreVal = score != null ? score!.toStringAsFixed(1) : '-';
    final confVal =
        confidence != null ? '${confidence!.toStringAsFixed(0)}%' : '-';
    final cleanExplanation = explanation
        .replaceAll(RegExp(r'[#*`_]'), '')
        .trim();

    return Container(
      width: 640,
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.amber.withValues(alpha: 0.4),
          width: 2,
        ),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header Brand Badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 7,
                ),
                decoration: BoxDecoration(
                  color: Colors.amber.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.amber, width: 1.2),
                ),
                child: const Row(
                  children: [
                    Icon(
                      Icons.show_chart_rounded,
                      color: Colors.amber,
                      size: 18,
                    ),
                    SizedBox(width: 6),
                    Text(
                      'سهمي كسبان | SAHMI KASBAN',
                      style: TextStyle(
                        color: Colors.amber,
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const Text(
                'تقرير تحليل آلي متكامل',
                style: TextStyle(color: Colors.white54, fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 18),

          // Main Header: Ticker & Recommendation Signal
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.04),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white12),
            ),
            child: Row(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      ticker,
                      textDirection: TextDirection.ltr,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 34,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'تحليل شامل ومفصل للسهم',
                      style: TextStyle(color: Colors.white60, fontSize: 12),
                    ),
                  ],
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        theme.colorScheme.primary,
                        theme.colorScheme.primary.withValues(alpha: 0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(14),
                    boxShadow: [
                      BoxShadow(
                        color: theme.colorScheme.primary.withValues(alpha: 0.4),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      const Text(
                        'القرار الآلي',
                        style: TextStyle(color: Colors.white70, fontSize: 10),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        signal,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w900,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Key Indicators & Scores Row
          Row(
            children: [
              Expanded(
                child: _ExportInfoTile(
                  label: 'تقييم الجودة',
                  value: '$scoreVal/100',
                  color: Colors.amber,
                  icon: Icons.workspace_premium_rounded,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _ExportInfoTile(
                  label: 'نسبة الثقة',
                  value: confVal,
                  color: Colors.lightGreenAccent,
                  icon: Icons.verified_user_rounded,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Trade Plan Grid Section (if available)
          if (tradePlan.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.black26,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(
                        Icons.alt_route_rounded,
                        color: Colors.cyanAccent,
                        size: 18,
                      ),
                      SizedBox(width: 6),
                      Text(
                        'خطة التداول الأهداف والمخاطر',
                        style: TextStyle(
                          color: Colors.cyanAccent,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      if (tradePlan['entry'] != null)
                        Expanded(
                          child: _ExportPlanCell(
                            label: 'سعر الدخول',
                            value: '${tradePlan['entry']}',
                            color: Colors.white,
                          ),
                        ),
                      if (tradePlan['stop_loss'] != null)
                        Expanded(
                          child: _ExportPlanCell(
                            label: 'وقف الخسارة',
                            value: '${tradePlan['stop_loss']}',
                            color: Colors.redAccent,
                          ),
                        ),
                      if (tradePlan['target_1'] != null)
                        Expanded(
                          child: _ExportPlanCell(
                            label: 'الهدف الأول',
                            value: '${tradePlan['target_1']}',
                            color: Colors.greenAccent,
                          ),
                        ),
                      if (tradePlan['target_2'] != null)
                        Expanded(
                          child: _ExportPlanCell(
                            label: 'الهدف الثاني',
                            value: '${tradePlan['target_2']}',
                            color: Colors.green,
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
          ],

          // Full Analysis Summary Box (Unclipped, Full Height)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.03),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.white12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.notes_rounded, color: Colors.white70, size: 18),
                    SizedBox(width: 6),
                    Text(
                      'ملخص التحليل الفني والمالي الكامل',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  cleanExplanation,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    height: 1.6,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Signature Branding Callout Box
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.amber.withValues(alpha: 0.3)),
            ),
            child: const Column(
              children: [
                Text(
                  'تم استخراج هذا التحليل الشامل عبر تطبيق سهمي كسبان (Sahmi Kasban)',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.amber,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'حمل تطبيق سهمي كسبان الآن من متجر بلاي للحصول على تحليلات دقيقة يومياً',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ExportInfoTile extends StatelessWidget {
  const _ExportInfoTile({
    required this.label,
    required this.value,
    required this.color,
    required this.icon,
  });

  final String label;
  final String value;
  final Color color;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(color: Colors.white60, fontSize: 11),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  color: color,
                  fontSize: 16,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ExportPlanCell extends StatelessWidget {
  const _ExportPlanCell({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white60, fontSize: 10),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          textDirection: TextDirection.ltr,
          style: TextStyle(
            color: color,
            fontSize: 13,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

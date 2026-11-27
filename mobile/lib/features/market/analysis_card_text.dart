/// Helpers that turn raw engine text and numbers into clean text for the
/// shareable analysis card and the copied summary.
library;

final RegExp _htmlBreak = RegExp(r'<\s*br\s*/?\s*>', caseSensitive: false);
final RegExp _htmlTag = RegExp(r'<[^>]+>');
final RegExp _tableDivider = RegExp(r'^\s*\|?[\s:\-|]+\|?\s*$');
final RegExp _markdownMarks = RegExp(r'[#*`_>~]');
// Internal engine keys such as resistanceproximitypct, volumeratio or
// buy_signal: long all-lowercase latin tokens or snake_case words.
final RegExp _internalKey = RegExp(r'[a-z]+_[a-z_0-9]+|\b[a-z]{9,}[a-z0-9]*\b');
final RegExp _arabic = RegExp(r'[\u0600-\u06FF]');

/// Formats a number-like value with two decimals. Returns null when empty.
String? formatPrice(Object? value) {
  if (value == null) return null;
  final parsed = value is num ? value : num.tryParse(value.toString().trim());
  if (parsed == null) {
    final text = value.toString().trim();
    return text.isEmpty ? null : text;
  }
  return parsed.toStringAsFixed(2);
}

/// Removes HTML, markdown tables and markdown marks. Keeps readable lines.
String cleanAnalysisText(String raw) {
  final withBreaks = raw.replaceAll(_htmlBreak, '\n').replaceAll(_htmlTag, ' ');
  final lines = <String>[];
  for (final original in withBreaks.split('\n')) {
    var line = original.trim();
    if (line.isEmpty) continue;
    if (_tableDivider.hasMatch(line)) continue;
    if (line.contains('|')) {
      final cells = line
          .split('|')
          .map((c) => c.replaceAll(_markdownMarks, '').trim())
          .where((c) => c.isNotEmpty && !_tableDivider.hasMatch(c))
          .toList();
      line = cells.join(' - ');
    } else {
      line = line.replaceAll(_markdownMarks, '').trim();
    }
    line = line.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (line.isEmpty || RegExp(r'^[-\s]+$').hasMatch(line)) continue;
    lines.add(line);
  }
  return lines.join('\n');
}

/// Picks a few short, readable Arabic highlights from the full analysis text.
List<String> extractHighlights(
  String raw, {
  int maxItems = 4,
  int maxChars = 110,
}) {
  final cleaned = cleanAnalysisText(raw);
  final results = <String>[];
  for (final line in cleaned.split('\n')) {
    var text = line.replaceFirst(RegExp(r'^\d+[\.\)]\s*'), '').trim();
    if (text.length < 15) continue;
    if (!_arabic.hasMatch(text)) continue;
    if (_internalKey.hasMatch(text)) continue;
    if (text.startsWith('القرار') || text.startsWith('تنويه')) continue;
    if (text.startsWith('ملخص') || text.startsWith('أسباب')) continue;
    if (text.length > maxChars) {
      text = '${text.substring(0, maxChars).trimRight()}...';
    }
    results.add(text);
    if (results.length >= maxItems) break;
  }
  return results;
}

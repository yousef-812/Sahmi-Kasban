import 'package:flutter/material.dart';

import '../../domain/models.dart';

String formatPrice(double? value) {
  if (value == null) {
    return '—';
  }
  final text = value.toStringAsFixed(2);
  // Use Arabic-friendly rendering; the trailing zeros are intentional.
  return text;
}

String formatChangePercent(double? value) {
  if (value == null) {
    return '—';
  }
  final sign = value > 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(2)}%';
}

Color changeColor(BuildContext context, double? value) {
  if (value == null) {
    return Theme.of(context).colorScheme.onSurfaceVariant;
  }
  if (value > 0) {
    return Colors.green;
  }
  if (value < 0) {
    return Colors.redAccent;
  }
  return Theme.of(context).colorScheme.onSurfaceVariant;
}

class StockQuoteCard extends StatelessWidget {
  const StockQuoteCard({super.key, required this.quote, required this.onTap});

  final MarketQuote quote;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isUp = (quote.changePercent ?? 0) > 0;
    final isDown = (quote.changePercent ?? 0) < 0;
    final accent = isUp
        ? Colors.green
        : isDown
        ? Colors.redAccent
        : Theme.of(context).colorScheme.primary;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(
                        context,
                      ).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      quote.ticker,
                      textDirection: TextDirection.ltr,
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    isUp
                        ? Icons.trending_up_rounded
                        : isDown
                        ? Icons.trending_down_rounded
                        : Icons.trending_flat_rounded,
                    color: accent,
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                quote.description.isEmpty ? quote.ticker : quote.description,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 10),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    formatPrice(quote.currentPrice),
                    textDirection: TextDirection.ltr,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: accent,
                    ),
                  ),
                  if (quote.volume != null) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _formatVolume(quote.volume),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 6),
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: Text(
                  formatChangePercent(quote.changePercent),
                  textDirection: TextDirection.ltr,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: changeColor(context, quote.changePercent),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatVolume(double? value) {
    if (value == null) {
      return '';
    }
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(1)}M';
    }
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}K';
    }
    return value.toStringAsFixed(0);
  }
}

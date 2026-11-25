import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'sentiment_models.dart';
import 'sentiment_repository.dart';

/// معنويات أخبار السهم خلال آخر 7 أيام (نافذة افتراضية).
final stockSentimentProvider = FutureProvider.autoDispose
    .family<SymbolSentiment, String>((ref, ticker) {
      return ref.watch(sentimentRepositoryProvider).symbolSentiment(ticker);
    });

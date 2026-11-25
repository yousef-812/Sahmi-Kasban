import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'order_flow_models.dart';
import 'order_flow_repository.dart';

/// دفتر الأوامر لسهم واحد (يُحمَّل فقط عند فتح تبويب تدفق الأوامر).
final orderBookProvider = FutureProvider.autoDispose
    .family<OrderBookSnapshot, String>((ref, ticker) {
      return ref.watch(orderFlowRepositoryProvider).orderBook(ticker);
    });

/// آخر الصفقات المنفّذة لسهم واحد.
final recentTradesProvider = FutureProvider.autoDispose
    .family<RecentTradesSnapshot, String>((ref, ticker) {
      return ref.watch(orderFlowRepositoryProvider).recentTrades(ticker);
    });

/// كشف «الحيتان» (دوران يومي استثنائي) — الإشارة البديلة المتاحة فعليًا.
final whaleActivityProvider = FutureProvider.autoDispose
    .family<WhaleDetectionSnapshot, String>((ref, ticker) {
      return ref.watch(orderFlowRepositoryProvider).bulkTrades(ticker);
    });

/// ملخّص عمق السوق لسهم واحد.
final marketDepthProvider = FutureProvider.autoDispose
    .family<MarketDepthSnapshot, String>((ref, ticker) {
      return ref.watch(orderFlowRepositoryProvider).depth(ticker);
    });

/// أفضل سعر bid/ask لحظي بدون أحجام (WP-27).
final topOfBookProvider = FutureProvider.autoDispose
    .family<TopOfBookQuote, String>((ref, ticker) {
      return ref.watch(orderFlowRepositoryProvider).topOfBook(ticker);
    });

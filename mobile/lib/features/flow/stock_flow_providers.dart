import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'stock_flow_models.dart';
import 'stock_flow_repository.dart';

/// ضغط الشراء/البيع لسهم واحد (يُحمَّل عند توسيع القسم).
final stockFlowProvider = FutureProvider.autoDispose
    .family<StockFlowSnapshot, String>((ref, ticker) {
      return ref.watch(stockFlowRepositoryProvider).stockFlow(ticker);
    });

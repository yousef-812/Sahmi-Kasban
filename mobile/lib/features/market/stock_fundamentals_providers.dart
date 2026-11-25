import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/backend_repository.dart';
import '../../domain/models.dart';

/// تحليل الاستثمار الأساسي لسهم واحد (PE/PB/عائد توزيعات...).
final stockInvestmentProvider = FutureProvider.autoDispose
    .family<StockInvestmentAnalysis, String>((ref, ticker) {
      return ref.watch(backendRepositoryProvider).getStockInvestmentAnalysis(ticker);
    });

/// تقويم أرباح السهم القادم — `available:false` عند غياب بيانات حقيقية.
final earningsCalendarProvider = FutureProvider.autoDispose
    .family<EarningsCalendarSnapshot, String>((ref, ticker) {
      return ref.watch(backendRepositoryProvider).getEarningsCalendar(ticker);
    });

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'scanner_models.dart';
import 'scanner_repository.dart';

final scannerTechnicalProvider =
    FutureProvider.autoDispose<ScannerList<ScannerTechnicalItem>>((ref) {
      return ref.watch(scannerRepositoryProvider).technical();
    });

final scannerTechnicalSymbolProvider = FutureProvider.autoDispose
    .family<ScannerTechnicalItem, String>((ref, symbol) {
      return ref.watch(scannerRepositoryProvider).technicalSymbol(symbol);
    });

final scannerFibonacciProvider =
    FutureProvider.autoDispose<ScannerList<ScannerFibonacciItem>>((ref) {
      return ref.watch(scannerRepositoryProvider).fibonacci();
    });

final scannerHarmonicProvider = FutureProvider.autoDispose
    .family<ScannerHarmonicItem, String>((ref, symbol) {
      return ref.watch(scannerRepositoryProvider).harmonicSymbol(symbol);
    });

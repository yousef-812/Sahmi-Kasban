import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import 'scanner_models.dart';

class ScannerRepository {
  const ScannerRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<ScannerList<ScannerTechnicalItem>> technical({
    String? sector,
    String? rating,
    double? minScore,
    int limit = 500,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/scanner/technical',
        queryParameters: _queryParameters(
          sector: sector,
          rating: rating,
          minScore: minScore,
          limit: limit,
        ),
      );
      return ScannerList.fromJson(
        _required(response.data),
        (Object? item) => ScannerTechnicalItem.fromJson(_map(item)),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<ScannerTechnicalItem> technicalSymbol(String symbol) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/scanner/technical/$symbol',
      );
      return ScannerTechnicalItem.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<ScannerList<ScannerFibonacciItem>> fibonacci({
    String? sector,
    String? rating,
    double? minScore,
    int limit = 500,
  }) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/scanner/fibonacci',
        queryParameters: _queryParameters(
          sector: sector,
          rating: rating,
          minScore: minScore,
          limit: limit,
        ),
      );
      return ScannerList.fromJson(
        _required(response.data),
        (Object? item) => ScannerFibonacciItem.fromJson(_map(item)),
      );
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<ScannerFibonacciItem> fibonacciSymbol(String symbol) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/scanner/fibonacci/$symbol',
      );
      return ScannerFibonacciItem.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<ScannerHarmonicItem> harmonicSymbol(String symbol) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/scanner/harmonic/$symbol',
      );
      return ScannerHarmonicItem.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Future<ScannerSmcItem> smc(String symbol) async {
    try {
      final response = await _apiClient.dio.get<Map<String, dynamic>>(
        '/scanner/smc/$symbol',
      );
      return ScannerSmcItem.fromJson(_required(response.data));
    } on Object catch (error) {
      throw _apiClient.mapError(error);
    }
  }

  Map<String, dynamic> _queryParameters({
    String? sector,
    String? rating,
    double? minScore,
    required int limit,
  }) {
    final parameters = <String, dynamic>{'limit': limit};
    if (sector != null && sector.isNotEmpty) {
      parameters['sector'] = sector;
    }
    if (rating != null && rating.isNotEmpty) {
      parameters['rating'] = rating;
    }
    if (minScore != null) {
      parameters['min_score'] = minScore;
    }
    return parameters;
  }

  Map<String, dynamic> _required(Map<String, dynamic>? value) {
    if (value == null) {
      throw const FormatException('Scanner response is empty.');
    }
    return value;
  }

  Map<String, dynamic> _map(Object? value) => value is Map<String, dynamic>
      ? value
      : value is Map
      ? Map<String, dynamic>.from(value)
      : <String, dynamic>{};
}

final scannerRepositoryProvider = Provider<ScannerRepository>((ref) {
  return ScannerRepository(ref.watch(apiClientProvider));
});

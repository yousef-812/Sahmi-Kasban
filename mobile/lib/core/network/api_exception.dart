class ApiException implements Exception {
  const ApiException({
    required this.message,
    this.statusCode,
    this.payload,
    this.retryAfterSeconds,
  });

  final String message;
  final int? statusCode;
  final Object? payload;
  final int? retryAfterSeconds;

  @override
  String toString() => 'ApiException($statusCode): $message';
}

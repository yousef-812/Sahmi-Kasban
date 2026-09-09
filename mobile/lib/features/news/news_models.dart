class StockNewsArticle {
  const StockNewsArticle({
    required this.id,
    required this.title,
    required this.summary,
    required this.url,
    required this.sourceName,
    required this.sourceKey,
    required this.publishedAt,
    this.imageUrl,
    this.content = '',
    this.sentiment,
    this.tickers = const [],
  });

  final String id;
  final String title;
  final String summary;
  final String content;
  final String url;
  final String sourceName;
  final String sourceKey;
  final DateTime publishedAt;
  final String? imageUrl;
  final String? sentiment; // "bullish" | "bearish" | "neutral"
  final List<String> tickers;

  factory StockNewsArticle.fromJson(Map<String, dynamic> json) {
    return StockNewsArticle(
      id: json['id'] as String,
      title: json['title'] as String,
      summary: json['summary'] as String? ?? '',
      content: json['content'] as String? ?? '',
      url: json['url'] as String,
      sourceName: json['source_name'] as String? ?? '',
      sourceKey: json['source_key'] as String? ?? '',
      publishedAt: DateTime.parse(json['published_at'] as String),
      imageUrl: json['image_url'] as String?,
      sentiment: json['sentiment'] as String?,
      tickers: (json['tickers'] as List<dynamic>? ?? const [])
          .map((e) => e.toString())
          .toList(growable: false),
    );
  }
}

class NewsListResponse {
  const NewsListResponse({
    required this.items,
    required this.total,
    required this.hasMore,
  });

  final List<StockNewsArticle> items;
  final int total;
  final bool hasMore;

  factory NewsListResponse.fromJson(Map<String, dynamic> json) {
    return NewsListResponse(
      items: (json['items'] as List<dynamic>)
          .map((e) => StockNewsArticle.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
      total: json['total'] as int? ?? 0,
      hasMore: json['has_more'] as bool? ?? false,
    );
  }
}

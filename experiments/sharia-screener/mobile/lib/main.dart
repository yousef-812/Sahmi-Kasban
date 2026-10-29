import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// Override at build time, e.g. --dart-define=API_BASE_URL=https://your-api.example.com
const apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

void main() => runApp(const ShariaScreenerApp());

class ShariaScreenerApp extends StatelessWidget {
  const ShariaScreenerApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'الأسهم الشرعية',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: const Color(0xFF167D74),
            useMaterial3: true, fontFamily: 'Roboto'),
        home: const ScreenerHome(),
      );
}

class ScreenerHome extends StatefulWidget {
  const ScreenerHome({super.key});
  @override
  State<ScreenerHome> createState() => _ScreenerHomeState();
}

class _ScreenerHomeState extends State<ScreenerHome> {
  bool loading = false;
  String? error;
  List<dynamic> ranked = [];

  Future<void> scan() async {
    setState(() { loading = true; error = null; });
    try {
      final response = await http.post(Uri.parse('$apiBaseUrl/api/v1/scan'))
          .timeout(const Duration(seconds: 40));
      final body = jsonDecode(response.body);
      if (response.statusCode >= 400) {
        throw Exception(body is Map ? body['detail'] ?? response.body : response.body);
      }
      setState(() => ranked = (body['ranked'] as List?) ?? []);
    } catch (e) {
      setState(() => error = 'تعذر تحميل التحليل: $e');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.rtl,
    child: Scaffold(
      appBar: AppBar(title: const Text('ماسح الأسهم الشرعية')),
      body: RefreshIndicator(
        onRefresh: scan,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text('ترتيب فني بعد إغلاق السوق',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            const Text('تأكد من أهلية السهم شرعيًا من مصدر رسمي مستقل. النتائج ليست ضمانًا للربح.'),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: loading ? null : scan,
              icon: loading
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.analytics_outlined),
              label: Text(loading ? 'جارٍ التحليل...' : 'تحليل كل الأسهم'),
            ),
            if (error != null) Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            ),
            if (ranked.isEmpty && error == null)
              const Padding(
                padding: EdgeInsets.only(top: 28),
                child: Center(child: Text('اضغط «تحليل كل الأسهم» بعد إعداد قائمة الأسهم وبيانات الإغلاق.')),
              ),
            ...ranked.map((item) => Card(
              child: ListTile(
                title: Text('${item['symbol']} — ${item['signal']}'),
                subtitle: Text('الإغلاق: ${item['close']} | ${item['as_of']}\n'
                    '${(item['reasons'] as List? ?? []).join('، ')}'),
                isThreeLine: true,
                trailing: CircleAvatar(child: Text('${item['score']}')),
              ),
            )),
          ],
        ),
      ),
    ),
  );
}

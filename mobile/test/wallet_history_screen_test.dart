import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahmi_kasban_mobile/data/backend_repository.dart';
import 'package:sahmi_kasban_mobile/domain/models.dart';
import 'package:sahmi_kasban_mobile/features/wallet/wallet_history_screen.dart';

class _MockBackendRepository extends Mock implements BackendRepository {}

void main() {
  testWidgets('wallet history renders Arabic-safe dates without intl setup', (
    tester,
  ) async {
    final repository = _MockBackendRepository();
    when(() => repository.getWalletHistory(limit: 20, offset: 0)).thenAnswer(
      (_) async => WalletHistoryPage(
        total: 1,
        limit: 20,
        offset: 0,
        items: <WalletEntryModel>[
          WalletEntryModel(
            transactionId: 'weekly:test:2026-07-27',
            entryType: 'weekly_plan_grant',
            amountPoints: 300,
            amountCoins: '3.00',
            status: 'confirmed',
            referenceType: 'subscription',
            referenceId: 'subscription-id',
            details: const <String, dynamic>{},
            createdAt: DateTime.utc(2026, 7, 28, 20, 15),
            confirmedAt: DateTime.utc(2026, 7, 28, 20, 15),
          ),
        ],
      ),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: <Override>[
          backendRepositoryProvider.overrideWithValue(repository),
        ],
        child: const MaterialApp(home: WalletHistoryScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('توزيع الخطة الأسبوعي'), findsOneWidget);
    expect(find.textContaining('الحالة: مكتملة'), findsOneWidget);
    expect(find.textContaining('+3.00 عملة'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

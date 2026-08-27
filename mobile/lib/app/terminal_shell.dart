import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme/terminal_theme.dart';

/// Navigation shell for the "Trading Terminal" experience with 5 main tabs:
/// PULSE, ANALYZE, WATCH, REPORTS, ME.
class TerminalShell extends StatelessWidget {
  const TerminalShell({required this.child, super.key});

  final Widget child;

  int _calculateSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/pulse')) return 0;
    if (location.startsWith('/stocks') || location.startsWith('/analyze')) {
      return 1;
    }
    if (location.startsWith('/watch') ||
        location.startsWith('/market/compare')) {
      return 2;
    }
    if (location.startsWith('/reports')) return 3;
    if (location.startsWith('/me') || location.startsWith('/profile')) return 4;
    return 0;
  }

  void _onItemTapped(int index, BuildContext context) {
    switch (index) {
      case 0:
        context.go('/pulse');
        break;
      case 1:
        context.go('/stocks');
        break;
      case 2:
        context.go('/market/compare');
        break;
      case 3:
        context.go('/reports');
        break;
      case 4:
        context.go('/profile/edit');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = TerminalTheme.of(context);
    final selectedIndex = _calculateSelectedIndex(context);

    return Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: theme.bgBase,
          border: Border(top: BorderSide(color: theme.border, width: 1)),
        ),
        child: BottomNavigationBar(
          currentIndex: selectedIndex,
          onTap: (index) => _onItemTapped(index, context),
          backgroundColor: theme.bgBase,
          selectedItemColor: theme.signalGold,
          unselectedItemColor: theme.textSecondary,
          selectedLabelStyle: theme.monoTiny.copyWith(
            fontWeight: FontWeight.w800,
          ),
          unselectedLabelStyle: theme.monoTiny,
          type: BottomNavigationBarType.fixed,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.bolt_rounded),
              label: 'النبض',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.analytics_rounded),
              label: 'تحليل',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.remove_red_eye_rounded),
              label: 'متابعة',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.insert_chart_outlined_rounded),
              label: 'التقارير',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline_rounded),
              label: 'أنا',
            ),
          ],
        ),
      ),
    );
  }
}

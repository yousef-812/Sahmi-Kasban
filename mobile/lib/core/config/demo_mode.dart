class DemoMode {
  const DemoMode._();

  static const enabled = bool.fromEnvironment('DEMO_MODE', defaultValue: false);
}

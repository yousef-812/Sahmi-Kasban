# Mobile 0.9.1 — Compact banner and performance ledger stability

- Replaced the large anchored adaptive free-plan banner with the standard 320x50 banner size.
- Initialized Arabic date symbols before the Flutter app starts.
- Added a numeric fallback so performance dates cannot crash the screen if locale data is unavailable.
- Clamped progress values and translated performance statuses.
- Made the session selector, best/worst cards, and report list safe on narrow phones.
- Made pull-to-refresh await the refreshed requests.
- Added visible validation for administrator OHLC corrections.
- Added regression tests for date fallback, progress clamping, and status labels.
- Mobile version: `0.9.1+16`.

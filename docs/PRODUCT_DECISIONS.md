# Sahmi Kasban — Launch Product Decisions

Status: approved for the first Google Play release  
Decision date: 2026-07-28

## Market data and reports

- Primary EGX provider: TradingView WebSocket and TradingView Egypt scanner.
- Fallback provider: yfinance when TradingView history is unavailable.
- The persisted TradingView catalog is authoritative for searchable Egyptian symbols; the 155-symbol seed remains offline fallback only.
- Daily Top 10 generation gate: 17:00 Africa/Cairo on an EGX trading day.
- Daily reports are immutable after publication. Corrections are appended to the audit/performance ledger rather than silently replacing history.
- Market-data cache: 30 minutes.
- TradingView instrument-catalog refresh: every 12 hours.
- A paid stock analysis remains available to the same account while its finalized market-data snapshot and engine version remain current. New finalized session data or a new analysis-engine version creates a new payable analysis.

## Wallet and weekly grants

- One coin equals 100 internal points.
- Coins accumulate and do not expire while the account is active.
- Coins have no cash value, cannot be withdrawn, and cannot be transferred between users.
- The Cairo week starts on Monday at 00:00.
- The server applies the weekly grant automatically and idempotently after the week starts; restarts cannot duplicate it.
- Weekly grants:
  - Free: 3 coins / 300 points.
  - Basic: 10 coins / 1,000 points.
  - Advanced: 15 coins / 1,500 points.
  - Pro: 50 coins / 5,000 points.
- After a paid subscription expires, the next due grant uses the free-plan amount.

## Launch pricing for Google Play Egypt

Google Play remains the source of truth for displayed localized prices.

### Monthly subscriptions

- Basic (`sahmi_basic_monthly`): EGP 79.99.
- Advanced (`sahmi_advanced_monthly`): EGP 149.99.
- Pro (`sahmi_pro_monthly`): EGP 299.99.

### One-time coin packs

- 5 coins (`sahmi_coins_5`): EGP 24.99.
- 15 coins (`sahmi_coins_15`): EGP 59.99.
- 40 coins (`sahmi_coins_40`): EGP 129.99.
- 100 coins (`sahmi_coins_100`): EGP 249.99.

These prices may be changed in Play Console without changing application code, but the product IDs and coin amounts must remain aligned with the server catalog.

## Plan limits

- Saved wallet/analysis history items exposed by plan:
  - Free: 20.
  - Basic: 100.
  - Advanced: 250.
  - Pro: 1,000.
- Daily-report history:
  - Free: latest day.
  - Basic: 30 days.
  - Advanced: 90 days.
  - Pro: 365 days.
- A watchlist is not part of the first public release, so no unsupported watchlist limits will be advertised.

## Community policy

- Published prediction content cannot be edited because the frozen version is used for later evaluation and rewards.
- Rejected or hidden content can use the existing appeal flow; accepted appeals preserve a complete audit trail.
- Links, contact information, advertising, abuse, spam, guaranteed-profit claims, and manipulation are prohibited.
- AI assists moderation and explanation, while deterministic server rules control charging, scoring, and rewards.

## Legal and positioning

- Product name and service operator shown to users: Sahmi Kasban / سهمي كسبان. The Play Console developer name must match the publisher account and should be added to the privacy page when finalized.
- Target market for the first release: Egypt.
- Applicable-law statement: laws applicable in the Arab Republic of Egypt, without removing mandatory consumer rights.
- The service is informational and educational. It is not a broker, does not execute trades, does not hold client funds, and does not provide personalized licensed investment advice.
- Public legal pages are hosted by the Fly application at `/legal`, `/privacy`, `/terms`, `/financial-disclaimer`, `/data-safety`, `/financial-features`, and `/delete-account`.

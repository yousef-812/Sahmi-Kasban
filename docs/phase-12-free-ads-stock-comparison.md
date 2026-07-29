# Phase 12 — Free-plan ads and stock comparison

## Scope

- A global anchored banner slot is shown only when the authenticated profile has ads enabled.
- A native ad slot is available for content-heavy free-plan surfaces.
- Interstitials are limited to natural post-action transitions, after three meaningful actions and with a minimum four-minute interval.
- All default mobile ad unit IDs remain Google's official test IDs. Production IDs must be supplied through build-time environment values.
- Users can compare two or more EGX stocks from the app.
- Free accounts can compare up to three stocks for 0.5 coin per comparison.
- Basic, Advanced, and Pro plans consume their included monthly comparison allowances before any comparison charge.
- A missing current stock analysis may still cost the normal 0.5 coin; owned analyses are reused without a second analysis charge.
- Comparison requests are idempotent per user and request key.
- Comparison results store the ranked inputs, plan, costs, source analysis IDs, and Arabic disclaimer.

## Plan limits

- Free: up to 3 stocks, no included monthly comparisons.
- Basic: up to 2 stocks, 4 included comparisons monthly.
- Advanced: up to 3 stocks, 12 included comparisons monthly.
- Pro: up to 5 stocks, 40 included comparisons monthly.

## Release

- Backend migration: `0014_stock_comparisons`.
- Mobile: `0.9.0+15`.

# Core v2.2 — elite opportunity quality

## Why this revision exists

Three persisted Core v2.1 historical replay windows showed two facts at the same time:

1. The directional engine and daily ranking could find strong opportunities in May–July.
2. In March, a fixed `score >= 80` elite rule selected late, volatile momentum and underperformed the same-day tested universe.

The product name **فرصة نخبوية** remains unchanged. Core v2.2 makes the classification harder to earn instead of weakening or renaming it.

## Changes

### Technical engine

The technical engine no longer gives the same positive momentum bonus to every 20-day move above 8%.

- 8%–20%: constructive momentum bonus.
- 20%–30%: treated as stretched, with no extra bonus.
- Above 30%: overextension penalty.
- RSI above 75 receives a stronger late-entry penalty.

Model marker: `technical-v2.2-overextension-aware`.

### Quantitative engine

The quantitative logit keeps normal momentum evidence but applies a nonlinear penalty after:

- 20-day momentum exceeds 30%; or
- 5-day momentum exceeds 15%.

The raw edge before and after the extension penalty is exported for auditing.

Model marker: `momentum-logit-v4-overextension-aware`.

### Elite quality engine

The new non-directional quality engine does not alter the directional weights. It decides whether a BUY is robust enough to be promoted to the elite tier.

A candidate must pass all of these checks:

- BUY signal and stock qualification;
- directional score of at least 80;
- aggregate confidence of at least 70;
- at least four bullish directional engines, no bearish engine, and no conflict;
- bullish market regime and bullish multi-timeframe alignment;
- 20-day return no greater than 30%;
- ATR no greater than 4.5%;
- total risk no greater than 30% and risk level not high;
- zero-volume ratio no greater than 10%.

Model marker: `elite-quality-v2.2`.

The output is stored under:

```text
analysis_quality.elite_assessment
```

A high-score BUY that fails any quality gate remains **شراء مشروط**. A candidate is labeled **فرصة نخبوية** only when both the daily Top 10 rank and the Core v2.2 quality assessment pass.

## Retrospective diagnostic

Applying only the two most influential quality controls (`20-day return <= 30%` and `ATR <= 4.5%`) to the previously exported score-80 Top 10 observations changed average excess return as follows:

| Replay window | Old fixed score-80 rule | Quality-controlled subset |
|---|---:|---:|
| March 2026 | -1.12% | +2.27% |
| 29 May–28 June 2026 | +2.25% | +2.35% |
| 29 June–29 July 2026 | +4.38% | +2.69% |

These are retrospective diagnostics on persisted replay rows, not a promise of future returns. A fresh Core v2.2 replay is required after deployment because the technical and quantitative scores themselves have changed.

## Safety boundaries

- Directional engine weights remain unchanged.
- Risk and qualification remain non-directional gates.
- Elite quality cannot upgrade WATCH or AVOID to BUY.
- The quality engine can only withhold the elite tier from an otherwise valid BUY.
- No database migration is required.

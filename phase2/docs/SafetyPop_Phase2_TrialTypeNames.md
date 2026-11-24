# SafetyPop Phase 2 — Trial-Type Names

Companion to `SafetyPop_Phase2_TrialDesign.md` and the PDF overview `SafetyPop_Phase2_TrialDesign.pdf`
(15 Sept 2026), both in this folder. Type letters A–J are unchanged
from Phase 1 and from the app's trial codes; the names below are labels for the same types.

## Framework

Every dual-task trial offers two routes to the reward:

- **Bubble Pop = physical-effort route.** Fixed, known cost: N_bub touches. No skill required.
- **Oddity = cognitive-effort route.** Cost depends on competence. With per-stage accuracy p under
  progressive elimination, expected cost is N_odd / p touches: N_odd(N_odd+1)/2 at chance
  (10 for 4-stim, 36 for 8-stim), N_odd at mastery.

Two factors, two levels each:

- **Physical effort** = bubble set size: Low = 4 bubbles, High = 8 bubbles.
- **Cognitive effort** = oddity set size: Low = 4-stim array, High = 8-stim array.

Break-even: Oddity is the cheaper route once p > p* = N_odd / N_bub. Only B has a reachable
break-even (0.5); C has none; A and D reach parity only at p = 1. The four route-choice cells are
named for that trajectory. Two-letter codes give physical then cognitive level (HL = High physical,
Low cognitive).

## Route choice (dual task) — the 2 × 2, 32 trials per session

| Type | Code | Name | Physical | Cognitive | Composition | Bubble cost | Oddity chance → mastery | p* | Predicted choice, chance → mastery | Role |
|---|---|---|---|---|---|---|---|---|---|---|
| A | LL | Parity-Low | Low | Low | 4 bub / 4 odd | 4 | 10 → ~4 | 1.0 | Bubble → indifference | Matched low-effort cell; H4 control; H1, H5, H7 |
| B | HL | Crossover | High | Low | 8 bub / 4 odd | 8 | 10 → ~4 | 0.5 | Near-indifferent → Oddity | Diagnostic cell (H3); only cell where Oddity ever becomes cheaper |
| C | LH | Anchor | Low | High | 4 bub / 8 odd | 4 | 36 → ~8 | none | Bubble → Bubble | Selectivity control (H4); strongest bubble preference at chance |
| D | HH | Parity-High | High | High | 8 bub / 8 odd | 8 | 36 → ~8 | 1.0 | Strong Bubble → indifference | Matched high-effort cell; H4 control; H1, H5, H7 |

Each runs 8 per session (2 polarity × 2 side × 2 passes), 80 per subject, 20 per polarity × side cell.

The discriminating test is B-vs-C: a flip in Crossover without one in Anchor is competence tracking;
a shift toward Oddity in every cell is a preference change.

## Same-route preference — 6 per session (H6)

| Type | Name | Framework label | Composition | Per session | Counterbalance | Role |
|---|---|---|---|---|---|---|
| E | Physical Preference | Low vs High physical, same route | 4 bub vs 8 bub | 2 | 2 side | Cheaper physical option taken? DV = first task completed |
| F | Cognitive Preference | Low vs High cognitive, same route | 4 odd vs 8 odd | 4 | 2 polarity × 2 side | Same on the Oddity route; each side has its own target |

## Forced single route — 12 per session

| Type | Name | Framework label | Composition | Per session | Counterbalance | Role |
|---|---|---|---|---|---|---|
| G | Physical Baseline-Low | Forced Low physical | 4 bub only | 2 | 2 side | Agency; latency and touch-rate reference |
| H | Physical Baseline-High | Forced High physical | 8 bub only | 2 | 2 side | Agency; latency and touch-rate reference |
| I | Competence Gauge-Low | Forced Low cognitive | 4 odd only | 4 | 2 polarity × 2 side | H2 accuracy signal; per-subject change-point that time-locks H3 |
| J | Competence Gauge-High | Forced High cognitive | 8 odd only | 4 | 2 polarity × 2 side | Same at the High cognitive level; polarity exploratory |

Totals: 50 per session, 500 per subject over 10 sessions (320 route-choice trials vs 240 in Phase 1).

## Stimulus notes carried into the PDF

- Bubble: inverted neutral face, cyan, carried over from Phase 1.
- Oddity: solid circles; target polarity-reversed vs distractors. Black-target (black among white) and
  white-target (white among black) arrays, 50/50, crossed with side in every oddity-containing type.
- Drawn on the mid-grey background the design doc specifies. Bubble colour and background are the two
  items still marked "confirm against the Phase 2 build".

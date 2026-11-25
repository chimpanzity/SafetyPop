# Results — Phase 2

Outputs of the scripts in `../analysis/`, built from `../data/processed/`. Nothing here is edited
by hand, and nothing here is an input to anything else.

| File | What it is |
|---|---|
| `results_Billy.txt`, `results_Ben.txt` | Printouts from `analyze_safetypop2.py`: competence, polarity, route choice by cell, the preregistered H3 test, switching, preference controls, ghost touches, within-trial monitoring, the race model, and the Phase 1 comparison |
| `results_across_subjects.txt` | Pooled ghost-touch test, cross-divider perseveration, Phase 1 side-switch rates for all five subjects |
| `figures/SafetyPop2_Billy_summary.png`, `SafetyPop2_Ben_summary.png` | Six-panel summary per subject from `figure_safetypop2.py`: competence by session, forced 4-circle cost by polarity, route choice by cell, the Crossover cell by session, within-trial monitoring, ghost touches against the adjusted chance |
| `figures/SafetyPop2_two_apes.png` | Both apes on the crossover cost curve (Experiment 1 open, Experiment 2 filled) and their Crossover-cell first-touch rates by session |
| `learning_flip.txt` | From `learning_flip.py`: errors on forced trials by session, oddity choice in each cell against the ape's own running 4-circle cost, the B-vs-C selectivity test, and ghost touches split at the break-even |
| `figures/SafetyPop2_learning_flip.png` | One row per ape: forced 4-circle cost by session against the break-even, then completed-by-Oddity and first-touch-on-Oddity by session for each cell |
| `figures/SafetyPop2_ghost_touches.png` | Ghost-touch rate against position-adjusted chance, per ape and pooled |

## Findings with five subjects (2026-11-24 compilation)

Headline numbers from `results_<Subject>.txt`; Billy and Ben now have 20 and 13 sessions, so the
figures below supersede the two-subject ones quoted in the Lilly deck.

| Subject | Sessions | Forced 4-circle cost, Phase 1 to Phase 2 | B first touch on oddity, Phase 1 to Phase 2 | A vs B first touch (price test) | Side switches |
|---|---|---|---|---|---|
| Arthur | 19 | 9.95 to 7.47 | 15% to 42% (p = 0.0001) | 49% vs 42%, p = 0.31 | 62% |
| Ben | 13 | 8.82 to 7.31 | 39% to 19% (p = 0.004) | 10% vs 19%, p = 0.08 | 8% |
| Billy | 19 | 8.45 to 6.77 | 26% to 89% (p < 1e-20) | 69% vs 89%, p < 1e-5, OR 3.9 | 82% |
| Evelyn | 12 | 8.52 to 6.54 | 55% to 62% (p = 0.57) | 50% vs 62%, p = 0.15 | 31% |
| Rowena | 7 | 8.28 to 8.39 | 25% to 34% (p = 0.28) | 45% vs 34%, p = 0.33 | 20% |

- Four of five crossed the break-even on forced 4-circle trials (Rowena, with seven sessions, has
  not); per-stage accuracy is above chance for all five, highest for Billy (0.56) and lowest for
  Arthur (0.32). Nobody is near mastery.
- Billy remains the only ape whose first touch tracks the price of the alternative (A vs B).
  Arthur's Crossover-cell first touch rose from 15% to 42% without an A-vs-B difference, and C is
  still never completed by oddity (0 of 156) while B is completed on 60%: his completion pattern is
  cost-sensitive, his first touch is not. Ben went backwards, as before. Evelyn and Rowena show no
  change the test can see.
- Ghost touches (H7) stay null and are now well powered: pooled 392 of 2,159 eligible trials,
  18.2% vs 17.7% adjusted chance, p = 0.57. No subject is individually above chance (Billy 20.9%
  vs 18.7%, p = 0.17, is the closest).
- Cross-divider perseveration (landing in the same grid cell after switching sides) is strong in
  Arthur (36% vs 24% chance), Billy (29% vs 25%) and Rowena (31% vs 23%), absent in Ben and Evelyn.
- The session-level correlation between competence and Crossover choice is not significant for any
  subject (the preregistered time-locked form of H3).

## Status of these numbers

Keep-earliest over the full booth dumps, with the twice-run and restarted sessions listed in
`../data/README.md` resolved in favour of the first run. The race-model and position-adjusted
ghost tests were developed after data collection and are exploratory.

# Results — Phase 2

Outputs of the scripts in `../analysis/`, built from `../data/processed/`. Nothing here is edited
by hand, and nothing here is an input to anything else.

| File | What it is |
|---|---|
| `results_Billy.txt`, `results_Ben.txt` | Printouts from `analyze_safetypop2.py`: competence, polarity, route choice by cell, the preregistered H3 test, switching, preference controls, ghost touches, within-trial monitoring, the race model, and the Phase 1 comparison |
| `results_across_subjects.txt` | Pooled ghost-touch test, cross-divider perseveration, Phase 1 side-switch rates for all five subjects |
| `figures/SafetyPop2_Billy_summary.png`, `SafetyPop2_Ben_summary.png` | Six-panel summary per subject from `figure_safetypop2.py`: competence by session, forced 4-circle cost by polarity, route choice by cell, the Crossover cell by session, within-trial monitoring, ghost touches against the adjusted chance |
| `figures/SafetyPop2_two_apes.png` | Both apes on the crossover cost curve (Experiment 1 open, Experiment 2 filled) and their Crossover-cell first-touch rates by session |

## Findings so far (Billy, 11 sessions; Ben, 10 sessions)

- Both apes crossed the break-even on the forced 4-circle trials: Billy 8.50 touches per array
  in Phase 1 to 7.33 in Phase 2, Ben 8.93 to 7.53. The gain comes almost entirely from
  white-target arrays, which pop out (about 6 touches); black-target arrays stay near 8 to 9.
  Neither ape reached mastery; accuracy at the two-stimulus stage stays near chance.
- Billy flipped in the Crossover cell (B, 8 bubbles vs 4 circles): first touch on oddity 87.5%
  (27% in Phase 1), completion by oddity 76% (28%). Choice tracks the price of the alternative:
  with the same 4-circle array he starts on oddity on 69% of A trials (4 bubbles) against 87.5%
  of B trials (8 bubbles), Fisher p = 0.003; C (8 circles, 4 bubbles) was never completed by
  oddity. In Phase 1, without competence, bubble count made no difference (28% vs 27%).
- Ben did not flip: B first touch 15% (43% in Phase 1), completion 22.5%, A, C and D 0 of 240.
  He sampled oddity in session 1 and stopped. Same place on the curve, opposite route.
- Billy alternates sides on 84% of consecutive touches, so his completion rates are reproduced
  by a strict-alternation race model fed with his forced-trial costs (85/67% predicted vs 84/68%
  observed for white/black arrays). First touch is the clean choice measure for him. Ben switches
  on 7% of touches, so his completion is a real decision.
- Within a trial both apes read the outcome of the first oddity touch: Billy finishes by oddity
  on 96% of B trials after a hit and 51% after a miss. His first touch does not read the
  polarity he can see before touching (91% vs 84%).
- Ghost touches (H7) are null so far: 74/332 vs 18.8% adjusted chance for Billy (p = 0.11),
  52/312 vs 17.6% for Ben (p = 0.70), pooled 126/644 vs 18.2% (p = 0.38). About 1,000 trials
  would be needed for 80% power at Billy's observed effect.
- H2 and H3 in their preregistered gradual, time-locked form are not supported: pop-out
  delivered most of the attainable competence within the first 100 trials, so there was no
  slow climb to test the flip against. The cross-sectional results above stand.

## Status of these numbers

Two subjects, with Billy's merge carrying the two open decisions listed in `../data/README.md`
(session 3 restart, session 9 missing trials). The race-model and position-adjusted ghost tests
were developed after data collection and are exploratory. Numbers here are the versions reviewed
on 2026-11-24.

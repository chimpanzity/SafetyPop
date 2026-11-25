# Analysis — Phase 2

Four scripts, run from the repository root in this order. Each takes `--subject <name>` or `--all`.

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `merge_safetypop2.py` | `../data/raw/<Subject>/` (`Partials/` included) | `../data/processed/SafetyPop2_<Subject>_AllSessions.xlsx` (sheets `All Sessions`, `Merge Log`) and a CSV of the `All Sessions` sheet |
| 2 | `derive_safetypop2.py` | the `_AllSessions.csv` | `../data/processed/SafetyPop2_<Subject>_Trials.csv`, one row per trial with the derived measures |
| 3 | `analyze_safetypop2.py` | the `_Trials.csv` files and `../../phase1/data/processed/SafetyPop_AllSubjects_CompleteSessions.xlsx` | `../results/results_<Subject>.txt`, `../results/results_across_subjects.txt` |
| 4 | `figure_safetypop2.py` | the `_Trials.csv` files and the Phase 1 workbook | `../results/figures/SafetyPop2_<Subject>_summary.png`, `SafetyPop2_two_apes.png` |

```
python phase2/analysis/merge_safetypop2.py --all
python phase2/analysis/derive_safetypop2.py --all
python phase2/analysis/analyze_safetypop2.py --all
python phase2/analysis/figure_safetypop2.py --all
```

Needs Python 3.10 or later with `pandas`, `numpy`, `scipy`, `openpyxl`, `matplotlib` and
`statsmodels` (the logistic model is skipped, with a note, if `statsmodels` is missing).
Rebuilding from a clean checkout reproduces every CSV, printout and figure byte for byte; the
workbooks differ only in their zip timestamps.

## `learning_flip.py`

Run after the pipeline. Writes `../data/processed/SafetyPop2_AllSubjects.csv` (every trial of the
five subjects in one file: raw columns, derived measures, and `RunningCost4`, the mean cost of
the previous 8 forced 4-circle trials), `../results/learning_flip.txt` (learning on forced
trials, oddity choice by cell against running cost, the B-vs-C selectivity test, ghost touches
split at the break-even) and two figures in `../results/figures/`.

## Merge rules (`merge_safetypop2.py`)

- Keep-earliest: for each (Session, Trial) the row with the earliest `TrialStart` is kept and
  later re-runs are dropped. Every kept row is rejoined with the file's separator and compared
  with its source line before anything is written.
- The `Merge Log` sheet lists flags (a file that contributes nothing, a session restarted from
  trial 1 instead of resumed, missing trial numbers, a session whose type composition differs from
  the 50-trial design, non-consecutive trials within a file), the source-file inventory,
  per-session coverage, and every dropped row beside the row kept in its place, with a check that
  the two rows carry the same `Code`.
- Flags do not change the merge. They are the list of things that need a decision or a note;
  `../data/README.md` has the current ones.

## Measures (`derive_safetypop2.py`)

The docstring at the top of the script defines every derived column. The ones the tests rest on:

| Measure | Definition |
|---|---|
| Per-stage accuracy | On forced oddity trials (I, J): the share of elimination stages whose first touch hit the target, leaving out the final stage, where one stimulus is left and a hit is certain. Chance is the mean of 1/k over the stages scored: 0.36 for a 4-stimulus array, 0.25 for 8 |
| Cost | Touches to clear a forced oddity array (`OddWins + OddErrors`): 10 at chance and 4 at mastery for 4 stimuli, 36 and 8 for 8 |
| Oddity first | The first touch of a dual-task trial landed on the oddity side |
| Completed by oddity | The trial ended by clearing the oddity array |
| Ghost touch | The first bubble touched sat in the oddity target's cell at that moment, using `TargetCellHistory`. Eligible trials are those where a bubble was touched and the target's cell held a bubble. The chance level is adjusted for the ape's own first-bubble cell habits, restricted to the bubble cells of each trial; the test is exact (Poisson-binomial) and two-sided |

## What `analyze_safetypop2.py` reports

Sections follow `../docs/SafetyPop_Phase2_TrialDesign.md`: H2 competence (per session, with a
single-step change-point at trial resolution and the gradual-gain regression), the exploratory
polarity analysis, H1/H3/H4 route choice by cell (A vs B and C vs D by Fisher's test, the paired
session comparison, and an additive logistic model with bubble count and circle count), H3 in its
preregistered form (choice against the subject's own competence over time), H5 switching,
H6 preference controls, H7 ghost touches with a power estimate, within-trial monitoring, the
race-model check on completion, and the Phase 1 comparison. The across-subjects file pools the
ghost-touch test, reports cross-divider perseveration, and lists the Phase 1 side-switch rates
for all five subjects. `../results/README.md` summarises the findings.

## Provenance

The four scripts were rebuilt on 2026-11-24 after the working session that produced the original
versions lost its sandbox. The merge reproduces the original counts exactly (Billy 607 rows read,
548 kept, 59 dropped; Ben 505, 500, 5) and the same three flags for Billy. The analysis reproduces
every figure quoted in that session's notes and in the Lilly deck, with one small difference:
Billy's competence change-point lands at trial 93 with LR = 16.0, where the original fit reported
trial 92 and LR = 17.9 (the rebuilt fit cuts only at trial boundaries and leaves out the final
single-stimulus stage).

## Requirements for anything added here

- Reads from `../data/raw/` or `../data/processed/`, writes to `../data/processed/` or
  `../results/`. Never writes into `../data/raw/`.
- Paths and options sit in a parameter block or command-line arguments at the top of the script.
- A merge keeps every retained row verbatim from its source file, records the source file per row,
  and logs every dropped row next to the row kept in its place.

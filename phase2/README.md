# Phase 2 — two-tone circle oddity

The oddity target is a circle of the opposite polarity to its distractors: black among white, or
white among black. Sessions are 50 trials. Output files are 33 columns and are named
`SafetyPop2_*`.

Collection started 2026-08-26 and is in progress. Ben and Billy have run so far.

## Why the stimuli changed

Phase 1 found no oddity discrimination at any set size, at any point in training. That makes
Bubble Pop the cheaper option in every core trial type, so the choice between the two tasks cannot
distinguish a subject tracking cost from one ignoring the oddity task altogether. Phase 2 uses a
discrimination the subjects can plausibly learn, so that the type B contrast (8 bubbles against 4
oddity stimuli) becomes diagnostic: a subject who has learned the discrimination should start
choosing Oddity there, and one who has not should not.

Because the target polarity alternates across trials, the task cannot be solved by a fixed
"touch the black one" rule.

Design: `docs/SafetyPop_Phase2_TrialDesign.pdf` is a two-page overview (15 Sept 2026); the full
text is in `docs/SafetyPop_Phase2_TrialDesign.md` and `docs/SafetyPop_Phase2_TrialTypeNames.md`.

## Data collected so far

| Subject | Sessions | Files | Sessions needing a merge |
|---|---|---|---|
| Ben | 1 to 10 | 13 | 2 (sessions 4 and 9) |
| Billy | 1 to 11 | 18 | 4 (sessions 3, 7, 8 and 9) |

All sessions reach 50 trials except **Billy session 9**, which covers trials 1 to 32 and 35 to 50.
Trials 33 and 34 are not in any file.

Two sessions need a decision before they can be merged:

- **Billy session 3** has a 40-trial file from 08-26 and a full 50-trial file from 08-27. The
  second is a complete independent run, not a resume. Keep-earliest would blend the two, taking
  trials 1 to 40 from the first run and 41 to 50 from the second. That is probably not what is
  wanted here.
- **Billy session 7** spans five files across four days, with overlapping and out-of-order ranges,
  one of them named `_correct_trial_number_`. The trial numbering needs checking before the merge
  is trusted.

## Columns

33 columns. The first 30 match Phase 1 except that `Face` is replaced by `Polarity`. The three
additions are:

| Column | Why it matters |
|---|---|
| `TargetCellHistory` | The oddity target's cell at every stage, not just at trial onset. In Phase 1 `TargetCellPos` was set at setup and never updated, so the target's position became unrecoverable after the first correct touch, which limited the ghost-touch analysis to zero-win trials. This column removes that limit. |
| `EventLog` | Per-trial event record |
| `TrialStart` | Trial onset timestamp |

Full column definitions will be written from the Phase 2 source once it is in `app/`.

## Layout

| Path | Contents |
|---|---|
| `app/` | Phase 2 task source. Not yet in the repository. |
| `data/raw/<Subject>/` | 31 session files, exactly as saved |
| `data/processed/` | Empty. Nothing merged yet. |
| `analysis/` | Empty. The Phase 2 merger is still to be written. |
| `results/` | Empty. |
| `docs/` | Trial design overview (PDF), full design text and trial type names |

## Still to add

- [ ] The Phase 2 task source and its `Stim/` assets
- [ ] `analysis/merge_safetypop2.py`, keep-earliest over 50-trial sessions
- [ ] Column definitions in `data/README.md`, written from the source
- [ ] A decision on Billy sessions 3 and 7 before either is merged

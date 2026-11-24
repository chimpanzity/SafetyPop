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

Both subjects are merged (`data/processed/`, 548 trials for Billy and 500 for Ben) and analysed
(`results/`). One session still needs a decision: **Billy session 3** has a 40-trial file from
08-26 and a full 50-trial file from 08-27, and the second is a complete independent run, not a
resume. The merge applies keep-earliest as it stands (1 to 40 from the first run, 41 to 50 from
the second) and flags it; the alternative is to keep the 08-27 run whole. Billy session 7's
numbering has been checked: every overlap trial carries the same `Code` in both files.

## Columns

33 columns. The first 30 match Phase 1 except that `Face` is replaced by `Polarity`. The three
additions are:

| Column | Why it matters |
|---|---|
| `TargetCellHistory` | The oddity target's cell at every stage, not just at trial onset. In Phase 1 `TargetCellPos` was set at setup and never updated, so the target's position became unrecoverable after the first correct touch, which limited the ghost-touch analysis to zero-win trials. This column removes that limit. |
| `EventLog` | Per-trial event record |
| `TrialStart` | Trial onset timestamp |

The full column table is in `data/README.md`, written from the files; it is to be checked against
the Phase 2 source once that is in `app/`.

## Layout

| Path | Contents |
|---|---|
| `app/` | Phase 2 task source. Not yet in the repository. |
| `data/raw/<Subject>/` | 31 session files, exactly as saved |
| `data/processed/` | Merged datasets and per-trial tables for Billy and Ben |
| `analysis/` | The pipeline: `merge_safetypop2.py`, `derive_safetypop2.py`, `analyze_safetypop2.py`, `figure_safetypop2.py` |
| `results/` | Printouts and figures for Billy and Ben, with a findings summary in its README |
| `docs/` | Trial design overview (PDF), full design text and trial type names |

## Still to add

- [ ] The Phase 2 task source and its `Stim/` assets
- [ ] Column definitions checked against the source
- [ ] A decision on Billy session 3 (keep-earliest blend, or the 08-27 run whole)
- [ ] Raw files for the remaining subjects, then the race-model check on each

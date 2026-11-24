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
Where they differ, the `.md` files are current: the break-even is defined there on cost (a 4-stim
array cleared in fewer than 8 touches), which the PDF expresses as "per-stage accuracy" of 0.5.

## Data collected so far

Target: 20 sessions per subject. From the full booth dumps (2026-11-24):

| Subject | Sessions in files | Complete | Trials kept | Incomplete | Dates |
|---|---|---|---|---|---|
| Arthur | 1 to 20 | 19 | 974 | S6 (24 trials) | 10-06 to 11-03 |
| Ben | 1 to 13, 19 | 13 | 665 | S19 (15 trials); 14 to 18 in no file | 08-26 to 09-17 |
| Billy | 1 to 20 | 19 | 998 | S9 (48 trials) | 08-26 to 09-23 |
| Evelyn | 1 to 12 | 12 | 600 | none | 08-26 to 09-23 |
| Rowena | 1 to 7 | 7 | 350 | none | 09-26 to 10-31 |

Rita (one complete session) and Liza (17 trials) were also tried; their files sit under their own
names and are merged but not analysed. All five target subjects are merged (`data/processed/`) and
analysed (`results/`).

Points that need a decision, all flagged in the merge logs and listed in `data/README.md`:

- Four sessions were run twice in full under the same session number: Billy 11 (09-08 and 09-09),
  Billy 19 and 20 (09-17 in the west booth, 09-23 in the east booth) and Evelyn 8 (09-09 and
  09-10). Keep-earliest keeps the first run of each; the second runs are extra sessions carrying a
  reused number.
- Restarts rather than resumes: Billy 3 (40 trials then a fresh 50), Billy 18 (21 trials, then a
  fresh run in the other booth the same day), Evelyn 7 and 9, Arthur 1 (a second 32-trial run on
  10-20 under session 1). Keep-earliest keeps the earlier run in each case.
- Ben's sessions 14 to 18 are in no file. His last file is session 19 on 09-16, 15 trials.
- One complete session on 10-20 (`SafetyPop2_TestSubject_S20_10-20-2026_13-29-05_finished.txt`,
  east booth) names no subject and is kept in `data/raw/Unassigned/`. Arthur ran in that booth
  seven minutes earlier under session 1.

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
| `data/raw/<Subject>/` | 113 session files, exactly as saved; `Unassigned/` holds one |
| `data/processed/` | Merged datasets for seven apes and per-trial tables for the five target subjects |
| `analysis/` | The pipeline: `merge_safetypop2.py`, `derive_safetypop2.py`, `analyze_safetypop2.py`, `figure_safetypop2.py` |
| `results/` | Printouts and figures for the five subjects, with a findings summary in its README |
| `docs/` | Trial design overview (PDF), full design text and trial type names |

## Still to add

- [ ] The Phase 2 collection build from a booth machine (the ApeTouch master copy holds only the 08-04 prototype, now in `app/prototype_2026-08-04/`)
- [ ] Column definitions checked against the source
- [ ] Decisions on the twice-run and restarted sessions listed above
- [ ] The subject of the unassigned 10-20 session
- [ ] Remaining sessions: Arthur 1, Ben 7, Billy 1, Evelyn 8, Rowena 13

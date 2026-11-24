# Data — Phase 2

## Layout

```
data/
  raw/
    <Subject>/             session files (SafetyPop2_*.txt), exactly as saved
    <Subject>/Partials/    session files that do not hold all 50 trials
  processed/               built from raw/ by the scripts in ../analysis/:
                           SafetyPop2_<Subject>_AllSessions.xlsx and .csv (merged, verbatim rows
                           plus SourceFile) and SafetyPop2_<Subject>_Trials.csv (per-trial measures)
```

A file sits in `Partials/` when it does not contain trials 1 to 50. That is decided by reading the
file, not from its name. The merge step works from file contents, so the folder is for a reader's
benefit only.

`.gitattributes` marks everything under `phase2/data/` as `-text`, so git stores those files byte
for byte and never converts their line endings.

## Raw session files

**Format.** As Phase 1: UTF-8 without a byte-order mark, CRLF line endings, one header line, then
one line per completed trial, fields separated by space-comma-space (` , `). A row is written only
when a trial is completed.

**Placeholder fields.** `Subject` is `TestSubject`, `Species` is `-`, and `Location` is `Orang1`.
All three are app defaults and must not be used in analysis or in a manuscript. The subject is
identified by the file name and the folder.

## Columns (33)

The first 30 match Phase 1, except that `Face` is replaced by `Polarity`. See
`../../phase1/data/README.md` for those definitions, with the following differences and additions,
checked against the Billy and Ben files.

| Column | Meaning |
|---|---|
| `Code` | Type letter, polarity code, side. Polarity codes: 1 black target, 2 white target, 0 no oddity. Example `B2L` |
| `Polarity` | `Black` (black target among white distractors) or `White` (white among black). Replaces Phase 1's `Face`. Blank on E, G and H |
| `DistractorType` | The distractor colour, the opposite of `Polarity`. Blank when there is no oddity |
| `Probe` | Always `N`: Phase 2 has no probe trials |
| `TargetCellPos`, `TargetSide` | As in Phase 1: the target's cell and side at onset (`B` on F trials, where each side has a target) |
| `FirstBubbleGhost` | As in Phase 1, but scored against the target's cell at the moment of the first bubble touch, not its onset cell. `../analysis/derive_safetypop2.py` recomputes it from `TargetCellHistory` and agrees with the app on every scored trial, including the 167 trials where the target had moved before the first bubble touch |
| `TargetCellHistory` | The oddity target's grid cell at every stage of the elimination: side letter then cell, separated by pipes (`L6|L8|L4|L9`). Starts with the onset target of each oddity side, then adds the new target cell after every correct touch, in order. Phase 1's `TargetCellPos` was fixed at setup and never reassigned, so after the first correct touch the target's position could not be recovered from the file. This column removes that limitation |
| `EventLog` | Every event with its time in ms from onset, separated by semicolons: `SETUP` (code, left task, right task); `STATE` (the visible cells and tags on each side, `cell:T`, `cell:D` or `cell:B`; `HIDDEN` while a side is hidden); `TOUCH` (side, cell, tag, stimulus index); `HIDE` (side); `END` (the task that completed). A touched side is hidden for about 500 ms |
| `TrialStart` | Local date and time of trial onset, ISO 8601 with milliseconds. The merge orders overlapping rows by this field |

On F trials `OddWins` and `OddErrors` count touches on both arrays.

- [ ] Check the table above against the Phase 2 source once it is in `../app/`.

## Sessions that span more than one visit

Same keep-earliest rule as Phase 1: when the same subject, session and trial number appears in
more than one file, the row from the earliest file is kept and the later ones are dropped. The
merge keeps retained rows verbatim, records the source file of every row, and logs each dropped
row next to the row kept in its place.

Six sessions need a merge: Ben 4 and 9, Billy 3, 7, 8 and 9. All six are merged in
`processed/` by `../analysis/merge_safetypop2.py`; the `Merge Log` sheet of each workbook lists
every dropped row beside the row kept in its place.

## What is in `processed/`

| Path | Contents |
|---|---|
| `SafetyPop2_<Subject>_AllSessions.xlsx` | `All Sessions` sheet: every retained trial, raw columns verbatim plus `SourceFile`. `Merge Log` sheet: flags, source-file inventory, per-session coverage against the 50-trial design, and every dropped row beside the row kept in its place |
| `SafetyPop2_<Subject>_AllSessions.csv` | The `All Sessions` sheet as CSV |
| `SafetyPop2_<Subject>_Trials.csv` | One row per trial with the derived measures (first touch, completion, per-stage outcomes, cost, switching, ghost touch); columns defined at the top of `../analysis/derive_safetypop2.py` |

Billy: 18 files, 607 rows read, 548 kept, 59 dropped, sessions 1 to 11. Ben: 13 files, 505 rows
read, 500 kept, 5 dropped, sessions 1 to 10. Every kept row is byte-identical to its source line.

## Open issues

- **Billy session 9 is incomplete.** Coverage is trials 1 to 32 and 35 to 50. Trials 33 and 34
  (one A trial and one I trial) are not in any file, so the session cannot be completed from what
  is here. The merged dataset carries the 48 trials.
- **Billy session 3 is not a resume.** The 08-26 file holds trials 1 to 40 and the 08-27 file holds
  all 50. The second looks like a complete independent run rather than a continuation. The merge
  applies keep-earliest as it stands, taking 1 to 40 from the first run and 41 to 50 from the
  second, and flags it. Decide whether to keep the 08-27 run whole instead; the alternative drops
  the 08-26 fragment.
- **Billy session 7 numbering checks out.** Five files across four days with overlapping and
  out-of-order ranges (1-11, 10-28, 25-36, 26-33, 33-50), one named `_correct_trial_number_`. The
  merge compared `Code` on all 64 overlap trials across both subjects and every pair agrees, so
  the trial numbers in these files are consistent with the design sequence. The
  `_correct_trial_number_` file re-runs trials 26 to 33 that the 09-01 and 09-02 13:14 files
  already hold, so it contributes no rows under keep-earliest.

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

Every session with more than one file is merged in `processed/` by `../analysis/merge_safetypop2.py`;
the `Merge Log` sheet of each workbook lists every dropped row beside the row kept in its place.
Files that were byte-identical copies of another file in the booth dumps were not added
(`..._S13_09-09-2026_13-31-46_Billyfinished.txt`, `..._S8_09-05-2026_13-39-01_ben_finished.txt`, which
is Billy's session 8 correction file under the wrong name, and the unnamed twins of the Evelyn S9
09-15 and Billy S11 09-08 files). Two repository names differ from the booth names because the
originals contain spaces and parentheses: `_Billy_t34__correct_trial_number_` and
`_billy_finisehd_correction_`.

## What is in `processed/`

| Path | Contents |
|---|---|
| `SafetyPop2_<Subject>_AllSessions.xlsx` | `All Sessions` sheet: every retained trial, raw columns verbatim plus `SourceFile`. `Merge Log` sheet: flags, source-file inventory, per-session coverage against the 50-trial design, and every dropped row beside the row kept in its place |
| `SafetyPop2_<Subject>_AllSessions.csv` | The `All Sessions` sheet as CSV |
| `SafetyPop2_<Subject>_Trials.csv` | One row per trial with the derived measures (first touch, completion, per-stage outcomes, cost, switching, ghost touch); columns defined at the top of `../analysis/derive_safetypop2.py` |

Arthur: 25 files, 1,012 rows read, 974 kept. Ben: 17 files, 670 read, 665 kept. Billy: 32 files,
1,242 read, 998 kept. Evelyn: 19 files, 719 read, 600 kept. Rowena: 11 files, 355 read, 350 kept.
Every kept row is byte-identical to its source line, and every overlap trial carries the same
`Code` in both files.

## Open issues

- **Sessions run twice in full under one number.** Billy 11 (09-08, 09-09), Billy 19 and 20
  (09-17 west booth, 09-23 east booth), Evelyn 8 (09-09, 09-10). Keep-earliest keeps the first run;
  the second runs are in the raw folders and in the Merge Log, and are not in the merged dataset.
- **Restarts rather than resumes.** Billy 18 (21 trials east booth, then a fresh run in the west
  booth the same day), Evelyn 7 (restarted at trial 27) and 9 (at trial 20), Arthur 1 (a second
  run on 10-20 of trials 19 to 50 under session 1, two weeks after the complete 10-06 session).
- **Ben sessions 14 to 18** are in no file; session 19 (09-16) stops at trial 15.
- **Arthur session 6** stops at trial 24 (10-09).
- **Unassigned:** a complete session-20 file from the east booth on 10-20 names no subject.

- **Billy session 9 is incomplete.** Coverage is trials 1 to 32 and 35 to 50. Trials 33 and 34
  (one A trial and one I trial) are not in any file, so the session cannot be completed from what
  is here; the 09-05 file stops at 32 and the 09-08 file resumes at 35, so they were most likely
  never run. Decision (2026-11-24): keep them as blank rows. The merged dataset has a row for each,
  with `Session`, `Trial` and the design columns `Code`, `Type`, `Polarity`, `Side` filled (I2R and
  A1L, read from the other subjects' runs of session 9, since the sequence for a session number is
  the same for every subject), every other column empty, and `SourceFile` set to
  `MISSING: trial in no file (blank row)`. In the `_Trials.csv` table they carry `Missing = 1`,
  and the analysis scripts leave them out. The merge adds such rows only for gaps inside a
  session, not for sessions that stop early.
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

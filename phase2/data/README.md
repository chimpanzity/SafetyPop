# Data — Phase 2

## Layout

```
data/
  raw/
    <Subject>/             session files (SafetyPop2_*.txt), exactly as saved
    <Subject>/Partials/    session files that do not hold all 50 trials
  processed/               built from raw/ by the scripts in ../analysis/
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
`../../phase1/data/README.md` for those definitions, with the following differences and additions.

| Column | Meaning |
|---|---|
| `Polarity` | Which way round the target is: a black target among white distractors, or white among black. Replaces Phase 1's `Face`. |
| `TargetCellHistory` | The oddity target's grid cell at every stage of the elimination, not just at onset. Phase 1's `TargetCellPos` was fixed at setup and never reassigned, so after the first correct touch the target's position could not be recovered from the file. This column removes that limitation. |
| `EventLog` | Per-trial event record |
| `TrialStart` | Trial onset timestamp |

- [ ] Write the full column table from the Phase 2 source once it is in `../app/`.

## Sessions that span more than one visit

Same keep-earliest rule as Phase 1: when the same subject, session and trial number appears in
more than one file, the row from the earliest file is kept and the later ones are dropped. The
merge keeps retained rows verbatim, records the source file of every row, and logs each dropped
row next to the row kept in its place.

Six sessions need a merge: Ben 4 and 9, Billy 3, 7, 8 and 9.

## Open issues

- **Billy session 9 is incomplete.** Coverage is trials 1 to 32 and 35 to 50. Trials 33 and 34 are
  not in any file, so the session cannot be completed from what is here.
- **Billy session 3 is not a resume.** The 08-26 file holds trials 1 to 40 and the 08-27 file holds
  all 50. The second looks like a complete independent run rather than a continuation. Applying
  keep-earliest would blend two separate runs, taking 1 to 40 from the first and 41 to 50 from the
  second. Decide which run to keep before merging.
- **Billy session 7 numbering needs checking.** Five files across four days with overlapping and
  out-of-order ranges (1-11, 10-28, 25-36, 26-33, 33-50), one named `_correct_trial_number_`. The
  union covers 1 to 50, but the correction in that file name means the trial numbers should be
  verified against the `Code` sequence before the merge is trusted.

# Data — Phase 1

## Layout

```
data/
  raw/
    <Subject>/                    session files (SafetyPop_*.txt), exactly as saved
    <Subject>/Partials/           session files that do not hold all 60 trials
  processed/
    merged_sessions/              one 60-trial file per multi-visit session
    merge_logs/                   audit log for each merge
    *.xlsx                        compiled workbooks
```

A file sits in `Partials/` when it does not contain trials 1 to 60. That is decided by reading the
file, not from its name: several files the operator named "finished" hold only the tail of a
session, and several outside a partials folder in the collection machine's own layout are partial.
The merge step works from file contents, so the folder is for a reader's benefit only.

`.gitattributes` marks everything under `phase1/data/` as `-text`, so git
stores those files byte for byte and never converts their line endings.

## Raw session files

**Name.** The app proposes `SafetyPop_<Subject>_S<session>_<MM-dd-yyyy>_<HH-mm-ss>`, where the
date and time are when the task page was opened. The operator adds the animal's name at the end
when saving (`..._arthur.txt`). That suffix, and the folder, are what identify the subject.

**Format.** UTF-8 without a byte-order mark, CRLF line endings. One header line, then one line
per completed trial. Fields are separated by space-comma-space (` , `). `TouchLog` contains bare
commas and semicolons but never that separator, so splitting on ` , ` is safe.

**What produces a row.** A row is written only when a trial is completed. An interrupted trial
leaves no row, and resuming after a pause restarts the current trial from the beginning. The file
holds whatever was in the app's data box when the operator pressed Save Data, so each run of the
page gives one file.

**Placeholder fields.** In the Phase 1 files checked so far, three fields hold app defaults and
must not be used in analysis or in a manuscript:

| Field | Value in the files | Use instead |
|---|---|---|
| `Subject` | `TestSubject` | The name in the file name or folder |
| `Species` | `-` | Chimpanzee |
| `Location` | `Orang1` | A station label, not a species or site. To be corrected before submission. |

## Columns, Phase 1 (30)

Taken from the v1.0 source in `app/` and checked against the two session files in the repository.

| Column | Meaning |
|---|---|
| `Subject`, `Species`, `Location` | App defaults, see above |
| `Date` | `MM-dd-yyyy`, the day the task page was opened |
| `Session` | Session number selected by the operator |
| `Trial` | Position in the session sequence, 1 to 60 |
| `Code` | Trial code: type letter, face code, side. Example `B2L` |
| `Type` | `A` to `J` |
| `Face` | Target face: `Happy`, `Angry` or `Fearful`. Blank on E, G and H |
| `Side` | `L` or `R`. On A to D, I and J: the side holding Oddity. On G and H: the side holding the bubbles. On E and F: the side holding the 4-stimulus set |
| `LTask`, `RTask` | Task on each side: `Bubble`, `Oddity` or `None` |
| `BubN`, `OddN` | Bubble and oddity set sizes. E rows record 0 and 0, and F rows record 0 and 4, although both sides are populated (4 and 8). Use the position columns for those types |
| `TargetCellPos` | Grid cell of the oddity target at trial onset: 1 to 12, numbered row by row in a grid 3 wide and 4 high. `-1` when there is no oddity target. Not updated when the target moves after a correct touch |
| `TargetSide` | `L` or `R`; `B` on F trials (a target on both sides); `-` when there is no oddity |
| `LeftPositions`, `RightPositions` | Cells occupied on each side at trial onset, separated by pipes |
| `Probe` | `Y` when the distractors are inverted faces of the target's emotion, otherwise `N` |
| `DistractorType` | `Neutral`, `Inverted`, or blank when there is no oddity |
| `CompletedBy` | `Bubble` or `Oddity`: the task whose completion ended the trial |
| `BubTouches` | Bubbles popped |
| `OddWins` | Touches on the oddity target |
| `OddErrors` | Touches on a distractor |
| `OddTwoStimWin` | The first choice made with two oddity stimuli left: `1` target, `0` distractor, `NA` if that stage was never reached |
| `FirstBubbleGhost` | A to D only. `1`: the first bubble touched sat in the cell matching the oddity target's onset cell. `2`: a different bubble. `3`: no bubble touched. `NA` on all other types |
| `LatencyFirstTouch_ms` | Trial onset to the first touch on any stimulus |
| `LatencyFirstTarget_ms` | Trial onset to the first touch on the oddity target. `-1` if it was never touched |
| `TrialTime_ms` | Trial onset to completion |
| `TouchLog` | Every touch in order, separated by semicolons. Each entry is `ms,side,task,stimIndex,cell,tag,bubTouches,oddWins`: time since onset, side touched, task on that side, stimulus slot (0 to 7), grid cell, `Bubble`, `Target` or `Distractor`, and the two running counts as they stood before the touch |

Face codes inside `Code`: 1 Happy, 2 Angry, 3 Fearful (neutral distractors); 4, 5, 6 the same
three emotions as probes (inverted distractors); 0 no face.

## Columns, Phase 2

Phase 2 files replace `Face` with `Polarity` and carry additional logging columns. Their
definitions will be written from the Phase 2 source and files once those are in the repository.

## Sessions that span more than one visit

A session that is not finished in one visit is resumed on a later visit, starting at or a few
trials before the stopping point so that no trial is skipped. The files of one session can
therefore overlap by a few trials.

**Keep-earliest rule.** When the same subject, session and trial number appears in more than one
file, the row from the earliest file is kept and the later ones are dropped. The merge keeps
retained rows verbatim, records the source file of every row, and logs each dropped row next to
the row kept in its place.

Why earliest. Overlapping rows are not duplicates. `Code` regenerates identically on resume, so
the design cell is reproducible, but `TargetCellPos` and the position grids are re-randomised, so
the later row is a fresh layout of the same cell. The later row also sits at the start of a visit,
where warm-up shows up as a long first-touch latency. Keeping the earliest row keeps the trial as
first encountered. It does not always give the better-looking record: Evelyn session 5 trial 4 is
retained at 121 s, almost all of it dead time, while the discarded 07-30 row ran 27 s.

Backup depth is set by the operator at each resume, not fixed. Observed depths across Phase 1 are
0 (a clean butt joint, Billy session 6), 2, 3, 4, 5, 6, 7 and one case of 17. Three sessions
(Ben 1, Billy 3, Evelyn 4) resumed at a trial well inside already-completed territory, which is
the failure mode that can leave a forward gap.

## What is in `data/processed/`

| Path | Contents |
|---|---|
| `merged_sessions/` | 20 merged session files, one per multi-visit session. Each holds trials 1 to 60. |
| `merge_logs/` | Audit log per merge: source files in date order, provenance by block, and a field-by-field diff of every overlap trial. 15 of the 20 merges have one; the five made before the audit log existed (Arthur 4, Billy 1, Evelyn 1, Rowena 5, Rowena 6) do not. |
| `SafetyPop_AllSubjects_CompleteSessions.xlsx` | Master workbook: 41 complete sessions, 2,460 trials, one sheet per subject plus a Summary sheet. Merged and single-visit sessions, with a `SourceFile` column per row. Excludes Arthur session 8, whose three partials cover trials 1 to 46 only. |
| `SafetyPop_AllSubjects_Overview_v2.xlsx` | Earlier cross-subject overview from the collection machine. |
| `SafetyPop_Arthur_AllSessions.xlsx` | Arthur's sessions, compiled on the collection machine. |

Every file in `merged_sessions/` has been checked against `data/raw/`: all 20 hold trials
1 to 60 with no gaps or duplicates, and every row is byte-identical to a row in a raw file for
that subject and session.

## Provenance notes

- Touch registration changed during Phase 1. The v1.0 build registers a touch on `MouseDown` and
  on `MouseEnter`; a later build uses `MouseDown` only. Rowena's sessions 1 to 10 were collected
  with the `MouseEnter` build.
- [ ] Record which build each of the other sessions used.
- `TargetCellPos` is set at trial setup and never reassigned. After each correct target touch the
  app kills the target and draws a new one at random from the surviving distractors, so the
  recorded cell is valid only until the first correct touch. Any analysis that needs the target's
  position later in a trial cannot get it from these files. Logging the current target cell per
  touch is on the list for the Phase 2 build.
- A session can span a month. Billy session 9 spans 32 days and Ben session 5 spans 33, so
  position within a session is not a usable time proxy for those.
- `CompletedBy` differs between the two instances of an overlap trial in 8 cases across Phase 1,
  4 of them on type B trials.
- Evelyn's files carry long mid-trial gaps far more often than the others: about 6 percent of her
  trials have a gap over 30 s inside the touch log or before the first touch, against 0.5 to 1.7
  percent for the other four. Her raw latency means are not usable without a stall filter.

# Data

## Layout

```
data/
  raw/
    phase1/<Subject>/    Phase 1 session files (SafetyPop_*.txt), exactly as saved
    phase2/<Subject>/    Phase 2 session files (SafetyPop2_*.txt), exactly as saved
  processed/             built from raw/ by the scripts in analysis/
```

Keep whatever subfolders the collection machine uses inside a subject's folder (for example a
folder of partial files). The merge step works from file contents, not from folder names.

`.gitattributes` marks everything under `data/raw/` as `-text`, so git stores those files byte
for byte and never converts their line endings.

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

## Provenance notes

- Touch registration changed during Phase 1. The v1.0 build registers a touch on `MouseDown` and
  on `MouseEnter`; a later build uses `MouseDown` only. Rowena's sessions 1 to 10 were collected
  with the `MouseEnter` build.
- [ ] Record which build each of the other sessions used.

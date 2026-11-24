# Task source — Phase 2

The build that wrote the `SafetyPop2_*` data files is **not** in the repository. It lives on the
booth machines. The ApeTouch master copy (`ApeTouch_18Apex_Master`, last built 2026-09-15) holds
only an earlier prototype of Phase 2, kept here in `prototype_2026-08-04/` for the record.

## What the collection build must have, from the data files

- Oddity stimuli are two-tone circles, with the target polarity alternating across trials
  (`Polarity` column, codes 1 black target and 2 white target in `Code`)
- 50-trial sessions, no probe trial types
- 33 columns: `Polarity` in place of `Face`, plus `TargetCellHistory`, `EventLog`, `TrialStart`
- `FirstBubbleGhost` scored against the target's cell at the moment of the first bubble touch
- the touched side hidden for about 500 ms after each touch

## `prototype_2026-08-04/`

| File | What it is |
|---|---|
| `SafetyPop2.xaml`, `SafetyPop2.xaml.vb` | "SafetyPop v2, simplified discrimination branch" (2026-08-04): a clone of the Phase 1 page in which the target is always a black diamond among empty black rings, and bubbles carry a black plus |
| `SafetyPopMenu.xaml`, `SafetyPopMenu.xaml.vb` | The menu page that offers SafetyPop (v1) and SafetyPop2 (v2) from the ApeTouch main menu |

The prototype differs from the collection build on every point above: fixed target (no
polarity), the canonical 60 trial codes, 30 columns with `Face`, no `TargetCellHistory`,
`EventLog` or `TrialStart`, and `FirstBubbleGhost` scored against the onset target cell. The
compiled `ApeTouch.exe` in the master copy contains neither `Polarity` nor `TargetCellHistory`,
so it is this prototype, not the collection build. No data in this repository came from it.
It loads the same `Stim/` sounds and background as Phase 1 (`../../phase1/app/Stim/`).

## Still to add

- [ ] The collection build of `SafetyPop2.xaml` and `SafetyPop2.xaml.vb`, from a booth machine

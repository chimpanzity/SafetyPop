# Task source

## What is here

| File | What it is |
|---|---|
| `SafetyPop.xaml`, `SafetyPop.xaml.vb` | The Phase 1 task: a WPF `Page` in VB.NET |
| `Set0empty.xaml`, `Set0empty.xaml.vb` | An empty page, kept as it was stored with the task source |

Version: **v1.0 as of 2026-05-12**. This copy has:

- the canonical 60-trial composition (`canonical60Codes`)
- 10 fixed session sequences, each a seeded shuffle of the 60 codes (seed = session number x 12345)
- touches registered on both `MouseDown` and `MouseEnter`, so sliding onto a stimulus counts as a touch

## Not a standalone project

The page runs as a task inside ApeTouch and will not build on its own. It expects the ApeTouch
host to provide:

- navigation back to `MenuScreen.xaml`
- the participant list and selection (`participantlist`, `selectedparticipant`)
- queue and lifecycle state (`CurrentQuePosition`, `JustFinished`, `Application.Current.Properties`, `My.Settings`)
- the MahApps.Metro styles used by the control screen

ApeTouch itself is not part of this repository.

The page is 2944 x 1080: an operator control screen (1920 wide) on the left and the ape's task
screen (1024 x 768) on the right.

## Assets the page loads from `Stim/`

Not in the repository yet.

| Kind | Files |
|---|---|
| Stimulus images | `Control.png` (bubble), `Happy.png`, `Anger.png`, `Fear.png`, `Neutral.png` |
| Background | `pmac_back1.png` |
| Sounds | `Bubble.wav`, `Click.wav`, `boop1.wav`, `DingDing.wav`, `silence.wav` |

Inverted faces (probe distractors) are the same images flipped in XAML, not separate files.

## Still to add

- [ ] The Phase 1 source as currently run. Changes made after this copy include extending the
      fixed sequences beyond 10 sessions and removing the `MouseEnter` handlers.
- [ ] The Phase 2 task source (the build that writes `SafetyPop2_` files)
- [ ] The `Stim/` folder

# Task source — Phase 1

## What is here

| File | What it is |
|---|---|
| `SafetyPop.xaml`, `SafetyPop.xaml.vb` | The Phase 1 task: a WPF `Page` in VB.NET |
| `Set0empty.xaml`, `Set0empty.xaml.vb` | An empty page, kept as it was stored with the task source |

Version: **the build of 2026-06-15** from the ApeTouch master copy (`ApeTouch_18Apex_Master`,
last built 2026-09-15). Compared with v1.0 of 2026-05-12, which is in this file's git history
(commit `0ba37bb`), it:

- registers touches on `MouseDown` only; v1.0 also counted `MouseEnter`, so sliding onto a stimulus
  registered as a touch. Rowena's sessions 1 to 10 were collected with the v1.0 behaviour
- generates 20 fixed session sequences instead of 10 (seeded shuffles of `canonical60Codes`,
  seed = session number x 12345), which is what allowed sessions 11 to 20

`SafetyPop.xaml` is unchanged between the two.

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

| Kind | Files | In the repository |
|---|---|---|
| Stimulus images | `Control.png` (bubble), `Anger.png`, `Happy.png`, `Fear.png`, `Neutral.png` | yes |
| Background | `pmac_back1.png` | yes |
| Sounds | `Bubble.wav`, `Click.wav`, `boop1.wav`, `DingDing.wav`, `silence.wav` | yes |

Inverted faces (probe distractors) are the same images flipped in XAML. `Anger_inv.png`,
`Happy_inv.png` and `Fear_inv.png` sit in the master copy's `Stim/` folder and are included, but the
source does not load them. The page has every asset it needs from this copy.

The page will not run from this copy until the five missing files are added.

## Still to add

- [ ] The Phase 1 source as currently run. Changes made after this copy include extending the
      fixed sequences beyond 10 sessions and removing the `MouseEnter` handlers.
- [ ] `Happy.png` and `Fear.png`, and the five `.wav` files

The Phase 2 task source lives in `../../phase2/app/`.

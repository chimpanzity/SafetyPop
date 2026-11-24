# SafetyPop

Touchscreen dual-task study of metacognitive task selection in great apes. The data collected
so far are from zoo-housed chimpanzees at the Indianapolis Zoo.

On a dual-task trial, two routes to the reward are on screen side by side:

- **Bubble Pop**: touch every bubble. Fixed physical cost, no skill required.
- **Oddity**: touch the odd stimulus at each stage of a progressive elimination. The cost depends on competence.

Bubble Pop takes the place of the single opt-out button of the classic opt-out paradigm, so the
opt-out decision is recorded touch by touch instead of as one button press.

Investigators: Christopher Flynn Martin (Indianapolis Zoo) and Jennifer Vonk (Oakland University).

## Layout

| Path | Contents |
|---|---|
| `app/` | Task source: a WPF page (VB.NET, XAML) that runs inside ApeTouch |
| `demo/` | Browser demo of the Phase 1 task (React) |
| `data/raw/` | Session files exactly as saved by the app. Never edited. |
| `data/processed/` | Merged datasets built from `data/raw/` by the scripts in `analysis/` |
| `analysis/` | Merge and analysis scripts (Python) |
| `docs/` | Preregistration and trial designs |

Each folder with something to explain has its own `README.md`.

## Experiments

| | Phase 1 (Experiment 1) | Phase 2 (Experiment 2) |
|---|---|---|
| Oddity stimuli | Emotion faces: angry, happy or fearful target among neutral distractors | Solid circles: black target among white distractors, or white among black |
| Trial types | 12 (A to J, plus A-probe and I-probe) | 10 (A to J) |
| Trials per session | 60 | 50 |
| Planned sessions per subject | 10 | 10 |
| Raw file prefix | `SafetyPop_` | `SafetyPop2_` |
| Design | `docs/SafetyPop_TrialDesign_430Final.pdf` | `docs/SafetyPop_Phase2_TrialDesign.md`, `docs/SafetyPop_Phase2_TrialTypeNames.md` |

The Phase 1 preregistration text (AsPredicted, H1 to H9) is in `docs/SafetyPop_Preregistration.pdf`.

## Trial types

| Type | On screen | Block |
|---|---|---|
| A | 4 bubbles and 4 oddity stimuli | Core dual task |
| B | 8 bubbles and 4 oddity stimuli | Core dual task |
| C | 4 bubbles and 8 oddity stimuli | Core dual task |
| D | 8 bubbles and 8 oddity stimuli | Core dual task |
| E | 4 bubbles vs 8 bubbles | Preference control |
| F | 4 oddity vs 8 oddity stimuli | Preference control |
| G | 4 bubbles only | Forced single task |
| H | 8 bubbles only | Forced single task |
| I | 4 oddity stimuli only | Forced single task |
| J | 8 oddity stimuli only | Forced single task |

Phase 1 also runs probe versions of A and I, in which the distractors are inverted faces of the
target's own emotion. Per-session counts and counterbalancing are in the design documents.

## Conventions

1. Files in `data/raw/` stay exactly as the app saved them: same bytes, same names. Corrections
   happen in the merge step, never in the raw files.
2. Everything in `data/processed/` is produced by a script in `analysis/` from `data/raw/`.
   Nothing there is edited by hand.
3. When a session spans more than one visit, overlapping trials are resolved with the
   keep-earliest rule described in `data/README.md`.

## Status (2026-11-24)

In the repository:

- `app/`: Phase 1 task source, v1.0 as of 2026-05-12
- `demo/`: Phase 1 browser demo
- `data/raw/phase1/`: two session files (Arthur S1 and Rowena S1, both 2026-05-19)
- `docs/`: preregistration, Phase 1 and Phase 2 trial designs

Still to add:

- [ ] Raw session files for all other sessions, both phases
- [ ] Current task source for both phases, with the `Stim/` images and sounds
- [ ] Merge and analysis scripts
- [ ] Merged datasets, rebuilt from `data/raw/` once the raw files are in

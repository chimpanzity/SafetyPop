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
| `data/processed/` | Merged datasets and compiled workbooks, built from `data/raw/` by the scripts in `analysis/` |
| `analysis/` | Merge and analysis scripts (Python) |
| `results/` | Figures and write-ups produced by `analysis/` |
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

## Data collected so far

Phase 1, five chimpanzees, collection running 2026-05-19 to 2026-07-30.

| Subject | Complete sessions | Trials | Of those, merged from more than one visit |
|---|---|---|---|
| Arthur | 1 to 7 | 420 | 1 |
| Ben | 1 to 9 | 540 | 5 |
| Billy | 1 to 10 | 600 | 6 |
| Evelyn | 1 to 5 | 300 | 5 |
| Rowena | 1 to 10 | 600 | 3 |
| **Total** | **41** | **2,460** | **20** |

One session is incomplete and is excluded from the master workbook: **Arthur session 8**, whose
three partial files cover trials 1 to 46. Trials 47 to 60 are not in any file.

## Status (2026-11-24)

In the repository:

- `app/`: Phase 1 task source, v1.0 as of 2026-05-12
- `demo/`: Phase 1 browser demo
- `data/raw/phase1/`: all 70 Phase 1 session files, complete and partial, for all five subjects
- `data/processed/phase1/`: 20 merged sessions with 15 audit logs, and three compiled workbooks
- `analysis/`: the session merger and the within-trial hazard analysis
- `results/`: Experiment 1 summary and figures
- `docs/`: preregistration, Phase 1 and Phase 2 trial designs, session metrics template

Still to add:

- [ ] Current task source for both phases, with the `Stim/` images and sounds
- [ ] The remaining analysis scripts (see `analysis/README.md`)
- [ ] Audit logs for the five merges made before the merger wrote them

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

The two phases run different tasks: different stimuli, different trial types, different session
length, and different columns in the output files. They are kept apart at the top level, and
nothing is shared between them.

```
phase1/      Emotion-face oddity. 60-trial sessions, 30-column files.
phase2/      Two-tone circle oddity. 50-trial sessions, 33-column files.
```

Each phase holds its own task source, data, analysis, documents and results:

| Path | Contents |
|---|---|
| `<phase>/app/` | Task source: a WPF page (VB.NET, XAML) that runs inside ApeTouch, with its `Stim/` assets |
| `<phase>/data/raw/<Subject>/` | Session files exactly as saved by the app. Never edited. |
| `<phase>/data/raw/<Subject>/Partials/` | Session files that do not hold a full session |
| `<phase>/data/processed/` | Merged datasets built from `raw/` by the scripts in `<phase>/analysis/` |
| `<phase>/analysis/` | Merge and analysis scripts (Python) |
| `<phase>/results/` | Figures and write-ups produced by `<phase>/analysis/` |
| `<phase>/docs/` | Preregistration and trial design for that phase |

Phase 1 also has `phase1/demo/`, a browser demo of the task. Each folder with something to
explain has its own `README.md`.

## The two phases

| | Phase 1 | Phase 2 |
|---|---|---|
| Oddity stimuli | Emotion faces: angry, happy or fearful target among neutral distractors | Two-tone circles: black target among white distractors, or white among black |
| Trial types | 12 (A to J, plus A-probe and I-probe) | 10 (A to J) |
| Trials per session | 60 | 50 |
| Raw file prefix | `SafetyPop_` | `SafetyPop2_` |
| Columns in the output file | 30 | 33 (`Polarity` replaces `Face`, plus `TargetCellHistory`, `EventLog`, `TrialStart`) |
| Subjects run so far | Arthur, Ben, Billy, Evelyn, Rowena | Ben, Billy |
| Collection dates | 2026-05-19 to 2026-07-30 | 2026-08-26 to 2026-09-08 |
| Status | Collection finished, analysed | Collection in progress |
| Design | `phase1/docs/SafetyPop_TrialDesign_430Final.pdf` | `phase2/docs/SafetyPop_Phase2_TrialDesign.pdf` (overview); full text in the two `.md` files beside it |

The Phase 1 preregistration (AsPredicted, H1 to H9) is in
`phase1/docs/SafetyPop_Preregistration.pdf`.

Phase 2 is not a continuation of Phase 1's analysis. Phase 1 established that these subjects
perform the emotion-face oddity task at chance at every set size, which makes Bubble Pop the
cheaper option in every trial type and leaves several preregistered hypotheses untestable. Phase 2
replaces the oddity stimuli with a discrimination the subjects can plausibly learn, so that the
choice between the two tasks becomes diagnostic. See `phase1/results/` for the Phase 1 findings
and `phase2/docs/` for the Phase 2 design.

## Trial types

Shared by both phases, though Phase 2 drops the probe versions.

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
target's own emotion. Per-session counts and counterbalancing are in each phase's design document.

## Conventions

Both phases follow the same rules.

1. Files in `data/raw/` stay exactly as the app saved them: same bytes, same names. Corrections
   happen in the merge step, never in the raw files.
2. A file sits in `<Subject>/Partials/` when it does not hold the full session. That is decided by
   reading the file, not from its name: several files the operator named "finished" hold only the
   tail of a session.
3. Everything in `data/processed/` is produced by a script in `analysis/` from `data/raw/`.
   Nothing there is edited by hand.
4. When a session spans more than one visit, overlapping trials are resolved with the
   keep-earliest rule described in each phase's `data/README.md`.

# SafetyPop Phase 2 — Trial Design

**50 trials per session · 10 trial types · faces removed**

Phase 2 strips the emotion manipulation out of the Oddity task and replaces it with a
two-level luminance-polarity manipulation — a discrimination that, unlike the Phase 1
oddity relation, subjects can plausibly acquire. The design's purpose is to observe opt-out
decision-making *during* acquisition: subjects should begin at chance, treat Bubble Pop as
the efficient option everywhere, and — if and when competence arrives — flip to Oddity in
exactly the one cell where competence makes it cheaper. All trial-type structure,
effort-cost logic, position constraints, and ghost-touch machinery transfer from Phase 1.

---

## What changed

| | Phase 1 | Phase 2 |
|---|---|---|
| Oddity target | Upright angry / happy / fearful emoji (gold) | Solid circle, polarity-reversed vs. distractors |
| Oddity distractor | Upright neutral emoji (gold) | Solid circle, opposite polarity to target |
| Stimulus factor | Emotion (3 levels) | Polarity (2 levels) |
| Probe trials | A-probe, I-probe | **Dropped** |
| Trial types | 12 | 10 |
| Trials per session | 60 | 50 |
| Trials per subject (10 sessions) | 600 | 500 |

**Polarity levels**

- **Black-target:** black circle target among white circle distractors
- **White-target:** white circle target among black circle distractors

Half of all oddity arrays use each. Polarity is fully crossed with side within every
oddity-containing trial type.

---

## Session composition (50 trials)

The base counterbalance pass for an oddity-containing type is **2 polarities × 2 sides = 4**.
The four core dual-task types (A–D) run **two full passes** for 8 trials each, weighting the
session toward the trials that carry H1–H4. Bubble-only types carry no stimulus factor and
remain at **2 (sides counterbalanced)**.

| Type | Description | Bub | Odd | N | Counterbalance |
|---|---|---|---|---|---|
| A | 4 bub / 4 odd (dual task) | 4 | 4 | 8 | 2 polarity × 2 side × 2 passes |
| B | 8 bub / 4 odd (dual task) | 8 | 4 | 8 | 2 polarity × 2 side × 2 passes |
| C | 4 bub / 8 odd (dual task) | 4 | 8 | 8 | 2 polarity × 2 side × 2 passes |
| D | 8 bub / 8 odd (dual task) | 8 | 8 | 8 | 2 polarity × 2 side × 2 passes |
| E | 4 bub vs 8 bub (preference) | 4+8 | — | 2 | 2 side |
| F | 4 odd vs 8 odd (preference) | — | 4+8 | 4 | 2 polarity × 2 side |
| G | 4 bub forced (agency) | 4 | — | 2 | 2 side |
| H | 8 bub forced (agency) | 8 | — | 2 | 2 side |
| I | 4 odd forced (agency) | — | 4 | 4 | 2 polarity × 2 side |
| J | 8 odd forced (agency) | — | 8 | 4 | 2 polarity × 2 side |
| **TOTAL** | | | | **50** | |

**Block totals:** Core (A–D) 32 · Preference (E, F) 6 · Agency (G–J) 12

---

## Why 50, and where the trials went

The Phase 1 count of 6 per oddity type was never arbitrary — it was `3 emotions × 2 sides`.
Two polarity levels make that base cell `2 × 2 = 4`, and the probes are gone because their
only function was controlling low-level feature saliency in the anger-superiority analysis;
with no emotion and no orientation manipulation, there is nothing for an inverted distractor
to control. One counterbalance pass across all ten types would give 34 trials.

Running the four core dual-task types at **two passes each** brings the session to **50** and
puts the recovered trials exactly where the main hypotheses live. Core trials rise from 24 of
60 in Phase 1 (40% of the session) to **32 of 50 (64%)**. Every count remains a whole multiple
of its counterbalance block, so polarity and side stay perfectly balanced within every type.

**Core cells now carry twice the Phase 1 data.** Phase 1 Type A gave 60 trials per subject
across 3 emotions × 2 sides = 10 per cell. Phase 2 Type A gives 80 trials across 2 polarities
× 2 sides = **20 per cell**. The control types (F, I, J) hold at 10 per cell, matching Phase 1
exactly.

**Session duration** lands near **12–13 minutes** at the Phase 1 rate, inside the 15-minute
slot. Ten sessions gives 500 trials per subject — fewer than Phase 1's 600, but 320 of them
core dual-task trials against Phase 1's 240.

---

## Unchanged from Phase 1

- 10 sessions per subject; same trial sequence across subjects
- Positions randomized at runtime with overlap constraint
- 4-stim side always a subset of 8-stim side positions (enables ghost-touch coding)
- Target always placed in an overlapping cell
- Progressive oddity elimination: N touches to complete an N-stim oddity array
- Bubble Pop mechanics: touch all bubbles, chime + removal per touch, reward on clearance
- All dependent variables (first task engaged, switches, touch counts, latencies, ghost touches)

---

## Hypotheses — competence and choice co-evolving

Phase 1 established that opt-out behaviour is exquisitely cost-calibrated (abandonment
tracked remaining cost with all five subjects showing significant cost sensitivity), but
Oddity competence never developed, so choices could only ever track a static cost
landscape. Phase 2's central question is whether choices *re-calibrate when the landscape
moves* — i.e., whether apes track their own emerging competence. The cost structure makes
one cell diagnostic and the rest controls.

**The break-even logic.** Under progressive elimination, random responding on an N-stim
Oddity array costs an expected N(N+1)/2 touches; competent responding costs ~N. So:

| Cell | Bubble cost | Oddity cost (chance) | Oddity cost (mastery) | Prediction at mastery |
|---|---|---|---|---|
| A (4b/4o) | 4 | 10 | ~4 | indifference |
| **B (8b/4o)** | **8** | **10** | **~4** | **flips to Oddity** |
| C (4b/8o) | 4 | 36 | ~8 | stays Bubble |
| D (8b/8o) | 8 | 36 | ~8 | indifference |

B is the only cell that crosses. Phase 1 data confirm the pre-learning state: bubble
preference was weakest in B (76.8%), exactly what near-indifference at chance-level
competence should look like. Per-stage accuracy of 0.5 is the approximate break-even at
which B inverts.

**Primary hypotheses:**

- **H1 (pre-learning state)** — While Oddity accuracy is at chance, Bubble Pop is chosen
  across all core cells, most strongly in C (as in Phase 1).
- **H2 (competence)** — Unlike Phase 1, accuracy on forced Oddity trials (I, J) rises above
  chance. The transition may be abrupt ("lightbulb") rather than gradual; no gradualness
  is assumed or required.
- **H3 (the flip — key metacognitive prediction)** — Oddity choice in Type B increases
  when, and only when, the subject's own per-stage accuracy (estimated from forced I/J
  trials) crosses the ~0.5 break-even. The flip should be time-locked to each subject's
  own competence crossing, not to session number.
- **H4 (selectivity controls)** — Type C does not flip at any competence level (Oddity
  never becomes cheaper there); A and D drift toward indifference. A general shift toward
  Oddity across all cells would indicate a preference change, not competence tracking —
  the B-vs-C contrast is the discriminating test.
- **H5 (switching)** — Fewer within-trial task switches as competence stabilises
  (replicates Phase 1 H4, which was supported).
- **H6 (preference controls)** — On E and F, subjects complete the fewer-stimuli side.
  Per the Phase 1 findings, the dependent variable is first task **completed**, not first
  touch (46.3% first-touch null traced to mid-trial side-switching; first touch measures
  a motor default, not the decision).
- **H7 (ghost touches)** — First-touched bubble on core trials is target-isomorphic above
  chance (0.25 on A/C, 0.125 on B/D). Null in Phase 1; retained because Phase 1 had no
  target representation to detect — Phase 2 provides the first meaningful test, gated on
  the subject having reached competence (H2).

**Analysis commitments:**

- **Trial resolution, not session resolution.** If the competence transition is abrupt and
  early, session aggregates will smear it. Competence (I/J accuracy) and choice (B-cell
  first-task-completed) are modelled at trial resolution using the discrete-time
  event-history framework developed in Phase 1, with the accuracy crossing estimated per
  subject (e.g., change-point fit) and choice modelled as a function of
  competence-relative time, not calendar time.
- **Scenario handling.** If a subject is above break-even from session 1 (pop-out too
  effective), the flip is unobservable for that subject: correct B-choice from the start
  is consistent with, but not evidence of, competence tracking. Such subjects contribute
  to H4–H7 but not H3. If a subject never exceeds chance, Phase 1's situation recurs and
  the subject contributes to H1 only.

**Dropped from Phase 1:** emotion hypotheses (anger superiority, response freezing,
emotion-driven opt-out) and the probe-vs-standard comparisons — all presupposed either an
emotion factor or a feature-saliency confound that no longer exists. All returned null in
Phase 1.

**Exploratory:** target polarity (black-on-white vs. white-on-black) as a fixed effect on
latency, touch count, and choice. Expected null; if non-null it is a salience asymmetry
and enters the primary models as a covariate rather than being averaged over.

---

## Open implementation items

1. **Bubble colour.** Phase 1 bubbles were inverted neutral faces in cyan, visually distinct
   from gold oddity stimuli. With oddity stimuli now black and white, confirm bubbles stay
   cyan/blue so the two tasks remain unambiguous at a glance.
2. **Background luminance.** A black target on white distractors against a given background
   is not perceptually symmetric with its reverse. Fixing a mid-grey background keeps the
   two polarity conditions comparable.
3. **Code changes.** `SafetyPop.xaml.vb` needs the emotion stimulus set replaced, the probe
   trial types removed, and the 60-trial sequence rebuilt at 50. Logging should record
   polarity in place of emotion so Phase 1 and Phase 2 output files stay parallel.
4. **Logging fix — `targetCellIndex`.** In Phase 1 the target position was fixed at trial
   setup and never reassigned after progressive elimination redrew the target, making the
   recorded position valid only until the first correct touch and restricting the
   ghost-touch analysis to 63.4% of trials. Phase 2 must log the target cell at every
   stage redraw so H7 gets a clean, full-coverage test.
5. **Preregistration.** Phase 2 needs its own AsPredicted entry built from the hypothesis
   section above — the B-flip prediction with its break-even table, the B-vs-C selectivity
   contrast, the trial-resolution analysis commitment, and the first-task-completed DV.

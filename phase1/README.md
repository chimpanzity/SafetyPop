# Phase 1 — emotion-face oddity

The oddity target is an emotional face (angry, happy or fearful) among neutral distractors.
Sessions are 60 trials. Output files are 30 columns and are named `SafetyPop_*`.

Collection ran 2026-05-19 to 2026-07-30 with five chimpanzees. It is finished.

## Data collected

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

## Layout

| Path | Contents |
|---|---|
| `app/` | Task source, v1.0 as of 2026-05-12, with its `Stim/` assets |
| `demo/` | Browser demo of the task (React) |
| `data/raw/<Subject>/` | 70 session files, exactly as saved |
| `data/processed/` | 20 merged sessions, 15 audit logs, three compiled workbooks |
| `analysis/` | Merge and analysis scripts |
| `results/` | Experiment 1 summary and figures |
| `docs/` | Preregistration (H1 to H9), trial design, session metrics template |

## Headline result

Replacing the opt-out button with a concurrent task shows that opting out is a graded,
within-trial process rather than a single decision. Of 1,148 core trials completed by Bubble Pop,
only 38 percent were up-front declines; the rest engaged the Oddity task first and left after
accruing errors. Leaving tracks the cost of the escape from the current moment, not a time limit.

The subjects never acquired the oddity discrimination: accuracy sits at chance at every set size,
including the 3-stimulus stage, across up to 600 trials each. Given chance performance, Bubble Pop
is the cheaper option in every core trial type, so the preference was economically correct. That
null is what motivates Phase 2.

Details, and every preregistered hypothesis with its outcome, are in
`results/SafetyPop_Experiment1_Summary.pdf`.

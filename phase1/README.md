# Phase 1 — emotion-face oddity

The oddity target is an emotional face (angry, happy or fearful) among neutral distractors.
Sessions are 60 trials. Output files are 30 columns and are named `SafetyPop_*`.

Collection ran 2026-05-19 to 2026-10-06 with five chimpanzees, with a target of 10 sessions each.
Five other apes were tried on the task as well (Cathy, Liza, Lucy, Rita, Sue); their files are
kept under their own names.

## Data collected (from the full booth dumps, 2026-11-24)

| Subject | Complete sessions | Incomplete sessions | Dates |
|---|---|---|---|
| Arthur | 10 (1 to 10) | none | 05-19 to 10-06 |
| Ben | 11 (1 to 11) | S12 (49 trials, 26 to 36 missing) | 06-01 to 08-10 |
| Billy | 11 (1 to 11) | none | 05-26 to 08-11 |
| Evelyn | 7 (1 to 5, 7, 10) | S6 (34 trials), S8 (50 trials), S9 (13 trials) | 06-03 to 08-11 |
| Rowena | 20 (1 to 20) | none | 05-19 to 08-05 |
| Cathy | 1 | none | 07-22 to 07-23 |
| Liza | 1 | S2 (28 trials) | 06-04 to 10-15 |
| Lucy | 0 | S1 (4 trials) | 06-29 |
| Rita | 0 | S1 (43 trials) | 08-13 to 09-29 |
| Sue | 1 | none | 08-04 to 09-15 |

Against the 10-session target, Arthur, Ben, Billy and Rowena are complete; Evelyn has 7 complete
sessions and three that stopped short. Ben and Billy have one session beyond the target and
Rowena ten. Arthur's session 9 (08-31) and session 10 (10-06) were run after his Phase 2 had
started on 10-06; Arthur's session 8 is complete now that its 07-16 file is in.

The earlier compilation (`data/processed/SafetyPop_AllSubjects_CompleteSessions.xlsx`, 41
sessions as of August) was built before the booth dumps were available. Five of its merged
sessions differ by a few rows from the keep-earliest merge over the full file set (see
`data/README.md`); the current compilation is `data/processed/SafetyPop_AllSubjects_AllSessions.xlsx`.

## Layout

| Path | Contents |
|---|---|
| `app/` | Task source, the 2026-06-15 build (MouseDown only, 20 session sequences), with every `Stim/` asset it loads |
| `demo/` | Browser demo of the task (React) |
| `data/raw/<Subject>/` | 148 session files, exactly as saved; `Unassigned/` holds three files whose subject the name does not give |
| `data/processed/` | 39 merged sessions with audit logs, the August compiled workbooks, and `SafetyPop_AllSubjects_AllSessions.xlsx` (every session, built by `analysis/compile_sessions.py`) |
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

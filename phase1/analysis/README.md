# Analysis — Phase 1

Python scripts that turn `data/raw/` into `data/processed/` and run the analyses.

Run them from the repository root; paths in each parameter block are relative to it.

## In the repository

| Script | Purpose |
|---|---|
| `merge_safetypop.py` | Merge the files of one multi-visit session under the keep-earliest rule. Validates trial continuity (no gaps, no duplicates, 1 to 60), copies retained rows byte for byte, and writes an audit log naming the source of every block and diffing every overlap trial. Edit the parameter block at the top per merge. |
| `hazard_analysis.py` | Within-trial hazard of abandoning Oddity for Bubble Popping. Discrete-time event-history model over Oddity-touch events, standard errors clustered by trial, with per-subject fits and a stratified model-free cross-check. Reads `phase1/data/processed/SafetyPop_AllSubjects_CompleteSessions.xlsx`. Needs `pandas`, `numpy`, `statsmodels`. |

Every merged file in `phase1/data/processed/merged_sessions/` has been checked to be reproducible from
`phase1/data/raw/`: all 20 contain trials 1 to 60 with no gaps, and every row is byte-identical to
a row in a raw file for that subject and session.

## Still to add

Written in earlier working sessions and not yet recovered into the repository:

- [ ] `build_workbook.py` — compiles the complete sessions into `SafetyPop_AllSubjects_CompleteSessions.xlsx`, one sheet per subject plus a Summary sheet with live counts and an exclusions table
- [ ] `analyze_safetypop.py` — per-session metrics and the checks against the preregistered hypotheses (H1 to H9)
- [ ] `figure_experiment1.py` — the four-panel figure in `results/figures/`
- [ ] `make_summary_pdf.py` — the Experiment 1 summary PDF in `results/`
- [ ] `divider_analysis.py` — conditional logit testing whether the screen divider organises behaviour (it does not when both sides carry the same task; it does when they carry different tasks)
- [ ] `retreat_ghost.py` — ghost-touch test at the moment of opting out
- [ ] `merge_safetypop2.py` — Phase 2 merge, one workbook per subject

The outputs of several of these are already in `phase1/data/processed/` and `phase1/results/`; the scripts
themselves were lost when the working sandbox was reset and need rewriting before those outputs
can be regenerated.

## Requirements for anything added here

- Reads from `phase1/data/raw/`, writes to `phase1/data/processed/` or `phase1/results/`. Never writes into `data/raw/`.
- Paths and options sit in a parameter block or command-line arguments at the top of the script.
- A merge keeps every retained row verbatim from its source file, records the source file per row,
  and logs every dropped row next to the row kept in its place.

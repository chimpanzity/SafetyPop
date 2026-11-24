# Analysis — Phase 2

Nothing here yet. Phase 2 files have a different schema from Phase 1 (33 columns, `Polarity`
instead of `Face`, 50-trial sessions), so the Phase 1 scripts do not apply unchanged.

## To write

- [ ] `merge_safetypop2.py` — keep-earliest merge over 50-trial sessions, audit log per merge.
      `../../phase1/analysis/merge_safetypop.py` is the starting point; the session length and the
      column count are the parts that change.
- [ ] `build_workbook2.py` — compile complete sessions into a workbook, one sheet per subject

## Requirements for anything added here

- Reads from `../data/raw/`, writes to `../data/processed/` or `../results/`. Never writes into
  `../data/raw/`.
- Paths and options sit in a parameter block or command-line arguments at the top of the script.
- A merge keeps every retained row verbatim from its source file, records the source file per row,
  and logs every dropped row next to the row kept in its place.

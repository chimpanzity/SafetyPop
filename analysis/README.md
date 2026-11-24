# Analysis

Python scripts that turn `data/raw/` into `data/processed/` and run the analyses.

No scripts are in the repository yet. The ones written in earlier working sessions, to be added here:

| Script | Purpose |
|---|---|
| `merge_session.py` | Merge the files of one multi-visit session (keep-earliest), check trial continuity, log what was kept and dropped |
| `merge_safetypop.py` | Phase 1 merge across subjects and sessions, keep-earliest, with an audit log per merge |
| `merge_safetypop2.py` | Phase 2 merge, one workbook per subject (`--subject <name>`) with an `All Sessions` sheet and a `Merge Log` sheet |
| `analyze_safetypop.py` | Per-session metrics and checks against the preregistered hypotheses |
| `make_progression_sheet.py` | Printable tracker of each subject's progress through the sessions |

## Requirements for anything added here

- Reads from `data/raw/`, writes to `data/processed/`. Never writes into `data/raw/`.
- Paths and options sit in a parameter block or command-line arguments at the top of the script.
- A merge keeps every retained row verbatim from its source file, records the source file per row,
  and logs every dropped row next to the row kept in its place.

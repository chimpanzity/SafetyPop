#!/usr/bin/env python3
"""
SafetyPop session merger — keep-earliest convention.

Merges partial session files produced when a subject does not finish all 60
trials in one visit. On resume, the app is restarted at a trial at or before
the last completed trial, producing an overlap block. Convention:

    KEEP-EAREST: for any trial present in more than one source file, the
    instance from the EARLIEST-dated source is retained verbatim; later
    re-presentations of the same trial are discarded.

Rows are preserved byte-for-byte (no recomputation, no blending). Provenance
is carried by the existing Date column; optionally a SourceFile column can be
appended via ADD_SOURCEFILE_COLUMN.
"""

# ============================ PARAMETERS =================================
# Paths are relative to the repository root. Edit this block per merge; the
# example below is the Rowena session 9 merge that is already in data/processed/phase1/.
SOURCE_FILES = [
    # List in chronological order (earliest visit first).
    "data/raw/phase1/Rowena/Partials/SafetyPop_TestSubject_S9_06-08-2026_13-23-59_Rowena40.txt",
    "data/raw/phase1/Rowena/Partials/SafetyPop_TestSubject_S9_06-10-2026_13-17-30_rowena_finsh.txt",
]
OUTPUT_FILE = "data/processed/phase1/merged_sessions/SafetyPop_TestSubject_S9_MERGED_rowena.txt"
AUDIT_FILE  = "data/processed/phase1/merge_logs/SafetyPop_TestSubject_S9_MERGED_rowena_auditlog.txt"

DELIM                  = " , "   # space-comma-space, as written by the app
EXPECTED_TRIALS        = 60      # full session length; None to skip the check
LINE_ENDING            = "\n"    # matches prior MERGED files
TRAILING_NEWLINE       = False   # matches prior MERGED files
ADD_SOURCEFILE_COLUMN  = False   # True appends a SourceFile column
SORT_BY_DATE           = True    # order SOURCE_FILES by earliest Date in file
# =========================================================================

import os
from datetime import datetime


def parse(path):
    with open(path, "r", newline="") as fh:
        raw = fh.read()
    lines = [l.rstrip("\r\n") for l in raw.splitlines() if l.strip()]
    header = lines[0]
    cols = [c.strip() for c in header.split(DELIM)]
    recs = []
    for line in lines[1:]:
        vals = [c.strip() for c in line.split(DELIM)]
        if len(vals) != len(cols):
            raise ValueError(f"{os.path.basename(path)}: column count "
                             f"{len(vals)} != header {len(cols)}")
        recs.append((dict(zip(cols, vals)), line))
    return header, cols, recs


def file_date(recs):
    ds = {r[0]["Date"] for r in recs}
    return min(datetime.strptime(d, "%m-%d-%Y") for d in ds)


def main():
    parsed = []
    for p in SOURCE_FILES:
        header, cols, recs = parse(p)
        parsed.append({"path": p, "header": header, "cols": cols,
                       "recs": recs, "date": file_date(recs)})

    headers = {p["header"] for p in parsed}
    if len(headers) != 1:
        raise ValueError("Source files have mismatched headers; cannot merge.")

    if SORT_BY_DATE:
        parsed.sort(key=lambda p: p["date"])

    kept, origin, dropped = {}, {}, []
    for p in parsed:
        tag = os.path.basename(p["path"])
        for rec, line in p["recs"]:
            t = int(rec["Trial"])
            if t in kept:
                dropped.append((t, tag, origin[t], rec, kept[t][0]))
            else:
                if ADD_SOURCEFILE_COLUMN:
                    line = line + DELIM + tag
                kept[t] = (rec, line)
                origin[t] = tag

    trials = sorted(kept)
    problems = []
    gaps = [t for t in range(trials[0], trials[-1] + 1) if t not in kept]
    if gaps:
        problems.append(f"MISSING TRIALS: {gaps}")
    if EXPECTED_TRIALS:
        if trials[0] != 1:
            problems.append(f"Sequence starts at trial {trials[0]}, expected 1")
        if trials[-1] != EXPECTED_TRIALS:
            problems.append(f"Sequence ends at trial {trials[-1]}, "
                            f"expected {EXPECTED_TRIALS}")

    header_out = parsed[0]["header"]
    if ADD_SOURCEFILE_COLUMN:
        header_out += DELIM + "SourceFile"
    body = [header_out] + [kept[t][1] for t in trials]
    text = LINE_ENDING.join(body) + (LINE_ENDING if TRAILING_NEWLINE else "")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as fh:
        fh.write(text)

    # ---- audit log ----
    L = []
    L.append("SafetyPop merge audit log")
    L.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    L.append("Rule: keep-earliest (first-dated source wins; rows verbatim)")
    L.append("")
    L.append("SOURCES (chronological):")
    for p in parsed:
        ts = sorted(int(r[0]["Trial"]) for r in p["recs"])
        L.append(f"  {p['date']:%m-%d-%Y}  {os.path.basename(p['path'])}"
                 f"  n={len(ts)}  trials {ts[0]}-{ts[-1]}")
    L.append("")
    L.append(f"OUTPUT: {os.path.basename(OUTPUT_FILE)}  n={len(trials)}  "
             f"trials {trials[0]}-{trials[-1]}")
    L.append("")
    L.append("PROVENANCE BY TRIAL BLOCK:")
    start, cur = trials[0], origin[trials[0]]
    for t in trials[1:] + [None]:
        if t is None or origin[t] != cur:
            end = trials[trials.index(t) - 1] if t is not None else trials[-1]
            L.append(f"  trials {start:>3}-{end:<3}  <- {cur}")
            if t is not None:
                start, cur = t, origin[t]
    L.append("")
    L.append(f"OVERLAP / DISCARDED ROWS (n={len(dropped)}):")
    if not dropped:
        L.append("  none")
    for t, src, keptsrc, drec, krec in dropped:
        L.append(f"  Trial {t}: kept {keptsrc} ({krec['Date']}), "
                 f"discarded {src} ({drec['Date']})")
        L.append(f"    design Code: kept={krec['Code']} discarded={drec['Code']}"
                 f"  {'MATCH' if krec['Code'] == drec['Code'] else '** MISMATCH **'}")
        diffs = [c for c in parsed[0]["cols"] if krec[c] != drec[c]]
        L.append(f"    fields differing: {', '.join(diffs)}")
    L.append("")
    L.append("VALIDATION: " + ("PASS - continuous, no gaps, no duplicates"
                               if not problems else "FAIL"))
    for pr in problems:
        L.append("  " + pr)
    with open(AUDIT_FILE, "w") as fh:
        fh.write("\n".join(L) + "\n")

    print("\n".join(L))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

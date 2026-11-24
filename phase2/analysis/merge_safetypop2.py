#!/usr/bin/env python3
"""Merge the Phase 2 session files of one subject into a single workbook.

    python phase2/analysis/merge_safetypop2.py --subject Billy
    python phase2/analysis/merge_safetypop2.py --all

Reads every ``SafetyPop2_*.txt`` under ``phase2/data/raw/<Subject>/`` (``Partials/`` included)
and writes ``phase2/data/processed/SafetyPop2_<Subject>_AllSessions.xlsx`` with two sheets:

* ``All Sessions``: one row per retained trial, the raw columns verbatim plus ``SourceFile``.
* ``Merge Log``: flags, the source-file inventory, per-session coverage and composition, and
  every dropped row beside the row kept in its place.

A CSV copy of the ``All Sessions`` sheet is written next to the workbook.

Keep-earliest rule. A session that spans more than one visit is resumed at or a few trials
before the stopping point, so its files overlap. When the same (Session, Trial) appears in
more than one file, the row with the earliest ``TrialStart`` is kept and the later re-runs are
dropped. Retained rows are never edited: joining a retained row's fields with the file's own
separator reproduces its source line byte for byte, and the script checks that before writing.
"""

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# ----------------------------------------------------------------------------- parameters
REPO = Path(__file__).resolve().parents[2]
PHASE = Path(__file__).resolve().parents[1]
RAW_DIR = PHASE / "data" / "raw"
OUT_DIR = PHASE / "data" / "processed"
SEP = " , "                       # field separator written by the app
TRIALS_PER_SESSION = 50
# Phase 2 session composition (phase2/docs/SafetyPop_Phase2_TrialDesign.md)
DESIGN = {"A": 8, "B": 8, "C": 8, "D": 8, "E": 2, "F": 4, "G": 2, "H": 2, "I": 4, "J": 4}
RESUME_OVERLAP_MAX = 5            # a later file re-running more trials than this is flagged as a restart
INT_RE = re.compile(r"^-?\d+$")
NAME_RE = re.compile(r"_S(\d+)_(\d\d)-(\d\d)-(\d{4})_(\d\d)-(\d\d)-(\d\d)")


def file_sort_key(path):
    """Session number, then the date-time in the file name (when the task page was opened)."""
    m = NAME_RE.search(path.name)
    if not m:
        return (0, "", path.name)
    s, mo, d, y, hh, mm, ss = m.groups()
    return (int(s), f"{y}-{mo}-{d}T{hh}:{mm}:{ss}", path.name)


def read_file(path):
    """Return (header_fields, rows). Each row is a dict with the fields, the verbatim line and
    the line number. Line endings are stripped; nothing else is touched."""
    text = path.read_bytes().decode("utf-8")
    lines = text.split("\r\n") if "\r\n" in text else text.split("\n")
    lines = [ln for ln in lines if ln.strip() != ""]
    header = lines[0].split(SEP)
    rows = []
    for n, line in enumerate(lines[1:], start=2):
        fields = line.split(SEP)
        if len(fields) != len(header):
            raise ValueError(f"{path.name} line {n}: {len(fields)} fields, header has {len(header)}")
        rows.append({"fields": fields, "line": line, "lineno": n})
    return header, rows


def merge(subject, raw_dir, out_dir, verbose=True):
    subj_dir = raw_dir / subject
    files = sorted((p for p in subj_dir.rglob("*.txt")), key=file_sort_key)
    if not files:
        sys.exit(f"No .txt files under {subj_dir}")

    header = None
    source = {}                       # file name -> list of row dicts
    for path in files:
        hdr, rows = read_file(path)
        if header is None:
            header = hdr
        elif hdr != header:
            raise ValueError(f"{path.name}: header differs from {files[0].name}")
        source[path] = rows
    col = {name: i for i, name in enumerate(header)}
    for needed in ("Session", "Trial", "Type", "Code", "TrialStart", "Polarity", "Side"):
        if needed not in col:
            raise ValueError(f"column {needed} missing from header")

    # ---- keep-earliest
    candidates = defaultdict(list)    # (session, trial) -> [(trialstart, file, row)]
    for path, rows in source.items():
        for r in rows:
            f = r["fields"]
            key = (int(f[col["Session"]]), int(f[col["Trial"]]))
            candidates[key].append((f[col["TrialStart"]], path, r))
    kept, dropped = {}, []            # key -> (file, row); list of (key, dropped, keptfor)
    for key, cands in candidates.items():
        cands.sort(key=lambda c: (c[0], file_sort_key(c[1])))
        kept[key] = (cands[0][1], cands[0][2])
        for c in cands[1:]:
            dropped.append((key, c[1], c[2], cands[0][1], cands[0][2]))

    # ---- verification: every retained row reproduces its source line
    for key, (path, r) in kept.items():
        assert SEP.join(r["fields"]) == r["line"], f"{path.name} line {r['lineno']} not verbatim"

    # ---- inventories and flags
    flags = []
    inventory = []
    for path in files:
        rows = source[path]
        sessions = sorted({int(r["fields"][col["Session"]]) for r in rows})
        trials = [int(r["fields"][col["Trial"]]) for r in rows]
        n_kept = sum(1 for r in rows if kept[(int(r["fields"][col["Session"]]), int(r["fields"][col["Trial"]]))][1] is r)
        starts = [r["fields"][col["TrialStart"]] for r in rows]
        inventory.append({
            "file": path.relative_to(raw_dir).as_posix(), "sessions": ", ".join(map(str, sessions)),
            "first_trial": min(trials), "last_trial": max(trials), "rows": len(rows),
            "kept": n_kept, "dropped": len(rows) - n_kept, "first_start": min(starts), "last_start": max(starts),
        })
        if n_kept == 0:
            flags.append(("File contributes nothing", path.name,
                          f"all {len(rows)} rows (trials {min(trials)}-{max(trials)}) were already covered by an earlier file"))
        # trial numbers within a file should be consecutive
        gaps = [(a, b) for a, b in zip(trials, trials[1:]) if b != a + 1]
        if gaps:
            flags.append(("Non-consecutive trials within a file", path.name,
                          "; ".join(f"{a} then {b}" for a, b in gaps)))
        if len(trials) != len(set(trials)):
            dup = [t for t, c in Counter(trials).items() if c > 1]
            flags.append(("Repeated trial number within a file", path.name, ", ".join(map(str, dup))))

    # restart vs resume: how many trials does each later file re-run?
    by_session = defaultdict(list)
    for path in files:
        for s in sorted({int(r["fields"][col["Session"]]) for r in source[path]}):
            by_session[s].append(path)
    for s, paths in by_session.items():
        covered = set()
        for path in paths:
            trials = {int(r["fields"][col["Trial"]]) for r in source[path] if int(r["fields"][col["Session"]]) == s}
            overlap = trials & covered
            if overlap and len(overlap) > RESUME_OVERLAP_MAX:
                flags.append(("Restart rather than resume", path.name,
                              f"session {s}: re-runs {len(overlap)} trials already recorded "
                              f"({min(overlap)}-{max(overlap)}); keep-earliest keeps the earlier run"))
            covered |= trials

    coverage = []
    for s in sorted(by_session):
        trials = sorted(t for (ss, t) in kept if ss == s)
        missing = sorted(set(range(1, TRIALS_PER_SESSION + 1)) - set(trials))
        extra = sorted(t for t in trials if t > TRIALS_PER_SESSION)
        types = Counter(kept[(s, t)][1]["fields"][col["Type"]] for t in trials)
        comp = " ".join(f"{k}{types.get(k, 0)}" for k in DESIGN)
        comp_ok = all(types.get(k, 0) == v for k, v in DESIGN.items()) and set(types) <= set(DESIGN)
        dates = sorted({kept[(s, t)][1]["fields"][col["Date"]] for t in trials})
        n_files = len(paths_for := sorted({kept[(s, t)][0].name for t in trials}))
        coverage.append({"session": s, "trials": len(trials), "missing": ", ".join(map(str, missing)) or "",
                         "extra": ", ".join(map(str, extra)) or "", "files": n_files, "dates": ", ".join(dates),
                         "composition": comp, "composition_ok": "yes" if comp_ok else "no"})
        if missing:
            flags.append(("Missing trials", f"session {s}", ", ".join(map(str, missing))))
        if extra:
            flags.append(("Trial numbers above 50", f"session {s}", ", ".join(map(str, extra))))
        if not comp_ok:
            flags.append(("Composition differs from design", f"session {s}", comp))
    for key, dpath, drow, kpath, krow in dropped:
        if drow["fields"][col["Code"]] != krow["fields"][col["Code"]]:
            flags.append(("Dropped row has a different code from the kept row", f"session {key[0]} trial {key[1]}",
                          f"{drow['fields'][col['Code']]} in {dpath.name} vs {krow['fields'][col['Code']]} in {kpath.name}"))

    # ---- write
    out_dir.mkdir(parents=True, exist_ok=True)
    order = sorted(kept)
    wb = Workbook()
    ws = wb.active
    ws.title = "All Sessions"
    ws.append(header + ["SourceFile"])
    for key in order:
        path, r = kept[key]
        ws.append([int(v) if INT_RE.match(v) else v for v in r["fields"]] + [path.name])
    ws.freeze_panes = "A2"
    for c in range(1, len(header) + 2):
        ws.column_dimensions[get_column_letter(c)].width = 12
    for name in ("TouchLog", "TargetCellHistory", "EventLog"):
        ws.column_dimensions[get_column_letter(col[name] + 1)].width = 40
    ws.column_dimensions[get_column_letter(col["TrialStart"] + 1)].width = 24
    ws.column_dimensions[get_column_letter(len(header) + 1)].width = 60
    for cell in ws[1]:
        cell.font = Font(bold=True)

    log = wb.create_sheet("Merge Log")
    bold = Font(bold=True)
    head_fill = PatternFill("solid", fgColor="DDDDDD")

    def title(text):
        log.append([])
        log.append([text])
        log.cell(row=log.max_row, column=1).font = Font(bold=True, size=12)

    def table(cols, rows):
        log.append(cols)
        for c in range(1, len(cols) + 1):
            log.cell(row=log.max_row, column=c).font = bold
            log.cell(row=log.max_row, column=c).fill = head_fill
        for row in rows:
            log.append(row)

    log.append([f"SafetyPop2 merge: {subject}"])
    log.cell(row=1, column=1).font = Font(bold=True, size=14)
    log.append(["Rule", "keep-earliest: for each (Session, Trial) the row with the earliest TrialStart is kept; later re-runs are dropped"])
    log.append(["Raw folder", subj_dir.relative_to(REPO).as_posix()])
    log.append(["Files read", len(files)])
    log.append(["Rows read", sum(len(r) for r in source.values())])
    log.append(["Rows kept", len(kept)])
    log.append(["Rows dropped", len(dropped)])
    log.append(["Sessions", ", ".join(map(str, sorted(by_session)))])
    log.append(["Verification", "every kept row rejoined with ' , ' equals its source line"])

    title("Flags (need a decision or a note; nothing here changes the merge)")
    if flags:
        table(["Flag", "Where", "Detail"], flags)
    else:
        log.append(["none"])

    title("Source files")
    table(["File", "Sessions", "First trial", "Last trial", "Rows", "Kept", "Dropped", "First TrialStart", "Last TrialStart"],
          [[i["file"], i["sessions"], i["first_trial"], i["last_trial"], i["rows"], i["kept"], i["dropped"], i["first_start"], i["last_start"]]
           for i in inventory])

    title("Per-session coverage")
    table(["Session", "Trials kept", "Missing", "Above 50", "Files", "Dates", "Composition (design A8 B8 C8 D8 E2 F4 G2 H2 I4 J4)", "Matches design"],
          [[c["session"], c["trials"], c["missing"], c["extra"], c["files"], c["dates"], c["composition"], c["composition_ok"]] for c in coverage])

    title("Dropped rows, each beside the row kept in its place")
    table(["Session", "Trial", "Dropped from", "Dropped TrialStart", "Dropped code", "Kept from", "Kept TrialStart", "Kept code", "Same code"],
          [[k[0], k[1], d.name, dr["fields"][col["TrialStart"]], dr["fields"][col["Code"]], kp.name, kr["fields"][col["TrialStart"]],
            kr["fields"][col["Code"]], "yes" if dr["fields"][col["Code"]] == kr["fields"][col["Code"]] else "no"]
           for k, d, dr, kp, kr in sorted(dropped, key=lambda x: (x[0], x[1].name))])
    log.column_dimensions["A"].width = 44
    log.column_dimensions["B"].width = 22
    log.column_dimensions["C"].width = 60
    for c in "DEFGHI":
        log.column_dimensions[c].width = 26
    for row in log.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top")

    xlsx = out_dir / f"SafetyPop2_{subject}_AllSessions.xlsx"
    wb.save(xlsx)
    csv_path = out_dir / f"SafetyPop2_{subject}_AllSessions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header + ["SourceFile"])
        for key in order:
            path, r = kept[key]
            w.writerow(r["fields"] + [path.name])

    if verbose:
        print(f"{subject}: {len(files)} files, {sum(len(r) for r in source.values())} rows read, "
              f"{len(kept)} kept, {len(dropped)} dropped, sessions {min(by_session)}-{max(by_session)}")
        for f in flags:
            print(f"  FLAG {f[0]} | {f[1]} | {f[2]}")
        print(f"  wrote {xlsx.relative_to(REPO)} and {csv_path.relative_to(REPO)}")
    return {"files": len(files), "read": sum(len(r) for r in source.values()), "kept": len(kept),
            "dropped": len(dropped), "flags": flags}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject", help="subject folder name under phase2/data/raw (for example Billy)")
    ap.add_argument("--all", action="store_true", help="merge every subject folder under phase2/data/raw")
    ap.add_argument("--raw", default=str(RAW_DIR), help=f"raw folder (default {RAW_DIR.relative_to(REPO)})")
    ap.add_argument("--out", default=str(OUT_DIR), help=f"output folder (default {OUT_DIR.relative_to(REPO)})")
    args = ap.parse_args()
    raw_dir, out_dir = Path(args.raw), Path(args.out)
    if args.all:
        subjects = sorted(p.name for p in raw_dir.iterdir() if p.is_dir())
    elif args.subject:
        subjects = [args.subject]
    else:
        ap.error("give --subject <name> or --all")
    for s in subjects:
        merge(s, raw_dir, out_dir)


if __name__ == "__main__":
    main()

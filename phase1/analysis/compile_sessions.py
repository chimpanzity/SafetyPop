#!/usr/bin/env python3
"""Compile every Phase 1 session from the raw files.

    python phase1/analysis/compile_sessions.py

For every subject folder under phase1/data/raw/ (Unassigned excluded) and every session in it:

* sessions held in more than one file are merged under the keep-earliest rule used by
  merge_safetypop.py (earliest-dated source wins per trial; rows verbatim; file-name time breaks
  ties on the same date) into phase1/data/processed/merged_sessions/SafetyPop_TestSubject_S<N>_<Subject>_MERGED.txt
  with an audit log in phase1/data/processed/merge_logs/ in the same format. A session that
  already has a MERGED file keeps its name; the file is rewritten only if the rows differ, which
  happens when a raw file that the original merge did not have has since surfaced.
* a single-file session is used as it is.

It then writes phase1/data/processed/SafetyPop_AllSubjects_AllSessions.xlsx: one sheet per
subject with every trial of every session, complete or not, plus SourceFile and a Summary sheet
of session coverage against the 60-trial design. The earlier compiled workbooks
(CompleteSessions, Overview_v2) are not touched.
"""

import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

PHASE = Path(__file__).resolve().parents[1]
RAW = PHASE / "data" / "raw"
PROC = PHASE / "data" / "processed"
MERGED = PROC / "merged_sessions"
LOGS = PROC / "merge_logs"
DELIM = " , "
EXPECTED = 60
# Files left out of the merge by decision (see phase1/data/README.md). Ben's session 1 was started
# on 05-20 and abandoned after 32 trials, then run again from trial 1 on 06-01; the 06-01 run is
# the session.
EXCLUDE = {
    "SafetyPop_TestSubject_S1_05-20-2026_13-04-13)_ben.txt",
    "SafetyPop_TestSubject_S1_05-20-2026_13-04-13_ben.txt",
}
NAME_RE = re.compile(r"_S(\d+)_(\d\d)-(\d\d)-(\d{4})_(\d\d)-(\d\d)-?(\d\d)?")


def parse(path):
    raw = path.read_bytes().decode("utf-8")
    lines = [l.rstrip("\r\n") for l in raw.splitlines() if l.strip()]
    cols = [c.strip() for c in lines[0].split(DELIM)]
    recs = []
    for line in lines[1:]:
        vals = [c.strip() for c in line.split(DELIM)]
        if len(vals) != len(cols):
            raise ValueError(f"{path.name}: {len(vals)} fields vs header {len(cols)}")
        recs.append((dict(zip(cols, vals)), line))
    return lines[0], cols, recs


def sort_key(path, recs):
    date = min(datetime.strptime(r[0]["Date"], "%m-%d-%Y") for r in recs)
    m = NAME_RE.search(path.name)
    t = f"{m.group(5)}{m.group(6)}{m.group(7)}" if m else ""
    return (date, t, path.name)


def merge(subject, session, paths):
    parsed = []
    for p in paths:
        header, cols, recs = parse(p)
        parsed.append({"path": p, "header": header, "cols": cols, "recs": recs, "key": sort_key(p, recs)})
    if len({p["header"] for p in parsed}) != 1:
        raise ValueError(f"{subject} S{session}: headers differ")
    parsed.sort(key=lambda p: p["key"])
    kept, origin, dropped = {}, {}, []
    for p in parsed:
        tag = p["path"].name
        for rec, line in p["recs"]:
            t = int(rec["Trial"])
            if t in kept:
                dropped.append((t, tag, origin[t], rec, kept[t][0]))
            else:
                kept[t] = (rec, line)
                origin[t] = tag
    trials = sorted(kept)
    problems = []
    gaps = [t for t in range(1, EXPECTED + 1) if t not in kept]
    if gaps:
        problems.append(f"MISSING TRIALS: {gaps}")
    if trials[-1] > EXPECTED:
        problems.append(f"Trial numbers above {EXPECTED}: {[t for t in trials if t > EXPECTED]}")
    return parsed, kept, origin, dropped, trials, problems


def audit_text(parsed, out_name, kept, origin, dropped, trials, problems):
    L = ["SafetyPop merge audit log", f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
         "Rule: keep-earliest (first-dated source wins; rows verbatim)", "", "SOURCES (chronological):"]
    for p in parsed:
        ts = sorted(int(r[0]["Trial"]) for r in p["recs"])
        L.append(f"  {p['key'][0]:%m-%d-%Y}  {p['path'].name}  n={len(ts)}  trials {ts[0]}-{ts[-1]}")
    L += ["", f"OUTPUT: {out_name}  n={len(trials)}  trials {trials[0]}-{trials[-1]}", "", "PROVENANCE BY TRIAL BLOCK:"]
    start, cur = trials[0], origin[trials[0]]
    for i, t in enumerate(trials[1:] + [None], start=1):
        if t is None or origin[t] != cur:
            end = trials[i - 1]
            L.append(f"  trials {start:>3}-{end:<3}  <- {cur}")
            if t is not None:
                start, cur = t, origin[t]
    L += ["", f"OVERLAP / DISCARDED ROWS (n={len(dropped)}):"]
    if not dropped:
        L.append("  none")
    cols = parsed[0]["cols"]
    for t, src, keptsrc, drec, krec in dropped:
        L.append(f"  Trial {t}: kept {keptsrc} ({krec['Date']}), discarded {src} ({drec['Date']})")
        L.append(f"    design Code: kept={krec['Code']} discarded={drec['Code']}  {'MATCH' if krec['Code'] == drec['Code'] else '** MISMATCH **'}")
        L.append(f"    fields differing: {', '.join(c for c in cols if krec[c] != drec[c])}")
    L += ["", "VALIDATION: " + ("PASS - continuous, no gaps, no duplicates" if not problems else "FAIL")]
    L += ["  " + pr for pr in problems]
    return "\n".join(L) + "\n"


def existing_merged(subject, session):
    for p in MERGED.glob(f"SafetyPop_TestSubject_S{session}_*MERGED*.txt"):
        if subject.lower() in p.name.lower():
            return p
    return None


def main():
    MERGED.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    subjects = sorted(p.name for p in RAW.iterdir() if p.is_dir() and p.name != "Unassigned")
    summary = []
    sheets = {}
    header_cols = None
    for subject in subjects:
        files = sorted((RAW / subject).rglob("*.txt"))
        by_session = defaultdict(list)
        for p in files:
            if p.name in EXCLUDE:
                continue
            m = NAME_RE.search(p.name)
            by_session[int(m.group(1))].append(p)
        rows = []
        for session in sorted(by_session):
            paths = by_session[session]
            parsed, kept, origin, dropped, trials, problems = merge(subject, session, paths)
            header_cols = header_cols or parsed[0]["cols"]
            n_files = len(paths)
            out = existing_merged(subject, session)
            if n_files > 1:
                name = f"SafetyPop_TestSubject_S{session}_{subject}_MERGED.txt"
                text = "\n".join([parsed[0]["header"]] + [kept[t][1] for t in trials])
                if out is None:
                    out = MERGED / name
                    out.write_bytes(text.encode("utf-8"))
                    (LOGS / name.replace(".txt", "_auditlog.txt")).write_text(
                        audit_text(parsed, name, kept, origin, dropped, trials, problems), encoding="utf-8")
                    status = "merged"
                else:
                    same = out.read_bytes().decode("utf-8").rstrip("\n") == text
                    if same:
                        status = "existing merge, same rows"
                    else:
                        out.write_bytes(text.encode("utf-8"))
                        (LOGS / out.name.replace(".txt", "_auditlog.txt")).write_text(
                            audit_text(parsed, out.name, kept, origin, dropped, trials, problems), encoding="utf-8")
                        status = "existing merge rebuilt (new source file surfaced)"
            else:
                status = "single file"
            complete = not problems
            dates = sorted({r[0]["Date"] for p in parsed for r in p["recs"]})
            summary.append([subject, session, len(trials), "yes" if complete else "no", n_files, len(dropped),
                            "; ".join(problems) or "", dates[0], dates[-1], status,
                            out.name if out else paths[0].name])
            for t in trials:
                rec, line = kept[t]
                rows.append([rec[c] for c in header_cols] + [origin[t], "yes" if complete else "no"])
        sheets[subject] = rows
    # workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Subject", "Session", "Trials", "Complete", "Files", "Dropped rows", "Problems", "First date", "Last date", "Merge status", "Session file"])
    for r in summary:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "A2"
    int_re = re.compile(r"^-?\d+$")
    for subject, rows in sheets.items():
        s = wb.create_sheet(subject)
        s.append(header_cols + ["SourceFile", "SessionComplete"])
        for c in s[1]:
            c.font = Font(bold=True)
        for r in rows:
            s.append([int(v) if isinstance(v, str) and int_re.match(v) else v for v in r])
        s.freeze_panes = "A2"
    out = PROC / "SafetyPop_AllSubjects_AllSessions.xlsx"
    wb.save(out)
    print(f"{'subject':8s} {'S':>3} {'n':>3} compl files drop  status")
    for r in summary:
        print(f"{r[0]:8s} {r[1]:>3} {r[2]:>3} {r[3]:>5} {r[4]:>5} {r[5]:>4}  {r[9]}  {r[6]}")
    print("wrote", out.relative_to(PHASE.parent))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Per-trial metrics for the Phase 2 datasets.

    python phase2/analysis/derive_safetypop2.py --subject Billy
    python phase2/analysis/derive_safetypop2.py --all

Reads ``phase2/data/processed/SafetyPop2_<Subject>_AllSessions.csv`` (made by
merge_safetypop2.py) and writes ``phase2/data/processed/SafetyPop2_<Subject>_Trials.csv``, one
row per trial with the raw design columns plus the measures the analyses use. Nothing here is
a test; analyze_safetypop2.py reads the output of this script.

Touch-level fields are parsed from ``TouchLog`` (``ms,side,task,stimIndex,cell,tag,bubTouches,
oddWins`` per touch, the two counts as they stood before the touch) and ``TargetCellHistory``
(the oddity target's cell at each stage of the progressive elimination, side letter then cell).

Derived columns
---------------
GlobalTrial            running index over the subject's kept trials, in session and trial order
OddTouches             OddWins + OddErrors: touches spent on the oddity side
TotalTouches           all touches in the log
FirstSide, FirstTask   side and task of the first touch
OddityFirst            1 if the first touch was on the oddity side (dual-task types A to D)
CompletedByOddity      1 if the trial ended by completing the oddity array
FirstOddTag            Target or Distractor: outcome of the first touch on the oddity side
StagesTotal            oddity stages reached (stages whose first touch exists)
StagesCorrect          stages whose first touch hit the target
StageOutcomes          the per-stage first-touch outcomes in order, T target or D distractor (for example TDTT)
Cost                   OddTouches, meaningful on forced oddity trials (I, J)
TouchPairs             consecutive touch pairs
SideSwitches           pairs whose two touches are on different sides
MeanIntervalSwitch     mean ms between touches on different sides
MeanIntervalStay       mean ms between touches on the same side
ChoseFourSide          E and F only: 1 if the completing touch was on the 4-stimulus side
FirstBubbleCell        cell of the first bubble touch (A to D)
TargetAtFirstBubble    oddity target's cell when that bubble was touched
GhostEligible          1 if that target cell held a bubble, so a ghost touch was possible
Ghost                  1 if the first bubble touched sat in the target's cell at that moment
GhostApp               the app's own FirstBubbleGhost flag, for comparison (1 ghost, 2 other, 3 none)
Missing                1 for a blank row standing in for a trial that is in no file; every measure is blank
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
DUAL = {"A", "B", "C", "D"}
FORCED_ODD = {"I", "J"}


def parse_touches(log):
    touches = []
    if isinstance(log, str) and log.strip():
        for entry in log.split(";"):
            ms, side, task, idx, cell, tag, bub, odd = entry.split(",")
            touches.append({"ms": int(ms), "side": side, "task": task, "idx": int(idx), "cell": int(cell),
                            "tag": tag, "bub": int(bub), "odd": int(odd)})
    return touches


def parse_history(hist):
    if not isinstance(hist, str) or not hist.strip():
        return []
    return [(h[0], int(h[1:])) for h in hist.split("|")]


def stage_outcomes(touches, side=None):
    """Per-stage first-touch outcomes on the oddity side (optionally one side only, for F).
    A stage ends with a Target touch; the stage's outcome is the tag of its first touch."""
    out = []
    first_of_stage = True
    for t in touches:
        if t["task"] != "Oddity" or (side and t["side"] != side):
            continue
        if first_of_stage:
            out.append(1 if t["tag"] == "Target" else 0)
            first_of_stage = False
        if t["tag"] == "Target":
            first_of_stage = True
    return out


def derive_row(r):
    touches = parse_touches(r["TouchLog"])
    hist = parse_history(r["TargetCellHistory"])
    d = {}
    d["OddTouches"] = int(r["OddWins"]) + int(r["OddErrors"])
    d["TotalTouches"] = len(touches)
    d["FirstSide"] = touches[0]["side"] if touches else ""
    d["FirstTask"] = touches[0]["task"] if touches else ""
    d["OddityFirst"] = int(d["FirstTask"] == "Oddity") if r["Type"] in DUAL and touches else np.nan
    d["CompletedByOddity"] = int(r["CompletedBy"] == "Oddity")
    odd_touches = [t for t in touches if t["task"] == "Oddity"]
    d["FirstOddTag"] = odd_touches[0]["tag"] if odd_touches else ""
    if r["Type"] == "F":
        # each side has its own array; score the side that was completed
        done_side = touches[-1]["side"] if touches else None
        so = stage_outcomes(touches, done_side)
    else:
        so = stage_outcomes(touches)
    d["StagesTotal"] = len(so)
    d["StagesCorrect"] = int(sum(so))
    d["StageOutcomes"] = "".join("T" if x else "D" for x in so)
    d["Cost"] = d["OddTouches"] if r["Type"] in FORCED_ODD else np.nan
    pairs = list(zip(touches, touches[1:]))
    d["TouchPairs"] = len(pairs)
    sw = [b["side"] != a["side"] for a, b in pairs]
    d["SideSwitches"] = int(sum(sw))
    iv_sw = [b["ms"] - a["ms"] for (a, b), s in zip(pairs, sw) if s]
    iv_st = [b["ms"] - a["ms"] for (a, b), s in zip(pairs, sw) if not s]
    d["MeanIntervalSwitch"] = float(np.mean(iv_sw)) if iv_sw else np.nan
    d["MeanIntervalStay"] = float(np.mean(iv_st)) if iv_st else np.nan
    # E and F: Side is the side holding the 4-stimulus set; the last touch completes the trial
    d["ChoseFourSide"] = int(touches[-1]["side"] == r["Side"]) if r["Type"] in {"E", "F"} and touches else np.nan
    # ghost touch: first bubble touched vs the target cell current at that moment
    d["FirstBubbleCell"] = np.nan
    d["TargetAtFirstBubble"] = np.nan
    d["GhostEligible"] = np.nan
    d["Ghost"] = np.nan
    d["GhostApp"] = r["FirstBubbleGhost"]
    if r["Type"] in DUAL:
        bubs = [t for t in touches if t["task"] == "Bubble"]
        bub_side = "L" if r["LTask"] == "Bubble" else "R"
        bub_cells = {int(c) for c in str(r["LeftPositions" if bub_side == "L" else "RightPositions"]).split("|") if c}
        if bubs:
            fb = bubs[0]
            d["FirstBubbleCell"] = fb["cell"]
            stage = fb["odd"]                       # oddity wins before this touch = current stage index
            if stage < len(hist):
                tgt = hist[stage][1]
                d["TargetAtFirstBubble"] = tgt
                d["GhostEligible"] = int(tgt in bub_cells)
                d["Ghost"] = int(fb["cell"] == tgt)
        else:
            d["GhostEligible"] = 0
    return d


def derive(subject, verbose=True):
    src = PROC / f"SafetyPop2_{subject}_AllSessions.csv"
    if not src.exists():
        sys.exit(f"{src} not found; run merge_safetypop2.py first")
    df = pd.read_csv(src)
    df = df.sort_values(["Session", "Trial"]).reset_index(drop=True)
    df.insert(df.columns.get_loc("Trial") + 1, "GlobalTrial", np.arange(1, len(df) + 1))
    df["Missing"] = df.SourceFile.astype(str).str.startswith("MISSING").astype(int)
    derived = pd.DataFrame([derive_row(r) if not r.Missing else {} for _, r in df.iterrows()])
    keep = ["Subject", "Date", "Session", "Trial", "GlobalTrial", "Code", "Type", "Polarity", "Side", "LTask", "RTask",
            "BubN", "OddN", "TargetCellPos", "TargetSide", "LeftPositions", "RightPositions", "CompletedBy",
            "BubTouches", "OddWins", "OddErrors", "OddTwoStimWin", "FirstBubbleGhost", "LatencyFirstTouch_ms",
            "LatencyFirstTarget_ms", "TrialTime_ms", "TouchLog", "TargetCellHistory", "TrialStart", "SourceFile", "Missing"]
    out = pd.concat([df[keep], derived], axis=1)
    out["Subject"] = subject                        # the raw column holds the app default 'TestSubject'
    dst = PROC / f"SafetyPop2_{subject}_Trials.csv"
    out.to_csv(dst, index=False, lineterminator="\n")
    if verbose:
        core = out[out.Type.isin(DUAL)]
        agree = (core.Ghost.notna() & (core.Ghost == (core.GhostApp == 1).astype(int)))
        print(f"{subject}: {len(out)} trials, sessions {out.Session.min()}-{out.Session.max()}; "
              f"ghost flag recomputed on {int(core.Ghost.notna().sum())} core trials, agrees with the app on {int(agree.sum())}; "
              f"wrote {dst.relative_to(REPO)}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.all:
        subjects = sorted(p.name.split("_")[1] for p in PROC.glob("SafetyPop2_*_AllSessions.csv"))
    elif args.subject:
        subjects = [args.subject]
    else:
        ap.error("give --subject <name> or --all")
    for s in subjects:
        derive(s)


if __name__ == "__main__":
    main()

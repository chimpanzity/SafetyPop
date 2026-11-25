#!/usr/bin/env python3
"""Figures for the Phase 2 analysis.

    python phase2/analysis/figure_safetypop2.py --all        # one summary figure per subject + the cross-subject figure
    python phase2/analysis/figure_safetypop2.py --subject Billy

Reads the Trials tables written by derive_safetypop2.py (and the Phase 1 workbook for the
reference lines) and writes PNG files to phase2/results/figures/:

* ``SafetyPop2_<Subject>_summary.png``: six panels. Competence by session, forced 4-circle cost by
  polarity, route choice by cell, the Crossover cell by session, within-trial monitoring, and
  ghost touches against the position-adjusted chance.
* ``SafetyPop2_two_apes.png``: both subjects on the crossover cost curve (Experiment 1 open markers,
  Experiment 2 filled) and their Crossover-cell first-touch rates by session.
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PHASE = Path(__file__).resolve().parents[1]
PROC = PHASE / "data" / "processed"
RESULTS = PHASE / "results" / "figures"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_safetypop2 import DUAL, load_phase1, stage_bits, stage_chance, wilson  # noqa: E402

HUE = {"Billy": "#C85A12", "Ben": "#2B6FC2", "Arthur": "#2E8B57", "Evelyn": "#7B3FA0", "Rowena": "#8A6D3B"}
MARK = {"Billy": "o", "Ben": "D", "Arthur": "s", "Evelyn": "^", "Rowena": "v"}
INK, MUTED, GRID = "#1F1F1F", "#6B7280", "#E5E7EB"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 10, "axes.titlelocation": "left"})


def light(hex_color, amount=0.55):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * amount) for c in (r, g, b))


def tidy(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def ghost_table(core):
    core = core.copy()
    core["BubSide"] = np.where(core.LTask == "Bubble", "L", "R")
    cells = [{int(c) for c in str(r["LeftPositions" if r.BubSide == "L" else "RightPositions"]).split("|") if c}
             for _, r in core.iterrows()]
    core["BubCells"] = cells
    habit = core.FirstBubbleCell.dropna().astype(int).value_counts().to_dict()
    el = core[core.GhostEligible == 1].copy()
    el["null"] = [(lambda w, tot: w.get(int(r.TargetAtFirstBubble), 0) / tot if tot else np.nan)(
        {c: habit.get(c, 0) for c in r.BubCells}, sum(habit.get(c, 0) for c in r.BubCells)) for _, r in el.iterrows()]
    return el


def summary_figure(subject, t, p1):
    hue = HUE.get(subject, "#C85A12")
    core = t[t.Type.isin(DUAL)]
    IJ = t[t.Type.isin(["I", "J"])]
    I = t[t.Type == "I"]
    sessions = sorted(t.Session.unique())
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.4))
    fig.suptitle(f"SafetyPop Phase 2: {subject} ({len(t)} trials, sessions {sessions[0]}-{sessions[-1]})",
                 x=0.02, ha="left", fontsize=12, fontweight="bold", color=INK)

    # (a) competence by session
    ax = axes[0, 0]
    acc = [np.mean([b for v in IJ[IJ.Session == s].StageOutcomes for b in stage_bits(v)]) for s in sessions]
    ch = [np.mean([c for v in IJ[IJ.Session == s].StageOutcomes for c in stage_chance(v)]) for s in sessions]
    ax.plot(sessions, ch, color=MUTED, linewidth=1.2, linestyle="--")
    ax.text(sessions[-1], ch[-1] - 0.03, "chance", color=MUTED, ha="right", va="top", fontsize=8)
    ax.plot(sessions, acc, color=hue, linewidth=2, marker="o", markersize=5)
    ax.set_ylim(0, 1)
    ax.set_xticks(sessions)
    ax.set_xlabel("Session")
    ax.set_ylabel("Share of stages hit at first touch")
    ax.set_title("Competence on forced oddity trials (I and J)")
    tidy(ax)

    # (b) forced 4-circle cost by polarity
    ax = axes[0, 1]
    for pol, mfc, label in [("White", "white", "white target among black"), ("Black", hue, "black target among white")]:
        g = I[I.Polarity == pol].groupby("Session").Cost.mean()
        ax.plot(g.index, g.values, color=hue, linewidth=1.6, marker="o", markersize=6, markerfacecolor=mfc,
                markeredgecolor=hue, markeredgewidth=1.5, label=label)
    ax.axhline(8, color=MUTED, linewidth=1.2, linestyle="--")
    ax.text(sessions[0], 8.25, "8 bubbles cost 8 touches", color=MUTED, fontsize=8, va="bottom")
    ax.axhline(4, color=GRID, linewidth=1)
    ax.set_ylim(0, max(14, I.groupby(["Session", "Polarity"]).Cost.mean().max() + 1.5))
    ax.set_xticks(sessions)
    ax.set_xlabel("Session")
    ax.set_ylabel("Touches to clear 4 circles")
    ax.set_title("Forced 4-circle cost, by target polarity")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    tidy(ax)

    # (c) route choice by cell
    ax = axes[0, 2]
    x = np.arange(4)
    ft = [core[core.Type == c].OddityFirst.mean() for c in DUAL]
    cp = [core[core.Type == c].CompletedByOddity.mean() for c in DUAL]
    ci = [wilson(int(core[core.Type == c].OddityFirst.sum()), len(core[core.Type == c])) for c in DUAL]
    ax.bar(x - 0.19, ft, 0.36, color=hue, label="first touch on oddity")
    ax.errorbar(x - 0.19, ft, yerr=[[f - lo for f, (lo, hi) in zip(ft, ci)], [hi - f for f, (lo, hi) in zip(ft, ci)]],
                fmt="none", ecolor=INK, elinewidth=1, capsize=2)
    ax.bar(x + 0.19, cp, 0.36, color=light(hue), label="completed by oddity")
    for i, (f, c, (lo, hi)) in enumerate(zip(ft, cp, ci)):
        ax.text(i - 0.19, hi + 0.02, f"{100 * f:.0f}", ha="center", fontsize=8, color=INK)
        ax.text(i + 0.19, c + 0.02, f"{100 * c:.0f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(["A\n4b / 4o", "B\n8b / 4o", "C\n4b / 8o", "D\n8b / 8o"])
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Share of trials")
    ax.set_title("Route choice by cell (B is the Crossover cell)")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    tidy(ax)

    # (d) Crossover cell by session
    ax = axes[1, 0]
    B = core[core.Type == "B"]
    ax.plot(sessions, B.groupby("Session").OddityFirst.mean().reindex(sessions), color=hue, linewidth=2, marker="o",
            markersize=5, label="first touch on oddity")
    ax.plot(sessions, B.groupby("Session").CompletedByOddity.mean().reindex(sessions), color=light(hue, 0.4), linewidth=2,
            marker="s", markersize=5, label="completed by oddity")
    if p1 is not None and subject in p1:
        b1 = p1[subject]
        b1 = b1[(b1.Type == "B") & (b1.Probe == "N")] if "Probe" in b1 else b1[b1.Type == "B"]
        ax.axhline(b1.OddityFirst.mean(), color=MUTED, linewidth=1.2, linestyle="--")
        ax.text(sessions[-1], b1.OddityFirst.mean() + 0.02, "Experiment 1, first touch", color=MUTED, ha="right", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(sessions)
    ax.set_xlabel("Session")
    ax.set_ylabel("Share of B trials")
    ax.set_title("The Crossover cell, session by session")
    ax.legend(frameon=False, loc="best", fontsize=8)
    tidy(ax)

    # (e) within-trial monitoring
    ax = axes[1, 1]
    g = B[B.FirstOddTag != ""]
    hit, miss = g[g.FirstOddTag == "Target"], g[g.FirstOddTag == "Distractor"]
    vals = [hit.CompletedByOddity.mean() if len(hit) else 0, miss.CompletedByOddity.mean() if len(miss) else 0]
    ax.bar([0, 1], vals, 0.55, color=[hue, light(hue)])
    for i, (v, n) in enumerate(zip(vals, [len(hit), len(miss)])):
        ax.text(i, v + 0.02, f"{100 * v:.0f}%  (n = {n})", ha="center", fontsize=8, color=INK)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["first oddity touch\nhit the target", "first oddity touch\nmissed"])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("B trials completed by oddity")
    ax.set_title("Within-trial monitoring in the Crossover cell")
    tidy(ax)

    # (f) ghost touches
    ax = axes[1, 2]
    el = ghost_table(core)
    labels, obs, nul, ns = [], [], [], []
    for c in DUAL + ["all"]:
        g = el if c == "all" else el[el.Type == c]
        if len(g):
            labels.append(c if c != "all" else "all cells")
            obs.append(g.Ghost.mean())
            nul.append(g["null"].mean())
            ns.append(len(g))
    y = np.arange(len(labels))
    for yi, o, nn in zip(y, obs, nul):
        ax.plot([nn, o], [yi, yi], color=GRID, linewidth=3, zorder=1)
    ax.scatter(nul, y, s=50, facecolor="white", edgecolor=MUTED, linewidth=1.5, zorder=2, label="adjusted chance")
    ax.scatter(obs, y, s=50, color=hue, zorder=3, label="observed")
    for yi, o, nn, n in zip(y, obs, nul, ns):
        ax.text(max(o, nn) + 0.02, yi, f"{100 * o:.0f}% vs {100 * nn:.0f}%  (n = {n})", va="center", fontsize=8, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.8)
    ax.set_xlabel("First bubble touched in the target's cell")
    ax.set_title("Ghost touches (H7)")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = RESULTS / f"SafetyPop2_{subject}_summary.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def two_apes_figure(subjects, tables, p1):
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw={"width_ratios": [1.15, 1]})
    # the crossover curve
    acc = np.linspace(0.4, 1.0, 200)
    ax.fill_between([0.4, 0.5], 0, 12, color="#FBE9DC", zorder=0)
    ax.fill_between([0.5, 1.0], 0, 12, color="#E6F1F8", zorder=0)
    ax.plot(acc, 4 / acc, color=INK, linewidth=2.2, zorder=2)
    ax.axhline(8, color="#1E9AB5", linewidth=2.2, zorder=2)
    ax.text(0.98, 8.2, "8 bubbles: 8 touches", color="#1E9AB5", ha="right", va="bottom", fontsize=9, fontweight="bold")
    ax.text(0.70, 4 / 0.70 + 0.6, "oddity: 4 / accuracy", color=INK, ha="left", va="bottom", fontsize=9, fontweight="bold")
    ax.text(0.41, 1.0, "bubbles cheaper", color="#C85A12", fontsize=8)
    ax.text(0.98, 1.0, "oddity cheaper", color="#1E9AB5", fontsize=8, ha="right")
    for s in subjects:
        t = tables[s]
        I2 = t[t.Type == "I"]
        c2 = I2.Cost.mean()
        b2 = t[t.Type == "B"].OddityFirst.mean()
        marker = MARK.get(s, "o")
        if p1 is not None and s in p1:
            d1 = p1[s]
            d1 = d1[d1.Probe == "N"] if "Probe" in d1 else d1
            c1 = d1[d1.Type == "I"].Cost.mean()
            b1 = d1[d1.Type == "B"].OddityFirst.mean()
            ax.scatter([4 / c1], [c1], s=70, facecolor="white", edgecolor=HUE.get(s, "#C85A12"), linewidth=1.8, marker=marker, zorder=4)
            ax.annotate("", xy=(4 / c2, c2), xytext=(4 / c1, c1),
                        arrowprops=dict(arrowstyle="->", color=HUE.get(s, "#C85A12"), linestyle="--", linewidth=1.2, shrinkA=6, shrinkB=6), zorder=3)
            label = f"{s}: B first touch {100 * b1:.0f}% → {100 * b2:.0f}%"
        else:
            label = f"{s}: B first touch {100 * b2:.0f}%"
        ax.scatter([4 / c2], [c2], s=70, color=HUE.get(s, "#C85A12"), marker=marker, zorder=5, label=label)
    ax.set_xlim(0.4, 1.0)
    ax.set_ylim(0, 12)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xticklabels(["40%\nguessing", "50%", "60%", "70%", "80%", "90%", "100%\nmastery"])
    ax.set_xlabel("Accuracy per touch on forced 4-circle trials (4 / mean cost)")
    ax.set_ylabel("Touches to finish the task")
    ax.set_title("Five apes on the crossover curve (open: Experiment 1, filled: Experiment 2)")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    ax.spines["left"].set_visible(True)

    # B first touch by session, both apes
    for s in subjects:
        t = tables[s]
        B = t[t.Type == "B"].groupby("Session").OddityFirst.mean()
        ax2.plot(B.index, B.values, color=HUE.get(s, "#C85A12"), linewidth=2, marker=MARK.get(s, "o"), markersize=5, label=s)
        ax2.text(B.index[-1] + 0.15, B.values[-1], s, color=HUE.get(s, "#C85A12"), va="center", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, 1.05)
    ax2.set_xlabel("Session")
    ax2.set_ylabel("Crossover trials started on oddity")
    ax2.set_title("The Crossover cell by session")
    ax2.set_xticks(range(1, 21))
    ax2.set_xlim(0.5, 21.5)
    tidy(ax2)
    fig.tight_layout()
    out = RESULTS / "SafetyPop2_two_apes.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.all:
        subjects = sorted(p.name.split("_")[1] for p in PROC.glob("SafetyPop2_*_Trials.csv"))
    elif args.subject:
        subjects = [args.subject]
    else:
        ap.error("give --subject <name> or --all")
    RESULTS.mkdir(parents=True, exist_ok=True)
    p1 = load_phase1()
    tables = {s: pd.read_csv(PROC / f"SafetyPop2_{s}_Trials.csv").query("Missing == 0") for s in subjects}
    for s in subjects:
        print("wrote", summary_figure(s, tables[s], p1).relative_to(REPO))
    if len(subjects) > 1:
        print("wrote", two_apes_figure(subjects, tables, p1).relative_to(REPO))


if __name__ == "__main__":
    main()

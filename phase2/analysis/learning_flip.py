#!/usr/bin/env python3
"""Learning and the Crossover flip, all five Phase 2 subjects.

    python phase2/analysis/learning_flip.py

Reads the merged and derived tables in phase2/data/processed/ and writes:

* phase2/data/processed/SafetyPop2_AllSubjects.csv: every trial of every target subject in one
  file. Raw columns as saved (with Subject set to the ape's name), the derived measures from
  derive_safetypop2.py, and RunningCost4 (see below). Blank rows for missing trials included,
  flagged Missing = 1.
* phase2/results/learning_flip.txt: the tests below, per subject and pooled.
* phase2/results/figures/SafetyPop2_learning_flip.png: competence, route choice and ghost
  touches by session for each subject.

The question (phase2/docs/SafetyPop_Phase2_TrialDesign.md, H2 to H4, H7):

1. Learning (H2). Do errors on the forced oddity trials fall over sessions? Measured as touches
   to clear a forced 4-circle array (Type I; 4 at mastery, 10 at chance) and an 8-circle array
   (Type J; 8 and 36). Errors = touches minus array size.
2. The flip (H3, H4). As a subject's own 4-circle cost falls below the 8-touch break-even, does
   Oddity choice rise in the Crossover cell (B, 8 bubbles vs 4 circles), and only there? C
   (4 bubbles vs 8 circles) should never flip; A and D at most drift toward indifference.
   Choice is measured two ways: completed by Oddity (the preregistered DV) and first touch on
   Oddity (the clean intention measure for an ape who alternates sides).
   RunningCost4 is the subject's mean cost over the 8 forced 4-circle trials before the trial
   in question (about two sessions), so each choice is set against competence the ape could
   have known about at that point.
3. Ghost touches (H7), gated on competence: is the first bubble touched in the oddity target's
   cell more often than position-adjusted chance once the subject is below the break-even?
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

PHASE = Path(__file__).resolve().parents[1]
PROC = PHASE / "data" / "processed"
RES = PHASE / "results"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_safetypop2 import poibin_two_sided  # noqa: E402

SUBJECTS = ["Arthur", "Ben", "Billy", "Evelyn", "Rowena"]
CORE = ["A", "B", "C", "D"]
WINDOW = 8
HUE = {"A": "#9CA3AF", "B": "#C85A12", "C": "#2B6FC2", "D": "#6B7280"}
INK, MUTED, GRID = "#1F1F1F", "#6B7280", "#E5E7EB"


def load():
    frames = []
    for s in SUBJECTS:
        t = pd.read_csv(PROC / f"SafetyPop2_{s}_Trials.csv")
        raw = pd.read_csv(PROC / f"SafetyPop2_{s}_AllSessions.csv")[["Session", "Trial", "Species", "Location",
                                                                       "Probe", "DistractorType", "EventLog"]]
        t = t.merge(raw, on=["Session", "Trial"], how="left")
        t["Subject"] = s
        t = t.sort_values("GlobalTrial").reset_index(drop=True)
        # running 4-circle cost: mean of the previous WINDOW forced I trials
        icost = t.Cost.where((t.Type == "I") & (t.Missing == 0))
        prev = icost.shift(1)
        t["RunningCost4"] = prev.rolling(500, min_periods=1).apply(
            lambda x: np.nanmean(x[~np.isnan(x)][-WINDOW:]) if (~np.isnan(x)).sum() >= WINDOW // 2 else np.nan, raw=True)
        frames.append(t)
    return pd.concat(frames, ignore_index=True)


def logit_slope(y, x):
    import statsmodels.api as sm
    d = pd.DataFrame({"y": y, "x": x}).dropna()
    if d.y.nunique() < 2 or len(d) < 20:
        return np.nan, np.nan
    m = sm.Logit(d.y, sm.add_constant(d.x)).fit(disp=0)
    return m.params["x"], m.pvalues["x"]


def main():
    df = load()
    lead = ["Subject", "Session", "Trial", "GlobalTrial", "Missing", "Date", "Code", "Type", "Polarity", "Side"]
    df = df[lead + [c for c in df.columns if c not in lead]]
    out_csv = PROC / "SafetyPop2_AllSubjects.csv"
    df.to_csv(out_csv, index=False, lineterminator="\n")
    d = df[df.Missing == 0].copy()

    L = []
    p = L.append
    p("SafetyPop Phase 2: learning, the Crossover flip, and ghost touches")
    p("=" * 78)
    p(f"{len(d)} trials, {d.groupby(['Subject', 'Session']).ngroups} sessions, subjects {', '.join(SUBJECTS)}")
    p(f"Running 4-circle cost = mean touches on the previous {WINDOW} forced 4-circle trials. Break-even = 8.")

    # ---------------------------------------------------------------- 1. learning
    p("\n1. LEARNING (H2): errors on forced oddity trials across sessions")
    p("-" * 78)
    p(f"{'':8s} {'4-circle errors (I)':^34s} {'8-circle errors (J)':^34s}")
    p(f"{'subject':8s} {'first 3 S':>9s} {'last 3 S':>9s} {'rho':>6s} {'p':>8s} {'first 3 S':>9s} {'last 3 S':>9s} {'rho':>6s} {'p':>8s}")
    learn = {}
    for s in SUBJECTS:
        g = d[d.Subject == s]
        row = [s]
        for typ, size in [("I", 4), ("J", 8)]:
            f = g[g.Type == typ]
            err = f.Cost - size
            sess = sorted(f.Session.unique())
            early = err[f.Session.isin(sess[:3])].mean()
            late = err[f.Session.isin(sess[-3:])].mean()
            r = stats.spearmanr(f.Session, err)
            row += [early, late, r.statistic, r.pvalue]
        learn[s] = row
        p(f"{s:8s} {row[1]:9.2f} {row[2]:9.2f} {row[3]:+6.2f} {row[4]:8.3g} {row[5]:9.2f} {row[6]:9.2f} {row[7]:+6.2f} {row[8]:8.3g}")
    p("Errors per array; chance is 6 for 4 circles and 28 for 8; rho is Spearman over trials, session vs errors.")
    for s in SUBJECTS:
        g = d[(d.Subject == s) & (d.Type == "I")]
        first = g.Session.min()
        below = g.groupby("Session").Cost.mean()
        cross = [k for k, v in below.items() if v < 8]
        p(f"   {s}: 4-circle cost by session " + " ".join(f"{v:.1f}" for v in below.values) +
          f"   (sessions below 8: {len(cross)} of {len(below)})")

    # ---------------------------------------------------------------- 2. flip
    p("\n2. THE FLIP (H3, H4): oddity choice by cell, against the subject's own running 4-circle cost")
    p("-" * 78)
    for measure, label in [("CompletedByOddity", "completed by Oddity (preregistered DV)"),
                           ("OddityFirst", "first touch on Oddity")]:
        p(f"\n{label}")
        p(f"{'subject':8s} {'cell':4s} {'all':>6s} {'cost>=8':>12s} {'cost<8':>12s} {'Fisher p':>9s} {'logit slope/touch':>18s} {'p':>8s}")
        for s in SUBJECTS:
            g = d[(d.Subject == s) & d.Type.isin(CORE)].dropna(subset=["RunningCost4"])
            for c in CORE:
                x = g[g.Type == c]
                hi, lo = x[x.RunningCost4 >= 8], x[x.RunningCost4 < 8]
                fp = stats.fisher_exact([[int(lo[measure].sum()), len(lo) - int(lo[measure].sum())],
                                         [int(hi[measure].sum()), len(hi) - int(hi[measure].sum())]])[1] if len(lo) and len(hi) else np.nan
                b, bp = logit_slope(x[measure], -x.RunningCost4)
                fmt = lambda z: f"{100 * z[measure].mean():4.0f}% n={len(z):<3d}" if len(z) else "      -     "
                p(f"{s:8s} {c:4s} {100 * x[measure].mean():5.0f}% {fmt(hi):>12s} {fmt(lo):>12s} {fp:9.3g} {b:+18.2f} {bp:8.3g}")
        p("Logit slope: change in log-odds of Oddity per touch drop in running cost (positive = more Oddity as the ape gets better).")

    # selectivity: B against C, the discriminating test, as an interaction
    import statsmodels.formula.api as smf
    p("\nSelectivity test (H4): does choice track competence in B more than in C?")
    p("Logit of completed-by-Oddity on core B and C trials: cell x running cost interaction, per subject.")
    for s in SUBJECTS:
        g = d[(d.Subject == s) & d.Type.isin(["B", "C"])].dropna(subset=["RunningCost4"]).copy()
        g["isB"] = (g.Type == "B").astype(int)
        g["skill"] = -g.RunningCost4
        if g[g.Type == "C"].CompletedByOddity.sum() == 0:
            bslope, bp = logit_slope(g[g.isB == 1].CompletedByOddity, g[g.isB == 1].skill)
            p(f"   {s}: C never completed by Oddity ({len(g[g.isB == 0])} trials), so C cannot move; "
              f"B slope {bslope:+.2f}, p = {bp:.3g}")
            continue
        try:
            m = smf.logit("CompletedByOddity ~ isB * skill", data=g).fit(disp=0)
            p(f"   {s}: interaction {m.params['isB:skill']:+.2f}, p = {m.pvalues['isB:skill']:.3g}")
        except Exception as e:
            p(f"   {s}: model did not fit ({type(e).__name__})")

    p("\nBy session: share of trials completed by Oddity in each cell")
    for s in SUBJECTS:
        g = d[(d.Subject == s) & d.Type.isin(CORE)]
        tab = g.groupby(["Session", "Type"]).CompletedByOddity.mean().unstack()
        p(f"   {s}")
        p("      session " + " ".join(f"{k:>4d}" for k in tab.index))
        for c in CORE:
            p(f"      {c}      " + " ".join(f"{100 * v:4.0f}" if not np.isnan(v) else "   -" for v in tab[c].values))
        rB = stats.spearmanr(tab.index, tab["B"])
        p(f"      B across sessions: Spearman rho = {rB.statistic:+.2f}, p = {rB.pvalue:.3g}")

    # ---------------------------------------------------------------- 3. ghost
    p("\n3. GHOST TOUCHES (H7): first bubble in the oddity target's cell, against position-adjusted chance")
    p("-" * 78)
    gh_all = []
    for s in SUBJECTS:
        g = d[(d.Subject == s) & d.Type.isin(CORE)].copy()
        g["BubSide"] = np.where(g.LTask == "Bubble", "L", "R")
        g["BubCells"] = [{int(c) for c in str(r["LeftPositions" if r.BubSide == "L" else "RightPositions"]).split("|") if c}
                         for _, r in g.iterrows()]
        habit = g.FirstBubbleCell.dropna().astype(int).value_counts().to_dict()
        el = g[g.GhostEligible == 1].copy()
        el["null"] = [(lambda w: w.get(int(r.TargetAtFirstBubble), 0) / sum(w.values()) if sum(w.values()) else np.nan)(
            {c: habit.get(c, 0) for c in r.BubCells}) for _, r in el.iterrows()]
        el["Subject"] = s
        gh_all.append(el)
        for lab, sub in [("all", el), ("cost >= 8", el[el.RunningCost4 >= 8]), ("cost < 8", el[el.RunningCost4 < 8])]:
            if len(sub) == 0:
                continue
            k = int(sub.Ghost.sum())
            p(f"   {s:8s} {lab:10s} {k:4d}/{len(sub):<4d} = {100 * k / len(sub):5.1f}%  chance {100 * sub['null'].mean():5.1f}%  "
              f"p = {poibin_two_sided(sub['null'].values, k):.2f}")
    G = pd.concat(gh_all)
    for lab, sub in [("all", G), ("cost >= 8", G[G.RunningCost4 >= 8]), ("cost < 8", G[G.RunningCost4 < 8])]:
        k = int(sub.Ghost.sum())
        p(f"   {'pooled':8s} {lab:10s} {k:4d}/{len(sub):<4d} = {100 * k / len(sub):5.1f}%  chance {100 * sub['null'].mean():5.1f}%  "
          f"p = {poibin_two_sided(sub['null'].values, k):.2f}")

    text = "\n".join(L) + "\n"
    (RES / "learning_flip.txt").write_text(text, encoding="utf-8")
    print(text)

    # ---------------------------------------------------------------- figure
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": MUTED})
    fig, axes = plt.subplots(len(SUBJECTS), 3, figsize=(14, 3.0 * len(SUBJECTS)), sharex="col")
    for i, s in enumerate(SUBJECTS):
        g = d[d.Subject == s]
        sess = sorted(g.Session.unique())
        # competence
        ax = axes[i, 0]
        ic = g[g.Type == "I"].groupby("Session").Cost.mean()
        ax.axhspan(0, 8, color="#F2F7FB", zorder=0)
        ax.axhline(8, color="#1E9AB5", lw=1.4)
        ax.axhline(10, color=MUTED, lw=1, ls=":")
        ax.plot(ic.index, ic.values, color=INK, marker="o", ms=4, lw=1.8)
        ax.set_ylim(3, 14)
        ax.set_ylabel(s, fontsize=11, fontweight="bold", rotation=0, ha="right", va="center", labelpad=18)
        if i == 0:
            ax.set_title("Competence: touches to clear 4 circles (forced I)", loc="left", fontsize=9.5, fontweight="bold")
            ax.text(sess[-1], 8.2, "break-even 8", color="#1E9AB5", ha="right", va="bottom", fontsize=8)
            ax.text(sess[-1], 10.2, "chance 10", color=MUTED, ha="right", va="bottom", fontsize=8)
        # choice: completed by oddity
        for j, (measure, title) in enumerate([("CompletedByOddity", "Completed by Oddity, by cell"),
                                              ("OddityFirst", "First touch on Oddity, by cell")]):
            ax = axes[i, j + 1]
            tab = g[g.Type.isin(CORE)].groupby(["Session", "Type"])[measure].mean().unstack()
            for c in CORE:
                ax.plot(tab.index, tab[c].values, color=HUE[c], lw=2.4 if c == "B" else 1.2,
                        marker="o" if c == "B" else None, ms=3.5, label={"A": "A 4b/4o", "B": "B 8b/4o (Crossover)",
                                                                       "C": "C 4b/8o", "D": "D 8b/8o"}[c], zorder=3 if c == "B" else 2)
            ax.set_ylim(-0.03, 1.03)
            ax.grid(axis="y", color=GRID, lw=0.7)
            if i == 0:
                ax.set_title(title, loc="left", fontsize=9.5, fontweight="bold")
            if i == 0 and j == 0:
                ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
    for ax in axes[-1]:
        ax.set_xlabel("Session")
        ax.set_xticks(range(1, 21, 2))
    fig.tight_layout()
    fig.savefig(RES / "figures" / "SafetyPop2_learning_flip.png", dpi=170)
    plt.close(fig)

    # ghost figure
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    rows = []
    for s in SUBJECTS + ["pooled"]:
        sub = G if s == "pooled" else G[G.Subject == s]
        rows.append((s, sub.Ghost.mean(), sub["null"].mean(), len(sub)))
    y = np.arange(len(rows))
    for yi, (s, o, n0, n) in zip(y, rows):
        ax.plot([n0, o], [yi, yi], color=GRID, lw=3, zorder=1)
        ax.scatter([n0], [yi], s=46, facecolor="white", edgecolor=MUTED, lw=1.5, zorder=2)
        ax.scatter([o], [yi], s=46, color="#C85A12" if s != "pooled" else INK, zorder=3)
        ax.text(max(o, n0) + 0.01, yi, f"{100 * o:.1f}% vs {100 * n0:.1f}%  (n = {n})", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0.10, 0.36)
    ax.set_xlabel("First bubble touched in the target's cell (filled: observed; open: position-adjusted chance)")
    ax.set_title("Ghost touches, core trials, all sessions", loc="left", fontweight="bold")
    ax.grid(axis="x", color=GRID, lw=0.7)
    fig.tight_layout()
    fig.savefig(RES / "figures" / "SafetyPop2_ghost_touches.png", dpi=170)
    plt.close(fig)
    print("wrote", out_csv.relative_to(PHASE.parent))


if __name__ == "__main__":
    main()

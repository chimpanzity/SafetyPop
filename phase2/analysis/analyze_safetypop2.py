#!/usr/bin/env python3
"""Phase 2 hypothesis tests and follow-ups for one subject.

    python phase2/analysis/analyze_safetypop2.py --subject Billy
    python phase2/analysis/analyze_safetypop2.py --all

Reads ``phase2/data/processed/SafetyPop2_<Subject>_Trials.csv`` (made by derive_safetypop2.py)
and, for the Phase 1 comparison, ``phase1/data/processed/SafetyPop_AllSubjects_AllSessions.xlsx`` (complete sessions only).
Writes ``phase2/results/results_<Subject>.txt`` and prints the same text.

Sections follow the Phase 2 design document (phase2/docs/SafetyPop_Phase2_TrialDesign.md):
H1 pre-learning choice, H2 competence, H3 the flip in the Crossover cell (B), H4 selectivity,
H5 switching, H6 preference controls, H7 ghost touches, then the exploratory polarity analysis,
the within-trial monitoring analysis, the race-model check on completion, and the Phase 1 comparison.

Definitions
-----------
Per-stage accuracy    on forced oddity trials (I, J), the share of elimination stages whose first
                      touch hit the target, leaving out the final stage, where one stimulus is left
                      and a hit is certain. Chance is the mean of 1/k over the stages scored:
                      0.36 for a 4-stimulus array, 0.25 for an 8-stimulus array.
Cost                  touches to clear a forced oddity array (OddWins + OddErrors).
Oddity first          first touch of a dual-task trial landed on the oddity side.
Completed by oddity   the trial ended by clearing the oddity array.
Ghost null            for each eligible core trial, the probability that the ape's first bubble
                      would land in the target's cell if his first-bubble cell were drawn from his
                      own first-bubble cell frequencies (all core trials, both sides pooled),
                      restricted to the cells holding a bubble on that trial. The test is exact
                      (Poisson-binomial) and two-sided.
"""

import argparse
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
PHASE = Path(__file__).resolve().parents[1]
PROC = PHASE / "data" / "processed"
PHASE1 = REPO / "phase1" / "data" / "processed" / "SafetyPop_AllSubjects_AllSessions.xlsx"
RESULTS = PHASE / "results"
DUAL = ["A", "B", "C", "D"]
CELL_NAMES = {"A": "A 4b/4o Parity-Low", "B": "B 8b/4o Crossover", "C": "C 4b/8o Anchor", "D": "D 8b/8o Parity-High"}


# ----------------------------------------------------------------------------- helpers
def pct(k, n):
    return f"{100 * k / n:.1f}% ({k}/{n})" if n else "n/a"


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def fisher(k1, n1, k2, n2):
    table = [[k1, n1 - k1], [k2, n2 - k2]]
    odds, p = stats.fisher_exact(table)
    return odds, p


def stage_bits(s):
    s = "" if pd.isna(s) else str(s)
    return [1 if c == "T" else 0 for c in s[:-1]]          # drop the final, trivial stage


def stage_chance(s):
    n = len("" if pd.isna(s) else str(s))
    return [1 / k for k in range(n, 1, -1)]                 # k stimuli left at each scored stage


def poibin_two_sided(ps, k):
    """Exact two-sided p for observing k successes under independent probabilities ps."""
    dist = np.zeros(len(ps) + 1)
    dist[0] = 1.0
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    upper = dist[k:].sum()
    lower = dist[: k + 1].sum()
    return min(1.0, 2 * min(upper, lower))


def change_point(x, group):
    """Best single step in a 0/1 sequence, cut only at group (trial) boundaries. Returns
    (cut, p_before, n_before, p_after, n_after, LR) with LR = 2 * (LL_step - LL_flat)."""
    x = np.asarray(x, float)
    group = np.asarray(group)

    def ll(v):
        if len(v) == 0:
            return 0.0
        p = min(max(v.mean(), 1e-9), 1 - 1e-9)
        k = v.sum()
        return k * np.log(p) + (len(v) - k) * np.log(1 - p)

    base = ll(x)
    best = None
    for cut in sorted(set(group))[1:]:
        a, b = x[group < cut], x[group >= cut]
        if len(a) < 10 or len(b) < 10:
            continue
        l = ll(a) + ll(b)
        if best is None or l > best[0]:
            best = (l, cut, a.mean(), len(a), b.mean(), len(b))
    if best is None:
        return None
    return best[1], best[2], best[3], best[4], best[5], 2 * (best[0] - base)


def power_n(p0, p1, alpha=0.05, power=0.8):
    """Trials needed for a one-sample test of a proportion against p0 (normal approximation)."""
    if p1 <= p0:
        return "not applicable, observed rate is not above chance"
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    n = ((z_a * np.sqrt(p0 * (1 - p0)) + z_b * np.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2
    return f"about {int(round(n, -2)):,}"


def logistic(df, formula):
    try:
        import statsmodels.formula.api as smf
    except ImportError:
        return None
    m = smf.logit(formula, data=df).fit(disp=0)
    return m


# ----------------------------------------------------------------------------- analysis
def analyze(subject, t, p1):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from derive_safetypop2 import parse_touches
    core = t[t.Type.isin(DUAL)].copy()
    IJ = t[t.Type.isin(["I", "J"])].copy()
    I = t[t.Type == "I"]
    J = t[t.Type == "J"]
    sessions = sorted(t.Session.unique())

    print(f"SafetyPop Phase 2: {subject}")
    print("=" * 72)
    print(f"{len(t)} trials in sessions {sessions[0]}-{sessions[-1]} ({t.Date.min()} to {t.Date.max()}); "
          f"core dual-task trials {len(core)}, forced oddity trials {len(IJ)}")
    print("Type counts:", " ".join(f"{k}{v}" for k, v in t.Type.value_counts().sort_index().items()))

    # ---------------- H2 competence
    print("\nH2  Competence on forced oddity trials (I = 4 stimuli, J = 8)")
    print("-" * 72)
    rows = []
    for s in sessions:
        g = IJ[IJ.Session == s]
        bits = [b for v in g.StageOutcomes for b in stage_bits(v)]
        ch = [c for v in g.StageOutcomes for c in stage_chance(v)]
        gi, gj = I[I.Session == s], J[J.Session == s]
        rows.append((s, len(bits), np.mean(bits) if bits else np.nan, np.mean(ch) if ch else np.nan,
                     gi.Cost.mean(), gj.Cost.mean(),
                     gi.OddTwoStimWin.mean()))
    print(f"{'session':>8} {'stages':>7} {'accuracy':>9} {'chance':>7} {'I cost':>7} {'J cost':>7} {'I 2-stim':>9}")
    for r in rows:
        print(f"{r[0]:>8} {r[1]:>7} {r[2]:>9.2f} {r[3]:>7.2f} {r[4]:>7.2f} {r[5]:>7.2f} {r[6]:>9.2f}")
    bits_all = [b for v in IJ.StageOutcomes for b in stage_bits(v)]
    ch_all = [c for v in IJ.StageOutcomes for c in stage_chance(v)]
    print(f"All sessions: per-stage accuracy {np.mean(bits_all):.3f} vs chance {np.mean(ch_all):.3f} "
          f"(binomial p = {stats.binomtest(int(sum(bits_all)), len(bits_all), np.mean(ch_all)).pvalue:.2g}); "
          f"I cost {I.Cost.mean():.2f} (chance 10, mastery 4; n = {len(I)}), J cost {J.Cost.mean():.2f} (chance 36, mastery 8; n = {len(J)})")
    print(f"Two-stimulus stage on I trials (chance 0.5): {I.OddTwoStimWin.mean():.2f}; on J: {J.OddTwoStimWin.mean():.2f}")
    # change-point at trial resolution
    seq, grp = [], []
    for _, r in IJ.sort_values("GlobalTrial").iterrows():
        for b in stage_bits(r.StageOutcomes):
            seq.append(b)
            grp.append(r.GlobalTrial)
    cp = change_point(seq, grp)
    if cp:
        cut, pb, nb, pa, na, lr = cp
        sess_at = int(t.loc[t.GlobalTrial == cut, "Session"].iloc[0])
        print(f"Single-step change-point in per-stage accuracy: before trial {cut} (session {sess_at}) {pb:.2f} "
              f"(n = {nb} stages), after {pa:.2f} (n = {na}); LR = {lr:.1f} "
              f"(a flat model is nested, 2 extra parameters; LR above ~6 is clear, above ~10 strong)")
    # gradual efficiency gain (preregistered form of H2)
    if len(sessions) > 2:
        reg = stats.linregress(I.Session, I.Cost)
        print(f"Gradual gain, I cost on session: slope {reg.slope:+.2f} touches/session, p = {reg.pvalue:.2f} "
              f"(trial level, n = {len(I)})")

    # ---------------- polarity
    print("\nExploratory  Target polarity (White = white target among black; Black = black among white)")
    print("-" * 72)
    for pol in ["White", "Black"]:
        g = IJ[IJ.Polarity == pol]
        bits = [b for v in g.StageOutcomes for b in stage_bits(v)]
        gi, gj = I[I.Polarity == pol], J[J.Polarity == pol]
        print(f"{pol:>6}: per-stage accuracy {np.mean(bits):.2f} (n = {len(bits)} stages); "
              f"I cost {gi.Cost.mean():.2f} (n = {len(gi)}), J cost {gj.Cost.mean():.2f} (n = {len(gj)})")
    iw, ib = I[I.Polarity == "White"].Cost, I[I.Polarity == "Black"].Cost
    mw = stats.mannwhitneyu(iw, ib, alternative="two-sided")
    print(f"I cost, White vs Black: Mann-Whitney U = {mw.statistic:.0f}, p = {mw.pvalue:.3f}")
    print("Per session, I cost by polarity:")
    tab = I.groupby(["Session", "Polarity"]).Cost.mean().unstack()
    for s, r in tab.iterrows():
        print(f"   session {s:>2}: White {r.get('White', np.nan):5.2f}  Black {r.get('Black', np.nan):5.2f}")

    # ---------------- H1, H3, H4 choice by cell
    print("\nH1/H3/H4  Route choice in the four dual-task cells")
    print("-" * 72)
    print(f"{'cell':<22} {'completed by oddity':>22} {'first touch on oddity':>24}")
    for c in DUAL:
        g = core[core.Type == c]
        print(f"{CELL_NAMES[c]:<22} {pct(int(g.CompletedByOddity.sum()), len(g)):>22} {pct(int(g.OddityFirst.sum()), len(g)):>24}")
    a, b = core[core.Type == "A"], core[core.Type == "B"]
    c_, d = core[core.Type == "C"], core[core.Type == "D"]
    for name, x, y, lab in [("A vs B (same 4-circle array, 4 vs 8 bubbles)", a, b, "B"),
                            ("C vs D (same 8-circle array, 4 vs 8 bubbles)", c_, d, "D")]:
        kx, ky = int(x.OddityFirst.sum()), int(y.OddityFirst.sum())
        odds, p = fisher(ky, len(y), kx, len(x))
        lo1, hi1 = wilson(kx, len(x))
        lo2, hi2 = wilson(ky, len(y))
        print(f"{name}: first touch on oddity {100 * kx / len(x):.1f}% [{100 * lo1:.0f}, {100 * hi1:.0f}] vs "
              f"{100 * ky / len(y):.1f}% [{100 * lo2:.0f}, {100 * hi2:.0f}]; Fisher p = {p:.3g}, OR = {odds:.2f}")
    # per-session paired comparison B - A
    ps = core[core.Type.isin(["A", "B"])].groupby(["Session", "Type"]).OddityFirst.mean().unstack()
    diff = (ps["B"] - ps["A"]).dropna()
    if len(diff) >= 6 and (diff != 0).any():
        w = stats.wilcoxon(diff, alternative="two-sided")
        print(f"B above A in {int((diff > 0).sum())} of {len(diff)} sessions (ties {int((diff == 0).sum())}); "
              f"Wilcoxon on session rates p = {w.pvalue:.3f}")
    print("Per session, first touch on oddity (A B C D) and completion by oddity in B:")
    for s in sessions:
        g = core[core.Session == s]
        ft = " ".join(f"{100 * g[g.Type == c].OddityFirst.mean():3.0f}" for c in DUAL)
        gb = g[g.Type == "B"]
        print(f"   session {s:>2}: first touch {ft}   B completed {100 * gb.CompletedByOddity.mean():3.0f}% "
              f"({int(gb.CompletedByOddity.sum())}/{len(gb)})")
    core["bub8"] = (core.BubN == 8).astype(int)
    core["odd8"] = (core.OddN == 8).astype(int)
    m = logistic(core.dropna(subset=["OddityFirst"]), "OddityFirst ~ bub8 + odd8")
    if m is not None:
        orr = np.exp(m.params)
        ci = np.exp(m.conf_int())
        print(f"Logistic, first touch on oddity ~ 8 bubbles + 8 circles: OR(8 bubbles) = {orr['bub8']:.2f} "
              f"[{ci.loc['bub8', 0]:.2f}, {ci.loc['bub8', 1]:.2f}], p = {m.pvalues['bub8']:.3g}; "
              f"OR(8 circles) = {orr['odd8']:.2f} [{ci.loc['odd8', 0]:.2f}, {ci.loc['odd8', 1]:.2f}], p = {m.pvalues['odd8']:.3g}")
        m2 = logistic(core.dropna(subset=["OddityFirst"]), "OddityFirst ~ bub8 * odd8")
        if m2 is not None:
            print(f"   with interaction: p(8 bubbles x 8 circles) = {m2.pvalues['bub8:odd8']:.2f}; "
                  f"LR vs additive = {2 * (m2.llf - m.llf):.2f}")
    else:
        print("(statsmodels not installed: logistic model skipped)")

    # ---------------- H3 as preregistered: choice against own competence
    print("\nH3 (preregistered form)  Does the B choice track competence over time?")
    print("-" * 72)
    sess_acc = {s: np.mean([b for v in IJ[IJ.Session == s].StageOutcomes for b in stage_bits(v)]) for s in sessions}
    sess_b_first = core[core.Type == "B"].groupby("Session").OddityFirst.mean()
    sess_b_done = core[core.Type == "B"].groupby("Session").CompletedByOddity.mean()
    x = np.array([sess_acc[s] for s in sessions])
    if len(sessions) >= 4:
        r1 = stats.spearmanr(x, [sess_b_first[s] for s in sessions])
        r2 = stats.spearmanr(x, [sess_b_done[s] for s in sessions])
        print(f"Session-level Spearman, I/J accuracy vs B first touch: rho = {r1.statistic:+.2f} (p = {r1.pvalue:.2f}); "
              f"vs B completion: rho = {r2.statistic:+.2f} (p = {r2.pvalue:.2f})")
    if cp:
        bt = core[core.Type == "B"]
        before, after = bt[bt.GlobalTrial < cut], bt[bt.GlobalTrial >= cut]
        if len(before) and len(after):
            o, p = fisher(int(after.OddityFirst.sum()), len(after), int(before.OddityFirst.sum()), len(before))
            print(f"B first touch before vs after the competence change-point (trial {cut}): "
                  f"{pct(int(before.OddityFirst.sum()), len(before))} vs {pct(int(after.OddityFirst.sum()), len(after))}, Fisher p = {p:.3g}")

    # ---------------- H5 switching
    print("\nH5  Within-trial switching (core trials)")
    print("-" * 72)
    sw = core.SideSwitches.sum() / core.TouchPairs.sum()
    print(f"Side switches per consecutive touch pair: {100 * sw:.1f}%; trials with no switch: "
          f"{100 * (core.SideSwitches == 0).mean():.0f}%")
    iv_sw, iv_st = [], []
    for log in core.TouchLog:
        touches = parse_touches(log)
        for a_, b_ in zip(touches, touches[1:]):
            (iv_sw if a_["side"] != b_["side"] else iv_st).append(b_["ms"] - a_["ms"])
    print(f"Median interval between consecutive touches: switching sides {np.median(iv_sw):.0f} ms (n = {len(iv_sw)}), "
          f"staying {np.median(iv_st):.0f} ms (n = {len(iv_st)}); the touched side is hidden for about 500 ms after a touch")
    print("Per session, switch rate on core trials: " +
          " ".join(f"S{s}:{100 * g.SideSwitches.sum() / g.TouchPairs.sum():.0f}%" for s, g in core.groupby("Session")))

    # ---------------- H6 preference controls
    print("\nH6  Preference controls (completing touch on the 4-stimulus side)")
    print("-" * 72)
    e, f = t[t.Type == "E"], t[t.Type == "F"]
    print(f"E, 4 vs 8 bubbles: {pct(int(e.ChoseFourSide.sum()), len(e))};  F, 4 vs 8 circles: {pct(int(f.ChoseFourSide.sum()), len(f))}")

    # ---------------- H7 ghost touches
    print("\nH7  Ghost touches: first bubble touched in the oddity target's cell")
    print("-" * 72)
    core["BubSide"] = np.where(core.LTask == "Bubble", "L", "R")
    cells = []
    for _, r in core.iterrows():
        col = "LeftPositions" if r.BubSide == "L" else "RightPositions"
        cells.append({int(c) for c in str(r[col]).split("|") if c})
    core["BubCells"] = cells
    habit = core.FirstBubbleCell.dropna().astype(int).value_counts().to_dict()
    el = core[core.GhostEligible == 1].copy()

    def null_p(r):
        w = {c: habit.get(c, 0) for c in r.BubCells}
        tot = sum(w.values())
        return w.get(int(r.TargetAtFirstBubble), 0) / tot if tot else np.nan

    el["null"] = [null_p(r) for _, r in el.iterrows()]
    k, n = int(el.Ghost.sum()), len(el)
    print(f"Eligible core trials (a bubble was touched and the target's cell held a bubble): {n} of {len(core)}; "
          f"app flag agrees with the recomputed flag on all {int(core.Ghost.notna().sum())} scored trials")
    print(f"Observed {pct(k, n)}; position-bias-adjusted chance {100 * el['null'].mean():.1f}% "
          f"(uniform over bubble cells would be {100 * np.mean([1 / len(c) for c in el.BubCells]):.1f}%); "
          f"two-sided exact p = {poibin_two_sided(el['null'].values, k):.2f}")
    for c in DUAL:
        g = el[el.Type == c]
        if len(g):
            print(f"   {CELL_NAMES[c]:<22}: {pct(int(g.Ghost.sum()), len(g))} vs chance {100 * g['null'].mean():.1f}%")
    print(f"   Trials needed for 80% power at this subject's observed effect: {power_n(el['null'].mean(), k / n)}")
    ghost_out = el[["null"]].assign(Ghost=el.Ghost.values, Subject=subject)

    # ---------------- within-trial monitoring
    print("\nWithin-trial monitoring (dual-task trials)")
    print("-" * 72)
    for c in ["B", "A"]:
        g = core[(core.Type == c) & (core.FirstOddTag != "")]
        hit, miss = g[g.FirstOddTag == "Target"], g[g.FirstOddTag == "Distractor"]
        if len(hit) and len(miss):
            o, p = fisher(int(hit.CompletedByOddity.sum()), len(hit), int(miss.CompletedByOddity.sum()), len(miss))
            print(f"{c}: completed by oddity after a first oddity touch that hit {pct(int(hit.CompletedByOddity.sum()), len(hit))} "
                  f"vs missed {pct(int(miss.CompletedByOddity.sum()), len(miss))}; Fisher p = {p:.3g}")
    bw = core[(core.Type == "B")]
    print(f"B first touch on oddity by polarity (visible before the first touch): "
          f"White {pct(int(bw[bw.Polarity == 'White'].OddityFirst.sum()), int((bw.Polarity == 'White').sum()))}, "
          f"Black {pct(int(bw[bw.Polarity == 'Black'].OddityFirst.sum()), int((bw.Polarity == 'Black').sum()))}; "
          f"completion by oddity: White {100 * bw[bw.Polarity == 'White'].CompletedByOddity.mean():.0f}%, "
          f"Black {100 * bw[bw.Polarity == 'Black'].CompletedByOddity.mean():.0f}%")

    # ---------------- race model
    print("\nRace model  Can strict side alternation alone produce the B completion rate?")
    print("-" * 72)
    print("Assume the ape alternates sides on every touch, starting on the side he actually touched first, "
          "with oddity touches drawn from his own forced 4-circle cost distribution for that polarity. "
          "Bubbles are cleared on the 8th bubble touch, so oddity wins the race if its array clears within "
          "8 oddity touches (start on oddity) or 7 (start on bubbles).")
    for pol in ["White", "Black"]:
        costs = I[I.Polarity == pol].Cost.values
        g = bw[bw.Polarity == pol]
        if len(costs) == 0 or len(g) == 0:
            continue
        pred = np.mean([(costs <= (8 if r.FirstTask == "Oddity" else 7)).mean() for _, r in g.iterrows()])
        print(f"   {pol}: predicted completion by oddity {100 * pred:.0f}%, observed {100 * g.CompletedByOddity.mean():.0f}% "
              f"(n = {len(g)} B trials; {100 * g.OddityFirst.mean():.0f}% started on oddity)")
    print(f"   Actual switch rate on core trials {100 * sw:.0f}%: the closer to 100%, the less completion says about choice.")

    # ---------------- Phase 1 comparison
    if p1 is not None and subject in p1:
        print(f"\nPhase 1 comparison ({subject}, complete sessions only)")
        print("-" * 72)
        d1 = p1[subject]
        d1 = d1[d1.Probe == "N"] if "Probe" in d1 else d1
        c1 = d1[d1.Type.isin(DUAL)]
        for c in DUAL:
            g1, g2 = c1[c1.Type == c], core[core.Type == c]
            print(f"   {CELL_NAMES[c]:<22} completed by oddity: Phase 1 {pct(int((g1.CompletedBy == 'Oddity').sum()), len(g1))}, "
                  f"Phase 2 {pct(int(g2.CompletedByOddity.sum()), len(g2))}; first touch on oddity: "
                  f"Phase 1 {pct(int(g1.OddityFirst.sum()), len(g1))}, Phase 2 {pct(int(g2.OddityFirst.sum()), len(g2))}")
        a1, b1 = c1[c1.Type == "A"], c1[c1.Type == "B"]
        o, p = fisher(int(b1.OddityFirst.sum()), len(b1), int(a1.OddityFirst.sum()), len(a1))
        print(f"   Phase 1 A vs B first touch on oddity: {100 * a1.OddityFirst.mean():.1f}% vs {100 * b1.OddityFirst.mean():.1f}%, Fisher p = {p:.2f}")
        b2 = core[core.Type == "B"]
        o, p = fisher(int(b2.OddityFirst.sum()), len(b2), int(b1.OddityFirst.sum()), len(b1))
        print(f"   B first touch on oddity, Phase 1 vs Phase 2: {100 * b1.OddityFirst.mean():.1f}% vs {100 * b2.OddityFirst.mean():.1f}%, Fisher p = {p:.3g}")
        i1 = d1[d1.Type == "I"]
        print(f"   Forced 4-stimulus cost: Phase 1 {i1.Cost.mean():.2f} (n = {len(i1)}), Phase 2 {I.Cost.mean():.2f} (n = {len(I)}); "
              f"accuracy per touch {400 / i1.Cost.mean():.0f}% vs {400 / I.Cost.mean():.0f}%")
        c1sw = c1.SideSwitches.sum() / c1.TouchPairs.sum()
        print(f"   Side-switch rate on core trials: Phase 1 {100 * c1sw:.0f}%, Phase 2 {100 * sw:.0f}%")
    return ghost_out


# ----------------------------------------------------------------------------- Phase 1 loader
def load_phase1():
    if not PHASE1.exists():
        return None
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from derive_safetypop2 import parse_touches, stage_outcomes
    out = {}
    xl = pd.ExcelFile(PHASE1)
    for sheet in xl.sheet_names:
        if sheet == "Summary":
            continue
        d = xl.parse(sheet)
        if "SessionComplete" in d:
            d = d[d.SessionComplete == "yes"]
        if len(d) == 0:
            continue
        d["Session"] = d.Session.astype(int)
        rows = []
        for _, r in d.iterrows():
            touches = parse_touches(r.TouchLog)
            pairs = list(zip(touches, touches[1:]))
            rows.append({
                "OddityFirst": int(touches[0]["task"] == "Oddity") if touches else np.nan,
                "Cost": int(r.OddWins) + int(r.OddErrors) if r.Type in ("I", "J") else np.nan,
                "TouchPairs": len(pairs), "SideSwitches": sum(b["side"] != a["side"] for a, b in pairs),
            })
        out[sheet] = pd.concat([d.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    return out


def ghost_pooled(ghost_frames):
    g = pd.concat(ghost_frames)
    k, n = int(g.Ghost.sum()), len(g)
    p = poibin_two_sided(g["null"].values, k)
    print("\nH7 pooled across subjects")
    print("-" * 72)
    print(f"Observed {pct(k, n)} vs adjusted chance {100 * g['null'].mean():.1f}%; two-sided exact p = {p:.2f}")
    # trials needed for 80% power at the pooled observed effect, two-sided alpha .05
    print(f"Trials needed for 80% power at the pooled effect ({100 * k / n:.1f}% vs {100 * g['null'].mean():.1f}%): "
          f"{power_n(g['null'].mean(), k / n)}")


def perseveration(subject, allsessions):
    """Cross-divider perseveration: after switching sides, how often does the next touch land in the
    same grid cell as the previous touch? Scored on consecutive cross-side touch pairs of core trials
    where that cell holds a stimulus on the destination side; chance is 1 / (stimuli visible there)."""
    def parse_state(s):
        L, R = s.split(",R=")
        L = L[2:]
        out = {}
        for side, txt in (("L", L), ("R", R)):
            out[side] = None if txt == "HIDDEN" else (set() if txt == "" else {int(x.split(":")[0]) for x in txt.split("|")})
        return out

    core = allsessions[allsessions.Type.isin(DUAL)]
    same, chance, n = 0, [], 0
    for _, r in core.iterrows():
        visible = {"L": set(), "R": set()}
        prev = None
        for ev in (e.split(",") for e in str(r.EventLog).split(";")):
            if ev[1] == "STATE":
                st = parse_state(",".join(ev[2:]))
                for sd in "LR":
                    if st[sd] is not None:
                        visible[sd] = st[sd]
            elif ev[1] == "TOUCH":
                side, cell = ev[2], int(ev[3])
                if prev is not None and prev[0] != side and visible[side] and prev[1] in visible[side]:
                    n += 1
                    same += int(cell == prev[1])
                    chance.append(1 / len(visible[side]))
                prev = (side, cell)
    if n:
        print(f"   {subject:<8} same cell on {pct(same, n)} of cross-side pairs vs chance {100 * np.mean(chance):.1f}%, "
              f"two-sided exact p = {poibin_two_sided(np.array(chance), same):.2g}")


def phase1_switching(p1):
    if p1 is None:
        return
    print("\nPhase 1 side-switch rates on core trials, all five subjects")
    print("-" * 72)
    for s, d in p1.items():
        c = d[d.Type.isin(DUAL)]
        if c.TouchPairs.sum():
            print(f"   {s:<8} {100 * c.SideSwitches.sum() / c.TouchPairs.sum():.0f}%")


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
    ghosts = []
    for s in subjects:
        t = pd.read_csv(PROC / f"SafetyPop2_{s}_Trials.csv")
        buf = io.StringIO()
        with redirect_stdout(buf):
            ghosts.append(analyze(s, t, p1))
        text = buf.getvalue()
        print(text)
        (RESULTS / f"results_{s}.txt").write_text(text, encoding="utf-8")
    if len(subjects) > 1:
        buf = io.StringIO()
        with redirect_stdout(buf):
            print("SafetyPop Phase 2: across subjects")
            print("=" * 72)
            ghost_pooled(ghosts)
            print("\nExploratory  Cross-divider perseveration (a floor under the ghost rate)")
            print("-" * 72)
            for s in subjects:
                perseveration(s, pd.read_csv(PROC / f"SafetyPop2_{s}_AllSessions.csv"))
            phase1_switching(p1)
        print(buf.getvalue())
        (RESULTS / "results_across_subjects.txt").write_text(buf.getvalue(), encoding="utf-8")


if __name__ == "__main__":
    main()

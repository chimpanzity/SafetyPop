#!/usr/bin/env python3
"""
SafetyPop — within-trial hazard of abandoning Oddity for Bubble Popping.

Time axis = cumulative Oddity ERRORS accrued within the trial.
Competing risks: ABANDON (trial ends via Bubble) vs SUCCEED (trial ends via Oddity).

Core question: is the decision to leave Oddity driven by accumulating EVIDENCE OF
FAILURE (errors), or is it just a clock/persistence limit (total touches)?
"""
import pandas as pd, numpy as np, warnings
import statsmodels.api as sm
warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)

XLSX = "phase1/data/processed/SafetyPop_AllSubjects_CompleteSessions.xlsx"
SUBJECTS = ["Arthur", "Ben", "Billy", "Evelyn", "Rowena"]
MIN_RISK = 15          # suppress hazard estimates from risk sets smaller than this

df = pd.concat([pd.read_excel(XLSX, sheet_name=s).assign(Subj=s) for s in SUBJECTS],
               ignore_index=True)


def touches(t):
    if not isinstance(t, str):
        return []
    out = []
    for e in t.split(";"):
        p = e.split(",")
        if len(p) >= 6:
            out.append(p[5])          # stimTag: Bubble / Target / Distractor
    return out


# ---------------------------------------------------------------- build event table
# One row per ODDITY touch, in core dual-task trials where Oddity was engaged.
rows, trials = [], []
core = df[df.Type.isin(list("ABCD"))]
for _, r in core.iterrows():
    tags = touches(r.TouchLog)
    if not tags:
        continue
    odd_idx = [i for i, t in enumerate(tags) if t in ("Target", "Distractor")]
    if not odd_idx:
        continue
    abandoned = (r.CompletedBy == "Bubble")
    last_odd = odd_idx[-1]
    cum_err = cum_win = 0
    for j, i in enumerate(odd_idx):
        if tags[i] == "Distractor":
            cum_err += 1
        else:
            cum_win += 1
        is_last = (i == last_odd)
        rows.append({
            "Subj": r.Subj, "Session": r.Session, "Type": r.Type, "Trial": r.Trial,
            "BubN": r.BubN, "odd_touch_n": j + 1,
            "cum_err": cum_err, "cum_win": cum_win,
            # event = this oddity touch was the final one AND the trial ended in Bubble
            "event": int(is_last and abandoned),
            "terminal": int(is_last),
        })
    trials.append({"Subj": r.Subj, "Session": r.Session, "Type": r.Type, "BubN": r.BubN,
                   "errors_at_exit": int(r.OddErrors) if pd.notna(r.OddErrors) else 0,
                   "odd_touches": len(odd_idx),
                   "outcome": "abandon" if abandoned else "succeed"})

ev = pd.DataFrame(rows)
tr = pd.DataFrame(trials)
print(f"Core trials with Oddity engaged: {len(tr)}   "
      f"(abandoned {100*(tr.outcome=='abandon').mean():.1f}%, succeeded {100*(tr.outcome=='succeed').mean():.1f}%)")
print(f"Oddity touch events in the risk set: {len(ev)}")


def hazard(t, by_err=True):
    """Discrete-time hazard of ABANDONING at each cumulative-error level."""
    out = []
    kmax = int(t.errors_at_exit.max())
    for k in range(0, kmax + 1):
        risk = t[t.errors_at_exit >= k]
        if len(risk) == 0:
            break
        ab = risk[(risk.errors_at_exit == k) & (risk.outcome == "abandon")]
        su = risk[(risk.errors_at_exit == k) & (risk.outcome == "succeed")]
        out.append({"errors": k, "at_risk": len(risk), "abandoned": len(ab),
                    "succeeded": len(su),
                    "h_abandon": len(ab) / len(risk),
                    "h_succeed": len(su) / len(risk)})
    return pd.DataFrame(out)


def hdr(t):
    print("\n" + "=" * 92); print(t); print("=" * 92)


# ------------------------------------------------------------------ 1. pooled hazard
hdr("1. POOLED HAZARD OF ABANDONING ODDITY, BY CUMULATIVE ERRORS")
h = hazard(tr)
h["h_abandon_pct"] = 100 * h.h_abandon
h["h_succeed_pct"] = 100 * h.h_succeed
show = h[h.at_risk >= MIN_RISK]
print(show[["errors", "at_risk", "abandoned", "succeeded",
            "h_abandon_pct", "h_succeed_pct"]].round(1).to_string(index=False))
print(f"\n(rows with at-risk < {MIN_RISK} suppressed; max errors observed = {int(tr.errors_at_exit.max())})")

# ------------------------------------------------------------------ 2. monotonicity
hdr("2. IS THE HAZARD MONOTONIC IN ERRORS?")
s = show[show.errors <= 8]
r = np.corrcoef(s.errors, s.h_abandon)[0, 1]
print(f"Pearson r(cumulative errors, abandonment hazard) over errors 0-8: {r:+.3f}")
print("Hazard at 0 errors: {:.1f}%   at 4 errors: {:.1f}%   at 8 errors: {:.1f}%".format(
    *[100 * h.loc[h.errors == k, "h_abandon"].iloc[0] for k in (0, 4, 8)]))

# ------------------------------------------------ 3. the discriminating test
hdr("3. MONITORING vs CLOCK — do errors predict leaving, holding touch count constant?")
print("Discrete-time logistic event-history model on oddity-touch events.")
print("event = this oddity touch is the last one and the trial ends in Bubble\n")
# NOTE: cum_err + cum_win == odd_touch_n exactly, so only two of the three are
# identifiable. We keep odd_touch_n (time-on-task) and cum_err (evidence of failure);
# the cum_err coefficient is then the effect of substituting an ERROR for a WIN at a
# FIXED number of oddity touches -- i.e. the pure evidence effect, purged of duration.
m = ev.copy()
m["tid"] = m.Subj + "_" + m.Session.astype(str) + "_" + m.Trial.astype(str)
X = pd.get_dummies(m[["cum_err", "odd_touch_n", "Subj"]],
                   columns=["Subj"], drop_first=True).astype(float)
X = sm.add_constant(X)
fit = sm.Logit(m.event.values, X).fit(disp=0, cov_type="cluster",
                                      cov_kwds={"groups": m.tid.values})
res = pd.DataFrame({"coef": fit.params, "SE": fit.bse, "z": fit.tvalues,
                    "p": fit.pvalues, "OR": np.exp(fit.params)})
print(res.round(3).to_string())
print(f"\nn events = {int(m.event.sum())} / {len(m)} touch-events;  pseudo-R2 = {fit.prsquared:.3f}")
print("\nInterpretation: cum_err OR > 1 with cum_win/odd_touch_n controlled means each additional")
print("ERROR raises the instantaneous odds of quitting beyond mere time-on-task.")

print("\n--- Stratified cross-check (no model): abandonment rate at matched touch counts ---")
strat = []
for t_n in range(2, 9):
    d = ev[ev.odd_touch_n == t_n]
    for lo, hi, lbl in [(0, 1, "0-1 errors"), (2, 3, "2-3 errors"), (4, 99, "4+ errors")]:
        dd = d[(d.cum_err >= lo) & (d.cum_err <= hi)]
        if len(dd) >= 20:
            strat.append({"odd_touch_n": t_n, "err_band": lbl, "n": len(dd),
                          "quit_pct": 100 * dd.event.mean()})
st = pd.DataFrame(strat)
print(st.pivot(index="odd_touch_n", columns="err_band", values="quit_pct").round(1).to_string(na_rep="-"))
print("(cell = % of oddity touches at that touch-number that were the last before quitting)")

# ------------------------------------------------------------------ 4. by session block
hdr("4. DOES THE HAZARD STEEPEN WITH EXPERIENCE?")
tr["block"] = np.where(tr.Session <= 3, "Early (S1-3)",
                np.where(tr.Session <= 6, "Mid (S4-6)", "Late (S7-10)"))
for b in ["Early (S1-3)", "Mid (S4-6)", "Late (S7-10)"]:
    hb = hazard(tr[tr.block == b])
    hb = hb[hb.at_risk >= MIN_RISK]
    vals = " ".join(f"{100*hb.loc[hb.errors==k,'h_abandon'].iloc[0]:5.1f}"
                    if k in hb.errors.values else "    -" for k in range(0, 9))
    print(f"  {b:<14} n_trials={len(tr[tr.block==b]):<5} hazard at errors 0-8: {vals}")
print("\n  Median errors at exit, abandoned trials only:")
ab = tr[tr.outcome == "abandon"]
print("   ", ab.groupby("block").errors_at_exit.agg(["median", "mean", "count"]).round(2).to_dict("index"))

print("\n  Model with session interaction (does cum_err get more potent over sessions?):")
m2 = ev.copy()
m2["err_x_session"] = m2.cum_err * m2.Session
m2["tid"] = m2.Subj + "_" + m2.Session.astype(str) + "_" + m2.Trial.astype(str)
X2 = pd.get_dummies(m2[["cum_err", "odd_touch_n", "Session",
                        "err_x_session", "Subj"]], columns=["Subj"], drop_first=True).astype(float)
X2 = sm.add_constant(X2)
f2 = sm.Logit(m2.event.values, X2).fit(disp=0, cov_type="cluster",
                                       cov_kwds={"groups": m2.tid.values})
print(pd.DataFrame({"coef": f2.params, "z": f2.tvalues, "p": f2.pvalues,
                    "OR": np.exp(f2.params)}).loc[
    ["cum_err", "Session", "err_x_session"]].round(4).to_string())

# ------------------------------------------------------------------ 5. cost sensitivity
hdr("5. IS THE THRESHOLD SENSITIVE TO THE COST OF THE ESCAPE ROUTE?")
print("4-bubble trials (A, C: cheap escape) vs 8-bubble trials (B, D: expensive escape)")
for lbl, tt in [("4 bubbles (A,C)", ["A", "C"]), ("8 bubbles (B,D)", ["B", "D"])]:
    d = tr[tr.Type.isin(tt)]
    hb = hazard(d); hb = hb[hb.at_risk >= MIN_RISK]
    vals = " ".join(f"{100*hb.loc[hb.errors==k,'h_abandon'].iloc[0]:5.1f}"
                    if k in hb.errors.values else "    -" for k in range(0, 9))
    ab = d[d.outcome == "abandon"]
    print(f"  {lbl:<18} n={len(d):<5} median errors at exit={ab.errors_at_exit.median():.1f}  "
          f"hazard 0-8: {vals}")
print("\n  Model with BubN (cost of escaping) added:")
m3 = ev.copy()
m3["tid"] = m3.Subj + "_" + m3.Session.astype(str) + "_" + m3.Trial.astype(str)
X3 = pd.get_dummies(m3[["cum_err", "odd_touch_n", "BubN", "Subj"]],
                    columns=["Subj"], drop_first=True).astype(float)
X3 = sm.add_constant(X3)
f3 = sm.Logit(m3.event.values, X3).fit(disp=0, cov_type="cluster",
                                       cov_kwds={"groups": m3.tid.values})
print(pd.DataFrame({"coef": f3.params, "z": f3.tvalues, "p": f3.pvalues,
                    "OR": np.exp(f3.params)}).loc[["cum_err", "BubN"]].round(4).to_string())

# ------------------------------------------------------------------ 6. per subject
hdr("6. PER-SUBJECT ABANDONMENT THRESHOLD (individual-differences measure)")
out = []
for s in SUBJECTS:
    d = tr[tr.Subj == s]
    ab = d[d.outcome == "abandon"]
    hb = hazard(d)
    # per-subject slope of hazard on errors, 0-6
    hs = hb[(hb.at_risk >= 10) & (hb.errors <= 6)]
    slope = np.polyfit(hs.errors, 100 * hs.h_abandon, 1)[0] if len(hs) > 2 else np.nan
    ms = ev[ev.Subj == s]
    tid = ms.Subj + "_" + ms.Session.astype(str) + "_" + ms.Trial.astype(str)
    Xs = sm.add_constant(ms[["cum_err", "odd_touch_n"]].astype(float))
    fs = sm.Logit(ms.event.values, Xs).fit(disp=0, cov_type="cluster",
                                           cov_kwds={"groups": tid.values})
    out.append({"Subject": s, "n_trials": len(d),
                "abandon_%": 100 * (d.outcome == "abandon").mean(),
                "median_err_at_exit": ab.errors_at_exit.median(),
                "mean_err_at_exit": ab.errors_at_exit.mean(),
                "hazard_slope_pp_per_err": slope,
                "OR_per_error": np.exp(fs.params["cum_err"]),
                "z": fs.tvalues["cum_err"]})
print(pd.DataFrame(out).round(2).to_string(index=False))

h.to_csv("phase1/data/processed/hazard_pooled.csv", index=False)
tr.to_csv("phase1/data/processed/hazard_trials.csv", index=False)
ev.to_csv("phase1/data/processed/hazard_events.csv", index=False)
print("\n[saved hazard_pooled.csv, hazard_trials.csv, hazard_events.csv]")

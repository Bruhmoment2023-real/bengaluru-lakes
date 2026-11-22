"""v18 analyses: can Bengaluru's official lake-monitoring data confirm themselves?

Added 22 Nov 2026 (protocol amendment A10). Uses only the compiled dataset; no new data.
Hypotheses H1-H8 are stated in docs/02b-v18-hypotheses.md (written before this script was run).
H1 and H2 formalise two patterns first seen in exploratory work (amendment A4); H3-H8 were specified after the
dataset was complete and are exploratory. Holm correction is applied across the four new primary tests (H4 DO,
H6 COD, H7 undated-vs-dated, H5 is descriptive and has no test).

Run:  python -X utf8 -I code/v18_self_confirmation_tests.py <path to full lake_measurements_long.csv> [outdir]
The FULL 108,915-row table is needed for H1 (CPCB), H6 (2011 table). With only the public 94,941-row release those
two blocks are skipped. Needs numpy, pandas, scipy, statsmodels.
"""
import sys, os, json, math
import numpy as np, pandas as pd
from scipy import stats

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "release", "lake_measurements_long.csv")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join("results", "v18")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261122)
KEY = {}          # every number quoted in the paper goes here and into results/v18/v18_key_numbers.json


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, j in enumerate(o):
        run = max(run, (m - i) * p[j]); adj[j] = min(1, run)
    return adj


def wilson(k, n, z=1.959964):
    if n == 0: return (np.nan, np.nan)
    p = k / n; den = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / den, (c + h) / den)


def boot_ci(x, fn=np.median, B=5000):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) < 3: return (np.nan, np.nan)
    bs = [fn(rng.choice(x, len(x))) for _ in range(B)]
    return tuple(np.percentile(bs, [2.5, 97.5]))


d = pd.read_csv(SRC, low_memory=False)
d = d[~d.analysis_use.fillna("").str.startswith("exclude: not a lake")]
HAS_FULL = {"CPCB", "DMG2011"} <= set(d.record_id)
KEY["rows_used"] = int(len(d)); KEY["full_table"] = bool(HAS_FULL)

# ------------------------------------------------------------------ KSPCB lake-month table (same construction as analysis_compliance_trends.py)
k = d[(d.record_id == "KSPCB") & (d.statistic == "single")].copy()
k["ym"] = k.date_start.str[:7]
w = k.pivot_table(index=["lake_key", "station_code", "ym"], columns="parameter_std", values="value_std", aggfunc="first").reset_index()
w["year"] = w.ym.str[:4].astype(int); w["month"] = w.ym.str[5:7].astype(int)
KEY["kspcb_lake_months"] = int(len(w)); KEY["kspcb_lakes"] = int(w.lake_key.nunique()); KEY["kspcb_stations"] = int(w.station_code.nunique())
KEY["kspcb_months_with_data"] = int(w.ym.nunique())


def klass(r, bod_override=None):
    g = lambda c: r.get(c, np.nan)
    DO, BOD, TC, pH, NH, EC, B = g("DO"), g("BOD"), g("total_coliform_MPN"), g("pH"), g("ammoniacal_N"), g("EC"), g("boron")
    if bod_override is not None and not np.isnan(BOD) and BOD <= bod_override: BOD = 2.0   # could be as low as the class A limit
    ok = lambda x, f: (not np.isnan(x)) and f(x)
    if all(not np.isnan(x) for x in (DO, BOD, TC, pH)):
        if DO >= 6 and BOD <= 2 and TC <= 50 and 6.5 <= pH <= 8.5: return "A"
        if DO >= 5 and BOD <= 3 and TC <= 500 and 6.5 <= pH <= 8.5: return "B"
        if DO >= 4 and BOD <= 3 and TC <= 5000 and 6 <= pH <= 9: return "C"
    if not np.isnan(DO) and not np.isnan(pH):
        if DO >= 4 and 6.5 <= pH <= 8.5 and (np.isnan(NH) or NH <= 1.2): return "D"
        if 6 <= pH <= 8.5 and ok(EC, lambda x: x <= 2250) and (np.isnan(B) or B <= 2): return "E"
        return "below E"
    return "unclassified"


w["class_printed"] = w.apply(klass, axis=1)
# sanity: must reproduce the paper's class shares
cs = w.class_printed.value_counts(normalize=True)
KEY["check_class_D_share"] = round(float(cs.get("D", 0)) * 100, 1); KEY["check_class_E_share"] = round(float(cs.get("E", 0)) * 100, 1)
KEY["check_belowE_share"] = round(float(cs.get("below E", 0)) * 100, 1)
KEY["check_n_classified_lake_months"] = int(len(w)); KEY["check_BOD_gt3_share"] = round(float((w.BOD > 3).sum() / w.BOD.notna().sum()) * 100, 1)
KEY["check_n_with_BOD"] = int(w.BOD.notna().sum())

# ================================================================== H1 independence of the two official series
if HAS_FULL:
    c = d[(d.record_id == "CPCB") & d.statistic.isin(["min", "max"])]
    cw = c.pivot_table(index=["station_code", "year"], columns=["parameter_std", "statistic"], values="value_std", aggfunc="first")
    cw.columns = [f"{a}_{b}" for a, b in cw.columns]; cw = cw.reset_index()
    rows = []; perm_rows = []
    for par in ("BOD", "DO"):
        lo, hi = f"{par}_min", f"{par}_max"
        for yr in (2023, 2024):
            kp = w[(w.year == yr) & w[par].notna()][["station_code", "ym", par]]
            cr = cw[(cw.year == yr) & cw[lo].notna() & cw[hi].notna()].set_index("station_code")[[lo, hi]]
            kp = kp[kp.station_code.isin(cr.index)].reset_index(drop=True)
            n = len(kp)
            v = kp[par].values; los = cr.loc[kp.station_code, lo].values; his = cr.loc[kp.station_code, hi].values
            inside = (v >= los - 1e-9) & (v <= his + 1e-9); kin = int(inside.sum())
            # null A: every KSPCB lake-month against the range of every OTHER station in the same year (exact mean)
            cl, ch = cr[lo].values, cr[hi].values; stn_idx = {s: i for i, s in enumerate(cr.index)}
            nullA = []
            for vv, s in zip(v, kp.station_code):
                m = np.ones(len(cl), bool); m[stn_idx[s]] = False
                nullA.append(((vv >= cl[m] - 1e-9) & (vv <= ch[m] + 1e-9)).mean())
            pA = float(np.mean(nullA))
            # null B: same station, CPCB ranges of 2016-2022
            ins_b = []; nb = 0
            for (s, ym, vv) in kp.itertuples(index=False):
                g_ = cw[(cw.station_code == s) & cw.year.between(2016, 2022) & cw[lo].notna() & cw[hi].notna()]
                for a, b in zip(g_[lo], g_[hi]): ins_b.append(a - 1e-9 <= vv <= b + 1e-9)
            pB = float(np.mean(ins_b)) if ins_b else np.nan
            # permutation test: shuffle which station's CPCB range goes with which station (5,000 shuffles, station-level)
            stns = list(cr.index); obs = kin / n
            cnt = 0; B_ = 5000; perm_vals = []
            by_stn = {s: np.where(kp.station_code.values == s)[0] for s in stns}
            for _ in range(B_):
                perm = rng.permutation(len(stns)); tot = 0
                for i, s in enumerate(stns):
                    idx = by_stn[s]
                    if len(idx) == 0: continue
                    j = perm[i]; tot += ((v[idx] >= cl[j] - 1e-9) & (v[idx] <= ch[j] + 1e-9)).sum()
                perm_vals.append(tot / n)
            perm_vals = np.array(perm_vals); p_perm = (1 + (perm_vals >= obs - 1e-12).sum()) / (B_ + 1)
            # exact binomial against the highest null (conservative)
            p0 = max(pA, pB if not np.isnan(pB) else 0)
            logp = stats.binom.logsf(kin - 1, n, p0) / math.log(10) if kin > 0 else 0.0
            lo_ci, hi_ci = wilson(kin, n)
            rows.append(dict(parameter=par, year=yr, stations=int(kp.station_code.nunique()), lake_months=n, inside=kin, share_inside=round(obs, 4),
                             wilson_lo=round(lo_ci, 4), wilson_hi=round(hi_ci, 4), null_other_station_same_year=round(pA, 4),
                             null_same_station_2016_2022=round(pB, 4), perm_null_mean=round(float(perm_vals.mean()), 4),
                             perm_null_max=round(float(perm_vals.max()), 4), p_perm=round(p_perm, 5), p0_binomial=round(p0, 4),
                             log10_p_binomial=round(float(logp), 1), diff_vs_null_pp=round(100 * (obs - p0), 1)))
    h1 = pd.DataFrame(rows); h1.to_csv(os.path.join(OUT, "v18_H1_independence.csv"), index=False); print(h1.to_string())
    # station-level: share of stations whose KSPCB values ALL lie inside the matched CPCB range
    st = []
    for par in ("BOD", "DO"):
        lo, hi = f"{par}_min", f"{par}_max"
        for yr in (2023, 2024):
            kp = w[(w.year == yr) & w[par].notna()]; cr = cw[(cw.year == yr)].set_index("station_code")
            for s, g_ in kp.groupby("station_code"):
                if s in cr.index and pd.notna(cr.loc[s, lo]) and pd.notna(cr.loc[s, hi]):
                    st.append(dict(parameter=par, year=yr, station=s, n=len(g_), all_inside=bool(((g_[par] >= cr.loc[s, lo] - 1e-9) & (g_[par] <= cr.loc[s, hi] + 1e-9)).all())))
    st = pd.DataFrame(st); KEY["H1_station_level"] = st.groupby(["parameter", "year"]).agg(stations=("station", "size"), all_inside=("all_inside", "sum")).reset_index().to_dict("records")
    KEY["H1"] = h1.to_dict("records")
    # Does the CPCB min-max reproduce KSPCB min/max exactly? (stronger than containment)
    ex = []
    for par in ("BOD", "DO"):
        lo, hi = f"{par}_min", f"{par}_max"
        for yr in (2023, 2024):
            kp = w[(w.year == yr) & w[par].notna()].groupby("station_code")[par].agg(["min", "max"]); cr = cw[(cw.year == yr)].set_index("station_code")
            j = kp.join(cr[[lo, hi]], how="inner").dropna()
            ex.append(dict(parameter=par, year=yr, stations=len(j), min_equal=int(np.isclose(j["min"], j[lo]).sum()), max_equal=int(np.isclose(j["max"], j[hi]).sum()),
                           both_equal=int((np.isclose(j["min"], j[lo]) & np.isclose(j["max"], j[hi])).sum())))
    ex = pd.DataFrame(ex); ex.to_csv(os.path.join(OUT, "v18_H1b_range_equals_extremes.csv"), index=False); KEY["H1b"] = ex.to_dict("records"); print(ex.to_string())

# ================================================================== H2 reporting floor and bounds on compliance
bod = w.BOD.dropna()
KEY["H2_n_bod"] = int(len(bod)); KEY["H2_bod_min"] = float(bod.min())
KEY["H2_share_below_3p2"] = float((bod < 3.2).mean()); KEY["H2_share_exact4"] = float((bod == 4).mean()); KEY["H2_share_exact5"] = float((bod == 5).mean())
KEY["H2_share_integer"] = float((bod == bod.round()).mean())
rng_ = bod[(bod >= 3.2) & (bod <= 10)]
KEY["H2_integer_share_3p2_10"] = float((rng_ == rng_.round()).mean()); KEY["H2_n_3p2_10"] = int(len(rng_))
# independent comparators: published studies with BOD values (same lake-month-level statistic where possible)
lit = d[d.record_id.str.startswith("L") & (d.parameter_std == "BOD") & d.statistic.isin(["single", "mean"]) & d.value_std.notna()
        & ~d.analysis_use.fillna("").str.startswith("exclude")]
comp = []
for rid, g_ in lit.groupby("record_id"):
    x = g_.value_std
    comp.append(dict(record=rid, n=len(x), min=float(x.min()), share_lt_3p2=float((x < 3.2).mean()), n_lt_3p2=int((x < 3.2).sum()), share_integer=float((x == x.round()).mean())))
comp = pd.DataFrame(comp).sort_values("n", ascending=False); comp.to_csv(os.path.join(OUT, "v18_H2_bod_lowvalues_by_source.csv"), index=False); print(comp.to_string())
big = lit[lit.record_id.isin(comp[comp.n >= 20].record)]
KEY["H2_lit_n"] = int(len(big)); KEY["H2_lit_n_lt_3p2"] = int((big.value_std < 3.2).sum()); KEY["H2_lit_sources"] = comp[comp.n >= 20].record.tolist()
a, b, c_, d_ = 0, len(bod), int((big.value_std < 3.2).sum()), len(big)
_, KEY["H2_fisher_p_floor"] = stats.fisher_exact([[a, b - a], [c_, d_ - c_]], alternative="less")
# heaping: share of values that are whole numbers among 3.2-10 mg/L, versus the share expected if reported to 0.1 mg/L (10%)
nint = int((rng_ == rng_.round()).sum()); KEY["H2_binom_p_integer_vs_10pct"] = float(stats.binomtest(nint, len(rng_), 0.10, alternative="greater").pvalue)
# local heaping at 4.0 and 5.0 against the four neighbouring 0.1-steps
def heaping(x, c0, step=0.1, nb=2):
    cnt = lambda v: int(np.isclose(x, v, atol=1e-9).sum())
    nbs = [cnt(round(c0 + s * step, 2)) for s in range(-nb, nb + 1) if s != 0]
    return cnt(c0), nbs
hp = []
for c0 in (4.0, 5.0, 6.0):
    n0, nbs = heaping(bod.values, c0)
    mean_nb = float(np.mean(nbs)); ratio = n0 / mean_nb if mean_nb > 0 else np.inf
    # conditional binomial: given the count at c0 + its neighbours, is c0's share > 1/(1+#neighbours)?
    tot = n0 + sum(nbs); p = stats.binomtest(n0, tot, 1 / (1 + len(nbs)), alternative="greater").pvalue
    hp.append(dict(value=c0, count=n0, neighbours=str(nbs), mean_neighbour=mean_nb, ratio=ratio, p_binom=p))
hp = pd.DataFrame(hp); hp.to_csv(os.path.join(OUT, "v18_H2_heaping.csv"), index=False); KEY["H2_heaping"] = hp.to_dict("records"); print(hp.to_string())
# bounds on the share of lake-months over the BOD limit and on class compliance if values at or below f are treated as unknown
bd = []
nB = w.BOD.notna().sum()
for f in (None, 3.2, 4.0, 5.0, 6.0):
    if f is None:
        over = (w.BOD > 3).sum(); lab = "as printed"
        cl_ = w.class_printed
    else:
        over = (w.BOD > max(f, 3)).sum(); lab = f"values <= {f} treated as possibly <= 2"
        cl_ = w.apply(lambda r: klass(r, f), axis=1)
    shares = cl_.value_counts(normalize=True)
    bd.append(dict(scenario=lab, floor=f if f else np.nan, share_BOD_over_3_lower_bound=round(100 * over / nB, 1), n_over=int(over), n_with_bod=int(nB),
                   share_class_A=round(100 * shares.get("A", 0), 1), share_class_B=round(100 * shares.get("B", 0), 1), share_class_C=round(100 * shares.get("C", 0), 1),
                   share_class_ABC=round(100 * sum(shares.get(x, 0) for x in "ABC"), 1)))
bd = pd.DataFrame(bd); bd.to_csv(os.path.join(OUT, "v18_H2_compliance_bounds.csv"), index=False); KEY["H2_bounds"] = bd.to_dict("records"); print(bd.to_string())

# ================================================================== H3 per-lake designated-use status with bounds, and the binding parameter
w["fail_DO"] = w.DO < 4; w["fail_BOD"] = w.BOD > 3; w["fail_TC"] = w.total_coliform_MPN > 5000; w["fail_pH"] = (w.pH < 6) | (w.pH > 9)
w["fail_BOD_floor5"] = w.BOD > 5
w["class_floor5"] = w.apply(lambda r: klass(r, 5.0), axis=1)
per = w.groupby("lake_key").agg(lake_months=("ym", "size"), pct_DO_lt4=("fail_DO", "mean"), pct_BOD_gt3=("fail_BOD", "mean"), pct_BOD_gt5=("fail_BOD_floor5", "mean"),
                                pct_TC_gt5000=("fail_TC", "mean"), pct_pH_out=("fail_pH", "mean"))
per["binding_printed"] = per[["pct_DO_lt4", "pct_BOD_gt3", "pct_TC_gt5000", "pct_pH_out"]].idxmax(axis=1).str.replace("pct_", "")
per["n_months_class_ABC_if_floor5"] = w.assign(x=w.class_floor5.isin(list("ABC"))).groupby("lake_key").x.sum()
per["n_months_class_ABC_printed"] = w.assign(x=w.class_printed.isin(list("ABC"))).groupby("lake_key").x.sum()
per["best_class_modal_printed"] = w.groupby("lake_key").class_printed.agg(lambda s: s.mode().iloc[0])
per.reset_index().to_csv(os.path.join(OUT, "v18_H3_per_lake_status.csv"), index=False)
KEY["H3_lakes"] = int(len(per)); KEY["H3_binding_printed_counts"] = per.binding_printed.value_counts().to_dict()
KEY["H3_lakes_with_any_ABC_floor5"] = int((per.n_months_class_ABC_if_floor5 > 0).sum())
KEY["H3_lakeMonths_ABC_floor5"] = int(per.n_months_class_ABC_if_floor5.sum()); KEY["H3_lakeMonths_ABC_printed"] = int(per.n_months_class_ABC_printed.sum())
KEY["H3_lakes_median_months"] = float(per.lake_months.median())
KEY["H3_lakes_ge12_months"] = int((per.lake_months >= 12).sum())
KEY["H3_lakes_every_month_BOD_gt5"] = int((per.pct_BOD_gt5 == 1).sum()); KEY["H3_lakes_every_month_BOD_gt3"] = int((per.pct_BOD_gt3 == 1).sum())
KEY["H3_lakes_DO_lt4_majority"] = int((per.pct_DO_lt4 > 0.5).sum())
print(per.binding_printed.value_counts(), KEY["H3_lakes_with_any_ABC_floor5"], KEY["H3_lakeMonths_ABC_floor5"])

# ================================================================== H4 seasonality (dry Jan-May vs wet Jun-Dec), lake as its own control
import statsmodels.formula.api as smf
w["dry"] = w.month.between(1, 5)
w["logBOD"] = np.log10(w.BOD.where(w.BOD > 0)); w["logTC"] = np.log10(w.total_coliform_MPN.where(w.total_coliform_MPN > 0))
w["site"] = w.lake_key + "_" + w.station_code.astype(int).astype(str)
season_rows = []
H4p = {}
for par, lab in (("DO", "DO (mg/L)"), ("logBOD", "log10 BOD"), ("logTC", "log10 total coliform")):
    for scope, mask in (("all months", w.year > 0), ("2024 only", w.year == 2024), ("2025 only", w.year == 2025)):
        s = w[mask & w[par].notna()]
        g = s.groupby(["site", "dry"])[par].agg(["median", "size"]).unstack()
        ok = g[("size", True)].ge(2) & g[("size", False)].ge(2)
        diff = (g[("median", True)] - g[("median", False)])[ok].dropna()
        if len(diff) < 8: continue
        wil = stats.wilcoxon(diff) if (diff != 0).sum() > 0 else None
        lo_, hi_ = boot_ci(diff)
        # fixed-effects regression with site effects, SE clustered on site
        try:
            m = smf.ols(f"{par} ~ dry + C(site)", data=s).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(s.site)[0]})
            b, se, pv = float(m.params["dry[T.True]"]), float(m.bse["dry[T.True]"]), float(m.pvalues["dry[T.True]"])
        except Exception as e:
            b = se = pv = np.nan
        season_rows.append(dict(parameter=lab, scope=scope, sites=int(len(diff)), median_dry_minus_wet=round(float(diff.median()), 3), boot_lo=round(lo_, 3), boot_hi=round(hi_, 3),
                                share_sites_higher_dry=round(float((diff > 0).mean()), 3), wilcoxon_p=wil.pvalue if wil else np.nan, FE_coef=round(b, 3), FE_se=round(se, 3), FE_p=pv,
                                months_dry=int(s[s.dry].ym.nunique()), months_wet=int(s[~s.dry].ym.nunique())))
sr = pd.DataFrame(season_rows); sr.to_csv(os.path.join(OUT, "v18_H4_seasonality.csv"), index=False); print(sr.to_string())
KEY["H4"] = sr.to_dict("records")
print("H4 table done",flush=True)
# the first-half-2024 rise: share of lake-months below class E, dry 2024 vs dry 2025 (descriptive; lake-months are not independent)
bE = w.assign(below=w.class_printed.eq("below E"))
a24 = bE[(bE.year == 2024) & bE.dry]; a25 = bE[(bE.year == 2025) & bE.dry]
tab = [[int(a24.below.sum()), int((~a24.below).sum())], [int(a25.below.sum()), int((~a25.below).sum())]]
KEY["H4_belowE_dry2024"] = tab[0]; KEY["H4_belowE_dry2025"] = tab[1]; KEY["H4_belowE_fisher_p"] = float(stats.fisher_exact(tab)[1])
KEY["H4_belowE_share_dry2024"] = tab[0][0] / sum(tab[0]); KEY["H4_belowE_share_dry2025"] = tab[1][0] / sum(tab[1])
# same-month year comparison (Jan-Nov): paired by site, DO in 2025 minus 2024
yy = w[w.month <= 11].groupby(["site", "year", "month"]).DO.first().reset_index()
p24 = yy[yy.year == 2024].set_index(["site", "month"]).DO; p25 = yy[yy.year == 2025].set_index(["site", "month"]).DO
j = pd.concat([p24.rename("y24"), p25.rename("y25")], axis=1).dropna()
KEY["H4_sameMonth_pairs"] = int(len(j)); KEY["H4_sameMonth_median_DO_2025_minus_2024"] = float((j.y25 - j.y24).median())
KEY["H4_sameMonth_wilcoxon_p"] = float(stats.wilcoxon(j.y25 - j.y24).pvalue)

print("pre-H5",flush=True)
# ================================================================== H5 between-site vs within-site variance (ICC) and the share explained by calendar month
def icc1(df, y, grp):
    g = df[[y, grp]].dropna(); n_i = g.groupby(grp)[y].size(); k_ = len(n_i); N = len(g)
    if k_ < 2: return np.nan
    gm = g[y].mean(); means = g.groupby(grp)[y].mean()
    ssb = (n_i * (means - gm) ** 2).sum(); ssw = ((g[y] - g[grp].map(means)) ** 2).sum()
    msb = ssb / (k_ - 1); msw = ssw / (N - k_); n0 = (N - (n_i ** 2).sum() / N) / (k_ - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw)

def icc_boot(df, y, grp, B=1000):
    g = df[[y, grp]].dropna(); st_ = g.groupby(grp)[y].agg(["size", "sum"]); st_["ss"] = g.assign(q=g[y] ** 2).groupby(grp).q.sum()
    n_i = st_["size"].values.astype(float); s_i = st_["sum"].values; q_i = st_["ss"].values; K = len(n_i); vals = []
    for _ in range(B):
        ix = rng.integers(0, K, K); n = n_i[ix]; s = s_i[ix]; q = q_i[ix]; N = n.sum(); gm = s.sum() / N
        ssb = (n * (s / n - gm) ** 2).sum(); ssw = (q - s ** 2 / n).sum()
        msb = ssb / (K - 1); msw = ssw / (N - K); n0 = (N - (n ** 2).sum() / N) / (K - 1)
        vals.append((msb - msw) / (msb + (n0 - 1) * msw))
    return tuple(np.nanpercentile(vals, [2.5, 97.5]))

icc_rows = []
ws = w[w.site.map(w.site.value_counts()) >= 12]            # sites with at least 12 months
KEY["H5_sites_ge12"] = int(ws.site.nunique()); KEY["H5_lake_months_ge12"] = int(len(ws))
for par, lab in (("DO", "DO"), ("logBOD", "log10 BOD"), ("logTC", "log10 total coliform"), ("pH", "pH"), ("EC", "conductivity (uS/cm)")):
    s = ws[ws[par].notna()].copy()
    if par == "EC": s["EC"] = np.log10(s.EC.where(s.EC > 0)); s = s[s.EC.notna()]; lab = "log10 conductivity"
    print("icc",par,flush=True)
    ic = icc1(s, par, "site"); lo_, hi_ = icc_boot(s, par, "site")
    # incremental R2 of calendar month (27 study months) after site effects
    print("ols",par,flush=True)
    m0 = smf.ols(f"{par} ~ C(site)", data=s).fit(); m1 = smf.ols(f"{par} ~ C(site) + C(ym)", data=s).fit()
    icc_rows.append(dict(parameter=lab, sites=int(s.site.nunique()), observations=int(len(s)), ICC_site=round(ic, 3), ICC_lo=round(lo_, 3), ICC_hi=round(hi_, 3),
                         R2_site=round(float(m0.rsquared), 3), R2_extra_month=round(float(m1.rsquared - m0.rsquared), 3), residual_share=round(float(1 - m1.rsquared), 3)))
ic = pd.DataFrame(icc_rows)
# CPCB 2016-2022 (not derived from the KSPCB window): station vs year, annual max BOD and min DO
if HAS_FULL:
    cp = cw[(cw.year.between(2016, 2022))].copy()
    cp["logBODmax"] = np.log10(cp.BOD_max.where(cp.BOD_max > 0)); cp["stn"] = cp.station_code.astype(str)
    cp = cp[cp.stn.map(cp.stn.value_counts()) >= 5]
    for par, lab in (("logBODmax", "CPCB 2016-22 annual max BOD (log10)"), ("DO_min", "CPCB 2016-22 annual min DO")):
        s = cp[cp[par].notna()]
        i_ = icc1(s, par, "stn"); lo_, hi_ = icc_boot(s, par, "stn", B=500)
        m0 = smf.ols(f"{par} ~ C(stn)", data=s).fit(); m1 = smf.ols(f"{par} ~ C(stn) + C(year)", data=s).fit()
        ic = pd.concat([ic, pd.DataFrame([dict(parameter=lab, sites=int(s.stn.nunique()), observations=int(len(s)), ICC_site=round(i_, 3), ICC_lo=round(lo_, 3), ICC_hi=round(hi_, 3),
                                                  R2_site=round(float(m0.rsquared), 3), R2_extra_month=round(float(m1.rsquared - m0.rsquared), 3), residual_share=round(float(1 - m1.rsquared), 3))])])
ic.to_csv(os.path.join(OUT, "v18_H5_variance_decomposition.csv"), index=False); print(ic.to_string()); KEY["H5"] = ic.to_dict("records")

# ================================================================== H6 inlet-to-outlet gradient in the 2011 table
if HAS_FULL:
    g11 = d[(d.record_id == "DMG2011") & d.value_std.notna()]
    h6 = []; h6p = {}
    for par in ("COD", "DO", "nitrate_N", "phosphate_P", "TSS", "chloride"):
        p_ = g11[g11.parameter_std == par].pivot_table(index="lake_key", columns="site", values="value_std", aggfunc="median")
        if not {"inlet", "outlet"} <= set(p_.columns): continue
        pr = p_[["inlet", "outlet"]].dropna(); n = len(pr)
        row = dict(parameter=par, lakes_with_inlet_and_outlet=n)
        if n >= 8:
            pos = pr[(pr.inlet > 0) & (pr.outlet > 0)]
            lr = np.log(pos.outlet / pos.inlet); wil = stats.wilcoxon(pr.outlet - pr.inlet)
            lo_, hi_ = boot_ci(lr); row.update(dict(n_positive_pairs=len(pos), median_inlet=float(pr.inlet.median()), median_outlet=float(pr.outlet.median()),
                       median_log_ratio_outlet_over_inlet=round(float(lr.median()), 3), ratio=round(math.exp(float(lr.median())), 3), ratio_lo=round(math.exp(lo_), 3), ratio_hi=round(math.exp(hi_), 3),
                       share_outlet_lower=round(float((pr.outlet < pr.inlet).mean()), 3), wilcoxon_p=wil.pvalue))
        h6.append(row)
    h6 = pd.DataFrame(h6)
    h6["p_holm_over_tested"] = np.nan
    t_ = h6.wilcoxon_p.notna(); h6.loc[t_, "p_holm_over_tested"] = holm(h6.loc[t_, "wilcoxon_p"])
    # sensitivity: drop lakes with any implausible-value flag, and values above the 99th percentile
    sens = []
    for par in ("COD", "nitrate_N", "phosphate_P", "TSS"):
        x = g11[g11.parameter_std == par]; cut = x.value_std.quantile(0.95); x = x[x.value_std <= cut]
        p_ = x.pivot_table(index="lake_key", columns="site", values="value_std", aggfunc="median")
        if {"inlet", "outlet"} <= set(p_.columns):
            pr = p_[["inlet", "outlet"]].dropna()
            if len(pr) >= 8: sens.append(dict(parameter=par, scope="values below the 95th percentile", lakes=len(pr), median_diff_outlet_minus_inlet=float((pr.outlet - pr.inlet).median()), wilcoxon_p=float(stats.wilcoxon(pr.outlet - pr.inlet).pvalue)))
    pd.DataFrame(sens).to_csv(os.path.join(OUT, "v18_H6_sensitivity.csv"), index=False)
    h6.to_csv(os.path.join(OUT, "v18_H6_inlet_outlet.csv"), index=False); print(h6.to_string()); print(pd.DataFrame(sens).to_string())
    KEY["H6"] = h6.to_dict("records"); KEY["H6_sens"] = sens
    KEY["H6_dmg_lakes"] = int(g11.lake_key.nunique()); KEY["H6_sites"] = g11.site.value_counts().to_dict()
    KEY["H6_DO_values"] = int((g11.parameter_std == "DO").sum()); KEY["H6_DO_max"] = float(g11[g11.parameter_std == "DO"].value_std.max())
    KEY["H6_lakes_inlet_outlet_any"] = int(g11.pivot_table(index="lake_key", columns="site", values="value_std", aggfunc="size").dropna(subset=["inlet", "outlet"]).shape[0]) if {"inlet", "outlet"} <= set(g11.site) else 0

# ================================================================== H7 published-versus-official disagreement and study quality
st = pd.read_csv(os.path.join(os.path.dirname(SRC), "studies.csv"))[["record_id", "year", "quality_score"]].rename(columns={"year": "pub_year"})
excl_ids = {"L112", "L462"}                      # secondary compilations of KSPCB / CPCB data, not independent measurements
lit = d[d.record_id.str.startswith("L") & ~d.record_id.isin(excl_ids) & d.statistic.isin(["single", "mean", "median"]) & d.value_std.notna() & (d.value_std > 0)
        & ~d.analysis_use.fillna("").str.startswith("exclude")]
ofc = d[(d.record_id == "KSPCB") & (d.statistic == "single") & d.value_std.notna() & (d.value_std > 0)]
pars = [p for p in ("BOD", "DO", "EC", "COD", "nitrate_N", "TDS", "total_hardness", "chloride", "sulphate", "turbidity", "ammoniacal_N", "total_coliform_MPN", "faecal_coliform_MPN") if p in set(lit.parameter_std)]
om = ofc.groupby(["lake_key", "parameter_std"]).value_std.agg(["median", "size"]).rename(columns={"median": "official_median", "size": "official_n"}).reset_index()
lm = lit.groupby(["record_id", "lake_key", "parameter_std"]).agg(study_median=("value_std", "median"), study_n=("value_std", "size"), year=("year", "min")).reset_index()
pp = lm.merge(om, on=["lake_key", "parameter_std"]).merge(st, on="record_id")
pp = pp[pp.parameter_std.isin(pars)].copy()
pp["abs_log10_ratio"] = np.abs(np.log10(pp.study_median / pp.official_median)); pp["log10_ratio"] = np.log10(pp.study_median / pp.official_median)
pp["undated"] = pp.year.isna(); pp["low_quality"] = pp.quality_score < 3; pp["small"] = pp.study_n < 10
pp["year_gap"] = (2024 - pp.year).abs()
pp.to_csv(os.path.join(OUT, "v18_H7_pairs.csv"), index=False)
KEY["H7_pairs"] = int(len(pp)); KEY["H7_studies"] = int(pp.record_id.nunique()); KEY["H7_lakes"] = int(pp.lake_key.nunique()); KEY["H7_params"] = pp.parameter_std.value_counts().to_dict()
KEY["H7_overall_median_abs_log10"] = float(pp.abs_log10_ratio.median()); KEY["H7_overall_median_ratio_factor"] = float(10 ** pp.abs_log10_ratio.median())
KEY["H7_share_within_factor2"] = float((pp.abs_log10_ratio <= math.log10(2)).mean())
KEY["H7_share_within_factor3"] = float((pp.abs_log10_ratio <= math.log10(3)).mean())
KEY["H7_studies_list"] = sorted(pp.record_id.unique().tolist())
h7 = []
def clustered_diff(df, flag, B=5000):
    # bootstrap over STUDIES (the unit that carries the quality attributes) of the difference in median |log ratio|
    ids = df.record_id.unique(); out = []
    byid = {i: df[df.record_id == i] for i in ids}
    for _ in range(B):
        pick = rng.choice(ids, len(ids)); bs = pd.concat([byid[i] for i in pick])
        a, b = bs[bs[flag]].abs_log10_ratio, bs[~bs[flag]].abs_log10_ratio
        if len(a) and len(b): out.append(a.median() - b.median())
    return tuple(np.percentile(out, [2.5, 97.5])) if len(out) > 100 else (np.nan, np.nan)
for flag, lab in (("undated", "undated vs dated"), ("low_quality", "quality score < 3 vs >= 3"), ("small", "fewer than 10 values vs 10 or more")):
    a, b = pp[pp[flag]], pp[~pp[flag]]
    row = dict(contrast=lab, pairs_flag=len(a), pairs_other=len(b), studies_flag=int(a.record_id.nunique()), studies_other=int(b.record_id.nunique()))
    if len(a) >= 5 and len(b) >= 5:
        mw = stats.mannwhitneyu(a.abs_log10_ratio, b.abs_log10_ratio, alternative="greater"); lo_, hi_ = clustered_diff(pp, flag)
        row.update(dict(median_abs_log10_flag=round(float(a.abs_log10_ratio.median()), 3), median_abs_log10_other=round(float(b.abs_log10_ratio.median()), 3),
                        factor_flag=round(float(10 ** a.abs_log10_ratio.median()), 2), factor_other=round(float(10 ** b.abs_log10_ratio.median()), 2),
                        diff=round(float(a.abs_log10_ratio.median() - b.abs_log10_ratio.median()), 3), diff_lo=round(lo_, 3), diff_hi=round(hi_, 3),
                        mannwhitney_p_one_sided=mw.pvalue,
                        auc=round(float(mw.statistic / (len(a) * len(b))), 3)))
    h7.append(row)
dated = pp[~pp.undated & pp.year_gap.notna()]
if len(dated) >= 8:
    rho, prho = stats.spearmanr(dated.year_gap, dated.abs_log10_ratio); KEY["H7_spearman_gap"] = dict(n=len(dated), rho=float(rho), p=float(prho))
h7 = pd.DataFrame(h7); h7.to_csv(os.path.join(OUT, "v18_H7_disagreement.csv"), index=False); print(h7.to_string()); KEY["H7"] = h7.to_dict("records")
# confound check among the contrasts
KEY["H7_undated_and_lowq"] = int((pp.undated & pp.low_quality).sum())

# ================================================================== H8 monitoring-gap table (lake x year x parameter family)
fam = {"DO": "DO", "BOD": "BOD", "COD": "COD", "total_coliform_MPN": "coliform", "faecal_coliform_MPN": "coliform", "total_coliform_CFU": "coliform", "E_coli_or_EC_MPN": "coliform",
       "nitrate_N": "nutrients", "nitrite_N": "nutrients", "ammoniacal_N": "nutrients", "phosphate_P": "nutrients", "phosphate": "nutrients", "orthophosphate": "nutrients",
       "phosphate_unspecified_basis": "nutrients", "orthophosphate_unspecified_basis": "nutrients", "TKN": "nutrients", "nitrate_plus_nitrite_N": "nutrients", "nitrate_plus_nitrite": "nutrients", "nitrate_unspecified_basis": "nutrients", "ammonium": "nutrients", "free_ammonia_N": "nutrients",
       "lead": "metals", "zinc": "metals", "copper": "metals", "iron": "metals", "cadmium": "metals", "manganese": "metals", "nickel": "metals", "chromium_total": "metals", "mercury": "metals"}
a_ = d[d.parameter_std.isin(fam) & d.year.notna() & ~d.lake_key.fillna("").str.contains("group|combined", case=False)].copy()
a_["family"] = a_.parameter_std.map(fam); a_["yr"] = a_.year.astype(int)
a_ = a_[~((a_.record_id == "CPCB") & a_.statistic.isin(["sd"]))]
cov = a_.groupby(["lake_key", "yr", "family"]).agg(values=("value_std", "size"), sources=("record_id", "nunique"), months=("date_start", lambda s: s.dropna().str[:7].nunique())).reset_index()
cov.to_csv(os.path.join(OUT, "v18_H8_lake_year_family_coverage.csv"), index=False)
lakes_all = pd.read_csv(os.path.join(os.path.dirname(SRC), "lakes.csv")); nl = int(lakes_all.shape[0]); KEY["H8_lakes_in_gazetteer"] = nl
yrs = range(2015, 2026)
summ = []
for fm in ("DO", "BOD", "coliform", "nutrients", "metals"):
    row = dict(family=fm)
    for y in yrs: row[str(y)] = int(cov[(cov.family == fm) & (cov.yr == y)].lake_key.nunique())
    summ.append(row)
summ = pd.DataFrame(summ); summ.to_csv(os.path.join(OUT, "v18_H8_lakes_per_year_by_family.csv"), index=False); print(summ.to_string()); KEY["H8_lakes_per_year"] = summ.to_dict("records")
# share of lake-years with >=9 monthly KSPCB values, 2024 and 2025 (2025 data end in November)
mo = d[(d.record_id == "KSPCB") & (d.parameter_std == "DO") & (d.statistic == "single")].copy(); mo["ym"] = mo.date_start.str[:7]; mo["yr"] = mo.ym.str[:4].astype(int)
mm = mo.groupby(["lake_key", "yr"]).ym.nunique().reset_index()
for y in (2024, 2025):
    x = mm[mm.yr == y]; KEY[f"H8_kspcb_lakes_{y}"] = int(len(x)); KEY[f"H8_kspcb_lakes_ge9_{y}"] = int((x.ym >= 9).sum()); KEY[f"H8_kspcb_lakes_all_months_{y}"] = int((x.ym >= (12 if y == 2024 else 11)).sum())
# cells: gazetteer lakes x years 2015-2025 with any DO value
do = cov[(cov.family == "DO") & cov.yr.between(2015, 2025)]
KEY["H8_cells_total"] = nl * 11; KEY["H8_cells_with_DO"] = int(len(do[["lake_key", "yr"]].drop_duplicates()))
yrs_per_lake = do.groupby("lake_key").yr.nunique().reindex(lakes_all.lake_key if "lake_key" in lakes_all else lakes_all.iloc[:, 0]).fillna(0)
KEY["H8_lakes_with_no_DO_2015_2025"] = int((yrs_per_lake == 0).sum()); KEY["H8_lakes_DO_ge3_years"] = int((yrs_per_lake >= 3).sum()); KEY["H8_lakes_DO_ge1_year"] = int((yrs_per_lake >= 1).sum())
# lakes known from the 2011 table only
srcs = d.groupby("lake_key").record_id.agg(lambda s: set(s))
only11 = [lk for lk, s in srcs.items() if s == {"DMG2011"}]; KEY["H8_lakes_only_2011"] = len(only11)
nostudy_kspcb = [lk for lk, s in srcs.items() if "KSPCB" in s and not any(x.startswith("L") for x in s)]; KEY["H8_kspcb_lakes_without_extracted_study"] = len(nostudy_kspcb)
KEY["H8_lakes_with_any_dated_DO_value"] = int(do.lake_key.nunique())
foam = d[d.parameter_std.str.contains("foam|surfact|detergent", case=False, na=False) | d.parameter.fillna("").str.contains("foam|surfact|detergent|MBAS", case=False)]
KEY["H8_foam_rows"] = int(len(foam))
fam_lakes = {fm: int(cov[cov.family == fm].lake_key.nunique()) for fm in ("DO", "BOD", "coliform", "nutrients", "metals")}; KEY["H8_lakes_any_year_by_family"] = fam_lakes

# ------------------------------------------------------------------ Holm over the four new primary tests
prim = []
r = sr[(sr.parameter == "DO (mg/L)") & (sr.scope == "all months")]
if len(r): prim.append(("H4 DO dry vs wet (site-paired Wilcoxon)", float(r.wilcoxon_p.iloc[0])))
r = sr[(sr.parameter == "log10 BOD") & (sr.scope == "all months")]
if len(r): prim.append(("H4 log BOD dry vs wet", float(r.wilcoxon_p.iloc[0])))
if HAS_FULL:
    r = h6[h6.parameter == "COD"]
    if len(r): prim.append(("H6 COD outlet vs inlet", float(r.wilcoxon_p.iloc[0])))
r = h7[h7.contrast.str.startswith("undated")]
if len(r) and "mannwhitney_p_one_sided" in r: prim.append(("H7 undated vs dated disagreement", float(r.mannwhitney_p_one_sided.iloc[0])))
pm = pd.DataFrame(prim, columns=["test", "p_raw"]); pm["p_holm"] = holm(pm.p_raw); pm.to_csv(os.path.join(OUT, "v18_primary_tests_holm.csv"), index=False); print(pm.to_string()); KEY["primary_holm"] = pm.to_dict("records")


def clean(o):
    if isinstance(o, dict): return {str(a): clean(b) for a, b in o.items()}
    if isinstance(o, (list, tuple)): return [clean(x) for x in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if (isinstance(o, float) and math.isnan(o)) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o


json.dump(clean(KEY), open(os.path.join(OUT, "v18_key_numbers.json"), "w"), indent=1)
print("done")

"""RQ3 compliance (CPCB designated-best-use criteria), RQ4 trends, RQ5 consistency. Outputs results/tables, results/figures."""
import pandas as pd, numpy as np, os
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = r"D:\Research-Publishing\13-bengaluru-lakes"; T = R + r"\results\tables"; F = R + r"\results\figures"
d = pd.read_csv(R + r"\data\release\lake_measurements_long.csv", low_memory=False)
d = d[~d.analysis_use.str.startswith("exclude: not a lake")]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
# ---------------------------------------------------------------- compliance, KSPCB monthly
k = d[(d.record_id == "KSPCB") & (d.statistic == "single")].copy()
k["ym"] = k.date_start.str[:7]
w = k.pivot_table(index=["lake_key", "station_code", "ym"], columns="parameter_std", values="value_std", aggfunc="first").reset_index()
def klass(r):
    g = lambda c: r.get(c, np.nan)
    DO, BOD, TC, pH, NH, EC, B = g("DO"), g("BOD"), g("total_coliform_MPN"), g("pH"), g("ammoniacal_N"), g("EC"), g("boron")
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
w["class_computed"] = w.apply(klass, axis=1)
w.to_csv(R + r"\data\release\derived_kspcb_monthly_class.csv", index=False)
sumtab = w.groupby("ym").class_computed.value_counts(normalize=True).unstack(fill_value=0)
sumtab.to_csv(T + r"\t04a_kspcb_class_share_by_month.csv")
bylake = w.groupby("lake_key").agg(months=("ym", "nunique"), pct_DO_lt4=("DO", lambda s: 100 * (s < 4).mean()), pct_BOD_gt3=("BOD", lambda s: 100 * (s > 3).mean()),
                                   pct_TC_gt5000=("total_coliform_MPN", lambda s: 100 * (s > 5000).mean()), pct_pH_out_6p5_8p5=("pH", lambda s: 100 * ((s < 6.5) | (s > 8.5)).mean()),
                                   median_BOD=("BOD", "median"), median_DO=("DO", "median"))
cl = w.groupby("lake_key").class_computed.value_counts(normalize=True).unstack(fill_value=0).add_prefix("share_class_")
bylake = bylake.join(cl).sort_values("pct_DO_lt4", ascending=False); bylake.to_csv(T + r"\t04_kspcb_compliance_by_lake.csv")
allc = w.class_computed.value_counts(normalize=True).rename("share").to_frame(); allc["n_lake_months"] = w.class_computed.value_counts(); allc.to_csv(T + r"\t04b_kspcb_class_share_overall.csv")
# per-parameter exceedance overall
ex = pd.Series({"DO < 4 mg/L (Class C/D floor)": (w.DO < 4).mean(), "DO < 5 mg/L (Class B)": (w.DO < 5).mean(), "BOD > 3 mg/L (Class B/C)": (w.BOD > 3).mean(), "total coliform > 5000 MPN/100 mL (Class C)": (w.total_coliform_MPN > 5000).mean(),
                "pH outside 6.5-8.5": ((w.pH < 6.5) | (w.pH > 8.5)).mean(), "free ammonia proxy (ammoniacal-N) > 1.2 mg/L": (w.ammoniacal_N > 1.2).mean() if "ammoniacal_N" in w else np.nan}); ex.to_csv(T + r"\t04c_kspcb_exceedance_overall.csv", header=["share_of_lake_months"])
# figure: class shares by month
order = ["A", "B", "C", "D", "E", "below E", "unclassified"]; cols = ["#1a9850", "#66bd63", "#d9ef8b", "#fee08b", "#fdae61", "#d73027", "#bdbdbd"]
fig, ax = plt.subplots(figsize=(10, 4)); bt = np.zeros(len(sumtab))
for c_, col in zip(order, cols):
    if c_ in sumtab: ax.bar(sumtab.index, sumtab[c_] * 100, bottom=bt * 100, color=col, label=c_); bt += sumtab[c_].values
ax.set_xticks(range(0, len(sumtab), 2)); ax.set_xticklabels(sumtab.index[::2], rotation=90); ax.set_ylabel("Share of monitored lakes (%)"); ax.set_xlabel("Month")
ax.set_title("KSPCB monthly lake monitoring: best CPCB designated-use class met per lake-month (computed from DO, BOD, coliform, pH, NH3, EC, boron)", fontsize=9); ax.legend(ncol=7, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.32))
fig.tight_layout(); fig.savefig(F + r"\fig06_kspcb_class_by_month.png", dpi=220); plt.close(fig)
# ---------------------------------------------------------------- compliance, CPCB annual min/max
c = d[(d.record_id == "CPCB") & d.statistic.isin(["min", "max"])].copy()
cw = c.pivot_table(index=["lake_key", "station_code", "year"], columns=["parameter_std", "statistic"], values="value_std", aggfunc="first")
cw.columns = [f"{a}_{b}" for a, b in cw.columns]; cw = cw.reset_index()
def verdict(lo, hi, f_pass_lo, f_pass_hi):
    pass
cw["DO_status"] = np.where(cw.DO_min >= 4, "always meets DO>4", np.where(cw.DO_max < 4, "never meets DO>4", "straddles"))
cw["BOD_status"] = np.where(cw.BOD_max <= 3, "always meets BOD<3", np.where(cw.BOD_min > 3, "never meets BOD<3", "straddles"))
cw["TC_status"] = np.where(cw.total_coliform_MPN_max <= 5000, "always meets TC<5000", np.where(cw.total_coliform_MPN_min > 5000, "never meets TC<5000", "straddles"))
cw.to_csv(R + r"\data\release\derived_cpcb_annual_wide.csv", index=False)
cs = cw.groupby("year")[["DO_status", "BOD_status", "TC_status"]].agg(lambda s: s.value_counts().to_dict()); cs.to_csv(T + r"\t05_cpcb_status_counts_by_year.csv")
for col in ("DO_status", "BOD_status", "TC_status"): print(cw.groupby("year")[col].value_counts().unstack(fill_value=0).to_string())
# ---------------------------------------------------------------- trends
def mk(y, x):
    if len(y) < 5 or len(set(x)) < 5: return None
    tau, p = stats.kendalltau(x, y); ts = stats.theilslopes(y, x)
    return dict(n=len(y), tau=tau, p=p, slope=ts[0], lo=ts[2], hi=ts[3])
res = []
# CPCB annual extremes, stations with >=7 years
for (lk, stn), g in cw.groupby(["lake_key", "station_code"]):
    for name, col, tr in (("annual max BOD (mg/L)", "BOD_max", lambda x: x), ("annual min DO (mg/L)", "DO_min", lambda x: x), ("annual max faecal coliform (log10 MPN/100mL)", "faecal_coliform_MPN_max", np.log10), ("annual max total coliform (log10)", "total_coliform_MPN_max", np.log10)):
        gg = g.dropna(subset=[col]); gg = gg[gg[col] > 0] if "coliform" in col else gg
        if gg.year.nunique() >= 7 and gg.year.max() - gg.year.min() >= 8:
            r = mk(tr(gg[col].values), gg.year.values)
            if r: res.append(dict(source="CPCB annual", lake=lk, station=int(stn), series=name, years=f"{int(gg.year.min())}-{int(gg.year.max())}", **r))
# KSPCB monthly (exploratory; ~27 months)
w["t"] = pd.to_datetime(w.ym + "-01"); w["tnum"] = (w.t.dt.year - 2023) * 12 + w.t.dt.month
for (lk, stn), g in w.groupby(["lake_key", "station_code"]):
    for name, col, tr in (("monthly BOD (mg/L)", "BOD", lambda x: x), ("monthly DO (mg/L)", "DO", lambda x: x)):
        gg = g.dropna(subset=[col])
        if len(gg) >= 18:
            tau, p = stats.kendalltau(gg.tnum, tr(gg[col])); ts = stats.theilslopes(tr(gg[col]), gg.tnum)
            res.append(dict(source="KSPCB monthly (2023-07..2025-11; short window, exploratory)", lake=lk, station=int(stn), series=name, years=f"{gg.ym.min()}..{gg.ym.max()}", n=len(gg), tau=tau, p=p, slope=ts[0] * 12, lo=ts[2] * 12, hi=ts[3] * 12))
tr_ = pd.DataFrame(res)
# Holm within source
def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, j in enumerate(o): run = max(run, (m - i) * p[j]); adj[j] = min(1, run)
    return adj
tr_["p_holm"] = np.nan
for s_, idx in tr_.groupby(["source", "series"]).groups.items(): tr_.loc[idx, "p_holm"] = holm(tr_.loc[idx, "p"].values)
tr_.to_csv(T + r"\t06_trend_tests.csv", index=False)
print(tr_.groupby(["source", "series"]).agg(n_series=("tau", "size"), n_sig_raw=("p", lambda s: int((s < 0.05).sum())), n_sig_holm=("p_holm", lambda s: int((s < 0.05).sum())), median_tau=("tau", "median")).to_string())
# balanced panel: stations present every year 2016-2024
yrs = range(2016, 2025); pan = cw.groupby("station_code").year.apply(lambda s: set(yrs) <= set(s)); ps = pan[pan].index
bp = cw[cw.station_code.isin(ps) & cw.year.between(2016, 2024)].groupby("year")[["BOD_max", "DO_min", "faecal_coliform_MPN_max"]].median()
bp["n_stations"] = len(ps); bp.to_csv(T + r"\t07_cpcb_balanced_panel_medians.csv")
fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
for a_, col, lab in zip(axs, ["BOD_max", "DO_min", "faecal_coliform_MPN_max"], ["Median of annual max BOD (mg/L)", "Median of annual min DO (mg/L)", "Median of annual max faecal coliform (MPN/100 mL)"]):
    a_.plot(bp.index, bp[col], marker="o"); a_.set_xlabel("Year"); a_.set_ylabel(lab, fontsize=8)
    if "coliform" in col: a_.set_yscale("log")
    a_.axvspan(2015, 2017, color="orange", alpha=0.15)
fig.suptitle(f"CPCB NWMP balanced panel: {len(ps)} Bengaluru lake stations reporting in every year 2016-2024 (orange = 2015-17 foaming/fire episodes)", fontsize=9); fig.tight_layout(); fig.savefig(F + r"\fig07_cpcb_balanced_panel.png", dpi=220); plt.close(fig)
# Ulsoor pre/post 2017 (CPCB primary: 2013, 2014 mean; 2016-2024 midrange of min/max -> use max BOD, min DO)
ul = d[(d.record_id == "CPCB") & (d.lake_key == "ulsoor") & (d.station_code == 1388)]
u = ul.pivot_table(index="year", columns=["parameter_std", "statistic"], values="value_std", aggfunc="first"); u.columns = [f"{a}_{b}" for a, b in u.columns]
u.to_csv(T + r"\t08_ulsoor_1388_cpcb_series.csv")
pre = u.loc[[y for y in u.index if y <= 2016]]; post = u.loc[[y for y in u.index if y >= 2018]]
out = []
for col in ("BOD_max", "DO_min", "faecal_coliform_MPN_max"):
    a, b = pre[col].dropna(), post[col].dropna()
    if len(a) >= 3 and len(b) >= 3:
        mw = stats.mannwhitneyu(a, b); out.append(dict(series=col, n_pre=len(a), n_post=len(b), median_pre=a.median(), median_post=b.median(), U=mw.statistic, p=mw.pvalue))
pd.DataFrame(out).to_csv(T + r"\t08b_ulsoor_pre_post_2017.csv", index=False); print(pd.DataFrame(out).to_string())
# ---------------------------------------------------------------- Hebbal cross-source figure (BOD, DO)
hb = d[d.lake_key == "hebbal"].copy()
# sized for print at the paper's text width (6.5 in); title on three lines, one legend under the panels; all text >= 8 pt
fig, axs = plt.subplots(1, 2, figsize=(6.5, 3.85))
for a_, par, lab in zip(axs, ["BOD", "DO"], ["BOD (mg/L)", "DO (mg/L)"]):
    x1 = hb[(hb.record_id == "L147") & (hb.parameter_std == par) & (hb.statistic == "single")]; x1 = x1.assign(t=pd.to_datetime(x1.date_start))
    a_.scatter(x1.t, x1.value_std, s=6, color="#9ecae1", label="L147 (thesis): 8 stations x 12 months, 2013")
    kk = hb[(hb.record_id == "KSPCB") & (hb.parameter_std == par)]; kk = kk.assign(t=pd.to_datetime(kk.date_start)); a_.plot(kk.t, kk.value_std, "o-", color="#08519c", ms=2.5, lw=1.2, label="KSPCB monthly (station 3625)")
    cc = hb[(hb.record_id == "CPCB") & (hb.parameter_std == par) & hb.statistic.isin(["min", "max"]) & (hb.station_code == 3627) | ((hb.record_id == "CPCB") & (hb.parameter_std == par) & hb.statistic.isin(["min", "max"]) & (hb.station_code == 3625))]
    for yr, g in cc.groupby("year"):
        a_.plot([pd.Timestamp(f"{int(yr)}-07-01")] * 2, [g[g.statistic == "min"].value_std.min(), g[g.statistic == "max"].value_std.max()], color="#d94801", lw=2.5, alpha=0.7, label="CPCB annual min-max" if yr == cc.year.min() else None)
    a_.axhline(3 if par == "BOD" else 4, ls="--", color="grey", lw=0.8); a_.set_ylabel(lab); a_.set_xlabel("Date")
    a_.tick_params(labelsize=8.5)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0.0))
fig.suptitle("Hebbal Lake (Bengaluru): three compilations of BOD and DO\n(CPCB 2023-24 annual ranges are derived from the KSPCB monthly data)\n(dashed = CPCB criterion BOD 3, DO 4)", fontsize=9)
fig.tight_layout(rect=(0, 0.11, 1, 1)); fig.savefig(F + r"\fig08_hebbal_cross_source.png", dpi=300); plt.close(fig)
# ---------------------------------------------------------------- consistency: KSPCB monthly values inside CPCB annual range, same station, 2023-24
inside = []
for yr in (2023, 2024):
    kk = k[(k.year == yr)]; cc = cw[cw.year == yr].set_index("station_code")
    for par, lo, hi in (("DO", "DO_min", "DO_max"), ("BOD", "BOD_min", "BOD_max"), ("pH", "pH_min", "pH_max"), ("EC", "EC_min", "EC_max")):
        kp = kk[kk.parameter_std == par]
        for stn, g in kp.groupby("station_code"):
            if stn in cc.index and not pd.isna(cc.loc[stn, lo]) and not pd.isna(cc.loc[stn, hi]):
                vv = g.value_std.dropna(); inside += [dict(year=yr, parameter=par, station=stn, n=len(vv), n_inside=int(((vv >= cc.loc[stn, lo] - 1e-9) & (vv <= cc.loc[stn, hi] + 1e-9)).sum()))]
ins = pd.DataFrame(inside)
cons = ins.groupby(["year", "parameter"]).agg(stations=("station", "nunique"), values=("n", "sum"), inside=("n_inside", "sum")); cons["share_inside_CPCB_annual_range"] = cons.inside / cons["values"]; cons.to_csv(T + r"\t10_consistency_kspcb_in_cpcb_range.csv"); print(cons.to_string())
# literature vs official spread for BOD/DO
sel = d[(d.parameter_std.isin(["BOD", "DO"])) & d.lake_key.isin(["bellandur", "varthur", "hebbal", "ulsoor", "madiwala", "jakkur", "sankey", "yelahanka", "lalbagh"]) & d.statistic.isin(["single", "mean", "min", "max"])]
sp = sel.groupby(["lake_key", "parameter_std", "record_id"]).value_std.agg(["count", "min", "median", "max"]).reset_index(); sp.to_csv(T + r"\t11_source_spread_BOD_DO.csv", index=False)
print("done")

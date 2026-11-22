"""v18 figures: Fig. 3 (four panels, no title inside) and Fig. S1 (balanced panel, no title) for the Water Resources Management submission.
Usage: python -X utf8 -I code/v18_figures.py <lake_measurements_long.csv> <results/v18 dir> <output dir>
"""
import sys, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC, RES, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
C = dict(blue="#0072B2", orange="#D55E00", grey="#7f7f7f", green="#009E73", light="#9ecae1")
d = pd.read_csv(SRC, low_memory=False)
d = d[~d.analysis_use.fillna("").str.startswith("exclude: not a lake")]
k = d[(d.record_id == "KSPCB") & (d.statistic == "single")].copy(); k["ym"] = k.date_start.str[:7]
w = k.pivot_table(index=["lake_key", "station_code", "ym"], columns="parameter_std", values="value_std", aggfunc="first").reset_index()
w["year"] = w.ym.str[:4].astype(int); w["month"] = w.ym.str[5:7].astype(int); w["dry"] = w.month.between(1, 5)
w["site"] = w.lake_key + "_" + w.station_code.astype(int).astype(str)

fig, ax = plt.subplots(2, 2, figsize=(174 / 25.4, 140 / 25.4))
# (a) BOD whole-number histogram
a = ax[0, 0]; b = w.BOD.dropna(); bins = np.arange(0.5, 21.5, 1.0)
a.bar(np.arange(1, 21), [((b >= x - 0.5) & (b < x + 0.5)).sum() for x in np.arange(1, 21)], width=0.8, color=C["blue"])
a.axvline(3.5, color=C["orange"], lw=1); a.text(3.7, 505, "limit 3 mg/L", ha="left", va="top", color=C["orange"], fontsize=8)
a.annotate("no value below 3.2", xy=(2.2, 0), xytext=(5.5, 330), arrowprops=dict(arrowstyle="->", color=C["grey"]), fontsize=8, color="black")
a.set_xlabel("KSPCB BOD, rounded to whole mg/L"); a.set_ylabel("Lake-months"); a.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19]); a.text(-0.2, 1.05, "a", transform=a.transAxes, fontweight="bold", fontsize=11)
# (b) containment
h1 = pd.read_csv(os.path.join(RES, "v18_H1_independence.csv")); lab = [f"{r.parameter}\n{r.year}" for r in h1.itertuples()]; x = np.arange(len(h1)); wd = 0.2
bb = ax[0, 1]
bb.bar(x - 1.5 * wd, h1.share_inside * 100, wd, color=C["blue"], label="Same station and year")
bb.bar(x - 0.5 * wd, h1.null_other_station_same_year * 100, wd, color=C["light"], label="Other station, same year")
bb.bar(x + 0.5 * wd, h1.null_same_station_2016_2022 * 100, wd, color="#c7c7c7", label="Same station, 2016-2022")
bb.bar(x + 1.5 * wd, h1.perm_null_mean * 100, wd, color="#e8b88f", label="Station labels shuffled")
bb.set_xticks(x); bb.set_xticklabels(lab); bb.set_ylim(50, 140); bb.set_yticks([50, 60, 70, 80, 90, 100]); bb.set_ylabel("Inside CPCB range (%)"); bb.legend(frameon=False, fontsize=6.5, loc="upper left", ncol=1, bbox_to_anchor=(0.02, 1.02)); bb.text(-0.14, 1.05, "b", transform=bb.transAxes, fontweight="bold", fontsize=11)
# (c) dry minus wet DO per site
c = ax[1, 0]; data = []; labs = []
for lab_, m in (("All months", w.year > 0), ("2024", w.year == 2024), ("2025", w.year == 2025)):
    s = w[m & w.DO.notna()]; g = s.groupby(["site", "dry"]).DO.agg(["median", "size"]).unstack()
    ok = g[("size", True)].ge(2) & g[("size", False)].ge(2); diff = (g[("median", True)] - g[("median", False)])[ok].dropna(); data.append(diff.values); labs.append(f"{lab_}\n(n = {len(diff)})")
bp = c.boxplot(data, tick_labels=labs, showfliers=False, patch_artist=True, widths=0.5, medianprops=dict(color="black"))
for p_ in bp["boxes"]: p_.set_facecolor(C["light"])
c.axhline(0, color=C["grey"], lw=0.8, ls="--"); c.set_ylabel("DO, dry minus wet (mg/L)"); c.text(-0.22, 1.05, "c", transform=c.transAxes, fontweight="bold", fontsize=11)
# (d) ICC
dd = ax[1, 1]; ic = pd.read_csv(os.path.join(RES, "v18_H5_variance_decomposition.csv")).iloc[::-1]
nm = {"DO": "DO", "log10 BOD": "BOD", "log10 total coliform": "Total coliform", "pH": "pH", "log10 conductivity": "Conductivity", "CPCB 2016-22 annual max BOD (log10)": "BOD, CPCB annual max", "CPCB 2016-22 annual min DO": "DO, CPCB annual min"}
y = np.arange(len(ic)); dd.errorbar(ic.ICC_site, y, xerr=[ic.ICC_site - ic.ICC_lo, ic.ICC_hi - ic.ICC_site], fmt="o", color=C["blue"], capsize=2)
dd.set_yticks(y); dd.set_yticklabels([nm.get(p_, p_) for p_ in ic.parameter]); dd.set_xlim(0, 0.7); dd.set_xlabel("Share of variance between sites (ICC)"); dd.axvline(0.5, color=C["grey"], lw=0.8, ls=":"); dd.text(-0.75, 1.05, "d", transform=dd.transAxes, fontweight="bold", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "Fig3_self_confirmation.png"), dpi=300); plt.close(fig)

# Fig. S1 balanced panel, no title
c_ = d[(d.record_id == "CPCB") & d.statistic.isin(["min", "max"])]
cw = c_.pivot_table(index=["station_code", "year"], columns=["parameter_std", "statistic"], values="value_std", aggfunc="first"); cw.columns = [f"{p}_{s}" for p, s in cw.columns]; cw = cw.reset_index()
yrs = set(range(2016, 2025)); ps = [s for s, g in cw.groupby("station_code") if yrs <= set(g.year)]
bpn = cw[cw.station_code.isin(ps) & cw.year.between(2016, 2024)].groupby("year")[["BOD_max", "DO_min", "faecal_coliform_MPN_max"]].median()
f2, axs = plt.subplots(1, 3, figsize=(174 / 25.4, 55 / 25.4))
for a_, col, lb in zip(axs, ["BOD_max", "DO_min", "faecal_coliform_MPN_max"], ["Median annual max BOD (mg/L)", "Median annual min DO (mg/L)", "Median annual max faecal\ncoliform (MPN/100 mL)"]):
    a_.plot(bpn.index, bpn[col], marker="o", color=C["blue"]); a_.set_xlabel("Year"); a_.set_ylabel(lb, fontsize=8)
    if "coliform" in col: a_.set_yscale("log")
    a_.axvspan(2015, 2017, color="orange", alpha=0.15); a_.set_xticks([2016, 2018, 2020, 2022, 2024])
f2.tight_layout(); f2.savefig(os.path.join(OUT, "FigS1_balanced_panel.png"), dpi=300); plt.close(f2); print(len(ps), "balanced stations")

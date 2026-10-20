"""Coverage tables and figures (RQ1) + lake map. Outputs to results/tables and results/figures."""
import pandas as pd, numpy as np, re, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = r"D:\Research-Publishing\13-bengaluru-lakes"
T = R + r"\results\tables"; F = R + r"\results\figures"; os.makedirs(T, exist_ok=True); os.makedirs(F, exist_ok=True)
d = pd.read_csv(R + r"\data\release\lake_measurements_long.csv", low_memory=False)
st = pd.read_csv(R + r"\data\release\studies.csv"); L = pd.read_csv(R + r"\data\release\lakes.csv")
log = pd.read_csv(R + r"\data\release\screening_log.csv")
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100})
lake_scope = d[~d.analysis_use.str.startswith("exclude: not a lake")].copy()
lake_scope = lake_scope[~lake_scope.lake_key.str.contains("pooled| and ", na=False)]
CORE = ["DO", "BOD", "COD", "pH", "EC", "TDS", "temperature", "turbidity", "nitrate_N", "nitrate_unspecified_basis", "nitrite_N", "nitrate_plus_nitrite_N", "ammoniacal_N", "phosphate_P", "phosphate_unspecified_basis",
        "total_coliform_MPN", "total_coliform_CFU", "faecal_coliform_MPN", "faecal_coliform_CFU", "lead", "cadmium", "chromium", "chromium_total", "copper", "zinc", "nickel", "iron", "manganese", "mercury", "arsenic"]
# ---------------- T1 studies
g = lake_scope[lake_scope.source_type == "literature"].groupby("record_id")
t1 = st.set_index("record_id").join(pd.DataFrame({"n_rows": g.size(), "n_lakes": g.lake_key.nunique(), "lakes": g.lake_key.agg(lambda s: ", ".join(sorted(set(s)))), "n_parameters": g.parameter_std.nunique(),
                                                  "first_year": g.year.min(), "last_year": g.year.max(), "undated_rows": g.year.agg(lambda s: int(s.isna().sum()))}))
t1.to_csv(T + r"\t01_studies_included.csv")
# ---------------- T3 parameter coverage
pc = lake_scope.groupby(["source_type", "parameter_std"]).agg(rows=("row_id", "size"), sources=("record_id", "nunique"), lakes=("lake_key", "nunique")).reset_index()
pc.to_csv(T + r"\t03_parameter_coverage.csv", index=False)
fam = {"DO/BOD/COD": ["DO", "BOD", "COD"], "nutrients (N, P)": ["nitrate_N", "nitrate_unspecified_basis", "nitrite_N", "nitrate_plus_nitrite_N", "ammoniacal_N", "TKN", "phosphate_P", "phosphate_unspecified_basis", "orthophosphate_unspecified_basis"],
       "coliforms": ["total_coliform_MPN", "total_coliform_CFU", "faecal_coliform_MPN", "faecal_coliform_CFU", "faecal_streptococci"], "heavy metals": ["lead", "cadmium", "chromium", "chromium_total", "copper", "zinc", "nickel", "iron", "manganese", "mercury", "arsenic", "cobalt"],
       "pH/EC/TDS/temp/turbidity": ["pH", "EC", "TDS", "temperature", "turbidity", "TSS"], "ions/hardness/alkalinity": ["chloride", "sulphate", "fluoride", "total_hardness", "total_alkalinity", "calcium", "magnesium", "sodium", "potassium", "bicarbonate", "carbonate"]}
p2f = {p: f for f, ps in fam.items() for p in ps}
lake_scope["family"] = lake_scope.parameter_std.map(p2f).fillna("other")
fam_tab = lake_scope.groupby(["family", "source_type"]).agg(rows=("row_id", "size"), lakes=("lake_key", "nunique"), sources=("record_id", "nunique")).reset_index()
fam_tab.to_csv(T + r"\t03b_parameter_family_coverage.csv", index=False)
# ---------------- coverage lake x year (distinct sources overlapping that year)
def years_of(r):
    a = pd.to_datetime(r.date_start, errors="coerce"); b = pd.to_datetime(r.date_end, errors="coerce")
    if pd.isna(a): return []
    return list(range(a.year, (b.year if not pd.isna(b) else a.year) + 1))
u = lake_scope.drop_duplicates(["record_id", "lake_key", "date_start", "date_end"]).copy()
u["yrs"] = u.apply(years_of, axis=1); u = u.explode("yrs").dropna(subset=["yrs"]); u["yrs"] = u.yrs.astype(int)
cov = u.groupby(["lake_key", "yrs"]).record_id.nunique().unstack(fill_value=0)
cov = cov.reindex(columns=range(1996, 2027), fill_value=0)
cov.to_csv(T + r"\t02_coverage_lake_by_year_nsources.csv")
top = cov.sum(axis=1).sort_values(ascending=False).head(30).index
fig, ax = plt.subplots(figsize=(11, 7))
M = cov.loc[top, 2004:2026] if False else cov.loc[top, [c for c in cov.columns if c >= 2000]]
im = ax.imshow(M.values, aspect="auto", cmap="YlGnBu", vmin=0, vmax=max(3, M.values.max()))
ax.set_yticks(range(len(top))); ax.set_yticklabels([k.title() for k in top]); ax.set_xticks(range(0, M.shape[1], 2)); ax.set_xticklabels(M.columns[::2], rotation=90)
ax.set_xlabel("Year (measurement period overlaps year)"); ax.set_ylabel("Lake (30 with most source-years)")
ax.set_title("Evidence coverage: number of distinct sources reporting measurements, by lake and year (2000-2026)")
cb = fig.colorbar(im, ax=ax, shrink=0.7); cb.set_label("distinct sources (published studies + KSPCB + CPCB)")
fig.tight_layout(); fig.savefig(F + r"\fig02_coverage_lake_year.png", dpi=220); plt.close(fig)
# ---------------- parameter family x year
uu = lake_scope.copy(); uu["yr"] = uu.date_start.map(lambda s: pd.to_datetime(s, errors="coerce").year)
fy = uu[uu.yr.notna()].groupby(["family", "yr"]).agg(sources=("record_id", "nunique")).reset_index()
pv = fy.pivot(index="family", columns="yr", values="sources").reindex(columns=range(2000, 2027)).fillna(0)
fig, ax = plt.subplots(figsize=(10, 3.6)); im = ax.imshow(pv.values, aspect="auto", cmap="YlOrBr", vmin=0)
ax.set_yticks(range(len(pv))); ax.set_yticklabels(pv.index); ax.set_xticks(range(0, 27, 2)); ax.set_xticklabels(range(2000, 2027, 2), rotation=90); ax.set_xlabel("Year"); ax.set_title("Parameter families by year: number of distinct sources")
fig.colorbar(im, ax=ax, label="sources"); fig.tight_layout(); fig.savefig(F + r"\fig03_parameter_family_year.png", dpi=220); plt.close(fig)
# ---------------- literature output by year (candidates vs extracted)
cand = log[log.stage1_decision == "retain for full-text check"].copy(); cand["year"] = pd.to_numeric(cand.year, errors="coerce")
ext_ids = cand[cand.stage2_status == "included - extracted to dataset"]
yrs = range(1985, 2027)
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.bar(list(yrs), [int((cand.year == y).sum()) for y in yrs], color="#9ecae1", label="records retained at title/abstract screening (n=%d)" % len(cand))
ax.bar(list(yrs), [int((ext_ids.year == y).sum()) for y in yrs], color="#08519c", label="extracted into dataset (n=%d)" % len(ext_ids))
ax.set_xlabel("Publication year"); ax.set_ylabel("Records"); ax.set_title("Bengaluru lake water-quality literature by year"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(F + r"\fig04_literature_by_year.png", dpi=220); plt.close(fig)
# ---------------- foaming mentions
pool = pd.read_csv(R + r"\data\clean\screen-pool.csv"); pool = pool[pool.key.isin(cand.key)]
txt = (pool.title.fillna("") + " " + pool.abstract.fillna("")).str.lower()
foam = pool[txt.str.contains(r"foam|froth|surfactant|fire\b|caught fire|burning")].copy()
foam[["year", "title", "doi", "venue"]].sort_values("year").to_csv(T + r"\t09_foam_fire_papers.csv", index=False)
# ---------------- MAP (static, no tiles)
LL = L.dropna(subset=["lat", "lon"]).copy()
LL["mentions"] = LL.n_candidate_papers_mentioning
fig, ax = plt.subplots(figsize=(8.6, 8))
has_off = (LL.kspcb_months > 0) | (LL.cpcb_years > 0)
ax.scatter(LL[~has_off].lon, LL[~has_off].lat, s=18 + 14 * LL[~has_off].mentions, c="#bdbdbd", edgecolor="k", lw=0.4, label="no official series in dataset")
sc = ax.scatter(LL[has_off].lon, LL[has_off].lat, s=18 + 14 * LL[has_off].mentions, c=LL[has_off].n_studies_extracted, cmap="viridis", edgecolor="k", lw=0.4, vmin=0, vmax=max(4, LL.n_studies_extracted.max()), label="KSPCB/CPCB series available")
cb = fig.colorbar(sc, ax=ax, shrink=0.6); cb.set_label("published studies extracted into dataset (per lake)")
for _, r in LL[LL.mentions >= 6].iterrows(): ax.annotate(r.lake_key.title() + f" ({int(r.mentions)})", (r.lon, r.lat), xytext=(4, 4), textcoords="offset points", fontsize=8)
ax.set_xlabel("Longitude (deg E)"); ax.set_ylabel("Latitude (deg N)"); ax.set_aspect(1 / np.cos(np.deg2rad(13.0)))
ax.set_title("Bengaluru lakes in the evidence base (OSM coordinates)\nmarker size = candidate papers mentioning the lake in title/abstract; labels show that count", fontsize=10)
ax.legend(loc="lower left", frameon=False, fontsize=8); ax.grid(alpha=0.2)
ax.text(0.99, 0.01, "Coordinates (c) OpenStreetMap contributors, ODbL", transform=ax.transAxes, ha="right", fontsize=7)
fig.tight_layout(); fig.savefig(F + r"\fig05_map_lakes_study_counts.png", dpi=220); fig.savefig(F + r"\fig05_map_lakes_study_counts.svg"); plt.close(fig)
# interactive HTML map
try:
    import plotly.graph_objects as go
    LL["hover"] = LL.apply(lambda r: f"{r.lake_key.title()}<br>candidate papers: {int(r.mentions)}<br>studies extracted: {int(r.n_studies_extracted)}<br>KSPCB months: {int(r.kspcb_months)}; CPCB years: {int(r.cpcb_years)}<br>coords: {r.coord_source} ({r.coord_confidence})", axis=1)
    fig = go.Figure(go.Scattermap(lat=LL.lat, lon=LL.lon, mode="markers", marker=dict(size=np.clip(6 + 1.2 * LL.mentions, 6, 40), color=LL.n_studies_extracted, colorscale="Viridis", showscale=True, colorbar=dict(title="studies extracted")), text=LL.hover, hoverinfo="text"))
    fig.update_layout(map=dict(style="open-street-map", center=dict(lat=12.98, lon=77.6), zoom=9.3), margin=dict(l=0, r=0, t=40, b=0), title="Bengaluru lakes: study counts (OSM coordinates; tiles load from OpenStreetMap when opened)")
    fig.write_html(F + r"\fig05_map_lakes_study_counts_interactive.html", include_plotlyjs="cdn")
except Exception as e: print("plotly map failed:", e)
print("coverage done;", len(LL), "mapped lakes")
print(t1[["n_rows", "n_lakes", "first_year", "last_year"]].to_string())

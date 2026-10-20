"""Literature map for the Bengaluru lake water-quality corpus (332 records retained at title/abstract screening).
Outputs: ../data/corpus.csv, ../tables/*.csv, ../figures/*.png (+captions), ../vosviewer/*.txt, ../evidence-table.csv. Python-only (no Bibliometrix: records lack references/affiliations needed for most of its outputs)."""
import pandas as pd, numpy as np, re, os, itertools, collections, math, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = r"D:\Research-Publishing\13-bengaluru-lakes"; B = R + r"\bibliometrics"
for sub in ("data", "tables", "figures", "vosviewer", "python", "pdfs"): os.makedirs(f"{B}\\{sub}", exist_ok=True)
log = pd.read_csv(R + r"\data\release\screening_log.csv"); pool = pd.read_csv(R + r"\data\clean\screen-pool.csv")
dd = pd.read_csv(R + r"\data\clean\records-dedup-flagged.csv")
c = log[log.stage1_decision == "retain for full-text check"].merge(pool[["id", "abstract", "authors", "oa_url", "type", "year"]].rename(columns={"year": "year_pool"}), left_on="pool_id", right_on="id", how="left")
c["year"] = pd.to_numeric(c.year, errors="coerce"); c["text"] = (c.title.fillna("") + ". " + c.abstract.fillna("")).str.lower()
c.drop(columns=["id"]).to_csv(B + r"\data\corpus.csv", index=False)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
# ---- annual production + growth
yr = c.year.dropna().astype(int).value_counts().sort_index(); yr.to_csv(B + r"\tables\annual_production.csv", header=["records"])
cagr = (yr.loc[2010:2025].iloc[-3:].mean() / yr.loc[2010:2025].iloc[:3].mean()) ** (1 / 12) - 1 if len(yr.loc[2010:2025]) > 6 else np.nan
fig, ax = plt.subplots(figsize=(8, 3.3)); ax.bar(yr.index, yr.values, color="#3182bd"); ax.set_xlabel("Publication year"); ax.set_ylabel("Records"); ax.set_title(f"Annual production of retained records (n={len(c)}; first 3 vs last 3 years of 2010-2025 growth {cagr*100:.0f}%/yr)")
fig.tight_layout(); fig.savefig(B + r"\figures\fig_annual_production.png", dpi=220); plt.close(fig)
# ---- sources / Bradford
v = c.venue.fillna("(none)").str.replace(r"\s+", " ", regex=True).str.strip(); vc = v.value_counts(); vc.to_csv(B + r"\tables\venues.csv", header=["records"])
cum = vc.cumsum() / vc.sum(); z1 = int((cum <= 1 / 3).sum() + 1); z2 = int((cum <= 2 / 3).sum() + 1)
fig, ax = plt.subplots(figsize=(8, 3.6)); ax.plot(range(1, len(vc) + 1), cum.values, marker=".", ms=3); ax.set_xscale("log"); ax.set_xlabel("Venue rank (log)"); ax.set_ylabel("Cumulative share of records"); ax.axvline(z1, ls=":", c="grey"); ax.axvline(z2, ls=":", c="grey")
ax.set_title(f"Bradford distribution: {z1} venues hold the first third, {z2} the first two thirds ({len(vc)} venues)"); fig.tight_layout(); fig.savefig(B + r"\figures\fig_bradford.png", dpi=220); plt.close(fig)
# ---- authors (Lotka) from OpenAlex-style 'a; b; c' strings only
au = c.authors.dropna(); names = [x.strip() for s in au for x in re.split(r";|,", s) if len(x.strip()) > 4 and not re.search(r"\d|\.\.\.|-", x)]
ac = collections.Counter(names); a_tab = pd.Series(ac).sort_values(ascending=False); a_tab.head(40).to_csv(B + r"\tables\authors_top40.csv", header=["records"])
lot = pd.Series(ac).value_counts().sort_index(); lot.to_csv(B + r"\tables\lotka_counts.csv", header=["n_authors"])
# ---- term extraction
STOP = set("the of and in a to for on at by with from is are was were as an or this that its be which water quality lake lakes study analysis case bangalore bengaluru india karnataka using used these their than into during between among also can has have been not but it we our two three based assessment evaluation different various city urban results present paper tank tanks".split())
def toks(t): return [w for w in re.findall(r"[a-z][a-z\-]{2,}", t) if w not in STOP]
TERMS = ["eutrophication", "heavy metals", "sewage", "foam", "froth", "water quality index", "phytoplankton", "zooplankton", "fish", "macrophyte", "restoration", "rejuvenation", "idol immersion", "governance", "urbanization", "groundwater", "coliform", "dissolved oxygen", "bod", "nutrient", "nitrate", "phosphate", "remote sensing", "sediment", "microplastic", "treatment wetland", "algal bloom", "surfactant", "pollution", "physico-chemical", "stp", "bellandur", "varthur", "hebbal", "ulsoor", "jakkur", "madiwala", "sankey", "lalbagh", "kengeri", "yelahanka"]
for t_ in TERMS: c["t_" + t_] = c.text.str.contains(r"\b" + re.escape(t_)).astype(int)
tf = c[[f"t_{t_}" for t_ in TERMS]].sum().rename(lambda s: s[2:]).sort_values(ascending=False); tf.to_csv(B + r"\tables\term_frequency.csv", header=["records"])
fig, ax = plt.subplots(figsize=(8, 6)); tf.sort_values().plot.barh(ax=ax, color="#31a354"); ax.set_xlabel("Records mentioning term in title/abstract (n=%d)" % len(c)); ax.set_title("Topic and lake terms in the retained corpus"); fig.tight_layout(); fig.savefig(B + r"\figures\fig_term_frequency.png", dpi=220); plt.close(fig)
# ---- topic x year stacked chart
fam = {"physico-chemical / WQI": ["physico-chemical", "water quality index", "dissolved oxygen", "bod", "nitrate", "phosphate", "nutrient"], "heavy metals": ["heavy metals"], "eutrophication/algae/plankton": ["eutrophication", "phytoplankton", "zooplankton", "algal bloom", "macrophyte"],
       "sewage/foam/pollution": ["sewage", "foam", "froth", "surfactant", "pollution", "coliform"], "restoration/governance": ["restoration", "rejuvenation", "governance", "treatment wetland"], "remote sensing/urbanization": ["remote sensing", "urbanization"]}
ys = range(1995, 2027); M = pd.DataFrame({k: [int(c[(c.year == y)][[f"t_{t_}" for t_ in v_]].max(axis=1).sum()) if (c.year == y).any() else 0 for y in ys] for k, v_ in fam.items()}, index=list(ys))
fig, ax = plt.subplots(figsize=(9, 3.8)); M.plot.bar(stacked=True, ax=ax, width=0.85, colormap="tab10"); ax.set_xticks(range(0, len(ys), 2)); ax.set_xticklabels(list(ys)[::2], rotation=90); ax.set_ylabel("Records (a record can count in several topics)"); ax.set_title("Topic families by year"); ax.legend(fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig(B + r"\figures\fig_topics_by_year_stacked.png", dpi=220); plt.close(fig); M.to_csv(B + r"\tables\topics_by_year.csv")
# ---- co-occurrence network (terms) + VOSviewer files
Tn = [t_ for t_ in TERMS if c["t_" + t_].sum() >= 3]; co = np.zeros((len(Tn), len(Tn)), int)
for _, r in c.iterrows():
    p = [i for i, t_ in enumerate(Tn) if r["t_" + t_]]
    for i, j in itertools.combinations(p, 2): co[i, j] += 1; co[j, i] += 1
open(B + r"\vosviewer\terms_map.txt", "w", encoding="utf-8").write("id\tlabel\tweight<Occurrences>\n" + "\n".join(f"{i+1}\t{t_}\t{int(c['t_'+t_].sum())}" for i, t_ in enumerate(Tn)))
open(B + r"\vosviewer\terms_network.txt", "w", encoding="utf-8").write("\n".join(f"{i+1}\t{j+1}\t{co[i,j]}" for i in range(len(Tn)) for j in range(i + 1, len(Tn)) if co[i, j] > 0))
import networkx as nx
G = nx.Graph(); [G.add_node(t_, w=int(c["t_" + t_].sum())) for t_ in Tn]; [G.add_edge(Tn[i], Tn[j], weight=int(co[i, j])) for i in range(len(Tn)) for j in range(i + 1, len(Tn)) if co[i, j] >= 3]
pos = nx.spring_layout(G, seed=7, k=0.9, weight="weight"); fig, ax = plt.subplots(figsize=(8.5, 7)); nx.draw_networkx_edges(G, pos, width=[0.3 + G[u][v]["weight"] / 12 for u, v in G.edges], alpha=0.35, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=[40 + 12 * G.nodes[n]["w"] for n in G], node_color="#fd8d3c", ax=ax); nx.draw_networkx_labels(G, pos, font_size=7, ax=ax); ax.axis("off"); ax.set_title("Term co-occurrence network (edges: >= 3 shared records; seed fixed 7)")
fig.tight_layout(); fig.savefig(B + r"\figures\fig_term_cooccurrence.png", dpi=220); plt.close(fig)
# ---- publication-type split and OA
c["has_oa_url"] = c.oa_url.notna(); c.groupby(["type"], dropna=False).size().to_csv(B + r"\tables\record_types.csv", header=["records"])
# ---- Kleinberg burst detection (offline, two-state, s=2, gamma=1) on yearly term proportions
def kleinberg(r, d, s=2.0, gamma=1.0):
    n = len(r); R_, D_ = r.sum(), d.sum(); p0 = R_ / D_; p1 = min(0.999, s * p0)
    if p0 == 0: return np.zeros(n, int)
    def cost(p, rt, dt): return -(math.log(math.comb(int(dt), int(rt)) if dt < 1000 else 1) + rt * math.log(p) + (dt - rt) * math.log(1 - p))
    INF = 1e18; C = np.full((n, 2), INF); back = np.zeros((n, 2), int); tau = gamma * math.log(n) if n > 1 else gamma
    for t in range(n):
        for q, p in ((0, p0), (1, p1)):
            ct = cost(p, r[t], d[t])
            if t == 0: C[t, q] = ct + (tau if q == 1 else 0)
            else:
                best = min(((C[t - 1, qq] + (tau if (q == 1 and qq == 0) else 0)), qq) for qq in (0, 1)); C[t, q] = best[0] + ct; back[t, q] = best[1]
    st = np.zeros(n, int); q = int(np.argmin(C[-1]));
    for t in range(n - 1, -1, -1): st[t] = q; q = back[t, q]
    return st
years = np.arange(2000, 2027); d_t = np.array([int((c.year == y).sum()) for y in years]); bursts = []
for t_ in TERMS:
    r_t = np.array([int(c[(c.year == y)]["t_" + t_].sum()) for y in years]);
    if r_t.sum() < 5: continue
    s_ = kleinberg(r_t, d_t)
    if s_.any():
        runs = [(years[i], years[j]) for i, j in [(k, k) for k in range(len(s_)) if s_[k] and (k == 0 or not s_[k - 1])] for j in [i + int(np.argmax(np.append(s_[i:], 0) == 0)) - 1]]
        for a, b in runs: bursts.append(dict(term=t_, burst_start=int(a), burst_end=int(b), records_total=int(r_t.sum())))
bt = pd.DataFrame(bursts); bt.to_csv(B + r"\tables\kleinberg_bursts.csv", index=False)
if len(bt):
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(bt) + 1.5)); bt = bt.sort_values("burst_start")
    for i, r in enumerate(bt.itertuples()): ax.barh(i, r.burst_end - r.burst_start + 1, left=r.burst_start, color="#de2d26")
    ax.set_yticks(range(len(bt))); ax.set_yticklabels(bt.term); ax.set_xlim(2000, 2027); ax.set_xlabel("Year"); ax.set_title("Kleinberg burst detection on yearly term share (2-state, s=2, gamma=1)"); fig.tight_layout(); fig.savefig(B + r"\figures\fig_burst_timeline.png", dpi=220); plt.close(fig)
print("bursts:", len(bt))
# ---- main-path analysis on direct citations among OpenAlex records (references listed in OpenAlex metadata)
oa_ids = {}
raw = pd.read_csv(R + r"\data\raw\records-raw.csv", usecols=["id", "title", "year", "refs", "doi"]); raw = raw[raw.id.notna()].drop_duplicates("id")
tt = set(c.title.str.lower()); raw = raw[raw.title.str.lower().isin(tt)]
idset = set(raw.id); edges = []
for _, r in raw.iterrows():
    for ref in str(r.refs).split("|"):
        if ref in idset and ref != r.id: edges.append((r.id, ref))   # citing -> cited
nxg = nx.DiGraph(edges); print("OpenAlex records in corpus with refs:", len(raw), "citation edges within corpus:", len(edges))
open(B + r"\tables\citation_edges_within_corpus.csv", "w").write("citing,cited\n" + "\n".join(f"{a},{b}" for a, b in edges))
pd.DataFrame({"records_with_openalex_id": [len(raw)], "internal_citation_edges": [len(edges)], "weakly_connected_components": [nx.number_weakly_connected_components(nxg) if len(edges) else 0]}).to_csv(B + r"\tables\citation_network_summary.csv", index=False)
# ---- evidence table
ext = {"L047": 47, "L063": 63, "L068": 68, "L112": 112, "L138": 138, "L147": 147, "L172": 172, "L175": 175, "L207": 207, "L234": 234, "L287": 287, "L291": 291, "L378": 378, "L409": 409, "L421": 421, "L445": 445, "L453": 453, "L462": 462, "L492": 492, "L514": 514}
inv = {v: k for k, v in ext.items()}
def find(abs_):
    if not isinstance(abs_, str) or len(abs_) < 80: return "", "metadata only"
    ss = re.split(r"(?<=[.!?])\s+", abs_.strip()); k = [s for s in ss if re.search(r"ranged|found|revealed|indicat|result|concluded|shows?|exceed", s, re.I)]
    return (k[0] if k else ss[-1])[:300], "abstract read"
rows = []
for _, r in c.iterrows():
    f, lvl = find(r.abstract); rid = inv.get(int(r.pool_id)) if pd.notna(r.pool_id) else None
    prio = (10 if rid else 0) + (3 if str(r.stage2_status).startswith("eligible") else 0) + (2 if r.n_hits >= 3 else 0) + (1 if lvl == "abstract read" else 0)
    rows.append(dict(priority=prio, citation=f"{str(r.authors)[:60]} ({int(r.year) if r.year == r.year else 'n.d.'}) {r.title}", doi=r.doi, link=(f"https://doi.org/{r.doi}" if isinstance(r.doi, str) and r.doi != "nan" else r.venue), open_access_link=r.oa_url if isinstance(r.oa_url, str) else "",
                     study_type=("thesis" if "Shodhganga" in str(r.venue) or "thesis" in str(r.title).lower() else "article/report"), data=("extracted to dataset as " + rid) if rid else "not extracted", method="see dataset flags" if rid else "",
                     main_finding_one_line=f, evidence_level=("full text read; numbers in dataset" if rid else lvl), stage2_status=r.stage2_status, relation_to_paper=("primary data source" if rid else "candidate")))
et = pd.DataFrame(rows).sort_values(["priority", "citation"], ascending=[False, True]).head(60); et.to_csv(B + r"\evidence-table.csv", index=False)
print(len(c), "corpus;", et.shape)

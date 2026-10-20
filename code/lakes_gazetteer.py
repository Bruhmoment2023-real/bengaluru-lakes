"""Build lake gazetteer from KSPCB station codes (STN) + OSM (Overpass, ODbL) coordinates.
Outputs data/clean/lake_gazetteer.csv and data/clean/official_kspcb_long_clean.csv (adds lake_id, lake_canonical, water_body_type)."""
import pandas as pd, re, json, difflib, collections, math, os, sys
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
R = r"D:\Research-Publishing\13-bengaluru-lakes"
d = pd.read_csv(R + r"\data\clean\official_kspcb_long.csv")
def n0(s): return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", str(s).lower())).strip()
d["n"] = d.lake_as_reported.map(n0)
d["stn"] = pd.to_numeric(d.stn, errors="coerce")
# canonical name per STN = most frequent normalised name among rows with that STN
canon = {}
for stn, g in d.dropna(subset=["stn"]).groupby("stn"):
    c = collections.Counter(g.n); best = c.most_common(1)[0][0]
    canon[int(stn)] = best
# short name
CUT = r"\b(bengaluru|bengalore|bangalore|bengaluru|near|vill|village|east|west|north|south|taluka|taluk|road|rd|main|layout|phase|nagr|nagar|itpl|pwd|quarters|sector|st|hsr|bgp|koppa)\b.*$"
def short(n):
    s = re.sub(CUT, "", n).strip()
    s = re.sub(r"\s+", " ", s)
    return s
cs = {k: short(v) for k, v in canon.items()}
def btype(n):
    if re.search(r"\briver\b|dakshina pinakini|arkavathi", n): return "river/reservoir (outside lake scope)"
    return "lake/tank"
# assign stn to rows without stn using fuzzy name match
names = list(set(canon.values()))
def match(n):
    m = difflib.get_close_matches(n, names, n=1, cutoff=0.82)
    return m[0] if m else None
rev = {v: k for k, v in canon.items()}
unres = 0
stn_f = []
for i, r in d.iterrows():
    if pd.notna(r.stn): stn_f.append(int(r.stn)); continue
    m = match(r.n)
    if m: stn_f.append(rev[m])
    else: stn_f.append(-1)
d["stn_filled"] = stn_f
# garbled rows with stn present keep stn (their name is garbled but stn is stable)
d["lake_id"] = d.stn_filled.map(lambda s: f"KSPCB-{s}" if s > 0 else "")
d["lake_canonical"] = d.stn_filled.map(lambda s: cs.get(s, ""))
d["water_body_type"] = d.stn_filled.map(lambda s: btype(canon.get(s, "")))
print("rows", len(d), "unresolved", (d.stn_filled < 0).sum())
d.to_csv(R + r"\data\clean\official_kspcb_long_clean.csv", index=False)
# --- OSM matching
osm = json.load(open(R + r"\data\raw\osm\overpass-water-bengaluru.json", encoding="utf-8"))["elements"]
def lat_lon(e):
    if "center" in e: return e["center"]["lat"], e["center"]["lon"]
    return e.get("lat"), e.get("lon")
def on(s): return re.sub(r"\b(lake|tank|kere|kunte|cheruvu|reservoir|pond|lakes|tanks|dam)\b", "", n0(s)).replace("  ", " ").strip()
OSM = []
for e in osm:
    t = e.get("tags", {}); la, lo = lat_lon(e)
    if la is None: continue
    for nm in {t.get("name"), t.get("name:en")}:
        if nm: OSM.append((on(nm), nm, la, lo, f"{e['type']}/{e['id']}"))
print("osm named features", len(OSM))
rows = []
for stn, nm in sorted(canon.items()):
    s = cs[stn]; key = on(s); best = None; bs = 0
    for k, nm2, la, lo, oid in OSM:
        sc = difflib.SequenceMatcher(None, key, k).ratio()
        if sc > bs: bs, best = sc, (nm2, la, lo, oid)
    rows.append(dict(lake_id=f"KSPCB-{stn}", stn=stn, name_kspcb=s, water_body_type=btype(nm), osm_name=best[0] if best and bs >= 0.8 else "", osm_id=best[3] if best and bs >= 0.8 else "",
                     lat=best[1] if best and bs >= 0.8 else None, lon=best[2] if best and bs >= 0.8 else None, match_score=round(bs, 2)))
g = pd.DataFrame(rows); g.to_csv(R + r"\data\clean\lake_gazetteer_kspcb.csv", index=False)
print(g.lat.notna().sum(), "of", len(g), "matched to OSM at >=0.8")
print(g[g.lat.isna()][["lake_id", "name_kspcb", "match_score"]].to_string())

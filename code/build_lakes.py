"""Lake table: one row per lake_key with coordinates (OSM), source counts and literature counts.
Coordinates: (1) KSPCB-station gazetteer matched to OSM (Overpass/Nominatim, ODbL), (2) Overpass fuzzy name match for literature-only lakes, (3) Nominatim fallback (1.5 s spacing). Low-confidence matches flagged."""
import pandas as pd, numpy as np, re, json, difflib, sys
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
import common
common.INTERVAL["nominatim.openstreetmap.org"] = 1.5
from common import get
from lakekey import lake_key
R = r"D:\Research-Publishing\13-bengaluru-lakes"
d = pd.read_csv(R + r"\data\release\lake_measurements_long.csv", low_memory=False)
g = pd.read_csv(R + r"\data\clean\lake_gazetteer_kspcb.csv"); g["lake_key"] = g.name_kspcb.map(lake_key)
pool = pd.read_csv(R + r"\data\clean\screening-pool-decisions-final.csv")
pool = pool[pool.decision == "full-text check"].merge(pd.read_csv(R + r"\data\clean\screen-pool.csv")[["id", "abstract", "authors"]], on="id", how="left")
# ---------- OSM features
osm = json.load(open(R + r"\data\raw\osm\overpass-water-bengaluru.json", encoding="utf-8"))["elements"]
feat = []
for e in osm:
    t = e.get("tags", {}); c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
    if t.get("name") and c.get("lat"): feat.append((lake_key(t["name"]), t["name"], c["lat"], c["lon"], f"{e['type']}/{e['id']}"))
keys = d[~d.lake_key.str.contains("pooled| and ", na=False)].lake_key.dropna().unique()
rows = []
for k in sorted(keys):
    row = dict(lake_key=k, display_name=k.title())
    gg = g[(g.lake_key == k) & g.lat.notna()]
    if len(gg):
        r = gg.iloc[0]; row.update(lat=r.lat, lon=r.lon, coord_source=r.coord_source, osm_name=r.osm_name, osm_id=r.osm_id, coord_confidence=r.coord_confidence)
    else:
        best = max(feat, key=lambda f: difflib.SequenceMatcher(None, k, f[0]).ratio())
        sc = difflib.SequenceMatcher(None, k, best[0]).ratio()
        if sc >= 0.85: row.update(lat=best[2], lon=best[3], coord_source="OSM-Overpass-name-match", osm_name=best[1], osm_id=best[4], coord_confidence=f"medium (name match score {sc:.2f})")
        else:
            hit = None
            for q in (k + " lake Bengaluru", k + " Bengaluru"):
                s, t = get("https://nominatim.openstreetmap.org/search", {"q": q, "format": "jsonv2", "limit": 3, "viewbox": "77.30,13.35,77.90,12.70", "bounded": 1})
                if s != 200: continue
                for h in json.loads(t):
                    if re.search(r"lake|kere|tank|pond|kunte", h["display_name"].split(",")[0].lower()): hit = h; break
                if hit: break
            if hit: row.update(lat=float(hit["lat"]), lon=float(hit["lon"]), coord_source="OSM-Nominatim", osm_name=hit["display_name"][:80], osm_id=f"{hit['osm_type']}/{hit['osm_id']}", coord_confidence="medium-low (Nominatim top hit whose name is a water feature)")
            else: row.update(lat=np.nan, lon=np.nan, coord_source="", coord_confidence="not found")
    rows.append(row)
L = pd.DataFrame(rows)
# manual overrides after eyeballing against the papers' own coordinates / more specific Nominatim queries (each documented)
OVR = {"agara": (12.9201739, 77.6418242, "OSM-Nominatim query 'Agara Lake HSR Layout Bengaluru' (top hit 'Agara Lake, HSR Layout')", "medium: replaces an earlier fuzzy match to a different 'Agara' feature ~8 km away; agrees with coordinates printed in L421"),
       "byramangala": (12.7674936, 77.4234771, "OSM-Nominatim query 'Byramangala Reservoir'", "medium: reservoir polygon centre; tank is in Ramanagara district")}
for k, (la, lo, src, conf) in OVR.items():
    m = L.lake_key == k
    L.loc[m, ["lat", "lon", "coord_source", "coord_confidence"]] = [la, lo, src, conf]
# ambiguous names (several OSM features with the same normalised name)
cnt = pd.Series([f[0] for f in feat]).value_counts()
L["osm_name_duplicates"] = L.lake_key.map(lambda k: int(cnt.get(k, 0)))
L.loc[L.osm_name_duplicates > 1, "coord_confidence"] = L.coord_confidence.astype(str) + "; AMBIGUOUS: " + L.osm_name_duplicates.astype(str) + " OSM features share this name"
# ---------- counts
ext = d[~d.record_id.isin(["KSPCB", "CPCB"])].groupby("lake_key").record_id.nunique().rename("n_studies_extracted")
off_k = d[(d.record_id == "KSPCB")].groupby("lake_key").date_start.nunique().rename("kspcb_months")
off_c = d[(d.record_id == "CPCB")].groupby("lake_key").year.nunique().rename("cpcb_years")
L = L.merge(ext, on="lake_key", how="left").merge(off_k, on="lake_key", how="left").merge(off_c, on="lake_key", how="left").fillna({"n_studies_extracted": 0, "kspcb_months": 0, "cpcb_years": 0})
# candidate-paper mentions (title+abstract of full-text-check records)
txt = (pool.title.fillna("") + " " + pool.abstract.fillna("")).str.lower()
def mentions(k):
    pat = r"\b" + re.escape(k) + r"\b" if k not in ("hebbal", "agara") else r"\b" + k + r"\b"
    return int(txt.str.contains(pat, regex=True).sum())
L["n_candidate_papers_mentioning"] = L.lake_key.map(mentions)
L.loc[L.lake_key == "hebbal", "note"] = "Hebbal Lake, Bengaluru (not Hebbal Lake, Mysuru: papers on Mysuru Hebbal were excluded X1)"
L.loc[L.lake_key == "puttenahalli", "note"] = "two lakes share this name (JP Nagar and Yelahanka): treated as one key; coordinates ambiguous"
L.to_csv(R + r"\data\release\lakes.csv", index=False, encoding="utf-8")
print(len(L), "lakes;", L.lat.notna().sum(), "with coordinates")
print(L.sort_values("n_candidate_papers_mentioning", ascending=False).head(15)[["lake_key", "lat", "n_studies_extracted", "kspcb_months", "cpcb_years", "n_candidate_papers_mentioning"]].to_string())

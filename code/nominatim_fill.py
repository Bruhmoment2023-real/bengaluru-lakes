"""Fill coordinates for KSPCB lakes not matched in Overpass using Nominatim (OSM, ODbL). 1 request/sec max, descriptive UA, results cached on E:. Accept only hits inside the Bengaluru bbox."""
import pandas as pd, json, sys, re
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
import common
common.INTERVAL["nominatim.openstreetmap.org"] = 1.5
from common import get
R = r"D:\Research-Publishing\13-bengaluru-lakes"
g = pd.read_csv(R + r"\data\clean\lake_gazetteer_kspcb.csv")
ALIAS = {"ulsoor lake temple": "Halasuru Lake", "ulsoor lake training centre of fish breeding": "Halasuru Lake", "viswaneedam lake": "Vishwaneedam", "vengaiyyanakere kr puram lake": "Vengaiahnakere Lake", "uttarahalli doraikere": "Uttarahalli Doddakere"}
g["coord_source"] = g.lat.notna().map({True: "OSM-Overpass-name-match", False: ""})
for i, r in g[g.lat.isna() & ~g.water_body_type.str.startswith("river")].iterrows():
    q = ALIAS.get(r.name_kspcb, r.name_kspcb)
    q = re.sub(r"\b(lake|tank|kere)\b", "", q).strip()
    best = None
    for qq in (q + " lake Bengaluru", q + " Bengaluru Karnataka"):
        s, t = get("https://nominatim.openstreetmap.org/search", {"q": qq, "format": "jsonv2", "limit": 3, "viewbox": "77.40,13.25,77.85,12.80", "bounded": 1})
        if s != 200: continue
        for h in json.loads(t):
            if 12.80 <= float(h["lat"]) <= 13.25 and 77.40 <= float(h["lon"]) <= 77.85 and (h.get("category") in ("natural", "water", "waterway", "landuse", "leisure") or "lake" in h.get("display_name", "").lower() or "kere" in h.get("display_name", "").lower()):
                best = h; break
        if best: break
    if best:
        g.loc[i, ["osm_name", "osm_id", "lat", "lon", "coord_source"]] = [best["display_name"][:80], f"{best['osm_type']}/{best['osm_id']}", float(best["lat"]), float(best["lon"]), "OSM-Nominatim"]
        print("OK ", r.name_kspcb, "->", best["display_name"][:70], flush=True)
    else: print("NO ", r.name_kspcb, flush=True)
# post-filter: accept Nominatim hits only if the hit name itself is a water feature name (lake/kere/tank/pond/kunte/Halasuru), not a street address or depot
bad = (g.coord_source == "OSM-Nominatim") & ~g.osm_name.fillna("").str.lower().str.match(r"^(\w+\W+){0,3}(lake|kere|tank|pond|kunte|halasuru)|^[^,]*(lake|kere|tank|pond|kunte)")
g.loc[bad, ["osm_name", "osm_id", "lat", "lon", "coord_source"]] = [None, None, None, None, ""]
g["coord_confidence"] = g.apply(lambda r: "" if pd.isna(r.lat) else ("medium (OSM name match score %.2f)" % r.match_score if str(r.coord_source).startswith("OSM-Overpass") else "medium-low (Nominatim top hit; name is a water feature)"), axis=1)
g.to_csv(R + r"\data\clean\lake_gazetteer_kspcb.csv", index=False)
print(g.lat.notna().sum(), "of", len(g), "with coordinates")

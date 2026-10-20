"""Dedupe raw records and apply the fixed protocol pre-screen rule (section 6 of 02-design.md). Writes data/clean/records-dedup.csv and candidates.csv"""
import pandas as pd, re, json
R = r"D:\Research-Publishing\13-bengaluru-lakes"
df = pd.read_csv(R + r"\data\raw\records-raw.csv")
def nt(t): return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()
df["doi"] = df.doi.fillna("").astype(str).str.lower().str.replace("https://doi.org/", "", regex=False).str.strip()
df["ntitle"] = df.title.map(nt)
df["year"] = pd.to_numeric(df.year, errors="coerce")
# group: DOI else title
df["key"] = df.apply(lambda r: r.doi if r.doi and r.doi != "nan" else "T:" + r.ntitle, axis=1)
# unify records which share title but differ in doi presence
t2d = df[df.doi.ne("") & df.doi.ne("nan")].groupby("ntitle").doi.first()
df["key"] = df.apply(lambda r: t2d.get(r.ntitle, r.key) if r.key.startswith("T:") and r.ntitle in t2d.index else r.key, axis=1)
agg = df.groupby("key").agg(title=("title", "first"), doi=("doi", "first"), year=("year", "max"), venue=("venue", lambda s: next((x for x in s if isinstance(x, str) and x), "")),
                            authors=("authors", lambda s: next((x for x in s if isinstance(x, str) and x), "")),
                            abstract=("abstract", lambda s: max([x for x in s if isinstance(x, str)] or [""], key=len)),
                            oa_url=("oa_url", lambda s: next((x for x in s if isinstance(x, str) and x), "")),
                            type=("type", lambda s: next((x for x in s if isinstance(x, str) and x), "")),
                            sources=("source_db", lambda s: "|".join(sorted(set(s)))), n_hits=("source_db", "size")).reset_index()
agg.to_csv(R + r"\data\clean\records-dedup.csv", index=False)
print("raw", len(df), "dedup", len(agg))
LAKES = r"bellandur|varthur|ulsoor|halasuru|hebbal|sankey|lalbagh|agara|madiwala|jakkur|yelahanka|puttenahalli|kaikondrahalli|nagawara|nagavara|hennur|kengeri|hesaraghatta|doddabommasandra|kommaghatta|rachenahalli|mylasandra|yediyur|dore kere|chikkabanavara|hosakere|byramangala|kundalahalli|thubarahalli|tubarahalli|whitefield|kothanur|munnekolala|sarakki|vengaiahnakere|hulimavu|begur|bommasandra|harohalli|ramasandra|kempambudhi|kempambudi|subramanyapura|kasavanahalli|iblur|ibbalur|carmelaram|kogilu|amruthahalli|dasarahalli|nayandahalli|nagarbhavi|mallathahalli|uttarahalli|chinnapanahalli|kudlu|belathur|hoskote|devanahalli|sampigehalli|gottigere|jakkasandra|doddakallasandra|konanakunte|vibhuthipura|gunjur|haralur|hosur|thippagondanahalli|tippagondanahalli|arkavathy|vrishabhavathi|k\&c valley|koramangala|challaghatta|bengaluru|bangalore|bangaluru"
BLR = r"bengaluru|bangalore|bangaluru|bellandur|varthur|hebbal|ulsoor|sankey|lalbagh|madiwala|jakkur|puttenahalli|kaikondrahalli|agara"
WB = r"\blake|\blakes|\btank|\btanks|wetland|\bkere\b|reservoir|pond"
WQ = r"water quality|dissolved oxygen|\bbod\b|\bcod\b|biochemical oxygen|physico|physicochemical|polluti|sewage|wastewater|nutrient|nitrate|phosph|nitrogen|coliform|heavy metal|metals|eutroph|foam|froth|surfactant|contaminat|chlorophyll|toxic|turbidity|conductiv|\bph\b|alkalinity|hardness|trophic|algal|algae|cyanobacter|phytoplankton|zooplankton|limnolog|treatment wetland|restoration|rejuvenation|effluent|ammonia|salinity|fecal|faecal"
def txt(r): return (str(r.title) + " " + str(r.abstract) + " " + str(r.venue)).lower()
def flag(r):
    t = txt(r)
    a = bool(re.search(BLR, t)); b = bool(re.search(WB, t)); c = bool(re.search(WQ, t))
    return pd.Series(dict(blr=a, wb=b, wq=c, cand=(a and b and c)))
f = agg.apply(flag, axis=1); agg = pd.concat([agg, f], axis=1)
agg.to_csv(R + r"\data\clean\records-dedup-flagged.csv", index=False)
print(agg[["blr", "wb", "wq", "cand"]].sum()); print(agg.groupby("sources").cand.agg(["size", "sum"]).sort_values("sum", ascending=False).head(15))
agg[agg.cand].sort_values("year").to_csv(R + r"\data\clean\candidates.csv", index=False)

"""Run protocol search families on 6 sources; write data/raw/records-raw.csv and search-log.csv. Resumable via cache."""
import sys, json, re, csv, html, time
from urllib.parse import quote
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from common import get, ROOT
rows = []; slog = []
def add(src, q, **k):
    k.update(source_db=src, query=q); rows.append(k)
def clean(s): return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", s or ""))).strip()

# ---- OpenAlex (title/abstract filter; cheap)
OA = [("A", '(Bengaluru OR Bangalore OR Bangaluru) AND (lake OR lakes OR tank OR tanks OR wetland OR wetlands) AND ("water quality" OR pollution OR eutrophication OR "dissolved oxygen" OR BOD OR physicochemical OR physico-chemical OR sewage OR nutrient OR coliform OR "heavy metal")'),
      ("B1", "(Bellandur OR Varthur OR Ulsoor OR Hebbal OR Sankey OR Lalbagh OR Agara OR Madiwala OR Jakkur OR Yelahanka OR Puttenahalli OR Kaikondrahalli OR Nagawara OR Hennur OR Kengeri OR Hesaraghatta OR Doddabommasandra OR Kommaghatta) AND (lake OR lakes OR tank OR wetland)"),
      ("C", '(Bellandur OR Varthur) AND (foam OR froth OR fire OR surfactant OR "heavy metal" OR metals OR pollution)'),
      ("A2", '(Bengaluru OR Bangalore) AND (lake OR lakes) AND (restoration OR rejuvenation OR sewage OR STP OR "treatment wetland" OR eutrophication OR algae OR cyanobacteria OR phytoplankton)')]
for fam, q in OA:
    cur = 1; n = 0
    while cur and n < 8:
        s, t = get("https://api.openalex.org/works", {"filter": "title_and_abstract.search:" + q, "per-page": 100, "page": cur,
                   "select": "id,doi,title,publication_year,type,abstract_inverted_index,primary_location,open_access,authorships,cited_by_count,referenced_works"})
        if s != 200:
            slog.append(("openalex", fam, q, "HTTP %s" % s, 0)); print("OA fail", s, t[:200]); break
        d = json.loads(t); n += 1
        for w in d["results"]:
            ab = ""
            if w.get("abstract_inverted_index"):
                pos = {}
                for word, ps in w["abstract_inverted_index"].items():
                    for p in ps: pos[p] = word
                ab = " ".join(pos[i] for i in sorted(pos))
            pl = w.get("primary_location") or {}
            add("OpenAlex", fam, id=w["id"], doi=(w.get("doi") or "").replace("https://doi.org/", ""), title=w["title"], year=w["publication_year"], abstract=ab,
                venue=((pl.get("source") or {}).get("display_name")), oa_url=(w.get("open_access") or {}).get("oa_url"),
                authors="; ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:6]), type=w.get("type"), refs="|".join(w.get("referenced_works") or []))
        slog.append(("openalex", fam, q, "count=%s page=%d" % (d["meta"]["count"], n), len(d["results"])))
        cur += 1
        if len(d["results"]) < 100: break
# ---- Crossref
CR = ["Bangalore lake water quality", "Bengaluru lake water quality", "Bellandur lake", "Varthur lake", "Bangalore lakes pollution", "Bengaluru lakes sewage eutrophication", "Bellandur Varthur foam", "Ulsoor lake", "Hebbal lake water", "Sankey tank water quality", "Lalbagh lake", "Madiwala lake", "Agara lake", "Jakkur lake", "Yelahanka lake", "Bangalore lake heavy metals", "Bangalore lake physico-chemical", "Bangalore lake zooplankton phytoplankton water quality", "Bangalore urban lakes restoration water", "Hesaraghatta lake", "Kengeri lake", "Puttenahalli lake", "Bangalore tank coliform"]
for q in CR:
    for off in (0, 100):
        s, t = get("https://api.crossref.org/works", {"query.bibliographic": q, "rows": 100, "offset": off, "select": "DOI,title,issued,container-title,abstract,author,type"})
        if s != 200:
            slog.append(("crossref", "", q, "HTTP %s" % s, 0)); break
        its = json.loads(t)["message"]["items"]
        for w in its:
            add("Crossref", q, doi=w.get("DOI"), title=clean((w.get("title") or [""])[0]), year=((w.get("issued", {}).get("date-parts") or [[None]])[0] or [None])[0], abstract=clean(w.get("abstract")),
                venue=clean((w.get("container-title") or [""])[0]), type=w.get("type"), authors="; ".join((a.get("family") or "") for a in w.get("author", [])[:6]))
        slog.append(("crossref", "", q, "offset=%d" % off, len(its)))
# ---- DOAJ
for q in ["Bangalore lake", "Bengaluru lake", "Bellandur", "Varthur", "Bangalore lakes water quality", "Bengaluru lakes pollution", "Bangalore wetland", "Bengaluru lake restoration"]:
    for pg in (1, 2):
        s, t = get("https://doaj.org/api/search/articles/" + quote(q), {"pageSize": 100, "page": pg})
        if s != 200:
            slog.append(("doaj", "", q, "HTTP %s" % s, 0)); break
        res = json.loads(t).get("results", [])
        for r in res:
            b = r["bibjson"]; doi = next((i["id"] for i in b.get("identifier", []) if i["type"] == "doi"), "")
            add("DOAJ", q, doi=doi, title=clean(b.get("title")), year=b.get("year"), abstract=clean(b.get("abstract")), venue=(b.get("journal") or {}).get("title"),
                authors="; ".join(a.get("name", "") for a in b.get("author", [])[:6]), type="article")
        slog.append(("doaj", "", q, "page=%d" % pg, len(res)))
        if len(res) < 100: break
# ---- Shodhganga
for q in ["Bangalore lake water quality", "Bengaluru lakes", "Bellandur", "Varthur lake", "lakes of Bangalore", "Bangalore tanks pollution", "Bangalore lake eutrophication", "urban lakes Bangalore restoration", "Hebbal lake", "Ulsoor lake", "Karnataka lakes physico-chemical"]:
    for st in (0, 10, 20):
        s, t = get("https://shodhganga.inflibnet.ac.in/simple-search", {"query": q, "rpp": 10, "start": st})
        if s != 200:
            slog.append(("shodhganga", "", q, "HTTP %s" % s, 0)); break
        its = re.findall(r'<td headers="t1"[^>]*>([^<]*)</td><td headers="t2"[^>]*><a href="(/handle/[^"]+)">(.*?)</a></td><td headers="t3"[^>]*><em>(.*?)</em>', t, re.S)
        for dt, h, ti, au in its:
            add("Shodhganga", q, title=clean(ti), authors=clean(au), year=dt.strip()[-4:], venue="Shodhganga thesis", type="thesis", oa_url="https://shodhganga.inflibnet.ac.in" + h)
        slog.append(("shodhganga", "", q, "start=%d" % st, len(its)))
        if len(its) < 10: break
# ---- Semantic Scholar (heavily rate-limited; best effort)
for q in ["Bellandur lake water quality", "Bangalore lakes water quality", "Bengaluru lake pollution", "Varthur lake", "Bangalore lake eutrophication", "Bengaluru urban lakes sewage"]:
    ok = False
    for t_ in range(1):
        s, t = get("https://api.semanticscholar.org/graph/v1/paper/search", {"query": q, "limit": 100, "fields": "title,year,externalIds,abstract,venue,authors"})
        if s == 200: ok = True; break
        time.sleep(5)
    if not ok:
        slog.append(("semanticscholar", "", q, "HTTP %s (rate-limited)" % s, 0)); continue
    res = json.loads(t).get("data", [])
    for r in res:
        add("SemanticScholar", q, doi=(r.get("externalIds") or {}).get("DOI"), title=r["title"], year=r.get("year"), abstract=r.get("abstract") or "", venue=r.get("venue"), authors="; ".join(a["name"] for a in (r.get("authors") or [])[:6]))
    slog.append(("semanticscholar", "", q, "ok", len(res)))
# ---- Google Scholar (plain fetch, polite; stop at first block)
blocked = False
for q in ["Bellandur lake water quality", "Bangalore lakes water quality", "Bengaluru lake pollution BOD dissolved oxygen", "Varthur lake water quality", "Bangalore lake physico-chemical parameters", "Bengaluru lakes coliform", "Bangalore lake heavy metals", "Ulsoor lake water quality", "Hebbal lake water quality", "Bengaluru lakes foam surfactants", "Bangalore lake eutrophication nutrients", "KSPCB lake water quality monitoring Bangalore"]:
    if blocked: break
    for st in (0, 10):
        s, t = get("https://scholar.google.com/scholar", {"q": q, "start": st, "hl": "en"})
        if s != 200 or "unusual traffic" in t or "gs_captcha" in t:
            blocked = True; slog.append(("scholar", "", q, "BLOCKED HTTP %s - stopped, not circumvented" % s, 0)); break
        n = 0
        for b in re.findall(r'<h3 class="gs_rt"[^>]*>(.*?)</h3>(.*?)(?=<h3 class="gs_rt"|$)', t, re.S):
            ti = clean(re.sub(r'<span class="gs_ct\w*">.*?</span>', '', b[0])); m = re.search(r'href="([^"]+)"', b[0])
            sn = re.search(r'class="gs_rs">(.*?)</div>', b[1], re.S); meta = re.search(r'class="gs_a">(.*?)</div>', b[1], re.S)
            ym = re.search(r"\b(19|20)\d\d\b", clean(meta.group(1)) if meta else "")
            add("GoogleScholar", q, title=ti, abstract=clean(sn.group(1)) if sn else "", authors=clean(meta.group(1)) if meta else "", year=ym.group(0) if ym else "", oa_url=m.group(1) if m else ""); n += 1
        slog.append(("scholar", "", q, "start=%d" % st, n))
import pandas as pd
df = pd.DataFrame(rows); df.to_csv(ROOT + r"\data\raw\records-raw.csv", index=False)
pd.DataFrame(slog, columns=["database", "family", "query", "note", "n_records"]).assign(date="2026-10-17").to_csv(ROOT + r"\data\raw\search-log.csv", index=False)
print(df.groupby("source_db").size())

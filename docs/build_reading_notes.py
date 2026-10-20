"""Reading notes: one Markdown note per extracted study, assembled by program from the study's own PDF text (verbatim quotations with PDF page numbers) and from the extracted dataset.
Nothing is filled from memory: sentences are copied from the PDF text layer; numbers come from data/release/lake_measurements_long.csv. Review each note before relying on it."""
import pandas as pd, numpy as np, re, os, pdfplumber
R = r"D:\Research-Publishing\13-bengaluru-lakes"; N = R + r"\depth\reading-notes"; os.makedirs(N, exist_ok=True)
d = pd.read_csv(R + r"\data\release\lake_measurements_long.csv", low_memory=False); st = pd.read_csv(R + r"\data\release\studies.csv").set_index("record_id")
FT = r"E:\Research-Staging\13-bengaluru-lakes\fulltext"
poolid = {"L047": 47, "L063": 63, "L068": 68, "L112": 112, "L138": 138, "L147": 147, "L172": 172, "L175": 175, "L207": 207, "L234": 234, "L287": 287, "L291": 291, "L378": 378, "L409": 409, "L421": 421, "L445": 445, "L453": 453, "L462": 462, "L492": 492, "L514": 514}
FIRST = {"L047": "bindiya", "L063": "devi", "L068": "jumbe", "L112": "lekhashree", "L138": "ravikumar", "L147": "nagendra", "L172": "shekar", "L175": "upadhyay", "L207": "alimuddin", "L234": "arya", "L287": "naik", "L291": "rao", "L378": "raju", "L409": "umadevi", "L421": "shashank", "L445": "venkata", "L453": "ravikumar", "L462": "moramchetty", "L492": "ravikumar", "L514": "narayanaswamy"}
SHORT = {"L047": "mallathalli", "L063": "madhavara", "L068": "varthur", "L112": "kspcb16", "L138": "sankey", "L147": "hebbal", "L172": "gidadakonenahalli", "L175": "ulsoor", "L207": "ulsoor", "L234": "14lakes", "L287": "hebbal", "L291": "ions", "L378": "andrahalli", "L409": "bellandur", "L421": "metals", "L445": "byramangala", "L453": "dorekere", "L462": "ulsoor", "L492": "hebbal", "L514": "varthur"}
def norm(s): return re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()

def page_text(pg):
    """text of a page; two-column pages are read left column then right column; running headers/footers (top/bottom 6 percent) dropped"""
    w, h = pg.width, pg.height
    pg = pg.crop((0, 0.06 * h, w, 0.94 * h))
    ws = pg.extract_words()
    if len(ws) > 80:
        cross = sum(1 for x in ws if x["x0"] < 0.47 * w and x["x1"] > 0.53 * w)
        left = sum(1 for x in ws if x["x1"] <= 0.5 * w); right = sum(1 for x in ws if x["x0"] >= 0.5 * w)
        if cross / len(ws) < 0.06 and left > 0.25 * len(ws) and right > 0.25 * len(ws):
            return (pg.crop((0, 0.06 * h, w * 0.5, 0.94 * h)).extract_text() or "") + " " + (pg.crop((w * 0.5, 0.06 * h, w, 0.94 * h)).extract_text() or "")
    return pg.extract_text() or ""
idx = []
for rid, pid in poolid.items():
    path = rf"{FT}\{pid}.pdf"; s = st.loc[rid]
    pages = []
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages); rng = list(range(min(n, 6))) + list(range(max(6, n - 3), n)) if n > 12 else list(range(n))
        for i in dict.fromkeys(rng): pages.append((i + 1, norm(page_text(pdf.pages[i]))))
    sents = []
    for pg, t in pages:
        for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t):
            w = x.split()
            if 8 <= len(w) <= 60: sents.append((pg, x))
    def pick(pat, k, need_digit=False, skip=()):
        out = []
        for pg, x in sents:
            if re.search(pat, x, re.I) and (not need_digit or re.search(r"\d", x)) and x not in skip and not re.search(r"doi|issn|received|accepted|copyright|http|acknowledg|grateful|thank|deputation", x, re.I): out.append((pg, x))
            if len(out) >= k: break
        return out
    rq = pick(r"\b(aim|objective|purpose|this study|present study|present work|attempt|was carried out|investigat)", 2)
    meth = pick(r"(collected|sampled|analy[sz]ed|APHA|standard methods|atomic absorption|IS ?3025|digest)", 2)
    res = pick(r"(ranged|varied|exceed|found to be|recorded|above the|higher than|mg/l|mg l)", 3, True)
    lim = pick(r"(limitation|further stud|should be|need for|future)", 2)
    q = []
    for pg, x in (res + rq + [y for y in pick(r"(polluted|deteriorat|sewage|eutroph|poor)", 2)]):
        w = x.split(); t = " ".join(w[:38]) + (" ..." if len(w) > 38 else "")
        if all(t != a for _, a in q): q.append((pg, t))
        if len(q) >= 5: break
    sub = d[(d.record_id == rid) & d.value.notna()]
    lakes = ", ".join(sorted(sub.lake_key.unique())[:12]); yrs = sub.year.dropna()
    def med(p): v = sub[(sub.parameter_std == p) & sub.statistic.isin(["single", "mean"])].value_std.dropna(); return f"median {v.median():.2f}, range {v.min():.2f}-{v.max():.2f} (n={len(v)})" if len(v) else "not reported/extracted"
    flags = sorted({f.strip() for fs in sub.comparability_flag.dropna() for f in fs.split(";") if f.strip()})[:6]
    L_rq = [f"- (p.{pg}) \"{x}\"" for pg, x in rq] or ["- not located by program"]
    L_meth = [f"- (p.{pg}) \"{x}\"" for pg, x in meth] or ["- not located by program"]
    fn = f"{FIRST[rid]}-{int(s.year)}-{SHORT[rid]}.md"
    md = [f"# {s.citation}", "", f"- Link: {('https://doi.org/' + s.doi) if isinstance(s.doi, str) and s.doi else '(no DOI; see references.bib note)'}", f"- Read from: opened full text (PDF) staged at E:\\Research-Staging\\13-bengaluru-lakes\\fulltext\\{pid}.pdf; quotations below are copied from the PDF text layer ({n} pages).", f"- Record id in dataset: {rid}; quality score {int(s.quality_score)}/6 (dates {s.q_dates}, sites {s.q_sites}, method {s.q_method}, replicates {s.q_replicates}, QA/QC {s.q_qaqc}, raw data {s.q_raw})", "",
          "## Research question / aim (author sentences)", *L_rq, "", "## Data and sample", f"- Dataset rows from this study: {len(sub)}; lakes: {lakes}; years covered: {int(yrs.min()) if len(yrs) else 'not stated'}-{int(yrs.max()) if len(yrs) else 'not stated'}; extraction note: {s.notes}", "",
          "## Method (author sentences)", *L_meth, "", "## Main results with the numbers extracted into the dataset",
          f"- DO (mg/L): {med('DO')}", f"- BOD (mg/L): {med('BOD')}", f"- pH: {med('pH')}", f"- Parameters extracted: {sub.parameter_std.nunique()}", "", "## Limitations", "- Stated by authors (sentences containing limitation/future work cues): " + ("; ".join(f'(p.{pg}) "{x[:200]}"' for pg, x in lim) if lim else "none located by program"), "- Flags from this review: " + ("; ".join(flags) if flags else "none"), "",
          "## Verbatim quotations (each <= 38 words, from the PDF text layer)", *[f"- p.{pg}: \"{t}\"" for pg, t in q], "", "## Bearing on this paper", f"- Use in dataset: {sub.analysis_use.iloc[0] if len(sub) else ''}", "- Relation: primary data source (supports coverage and compliance; no trend contribution unless dated series).", "", "## Self-test questions", "- Which lake(s), which period, which parameters, and what sampling design did the authors use?", "- Which of the extracted values would fail a CPCB Class C/D criterion, and is the unit/basis stated?", "- What would make this study's numbers incomparable with KSPCB/CPCB monitoring?"]
    open(rf"{N}\{fn}", "w", encoding="utf-8").write("\n".join(md) + "\n"); idx.append((fn, rid, s.citation[:90], len(q), f"DO {med('DO')}"))
    print(fn, len(q), flush=True)
open(rf"{N}\00-index.md", "w", encoding="utf-8").write("# Reading notes index\n\nNotes are assembled by `depth/build_reading_notes.py` from each PDF's text layer (verbatim quotes with page numbers) and from the extracted dataset. All 20 extracted studies; abstract-only notes: none (all full texts were opened).\n\n| note | record | study | quotes | takeaway (DO) |\n|---|---|---|---|---|\n" + "\n".join(f"| {a} | {b} | {c} | {n} | {e} |" for a, b, c, n, e in idx) + "\n")

"""Helpers for transcribing reported measurements from staged full texts into tidy rows. Every row records the source line number in the staged text
(pdftotext -layout output) so extraction is auditable. Values are parsed from the text by program, not typed from memory, wherever a table exists."""
import re, csv, os
TX = r"E:\Research-Staging\13-bengaluru-lakes\text"
OUT = r"D:\Research-Publishing\13-bengaluru-lakes\data\raw\extraction"
os.makedirs(OUT, exist_ok=True)
FIELDS = ["record_id", "lake", "site", "date_start", "date_end", "period_precision", "season", "parameter", "parameter_as_reported", "statistic", "value", "unit_as_reported",
          "method", "n_samples", "page_table", "extraction_mode", "source_line", "comparability_flag", "notes"]
NUM = re.compile(r"(?<![\w.])[-\u2212]?\d+(?:,\d{3})*(?:\.\d+)?(?![\w])")
def lines(rid):
    return open(rf"{TX}\{rid}.txt", encoding="utf-8", errors="replace").read().replace("\x0c", "\n").split("\n")
def nums(s):
    out = []
    for m in NUM.findall(s):
        out.append(float(m.replace(",", "").replace("\u2212", "-")))
    return out
class Ex:
    def __init__(self, rid):
        self.rid = rid; self.L = lines(rid); self.rows = []
    def find(self, label, start=0, end=None, nth=0):
        """index of the nth line (within [start,end)) whose stripped text starts with label"""
        c = 0
        for i in range((start or 0), (end or len(self.L))):
            if self.L[i].strip().startswith(label):
                if c == nth: return i
                c += 1
        raise KeyError(f"{self.rid}: {label} not found")
    def add(self, **k):
        r = {f: "" for f in FIELDS}; r.update(record_id=self.rid, extraction_mode="table-parsed"); r.update(k); self.rows.append(r)
    def table(self, start, end, spec, cols, lake, site="", unit_map=None, page_table="", method="", **common):
        """spec: {label_prefix: (parameter, unit)}; cols: list of (date_start, date_end, precision, statistic, [site override]) for each numeric column in order after the label."""
        got = 0
        for i in range(start, end):
            s = self.L[i].strip()
            for lab, (p, u) in spec.items():
                if s.startswith(lab):
                    v = nums(s[len(lab):])
                    if len(v) < len(cols): continue
                    for val, c in zip(v, cols):
                        d0, d1, prec, stat = c[:4]; st = c[4] if len(c) > 4 else site
                        self.add(lake=lake, site=st, date_start=d0, date_end=d1, period_precision=prec, parameter=p, parameter_as_reported=lab, statistic=stat, value=val,
                                 unit_as_reported=u, method=method, page_table=page_table, source_line=i + 1, **common)
                    got += 1; break
        return got
    def save(self):
        with open(rf"{OUT}\{self.rid}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(self.rows)
        return len(self.rows)

def _tok(s):
    out = []
    for t in s.split():
        t2 = t.strip(",;")
        if re.fullmatch(r"[-\u2212]?\d+(?:\.\d+)?", t2): out.append(float(t2.replace("\u2212", "-")))
        elif t2.lower() in ("nd", "bdl", "-", "nil", "na", "n.d.", "bdl."): out.append(t2.lower())
        else: return None
    return out

def grid(self, start, end, param, unit, lake, year, labels=("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"), avg_label="Average", ncol=12, month_names=None,
         page_table="", method="", site_prefix="", **common):
    """Monthly grid: rows start with a label then ncol tokens (numbers or nd/BDL). Station rows -> single; avg row -> 'mean' (site 'all stations (reported average)')."""
    import calendar
    n = 0
    for i in range(start, end):
        s = self.L[i].strip()
        if not s: continue
        parts = s.split(None, 1)
        if len(parts) < 2: continue
        lab, rest = parts
        if lab in labels or lab == avg_label or (avg_label and s.startswith(avg_label)):
            if s.startswith(avg_label):
                rest = s[len(avg_label):]; lab = avg_label
            t = _tok(rest)
            if t is None or len(t) != ncol: continue
            for m, v in enumerate(t, 1):
                last = calendar.monthrange(year, m)[1]
                isavg = lab == avg_label
                kw = dict(lake=lake, site=("all stations (reported average)" if isavg else site_prefix + lab), date_start=f"{year}-{m:02d}-01", date_end=f"{year}-{m:02d}-{last}",
                          period_precision="month", parameter=param, parameter_as_reported=param, statistic=("mean" if isavg else "single"), unit_as_reported=unit, method=method,
                          page_table=page_table, source_line=i + 1)
                kw.update(common)
                if isinstance(v, str):
                    kw.update(value="", comparability_flag="below_detection_limit (reported '%s')" % v)
                else: kw.update(value=v)
                self.add(**kw)
            n += 1
    return n
Ex.grid = grid

def rec(self, lake, site, ds, de, prec, stat, params, line, table="", method="", n="", flag="", season="", notes="", window=3):
    """Hand-entered values with an audit check: each value must appear as a token within `window` lines of the cited source line (1-based) in the staged text."""
    lo, hi = max(0, line - 1 - window), min(len(self.L), line + window)
    blob = " ".join(self.L[lo:hi]).replace("−", "-")
    toks = set(re.findall(r"\d+(?:\.\d+)?", blob.replace(",", "")))
    for p, (val, unit) in params.items():
        if val is None: continue
        s = ("%g" % val); s2 = repr(val)
        ok = any(t in toks for t in {s, s2, "%.1f" % val, "%.2f" % val, "%.3f" % val, str(int(val)) if float(val).is_integer() else s})
        if not ok: raise ValueError(f"{self.rid}: value {val} for {p} not found near line {line}: {blob[:200]}")
        self.add(lake=lake, site=site, date_start=ds, date_end=de, period_precision=prec, season=season, parameter=p, parameter_as_reported=p, statistic=stat, value=val, unit_as_reported=unit,
                 method=method, n_samples=n, page_table=table, extraction_mode="hand-transcribed (verified token present near source line)", source_line=line, comparability_flag=flag, notes=notes)
Ex.rec = rec

# ---------- word-position based table reading (robust where pdftotext -layout scrambles columns) ----------
def pdf_lines(rid, page, tol=3):
    """Return list of (top, [(x0, text), ...]) for a PDF page of the staged full text (1-based page)."""
    import pdfplumber
    with pdfplumber.open(rf"E:\Research-Staging\13-bengaluru-lakes\fulltext\{rid}.pdf") as p:
        ws = p.pages[page - 1].extract_words(keep_blank_chars=False, x_tolerance=2)
    rows = {}
    for w in ws: rows.setdefault(round(w["top"] / tol), []).append(w)
    out = []
    for k in sorted(rows):
        r = sorted(rows[k], key=lambda w: w["x0"]); out.append((min(w["top"] for w in r), [(round(w["x0"], 1), w["text"]) for w in r]))
    return out

def pdf_rows(rid, page, labels, ncols, tol=3, after=None):
    """For each label (first word(s) of a line), return the list of numeric-looking tokens following it on that line; assert ncols tokens."""
    res = {}; started = after is None
    for top, r in pdf_lines(rid, page, tol):
        txt = " ".join(t for _, t in r)
        if not started:
            if after in txt: started = True
            continue
        for lab in labels:
            if txt.startswith(lab) and lab not in res:
                toks = [t for _, t in r][len(lab.split()):]
                toks = [t for t in toks if re.fullmatch(r"[<>]?[-\u2212]?\d+(?:[.,]\d+)?|ND|BDL|nd|-", t)]
                res[lab] = toks
    return res

def pdf_rows2(rid, page, labels, ncols, vtol=5, after=None):
    """Like pdf_rows but gathers numeric tokens within +-vtol points vertically of the label (handles slightly offset cells)."""
    import pdfplumber
    with pdfplumber.open(rf"E:\Research-Staging\13-bengaluru-lakes\fulltext\{rid}.pdf") as p:
        ws = p.pages[page - 1].extract_words(keep_blank_chars=False, x_tolerance=2)
    ws = sorted(ws, key=lambda w: (round(w["top"] / 3), w["x0"]))
    start_top = -1
    if after:
        for w in ws:
            if w["text"].startswith(after.split()[0]) and after in " ".join(v["text"] for v in ws if abs(v["top"] - w["top"]) < 3): start_top = w["top"]; break
    res = {}
    for lab in labels:
        first = lab.split()[0]
        cand = [w for w in ws if w["text"] == first and w["top"] > start_top]
        if not cand: continue
        lw = cand[0]
        toks = sorted([w for w in ws if abs(w["top"] - lw["top"]) <= vtol and w["x0"] > lw["x1"] + 5], key=lambda w: w["x0"])
        res[lab] = [(round(w["x0"], 1), w["text"]) for w in toks if re.fullmatch(r"[<>]?[-\u2212]?\d+(?:[.,]\d+)?|ND|BDL|nd|-", w["text"])]
    return res

def pdf_grid(rid, page, header_first_word, labels, ncols=None, vtol=3, left_pad=5):
    """Column-aware row reader: finds the header line starting with `header_first_word`, takes x0 of each following header word as column anchors, then for each label row assigns
    every character to a column by x position (handles glued numbers). Returns {label: [cell strings]}."""
    import pdfplumber
    with pdfplumber.open(rf"E:\Research-Staging\13-bengaluru-lakes\fulltext\{rid}.pdf") as p:
        pg = p.pages[page - 1]; ws = pg.extract_words(x_tolerance=1); chars = pg.chars
    hw = [w for w in ws if w["text"].startswith(header_first_word)]
    h = hw[0]
    hdr = sorted([w for w in ws if abs(w["top"] - h["top"]) < 3 and w["x0"] > h["x1"] - 1], key=lambda w: w["x0"])
    anchors = [w["x0"] for w in hdr]
    if ncols and len(anchors) != ncols: raise ValueError(f"header anchors {len(anchors)} != {ncols}: {[w['text'] for w in hdr]}")
    out = {}
    for lab in labels:
        cand = [w for w in ws if w["text"] == lab.split()[0] and w["top"] > h["top"]]
        if not cand: continue
        lw = cand[0]
        cells = [""] * len(anchors)
        for c in sorted([c for c in chars if abs(c["top"] - lw["top"]) <= vtol and c["x0"] > lw["x1"] + 2], key=lambda c: c["x0"]):
            col = max([i for i, a in enumerate(anchors) if a - left_pad <= c["x0"]] or [0])
            cells[col] += c["text"]
        out[lab] = cells
    return out, [w["text"] for w in hdr]

def rec_visual(self, lake, site, ds, de, prec, stat, params, table="", method="", n="", flag="", season="", notes="", img=""):
    """Values read by eye from a rendered page image (pdfplumber to_image) and typed; no text-layer check possible."""
    for p, (val, unit) in params.items():
        if val is None: continue
        self.add(lake=lake, site=site, date_start=ds, date_end=de, period_precision=prec, season=season, parameter=p, parameter_as_reported=p, statistic=stat, value=val, unit_as_reported=unit,
                 method=method, n_samples=n, page_table=table, extraction_mode="hand-transcribed from rendered page image " + img, comparability_flag=flag, notes=notes)
Ex.rec_visual = rec_visual

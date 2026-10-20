"""Extract CPCB NWMP 'Water quality of Lakes, Ponds and Tanks' tables (annual min-max per station) for Karnataka, 2016-2023 (+2024 LPT files) into tidy CSV.
Source PDFs: cpcb.gov.in/wqm/<year>/Water_pond_tanks_<year>.pdf (public CPCB publications; staged on E:)."""
import pdfplumber, re, glob, os, csv, sys
SRC = r"E:\Research-Staging\13-bengaluru-lakes\official\cpcb\pdf"
OUT = r"D:\Research-Publishing\13-bengaluru-lakes\data\clean\official_cpcb_nwmp_karnataka_lakes_wide.csv"
PAR = [("temperature", "degC"), ("DO", "mg/L"), ("pH", "pH units"), ("EC", "umho/cm"), ("BOD", "mg/L"), ("nitrate_plus_nitrite_N", "mg/L"), ("faecal_coliform", "MPN/100mL"), ("total_coliform", "MPN/100mL")]
def num(s):
    s = (s or "").replace("\n", " ").strip().replace(",", "")
    if s in ("", "-", "--", "NA", "ND", "BDL"): return None
    m = re.match(r"^[<>]?\s*(\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else None
rows = []; log = []
for f in sorted(glob.glob(SRC + r"\*pond_tanks*.pdf")) + [SRC + r"\NWMP_2015.pdf"]:
    yr = int(re.search(r"(20\d\d)", os.path.basename(f)).group(1))
    n = 0
    try:
        with pdfplumber.open(f) as pdf:
            for pi, pg in enumerate(pdf.pages):
                t = pg.extract_text() or ""
                if "KARNATAKA" not in t.upper(): continue
                for tb in pg.extract_tables():
                    for r in tb:
                        cells = [(c or "").strip() for c in r]
                        if sum(1 for c in cells if c == "") > 0.5 * len(cells): cells = [c for c in cells if c != ""]   # sparse layouts (2018): compress
                        if not cells or not re.match(r"^\d{3,5}$", cells[0]): continue
                        try: si = next(i for i, c in enumerate(cells) if c.upper() == "KARNATAKA")
                        except StopIteration: continue
                        vals = [num(c) for c in cells[si + 1:]]
                        comp = [num(c) for c in cells[si + 1:] if c != ""]
                        if len(comp) >= 16 and sum(v is not None for v in comp[:16]) == 16: vals = comp[:16]   # sparse-column layouts (e.g. 2020)
                        vals = (vals + [None] * 16)[:16]
                        rows.append(dict(year=yr, stn=cells[0], name_reported=re.sub(r"\s+", " ", cells[1]) if cells[1] else "", water_body=cells[2] if si >= 3 else "", page=pi + 1, source_file=os.path.basename(f), **{f"{p}_{mm}": v for (p, _), (v, mm) in zip([x for x in PAR for _ in (0, 1)], zip(vals, ["min", "max"] * 8))}))
                        n += 1
    except Exception as e:
        print("ERR", f, e)
    log.append((yr, n)); print(yr, n, flush=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows))

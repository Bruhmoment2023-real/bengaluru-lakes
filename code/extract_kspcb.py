"""Extract KSPCB monthly 'Water Quality Data of Bengaluru Lakes' PDFs (OpenCity mirror of KSPCB; licence 'Other (Public Domain)') into tidy long CSV.
Files with readable headers: all columns mapped by header text. Files with garbled (rotated-text) headers: core columns only, by position, validated by value ranges.
PDFs are in E:\\Research-Staging (staging)."""
import re, glob, os, csv
import pdfplumber
SRC = r"E:\Research-Staging\13-bengaluru-lakes\official\kspcb-monthly"
OUT = r"D:\Research-Publishing\13-bengaluru-lakes\data\clean\official_kspcb_long.csv"
PARAMS = [  # regex on collapsed (no spaces) lower header
    (r"temper", "temperature", "degC"), (r"dissolved?o|^do\b", "DO", "mg/L"), (r"^ph$|^ph\(", "pH", "pH"), (r"conductiv", "EC", "uS/cm"),
    (r"^bod", "BOD", "mg/L"), (r"nitraten|nitrate", "nitrate_N", "mg/L"), (r"nitriten|nitrite", "nitrite_N", "mg/L"),
    (r"fecalcoliform|faecalcoliform", "faecal_coliform", "MPN/100mL"), (r"totalcoliform", "total_coliform", "MPN/100mL"),
    (r"strepto|cci\(", "faecal_streptococci", "MPN/100mL"), (r"bicarb|hco3", "bicarbonate", "mg/L"), (r"^carbo", "carbonate", "mg/L"),
    (r"turbid", "turbidity", "NTU"), (r"phenolph", "phenolphthalein_alkalinity", "mg/L"), (r"totalalkalin", "total_alkalinity", "mg/L"),
    (r"chlorid", "chloride", "mg/L"), (r"^cod", "COD", "mg/L"), (r"kjeldahl|^tkn", "TKN", "mg/L"), (r"ammon", "ammoniacal_N", "mg/L"),
    (r"totalhardness", "total_hardness", "mg/L as CaCO3"), (r"caasca", "calcium_hardness", "mg/L as CaCO3"), (r"^ca\(|^calcium", "calcium", "mg/L"),
    (r"mgasca", "magnesium_hardness", "mg/L as CaCO3"), (r"^mg\(|magnesium", "magnesium", "mg/L"), (r"sodiumperc|^na%", "sodium_percentage", "%"),
    (r"^sodium", "sodium", "mg/L"), (r"dissolvedsolid|^tds", "TDS", "mg/L"), (r"suspended", "TSS", "mg/L"), (r"ortho", "orthophosphate", "mg/L"),
    (r"phosphate", "phosphate", "mg/L"), (r"boron", "boron", "mg/L"), (r"potass", "potassium", "mg/L"), (r"fluorid", "fluoride", "mg/L"),
    (r"sulph|sulf", "sulphate", "mg/L"), (r"^sar", "SAR", "ratio"), (r"saprob", "saprobity_index", "index"), (r"diversity", "diversity_index", "index"),
    (r"cadmium", "cadmium", "mg/L"), (r"copper", "copper", "mg/L"), (r"chromium", "chromium_total", "mg/L"), (r"nickel", "nickel", "mg/L"), (r"zinc", "zinc", "mg/L"),
    (r"^iron|^fe\(", "iron", "mg/L"), (r"mangan", "manganese", "mg/L"), (r"^lead", "lead", "mg/L"), (r"mercury", "mercury", "mg/L"), (r"arsenic", "arsenic", "mg/L"),
]
def norm(h): return re.sub(r"\s+", " ", (h or "").replace("&micro;", "u").replace("\n", " ")).strip().lower()
def coll(h): return re.sub(r"[\s\-]+", "", norm(h))
def canon(h):
    n = coll(h)
    if not n or re.match(r"(stn|sl\.?no|sampling|name|location|use|class|code)", n): return None
    for rx, c, u in PARAMS:
        if re.search(rx, n): return (c, u)
    return ("UNMAPPED", "")
MON = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
MONFULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def parse_val(s):
    s = (s or "").replace("\n", " ").strip()
    if s in ("", "NA", "_", "-", "--", "N/A", "ND", "NR", "NIL", "Nil"): return None
    if s.upper() == "BDL": return (None, "below_detection_limit_value_missing")
    flag = "below_detection_limit" if re.search(r"bdl", s, re.I) else ""
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", s.replace(",", ""))
    if not m: return None
    if s[0] in "<>": flag = "censored:" + s[0]
    return (float(m.group(1)), flag)
def num(s):
    try: return float(re.sub(r"[^0-9.]", "", (s or "").replace("(BDL)", "")) or "nan")
    except: return float("nan")
def is_header(cells):
    j = norm(" ".join(cells))
    ne = sum(1 for c in cells if c.strip())
    return ne >= 8 and ((("monitoring" in j or "location" in j) and "class" in j) or any(norm(c) == "ph" for c in cells))
rows = []; flog = []
for f in sorted(glob.glob(SRC + r"\*.pdf")):
    base = os.path.basename(f)
    ym = re.search(r"_(" + "|".join(MONFULL) + r")_(\d{4})", base)
    month = MONFULL.index(ym.group(1)) + 1; year = int(ym.group(2))
    OVERRIDE = {'Lakes_Water_Quality_Report_February_2024.pdf': 3, 'Lakes_Water_Quality_Report_March_2024.pdf': 2}  # OpenCity labels swapped: in-document titles say March / February
    if base in OVERRIDE: month = OVERRIDE[base]
    hdr = None; garbled = False; n = 0
    with pdfplumber.open(f) as pdf:
        for pi, pg in enumerate(pdf.pages):
            for tb in pg.extract_tables():
                for r in tb:
                    cells = [(c or "").strip() for c in r]
                    if is_header(cells):
                        hdr = cells; hn = [coll(h) for h in hdr]
                        core_ok = sum(1 for h in hdr if canon(h) and canon(h)[0] in ("DO", "BOD", "EC", "faecal_coliform", "total_coliform", "pH"))
                        garbled = core_ok < 5; continue
                    if hdr is None or len(cells) < 8: continue
                    hn = [coll(h) for h in hdr]
                    ni = next((i for i, h in enumerate(hn) if "monitoring" in h or h.startswith("name") or h.startswith("location")), None)
                    if ni is None and garbled:
                        ni = next((i for i, c in enumerate(cells[:5]) if len(c) > 6 and re.search(r"[A-Za-z]{4}", c) and not re.match(r"^[A-E] \(", c)), None)
                    if ni is None or ni >= len(cells): continue
                    name = re.sub(r"\s+", " ", cells[ni]).strip()
                    if not re.search(r"[A-Za-z]{3}", name) or re.match(r"(use based|class|water quality)", name, re.I): continue
                    si = next((i for i, h in enumerate(hn) if h.startswith("stn") or h.startswith('"stn') or h.startswith("cstod")), None)
                    stn = cells[si] if si is not None and si < len(cells) else ""
                    ci = next((i for i in range(ni + 1, min(ni + 3, len(cells))) if re.match(r"^[A-E]\b", cells[i])), None)
                    cls = re.sub(r"\s+", " ", cells[ci]) if ci is not None else ""
                    # month: from the sampling-month column if present else filename
                    mon = month
                    for c in ([] if base in OVERRIDE else cells[:5]):
                        if c[:3].lower() in MON and len(c) <= 9 and c.isalpha(): mon = MON[c[:3].lower()]
                    base_rec = dict(source_file=base, page=pi + 1, stn=stn, year=year, month=mon, lake_as_reported=name, kspcb_use_class=cls)
                    colmap = {}
                    if not garbled:
                        for i, h in enumerate(hdr):
                            c = canon(h)
                            if c and c[0] != "UNMAPPED": colmap[i] = (c[0], c[1], norm(h))
                    elif ci is not None:
                        seq = list(range(ci + 1, len(cells)))
                        v = lambda k: num(cells[seq[k]]) if k < len(seq) else float("nan")
                        off = None
                        if 5 <= v(2) <= 10.5 and v(3) >= 50: off = 1   # temp present
                        elif 5 <= v(1) <= 10.5 and v(2) >= 50: off = 0
                        if off is None: continue
                        nit_cols = sum(1 for h in hdr if re.search(r"nitriten|^n\(", coll(h)) or re.search(r"^n\(im|^n\(", coll(h)))
                        order = (["temperature"] if off else []) + ["DO", "pH", "EC", "BOD", "nitrate_N"]
                        has_nitrite = any("nitriten" in h for h in hn)
                        if has_nitrite: order.append("nitrite_N")
                        order += ["faecal_coliform", "total_coliform"]
                        units = {p[1]: p[2] for p in PARAMS}
                        U = {c: u for _, c, u in PARAMS}
                        for k, pname in enumerate(order):
                            colmap[seq[k]] = (pname, U.get(pname, ""), "positional(garbled header)")
                    for i, (pname, unit, hh) in colmap.items():
                        if i >= len(cells): continue
                        pv = parse_val(cells[i])
                        if pv is None: continue
                        rows.append(dict(base_rec, parameter=pname, unit_std=unit, raw=re.sub(r"\s+", " ", cells[i]), value=pv[0], flag=pv[1], header=hh, header_mode="positional" if garbled else "header"))
                    n += 1
    flog.append((base, n, "garbled-core-only" if garbled else "header")); print(base, n, "GARBLED" if garbled else "", flush=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(OUT.replace("official_kspcb_long.csv", "official_kspcb_extraction_log.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["file", "station_rows", "mode_last_table"]); w.writerows(flog)
print(len(rows), "rows")

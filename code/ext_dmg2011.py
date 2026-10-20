"""Parse 'Bangalore Lakes Water Quality Results (2011)' CSV (OpenCity dataset 'Bengaluru Lakes - Water Quality Data', publisher Department of Mines and Geology per OpenCity; licence field 'None') into the extraction format.
Cleaning: blank lake names fill down; 'a b' (digit space digit) -> a.b (OCR lost decimal point) flagged; '>1600' censored; 'Nil' -> 0 flagged; unparseable -> dropped and counted."""
import csv, re, sys, difflib, os
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import FIELDS, OUT
from lakekey import lake_key
import pandas as pd
R = r"D:\Research-Publishing\13-bengaluru-lakes"
rows = list(csv.reader(open(r"E:\Research-Staging\13-bengaluru-lakes\official\opencity_extra\dmg2011.csv", encoding="utf-8")))
hdr = rows[0]
known = set(pd.read_csv(R + r"\data\clean\lake_gazetteer_kspcb.csv").name_kspcb.map(lake_key)) | {"bellandur", "varthur", "hebbal", "ulsoor", "madiwala", "lalbagh", "jakkur", "kengeri", "begur", "ibbalur"}
COLS = {3: ("chloride", "mg/L"), 4: ("phosphate_P", "mg/L as P (header 'PO-P'; unit not printed)"), 5: ("TSS", "mg/L"), 6: ("DO", "mg/L"), 7: ("COD", "mg/L"), 8: ("nitrate", "mg/L as NO3 (header 'NO3'; unit not printed)"), 9: ("total_hardness", "mg/L"),
        10: ("fluoride", "mg/L"), 11: ("pH", "pH units"), 12: ("zinc", "mg/L"), 13: ("lead", "mg/L"), 14: ("copper", "mg/L"), 15: ("manganese", "mg/L"), 16: ("aluminium", "mg/L"), 17: ("chromium", "mg/L"),
        18: ("E_coli_or_EC_MPN", "MPN/100mL (header 'EC MPN/100 ml', read as E. coli)"), 19: ("total_coliform", "MPN/100mL")}
out = []; dropped = 0; name = ""; kept = 0
for r in rows[1:]:
    if r[0].strip(): name = re.sub(r"\s+", " ", r[0]).strip()
    loc = re.sub(r"[^a-z]", "", r[2].lower()); loc = {"inlel": "inlet", "inlet": "inlet", "outlet": "outlet", "middle": "middle", "periphery": "periphery"}.get(loc, r[2].strip())
    k = lake_key(name); m = difflib.get_close_matches(k, known, n=1, cutoff=0.85); cname = m[0] if m else k
    for ci, (p, u) in COLS.items():
        if ci >= len(r): continue
        s = r[ci].strip()
        if s in ("", "-"): continue
        fl = ["year 2011 only (month not stated); units not printed in file; values transcribed by the data publisher from a scanned table (OCR-type errors possible)"]
        cens = ""
        if re.fullmatch(r"(?i)\.?nil", s): v = 0.0; fl.append("reported 'Nil' (below detection; value set to 0 as a placeholder)")
        elif re.fullmatch(r">\s*\d+", s): v = float(s.strip("> ")); cens = "censored >"; fl.append("reported as > value (censored)")
        elif re.fullmatch(r"\d+(\.\d+)?", s): v = float(s)
        elif re.fullmatch(r"\d+ \d+", s): v = float(s.replace(" ", ".")); fl.append("decimal point reconstructed from 'a b' in the source file")
        elif re.fullmatch(r"\d+:\d+", s): v = float(s.replace(":", ".")); fl.append("decimal point reconstructed from ':'")
        elif re.fullmatch(r"\?\s*\d+(\.\d+)?", s): v = float(re.sub(r"[^\d.]", "", s)); fl.append("leading '?' in source: uncertain")
        else: dropped += 1; continue
        out.append({f: "" for f in FIELDS} | dict(record_id="DMG2011", lake=name, site=loc, date_start="2011-01-01", date_end="2011-12-31", period_precision="year (month not stated)", parameter=p, parameter_as_reported=hdr[ci], statistic="single",
                  value=v, unit_as_reported=u, method="not stated", n_samples="1", page_table=f"CSV row for '{name}'", extraction_mode="CSV parsed", comparability_flag="; ".join(fl) + ("; " + cens if cens else ""), notes=f"lake_key_guess={cname}"))
        kept += 1
pd.DataFrame(out).to_csv(OUT + r"\DMG2011.csv", index=False)
print(kept, "values kept;", dropped, "dropped as unparseable;", len({o["lake"] for o in out}), "lake names")

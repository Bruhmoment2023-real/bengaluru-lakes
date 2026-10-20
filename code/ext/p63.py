import sys, calendar; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, pdf_grid
# P63 Madhavara (Madavara) lake, Bangalore: Assessment of water quality for aquaculture. Nature Environ Pollut Technol 8(4):755-760 (2009). Table 1 monthly Jul 2005 - Jun 2006 (read from PDF word positions, page 2).
x = Ex("63")
labs = ["Temperature", "pH", "Conductivity", "DO", "BOD", "COD", "Hardness", "Calcium", "Magnesium", "Chloride", "Fluoride", "Nitrate", "Phosphate", "Sulphate", "Amm-N"]
rows, hdrs = pdf_grid("63", 2, "Parameter/", labs, 12)
P = {"Temperature": ("temperature", "degC"), "pH": ("pH", "pH units"), "Conductivity": ("EC", "mS (per paper; N.B. says conductivity in mS)"), "DO": ("DO", "mg/L"), "BOD": ("BOD", "mg/L"), "COD": ("COD", "mg/L"),
     "Hardness": ("total_hardness", "mg/L"), "Calcium": ("calcium", "mg/L"), "Magnesium": ("magnesium", "mg/L"), "Chloride": ("chloride", "mg/L"), "Fluoride": ("fluoride", "mg/L"), "Nitrate": ("nitrate", "mg/L"),
     "Phosphate": ("phosphate", "mg/L"), "Sulphate": ("sulphate", "mg/L"), "Amm-N": ("ammoniacal_N", "mg/L")}
mons = [(2005, 7), (2005, 8), (2005, 9), (2005, 10), (2005, 11), (2005, 12), (2006, 1), (2006, 2), (2006, 3), (2006, 4), (2006, 5), (2006, 6)]
for lab, toks in rows.items():
    toks = [t for t in toks]; assert len(toks) == 12, (lab, toks)
    p, u = P[lab]
    for (y, m), t in zip(mons, toks):
        ds, de = f"{y}-{m:02d}-01", f"{y}-{m:02d}-{calendar.monthrange(y, m)[1]}"
        if t in ("ND", "nd", "BDL"):
            x.add(lake="Madavara Lake", site="single composite series", date_start=ds, date_end=de, period_precision="month", parameter=p, parameter_as_reported=lab, statistic="single", value="", unit_as_reported=u,
                  page_table="Table 1, p.757", comparability_flag="below detection (reported ND)", method="APHA; monthly samples")
        else:
            x.add(lake="Madavara Lake", site="single composite series", date_start=ds, date_end=de, period_precision="month", parameter=p, parameter_as_reported=lab, statistic="single", value=float(t.replace(",", ".")), unit_as_reported=u,
                  page_table="Table 1, p.757", method="APHA (as stated); samples collected periodically Jul 2005-Jun 2006", extraction_mode="table-parsed (PDF word positions)",
                  comparability_flag="conductivity reported in mS (unit per paper): convert 1 mS = 1000 uS/cm only after confirming with source" if lab == "Conductivity" else "")
print(len(rows), x.save())

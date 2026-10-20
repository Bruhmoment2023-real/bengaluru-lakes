import sys, re; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P68 Jumbe A.S., Nandini N. (2009) Impact assessment of heavy metals pollution of Vartur lake, Bangalore. J Appl Nat Sci 1(1):53-61. Table 1 (water): mean and range, sampling May 2006-Dec 2007 (seasonal; inlet/middle/outlet zones).
x = Ex("68"); M = "AAS (Shimadzu AA-6300) after microwave digestion (EPA 3015); APHA 1995 sampling; procedural/reagent blanks and certified standards stated; seasonal samples May 2006-Dec 2007 at inlet, middle, outlet zones"
NM = {"Cd": "cadmium", "Co": "cobalt", "Cr": "chromium", "Cu": "copper", "Mn": "manganese", "Ni": "nickel", "Pb": "lead", "Zn": "zinc"}
for i in range(173, 192):
    s = x.L[i].strip()
    m = re.match(r"^(Cd|Co|Cr|Cu|Mn|Ni|Pb|Zn)\s+([\d.]+)\s+(BDL|[\d.]+)\s*[-\u2013\ufffd]\s*([\d.]+)", s)
    if not m: continue
    el, mean, lo, hi = m.groups(); p = NM[el]
    kw = dict(lake="Varthur Lake", site="inlet, middle and outlet zones pooled", date_start="2006-05-01", date_end="2007-12-31", period_precision="period (May 2006-Dec 2007)", method=M, n_samples="not stated (seasonal)",
              page_table="Table 1, p.56")
    x.rec(kw["lake"], kw["site"], kw["date_start"], kw["date_end"], kw["period_precision"], "mean", {p: (float(mean), "mg/L (reported as ppm)")}, i + 1, kw["page_table"], M, kw["n_samples"], "values in ppm taken as mg/L; metals unusually high (e.g. Pb 2.72, Cr 2.13): verify", window=1)
    x.rec(kw["lake"], kw["site"], kw["date_start"], kw["date_end"], kw["period_precision"], "max", {p: (float(hi), "mg/L (reported as ppm)")}, i + 1, kw["page_table"], M, kw["n_samples"], "values in ppm taken as mg/L", window=1)
    if lo == "BDL":
        x.add(lake=kw["lake"], site=kw["site"], date_start=kw["date_start"], date_end=kw["date_end"], period_precision=kw["period_precision"], parameter=p, parameter_as_reported=el, statistic="min", value="",
              unit_as_reported="mg/L (reported as ppm)", method=M, page_table=kw["page_table"], source_line=i + 1, comparability_flag="minimum reported as BDL (detection limit not stated)")
    else:
        x.rec(kw["lake"], kw["site"], kw["date_start"], kw["date_end"], kw["period_precision"], "min", {p: (float(lo), "mg/L (reported as ppm)")}, i + 1, kw["page_table"], M, kw["n_samples"], "values in ppm taken as mg/L", window=1)
print(x.save())

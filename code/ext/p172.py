import sys, re, calendar; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, nums
# P172 Ramachandra-group paper: Gidadakonenahalli Lake, Bangalore; Adv. For. Sci. 2(1):7-12 (2015). Table 1 monthly Jan-Dec 2010; Sep-Dec values sit on separate lines (text-layer wrap) in parameter order - verified against text ranges (alkalinity 194 mg/L Oct, 446 Jun; chloride 169.8 Oct).
x = Ex("172")
P = [("temperature", "degC"), ("pH", "pH units"), ("TDS", "mg/L"), ("EC", "umho/cm"), ("DO", "mg/L"), ("BOD", "mg/L"), ("COD", "mg/L"), ("chloride", "mg/L"), ("total_alkalinity", "mg/L"), ("total_hardness", "mg/L"),
     ("phosphate", "mg/L"), ("nitrate", "mg/L"), ("sulphate", "mg/L"), ("phytoplankton", "units/mL"), ("zooplankton", "units/mL"), ("total_coliform", "CFU/100mL")]
main = []; quad = []
for i in range(168, 190):
    s = re.sub(r"(?<=[A-Za-z])-1\b", "", x.L[i].strip())  # drop the "-1" exponent in units (mg L-1, cm-1): read as a number it shifted every month by one (check E062-E064)
    if re.match(r"^\d{1,2}\s+[A-Za-z]", s):
        v = nums(s)[1:]
        if "cfu 100" in s: v.remove(100.0)
        main.append((i + 1, v[:8]))
        if len(v) >= 12: quad.append((i + 1, v[8:12]))
    elif len(nums(s)) == 4 and not re.search(r"[A-Za-z]", s): quad.append((i + 1, nums(s)))
assert len(main) == 16 and len(quad) == 16, (len(main), len(quad))
for k, ((pn, u), (l1, v1), (l2, v2)) in enumerate(zip(P, main, quad)):
    if pn in ("phytoplankton", "zooplankton"): continue
    assert len(v1) == 8, (pn, v1)
    vals = v1 + v2
    for m, val in enumerate(vals, 1):
        ln = l1 if m <= 8 else l2
        x.rec("Gidadakonenahalli Lake", "single composite series", f"2010-{m:02d}-01", f"2010-{m:02d}-{calendar.monthrange(2010, m)[1]}", "month", "single", {pn: (val, u)}, ln, "Table 1, p.9",
              "APHA standard methods (as stated); monthly 8-9 am surface samples", "1", "total coliform reported as cfu/100 mL (membrane filtration), not MPN" if pn == "total_coliform" else "", window=1)
print(x.save())

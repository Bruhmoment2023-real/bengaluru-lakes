import sys, re; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, nums
# P287 Hebbal Lake water quality assessment, IJITEE 8(11) Sept 2019, doi 10.35940/ijitee.K1274.0981119. Tables II (February) and III (March): 19 sampling points. Year of sampling not stated.
x = Ex("287")
cols = [("pH", "pH units"), ("acidity", "mg/L"), ("total_alkalinity", "mg/L"), ("turbidity", "NTU"), ("DO", "mg/L"), ("total_solids", "mg/L"), ("TSS", "mg/L"), ("TDS", "mg/L"), ("chloride", "mg/L"),
        ("total_hardness", "mg/L"), ("calcium_hardness", "mg/L"), ("magnesium_hardness", "mg/L"), ("sulphate", "mg/L"), ("BOD", "mg/L")]
n = 0
for (a, b, mon, tab) in ((294, 333, "Feb", "Table II, p.5"), (348, 386, "Mar", "Table III, p.6")):
    for i in range(a, b):
        s = x.L[i].strip()
        m = re.match(r"^(\d{1,2})\s+(.*)$", s)
        if not m: continue
        v = nums(m.group(2))
        if len(v) != 14: continue
        for (p, u), val in zip(cols, v):
            x.rec("Hebbal Lake", f"sampling point {int(m.group(1)):02d}", "", "", f"{mon} (year not stated)", "single", {p: (val, u)}, i + 1, tab,
                  "BIS/APHA-type methods listed in Table I of paper; 19 sampling points", "1", "sampling year not reported (paper published 2019-09): cannot be placed on a timeline; column assignment follows header order in text layer", season=mon)
        n += 1
print(n, "rows(points)", x.save())

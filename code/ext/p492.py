import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P492 Ravi Kumar K., Spoorthi (2025) Assessment and management of Hebbal Lake, Bangalore. Curr World Environ 20(3):1360-1366. Table 1, n=49 water samples; sampling date not stated.
x = Ex("492"); FL = "sampling date/year not stated: cannot be placed on a timeline"; M = "49 surface samples (CPCB/KSPCB-style protocol per paper); composite samples"
R = [(150, "pH", "pH units", 6.55, 8.2, 7.63, 0.36), (152, "DO", "mg/L", 4.1, 6.2, 5.36, 0.53), (156, "EC", "uS/cm", 882, 1468, 914, 145), (160, "BOD", "mg/L", 1.9, 5.2, 3.09, 0.93),
     (164, "nitrate", "mg/L", 6.65, 16.27, 7.97, 2.11), (172, "sulphate", "mg/L", 2.3, 11.23, 10.68, 2.31), (176, "free_ammonia_N", "mg/L", 0.02, 0.29, 0.17, 0.07), (184, "fluoride", "mg/L", 0.6, 0.82, 0.70, 0.06)]
for ln, p, u, a, b, m, s in R:
    for st, v in (("min", a), ("max", b), ("mean", m), ("sd", s)):
        x.rec("Hebbal Lake", "49 sampling locations pooled", "", "", "single survey (year not stated)", st, {p: (v, u)}, ln, "Table 1, p.1363", M, "49", FL, window=2)
x.rec("Hebbal Lake", "49 sampling locations pooled", "", "", "single survey (year not stated)", "min", {"phosphate": (0.05, "mg/L as PO4")}, 168, "Table 1, p.1363", M, "49", FL + "; reported '<0.05' (censored)", window=2)
x.rec("Hebbal Lake", "49 sampling locations pooled", "", "", "single survey (year not stated)", "max", {"phosphate": (1.0, "mg/L as PO4")}, 168, "Table 1, p.1363", M, "49", FL, window=2)
x.rec("Hebbal Lake", "49 sampling locations pooled", "", "", "single survey (year not stated)", "mean", {"phosphate": (0.32, "mg/L as PO4")}, 168, "Table 1, p.1363", M, "49", FL, window=2)
for ln, p, lim in ((186, "boron", 0.1), (188, "lead", 0.05), (190, "copper", 0.05), (192, "zinc", 0.05), (194, "cadmium", 0.05), (198, "iron", 0.2)):
    x.rec("Hebbal Lake", "49 sampling locations pooled", "", "", "single survey (year not stated)", "all_below_limit", {p: (lim, "mg/L")}, ln, "Table 1, p.1363-4", M, "49", FL + f"; all samples reported '<{lim}' (censored; value = reporting limit)", window=2)
print(x.save())

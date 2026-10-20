import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P514 Narayanaswamy SY (2026) Impact of urbanization on the physicochemical parameters of Varthur Lake. J Res Dev 18(2(VI)):182-185. Six sampling points, sampled October 2025 (abstract). Rows with unambiguous 6-value alignment only.
x = Ex("514")
R = [(142, "temperature", "degC", [29.3, 29.6, 29.4, 28.3, 28.6, 28.1], ""), (158, "TDS", "mg/L", [735, 607, 732, 735, 722, 789], ""), (176, "DO", "mg/L", [2.8, 2.5, 2.7, 2.8, 2.4, 2.4], ""),
     (178, "BOD", "mg/L", [41.8, 39.4, 55.0, 62.0, 70.5, 69.7], ""), (174, "fluoride", "mg/L", [1.3, 1.4, 1.6, 1.8, 1.2, 1.4], ""), (162, "total_hardness", "mg/L", [300.9, 276.2, 288.4, 284.6, 292.2, 200.7], ""),
     (180, "COD", "mg/L", [121.22, 101.41, 156.75, 155.5, 186.82, 201.43], "row-label/value alignment inferred from text-layer order")]
for ln, p, u, vals, fl in R:
    for i, v in enumerate(vals, 1):
        x.rec("Varthur Lake", f"sampling point {i}", "2025-10-01", "2025-10-31", "month", "single", {p: (v, u)}, ln, "Table 1, p.183-184", "IS 3025 standards (as stated); samples analysed 2 days after collection", "1", fl, window=2)
print(x.save())

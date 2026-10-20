import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P138 Ravikumar, Mehmood, Somashekar 2013 Appl Water Sci 3:247-261, doi 10.1007/s13201-013-0077-2. Tables 3 (Sankey tank) and 4 (Mallathahalli lake); mean, SD, min, max per month of 2012 (3 sites pooled).
x = Ex("138")
SPEC = {"DO": ("DO", "mg/L"), "pH": ("pH", "pH units"), "EC": ("EC", "uS/cm"), "TDS": ("TDS", "mg/L"), "Turbidity": ("turbidity", "NTU"), "BOD": ("BOD", "mg/L"), "COD": ("COD", "mg/L"),
        "Temp": ("temperature", "degC"), "TA": ("total_alkalinity", "mg/L as CaCO3"), "TH ": ("total_hardness", "mg/L as CaCO3"), "Cl-": ("chloride", "mg/L"), "NO3-": ("nitrate", "mg/L as NO3"),
        "PO43-": ("phosphate", "mg/L as PO4"), "SO42-": ("sulphate", "mg/L"), "Fe2": ("iron", "mg/L")}
cols = []
for m, (a, b) in {"03": ("2012-03-01", "2012-03-31"), "04": ("2012-04-01", "2012-04-30"), "05": ("2012-05-01", "2012-05-31")}.items():
    for st in ("mean", "sd", "min", "max"): cols.append((a, b, "month", st))
meth = "APHA 2005; DO/BOD modified Winkler; COD closed reflux; samples per station analysed in triplicate; 3 sites pooled (Table 3/4 columns are across sites)"
a = x.find("Table 3 Analytical results of Sankey"); b = x.find("Table 4 Analytical results of Mallathahalli")
n1 = x.table(a, b, {k.strip() if k == "TH " else k: v for k, v in SPEC.items()}, cols, "Sankey Tank", "3 sites (A,B,C) pooled", page_table="Table 3, p.253", method=meth, n_samples="3 sites x triplicate")
c = x.find("Table 5 Classification of")
n2 = x.table(b, c, {k.strip() if k == "TH " else k: v for k, v in SPEC.items()}, cols, "Mallathalli Lake", "3 sites (inlet,centre,outlet) pooled", page_table="Table 4, p.254", method=meth, n_samples="3 sites x triplicate")
print(n1, n2, x.save())

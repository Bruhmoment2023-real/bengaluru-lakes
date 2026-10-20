import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P47 Bindiya C. et al. (2008) Environmental degradation of Mallathalli Lake in Bangalore district, India - a case study. Nature Environ Pollut Technol 7(2):189-196. Table 2: 3 stations, Jan-Jun 2007, Max/Min/Avg/SD.
x = Ex("47")
SPEC = {"pH": ("pH", "pH units"), "Turbidity (NTU)": ("turbidity", "NTU"), "TDS": ("TDS", "mg/L"), "TH ": ("total_hardness", "mg/L"), "Chlorides": ("chloride", "mg/L"), "Fluorides": ("fluoride", "mg/L"),
        "Sulphates": ("sulphate", "mg/L"), "Phosphates": ("phosphate", "mg/L"), "Nitrates": ("nitrate", "mg/L"), "T. Alkalinity": ("total_alkalinity", "mg/L"), "Sus. Solids": ("TSS", "mg/L"),
        "Sodium": ("sodium", "mg/L"), "Potassium": ("potassium", "mg/L")}
SPEC = {k.strip(): v for k, v in SPEC.items()}
cols = []
for st in ("Station 1", "Station 2", "Station 3"):
    for stat in ("max", "min", "mean", "sd"): cols.append(("2007-01-01", "2007-06-30", "period (Jan-Jun 2007)", stat, st))
n = x.table(299, 318, SPEC, cols, "Mallathahalli Lake", page_table="Table 2, p.194", method="APHA (1985) standard methods; DO in field; 3 stations, monthly Jan-Jun 2007", n_samples="6 monthly samples per station (as inferred)",
            comparability_flag="paper's Table 2 has internal inconsistencies in some rows (e.g. colour, turbidity average vs range); nitrate/phosphate basis not stated")
print(n, x.save())

import sys, re; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, nums
# P462 Moramchetty A. (2025) SSRG Int J Agric Environ Sci 12(4):9-16, doi 10.14445/23942568/IJAES-V12I4P102. Table 1 annual means 2012-2023 for Ulsoor Lake; secondary data, CPCB NWMP (ref [23]); station named in text as Ulsoor Lake, Training Centre of Fish Breeding.
x = Ex("462")
cols = [("temperature", "degC"), ("DO", "mg/L"), ("pH", "pH units"), ("EC", "umho/cm"), ("BOD", "mg/L"), ("nitrate_plus_nitrite", "mg/L"), ("faecal_coliform", "MPN/100mL"), ("total_coliform", "MPN/100mL")]
for i in range(145, 168):
    s = x.L[i].strip()
    if not re.match(r"^20(1[2-9]|2[0-3])\s", s): continue
    v = nums(s); yr = int(v[0]); v = v[1:]
    assert len(v) == 8, (s, v)
    for (p, u), val in zip(cols, v):
        flag = "secondary source (via CPCB NWMP as cited by the paper); annual mean, n per year not stated"
        if p == "total_coliform" and v[7] < v[6]: flag += "; total coliform < faecal coliform (internally inconsistent)"
        if p == "faecal_coliform" and v[7] < v[6]: flag += "; total coliform < faecal coliform (internally inconsistent)"
        x.rec("Ulsoor Lake", "Training Centre of Fish Breeding (CPCB NWMP station, per text)", f"{yr}-01-01", f"{yr}-12-31", "year", "mean", {p: (val, u)}, i + 1, "Table 1, p.12",
              "CPCB NWMP monitoring (methods not described in paper)", "", flag, notes="Nitrate+nitrite combined; coliform basis MPN/100 mL")
print(x.save())

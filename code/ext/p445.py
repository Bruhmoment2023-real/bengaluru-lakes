import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P445 Venkata Ramaiah G, Ravindra PK, Kallimani AK (2024) Water quality assessment of Byramangala Lake and its proximate groundwater. Afr J Biomed Res 27(4s):15074-15078.
# Only the surface-water columns (LAKE, CHANNEL) are extracted; bore/open wells (groundwater) are out of scope (X3). Phase 1 / Phase 2 = samples in 'March and June' (mapping not stated); year not stated.
x = Ex("445")
FL = "sampling year not stated; phase-to-month mapping not stated; Byramangala is a peri-urban tank (Ramanagara district, formerly Bangalore Rural): scope borderline; very high COD/F values: verify"
P1 = {"LAKE": {"acidity": 108, "total_alkalinity": 518, "total_hardness": 150, "calcium_hardness": 150, "COD": 1024, "BOD": 108, "fluoride": 5.2, "iron": 2.8, "sulphate": 184.6, "nitrate": 39, "chloride": 235.9, "temperature": 33, "pH": 7.6, "turbidity": 46},
      "CHANNEL": {"acidity": 88, "total_alkalinity": 546, "total_hardness": 162, "calcium_hardness": 410, "COD": 992, "BOD": 91.7, "fluoride": 3.32, "iron": 2.3, "sulphate": 181.93, "nitrate": 85, "chloride": 293.9, "temperature": 33, "pH": 7.9, "turbidity": 49}}
LN1 = {"acidity": 95, "total_alkalinity": 97, "total_hardness": 99, "calcium_hardness": 101, "COD": 105, "BOD": 106, "fluoride": 107, "iron": 108, "sulphate": 109, "nitrate": 110, "chloride": 111, "temperature": 112, "pH": 114, "turbidity": 115}
P2 = {"LAKE": {"acidity": 117, "COD": 1008, "BOD": 112.2, "fluoride": 5.6, "iron": 2.9, "sulphate": 193.9, "nitrate": 41, "chloride": 223.9, "temperature": 35, "pH": 7.6, "turbidity": 65},
      "CHANNEL": {"acidity": 90, "COD": 976, "BOD": 108, "fluoride": 3.42, "iron": 2.5, "sulphate": 291.9, "nitrate": 87, "chloride": 321.9, "temperature": 35, "pH": 7.9, "turbidity": 70}}
LN2 = {"acidity": 121, "COD": 137, "BOD": 139, "fluoride": 141, "iron": 142, "sulphate": 144, "nitrate": 145, "chloride": 146, "temperature": 147, "pH": 148, "turbidity": 149}
U = {"acidity": "mg/L", "total_alkalinity": "mg/L", "total_hardness": "mg/L", "calcium_hardness": "mg/L", "COD": "mg/L", "BOD": "mg/L", "fluoride": "mg/L", "iron": "mg/L", "sulphate": "mg/L", "nitrate": "mg/L", "chloride": "mg/L", "temperature": "degC", "pH": "pH units", "turbidity": "NTU"}
for (ph, P, LN, tab) in (("Phase 1", P1, LN1, "Table 1, p.15074-5"), ("Phase 2", P2, LN2, "Table 2, p.15075")):
    for site, d in P.items():
        for p, v in d.items():
            x.rec("Byramangala Lake", "lake sample" if site == "LAKE" else "inflow channel sample", "", "", f"{ph} (March or June; year not stated)", "single", {p: (v, U[p])}, LN[p], tab, "one sample per site per phase; methods not described in detail", "1", FL, window=1)
    x.add(lake="Byramangala Lake", site="lake sample", period_precision=f"{ph} (March or June; year not stated)", parameter="DO", parameter_as_reported="DISSOLVED OXYGEN", statistic="single", value="", unit_as_reported="mg/L",
          page_table=tab, comparability_flag="reported as 'Absent' (no numeric value)")
print(x.save())

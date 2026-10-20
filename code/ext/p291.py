import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P291 Rao S., Mogili N.V., Priscilla A., Lydia A. (2020) Aqueous chemistry of anthropogenically contaminated Bengaluru lakes. Sustainable Environ Res 30:8, doi 10.1186/s42834-020-00049-5. Table 2 (lake samples), p.6, read from rendered page image.
x = Ex("291")
T = {  # param: (unit, min, median, max)
    "pH": ("pH units", 6.0, 8.8, 10.3), "bicarbonate": ("mg/L", 80, 109, 344), "chloride": ("mg/L", 36, 66, 102), "sulphate": ("mg/L", 7, 40, 319), "nitrate": ("mg/L as NO3", 0.0, 3.5, 9.0),
    "calcium": ("mg/L", 17, 25, 90), "magnesium": ("mg/L", 7, 14, 40), "sodium": ("mg/L", 20, 57, 92), "potassium": ("mg/L", 8, 13, 16), "ammonium": ("mg/L as NH4", 0.0, 0.0, 4), "TDS": ("mg/L", 173, 359, 882),
    "COD": ("mg/L", 12, 42, 67), "DO": ("mg/L", 4.1, 7.5, 15.0)}
for p, (u, a, b, c) in T.items():
    for stat, v in (("min", a), ("median", b), ("max", c)):
        x.rec_visual("Puttenahalli, Ulsoor, Nagawara and Sankey lakes (pooled)", "19+ grab samples (Puttenahalli, Ulsoor, Nagawara, Sankey)", "2018-01-01", "2019-05-31", "period (Jan 2018-May 2019)", stat, {p: (v, u)},
                     "Table 2, p.6 (lake samples columns)", "grab samples 15-90 cm depth; AAS/IC/titration; EC reported as TDS; DO/pH/EC field meters", "19 grab samples Jan-Jun 2018 + additional sampling to May 2019",
                     "four lakes pooled (cannot be split by lake); includes fish-kill and non-fish-kill episodes (Puttenahalli Mar 2018, Ulsoor May 2018)", img="291_p6.png")
print(x.save())

import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
import pandas as pd
from litlib import FIELDS, OUT
# Ramachandra T.V. et al. (2017) Bellandur and Varthur Lakes Rejuvenation Blueprint, ENVIS Technical Report 116 (IISc), Table 3.1 p.27: ranges 'observed in the two lakes over past several years' (synthesis of IISc studies 2008-2015). Rows typed from the PDF text layer (pdftotext, layout partly scrambled).
T = {"Bellandur Lake": {"pH": (6.8, 8.4, "pH units"), "DO": (0, 3, "mg/L"), "BOD": (25, 180, "mg/L (5-day 20 C)"), "COD": (44, 330, "mg/L")},
     "Varthur Lake": {"pH": (6.9, 8.2, "pH units"), "DO": (0, 5, "mg/L"), "BOD": (32, 175, "mg/L (5-day 20 C)"), "COD": (51, 280, "mg/L")}}
rows = []
for lake, d in T.items():
    for p, (a, b, u) in d.items():
        for st, v in (("min", a), ("max", b)):
            rows.append({f: "" for f in FIELDS} | dict(record_id="BP2017", lake=lake, site="lake-wide (synthesis)", date_start="2008-01-01", date_end="2015-12-31", period_precision="multi-year synthesis (2008-2015 studies; exact years not given)", parameter=p,
                  parameter_as_reported=p, statistic=st, value=v, unit_as_reported=u, method="synthesis of earlier IISc studies (Ramachandra et al., Mahapatra et al.)", page_table="Table 3.1, p.27", extraction_mode="hand-transcribed from PDF text layer",
                  comparability_flag="secondary synthesis of other studies: overlaps with primary IISc papers; not used for trends/compliance counts"))
pd.DataFrame(rows).to_csv(OUT + r"\BP2017.csv", index=False); print(len(rows))
